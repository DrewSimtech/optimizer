
# Local package imports
from containers.mutable_data import MutableVar


class GaussianVar(MutableVar):

    def __init__(self, start_value, sigma, **kwargs):
        self._sigma = sigma
        self._mean = start_value
        super(GaussianVar, self).__init__(start_value=start_value, **kwargs)

    def getDistribution(self):
        return self._mean, self._sigma
