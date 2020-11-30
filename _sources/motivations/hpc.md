# The Need for HPC

```{epigraph}
HPC is the art of taking a CPU-bound computation and making it I/O bound
```

I anticipated that the calibration process is time-consuming. What does this mean exactly? 

## The curse of dimensionality 

Let's consider an imaginary calibration. The first problem is to establish what is the scale at which variations in a parameter produce relevant variations in the output of the model. Note that this quantity may not be constant, meaning that small changes can produce huge differences in a region of the parameters space and negligible in another. Furthermore, the parameter might take values in an interval or a very complicated domain, for example, with constraints given by other parameters. 
So paradoxically even before doing the calibration, we would need precise knowledge of the cost function to design a numerical experiment. 

Anyway, in the simplest model possible, each parameter can be quantized with one bit, and it is enough to sample just two of its values. Most readers will readily recognize the resemblance with the wheat and chessboard problem. With only 20 parameters, a perfectly reasonable number for these models, if not small, a brute force search would need $2^{20} \approx 10^6$ evaluations of the cost function, which, as mentioned in the last chapter, take about one minute each. Hence a calibration of this toy model with 20 parameters would take two years on a single CPU, with 30 parameters 2000 years.

The moral of the story is twofold: 1) that whatever algorithm we choose, it must significantly outperform random or grid search, 2) this algorithm must be executed in parallel to some degree. Ironically, random and grid search algorithms are the only truly embarrassingly parallel ones. Still, even on large supercomputers with hundreds of thousands of CPUs, the volume of the search space is just too large to use them.

The class of iterative algorithms which I will consider will use an educated random search at each step. Hence within each step, one can perform massively parallel computations with very little communication among processes. But since there is a data dependency between one step and the following, these algorithms have an unavoidable sequential part. Therefore we trade concurrency for efficiency, and it is conceivable that there exists a sweet spot. To find it, a numerical experiment can be designed in which several calibrations using a different strategy take place at the same time.

## The HPC relevance

Therefore if the curse of dimensionality explains why High-Performance Computing resources are needed, 
the interesting part is *how* these are employed. The problem has two HPC relevant aspects:

1. How to distribute the work in a single calibration
2. How to schedule multiple calibrations
 
The scheduling must be asynchronous and guarantees some form of resiliency if something fails.

This answer the question about the relevance of HPC techniques to the solution of the particular problem of GEOtop calibration. However, the calibration of physical or machine learning models is a vast field. 

On the one hand, it's an effective way of taking advantage of supercomputer resources for tackling a real-world research problem without rewriting old, sequential code, sometimes known to work, virtually, without bugs. On the other, it is a way of dealing with models of which we have very little understanding (es. neural networks). Moral of the story: know how to deal with calibrations on a supercomputer is a marketable HPC skill.

However, from above, it is clear that black-box optimization is not a standard HPC job. It is difficult to benchmark 


