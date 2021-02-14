# Implementation

```{epigraph}

Talk is cheap, show me the code.

-- Linus Torvalds
```

## Model, Parameters, Observations

As discussed in the previous chapter, in order to have a functioning interface to the GEOtop model using GEOtoPy it is necessary to specify how to do preprocessing of the data (basically meteorological forcings and input parameters) and postprocessing of simulation results. The following is the implementation used for simulations with uniform soil parameters.

```python
import json
import importlib.resources as resources
from geotopy import GEOtop
from mhpc_project.utils import postprocess_full

class UniformSoilModel(GEOtop):
    with resources.open_text('mhpc_project', 'uniform_defaults.json') as file:
        default_settings = json.load(file)

    def preprocess(self, working_dir, *args, **kwargs):
        settings = self.settings.copy()
        settings.update(self.default_settings)
        settings.update(args[0])
        self.clone_into(working_dir)
        self.patch_inpts_file(working_dir, settings)

    def postprocess(self, working_dir):
        settings = self.read_settings(working_dir / 'geotop.inpts')
        return postprocess_full(settings, working_dir)
```

In this case, preprocessing is trivial and consist of copying the files to the proper directory and patching the `geotop.inpts` with the new value of the parameters. Notice that the `self.settings` dictionary of settings is copied to avoid nefarious side effects. Preprocessing also takes care of appling some defaults settings, which are assumed in the postprocessing phase.

The postprocess is just a wrapper around a utility function. This is because the same postprocessing is done also in the variable soil model, discussed below. In this way one can avoid code duplication without introducing a intermediate class in the inheritance scheme.

We will not walk through `postprocess_full`, but it's implementation is just a sequence of repeated calls to `Pandas.read_csv`.

The following is an example with varying depth of soil, number of soil layers and parameters accross layers.

```python
import json
import importlib.resources as resources
import pandas as pd
from geotopy import GEOtop
from mhpc_project.utils import calculate_widths, calculate_weights

class VariedSoilModel(GEOtop):
    with resources.open_text('mhpc_project', 'geotop_headers_map.json') as file:
        headers_map = json.load(file)

    with resources.open_text('mhpc_project', 'varsoil_defaults.json') as file:
        default_settings = json.load(file)

    def preprocess(self, working_dir, *args, **kwargs):
        extra_settings, inpts_settings, soil_settings = \ 
            (args[0][key] for key in ['extra', 'inpts', 'soil'])

        number_of_layers = self.default_settings['SoilLayerNumber']
        first_layer_width = extra_settings['FirstLayerWidth']
        max_depth = extra_settings['MaxDepth']
        widths = calculate_widths(first_layer_width,
                                  number_of_layers,
                                  max_depth)
        soil = pd.DataFrame(index=widths)
        soil.index.rename('SoilLayerThicknesses', inplace=True)

        edge_depth = extra_settings['EdgeDepth']
        edge_width = extra_settings['EdgeWidth']
        weights = calculate_weights(edge_depth, edge_width, widths)
        for parameter, (a, b) in soil_settings.items():
            soil[parameter] = a + weights * (b - a)
            header_keyword = self.headers_map[parameter]
            inpts_settings[header_keyword] = parameter
            inpts_settings[parameter] = None

        settings = self.settings.copy()
        settings.update(self.default_settings)

        self.clone_into(working_dir)

        soil_file = working_dir / (settings['SoilParFile'].strip('"') + '0001.txt')
        soil_file.parent.mkdir(parents=True, exist_ok=True)
        soil.to_csv(soil_file)

        settings.update(inpts_settings)

        self.dump_in(settings, working_dir)
```
The preprocessing for soil varying with depth is a bit more involved. The main idea is that the 


## A Look at the Optimization Loop

## Executing the Program on a Cluster
