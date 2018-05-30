
# global package imports
from math import sqrt
# local package imports
from launcher.root_launcher import RootLauncher


# Class definition
class PythagLauncher(RootLauncher):
    out_data_layout = 'Pythag = {value}'

    #############################################
    # INITIALIZATION                            #
    #############################################
    def __init__(self, **kwargs):
        super(PythagLauncher, self).__init__(**kwargs)

    def __repr__(self):
        # Has no additional kwargs, so it just replaces super()'s
        # class name with our own.
        msg = super(PythagLauncher, self).__repr__()
        msg = 'RosenbrockLauncher(' + msg.partition('(')[-1]
        return msg

    #############################################
    # CREATE RUN DATA                           #
    #############################################
    # Implemented in RootLauncher

    #############################################
    # LAUNCH RUNS                               #
    #############################################
    def getLatestRunset(self):
        latest = list(x.replace('.CRD', '.OUT') for x in self._cards_to_launch)
        return latest

    def launch(self):
        for c in self._cards_to_launch:
            discriminant = 0.0
            with open(c, 'r') as cardf:
                for line in iter(cardf.readline, ''):
                    if ('=' in line):
                        info = float(line.partition('= ')[-1])
                        discriminant += info * info
            pythag = sqrt(discriminant)
            outfile_name = c[:-4] + '.OUT'
            with open(outfile_name, 'w') as outf:
                outf.write(self.out_data_layout.format(value=pythag))
        super(PythagLauncher, self).launch()
