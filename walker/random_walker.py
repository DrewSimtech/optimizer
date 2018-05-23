from walker.root_walker import RootWalker


class RandomWalker(RootWalker):

    #############################################
    # INITIALIZATION                            #
    #############################################
    def __init__(self, loops, **kwargs):
        self.setRunLoops(loops)
        self._starting_locations = {}
        super(RandomWalker, self).__init__(**kwargs)

    def setRunLoops(self, loops):
        self._run_loops = loops

    #############################################
    # WALKER ENTRY POINT                        #
    #############################################
    def run(self, **kwargs):
        pass
