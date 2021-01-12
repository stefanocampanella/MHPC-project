import importlib.resources as resources
import json

import pandas as pd

from geotopy import GEOtop
from .utils import date_parser, calculate_widths, calculate_weights

with resources.open_text('mhpc_project', 'geotop_headers_map.json') as file:
    headers_map = json.load(file)

with resources.open_text('mhpc_project', 'varsoil_model_defaults.json') as file:
    default_settings = json.load(file)


class UniformLiqModel(GEOtop):

    def preprocess(self, working_dir, *args, **kwargs):
        self.patch_inpts_file(working_dir, kwargs)

    def postprocess(self, working_dir):
        liq_path = working_dir / (self.settings['SoilLiqContentProfileFileWriteEnd'].strip('"') + '.txt')
        liq = pd.read_csv(liq_path,
                          na_values=['-9999'],
                          usecols=[0, 6],
                          skiprows=1,
                          header=0,
                          names=['datetime', 'soil_moisture_content_50'],
                          parse_dates=[0],
                          date_parser=date_parser,
                          index_col=0,
                          low_memory=False,
                          squeeze=True)

        return liq


class UniformFullModel(GEOtop):

    def preprocess(self, working_dir, *args, **kwargs):
        self.patch_inpts_file(working_dir, kwargs)

    def postprocess(self, working_dir):
        depths = self.settings['SoilPlotDepths']
        usecols = [0]
        usecols.extend(range(6, 6 + len(depths)))

        moisture_columns = ['datetime']
        moisture_columns.extend(f"soil_moisture_{d:.0f}" for d in depths)

        temperature_columns = ['datetime']
        temperature_columns.extend(f"soil_temperature_{d:.0f}" for d in depths)

        liq_path = working_dir / (self.settings['SoilLiqContentProfileFileWriteEnd'].strip('"') + '.txt')
        liq = pd.read_csv(liq_path,
                          na_values=['-9999'],
                          usecols=usecols,
                          skiprows=1,
                          header=0,
                          names=moisture_columns,
                          parse_dates=[0],
                          date_parser=date_parser,
                          index_col=0,
                          low_memory=False)

        ice_path = working_dir / (self.settings['SoilIceContentProfileFileWriteEnd'].strip('"') + '.txt')
        ice = pd.read_csv(ice_path,
                          na_values=['-9999'],
                          usecols=usecols,
                          skiprows=1,
                          header=0,
                          names=moisture_columns,
                          parse_dates=[0],
                          date_parser=date_parser,
                          index_col=0,
                          low_memory=False)

        temperature_path = working_dir / (self.settings['SoilTempProfileFileWriteEnd'].strip('"') + '.txt')
        temperature = pd.read_csv(temperature_path,
                                  na_values=['-9999'],
                                  usecols=usecols,
                                  skiprows=1,
                                  header=0,
                                  names=temperature_columns,
                                  parse_dates=[0],
                                  date_parser=date_parser,
                                  index_col=0,
                                  low_memory=False)

        point_path = working_dir / 'point.txt'
        point = pd.read_csv(point_path,
                            na_values=['-9999'],
                            parse_dates=[0],
                            date_parser=date_parser,
                            index_col=0,
                            low_memory=False)
        point.index.rename('datetime', inplace=True)

        sim = pd.DataFrame(index=point.index)

        for col in moisture_columns[1:]:
            sim[col] = ice[col] + liq[col]

        for col in temperature_columns[1:]:
            sim[col] = temperature[col]

        sim['latent_heat'] = \
            point['Canopy_fraction[-]'] * (point['LEg_veg[W/m2]'] + point['LEv[W/m2]']) + \
            (1 - point['Canopy_fraction[-]']) * point['LEg_unveg[W/m2]']

        sim['sensible_heat'] = \
            point['Canopy_fraction[-]'] * (point['Hg_veg[W/m2]'] + point['Hv[W/m2]']) + \
            (1 - point['Canopy_fraction[-]']) * point['Hg_unveg[W/m2]']

        sim['soil_heat'] = point['Soil_heat_flux[W/m2]']

        return sim


class VarSoilFullModel(GEOtop):

    def preprocess(self, working_dir, *args, **kwargs):
        extra_settings, inpts_settings, soil_settings =\
            (args[0][key] for key in ['extra', 'inpts', 'soil'])

        number_of_layers = default_settings['SoilLayerNumber']
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
            header_keyword = headers_map[parameter]
            inpts_settings[header_keyword] = parameter
            inpts_settings[parameter] = None

        settings = self.settings.copy()
        settings.update(default_settings)

        self.clone_into(working_dir)

        soil_file = working_dir / (settings['SoilParFile'].strip('"') + '0001.txt')
        soil_file.parent.mkdir(parents=True, exist_ok=True)
        soil.to_csv(soil_file)

        settings.update(inpts_settings)

        self.dump_in(settings, working_dir)

    def postprocess(self, working_dir):
        data = []

        point_setting = default_settings['PointOutputFileWriteEnd']
        point_path = working_dir / (point_setting.strip('"') + '.txt')
        point = pd.read_csv(point_path,
                            na_values=['-9999'],
                            parse_dates=[0],
                            date_parser=date_parser,
                            index_col=0,
                            low_memory=False)

        fluxes = pd.DataFrame(index=point.index)
        canopy_fraction_header = default_settings['HeaderCanopyFractionPoint']
        canopy_fraction = point[canopy_fraction_header.strip('"')]

        leg_veg_header = default_settings['HeaderLEgVegPoint']
        leg_veg = point[leg_veg_header.strip('"')]
        lev_header = default_settings['HeaderLEvPoint']
        lev = point[lev_header.strip('"')]
        leg_unveg_header = default_settings['HeaderLEgUnvegPoint']
        leg_unveg = point[leg_unveg_header.strip('"')]
        fluxes['latent_heat'] = canopy_fraction * (leg_veg + lev) + (1 - canopy_fraction) * leg_unveg

        hg_veg_header = default_settings['HeaderHgVegPoint']
        hg_veg = point[hg_veg_header.strip('"')]
        hv_header = default_settings['HeaderHvPoint']
        hv = point[hv_header.strip('"')]
        hg_unveg_header = default_settings['HeaderHgUnvegPoint']
        hg_unveg = point[hg_unveg_header.strip('"')]
        fluxes['sensible_heat'] = canopy_fraction * (hg_veg + hv) + (1 - canopy_fraction) * hg_unveg

        soil_heat_header = default_settings['HeaderSoilHeatFluxPoint']
        soil_heat = point[soil_heat_header.strip('"')]
        fluxes['soil_heat'] = soil_heat
        data.append(fluxes)

        liq = self.read_soil_profile(working_dir,
                                     default_settings['SoilLiqContentProfileFileWriteEnd'],
                                     "soil_moisture_{:.0f}",
                                     point.index)
        ice = self.read_soil_profile(working_dir,
                                     default_settings['SoilIceContentProfileFileWriteEnd'],
                                     "soil_moisture_{:.0f}",
                                     point.index)
        theta = liq + ice
        data.append(theta)

        temperature = self.read_soil_profile(working_dir,
                                             default_settings['SoilTempProfileFileWriteEnd'],
                                             "soil_temperature_{:.0f}",
                                             point.index)
        data.append(temperature)

        return pd.concat(data)

    def read_soil_profile(self, working_dir, basename, header, index):
        depths = self.settings['SoilPlotDepths']
        names = [header.format(d) for d in depths]
        profile_path = working_dir / (basename.strip('"') + '.txt')
        profile = pd.read_csv(profile_path,
                              na_values=['-9999'],
                              skiprows=1,
                              header=0,
                              names=['skipme'] + names,
                              usecols=names,
                              low_memory=False)
        profile.index = index
        return profile
