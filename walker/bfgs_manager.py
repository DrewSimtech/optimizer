
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
        self._debug_write = False

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
    def initBaselineData(self, prime, first):
        # calc out the new gradients
        self.updateStatesAndGradients(prime, step=0.0, resolution=0.0)
        self.updateStatesAndGradients(first, step=0.0, resolution=0.0)
        # we have to manualy update the states here because i messed up the
        # architecture and this is easier.
        # TODO: rewrite this so we dont have to overwrite the states with
        # this jank nonsense code
        for m in self._mutables:
            grad = m.getGradientWidthAtStep(0.0, 0.0)
            val = m.getValueAtStep(0.0, 0.0)
            self._states[0][m.name] = val - grad
            self._states[1][m.name] = val + grad
        Debug.log('new states:\n' + str(self._states))
        self._bfgs.append(np.matrix(np.identity(len(self._mutables))))
        self.updateBFGSandRHO()
        self.updateMutableValuesAndSteps()

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
        # append the next set of states and gradients
        self._states.append({})
        self._gradients.append({})
        next = -1
        for m in self._mutables:
            # get set of plus and minus runs per variable name.
            xi_runs = list(
                x for x in costs.keys() if m.name.lower() in x.lower())
            Debug.log('costs:\n' + str(xi_runs), self._debug_write)
            xi_plus = list(x for x in xi_runs if 'plus' in x.lower())[0]
            Debug.log('xip: ' + str(xi_plus), self._debug_write)
            xi_minus = list(x for x in xi_runs if 'minus' in x.lower())[0]
            Debug.log('xim: ' + str(xi_minus), self._debug_write)
            # get offsets widths for calculating gradients
            Debug.log('step: ' + str(step), self._debug_write)
            gradient_width = m.getGradientWidthAtStep(step, resolution)
            Debug.log('grad: ' + str(gradient_width), self._debug_write)
            # ======================================================= #
            # calculate gradient per variable:                        #
            #           F(x[i] + s[i]) - F(x[i] - s[i])               #
            # g(x[i]) = -------------------------------               #
            #                        2s[i]                            #
            # where x is the value of the mutable at the current step #
            # s is the gradient width at the same step                #
            # ======================================================= #
            Debug.log('costs[xip]: ' + str(costs[xi_plus]), self._debug_write)
            Debug.log('costs[xim]: ' + str(costs[xi_minus]), self._debug_write)
            gradient = (costs[xi_plus] - costs[xi_minus])
            gradient /= (2.0 * gradient_width)
            msg = 'full: {0}\n({1} - {2}) / (2.0 * {3})\n{4} / {5}'
            Debug.log(msg.format(gradient,
                                 costs[xi_plus],
                                 costs[xi_minus],
                                 gradient_width,
                                 costs[xi_plus] - costs[xi_minus],
                                 2.0 * gradient_width,
                                 ), self._debug_write)
            # append k+1 state and gradient to the list\
            val = m.getValueAtStep(step, resolution)
            Debug.log('val: ' + str(val), self._debug_write)
            self._states[next][m.name] = val
            self._gradients[next][m.name] = gradient
        Debug.log('states:\n' + str(self._states), self._debug_write)
        Debug.log('grades:\n' + str(self._gradients), self._debug_write)

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

        # create and format np matricies using passed in dicts of data
        # use .T to get them into 1xN size matricies
        def getMatrixOfValues(info):
            mat = []
            name_list = ''
            for m in self._mutables:
                name_list += m.name + ' . '
                mat.append(info[m.name])
            Debug.log('Names: ' + name_list, self._debug_write)
            return np.matrix(mat).T

        # create y[k]
        gkc = getMatrixOfValues(self._gradients[-2])
        gkn = getMatrixOfValues(self._gradients[-1])
        yk = np.subtract(gkn, gkc)
        Debug.log('yk:\n' + str(yk), self._debug_write)
        # create s[k]
        xkc = getMatrixOfValues(self._states[-2])
        xkn = getMatrixOfValues(self._states[-1])
        sk = np.subtract(xkn, xkc)
        Debug.log('sk:\n' + str(sk), self._debug_write)

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
        Debug.log('Rho names: ' + rho_names, self._debug_write)
        Debug.log('rho:\n' + str(self._rho), self._debug_write)

    def updateMutableValuesAndSteps(self):
        for m in self._mutables:
            m.setCurValue(self._states[-1][m.name])
            m.setCurStepWidth(self._rho[-1][m.name])
            Debug.log(str(m))

    def updateMutableSteps(self):
        for m in self._mutables:
            m.setCurStepWidth(self._rho[-1][m.name])
            Debug.log(str(m))

    #############################################
    # DISCOVERING EXTREMA                       #
    #############################################
    def determineExtrema(self, epsilon=0.01):
        '''Returns:
        True if at a local minimum.
        False otherwise.'''
        # ============================================================== #
        # calculate gradient norm to check for an extrema based on       #
        # the Kuhn Tucker optimality conditions:                         #
        # https://en.wikipedia.org/wiki/Karush-Kuhn-Tucker_conditions    #
        # first condition is that the gradient vanishes:                 #
        #           lim(x -> x*) ||g[k]|| -> 0                           #
        # effectively:                                                   #
        #           ||g[k]|| < ε[c]                                      #
        # the second condition is that the Hessian is positive definite: #
        #           B[k] = ΓΛΓt                                          #
        # Γ being the eigenvector matrix and                             #
        # Λ being the matrix of eigenvalues                              #
        # as the solution approaches a minima the Hessian becomes        #
        # positive definite, therefore all eigenvalues [λ1, .., λn] must #
        # all be greater than 0.                                         #
        #           lim(x -> x*) as B[k] -> B* : ∀λ[i] > 0               #
        # ============================================================== #
        
        # Calculate the magnitude of the gradients
        gradient_norm = 0.0
        for g in self._gradients[-1].values():
            gradient_norm += g * g
        gradient_norm = np.sqrt(gradient_norm)
        Debug.log('||g[k]|| = {0}'.format(gradient_norm), self._debug_write)
        
        # If the gradients are within epsilon bounds then:
        # Check each Eigen Value (EV) individualy to determine our extrema:
        # 1) If all EVs are positive then its a minima
        # 2) If all EVs are negative then its a maxima
        # 3) If not all EVs are on the same side of 0 then we're on a saddle point
        if (epsilon > gradient_norm):
            # the BFGS matrix is always symetric so use eigh instead of eig
            eigenvalues = np.linalg.eigh(self._bfgs[-1])[0]
            Debug.log('EVs: {0}'.format(eigenvalues), True)
            # for ev in eigenvalues:
            #     if (0.0 > ev):
            #         return False
            return True
        return False
