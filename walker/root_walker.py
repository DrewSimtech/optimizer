
# Global imports
import shutil


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

    def setMutables(self, mutables):
        assert not hasattr(super(), '_setMutables')
        self._mutables = mutables

    def setCostFuncs(self, cost_funcs):
        assert not hasattr(super(), '_setCostFuncs')
        self._cost_funcs = cost_funcs

    def setLauncher(self, launcher):
        assert not hasattr(super(), '_setLauncher')
        self._launcher = launcher

    #############################################
    # CALCULATE STEP SIZING                     #
    #############################################
    def _determineSteps(self, costs):
        assert not hasattr(super(), '_determineSteps')
        self._flattest_curve = self._findSmallestCost(costs)
        print(self._flattest_curve)
        # trim info not at the step of closest fit.
        dir_k_next = self._launcher.getDirNameFromRunName(
            self._flattest_curve[0])
        print(dir_k_next)
        for c in costs.keys():
            if (dir_k_next not in c):
                # rmtree is dangerous cause it will remove the folder and
                # all of its contents. So be careful with what we remove.
                # Don't want to accedently clean an entire folder of code.
                shutil.rmtree(c)
                # Then clean the key from our dictionary.
                del costs[c]
        # TODO: archive the data from the cheapest run,
        # so we have a log of th path we took.
        self._updateGradients(costs)
        # TODO: generate BFGS matrix
        # TODO: generate step sizes

    def _findSmallestCost(self, costs):
        assert not hasattr(super(), '_findSmallestCost')
        smallest_cost = ('None', float('-inf'))
        for c in costs.items():
            # don't need to check against gradient runs
            if('all' in c[0] and c[1] < smallest_cost[1]):
                smallest_cost = c
        return smallest_cost

    def _updateGradients(self, costs):
        assert not hasattr(super(), '_updateGradients')
        # TODO: this function.
        for m in self._mutables:
            # get set of unique runs per variable name.
            xi_gradient_runs = \
                {x for x in costs.keys() if m.name.lower() in x.lower()}
            print(xi_gradient_runs)
            # get the plus and minus run
            xi_plus = {x for x in xi_gradient_runs if 'plus' in x.lower()}[0]
            xi_minus = {x for x in xi_gradient_runs if 'minus' in x.lower()}[0]
            print(xi_plus)
            print(xi_minus)

    #############################################
    # CREATING DATA                             #
    #############################################
    def _launchSet(self, num_runs=10):
        assert not hasattr(super(), '_launchSet')
        self._launcher.createRuns(self._mutables, num_runs)
        self._launcher.launch()

    #############################################
    # CALCULATING DIFFERENCE                    #
    #############################################
    def _calculateCosts(self):
        assert not hasattr(super(), '_calculateCosts')
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
    def run(self, epsilon=1.0):
        assert not hasattr(super(), 'run')
        # Main loop after first pass. Loop till acceptable convergance
        while(self._flattest_curve[1] > epsilon):
            self._launchSet()
            costs = self._calculateCosts()
            self._determineSteps(costs)
        print('Flattest Curve Found: ' + str(self._flattest_curve))
