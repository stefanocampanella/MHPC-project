# The need for HPC

```{epigraph}
The old joke is "HPC is the art of taking a CPU-bound computation and making it I/O bound"

-- dnautics, comment on Hacker News
```

In the previous chapter, I anticipated that the calibration process is time-consuming. What does this mean exactly?

## The curse of dimensionality

Let's consider an imaginary calibration. The first problem is the discretization of the parameters space: i.e. establish what is the scale at which changes of a parameter produce relevant variations of the output of the model. Note that this quantity may not be constant, meaning that small changes can produce huge differences in a region of the parameters space and negligible in another. Furthermore, the parameters might take values on a domain with complicated shape. Paradoxically, even before doing the calibration, we would need precise knowledge of the objective function to design calibration. 

Anyway, in the simplest possible model, each parameter can be quantized with one bit, and it is enough to sample just two of its values. The reader will readily recognize the resemblance with the wheat and chessboard problem or viral disease spread. With only 20 parameters (a perfectly reasonable number for GEOtop, if not small), a brute force search would need $2^{20} \approx 10^6$ evaluations of the objective function. Hence, a calibration of this toy model with 20 parameters and one minute per objective evaluation would take two years on a single CPU, and 2000 years with 30 parameters.

The moral of the story is twofold: 1) whatever algorithm we choose, it must significantly outperform grid search, 2) this algorithm must be executed in parallel to some degree. Ironically, grid search algorithms is a truly embarrassingly parallel algorithm. Still, even on large supercomputers with hundreds of thousands of CPUs, the volume of the search space is just too large to use it.

## Evolutionary Algorithms

The evolutionary algorithms used for calibration basically use random search at each iteration, making increasingly educated guesses. Within each iteration, one can perform massively parallel computations with very little communication among processes. However, since there is data dependency between one iteration and the following, these algorithms cannot scale indefinitely. Nonetheless, the upper limit for scaling within a iteration usually depends on a free parameter.

Having access to a supercomputer, one could think to tweak this parameter and scale up the number processing units with impunity. This way, he could keep the same number of iterations and find "better" results in the same amount of time, or use fewer iterations and find the old results in shorter time. Unfortunately, this is not the case. 

As a first approximation, we can decompose calibration in two tasks. The first is locating the region of the search space containing the global minimum, and the second is exploring this region to locate its exact value. Increasing the number of guesses each iteration, which determines maximum scaling, increases the chances to escape from local minima, and move the exploration and refinement phase at later iterations. We can say that the convergence of the evolutionary algorithm slows down. Conversely, the fewer the guesses at each iteration, the sooner the local-search behaviour kicks in. 

It is reasonable that a sweet spot for the number of guesses exists, providing acceptable solutions in the least amount of time. The optimal combination of algorithm, number of concurrent guesses and iterations must be determined by empirical studies, in lack of a general theory. These empirical studies may use optimization algorithms as well, instead of trying each possible combination, as done in grid search. Since the degree of concurrency is multiplicative under composition, optimization of calibration hyperparameters could easily exceed a large supercomputer capacity.


## Scaling in Theory and in Practice

In the previous section, I explained why High-Performance Computing resources are needed. Of course, it is interesting to see *how* these are employed. There are at least two HPC relevant aspects:

1. How to distribute the work in a single calibration
2. How to schedule multiple calibrations

Furthermore, the scheduling must be asynchronous and guarantees some form of resiliency if something fails.

The following sections, which explain the implementation of the numerical experiments, should be a sufficient commentary about these aspects and show the relevance of HPC techniques to the solution of the particular problem of GEOtop calibration.

However, one must admit that black-box optimization is not a typical HPC application. As discussed, it does not scale, and therefore, it isn't easy to benchmark. The domain of the problem one is trying to solve remains fixed, the solution changes from run to run without tending toward a particular value, and the time to solution increase on parallel execution instead of decreasing. Therefore, it is challenging to produce a good looking scaling plot and even to define what weak or hard scaling means in this context.

Furthermore, the specific set of HPC techniques (a conveniently broad term) used in black-box optimizations depends on the particular model. A climatological model may present different challenges from drug discovery research. Nonetheless, from a strictly computational perspective, placing your objective function in one of the four quadrants of a plane where the axes are the boundedness (CPU, IO) and cost (cheap, expensive) is a good indication of what to expect.

For example, the execution of cheap CPU-bounded functions may need a very responsive scheduler, as you may receive too many TCP requests on a distributed system or even waste too much time on forking and joining threads. An expensive IO-bound function will require almost certainly a distributed file system.

Finally, I would like to point out that the calibration of physical or machine learning models is a vast, rapidly evolving field.

On the one hand, it's an effective way of taking advantage of supercomputer resources for tackling a real-world research problem without rewriting old, sequential code, sometimes known to work, virtually, without bugs. On the other, it is a way of dealing with models of which we have very little understanding (es. neural networks). Moral of the story: know how to deal with calibrations on a supercomputer is a marketable HPC skill!
