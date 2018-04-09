
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
        self._itterations = 0
        super().__init__(**kwargs)

    @rootClassMethod
    def setMutables(self, mutables):
        self._mutables = mutables

    @rootClassMethod
    def setCostFuncs(self, cost_funcs):
        self._cost_funcs = cost_funcs

    @rootClassMethod
    def setLauncher(self, launcher):
        self._launcher = launcher

    #############################################
    # CALCULATE STEP SIZING                     #
    #############################################
    @rootClassMethod
    def _determineSteps(self, costs):
        self._flattest_curve = self._findSmallestCost(costs)
        Debug.log('flattest curve: ' + str(self._flattest_curve))
        # trim info not at the step of closest fit.
        dir_k_next = self._launcher.getDirNameFromRunName(
            self._flattest_curve[0])
        Debug.log('dir_k_next: ' + str(dir_k_next))
        # Archive the data from the cheapest run,
        # so we have a log of the path we took.
        self._launcher.archiveDir(dir_k_next)
        for c in costs.keys():
            if (dir_k_next not in c):
                # Clean the expensive keys from our dictionary.
                del costs[c]
        self._updateGradients(costs)
        # TODO: generate BFGS matrix
        # TODO: generate step sizes
        # TODO: call our launcher's data cleaning method

    @rootClassMethod
    def _findSmallestCost(self, costs):
        smallest_cost = ('None', float('-inf'))
        for c in costs.items():
            # don't need to check against gradient runs
            if('all' in c[0] and c[1] < smallest_cost[1]):
                smallest_cost = c
        return smallest_cost

    @rootClassMethod
    def _updateGradients(self, costs):
        # TODO: this function.
        for m in self._mutables:
            # get set of unique runs per variable name.
            xi_gradient_runs = \
                {x for x in costs.keys() if m.name.lower() in x.lower()}
            Debug.log('Gradient Runs: ' + str(xi_gradient_runs))
            # get the plus and minus run
            xi_plus = {x for x in xi_gradient_runs if 'plus' in x.lower()}[0]
            xi_minus = {x for x in xi_gradient_runs if 'minus' in x.lower()}[0]
            Debug.log('plus:  ' + str(xi_plus))
            Debug.log('minus: ' + str(xi_minus))
            # get offsets widths for calculating gradients
            step = self._launcher.getStepFromRunName(xi_plus)
            gradient_width = m.getGradientWidthAtStep(step)
            # Gradient per variable:
            #           F(x[i] + s[i]) - F(x[i] - s[i])
            # g(x[i]) = -------------------------------
            #                        2s[i]
            gradient = (costs[xi_plus] - costs[xi_minus])
            gradient /= (2.0 * gradient_width)

    #############################################
    # CREATING DATA                             #
    #############################################
    @rootClassMethod
    def _launchSet(self, num_runs=10):
        self._launcher.createRuns(self._mutables, num_runs)
        self._launcher.launch()

    #############################################
    # CALCULATING DIFFERENCE                    #
    #############################################
    @rootClassMethod
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
    @rootClassMethod
    def run(self, epsilon=1.0):
        # Main loop after first pass. Loop till acceptable convergance
        while(self._flattest_curve[1] > epsilon):
            self._launchSet()
            costs = self._calculateCosts()
            self._determineSteps(costs)
        Debug.log('Flattest Curve Found: ' + str(self._flattest_curve))
