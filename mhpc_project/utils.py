import shutil
import tempfile
from datetime import datetime
from math import sqrt, exp
from pathlib import Path
from subprocess import CalledProcessError, TimeoutExpired
from tempfile import TemporaryDirectory
from timeit import default_timer as timer

import nevergrad as ng
import numpy as np
import pandas as pd
from SALib.analyze import delta
from dask.distributed import as_completed, wait
from nevergrad.parametrization.parameter import Scalar, Log
from scipy.optimize import root_scalar


def date_parser(x):
    return datetime.strptime(x, '%d/%m/%Y %H:%M')


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
            predictions = model.run_in(tmpdir, *candidate.args, **candidate.kwargs)
    except (CalledProcessError, TimeoutExpired):
        predictions = None
    loss = kge_cmp(predictions, observations)
    elapsed = timer() - start
    return candidate, loss, elapsed


def average_success_rate(log, alpha):
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


def nodes_cleanup(client):
    workers_hosts = {}
    for address, worker in client.scheduler_info()['workers'].items():
        host = worker['host']
        if host not in workers_hosts:
            workers_hosts[host] = address
    cleanups = [client.submit(do_cleanup, workers=address)
                for address in workers_hosts.values()]
    wait(cleanups)
    cleanups.clear()


def calibrate(model, parameters, observations,
              algorithm, popsize, num_generations,
              client, num_workers, overshoot=2):
    log = []
    optimizer_class = ng.optimizers.registry[algorithm]
    optimizer = optimizer_class(parameters.instrumentation,
                                budget=np.inf,
                                num_workers=popsize)
    remote_observations = client.scatter(observations, broadcast=True)
    remote_model = client.scatter(model, broadcast=True)
    for _ in range(num_generations):
        to_tell = []
        remote_samples = [client.submit(wrapped_objective,
                                        remote_model,
                                        optimizer.ask(),
                                        remote_observations)
                          for _ in range(num_workers)]
        completed_queue = as_completed(remote_samples, with_results=True)
        for batch in completed_queue.batches():
            for future, (candidate, loss, time) in batch:
                log.append((candidate, loss, time))
                if np.isfinite(loss):
                    to_tell.append((candidate, loss))
            if len(to_tell) >= popsize:
                break
            else:
                r = average_success_rate(log, 1 / popsize)
                if (num_remaining_samples := popsize - len(to_tell) - r * completed_queue.count()) > 0:
                    if r > 0:
                        num_new_samples = min(num_workers, int(overshoot * num_remaining_samples / r))
                    else:
                        num_new_samples = num_workers
                    remote_samples = [client.submit(wrapped_objective,
                                                    remote_model,
                                                    optimizer.ask(),
                                                    remote_observations)
                                      for _ in range(num_new_samples)]
                    completed_queue.update(remote_samples)

        completed_queue.clear()

        for candidate, loss in to_tell:
            optimizer.tell(candidate, loss)

    recommendation = optimizer.recommend()
    predictions = None
    while predictions is None:
        try:
            recommendation = recommendation.spawn_child()
            predictions = model(*recommendation.args, **recommendation.kwargs)
        except (CalledProcessError, TimeoutExpired):
            predictions = None

    return recommendation, predictions, log


def is_cell_ok(cell):
    cell_type = cell['cell_type']
    cell_status = cell['metadata']['papermill']['status'] == 'completed'
    if cell_type == 'markdown':
        return cell_status
    elif cell_type == 'code':
        return cell['execution_count'] and cell_status
    else:
        raise ValueError(f"Unknown cell type {cell_type}")


def notebook_status(notebook):
    if notebook.metadata['papermill']['exception']:
        return 'exception'
    if all(is_cell_ok(cell) for cell in notebook.cells):
        return 'completed'
    else:
        return 'uncompleted'


def get_scaling_data(book, efficiency=False):
    data = []
    for name, nb in book.items():
        if notebook_status(nb) == 'completed':
            parameters = nb.metadata['papermill']['parameters']
            record = {key: value for key, value in parameters.items()
                      if key in ['num_cpus', 'popsize', 'num_generations']}
            record['name'] = name
            record['duration'] = nb.metadata['papermill']['duration']
            if efficiency:
                num_cpus = record['num_cpus']
                duration = record['duration']
                tasks_duration = sum(t for _, l, t in nb.scraps['log'].data if l != 'nan')
                record['efficiency'] = tasks_duration / (num_cpus * duration)
            data.append(record)
    return pd.DataFrame.from_records(data)


def delta_mim(parameters, candidates_dict_log):
    samples = []
    losses = []
    for candidate, loss in candidates_dict_log:
        sample = parameters.from_dict(candidate)
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
