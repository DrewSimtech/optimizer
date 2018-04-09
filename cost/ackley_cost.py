
# Local imports
from cost.root_cost_function import RootCostFunction


# Class definition
class AckleyCostFunction(RootCostFunction):

    #############################################
    # INITIALIZATION                            #
    #############################################
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    #############################################
    # COST FUNCTION                             #
    #############################################
    def calculate(self, cur_run_file):
        # Get data to compare
        cur_info = self._getData(cur_run_file)
        tgt_info = self._getData(self._tgt_run)
        # Calculate difference
        self._cost = tgt_info - cur_info  # abs()?
        # super
        super().calculate(cur_run_file)
        return self._cost

    #############################################
    # DATA RETRIEVAL                            #
    #############################################
    def _getData(self, from_file):
        # open the file and read the info from it
        with open(from_file, 'r') as ff:
            for line in iter(ff.readline, ''):
                if ('ackley' in line.lower()):
                    return float(line.partition('= ')[-1])
        # this specific child class's implementation doesn't call super()
