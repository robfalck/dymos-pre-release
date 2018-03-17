from dymos.utils.misc import get_rate_units
from openmdao.core.explicitcomponent import ExplicitComponent
from six import string_types, iteritems


class ControlInterpolationComp(ExplicitComponent):
    """
    Provides the interpolated value and rate of a control variable during explicit integration.

    For each control handled by ControlInterpolationComp, the user must provide an object
    with methods `eval(t)` and `eval_deriv(t)` which return the interpolated value and
    derivative of the control at time `t`, respectively.
    """
    def initialize(self):
        self.metadata.declare('time_units', default='s', allow_none=True, types=string_types,
                              desc='Units of time')
        self.metadata.declare('control_options', types=dict,
                              desc='Dictionary of options for the dynamic controls')
        self.interpolants = {}

    def setup(self):
        time_units = self.metadata['time_units']

        self.add_input('time', val=1.0, units=time_units)

        for control_name, options in iteritems(self.metadata['control_options']):
            shape = options['shape']
            units = options['units']
            rate_units = get_rate_units(units, time_units, deriv=1)
            rate2_units = get_rate_units(units, time_units, deriv=2)

            self.add_output('controls:{0}'.format(control_name), shape=shape, units=units)

            self.add_output('control_rates:{0}_rate'.format(control_name), shape=shape,
                            units=rate_units)

            self.add_output('control_rates:{0}_rate2'.format(control_name), shape=shape,
                            units=rate2_units)

    def compute(self, inputs, outputs):
        time = inputs['time']

        for name in self.metadata['control_options']:
            if name not in self.interpolants:
                raise(ValueError('No interpolant has been specified for {0}'.format(name)))

            outputs['controls:{0}'.format(name)] = self.interpolants[name].eval(time)

            outputs['control_rates:{0}_rate'.format(name)] = \
                self.interpolants[name].eval_deriv(time)

            outputs['control_rates:{0}_rate2'.format(name)] = \
                self.interpolants[name].eval_deriv(time, der=2)
