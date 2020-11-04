import pandas as pd
import numpy as np
from subprocess import CalledProcessError, TimeoutExpired
from tempfile import TemporaryDirectory
import pkg_resources

from .core import Observations, GEOtopRun

inputs_path = pkg_resources.resource_filename(__name__, 'data/geotop')
obs_path = pkg_resources.resource_filename(__name__, 'data/obs.csv')
var_path = pkg_resources.resource_filename(__name__, 'data/variables.csv')
timeout = 120
targets = ['soil_moisture_content_50', 'sensible_heat_flux_in_air']
weights = [1.0, 1.0]

obs = Observations(obs_path)

variables = pd.read_csv(var_path, index_col='name')

class GEOtopRunLogVars(GEOtopRun):
    
    def preprocess(self, working_dir, *args, **kwargs):
        
        for key, value in kwargs.items():
            if variables.type[key] == 'log':
                kwargs[key] = 10 ** value
                
        super().preprocess(working_dir, *args, **kwargs)

model = GEOtopRunLogVars(inputs_path,
                  run_args={'check': True,
                            'capture_output': True,
                            'timeout': timeout})


def loss(*args, sim=None, **kwargs):

    if sim is None:
        with TemporaryDirectory() as tmpdir:
            try:
                sim = model.eval(tmpdir, *args, **kwargs)
            except CalledProcessError:
                return np.nan
            except TimeoutExpired:
                return np.nan
    return sum(w * obs.metric(t, sim) for w, t in zip(weights, targets)) / sum(weights)
