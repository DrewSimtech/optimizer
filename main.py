
# Global imports
import os
import shutil
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
    # prelaunch
    clearPreviousRunData()

    # setup
    mutables = getMutables()
    cost_funcs = getCostFuncs()
    launcher = getLauncher()
    walk = Walker(mutables=mutables, cost_funcs=cost_funcs, launcher=launcher)

    # launch
    walk.run()


# entry point
if __name__ == '__main__':
    Debug.initialize()
    main()
