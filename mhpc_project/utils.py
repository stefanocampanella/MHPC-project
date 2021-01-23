import shutil
import tempfile
from datetime import datetime
from math import sqrt, exp
from pathlib import Path
from subprocess import CalledProcessError, TimeoutExpired
from tempfile import TemporaryDirectory
from timeit import default_timer as timer

import matplotlib.pyplot as plt
import matplotlib.ticker as mtick
import nevergrad as ng
import numpy as np
import pandas as pd
import seaborn as sns
from SALib.analyze import delta
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


def read_soil_profile(working_dir, basename, header, depths, index):
    names = [header.format(d) for d in depths]
    profile_path = working_dir / (basename + '.txt')
    profile = pd.read_csv(profile_path,
                          na_values=['-9999'],
                          skiprows=1,
                          header=0,
                          names=['skipme'] + names,
                          usecols=names,
                          low_memory=False)
    profile.index = index
    return profile


def postprocess_full(settings, working_dir):
    def setting_string(name):
        return settings[name].strip('"')

    data = []

    point_setting = setting_string('PointOutputFileWriteEnd')
    point_path = working_dir / (point_setting + '.txt')
    point = pd.read_csv(point_path,
                        na_values=['-9999'],
                        parse_dates=[0],
                        date_parser=date_parser,
                        index_col=0,
                        low_memory=False)

    fluxes = pd.DataFrame(index=point.index)
    canopy_fraction = point[setting_string('HeaderCanopyFractionPoint')]

    leg_veg = point[setting_string('HeaderLEgVegPoint')]
    lev = point[setting_string('HeaderLEvPoint')]
    leg_unveg = point[setting_string('HeaderLEgUnvegPoint')]
    fluxes['latent_heat'] = canopy_fraction * (leg_veg + lev) + (1 - canopy_fraction) * leg_unveg

    hg_veg = point[setting_string('HeaderHgVegPoint')]
    hv = point[setting_string('HeaderHvPoint')]
    hg_unveg = point[setting_string('HeaderHgUnvegPoint')]
    fluxes['sensible_heat'] = canopy_fraction * (hg_veg + hv) + (1 - canopy_fraction) * hg_unveg

    fluxes['soil_heat'] = point[setting_string('HeaderSoilHeatFluxPoint')]
    data.append(fluxes)

    depths = settings['SoilPlotDepths']
    liq = read_soil_profile(working_dir,
                            setting_string('SoilLiqContentProfileFileWriteEnd'),
                            "soil_moisture_{:.0f}",
                            depths,
                            point.index)
    ice = read_soil_profile(working_dir,
                            setting_string('SoilIceContentProfileFileWriteEnd'),
                            "soil_moisture_{:.0f}",
                            depths,
                            point.index)
    theta = liq + ice
    data.append(theta)

    temperature = read_soil_profile(working_dir,
                                    setting_string('SoilTempProfileFileWriteEnd'),
                                    "soil_temperature_{:.0f}",
                                    depths,
                                    point.index)
    data.append(temperature)

    return pd.concat(data)


def make_nevergrad_parameter(mapping, **kwargs):
    if mapping == 'linear':
        return Scalar(**kwargs)
    elif mapping == 'exp':
        return Log(**kwargs)
    else:
        raise ValueError("Unknown type of mapping {mapping}.")


def convergence_plot(gen_loss_log, figsize=(16, 9), dpi=100):
    max_generation_number = max(n for n, _ in gen_loss_log)
    min_losses = [min(l for n, l in gen_loss_log if n <= k)
                  for k in range(1, max_generation_number + 1)]
    data = pd.DataFrame(gen_loss_log, columns=['generation', 'loss'])
    figure, axes = plt.subplots(figsize=figsize, dpi=dpi)
    sns.lineplot(data=data, x='generation', y='loss', ax=axes)
    sns.lineplot(x=range(1, max_generation_number + 1), y=min_losses, ax=axes)


def comparison_plots(predictions, observations, **kwargs):
    for target in observations.columns:
        if target in predictions.columns:
            desc = target.replace('_', ' ').title()
            comparison_plot(observations[target], predictions[target], desc=desc, **kwargs)


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


def wrapped_objective(model, candidate, observations):
    start = timer()
    try:
        with TemporaryDirectory(prefix='geotop_inputs_') as tmpdir:
            result = model.run_in(tmpdir, *candidate.args, **candidate.kwargs)
    except (CalledProcessError, TimeoutExpired):
        result = None
    elapsed = timer() - start
    return candidate, kge_cmp(result, observations), elapsed


def weighted_success_rate(log, alpha):
    if log:
        successes = [1 if np.isfinite(l) else 0 for (_, l, _) in reversed(log)]
        weights = [exp(-alpha * n) for n in range(len(log))]
        return sum(w * x for w, x in zip(weights, successes)) / sum(weights)
    else:
        return 1.0


def do_cleanup():
    tempdir = Path(tempfile.gettempdir())
    for geotop_inpts_path in tempdir.glob('geotop_inputs_*'):
        shutil.rmtree(geotop_inpts_path)


def calibrate(model,
              parameters,
              observations,
              algorithm,
              popsize,
              num_generations,
              client,
              num_workers,
              alpha=None,
              overshoot=4):
    alpha = alpha if alpha else 1 / num_workers
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
            remote_samples = [client.submit(wrapped_objective,
                                            remote_model,
                                            remote_candidate,
                                            remote_observations)
                              for remote_candidate in client.scatter(candidates)]
            completed_queue = as_completed(remote_samples, with_results=True)
            for batch in completed_queue.batches():
                for future, (candidate, loss, time) in batch:
                    log.append((candidate, loss, time))
                    if np.isfinite(loss):
                        to_tell.append((candidate, loss))
                    else:
                        r = weighted_success_rate(log, alpha)
                        if len(to_tell) + r * completed_queue.count() < popsize:
                            if r > 0:
                                num_new_samples = min(num_workers, int(overshoot / r))
                            else:
                                num_new_samples = num_workers
                            for _ in range(num_new_samples):
                                candidate = optimizer.ask()
                                remote_sample = client.submit(wrapped_objective,
                                                              remote_model,
                                                              candidate,
                                                              remote_observations)
                                completed_queue.add(remote_sample)
        for candidate, loss in to_tell:
            optimizer.tell(candidate, loss)

        workers_hosts = {}
        for address, worker in client.scheduler_info()['workers'].items():
            host = worker['host']
            if host not in workers_hosts:
                workers_hosts[host] = address
        for address in workers_hosts.values():
            cleanup = client.submit(do_cleanup, workers=address)
            fire_and_forget(cleanup)
    elapsed = timer() - start

    recommendation = optimizer.provide_recommendation()
    return recommendation, model(*recommendation.args, **recommendation.kwargs), log, elapsed


def delta_mim(parameters, candidates_log):
    samples = []
    losses = []
    for candidate, loss in candidates_log:
        sample = parameters.from_instrumentation(candidate)
        if parameters.defaults:
            sample.drop(parameters.defaults, inplace=True)
        sample = sample.to_numpy()
        samples.append(sample)
        losses.append(loss)
    samples = np.asarray(samples)
    losses = np.asarray(losses)

    bounds = {key: value for key, value in parameters.bounds.items()
              if key not in parameters.defaults}
    problem = {'num_vars': len(bounds),
               'names': list(bounds),
               'bounds': bounds}

    return delta.analyze(problem, samples, losses).to_df()
