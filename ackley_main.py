
# Local Imports
# from containers.mutable_data import MutableVar
from containers.gaussian_data import GaussianVar as MutableVar
from cost.ackley_cost import AckleyCostFunction
from launcher.ackley_launcher import AckleyLauncher


def getMutables():
    mutables = []
    mutables.append(MutableVar(
        name='x', start_value=10.4, step_width=-12.0, sigma=5.0))
    mutables.append(MutableVar(
        name='y', start_value=-10.4, step_width=-18.0, sigma=5.0))
    # mutables.append(MutableVar(
    #    name='z', start_value=5, step_width=0.1, sigma=0.5))
    return mutables


def getCostFuncs():
    tgt_run = './data/tgt.txt'
    cost_funcs = []
    cost_funcs.append(AckleyCostFunction(tgt_run=tgt_run))
    return cost_funcs


def getLauncher():
    base_file = 'hello_world.txt'
    data_dir = './data/'
    launcher = AckleyLauncher(base_file=base_file, data_dir=data_dir)
    return launcher
