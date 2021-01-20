from abc import abstractmethod

import pandas as pd
from nevergrad.parametrization.parameter import Dict, Tuple
from .utils import make_nevergrad_parameter


class Parameters:

    def __init__(self, path, defaults=None):
        self.data = pd.read_csv(path, index_col=0)
        self.defaults = defaults

    @property
    @abstractmethod
    def bounds(self):
        raise NotImplementedError

    @abstractmethod
    def from_instrumentation(self, candidate):
        raise NotImplementedError

    @property
    @abstractmethod
    def instrumentation(self):
        raise NotImplementedError


class UniformSoilParameters(Parameters):

    @property
    def bounds(self):
        bounds = {}
        for parameter in self.data.intertuples():
            bounds[parameter.Index] = (parameter.lower, parameter.upper)
        return bounds

    def from_instrumentation(self, candidate):
        series = pd.Series(candidate.args[0])
        series.index.rename('name', inplace=True)
        return series

    @property
    def instrumentation(self):
        instrumentation = {}
        for parameter in self.data.itertuples():
            name = parameter.Index
            if name in self.defaults:
                ng_parameter = self.defaults[name]
            else:
                ng_parameter = make_nevergrad_parameter(parameter.mapping,
                                                        init=parameter.init,
                                                        lower=parameter.lower,
                                                        upper=parameter.upper)
            instrumentation[name] = ng_parameter
        return Dict(**instrumentation)


class VariedSoilParameters(Parameters):

    def bounds(self):
        bounds = {}
        for parameter in self.data.itertuples():
            parameter_bounds = (parameter.lower, parameter.upper)
            if parameter.where == 'soil':
                bounds[parameter.Index + '_a'] = parameter_bounds
                bounds[parameter.Index + '_b'] = parameter_bounds
            else:
                bounds[parameter.Index] = parameter_bounds
        return bounds

    def from_instrumentation(self, candidate):
        parameters = candidate.args[0]
        extra, inpts, soil = (parameters[key] for key in ('extra', 'inpts', 'soil'))
        soil_ab = {}
        for name, (a, b) in soil.items():
            soil_ab[name + '_a'] = a
            soil_ab[name + '_b'] = b
        series = pd.Series({**extra, **inpts, **soil_ab})
        series.index.rename('name', inplace=True)
        return series

    @property
    def instrumentation(self):
        parameters = self.data.to_dict('index')
        instrumentation = {}
        for place in 'inpts', 'soil', 'extra':
            place_settings = {}
            for name, properties in parameters.items():
                if properties['where'] == place:
                    if name in self.defaults:
                        parameter = self.defaults[name]
                        if place == 'soil':
                            parameter = (parameter, parameter)
                    else:
                        keys = properties.keys() & {'init', 'lower', 'upper'}
                        kwargs = {key: properties[key] for key in keys}
                        parameter = make_nevergrad_parameter(properties['mapping'], **kwargs)
                        if place == 'soil':
                            parameter = Tuple(parameter, parameter.copy())
                    place_settings[name] = parameter
            instrumentation[place] = Dict(**place_settings)
        return Dict(**instrumentation)
