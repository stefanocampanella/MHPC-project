import pandas as pd
from nevergrad.parametrization.parameter import Scalar, Log, Dict, Tuple


def make_parameter(mapping, **kwargs):
    if mapping == 'linear':
        return Scalar(**kwargs)
    elif mapping == 'exp':
        return Log(**kwargs)
    else:
        raise ValueError("Unknown type of mapping {mapping}.")


class VarSoilParameters:

    def __init__(self, path, defaults=None):
        self.data = pd.read_csv(path, index_col=0)
        self.defaults = defaults

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
                        parameter = make_parameter(properties['mapping'], **kwargs)
                        if place == 'soil':
                            parameter = Tuple(parameter, parameter.copy())
                    place_settings[name] = parameter
            instrumentation[place] = Dict(**place_settings)
        return Dict(**instrumentation)
