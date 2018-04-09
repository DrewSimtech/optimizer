
# Global imports
from math import exp, sqrt, cos, pi, e
# Local imports
from launcher.root_launcher import RootLauncher


class AckleyLauncher(RootLauncher):
    out_data_layout = 'Ackley = {value}'

    #############################################
    # INITIALIZATION                            #
    #############################################
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

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
            primary = 0.0
            secondary = 0.0
            with open(c, 'r') as cardf:
                for line in iter(cardf.readline, ''):
                    if ('=' in line):
                        info = float(line.partition('= ')[-1])
                        # x^2 + .. + z^2
                        primary += info * info
                        # cos(2 pi x) + .. + cos(2 pi z)
                        secondary += cos(2.0 * pi * info)

            # https://en.wikipedia.org/wiki/Ackley_function
            ackley_prime = exp(-0.2 * sqrt(0.5 * primary))
            ackley_second = exp(0.5 * secondary)
            ackley = -20.0 * ackley_prime - ackley_second + e + 20.0
            print('{} = {} - {}'.format(ackley, ackley_prime, ackley_second))

            # Write info out to the file
            outfile_name = c[:-4] + '.OUT'
            with open(outfile_name, 'w') as outf:
                outf.write(self.out_data_layout.format(value=ackley))
        super().launch()
