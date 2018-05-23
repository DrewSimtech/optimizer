
# Local Imports
from containers.mutable_data import MutableVar
from cost.himmelblau_cost import HimmelblauCostFunction
from launcher.himmelblau_launcher import HimmelblauLauncher


def getMutables():
    mutables = []
    mutables.append(MutableVar(name='x', start_value=-1.1))
    mutables.append(MutableVar(name='y', start_value=-1.0))
    # mutables.append(MutableVar(name='z', start_value=0.9))
    # mutables.append(MutableVar(name='w', start_value=0.8))
    return mutables


def getCostFuncs():
    tgt_run = './data/tgt.txt'
    cost_funcs = []
    cost_funcs.append(HimmelblauCostFunction(tgt_run=tgt_run))
    return cost_funcs


def getLauncher():
    base_file = 'hello_world.txt'
    data_dir = './data/'
    launcher = HimmelblauLauncher(base_file=base_file, data_dir=data_dir)
    return launcher
