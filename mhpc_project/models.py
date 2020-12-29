import pandas as pd
from geotopy import GEOtop
from .utils import date_parser, calculate_widths, calculate_weights


class SMCMultiLayer(GEOtop):

    def preprocess(self, working_dir, *args, **kwargs):
        settings, soil_params = args
        first_layer_width = settings.pop('FirstLayerWidth')
        maximum_depth = settings.pop('MaxDepth')
        edge_depth = settings.pop('EdgeDepth')
        edge_width = settings.pop('EdgeWidth')

        number_of_layers = settings['SoilLayerNumber']
        widths = calculate_widths(first_layer_width, maximum_depth, number_of_layers)
        weights = calculate_weights(edge_depth, edge_width, widths)

        soil = pd.DataFrame()
        soil['widths'] = widths
        for name, lower, upper in soil_params:
            soil[name] = lower + weights * (upper - lower)
        soil_params_file_path = working_dir / settings['SoilParFile']
        soil.to_csv(soil_params_file_path, index=False)

        self.overwrite_settings(working_dir, settings)

    def postprocess(self, working_dir):
        depths = self.settings['SoilPlotDepths']
        usecols = [0]
        usecols.extend(range(6, 6 + len(depths)))

        moisture_columns = ['datetime']
        moisture_columns.extend(f"soil_moisture_{d:.0f}" for d in depths)
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

        return liq


class SMC50(GEOtop):

    def preprocess(self, working_dir, *args, **kwargs):
        self.overwrite_settings(working_dir, kwargs)

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


class FullModel(GEOtop):

    def preprocess(self, working_dir, *args, **kwargs):
        self.overwrite_settings(working_dir, kwargs)

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
