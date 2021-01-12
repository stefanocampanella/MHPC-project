from datetime import datetime

import matplotlib.pyplot as plt
import matplotlib.ticker as mtick
import numpy as np
import pandas as pd
import seaborn as sns
from scipy.optimize import root_scalar


def date_parser(x):
    return datetime.strptime(x, '%d/%m/%Y %H:%M')


def comparison_plot(observations, simulation, scales=None, desc=None, unit=None, rel=False, figsize=(16, 9),
                    dpi=100):
    if not scales:
        scales = {'Daily': 'D', 'Weekly': 'W', 'Monthly': 'M'}

    fig, axes = plt.subplots(ncols=3,
                             nrows=len(scales),
                             figsize=figsize,
                             dpi=dpi,
                             constrained_layout=True)

    if desc:
        fig.suptitle(desc)

    for i, (time_scale_description, time_scale) in enumerate(scales.items()):
        comp_plot, diff_plot, hist_plot = axes[i, :]

        obs_resampled = observations.resample(time_scale).mean()
        sim_resampled = simulation.resample(time_scale).mean()

        err = obs_resampled - sim_resampled
        if rel:
            err = err / obs_resampled.abs()

        data = pd.DataFrame({'Observations': obs_resampled, 'Simulation': sim_resampled})
        sns.lineplot(data=data, ax=comp_plot)
        plt.setp(comp_plot.get_xticklabels(), rotation=20)
        comp_plot.set_title(time_scale_description)
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
        hist_plot.set_ylim(y1, y2)
        hist_plot.set_yticklabels([])
        hist_plot.set_ylabel('')

    return fig


def find_scale(first_layer_width, number_of_layers, max_depth):
    if first_layer_width * number_of_layers >= max_depth:
        raise ValueError("Max depth must be greater then the number of layers times "
                         "the first layer width.")
    else:
        solver = root_scalar(lambda x: max_depth - first_layer_width * np.sum(np.exp(x * np.arange(number_of_layers))),
                             bracket=(0.0, 1.0))

        if solver.converged:
            return solver.root
        else:
            raise RuntimeError


def calculate_widths(first_layer_width, number_of_layers, max_depth):
    log_scale_factor = find_scale(first_layer_width, number_of_layers, max_depth)
    return first_layer_width * np.exp(log_scale_factor * np.arange(number_of_layers))


def calculate_weights(edge_depth, edge_width, widths):
    depths = np.insert(np.cumsum(widths), 0, 0.0)
    weights = np.diff(edge_width * np.log(1 + np.exp((depths - edge_depth) / edge_width))) / widths
    return weights
