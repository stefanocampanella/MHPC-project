from os.path import join as joinpath

import geotopy.optim as gto
from geotopy.utils import date_parser
import nevergrad as ng
import pandas as pd


class CalibrationModel(gto.GEOtopRun):

    def postprocess(self, working_dir):

        liq_path = joinpath(working_dir, 'theta_liq.txt')
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

    def preprocess(self, working_dir, *args, **kwargs):

        self.settings['SoilPlotDepths'] = [0.5, 2]
        self.settings['SoilIceContentProfileFileWriteEnd'] = '"theta_ice"'
        self.settings['PointAll'] = True
        self.settings['PointOutputFileWriteEnd'] = '"point"'

        super().preprocess(working_dir, *args, **kwargs)

    def postprocess(self, working_dir):

        liq_path = joinpath(working_dir, 'theta_liq.txt')
        liq = pd.read_csv(liq_path,
                          na_values=['-9999'],
                          usecols=[0, 6, 7],
                          skiprows=1,
                          header=0,
                          names=['datetime', 'soil_moisture_content_50', 'soil_moisture_content_200'],
                          parse_dates=[0],
                          date_parser=date_parser,
                          index_col=0,
                          low_memory=False)

        ice_path = joinpath(working_dir, 'theta_ice.txt')
        ice = pd.read_csv(ice_path,
                          na_values=['-9999'],
                          usecols=[0, 6, 7],
                          skiprows=1,
                          header=0,
                          names=['datetime', 'soil_moisture_content_50', 'soil_moisture_content_200'],
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

        sim['rainfall_amount'] = point['Prain_over_canopy[mm]'] + point['Psnow_over_canopy[mm]']

        sim['wind_speed'] = point['Wind_speed[m/s]']

        sim['relative_humidity'] = point['Relative_Humidity[-]']

        sim['air_temperature'] = point['Tair[C]']

        sim['surface_downwelling_shortwave_flux'] = point['SWin[W/m2]']

        sim['soil_moisture_content_50'] = ice['soil_moisture_content_50'] + liq['soil_moisture_content_50']

        sim['soil_moisture_content_200'] = ice['soil_moisture_content_200'] + liq['soil_moisture_content_200']

        sim['latent_heat_flux_in_air'] = \
            point['Canopy_fraction[-]'] * (point['LEg_veg[W/m2]'] + point['LEv[W/m2]']) + \
            (1 - point['Canopy_fraction[-]']) * point['LEg_unveg[W/m2]']

        sim['sensible_heat_flux_in_air'] = \
            point['Canopy_fraction[-]'] * (point['Hg_veg[W/m2]'] + point['Hv[W/m2]']) + \
            (1 - point['Canopy_fraction[-]']) * point['Hg_unveg[W/m2]']

        return sim


class Variables(gto.Variables):

    def __init__(self, path):
        data = pd.read_csv(path, index_col='name')
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
            settings[name] = y if t != 'log' else 10 ** y

        return (), settings


class NGO(gto.Calibration):

    def __init__(self, loss, **kwargs):

        super().__init__(loss)

        self._optimizer_istance = ng.optimizers.NGO(self.parametrization, **kwargs)

    @property
    def parametrization(self):

        shape = (self.loss.variables.num_vars,)

        array = ng.p.Array(shape=shape, mutable_sigma=True)
        array.set_mutation(sigma=1/6)
        array.set_bounds(lower=0.0, upper=1.0)

        return array

    @property
    def optimizer(self):

        return self._optimizer_istance

    def __call__(self, *args, **kwargs):

        recommendation = self.optimizer.minimize(self.loss, *args, **kwargs)
        _, recommendation = self.loss.massage(*recommendation.args)

        return recommendation

    def to_dataframe(self, recommendation):

        bounds = self.loss.variables.bounds
        massage = self.loss.massage
        lower = pd.DataFrame.from_dict(massage([x for (x, _) in bounds]), orient='index', columns=['lower'])
        upper = pd.DataFrame.from_dict(massage([x for (_, x) in bounds]), orient='index', columns=['upper'])
        best = pd.DataFrame.from_dict(recommendation, orient='index', columns=['best'])

        return best.append([lower, upper], sort=False)


