
# Global Imports
import time
from numpy import random
# Local Imports
from walker.root_walker import RootWalker
from containers.mutable_data import MutableVar
from debug import Debug


class RandomWalker(RootWalker):

    #############################################
    # INITIALIZATION                            #
    #############################################
    def __init__(self, loops=10, **kwargs):
        print('RandomWalker.__init__()')
        self.setRunLoops(loops)
        self._extrema_value = []
        super(RandomWalker, self).__init__(**kwargs)

    def _storeDefaults(self):
        # Called from super().__init__()
        print('RandomWalker._storeDefaults()')
        super(RandomWalker, self)._storeDefaults()
        self._default['run_loops'] = self._run_loops

    def _reInit(self):
        super(RandomWalker, self)._reInit()
        self._starting_locations = [self._default['mutables']]
        self.setRunLoops(self._default['run_loops'])
        self._extrema_value = []

    def _reInitSuperOnly(self):
        super(RandomWalker, self)._reInit()

    def setRunLoops(self, loops):
        self._run_loops = loops

    #############################################
    # WALKER ENTRY POINT                        #
    #############################################
    def _updateStartingLocation(self):
        # This pulls a random restart location with a guassian distribution
        updated_loc = []
        for m in self._bfgs_man.getMutables():
            mean, sigma = m.getDistribution()
            gaussian_draw = random.normal(mean, sigma)
            updated_loc.append(MutableVar(m.name, gaussian_draw))
        # TODO: check to ensure we haven't draw this same coordinate before.
        # did someone say recursion?
        pass
        # Set our new starting coordinates
        self.setMutables(updated_loc)

    #############################################
    # WALKER ENTRY POINT                        #
    #############################################
    def run(self, **kwargs):
        # ==============================================================
        # The basic strategy for this is to create a loop
        # where we alternate calling super().run() and self._reInit().
        # After each _reInit() we can update the start coordinates of
        # our mutable group to achieve a new starting location before
        # we call run() again.
        # ==============================================================

        # store our initial initial location
        self._starting_locations = [self._default['mutables']]
        # log time
        start = time.time()
        start_str = time.ctime()
        Debug.log('random start  : ' + str(start_str))
        while(self._run_loops):
            Debug.log('loops: ' + str(self._run_loops))
            print('loops: ' + str(self._run_loops))
            # Do a full run.
            super(RandomWalker, self).run()
            self._extrema_value.append(
                (self._flattest_curve, self._bfgs_man.getMutables()))
            # separate the runs in the debug log
            Debug.log('\n')
            Debug.log('/\n' * 10)
            # reinit
            self._reInitSuperOnly()
            # update the starting locations for the next run
            self._updateStartingLocation()
            # decrement the loop counter
            self._run_loops -= 1
            # then back to the top
        end = time.time()
        Debug.log('random start  : ' + str(start_str))
        Debug.log('random end    : ' + str(time.ctime()))
        Debug.log('random elapsed: ' + str(end - start) + 's')
        Debug.log('\nextrema found :\n')
        for loc in sorted(self._extrema_value, key=lambda x: x[0][1]):
            Debug.log('   Coord:\n' + str(loc[1]))
            Debug.log('   Value: ' + str(loc[0]))
            Debug.log('\n')
