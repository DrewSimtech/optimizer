
# Local Imports
from containers.mutable_data import MutableVar
from cost.rosenbrock_cost import RosenbrockCostFunction
from launcher.rosenbrock_launcher import RosenbrockLauncher


def getMutables():
    mutables = []
    mutables.append(MutableVar(name='rb_x', start_value=0.50, step_width=-0.5))
    mutables.append(MutableVar(name='rb_y', start_value=3.0, step_width=-0.5))
    # mutables.append(MutableVar(name='z', start_value=5, step_width=0.1))
    return mutables


def getCostFuncs():
    tgt_run = './data/tgt.txt'
    cost_funcs = []
    cost_funcs.append(RosenbrockCostFunction(tgt_run=tgt_run))
    return cost_funcs


def getLauncher():
    base_file = 'hello_world.txt'
    data_dir = './data/'
    launcher = RosenbrockLauncher(base_file=base_file, data_dir=data_dir)
    return launcher
