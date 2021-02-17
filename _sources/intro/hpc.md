# The need for HPC

```{epigraph}
The old joke is "HPC is the art of taking a CPU-bound computation and making it I/O bound"

-- dnautics, comment on Hacker News
```

In the previous chapter, I anticipated that the calibration process is time-consuming. What does this mean exactly?

## The Curse of Dimensionality

Let's consider an imaginary calibration. The first problem is the discretization of the parameters space: i.e. establish what is the scale at which changes of a parameter produce relevant variations of the output of the model. Note that this quantity may not be constant, meaning that small changes can produce huge differences in a region of the parameters space and negligible in another. Furthermore, the parameters might take values on a domain with complicated shape. Paradoxically, even before doing the calibration, we would need precise knowledge of the objective function to design calibration. 

Anyway, in the simplest possible model, each parameter can be quantized with one bit, and it is enough to sample just two of its values. The reader will readily recognize the resemblance with the wheat and chessboard problem or viral disease spread. With only 20 parameters (a perfectly reasonable number for GEOtop, if not small), a brute force search would need $2^{20} \approx 10^6$ evaluations of the objective function. Hence, a calibration of this toy model with 20 parameters and one minute per objective evaluation would take two years on a single CPU, and 2000 years with 30 parameters.

The moral of the story is twofold:

1. whatever algorithm we choose, it must significantly outperform grid search, and
2. this algorithm must be executed in parallel to some degree. 
   
Ironically, grid search algorithms is a truly embarrassingly parallel algorithm. Still, even on large supercomputers with hundreds of thousands of CPUs, the volume of the search space is just too large to use it.

## Scalability of Evolutionary Algorithms

The evolutionary algorithms used for calibration basically use random search at each iteration, making increasingly educated guesses. Within each iteration, one can perform massively parallel computations with very little communication among processes. However, since there is data dependency between one iteration and the following, these algorithms cannot scale indefinitely. Nonetheless, the upper limit for scaling within a iteration usually depends on a free parameter.

Having access to a supercomputer, one could think to tweak this parameter and scale up the number processing units with impunity. This way, he could keep the same number of iterations and find "better" results in the same amount of time, or use fewer iterations and find the old results in shorter time. Unfortunately, this is not the case. 

As a first approximation, we can decompose calibration in two tasks. The first is locating the region of the search space containing the global minimum, and the second is exploring this region to locate its exact value. Increasing the number of guesses each iteration, which determines maximum scaling, increases the chances to escape from local minima, and move the exploration and refinement phase at later iterations. We can say that the convergence of the evolutionary algorithm slows down. Conversely, the fewer the guesses at each iteration, the sooner the local-search behaviour kicks in. 

It is reasonable that a sweet spot for the number of guesses exists, providing acceptable solutions in the least amount of time. The optimal combination of algorithm, number of concurrent guesses and iterations must be determined by empirical studies, in lack of a general theory. These empirical studies may use optimization algorithms as well, instead of trying each possible combination, as done in grid search. Since the degree of concurrency is multiplicative under composition, optimization of calibration hyperparameters could easily exceed a large supercomputer capacity.


## Scaling in Theory and in Practice

```{epigraph}
In theory there is no difference between theory and practice - in practice there is

-- Yogi Berra
```

The remarks on scaling of the algorithms sketched in the previous section do not apply to their implementation. For example, they don't take into account finite data transfer bandwidths and latencies among CPUs. Also, they neglect the CPU cycles needed by the optimizer itself and consider only the load due to objective function evaluations. Therefore, the scaling of real calibration is a different matter. 

A crucial difference from the ideal case, is that the objective function is not a total function. There are values of the parameters for which GEOtop crashes, immediately or at later times, or it does not converge, and the computation takes forever. This occurrence has an impact both on the implementation and scaling. On the one hand, the implementation must have some form of resiliency against objective function failure. On the other, it motivates speculative execution: it is convenient to evaluate the objetive function more times than needed, using all the available CPUs, because some of them will fail. The consequences of objective function failure will be investigated in later chapters.

In the general case of black-box optimization, the specific bottlenecks that an implementation might find depends on the characteristics of the objective function. Placing the objective function in one of the four quadrants of a plane where the axes are the boundedness (CPU, IO) and cost (cheap, expensive) is a good indication of what to expect. 

For example, the execution of cheap CPU-bounded functions may need a very responsive scheduler, as you may receive too many requests on a distributed system or even waste too much time on forking and joining threads. An expensive IO-bound function will require almost certainly a distributed file system. 

This kind of optmization problems are common and already cited examples are earth-system model calibration and hyperparameters optimization in machine learning models. The application of HPC to these problems is an active reseach topic and a vast, rapidly evolving field.
