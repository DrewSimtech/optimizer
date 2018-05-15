
# Local Imports
from containers.mutable_data import MutableVar
from cost.rosenbrock_cost import RosenbrockCostFunction
from launcher.rosenbrock_md_launcher import RosenbrockMDLauncher


def getMutables():
    mutables = []
    mutables.append(MutableVar(name='rb_w', start_value=3.2))
    mutables.append(MutableVar(name='rb_x', start_value=5.0))
    mutables.append(MutableVar(name='rb_y', start_value=4.0))
    mutables.append(MutableVar(name='rb_z', start_value=4.6))
    # mutables.append(
    #     MutableVar(name='rb_x', start_value=5.0, step_width=10.5))
    # mutables.append(
    #     MutableVar(name='rb_y', start_value=3.0, step_width=6.5))
    return mutables


def getCostFuncs():
    tgt_run = './data/tgt.txt'
    cost_funcs = []
    cost_funcs.append(RosenbrockCostFunction(tgt_run=tgt_run))
    return cost_funcs


def getLauncher():
    base_file = 'hello_world.txt'
    data_dir = './data/'
    launcher = RosenbrockMDLauncher(base_file=base_file, data_dir=data_dir)
    return launcher
