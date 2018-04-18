

# Class definition
class MutableVar(object):

    #############################################
    # INITIALIZATION                            #
    #############################################
    def __init__(self, name, start_value, step_width, **kwargs):
        self.name = name
        self._start_value = start_value
        self.setCurValue(start_value)
        self.setCurStepWidth(step_width)
        super().__init__(**kwargs)

    def setCurValue(self, value):
        assert not hasattr(super(), 'setCurValue')
        self._cur_value = value

    def setCurStepWidth(self, width):
        assert not hasattr(super(), 'setCurStepWidth')
        self._cur_step_width = width

    #############################################
    # ACCESSORS                                 #
    #############################################
    def getValueAtStep(self, at_step=0, resolution=0.1):
        assert not hasattr(super(), 'getValueAtStep')
        return self._cur_value + self._cur_step_width * resolution * at_step

    def getGradientWidthAtStep(self, at_step=0, resolution=0.1):
        assert not hasattr(super(), 'getGradientWidthAtStep')
        #            F(x[i] + s[i]) - F(x[i] - s[i])
        # g(x[i]) = ---------------------------------
        #                        2s[i]
        #
        # such that s[i] = (10^-4) * |x[i]|
        # return s[i]
        # return (10.0**-4.0) * self.getValueAtStep(at_step, resolution)
        return (0.01) * self.getValueAtStep(at_step, resolution)

    #############################################
    # BUILT-INS                                 #
    #############################################
    def __eq__(self, other):
        return (self.name == other.name)

    def __repr__(self):
        msg = 'MutableVar("{0.name}", {0._cur_value}, {0._cur_step_width})'
        return msg.format(self)
