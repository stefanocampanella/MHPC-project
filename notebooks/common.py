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
import psutil
import geotopy as gtp

systmpfs = '/tmp'

def date_parser(x):
    return datetime.strptime(x, "%d/%m/%Y %H:%M")

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
                          index_col=0)
        
        ice_path = joinpath(working_dir, 'theta_ice.txt')
        ice = pd.read_csv(ice_path, 
                          na_values=['-9999'], 
                          usecols=[0, 6, 7], 
                          skiprows=1,
                          header=0, 
                          names=['datetime', 'soil_moisture_content_50', 'soil_moisture_content_200'],
                          parse_dates=[0], 
                          date_parser=date_parser,
                          index_col=0)
        
        sim = ice + liq
        
        return sim

class observations(Mapping):
    
    def __init__(self, path):
        
        self.data = pd.read_csv(path, 
                                na_values=['-9999'],
                                parse_dates=[0], 
                                date_parser=date_parser,
                                index_col=0)
        
        self.data.index.rename('datetime', inplace=True)
        
    def __getitem__(self, key):
        
        return self.data[key]

    def __len__(self):
        
        return len(self.data)

    def __iter__(self):
        
        return iter(self.data)

    def compare(self, target, simulation, scales=None, name=None, unit=None, rel=False, figsize=(16,9), dpi=100):

        if not scales:
            scales = {'Daily': 'D', 'Weekly': 'W', 'Monthly': 'M'}

        fig, axes = plt.subplots(ncols=3, 
                                 nrows=len(scales),
                                 figsize=figsize,
                                 dpi=dpi,
                                 constrained_layout=True)

        if name:
            fig.suptitle(name)

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
    
    def metric(self, target, simulation, scale='D'):
        
        y_obs = self[target].resample(scale).mean()
        y_sim = simulation[target].resample(scale).mean()
        diff_squared = (y_obs - y_sim) * (y_obs - y_sim)
        y_obs_squared = y_obs * y_obs
        
        return np.sqrt(diff_squared.mean() / y_obs_squared.mean())

    
class monitor:
    def __init__(self, interval):
        self.datetime = []
        self.cpu_usage = []
        self.memory_usage = []
        self.interval = interval
        self.running = False
        
        self.thread = Thread(target=self.run, args=())
        self.thread.daemon = True
        self.start()

    def sample(self):
        self.datetime.append(datetime.now())
        self.cpu_usage.append(psutil.cpu_percent())
        self.memory_usage.append(psutil.virtual_memory().percent)
        
    def run(self):
        while self.running:
            self.sample()
            sleep(self.interval)
    
    def start(self):
        self.running = True
        self.thread.start()
        
    def stop(self):
        self.running = False
        self.thread.join()
        
    def plot(self, figsize=(16,9), dpi=100):
        self.stop()
        stats = pd.DataFrame({'CPU': self.cpu_usage, 'Memory': self.memory_usage}, index=self.datetime)
        fig = plt.figure(figsize=figsize, dpi=dpi)
        axes = fig.add_subplot()
        axes.set_title('Resource Monitor')
        axes.set_xlabel('Time')
        axes.set_ylabel('Usage [%]')
        sns.lineplot(data=stats, ax=axes)