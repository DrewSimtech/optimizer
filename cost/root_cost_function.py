
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

    def setTargetFile(self, tgt_run):
        # Defensive programming
        assert not hasattr(super(), 'setDataFiles')
        self._tgt_run = tgt_run

    #############################################
    # COST FUNCTION                             #
    #############################################
    def calculate(self, cur_run_file):
        '''determine the value of each run'''
        # Defensive programming. Make sure we're the last
        # super()._calculate call. We dont want attribute errors.
        assert not hasattr(super(), '_calculate')
        # Apply the weight to the cost function
        self._cost *= self.__weight
        return self._cost

    #############################################
    # DATA RETRIEVAL                            #
    #############################################
    def _getData(self, from_file):
        assert not hasattr(super(), '_getData')
