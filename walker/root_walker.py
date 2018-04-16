
# Local package imports
from debug import Debug, rootClassMethod


class RootWalker(object):
    '''Interface for the walker class.
    Determines the step size of each iteration and launches runs.'''

    #############################################
    # INITIALIZATION                            #
    #############################################
    def __init__(self, mutables, cost_funcs, launcher, **kwargs):
        self.setMutables(mutables)
        self.setCostFuncs(cost_funcs)
        self.setLauncher(launcher)
        self._flattest_curve = ('None', float('inf'))
        super().__init__(**kwargs)

    @rootClassMethod('walker.root_walker', 'RootWalker')
    def setMutables(self, mutables):
        self._mutables = mutables

    @rootClassMethod('walker.root_walker', 'RootWalker')
    def setCostFuncs(self, cost_funcs):
        self._cost_funcs = cost_funcs

    @rootClassMethod('walker.root_walker', 'RootWalker')
    def setLauncher(self, launcher):
        self._launcher = launcher

    #############################################
    # INITIALIZING MATRIX DATA                  #
    #############################################
    # These calculations are performed after the first run has
    # completed. It requires two runs to be performed
    # in order to build a set of data to iterate upon.
    @rootClassMethod('walker.root_walker', 'RootWalker')
    def _initBaselineData(self, costs, resolution):
        Debug.log('init baseline data')
        init_run_batch = self._launcher.getLatestRunset()
        prime_run_dir = self._launcher.getDirNameFromRunName(
            init_run_batch[0])
        Debug.log('prime: ' + prime_run_dir)
        # TODO: find the cheapest cost in the first runset and use
        # that instead of just using the last one.
        first_run_dir = self._launcher.getDirNameFromRunName(
            init_run_batch[-1])
        Debug.log('first: ' + first_run_dir)
        prime_costs = \
            dict((x, y) for x, y in costs.items() if prime_run_dir in x)
        first_costs = \
            dict((x, y) for x, y in costs.items() if first_run_dir in x)
        self._initStatesAndGradients(prime_costs, first_costs, resolution)
        self._initBFGS()
        # keep track of the previous curve to make sure were not in a local min
        self._previous_curve = None

    @rootClassMethod('walker.root_walker', 'RootWalker')
    def _initStatesAndGradients(self, prime_costs, first_costs, resolution):
        self._iterations = 0
        self._states = []
        self._gradients = []
        self._updateStatesAndGradients(prime_costs, resolution)
        self._updateStatesAndGradients(first_costs, resolution)

    @rootClassMethod('walker.root_walker', 'RootWalker')
    def _initBFGS(self):
        self._bfgs = []
        self._rho = []
        # initial matrix B[0] = I where diagonal length = number of mutables
        self._bfgs.append(np.matrix(np.identity(len(self._mutables))))
        self._updateBFGSandRHO()

    #############################################
    # CALCULATE STEP SIZING                     #
    #############################################
    @rootClassMethod('walker.root_walker', 'RootWalker')
    def _determineSteps(self, costs, resolution, epsilon):
        # our boolean return value:
        # true : continue searching
        # false: we've hit a local minimum
        continue_searching = True
        self._flattest_curve = self._findSmallestCost(costs)
        msg = 'Flattest curve at {0._iterations}: {0._flattest_curve}'
        Debug.log(msg.format(self))
        dir_k_next = self._launcher.getDirNameFromRunName(
            self._flattest_curve[0])
        # Archive the data from the cheapest run,
        # so we have a log of the path we took.
        self._launcher.archiveDir(dir_k_next, self._iterations)
        step_k_next = self._launcher.getStepFromRunName(
            self._flattest_curve[0])
        # determine if we're close enough to our result.
        if (abs(self._flattest_curve[1]) < epsilon):
            msg = "ENDING RUN:: We're within epsilon({}) of our target."
            Debug.log(msg.format(epsilon))
            continue_searching = False
        # if the same step is the flattest twice: then we've hit local minima
        elif (self._flattest_curve == self._previous_curve):
            Debug.log("We've hit a local minimum.")
            # TODO: create a gradient between step[i] and step[i+1]
            # and refine our search with smaller increments until we
            # get to epsilon
            continue_searching = False
        # otherwise calculate our next set of search parameters
        else:
            # trim info not at the step of closest fit.
            for c in list(costs.keys())[:]:
                if (dir_k_next not in c):
                    # Clean the expensive keys from our dictionary.
                    del costs[c]
            # math functions are broken up and implemented below.
            self._updateStatesAndGradients(costs, resolution)
            self._updateBFGSandRHO()
            self._updateMutableValuesAndSteps(step_k_next)
            self._previous_curve = self._flattest_curve
        return continue_searching

    @rootClassMethod('walker.root_walker', 'RootWalker')
    def _findSmallestCost(self, costs):
        smallest_cost = ('None', float('inf'))
        for c in costs.items():
            # don't need to check against gradient runs
            if('all' in c[0] and abs(c[1]) < abs(smallest_cost[1])):
                smallest_cost = c
                Debug.log('smaller: ' + str(c))
        return smallest_cost

    @rootClassMethod('walker.root_walker', 'RootWalker')
    def _updateStatesAndGradients(self, costs, resolution):
        # append the next set of states and gradients
        self._states.append({})
        self._gradients.append({})
        next = -1
        for m in self._mutables:
            # get set of plus and minus runs per variable name.
            xi_runs = {x for x in costs.keys() if m.name.lower() in x.lower()}
            xi_plus = list(x for x in xi_runs if 'plus' in x.lower())[0]
            xi_minus = list(x for x in xi_runs if 'minus' in x.lower())[0]
            # get offsets widths for calculating gradients
            step = self._launcher.getStepFromRunName(xi_plus)
            Debug.log('step: ' + str(step))
            gradient_width = m.getGradientWidthAtStep(step, resolution)
            # ======================================================= #
            # calculate gradient per variable:                        #
            #           F(x[i] + s[i]) - F(x[i] - s[i])               #
            # g(x[i]) = -------------------------------               #
            #                        2s[i]                            #
            # where x is the value of the mutable at the current step #
            # s is the gradient width at the same step                #
            # ======================================================= #
            gradient = (costs[xi_plus] - costs[xi_minus])
            gradient /= (2.0 * gradient_width)
            # append k+1 state and gradient to the list
            self._states[next][m.name] = m.getValueAtStep(step, resolution)
            self._gradients[next][m.name] = gradient

    @rootClassMethod('walker.root_walker', 'RootWalker')
    def _updateBFGSandRHO(self):
        # ================================================================ #
        # The Broyden Fletcher Goldfarb Shanno (BFGS) update:              #
        # B[0] = I, where diagonal length = number of mutables             #
        #                                                                  #
        #                 (B[k] s[k] s[k]t B[k])   (y[k] y[k]t)            #
        # B[k+1] = B[k] -   (s[k]t B[k] s[k])    + (y[k]t s[k])            #
        #                                                                  #
        # where the 1xN matrices of "y" and "s" are:                       #
        # y[k] = gradients[k+1] - gradients[k]                             #
        #           and                                                    #
        # s[k] = alpha[k] rho[k] = mutable_values[k+1] - mutable_values[k] #
        # ================================================================ #

        # create and format np matricies using passed in dicts of data
        # use .T to get them into 1xN size matricies
        def getMatrixOfValues(info):
            mat = []
            for m in self._mutables:
                mat.append(info[m.name])
            return np.matrix(mat).T

        # create y[k]
        gkc = getMatrixOfValues(self._gradients[-2])
        gkn = getMatrixOfValues(self._gradients[-1])
        yk = np.subtract(gkn, gkc)
        # create s[k]
        xkc = getMatrixOfValues(self._states[-2])
        xkn = getMatrixOfValues(self._states[-1])
        sk = np.subtract(xkn, xkc)

        # cache B[k] from our list
        bk = self._bfgs[-1]
        # break up calculation for debugging
        # first section
        top = bk * sk * sk.T * bk
        bot = sk.T * bk * sk
        first = top / bot
        # second section
        top = yk * yk.T
        bot = yk.T * sk
        second = top / bot
        # combine components
        bkn = bk - first + second
        # append it to our list
        self._bfgs.append(bkn)

        # Next step size is a function of the Hessian and the gradient
        # rho[k+1] = -B[k+1]i g[k+1]
        rho = -bkn.I * gkn
        # sort the rho values into a map
        self._rho.append({})
        rho_gen = (x for x in rho.A1)
        for m in self._mutables:
            self._rho[-1][m.name] = next(rho_gen)

    @rootClassMethod('walker.root_walker', 'RootWalker')
    def _updateMutableValuesAndSteps(self, step_k_next):
        for m in self._mutables:
            m.setCurValue(self._states[-1][m.name])
            m.setCurStepWidth(self._rho[-1][m.name])
            Debug.log(str(m))

    #############################################
    # CREATING DATA                             #
    #############################################
    @rootClassMethod('walker.root_walker', 'RootWalker')
    def _launchSet(self, num_runs=10, resolution=0.1):
        self._launcher.createRuns(self._mutables, num_runs, resolution)
        self._launcher.launch()

    #############################################
    # CALCULATING DIFFERENCE                    #
    #############################################
    @rootClassMethod('walker.root_walker', 'RootWalker')
    def _calculateCosts(self):
        cost_sums = {}
        # for each run add up the costs
        for run in self._launcher.getLatestRunset():
            cost_sum_at_resolution = 0.0
            for cf in self._cost_funcs:
                cost_sum_at_resolution += cf.calculate(run)
            cost_sums[run] = cost_sum_at_resolution
        return cost_sums

    #############################################
    # WALKER ENTRY POINT                        #
    #############################################
    # This method name wasn't meant to be a joke.
    @rootClassMethod('walker.root_walker', 'RootWalker')
    def run(self, resolution=0.01, epsilon=0.001):
        # Set number of runs per step based on resolution percentage
        num_runs = int(1.0 / resolution)
        # first pass
        self._launchSet(num_runs, resolution)
        costs = self._calculateCosts()
        # need to initialize the baseline between launch and calculate next
        self._initBaselineData(costs, resolution)
        # the rest of this first pass is the same as the main loop below.
        # Our termination condition:
        continue_searching = self._determineSteps(
            costs, resolution, epsilon)
        self._iterations += 1
        # Main loop after first pass. Loop till acceptable convergance
        test = 15
        while(continue_searching):
            self._launchSet(num_runs, resolution)
            costs = self._calculateCosts()
            continue_searching = self._determineSteps(
                costs, resolution, epsilon)
            self._iterations += 1
            if (test < 0):
                Debug.log('Loop exit from test iteration limit(15).')
                break
            test -= 1
        msg = 'Closest fit after {0._iterations} runs: {0._flattest_curve}'
        Debug.log(msg.format(self))
