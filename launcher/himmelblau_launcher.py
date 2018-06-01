
# Local imports
from launcher.root_launcher import RootLauncher
# from debug import Debug


# Multidimentional complex varient
class HimmelblauLauncher(RootLauncher):
    out_data_layout = 'Himmelblau = {value}'

    #############################################
    # INITIALIZATION                            #
    #############################################
    def __init__(self, **kwargs):
        super(HimmelblauLauncher, self).__init__(**kwargs)

    #############################################
    # CREATE RUN DATA                           #
    #############################################
    # Implemented in RootLauncher

    #############################################
    # LAUNCH RUNS                               #
    #############################################
    def _launchCard(self, card):
        x = []
        with open(card, 'r') as cardf:
            for line in iter(cardf.readline, ''):
                if('= ' in line.lower()):
                    x.append(float(line.partition('= ')[-1]))
        # https://en.wikipedia.org/wiki/Himmelblau's_function
        # Multidimentional complex varient:
        # f(x[0], .., x[n]) = (N-1|E|i=1) =
        # (x[i]^2 + x[i+1] - 11)^2 + (x[i] + x[i+1]^2 - 7)^2
        himmelblau = 0.0
        for i in range(len(x)):
            next = i + 1
            if (next < len(x)):
                himmelblau += (x[i]**2 + x[next] - 11.0)**2
                himmelblau += (x[i] + x[next]**2 - 7.0)**2

        # Write info out to the file
        outfile_name = card[:-4] + '.OUT'
        # Debug.log(outfile_name + ': ' + str(rosenbrock))
        with open(outfile_name, 'w') as outf:
            outf.write(self.out_data_layout.format(value=himmelblau))
        super(HimmelblauLauncher, self)._launchCard(card)
