
# Local package imports
from debug import rootClassMethod


class RootCostFunction(object):
    '''Information for ranking.'''

    #############################################
    # INITIALIZATION                            #
    #############################################
    def __init__(self, cur_run=None, tgt_run=None, weight=1.0, **kwargs):
        '''set up the class'''
        # Weight is a scalar to the cost.
        self.__weight = weight
        # Filenames for the data to compare
        self.setTargetFile(tgt_run)
        # pass on init
        super().__init__(**kwargs)

    @rootClassMethod
    def setTargetFile(self, tgt_run):
        self._tgt_run = tgt_run

    #############################################
    # COST FUNCTION                             #
    #############################################
    @rootClassMethod
    def calculate(self, cur_run_file):
        '''determine the value of each run'''
        # Apply the weight to the cost function
        self._cost *= self.__weight
        return self._cost

    #############################################
    # DATA RETRIEVAL                            #
    #############################################
    @rootClassMethod
    def _getData(self, from_file):
        pass
