
# Local package imports
from walker.bfgs_manager import BFGSManager
from debug import Debug, rootClassMethod


class RootWalker(object):
    '''Interface for the walker class.
    Determines the step size of each iteration and launches runs.'''

    #############################################
    # INITIALIZATION                            #
    #############################################
    def __init__(self, mutables, cost_funcs, launcher,
                 resolution=0.01, **kwargs):
        self._storeDefaults(mutables, cost_funcs, launcher, resolution)
        self.setMutables(mutables)
        self.setCostFuncs(cost_funcs)
        self.setLauncher(launcher)
        self._iterations = 0
        self._total_run_count = 0
        self.setRunResolution(resolution)
        super(RootWalker, self).__init__(**kwargs)

    @rootClassMethod('walker.root_walker', 'RootWalker')
    def _storeDefaults(self, mutables, cost_funcs, launcher, resolution):
        self._default = {}
        self._default['mutables'] = mutables
        self._default['resolution'] = resolution

    @rootClassMethod('walker.root_walker', 'RootWalker')
    def _reInit(self):
        # We can skip reseting the cost functions since
        # "they shouldn't change" (tm) ~Drew M. Streb 05/30/2018
        self.setMutables(self._default['mutables'])
        self.setLauncher(eval(self._launcher))
        self._iterations = 0
        self._total_run_count = 0
        self.setRunResolution(self._default['resolution'])
        pass

    @rootClassMethod('walker.root_walker', 'RootWalker')
    def setMutables(self, mutables):
        self._bfgs_man = BFGSManager()
        self._bfgs_man.setMutables(mutables)

    @rootClassMethod('walker.root_walker', 'RootWalker')
    def setCostFuncs(self, cost_funcs):
        self._cost_funcs = cost_funcs

    @rootClassMethod('walker.root_walker', 'RootWalker')
    def setLauncher(self, launcher):
        self._launcher = launcher

    @rootClassMethod('walker.root_walker', 'RootWalker')
    def setRunResolution(self, resolution=0.01):
        self._resolution = resolution
        self._num_runs = int(1.0 / resolution)

    #############################################
    # SPECIAL INSTRUCTIONS FOR FIRST RUNSET     #
    #############################################
    # We calculate a special first run scenario so that we dont
    # run into issues where we have the same curve twice in a row.
    # It breaks the matrix math if we have the same curve twice.
    @rootClassMethod('walker.root_walker', 'RootWalker')
    def _firstLaunchSet(self, ):
        self._launcher.clearRunData()
        self._launcher.firstCreateRuns(self._bfgs_man.getMutables())
        self._launcher.launch()
        costs = self._calculateCosts()
        self._setupBFGSManager(costs)
        # return self.determineSteps(costs, resolution=0.0, epsilon=0.0)

    #############################################
    # BUILDING THE INITIAL BFGS MATRIX          #
    #############################################
    # Done after the first runset has been launched.
    @rootClassMethod('walker.root_walker', 'RootWalker')
    def _setupBFGSManager(self, costs):
        # grab the first runset
        init_run_batch = self._launcher.getLatestRunset()
        Debug.log('init_run_batch')
        for name in init_run_batch:
            Debug.log(name)
        # grab runs at k[0]
        prime_run_dir = self._launcher.getDirNameFromRunName(
            init_run_batch[0])
        prime_costs = \
            dict((x, y) for x, y in costs.items() if prime_run_dir in x)
        # grab runs at k[1]
        first_run_dir = self._launcher.getDirNameFromRunName(
            init_run_batch[-1])
        first_costs = \
            dict((x, y) for x, y in costs.items() if first_run_dir in x)
        # init baseline using the data we've just gathered
        self._bfgs_man.initBaselineData(prime_costs, first_costs)
        self._previous_curve = self._bfgs_man.findSmallestCost(costs)
        self._iterations = 0

    #############################################
    # CREATING DATA                             #
    #############################################
    @rootClassMethod('walker.root_walker', 'RootWalker')
    def _launchSet(self):
        self._launcher.clearRunData()
        self._launcher.createRuns(
            self._bfgs_man.getMutables(),
            self._num_runs,
            self._resolution)
        self._launcher.launch()
        self._total_run_count += self._num_runs

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
    # CALCULATE STEP SIZING                     #
    #############################################
    def determineSteps(self, costs, epsilon):
        # our boolean return value:
        # true : continue searching
        # false: we've reached epsilon. stop looking.
        continue_searching = True
        self._flattest_curve = self._bfgs_man.findSmallestCost(costs)
        msg = 'Flattest curve at {0._iterations}: {0._flattest_curve}'
        Debug.log(msg.format(self))
        dir_k_next = self._launcher.getDirNameFromRunName(
            self._flattest_curve[0])
        # Archive the data and have a log of the path we took.
        self._launcher.archiveDir(dir_k_next, self._iterations)
        step_k_next = self._launcher.getStepFromRunName(
            self._flattest_curve[0])

        # determine if we're close enough to our result.
        if (self._bfgs_man.determineExtrema(epsilon)):
            Debug.log("ENDING RUN:: We've found a local minima.")
            continue_searching = False
        # if the same step is the flattest twice: then we're stuck
        elif (self._flattest_curve[1] == self._previous_curve[1]):
            Debug.log("ENDING RUN:: We're stuck...")
            continue_searching = False
        # TODO: if we overshoot the local min and cost[k+1] > cost[k] then:
        # a) increase resolution and rerun?
        # b) recalc BFGS and rerun?
        # c) both?
        else:
            # trim info not at the step of closest fit.
            for c in list(costs.keys())[:]:
                if (dir_k_next not in c):
                    # Clean the expensive keys from our dictionary.
                    del costs[c]
            # math functions are broken up and implemented below.
            self._bfgs_man.updateStatesAndGradients(
                costs, step_k_next, self._resolution)
            self._bfgs_man.updateBFGSandRHO()
            self._bfgs_man.updateMutableValuesAndSteps()
            self._previous_curve = self._flattest_curve

            # max_res = 0.2
            # Debug.log('step: {}   numruns: {}'.format(
            #     step_k_next, self._num_runs))
            # if (step_k_next >= self._num_runs):
            #     # decrease run count -> fewer runs since we're
            #     # on a strait away and can just ride it down.
            #     self.setRunResolution(self._resolution * 1.0)  # 1.2)  # 20%
            #     if (max_res <= self._resolution):
            #         self.setRunResolution(max_res)
            # else:
            #     # increase run count -> more runs since we're
            #     # starting to approach an extrema, and want finer detail
            #     self.setRunResolution(self._default_resolution)
        return continue_searching

    #############################################
    # WALKER ENTRY POINT                        #
    #############################################
    # This method name wasn't meant to be a joke.
    @rootClassMethod('walker.root_walker', 'RootWalker')
    def run(self, epsilon=0.001):
        # Set number of runs per step based on resolution percentage
        # initialize the search slope and the bfgs matrix.
        self._firstLaunchSet()
        # prevent infinite loops durring testing.
        test = 500
        # search condition trigger
        continue_searching = True
        while(continue_searching):
            self._iterations += 1
            Debug.log('' + '*' * 50 + '')
            # Launch info
            self._launchSet()
            # Calculate how far from target we are
            costs = self._calculateCosts()
            # find our next move
            continue_searching = self.determineSteps(
                costs, epsilon)
            if (test < 0):
                Debug.log('Loop exit from test iteration limit(100).')
                break
            test -= 1
        msg = 'Closest fit after {0._iterations}: {0._flattest_curve}'
        Debug.log(msg.format(self))
        Debug.log('Total run count: {0}'.format(self._total_run_count))
