
# Local imports
from ackley_main import getMutables, getCostFuncs, getLauncher
# from pythag_main import getMutables, getCostFuncs, getLauncher
from walker.walker import Walker


def main():
    mutables = getMutables()
    cost_funcs = getCostFuncs()
    launcher = getLauncher()
    walk = Walker(mutables=mutables, cost_funcs=cost_funcs, launcher=launcher)
    walk.run()


# entry point
if __name__ == '__main__':
    main()
