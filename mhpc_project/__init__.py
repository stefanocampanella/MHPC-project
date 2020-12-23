from os.path import join as joinpath

import nevergrad as ng
import numpy as np
import pandas as pd

import geotopy.optim as gto
from geotopy.utils import date_parser


class SMC50(gto.GEOtopRun):

    def postprocess(self, working_dir):
        liq_path = joinpath(working_dir, self.settings['SoilLiqContentProfileFileWriteEnd'].strip('"') + '.txt')
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


class FullModel(gto.GEOtopRun):

    def postprocess(self, working_dir):
        depths = self.settings['SoilPlotDepths']
        usecols = [0]
        usecols.extend(range(6, 6 + len(depths)))

        moisture_columns = ['datetime']
        moisture_columns.extend(f"soil_moisture_{d:.0f}" for d in depths)

        temperature_columns = ['datetime']
        temperature_columns.extend(f"soil_temperature_{d:.0f}" for d in depths)

        liq_path = joinpath(working_dir, self.settings['SoilLiqContentProfileFileWriteEnd'].strip('"') + '.txt')
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

        ice_path = joinpath(working_dir, self.settings['SoilIceContentProfileFileWriteEnd'].strip('"') + '.txt')
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

        temperature_path = joinpath(working_dir, self.settings['SoilTempProfileFileWriteEnd'].strip('"') + '.txt')
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
        
        point_path = joinpath(working_dir, 'point.txt')
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
        
        sim['shortwave_downwelling'] = point['SWin[W/m2]']
        sim['shortwave_upwelling'] = point['SWup[W/m2]']
        sim['shortwave_net'] = point['SWnet[W/m2]']
        
        sim['longwave_downwelling'] = point['LWin[W/m2]']
        sim['longwave_upwelling'] = point['LWup[W/m2]']
        sim['longwave_upwelling'] = point['LWnet[W/m2]']

        sim['latent_heat'] = \
            point['Canopy_fraction[-]'] * (point['LEg_veg[W/m2]'] + point['LEv[W/m2]']) + \
            (1 - point['Canopy_fraction[-]']) * point['LEg_unveg[W/m2]']

        sim['sensible_heat'] = \
            point['Canopy_fraction[-]'] * (point['Hg_veg[W/m2]'] + point['Hv[W/m2]']) + \
            (1 - point['Canopy_fraction[-]']) * point['Hg_unveg[W/m2]']
        
        sim['soil_heat'] = point['Soil_heat_flux[W/m2]']

        return sim


class Variables(gto.Variables):

    def __init__(self, *paths):
        data = pd.DataFrame()
        for path in paths:
            data = data.append(pd.read_csv(path, index_col='name'))
        self.data = data

    @property
    def num_vars(self):
        return self.data.shape[0]

    @property
    def names(self):
        return list(self.data.index)

    @property
    def bounds(self):
        return list(zip(self.data['lower'], self.data['upper']))

    @property
    def types(self):
        return list(self.data['type'])


class Loss(gto.Loss):

    def massage(self, xs):
        names = self.variables.names
        bounds = self.variables.bounds
        types = self.variables.types
        settings = {}
        for x, name, (a, b), t in zip(xs, names, bounds, types):
            y = a + x * (b - a)
            if t == 'log':
                y = 10 ** y
            settings[name] = y

        return (), settings


class NGO(gto.Calibration):

    def __init__(self, loss, **kwargs):
        super().__init__(loss)

        self._optimizer_istance = ng.optimizers.NGO(self.parametrization, **kwargs)

    @property
    def parametrization(self):
        shape = (self.loss.variables.num_vars,)

        array = ng.p.Array(shape=shape, mutable_sigma=True)
        array.set_mutation(sigma=1 / 6)
        array.set_bounds(lower=0.0, upper=1.0)

        return array

    @property
    def optimizer(self):
        return self._optimizer_istance

    def __call__(self, *args, **kwargs):
        recommendation = self.optimizer.minimize(self.loss, *args, **kwargs)
        _, recommendation = self.loss.massage(*recommendation.args)

        return recommendation

    def to_dataframe(self, recommendation, name='recommendation'):
        num_vars = self.loss.variables.num_vars
        massage = self.loss.massage
        _, lower = massage(np.zeros(num_vars))
        lower = pd.DataFrame.from_dict(lower, orient='index', columns=['lower'])
        _, upper = massage(np.ones(num_vars))
        upper = pd.DataFrame.from_dict(upper, orient='index', columns=['upper'])
        best = pd.DataFrame.from_dict(recommendation, orient='index', columns=[name])

        return pd.concat([lower, upper, best], axis=1)
