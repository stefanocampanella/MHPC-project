from datetime import datetime
from subprocess import CalledProcessError, TimeoutExpired
from tempfile import TemporaryDirectory
from timeit import default_timer as timer

import matplotlib.pyplot as plt
import matplotlib.ticker as mtick
import nevergrad as ng
import numpy as np
import pandas as pd
import seaborn as sns
from dask.distributed import as_completed
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
    loss_log = [(x.generation, l) for x, l, _ in log]
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


def time_loss_plot(log, figsize=(16, 9), dpi=100):
    losses = [l for _, l, _ in log]
    times = [t for _, _, t in log]
    data = pd.DataFrame({'losses': losses, 'times': times})
    figure, axes = plt.subplots(figsize=figsize, dpi=dpi)
    sns.jointplot(data=data, x='losses', y='times', ax=axes)


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
        return np.sqrt(square_loss)


def run_model(model, candidate):
    start = timer()
    try:
        with TemporaryDirectory() as tmpdir:
            result = model.run_in(tmpdir, *candidate.args, **candidate.kwargs)
    except CalledProcessError or TimeoutExpired:
        result = None
    elapsed = timer() - start

    return result, elapsed


def calibrate(model, parameters, observations, budget, algorithm, num_workers, client):
    log = []
    start = timer()
    optimizer_class = ng.optimizers.registry[algorithm]
    optimizer = optimizer_class(parameters.instrumentation,
                                budget=np.inf,
                                num_workers=num_workers)

    remote_observations = client.scatter(observations, broadcast=True)
    remote_model = client.scatter(model, broadcast=True)
    while optimizer.num_tell < budget:
        remote_candidates = client.scatter([optimizer.ask() for _ in range(num_workers)])
        remote_timed_simulations = [client.submit(run_model, remote_model, candidate)
                                    for candidate in remote_candidates]
        remote_simulations = [client.submit(lambda x: x[0], timed_simulation)
                              for timed_simulation in remote_timed_simulations]
        remote_times = [client.submit(lambda x: x[1], timed_simulation)
                        for timed_simulation in remote_timed_simulations]
        remote_losses = [client.submit(kge_cmp, sim, remote_observations)
                         for sim in remote_simulations]
        remote_triples = [client.submit(lambda x, y, z: (x, y, z), candidate, loss, time)
                          for candidate, loss, time in zip(remote_candidates, remote_losses, remote_times)]
        completed_queue = as_completed(remote_triples, with_results=True)
        for batch in completed_queue.batches():
            for future, (candidate, loss, time) in batch:
                if np.isfinite(loss):
                    optimizer.tell(candidate, loss)
                    log.append((candidate, loss, time))
                else:
                    new_candidate = optimizer.ask()
                    new_timed_sim = client.submit(run_model, remote_model, new_candidate)
                    new_sim = client.submit(lambda x: x[0], new_timed_sim)
                    new_time = client.submit(lambda x: x[1], new_timed_sim)
                    new_loss = client.submit(kge_cmp, new_sim, remote_observations)
                    new_pair = client.submit(lambda x, y, z: (x, y, z), new_candidate, new_loss, new_time)
                    completed_queue.add(new_pair)
    elapsed = timer() - start

    return optimizer.provide_recommendation(), log, elapsed
