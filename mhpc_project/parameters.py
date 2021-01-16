import pandas as pd
import numpy as np
from nevergrad.parametrization.parameter import Dict, Tuple
from SALib.analyze import delta
from .utils import make_parameter


class VarSoilParameters:

    def __init__(self, path, defaults=None):
        self.data = pd.read_csv(path, index_col=0)
        self.defaults = defaults

    def delta_mim(self, log):
        data = self.data.drop(self.defaults)
        names = list(data.index)
        num_vars = len(names)
        bounds = zip(data['lower'], data['upper'])
        problem = {'num_vars': num_vars,
                   'names': names,
                   'bounds': bounds}
        samples = []
        for candidate, _, _ in log:
            sample_dataframe = self.from_instrumentation(candidate, column_name='candidate')
            sample_array = sample_dataframe['candidate'].to_numpy()
            samples.append(sample_array)
        samples = np.concatenate(samples, axis=0)

        losses = np.fromiter((l for _, l, _ in log), dtype=float)
        sa = delta.analyze(problem, samples, losses)
        return sa.to_df()

    def from_instrumentation(self, candidate, column_name='best'):
        parameters = candidate.args[0]

        extra, inpts, soil = (parameters[key] for key in ('extra', 'inpts', 'soil'))
        soil_a = {name + '_a': a for name, (a, b) in soil.items()}
        soil_b = {name + '_b': b for name, (a, b) in soil.items()}
        dataframe = pd.DataFrame.from_dict({**extra, **inpts, **soil_a, **soil_b},
                                           orient='index',
                                           columns=[column_name])
        dataframe.index.rename('name', inplace=True)
        dataframe.drop(self.defaults, inplace=True)
        return dataframe

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
