
# Local Imports
from containers.mutable_data import MutableVar
from cost.pythag_cost import PythagCostFunction
from launcher.pythag_launcher import PythagLauncher


# Set up the list of mutable variables to pass to the walker
def getMutables():
    mutables = []
    mutables.append(MutableVar(name='x', start_value=3, step_width=1))
    mutables.append(MutableVar(name='y', start_value=4, step_width=1))
    mutables.append(MutableVar(name='z', start_value=5, step_width=1))
    return mutables


# Set up the list of cost functions to pass to the walker
def getCostFuncs():
    tgt_run = './data/tgt.txt'
    cost_funcs = []
    cost_funcs.append(PythagCostFunction(tgt_run=tgt_run))
    return cost_funcs


# Set up a single launcher
def getLauncher():
    base_file = 'hello_world.txt'
    data_dir = './data/'
    launcher = PythagLauncher(base_file=base_file, data_dir=data_dir)
    return launcher
