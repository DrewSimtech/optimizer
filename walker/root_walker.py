
# Local package imports
from walker.bfgs_manager import BFGSManager
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
        self._iterations = 0
        super().__init__(**kwargs)

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

    #############################################
    # BUILDING THE INITIAL BFGS MATRIX          #
    #############################################
    # Done after the first runset has been launched.
    @rootClassMethod('walker.root_walker', 'RootWalker')
    def _setupBFGSManager(self, costs, resolution):
        # grab the first runset
        init_run_batch = self._launcher.getLatestRunset()
        # grab runs at k[0]
        prime_run_dir = self._launcher.getDirNameFromRunName(
            init_run_batch[0])
        prime_costs = \
            dict((x, y) for x, y in costs.items() if prime_run_dir in x)
        # grab runs at k[1]: means we need to find the smallest cost run
        self._flattest_curve = self._bfgs_man.findSmallestCost(costs)
        first_run_step = self._launcher.getStepFromRunName(
            self._flattest_curve[0])
        first_run_dir = self._launcher.getDirNameFromRunName(
            self._flattest_curve[0])
        first_costs = \
            dict((x, y) for x, y in costs.items() if first_run_dir in x)
        # init baseline using the data we've just gathered
        self._bfgs_man.initBaselineData(
            prime_costs, first_costs, first_run_step, resolution)
        self._iterations = 0
        self._previous_curve = ('None', float('NaN'))

    #############################################
    # CREATING DATA                             #
    #############################################
    @rootClassMethod('walker.root_walker', 'RootWalker')
    def _launchSet(self, num_runs=10, resolution=0.1):
        self._launcher.createRuns(
            self._bfgs_man.getMutables(), num_runs, resolution)
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
    # CALCULATE STEP SIZING                     #
    #############################################
    def determineSteps(self, costs, resolution, epsilon):
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
        if (abs(self._flattest_curve[1]) < epsilon):
            msg = "ENDING RUN:: We're within epsilon({}) of our target."
            Debug.log(msg.format(epsilon))
            continue_searching = False
        # if the same step is the flattest twice: then we've hit local minima
        elif (self._flattest_curve[1] == self._previous_curve[1]):
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
            self._bfgs_man.updateStatesAndGradients(
                costs, step_k_next, resolution)
            self._bfgs_man.updateBFGSandRHO()
            self._bfgs_man.updateMutableValuesAndSteps()
            self._previous_curve = self._flattest_curve
        return continue_searching

    #############################################
    # WALKER ENTRY POINT                        #
    #############################################
    # This method name wasn't meant to be a joke.
    @rootClassMethod('walker.root_walker', 'RootWalker')
    def run(self, resolution=0.01, epsilon=0.001):
        # Set number of runs per step based on resolution percentage
        num_runs = int(1.0 / resolution)
        first_pass = True
        test = 15
        continue_searching = True
        while(continue_searching):
            Debug.log('')
            Debug.log('*' * 50)
            Debug.log('')
            # Launch info
            self._launchSet(num_runs, resolution)
            # Calculate how far from target we are
            costs = self._calculateCosts()
            if (first_pass):
                # initializing the baseline bfgs requires costs
                self._setupBFGSManager(costs, resolution)
                first_pass = False
            # find our next move
            continue_searching = self.determineSteps(
                costs, resolution, epsilon)
            self._iterations += 1
            if (test < 0):
                Debug.log('Loop exit from test iteration limit(15).')
                break
            test -= 1
        msg = 'Closest fit after {0._iterations}: {0._flattest_curve}'
        Debug.log(msg.format(self))
