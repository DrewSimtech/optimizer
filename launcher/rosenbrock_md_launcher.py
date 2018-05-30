
# Local imports
from launcher.root_launcher import RootLauncher
# from debug import Debug


# Multidimentional complex varient
class RosenbrockMDLauncher(RootLauncher):
    out_data_layout = 'Rosenbrock = {value}'

    #############################################
    # INITIALIZATION                            #
    #############################################
    def __init__(self, **kwargs):
        super(RosenbrockMDLauncher, self).__init__(**kwargs)

    def __repr__(self):
        # Has no additional kwargs, so it just replaces super()'s
        # class name with our own.
        msg = super(RosenbrockMDLauncher, self).__repr__()
        msg = 'RosenbrockMDLauncher(' + msg.partition('(')[-1]
        return msg

    #############################################
    # CREATE RUN DATA                           #
    #############################################
    # Implemented in RootLauncher

    #############################################
    # LAUNCH RUNS                               #
    #############################################
    def _launchCard(self, card):
        a = 1.0
        b = 100.0
        x = []
        with open(card, 'r') as cardf:
            for line in iter(cardf.readline, ''):
                if('= ' in line.lower()):
                    x.append(float(line.partition('= ')[-1]))
        # https://en.wikipedia.org/wiki/Rosenbrock_function
        # Multidimentional complex varient:
        # f(x[0], .., x[n]) = (N-1|E|i=1) = [b(x[i+1] - x[i]^2) + (a - x[i])^2]
        rosenbrock = 0.0
        for i in range(len(x)):
            next = i + 1
            if (next < len(x)):
                rosenbrock += b * (x[next] - x[i]**2)**2 + (a - x[i])**2

        # Write info out to the file
        outfile_name = card[:-4] + '.OUT'
        # Debug.log(outfile_name + ': ' + str(rosenbrock))
        with open(outfile_name, 'w') as outf:
            outf.write(self.out_data_layout.format(value=rosenbrock))
        super(RosenbrockMDLauncher, self)._launchCard(card)
