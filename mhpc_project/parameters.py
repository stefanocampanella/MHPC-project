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
        sample_log = [(x, l) for x, l, t in log if np.isfinite(l)]

        samples = []
        losses = []
        for candidate, loss in sample_log:
            sample = self.from_instrumentation(candidate)
            sample.drop(labels=self.defaults, inplace=True)
            sample.sort_index()
            samples.append(sample)
            losses.append(loss)
        samples = np.asarray(samples)
        losses = np.asarray(losses)

        variables = {}
        for parameter in self.data.itertuples():
            if parameter.Index not in self.defaults:
                variables[parameter.Index] = (parameter.lower, parameter.upper)

        names = sorted(variables)
        num_vars = len(names)
        bounds = [variables[name] for name in names]
        problem = {'num_vars': num_vars,
                   'names': names,
                   'bounds': bounds}

        sa = delta.analyze(problem, samples, losses)
        return sa.to_df()

    def from_instrumentation(self, candidate):
        parameters = candidate.args[0]

        extra, inpts, soil = (parameters[key] for key in ('extra', 'inpts', 'soil'))
        soil_a = {name + '_a': a for name, (a, b) in soil.items()}
        soil_b = {name + '_b': b for name, (a, b) in soil.items()}
        series = pd.Series({**extra, **inpts, **soil_a, **soil_b})
        series.index.rename('name', inplace=True)
        series.drop(self.defaults, inplace=True)
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
                        parameter = make_parameter(properties['mapping'], **kwargs)
                        if place == 'soil':
                            parameter = Tuple(parameter, parameter.copy())
                    place_settings[name] = parameter
            instrumentation[place] = Dict(**place_settings)
        return Dict(**instrumentation)
