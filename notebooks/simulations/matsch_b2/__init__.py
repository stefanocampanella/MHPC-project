from os.path import join as joinpath
from threading import Thread
from time import sleep
from collections.abc import Mapping
from datetime import datetime

import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
import matplotlib.ticker as mtick
import geotopy as gtp
import pkg_resources

inputs_path = pkg_resources.resource_filename(__name__, 'geotop')
obs_path = pkg_resources.resource_filename(__name__, 'obs.csv')

def date_parser(x):
    return datetime.strptime(x, '%d/%m/%Y %H:%M')

class GEOtopRun(gtp.GEOtop):

    def preprocess(self, working_dir, *args, **kwargs):
        
        settings = {**self, **kwargs}
        
        inpts_src_path = joinpath(self.inputs_dir, 'geotop.inpts')
        inpts_dest_path = joinpath(working_dir, 'geotop.inpts')
        
        with open(inpts_src_path, 'r') as inpts_src, open(inpts_dest_path, 'w') as inpts_dest:
            inpts_dest.write(f"! GEOtop input file written by GEOtoPy {datetime.now().strftime('%x %X')}\n")
            while line := inpts_src.readline():
                if gtp._comment_re.match(line):
                    inpts_dest.write(line)
                else:
                    try:
                        key, value = gtp.read_setting(line)
                        
                        if key in settings and value != settings[key]:
                            inpts_dest.write(f"! GEOtoPy: {key} overwritten, was {value}\n")
                            line = gtp.print_setting(key, settings[key])
                        else:
                            line = gtp.print_setting(key, value)
                        
                        inpts_dest.write(line)
                        del settings[key]
                    
                    except ValueError as err:
                        inpts_dest.write(f"! GEOtoPy: {err}\n")
                        inpts_dest.write(line)
            
            if settings:
                inpts_dest.write("\n! Settings added by GEOtoPy\n")
                for key, value in settings.items():
                    try:
                        line = gtp.print_setting(key, value)
                        inpts_dest.write(line)
                    except ValueError as err:
                        inpts_dest.write(f"! GEOtoPy: {err}\n")
                        inpts_dest.write(f"{key} = {value}\n")
                            
        
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

class observations(Mapping):
    
    def __init__(self, source, scale='D', start=None, end=None):
        
        self.scale = scale
        
        if isinstance(source, pd.DataFrame):
            obs = source
        else:
            obs = pd.read_csv(source, 
                              na_values=['-9999', '-99.99'],
                              parse_dates=[0], 
                              date_parser=date_parser,
                              index_col=0)
        
        obs.index.rename('datetime', inplace=True)
        
        if start and end:
            obs = obs[date_parser(start):date_parser(end)]
        elif start:
            obs = obs[date_parser(start):]
        elif end:
            obs = obs[:date_parser(end)]
        
        self.data = obs.resample(scale).mean()
        
        self.mean_square = (self.data * self.data).mean()
        
        
    def __getitem__(self, key):
        
        return self.data[key]

    def __len__(self):
        
        return len(self.data)

    def __iter__(self):
        
        return iter(self.data)

    def compare(self, target, simulation, scales=None, desc=None, unit=None, rel=False, figsize=(16,9), dpi=100):

        if not scales:
            scales = {'Daily': 'D', 'Weekly': 'W', 'Monthly': 'M'}

        fig, axes = plt.subplots(ncols=3, 
                                 nrows=len(scales),
                                 figsize=figsize,
                                 dpi=dpi,
                                 constrained_layout=True)

        if desc:
            fig.suptitle(desc)

        for i, (Tstr, T) in enumerate(scales.items()):
            comp_plot, diff_plot, hist_plot = axes[i, :]
            
            obs_resampled = self[target].resample(T).mean()
            sim_resampled = simulation[target].resample(T).mean()

            err = obs_resampled - sim_resampled        
            if rel:
                err = err / obs_resampled.abs()

            data = pd.DataFrame({'Observations': obs_resampled, 'Simulation': sim_resampled})
            sns.lineplot(data=data, ax=comp_plot)
            comp_plot.set_title(Tstr)
            comp_plot.set_xlabel('')
            if unit:
                comp_plot.set_ylabel(f"[{unit}]")

            sns.lineplot(data=err, ax=diff_plot)
            plt.setp(diff_plot.get_xticklabels(), rotation=20)
            diff_plot.set_xlabel('')
            if rel:
                diff_plot.set_ylabel("Relative error")
                diff_plot.yaxis.set_major_formatter(mtick.PercentFormatter(xmax=1.0))
            elif unit:
                diff_plot.set_ylabel(f"Error [{unit}]")
            else:
                diff_plot.set_ylabel("Error")

            sns.histplot(y=err, kde=True, stat='probability', ax=hist_plot)
            y1, y2 = diff_plot.get_ylim()
            hist_plot.set_ylim(y1,y2)
            hist_plot.set_yticklabels([])
            hist_plot.set_ylabel('')
        
        return fig
    
    def metric(self, target, simulation):
        
        diff = self[target] - simulation[target].resample(self.scale).mean()
        
        return np.sqrt((diff * diff).mean() / self.mean_square[target])
