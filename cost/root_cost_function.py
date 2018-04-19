
# Local package imports
from debug import Debug, rootClassMethod


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

    @rootClassMethod('cost.root_cost_function', 'RootCostFunction')
    def setTargetFile(self, tgt_run):
        Debug.log(tgt_run)
        self._tgt_run = tgt_run

    #############################################
    # COST FUNCTION                             #
    #############################################
    @rootClassMethod('cost.root_cost_function', 'RootCostFunction')
    def calculate(self, cur_run_file):
        '''determine the value of each run'''
        # Get data to compare
        self._cost = self._getData(cur_run_file)
        # Apply the weight to the cost function
        self._cost *= self.__weight
        Debug.log('cost: {}'.format(self._cost), False)
        return self._cost

    @rootClassMethod('cost.root_cost_function', 'RootCostFunction')
    def calculateRelative(self, cur_run_file):
        '''determine the value of each run'''
        # Get data to compare
        cur_info = self._getData(cur_run_file)
        tgt_info = self._getData(self._tgt_run)
        # Calculate difference
        self._cost = tgt_info - cur_info  # abs()?
        # Apply the weight to the cost function
        self._cost *= self.__weight
        if (False):  # ('all' in cur_run_file):
            Debug.log('cost: {} = {} - {}'.format(
                self._cost,
                tgt_info,
                cur_info,
            ))
        return self._cost

    #############################################
    # DATA RETRIEVAL                            #
    #############################################
    @rootClassMethod('cost.root_cost_function', 'RootCostFunction')
    def _getData(self, from_file):
        # implement in child classes
        pass
