# Implementation

```{epigraph}

Talk is cheap, show me the code.

-- Linus Torvalds
```

## Model and Objective Function

As discussed in the previous chapter, in order to have a functioning interface to the GEOtop model using GEOtoPy it is necessary to specify how to do preprocessing of the data (basically meteorological forcings and input parameters) and postprocessing of simulation results. The following is the implementation used for simulations with uniform soil parameters.

```python
import json
import importlib.resources as resources
from geotopy import GEOtop
from mhpc_project.utils import postprocess_full

class UniformSoilModel(GEOtop):
    with resources.open_text('mhpc_project', 'uniform_defaults.json') as file:
        default_settings = json.load(file)

    def preprocess(self, working_dir, *args, **kwargs):
        settings = self.settings.copy()
        settings.update(self.default_settings)
        settings.update(args[0])
        self.clone_into(working_dir)
        self.patch_inpts_file(working_dir, settings)

    def postprocess(self, working_dir):
        settings = self.read_settings(working_dir / 'geotop.inpts')
        return postprocess_full(settings, working_dir)
```

In this case, preprocessing is trivial and consist of copying the files to the proper directory and patching the `geotop.inpts` with the new value of the parameters. Notice that the `self.settings` dictionary of settings is copied to avoid nefarious side effects. Preprocessing also takes care of appling some defaults settings, which are assumed in the postprocessing phase.

The postprocess is just a wrapper around a utility function. This is because the same postprocessing is done also in the variable soil model, discussed below. In this way one can avoid code duplication without introducing a intermediate class in the inheritance scheme.

Once having a functioning model, the objective function can be easily implemented.

```python
def objective(model, candidate, observations):
    try:
        with TemporaryDirectory() as tmpdir:
            predictions = model.run_in(tmpdir, *candidate.args, **candidate.kwargs)
    except (CalledProcessError, TimeoutExpired):
        predictions = None
    return compare(predictions, observations)
```

The `compare` function should return the loss value. A good choice is to use the Kling-Gupta or Nash-Sutcliffe efficiencies, which are well-suited for hydrological models, notice however that higher number of these correspond to better overlap of simulation and observations.

Using `TemporaryDirectory` from the tempfile module allows running the model in `tmpfs` (i.e. in RAM) and automatic deletion of files on exit (also in case of exceptions and canceled Dask task). The `CalledProcessError` and `TimeoutExpired` exceptions from the subprocess module must be caught since they represent routine GEOtop failures. Other exceptions will be propagated since they signal abnormal behaviours. 

## A Closer Look at the Optimization Loop

A wide class of algorithms can be implemented using the unique interface described in {cite}`collette2013object`, and the ones sketched in the chapter {ref}`content:optimization` belong to them. Let's say we want to minimize the objective function `f`, the optimization loop will look like the following

```python
while not optimizer.stop():
    x = optimizer.ask()
    y = f(x)
    optimizer.tell(x, y)
```

The pseudocode is rather self explicative: the `optimizer.stop` method must implement some stopping criterion, the `optimizer.ask` method suggests a new point where to evaluate the objective function, and `optimizer.tell` communicates the result to the optimizer. This design allows decoupling the optimizer from the objective function. 

Since the state of the `optimizer` object contains the information about the history of evaluations, different criteria are possible, such as asking a decrease of the objective above some threshold. The simplest is to use an internal counter to allow a maximum number of objective evaluations, the budget in the Nevergrad parlance. It is crucial to notice that the number of `optimizer.ask` calls can differ from the one of `optimizer.tell` calls.

As it is, the loop is fully serial. We need an optimization algorithm capable of suggesting several points at ones to make it parallel. The requirement is non-trivial, for example Bayesian optimization does not fulfill it. Evolutionary algorithms generally satisfy the requirement, since individuals of the same generation are independent one another.

A parallelizable loop using generation count as stopping criterion will look like the following.

```python
for _ in range(num_generations):
    for i in range(popsize):
        x[i] = optimizer.ask()
        
    for i in range(popsize):
        y[i] = f(x[i])
        
    for i in range(popsize):
        optimizer.tell(x[i], y[i])
```

In theory, `optimizer.ask` could be read-only, and the first loop could be executed in parallel. In practice, it must change the state of the internal pseudo-random generator. Since `optimizer.tell` changes the state of the object (with exception of random search), concurrent execution of the third loop is guaranteed to cause race conditions unless `optimizer.tell` uses some mutex. However, both `optimizer.ask` and `optimizer.tell` are not supposed to be expensive to call[^expensive_ask], hence their loops can be executed in serial fashion without performance degradation.

[^expensive_ask]: This is true within a generation. From one generation and the next, in case of large population size, the optimizer can perform expensive computations.

When the objective function evaluation is time-consuming, as it is the case for GEOtop, most of the time is spent in the second loop. The objective loop is embarrassingly parallel and can be executed concurrently for example using futures. Let's suppose to have a Dask Client `client`, the loop becomes.

```python
for _ in range(num_generations):
    for i in range(popsize):
        x[i] = optimizer.ask()
        
    for i in range(popsize):
        futures[i] = client.submit(f, x[i])
    
    for i in range(popsize):
        y[i] = futures[i].result()
        
    for i in range(popsize):
        optimizer.tell(x[i], y[i])
```

The first two loops can be fused, as well as the second two. Notice that Dask assumes that `f` is a pure function (otherwise, the whole computation would not make sense anyway).

The previous design however has a serious flaw: the third loop is executed synchronously (there is no event loop) and `future.result()` is blocking. Therefore, the interpreter will wait the first future, then the second, and so go on. However, since the execution time of `f` is random (and varies in a large interval of values), some results may be ready much before their turn. Fortunately Dask Distributed as the `as_completed` class, which iterates the futures as soon as they are done.

However, since we lost the information about the order of the results, we need to use a small wrapper that keeps track of the argument and the loss.

```python
for _ in range(num_generations):
    for i in range(popsize):
        x[i] = optimizer.ask()
        
    for i in range(popsize):
        futures[i] = client.submit(lambda x: (x, f(x)), x[i])
   
    to_tell = [] 
    for future in as_completed(futures):
        to_tell.append(future.result())
        
    for x, y in to_tell:
        optimizer.tell(x, y)
```

Such optimization loop still does not take into account objective function failures. In our implementation failing computations return nan. We can check that the result is valid using the `isfinite` function from Numpy. It is possible to elegantly solve the problem by submitting other computations to `as_completed`. Indeed, it has two methods `as_completed.add` and `as_completed.update` which allow adding one or more futures to the queue respectively, and a `as_completed.count()` method which counts how many futures are still in the queue.

```python
completed_queue = as_completed(futures)   
to_tell = []
for future in completed_queue:
    x, y = future.result()
    if isfinite(y):
        to_tell.append(future.result())
    if len(to_tell) + completed_queue.count() < popsize:
        new_x = optimizer.ask()
        new_future = client.submit(lambda x: (x, f(x)), new_x)
        completed_queue.add(new_future)
```

The previous code works since to exit the loop `completed_queue` must be empty. If `completed_queue` is empty, then bottom of the loop has been reached without a insertion of a new future, that is `len(to_tell) + completed_queue.count() < popsize` must have been false. But `completed_queue.count()` is equal to zero, hence `len(to_tell) >= popsize`. However, the number of failures equals the number of insertions, hence `len(to_tell) == popsize`.

Let's consider what happen when we reach the end of a generation. There are `popsize - 1` elements in `to_tell`, and if the objective fails a single new future is added to `completed_queue`: all CPUs except one will wait in idle. A better idea is to speculatively execute more objective functions, so to increase the chances that at least one of them does not fail.

```python
completed_queue = as_completed(futures)   
to_tell = []
for future in completed_queue:
    x, y = future.result()
    if isfinite(y):
        to_tell.append(future.result())
    if len(to_tell) + completed_queue.count() < popsize:
        for _ in range(num_new_futures):
            new_x = optimizer.ask()
            new_future = client.submit(lambda x: (x, f(x)), new_x)
            completed_queue.add(new_future)
```

In this way, there will be a buffer of approximately `num_new_futures` extra futures. Indeed, the upper bound for the size of the queue is `popsize - len(to_tell) + num_new_futures - 1`. However, with this modification there is no guarantee that at the end of a calculation we have `popsize` elements in `to_tell`. Usually this is not a problem, since the optimizer will throw away the worst individuals (or include them in computations, in a non-elitist fashion). However, we can enforce the old behaviour using a `break` statement and `completed_queue.clear()`. When the latter is called, the futures still in the queue are garbage collected, and Dask cancels the corresponding computations.

```python
completed_queue = as_completed(futures)   
to_tell = []
for future in completed_queue:
    x, y = future.result()
    if isfinite(y):
        to_tell.append(future.result())
    if len(to_tell) >= popsize:
        break
    else:
        if len(to_tell) + completed_queue.count() < popsize:
            for _ in range(num_new_futures):
                new_x = optimizer.ask()
                new_future = client.submit(lambda x: (x, f(x)), new_x)
                completed_queue.add(new_future)
completed_queue.clear()
```

However, this introduces a bias: futures that terminates earlier have more chance to be reported to the optimizer, whatever their loss is. This new behaviour is located near the end of a generation, when the computation start to consume the buffer, and it is more evident the larger `num_new_futures`.

Let's suppose that we are able to guess how many computations will be successful. In this case, we could add to the queue only the futures that will be consumed. If the fraction of valid futures in the queue is `r` then we will need to add new futures to the queue only if `len(to_tell) + r * completed_queue.count() < popsize`. Not only, we can now get rid of the free parameter `num_new_futures`. Indeed, if `r` can be expected to stay constant within a generation, a reasonable heuristic is to add each time `(popsize - len(to_tell) - r * completed_queue.count()) / r` new futures.

The actual optimization loop used implements this strategy, estimating `r` as the weighted average success rate using the following function.
```python
# log is a list of triples [(individual, loss, execution time)]
def average_success_rate(log, alpha):
    if log:
        successes = [1 if np.isfinite(l) else 0 for (_, l, _) in reversed(log)]
        weights = [exp(-alpha * n) for n in range(len(log))]
        return sum(w * x for w, x in zip(weights, successes)) / sum(weights)
    else:
        return 1.0
```
In this way, the success rate looses memory of older evaluations. The timescale parameter `alpha` is chosen as `1 / popsize`.

However, it turns out that this strategy fails when the number of missing futures is small. For this reason the actual optimization loop implements also an `overshoot` parameter that allows to submit more new futures than estimated (but introducing again a bias related to execution times). Also, the actual implementation prefetches futures in batches, and pre-scatters the data across the Dask cluster.

```{bibliography}
:filter: docname in docnames
```
