import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import matplotlib.ticker as mtick
from datetime import timedelta
from .utils import get_scaling_data


def comparison(observations, simulation, scales=None, desc=None, unit=None, rel=False, figsize=(16, 9),
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


def comparisons(predictions, observations, **kwargs):
    plots = {}
    for target in observations.columns:
        if target in predictions.columns:
            desc = target.replace('_', ' ').title()
            plots[target] = comparison(observations[target], predictions[target], desc=desc, **kwargs)
    return plots


def convergence(gen_loss_log, figsize=(16, 9), dpi=100):
    max_generation_number = max(n for n, _ in gen_loss_log)
    min_losses = [min(l for n, l in gen_loss_log if n <= k)
                  for k in range(1, max_generation_number + 1)]
    data = pd.DataFrame(gen_loss_log, columns=['generation', 'loss'])
    figure, axes = plt.subplots(figsize=figsize, dpi=dpi)
    sns.lineplot(data=data, x='generation', y='loss', ax=axes)
    sns.lineplot(x=range(1, max_generation_number + 1), y=min_losses, ax=axes)
    return figure


def strong_scaling(data, dpi=100, figsize=(16, 9), title=None, **kwargs):
    min_cpus = data['num_cpus'].min()
    duration_baseline = data[data['num_cpus'] == min_cpus]['duration'].mean()
    data['speedup'] = duration_baseline / data['duration']
    data['ref'] = data[['num_cpus', 'popsize']].min(axis=1) / min_cpus
    figure, axes = plt.subplots(dpi=dpi, figsize=figsize)
    if title:
        axes.set_title(title)
    sns.lineplot(data=data, x='num_cpus', y='speedup',
                 err_style='bars', marker='o',
                 label='data', ax=axes, **kwargs)
    sns.lineplot(data=data, x='num_cpus', y='ref',
                 label='reference', ax=axes, **kwargs)
    return figure


def weak_scaling(data, dpi=100, figsize=(16, 9), title=None, **kwargs):
    data['ref'] = data['duration'].mean()
    figure, axes = plt.subplots(dpi=dpi, figsize=figsize)
    if title:
        axes.set_title(title)
    sns.lineplot(data=data, x='num_cpus', y='duration',
                 label='data', err_style='bars', marker='o',
                 ax=axes, **kwargs)
    axes.yaxis.set_major_formatter(lambda value, position: timedelta(seconds=value))
    sns.lineplot(data=data, x='num_cpus', y='ref',
                 label='reference',
                 ax=axes, **kwargs)
    return figure

def duration_regplot(data):
    xmin = data['num_cpus'].min()
    xmax = data['num_cpus'].max()
    xdel = xmax - xmin
    xlim = xmin - 0.05 * xdel, xmax + 0.05 * xdel
    grid = sns.JointGrid(data=data, x='num_cpus', y='duration', xlim=xlim)
    grid.fig.set_figwidth(16)
    grid.fig.set_figheight(9)
    grid.plot_joint(sns.regplot, x_estimator=np.mean, truncate=False)
    grid.ax_marg_x.set_axis_off()
    sns.histplot(data=data, y='duration', kde=True, ax=grid.ax_marg_y)
    grid.ax_joint.yaxis.set_major_formatter(lambda value, position: timedelta(seconds=value))


def efficiency(data, dpi=100, figsize=(16, 9), title=None, **kwargs):
    xmin, xmax = data['num_cpus'].min(), data['num_cpus'].max()
    figure, axes = plt.subplots(dpi=dpi, figsize=figsize)
    axes.set_xlim(xmin - 0.05 * (xmax - xmin), xmax + 0.05 * (xmax - xmin))
    if title:
        axes.set_title(title)
    sns.regplot(data=data, x='num_cpus', y='efficiency',
                x_estimator=np.mean, truncate=False,
                ax=axes, **kwargs)
    return figure
