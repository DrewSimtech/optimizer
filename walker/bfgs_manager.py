
# Global Package Imports
import numpy as np
# Local package imports
from debug import Debug


class BFGSManager(object):

    #############################################
    # CLASS INITIALIZATION                      #
    #############################################
    def __init__(self):
        self.iterations = 0
        self.states = []
        self.gradients = []
        self.bfgs = []
        self.rho = []

    #############################################
    # INITIALIZING MATRIX DATA                  #
    #############################################
    # These calculations are performed after the first run has
    # completed. It requires two runs to be performed
    # in order to build a set of data to iterate upon.
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

    def _initStatesAndGradients(self, prime_costs, first_costs, resolution):
        self._updateStatesAndGradients(prime_costs, resolution)
        self._updateStatesAndGradients(first_costs, resolution)

    def _initBFGS(self):
        # initial matrix B[0] = I where diagonal length = number of mutables
        self.bfgs.append(np.matrix(np.identity(len(self._mutables))))
        self._updateBFGSandRHO()
