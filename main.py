
# Global imports
import os
import shutil
import time
# Local imports
from rosenbrock_main import getMutables, getCostFuncs, getLauncher
# from ackley_main import getMutables, getCostFuncs, getLauncher
# from pythag_main import getMutables, getCostFuncs, getLauncher
from walker.walker import Walker
from debug import Debug


def clearPreviousRunData():
    for path in os.listdir('data'):
        if('step' in path):
            path = os.path.join('data', path)
            shutil.rmtree(path)


def main():
    start = time.time()
    print('start  : ' + str(time.ctime()))
    # prelaunch
    clearPreviousRunData()

    # setup
    mutables = getMutables()
    cost_funcs = getCostFuncs()
    launcher = getLauncher()
    walk = Walker(mutables=mutables, cost_funcs=cost_funcs, launcher=launcher)

    # launch
    walk.run()
    end = time.time()
    print('end    : ' + str(time.ctime()))
    print('elapsed: ' + str(end - start) + 's')


# entry point
if __name__ == '__main__':
    Debug.initialize()  # file_only=False)
    main()
