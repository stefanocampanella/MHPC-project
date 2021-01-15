import nevergrad as ng
import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from dask.distributed import as_completed

from .comparators import KGE
from .utils import comparison_plot


def objective_function(model, comparators, candidate):
    sim = model(*candidate.args, **candidate.kwargs)

    square_loss = sum(f(sim[target]) ** 2 for target, f
                      in comparators.items() if target in sim)

    return candidate, np.sqrt(square_loss)


class Calibration:

    def __init__(self, model, parameters, observations):
        self.model = model
        self.parameters = parameters
        self.observations = observations
        self.comparators = {col: KGE(self.observations[col]) for col in self.observations.columns}
        self.log = []

    def __call__(self, algorithm, budget, num_workers, client):
        optimizer_class = ng.optimizers.registry[algorithm]
        optimizer = optimizer_class(self.parameters.instrumentation,
                                    budget=np.inf,
                                    num_workers=num_workers)

        while optimizer.num_tell < budget:
            client.scatter(self.model, broadcast=True)
            client.scatter(self.comparators, broadcast=True)
            futures = [client.submit(objective_function, self.model, self.comparators, optimizer.ask())
                       for _ in range(num_workers)]
            completed_queue = as_completed(futures)
            for batch in completed_queue.batches():
                for future in batch:
                    if future.status == 'finished':
                        candidate, loss = future.result()
                        optimizer.tell(candidate, loss)
                        self.log.append((candidate.generation, loss))
                    else:
                        new_future = client.submit(objective_function,
                                                   self.model,
                                                   self.comparators,
                                                   optimizer.ask())
                        completed_queue.add(new_future)

        return optimizer.provide_recommendation()

    def convergence_plot(self, figsize=(16, 9), dpi=100):
        max_generation_number = max(n for n, _ in self.log)
        min_losses = np.fromiter([min(l for n, l in self.log if n <= k)
                                  for k in range(1, max_generation_number + 1)], dtype=float)
        data = pd.DataFrame(self.log, columns=['generation', 'loss'])
        figure, axes = plt.subplots(figsize=figsize, dpi=dpi)
        sns.lineplot(data=data, x='generation', y='loss', ax=axes)
        sns.lineplot(x=range(1, max_generation_number + 1), y=min_losses, ax=axes)

        return figure

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
