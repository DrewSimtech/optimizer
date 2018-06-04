from walker.root_walker import RootWalker


class StdWalker(RootWalker):
    '''Base functionality for the walker class.
    Determines stepsize for runs.'''

    #############################################
    # INITIALIZATION                            #
    #############################################
    def __init__(self, **kwargs):
        super(StdWalker, self).__init__(**kwargs)

    #############################################
    # CALCULATE STEP SIZE                       #
    #############################################
    # Implemented in RootWalker

    #############################################
    # SUBMIT RUNS                               #
    #############################################
    # Implemented in RootWalker

    #############################################
    # WALKER ENTRY POINT                        #
    #############################################
    # Implemented in RootWalker
