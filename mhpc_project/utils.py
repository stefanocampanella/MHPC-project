import subprocess
from datetime import datetime
from subprocess import CalledProcessError, TimeoutExpired
from tempfile import TemporaryDirectory
from timeit import default_timer as timer
from math import sqrt, exp

import matplotlib.pyplot as plt
import matplotlib.ticker as mtick
import nevergrad as ng
import numpy as np
import pandas as pd
import seaborn as sns
from dask.distributed import as_completed, fire_and_forget
from nevergrad.parametrization.parameter import Scalar, Log
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


def make_parameter(mapping, **kwargs):
    if mapping == 'linear':
        return Scalar(**kwargs)
    elif mapping == 'exp':
        return Log(**kwargs)
    else:
        raise ValueError("Unknown type of mapping {mapping}.")


def convergence_plot(log, figsize=(16, 9), dpi=100):
    loss_log = [(x.generation, l) for x, l, _ in log if np.isfinite(l)]
    max_generation_number = max(n for n, _ in loss_log)
    min_losses = [min(l for n, l in loss_log if n <= k)
                  for k in range(1, max_generation_number + 1)]
    data = pd.DataFrame(loss_log, columns=['generation', 'loss'])
    figure, axes = plt.subplots(figsize=figsize, dpi=dpi)
    sns.lineplot(data=data, x='generation', y='loss', ax=axes)
    sns.lineplot(x=range(1, max_generation_number + 1), y=min_losses, ax=axes)


def comparison_plots(model, observations, candidate, **kwargs):
    predictions = model(*candidate.args, **candidate.kwargs)
    for target in observations.columns:
        if target in predictions.columns:
            desc = target.replace('_', ' ').title()
            comparison_plot(observations[target], predictions[target], desc=desc, **kwargs)


def time_loss_plot(log):
    losses = [l for _, l, _ in log if np.isfinite(l)]
    times = [t for _, l, t in log if np.isfinite(l)]
    data = pd.DataFrame({'losses': losses, 'times': times})
    sns.jointplot(data=data, x='losses', y='times', height=10)


def kge_cmp(sim, obs):
    if sim is None:
        return np.nan
    else:
        square_loss = 0.0
        for target in sim.columns:
            if target in obs.columns:
                x, y = sim[target], obs[target]
                r = x.corr(y) - 1
                m = x.mean() / y.mean() - 1
                v = x.std() / y.std() - 1
                square_loss += r * r + m * m + v * v
        return sqrt(square_loss)


def run_model(model, candidate):
    start = timer()
    try:
        with TemporaryDirectory(prefix='geotop_inputs_') as tmpdir:
            result = model.run_in(tmpdir, *candidate.args, **candidate.kwargs)
    except (CalledProcessError, TimeoutExpired):
        result = None
    elapsed = timer() - start

    return result, elapsed


def submit_run(candidate, model, observations, client):
    timed_sim = client.submit(run_model, model, candidate)
    sim = client.submit(lambda x: x[0], timed_sim)
    time = client.submit(lambda x: x[1], timed_sim)
    loss = client.submit(kge_cmp, sim, observations)
    return client.submit(lambda x, y, z: (x, y, z), candidate, loss, time)


def weighted_success_rate(log, alpha):
    if log:
        successes = [1 if np.isfinite(l) else 0 for (_, l, _) in reversed(log)]
        weights = [exp(-alpha * n) for n in range(len(log))]
        return sum(w * x for w, x in zip(weights, successes)) / sum(weights)
    else:
        return 1.0


def calibrate(model, parameters, observations, algorithm, popsize, num_generations, client, num_workers):
    log = []
    start = timer()
    optimizer_class = ng.optimizers.registry[algorithm]
    optimizer = optimizer_class(parameters.instrumentation,
                                budget=np.inf,
                                num_workers=popsize)
    remote_observations = client.scatter(observations, broadcast=True)
    remote_model = client.scatter(model, broadcast=True)
    for _ in range(num_generations):
        to_tell = []
        while len(to_tell) < popsize:
            candidates = [optimizer.ask() for _ in range(num_workers)]
            remote_samples = [submit_run(remote_candidate, remote_model, remote_observations, client)
                              for remote_candidate in client.scatter(candidates)]
            completed_queue = as_completed(remote_samples, with_results=True)
            for batch in completed_queue.batches():
                for future, (candidate, loss, time) in batch:
                    log.append((candidate, loss, time))
                    if np.isfinite(loss):
                        to_tell.append((candidate, loss))
                    else:
                        r = weighted_success_rate(log, 1 / num_workers)
                        if len(to_tell) + r * completed_queue.count() < popsize:
                            candidate = optimizer.ask()
                            remote_sample = submit_run(candidate, remote_model, remote_observations, client)
                            completed_queue.add(remote_sample)

        for candidate, loss in to_tell:
            optimizer.tell(candidate, loss)

        cleanup = client.map(lambda: subprocess.run(['rm', '-r', '$TMPDIR/geotop_inputs_*']), range(num_workers))
        fire_and_forget(cleanup)

    elapsed = timer() - start

    return optimizer.provide_recommendation(), log, elapsed
