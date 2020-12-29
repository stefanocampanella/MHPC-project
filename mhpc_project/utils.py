from datetime import datetime
from math import isnan

import hiplot as hip
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as mtick
import pandas as pd
import seaborn as sns
from scipy.optimize import root_scalar
from tqdm.auto import tqdm


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


def find_scale(first_layer_widths, number_of_layers, max_depth):
    if first_layer_widths * number_of_layers >= max_depth:
        raise ValueError

    solver = root_scalar(lambda x: max_depth - sum(calculate_widths(first_layer_widths, x, number_of_layers)),
                         bracket=(0.0, 1.0))

    if not solver.converged:
        raise RuntimeError
    else:
        return solver.root


def calculate_widths(first_layer_width, max_depth, number_of_layers):
    log_scale_factor = find_scale(first_layer_width, max_depth, number_of_layers)
    return first_layer_width * np.exp(log_scale_factor * np.arange(number_of_layers))


def calculate_weights(edge_depth, edge_width, widths):
    depths = np.insert(np.cumsum(widths), 0, 0.0)
    weights = np.diff(edge_width * np.log(1 + np.exp((depths - edge_depth) / edge_width))) / widths
    return weights


class ParametersLogger:

    def __init__(self, massage):
        self.massage = massage
        self.data = []

    def __call__(self, optimizer, candidate, loss):
        data = {"num-tell": optimizer.num_tell,
                "generation": candidate.generation,
                "loss": loss}
        args, kwargs = self.massage(*candidate.args, **candidate.kwargs)
        for position, value in enumerate(args):
            kwargs[repr(position)] = value
        data.update(kwargs)
        self.data.append(data)

    @property
    def experiment(self):
        return hip.Experiment.from_iterable(self.data)

    def parallel_coordinate_plot(self):
        self.experiment.display()


class ProgressBar(tqdm):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.loss = None

    def __call__(self, optimizer, candidate, loss, **kwargs):
        super().update()

        from_none = self.loss is None
        from_nan = not from_none and isnan(self.loss) and not isnan(loss)
        from_greater = not from_none and not from_nan and self.loss > loss

        if from_none or from_nan or from_greater:
            self.loss = loss
            self.set_description(desc=f"(Current loss: {self.loss:.4f})")
