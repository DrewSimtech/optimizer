
# Local imports
from launcher.root_launcher import RootLauncher
# from debug import Debug


class RosenbrockLauncher(RootLauncher):
    out_data_layout = 'Rosenbrock = {value}'

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
    def _launchCard(self, card):
        a = 1
        b = 100
        with open(card, 'r') as cardf:
            for line in iter(cardf.readline, ''):
                if('rb_x = ' in line.lower()):
                    rb_x = float(line.partition('= ')[-1])
                if('rb_y = ' in line.lower()):
                    rb_y = float(line.partition('= ')[-1])
        # https://en.wikipedia.org/wiki/Rosenbrock_function
        # f(x,y) = (a-x)^2 + b(y-x^2)^2
        rosenbrock = (a - rb_x)**2 + b * (rb_y - rb_x**2)**2

        # Write info out to the file
        outfile_name = card[:-4] + '.OUT'
        # Debug.log(outfile_name + ': ' + str(rosenbrock))
        with open(outfile_name, 'w') as outf:
            outf.write(self.out_data_layout.format(value=rosenbrock))
        super()._launchCard(card)
