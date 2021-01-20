import importlib.resources as resources
import json

import pandas as pd

from geotopy import GEOtop
from .utils import calculate_widths, calculate_weights, postprocess_full


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

    def postprocess(self, working_dir):
        settings = self.read_settings(working_dir / 'geotop.inpts')
        return postprocess_full(settings, working_dir)
