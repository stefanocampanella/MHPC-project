import nevergrad as ng
import numpy as np
import pandas as pd
from dask.distributed import as_completed
from tqdm.auto import tqdm

from .comparators import KGE
from .utils import comparison_plot


# The objective function must be a callable object
# which can be serialized using cloudpickle by Dask.
class ObjectiveFunction:

    def __init__(self, model, observations):
        self.model = model
        self.comparators = {}
        for target in observations.columns:
            self.comparators[target] = KGE(observations[target])

    def __call__(self, candidate):
        predictions = self.model(*candidate.args, **candidate.kwargs)

        square_loss = sum(comp(predictions[target]) ** 2 for target, comp
                          in self.comparators.items() if target in predictions)

        return candidate, np.sqrt(square_loss)


class Calibration:

    def __init__(self, model, parameters, observations):
        self.model = model
        self.parameters = parameters
        self.observations = observations
        self.objective_function = ObjectiveFunction(model, observations)
        self.log = []

    def __call__(self, algorithm, budget, popsize, client, show_progress=False):
        optimizer_class = ng.optimizers.registry[algorithm]
        optimizer = optimizer_class(self.parameters.instrumentation,
                                    budget=np.inf,
                                    num_workers=popsize)

        with tqdm(total=budget, disable=not show_progress) as progress_bar:
            while optimizer.num_tell < budget:
                asked_points = [optimizer.ask() for _ in range(popsize)]
                # To avoid annoyances with argument unpacking,
                # ensure that loss takes just one argument.
                # The best option is passing (and return) the whole candidate object.
                # Otherwise, because as_completed change the order of the inputs,
                # one should keep track of the candidates to which the losses belong.
                futures = client.map(self.objective_function, asked_points)
                completed_queue = as_completed(futures)
                for batch in completed_queue.batches():
                    for future in batch:
                        if future.status == 'finished':
                            result = future.result()
                            optimizer.tell(*result)
                            self.log.append(result)
                            progress_bar.update()
                        else:
                            # See the executor.map comment
                            new_future = client.submit(self.objective_function, optimizer.ask())
                            completed_queue.add(new_future)

        recommendation = optimizer.provide_recommendation()
        predictions = self.objective_function.model(*recommendation.args, **recommendation.kwargs)

        return predictions, recommendation

    def comparison_plots(self, candidate, **kwargs):
        predictions = self.model(*candidate.args, **candidate.kwargs)
        for target in self.observations.columns:
            if target in predictions.columns:
                desc = target.replace('_', ' ').title()
                comparison_plot(self.observations[target], predictions[target], desc=desc, **kwargs)

    def parameters_table(self, candidate):
        table = self.parameters.data.copy()
        table = table[['init', 'lower', 'upper']]
        extra, inpts, soil = (candidate.args[0][key] for key in ('extra', 'inpts', 'soil'))
        best = pd.DataFrame.from_dict({**extra, **inpts, **soil}, orient='index')
        table['best'] = best
        return table
