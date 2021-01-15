import nevergrad as ng
import numpy as np
from dask.distributed import as_completed

from .comparators import KGE
from .utils import objective_function


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
            model_future = client.scatter(self.model, broadcast=True)
            comparators_future = client.scatter(self.comparators, broadcast=True)
            futures = [client.submit(objective_function, model_future, comparators_future, optimizer.ask())
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
                                                   model_future,
                                                   comparators_future,
                                                   optimizer.ask())
                        completed_queue.add(new_future)

        return optimizer.provide_recommendation()
