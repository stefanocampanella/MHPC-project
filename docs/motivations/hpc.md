# The need for HPC

```{epigraph}
The old joke is "HPC is the art of taking a CPU-bound computation and making it I/O bound"

-- dnautics, comment on Hacker News
```

I anticipated that the calibration process is time-consuming. What does this mean exactly?

## The curse of dimensionality

Let's consider an imaginary calibration. The first problem is to establish what is the scale at which variations in a
parameter produce relevant variations in the output of the model. Note that this quantity may not be constant, meaning
that small changes can produce huge differences in a region of the parameters space and negligible in another.
Furthermore, the parameter might take values in an interval or a very complicated domain, for example, with constraints
given by other parameters. So paradoxically even before doing the calibration, we would need precise knowledge of the
cost function to design a numerical experiment.

Anyway, in the simplest model possible, each parameter can be quantized with one bit, and it is enough to sample just
two of its values. Most readers will readily recognize the resemblance with the wheat and chessboard problem. With only
20 parameters, a perfectly reasonable number for these models, if not small, a brute force search would need $2^{20}
\approx 10^6$ evaluations of the cost function, which, as mentioned in the last chapter, take about one minute each.
Hence a calibration of this toy model with 20 parameters would take two years on a single CPU, with 30 parameters 2000
years.

The moral of the story is twofold: 1) that whatever algorithm we choose, it must significantly outperform random or grid
search, 2) this algorithm must be executed in parallel to some degree. Ironically, random and grid search algorithms are
the only truly embarrassingly parallel ones. Still, even on large supercomputers with hundreds of thousands of CPUs, the
volume of the search space is just too large to use them.

## Optimize the optimzer

The class of iterative algorithms which I will consider will use a random search at each step, making educated guesses.
Hence within each step, one can perform massively parallel computations with very little communication among processes.
But since there is a data dependency between one step and the following, these algorithms have an unavoidable sequential
part.

Here comes a crucial observation. Having access to a supercomputer, one could think to scale the parallel part up with
impunity and find better results in the same amount of time or find the same ones in a shorter time. Unfortunately, this
is not the case. As we scale the parallel part up, the number of steps to reach convergence generally increases, hence
the time to solution. In other words, there is no way to go faster and scaling up means go slower.

Given that, it could seem that the solution is to scale down the parallel part. But this misses an important point:
increasing the number of guesses made at each step increases the chances to escape from a particular local minimum (
indeed, this is why convergence slow down) and reach a better solution. Hence there will be a lower bound for this
number under which the calibration will return "bad values" of the parameters.

Which strategy (algorithm, number of concurrent guesses and iterations) returns "right enough" values the quickest? To
find it, one can design a numerical experiment in which several calibrations take place at the same time, each one using
a different one. But if you think about it, this is again an optimization problem.

However, it is a multi-objective optimization, and the cost functions (whose arguments are the hyper-parameters of the
strategy) are the fitness of the parameters found by calibration and the time to solution. To solve this problem, we can
use the same algorithms, which, as discussed, have some degree of concurrency. But each evaluation of these cost
functions requires many concurrent simulations. Finally, since the considered algorithms have a stochastic component, we
need to run each calibration several times and average. Because concurrency is a multiplicative quantity, performing
this hyper-parameters optimization requires a massive amount of parallel runs of GEOtop. Therefore such a numerical
experiment is possible only on a modern supercomputer with many processing units.

## Scaling doesn't matter, it's how you use it

In the previous section, I explained why High-Performance Computing resources are needed. Of course, it is interesting
to see *how* these are employed. There are at least two HPC relevant aspects:

1. How to distribute the work in a single calibration
2. How to schedule multiple calibrations

Furthermore, the scheduling must be asynchronous and guarantees some form of resiliency if something fails.

The following sections, which explain the implementation of the numerical experiments, should be a sufficient commentary
about these aspects and show the relevance of HPC techniques to the solution of the particular problem of GEOtop
calibration.

However, one must admit that black-box optimization is not a typical HPC application. As discussed, it does not scale,
and therefore, it isn't easy to benchmark. The domain of the problem one is trying to solve remains fixed, the solution
changes from run to run without tending toward a particular value, and the time to solution increase on parallel
execution instead of decreasing. Therefore, it is challenging to produce a good looking scaling plot and even to define
what weak or hard scaling means in this context.

Furthermore, the specific set of HPC techniques (a conveniently broad term) used in black-box optimizations depends on
the particular model. A climatological model may present different challenges from drug discovery research. Nonetheless,
from a strictly computational perspective, placing your objective function in one of the four quadrants of a plane where
the axes are the boundedness (CPU, IO) and cost (cheap, expensive) is a good indication of what to expect.

For example, the execution of cheap CPU-bounded functions may need a very responsive scheduler, as you may receive too
many TCP requests on a distributed system or even waste too much time on forking and joining threads. An expensive
IO-bound function will require almost certainly a distributed file system.

Finally, I would like to point out that the calibration of physical or machine learning models is a vast, rapidly
evolving field.

On the one hand, it's an effective way of taking advantage of supercomputer resources for tackling a real-world research
problem without rewriting old, sequential code, sometimes known to work, virtually, without bugs. On the other, it is a
way of dealing with models of which we have very little understanding (es. neural networks). Moral of the story: know
how to deal with calibrations on a supercomputer is a marketable HPC skill!
