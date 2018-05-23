from debug import rootClassMethod


# Class definition
class MutableVar(object):

    #############################################
    # INITIALIZATION                            #
    #############################################
    def __init__(self, name, start_value, step_width=0.01, **kwargs):
        self.name = name
        self._start_value = start_value
        self.setCurValue(start_value)
        self.setCurStepWidth(step_width)
        super(MutableVar, self).__init__(**kwargs)

    @rootClassMethod('containers.mutable_data', 'MutableVar')
    def setCurValue(self, value):
        self._cur_value = value

    @rootClassMethod('containers.mutable_data', 'MutableVar')
    def setCurStepWidth(self, width):
        self._cur_step_width = width

    # I can use eval to copy variables like this because
    # I set up __repr__ correctly. gross? dangerous?
    # sorry not sorry.
    def getCopy(self):
        return eval(str(self))

    #############################################
    # ACCESSORS                                 #
    #############################################
    @rootClassMethod('containers.mutable_data', 'MutableVar')
    def getValueAtStep(self, at_step=0, resolution=0.1):
        return self._cur_value + self._cur_step_width * resolution * at_step

    @rootClassMethod('containers.mutable_data', 'MutableVar')
    def getGradientWidthAtStep(self, at_step=0, resolution=0.1):
        #            F(x[i] + s[i]) - F(x[i] - s[i])
        # g(x[i]) = ---------------------------------
        #                        2s[i]
        #
        # such that s[i] = (10^-4) * |x[i]|
        # return s[i]
        value = self.getValueAtStep(at_step, resolution)
        return (10.0**-4.0) * abs(value)  # abs()?
        # return (0.01) * self.getValueAtStep(at_step, resolution)

    #############################################
    # BUILT-INS                                 #
    #############################################
    def __eq__(self, other):
        return (self.name == other.name)

    def __repr__(self):
        msg = 'MutableVar("{0.name}", {0._cur_value} , {0._cur_step_width})'
        return msg.format(self)
