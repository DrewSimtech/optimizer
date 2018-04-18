
# Global Package Imports
import numpy as np
# Local package imports
from debug import Debug


class BFGSManager(object):

    #############################################
    # CLASS INITIALIZATION                      #
    #############################################
    def __init__(self):
        self._states = []
        self._gradients = []
        self._bfgs = []
        self._rho = []

    def setMutables(self, mutables):
        self._mutables = mutables

    def getMutables(self):
        # return a slice of the whole array so it cant be modified
        return self._mutables[:]

    #############################################
    # INITIALIZING MATRIX DATA                  #
    #############################################
    # These calculations are performed after the first run has
    # completed. It requires two runs to be performed
    # in order to build a set of data to iterate upon.
    def initBaselineData(self, prime_costs, first_costs,
                         step, resolution):
        self._initStatesAndGradients(
            prime_costs, first_costs, step, resolution)
        self._initBFGS()
        self.updateMutableValuesAndSteps()

    def _initStatesAndGradients(self, prime_costs, first_costs,
                                step, resolution):
        self.updateStatesAndGradients(prime_costs, 0, resolution)
        self.updateStatesAndGradients(first_costs, step, resolution)

    def _initBFGS(self):
        # initial matrix B[0] = I where diagonal length = number of mutables
        self._bfgs.append(np.matrix(np.identity(len(self._mutables))))
        self.updateBFGSandRHO()

    #############################################
    # CALCULATE STEP SIZING                     #
    #############################################
    def findSmallestCost(self, costs):
        smallest_cost = ('None', float('inf'))
        for c in costs.items():
            # don't need to check against gradient runs
            if('all' in c[0] and abs(c[1]) < abs(smallest_cost[1])):
                smallest_cost = c
                Debug.log('smaller: ' + str(c))
        return smallest_cost

    def updateStatesAndGradients(self, costs, step, resolution):
        debug_write = False
        # append the next set of states and gradients
        self._states.append({})
        self._gradients.append({})
        next = -1
        for m in self._mutables:
            # get set of plus and minus runs per variable name.
            xi_runs = {x for x in costs.keys() if m.name.lower() in x.lower()}
            Debug.log('costs:\n' + str(xi_runs), debug_write)
            xi_plus = list(x for x in xi_runs if 'plus' in x.lower())[0]
            Debug.log('xip: ' + str(xi_plus), debug_write)
            xi_minus = list(x for x in xi_runs if 'minus' in x.lower())[0]
            Debug.log('xim: ' + str(xi_minus), debug_write)
            # get offsets widths for calculating gradients
            Debug.log('step: ' + str(step))
            gradient_width = m.getGradientWidthAtStep(step, resolution)
            Debug.log('grad: ' + str(gradient_width), debug_write)
            # ======================================================= #
            # calculate gradient per variable:                        #
            #           F(x[i] + s[i]) - F(x[i] - s[i])               #
            # g(x[i]) = -------------------------------               #
            #                        2s[i]                            #
            # where x is the value of the mutable at the current step #
            # s is the gradient width at the same step                #
            # ======================================================= #
            Debug.log('costs[xip]: ' + str(costs[xi_plus]), debug_write)
            Debug.log('costs[xim]: ' + str(costs[xi_minus]), debug_write)
            gradient = (costs[xi_plus] - costs[xi_minus])
            gradient /= (2.0 * gradient_width)
            msg = 'full: {0}\n({1} - {2}) / (2.0 * {3})\n{4} / {5}'
            Debug.log(msg.format(gradient,
                                 costs[xi_plus],
                                 costs[xi_minus],
                                 gradient_width,
                                 costs[xi_plus] - costs[xi_minus],
                                 2.0 * gradient_width,
                                 ), debug_write)
            # append k+1 state and gradient to the list\
            Debug.log('step: ' + str(step) + ' resolution: ' + str(resolution))
            Debug.log('Value: ' + str(m.getValueAtStep(step, resolution)))
            self._states[next][m.name] = m.getValueAtStep(step, resolution)
            self._gradients[next][m.name] = gradient
        Debug.log('states:\n' + str(self._states))
        Debug.log('grades:\n' + str(self._gradients))

    def updateBFGSandRHO(self):
        # ================================================================ #
        # The Broyden Fletcher Goldfarb Shanno (BFGS) update:              #
        # B[0] = I, where diagonal length = number of mutables             #
        #                                                                  #
        #                 (B[k] s[k] s[k]t B[k])   (y[k] y[k]t)            #
        # B[k+1] = B[k] -   (s[k]t B[k] s[k])    + (y[k]t s[k])            #
        #                                                                  #
        # where the 1xN matrices of "y" and "s" are:                       #
        # y[k] = gradients[k+1] - gradients[k]                             #
        #           and                                                    #
        # s[k] = alpha[k] rho[k] = mutable_values[k+1] - mutable_values[k] #
        # ================================================================ #

        debug_write = False

        # create and format np matricies using passed in dicts of data
        # use .T to get them into 1xN size matricies
        def getMatrixOfValues(info):
            mat = []
            name_list = ''
            for m in self._mutables:
                name_list += m.name + ' . '
                mat.append(info[m.name])
            Debug.log('Names: ' + name_list, debug_write)
            return np.matrix(mat).T

        # create y[k]
        gkc = getMatrixOfValues(self._gradients[-2])
        gkn = getMatrixOfValues(self._gradients[-1])
        yk = np.subtract(gkn, gkc)
        Debug.log('yk:\n' + str(yk), debug_write)
        # create s[k]
        xkc = getMatrixOfValues(self._states[-2])
        xkn = getMatrixOfValues(self._states[-1])
        sk = np.subtract(xkn, xkc)
        Debug.log('sk:\n' + str(sk), debug_write)

        # cache B[k] from our list
        bk = self._bfgs[-1]
        # break up calculation for debugging
        # first section
        top = bk * sk * sk.T * bk
        bot = sk.T * bk * sk
        first = top / bot
        # second section
        top = yk * yk.T
        bot = yk.T * sk
        second = top / bot
        # combine components
        bkn = bk - first + second
        # append it to our list
        self._bfgs.append(bkn)

        # Next step size is a function of the Hessian and the gradient
        # rho[k+1] = -B[k+1]i g[k+1]
        rho = -bkn.I * gkn
        # sort the rho values into a map
        self._rho.append({})
        rho_gen = (x for x in rho.A1)
        rho_names = ''
        for m in self._mutables:
            rho_names += m.name + ' . '
            self._rho[-1][m.name] = next(rho_gen)
        Debug.log('Rho names: ' + rho_names, debug_write)
        Debug.log('rho:\n' + str(self._rho), debug_write)

    def updateMutableValuesAndSteps(self):
        for m in self._mutables:
            m.setCurValue(self._states[-1][m.name])
            m.setCurStepWidth(self._rho[-1][m.name])
            Debug.log(str(m))