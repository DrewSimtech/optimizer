
# Local imports
from cost.root_cost_function import RootCostFunction


# Class definition
class AckleyCostFunction(RootCostFunction):

    #############################################
    # INITIALIZATION                            #
    #############################################
    def __init__(self, **kwargs):
        super(AckleyCostFunction, self).__init__(**kwargs)

    #############################################
    # COST FUNCTION                             #
    #############################################
    # implemented in RootCostFunction

    #############################################
    # DATA RETRIEVAL                            #
    #############################################
    def _getData(self, from_file):
        # open the file and read the info from it
        with open(from_file, 'r') as ff:
            for line in iter(ff.readline, ''):
                if ('ackley' in line.lower()):
                    return float(line.partition('= ')[-1])
        # this implementation doesn't call super()
