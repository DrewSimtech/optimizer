from walker.root_walker import RootWalker


class Walker(RootWalker):
    '''Base functionality for the walker class.
    Determines stepsize for runs.'''

    #############################################
    # INITIALIZATION                            #
    #############################################
    def __init__(self, **kwargs):
        super(Walker, self).__init__(**kwargs)

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
