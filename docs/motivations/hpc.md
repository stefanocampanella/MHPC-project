# The Need for HPC

```{epigraph}
HPC is the art of taking a cpu-bound computation and making it I/O bound
```

I anticipated that the calibration process is time consuming. What does this means exactly? 
Let's consider an imaginary calibration. The first problem is to establish what
is the scale at which variations in a parameter produce relevant variations in 
the output of the model. Note that this quantity may not be constant, meaning that
small changes can produce huge differences in a region of the parameters space and 
negligible in another. Furthermore the parameter might take values in an interval or 
in a very complicated domain, for example with constrains given by other parameters. 
So even before doing the calibration we would need a precise knowledge of the cost function 
to design a numerical experiment. 

Anyway, in the simplest model possible each parameter can be quantized with one bit and 
it is enough to sample just two of its values. Most readers will readily recognize the 
resemblance with the wheat and chessboard story. With just 20 parameters, a perfectly reasonable 
number for these models, if not small, a brute force search would need $2^{20} \approx 10^6$ evaluations 
of the cost function. As we said each evaluation take order of magnitude of one minute, meaning that
for 20 parameters it would take two years to calibrate this toy model on a single CPU, 
with 30 parameters 2000 years.

The moral of the story is twofold: 1) that whatever algorithm we choose, it must greatly 
outperform random or grid search, 2) this algorithm must be executed in parallel to some degree. 
Ironically, random and grid search are the only truly-embarrassingly parallel algorithm, but even on 
large supercomputers with hundreds of thousands of CPUs the volume of the search space 
is just too large to use them.

The class of iterative algorithms which I will consider, will use an educated random search at each step. 
Hence within each step one can perform massive parallel computation with very little 
communication among processes. But nothing can be done to do parallel computations between one step and the following, 
which accounts for the sequential part of our algorithm. Therefore we trade concurrency for 
efficiency, and it is conceivable that there exist a sweet spot. To find it, a numerical experiment
can be designed in which several calibrations using a different strategy take place at the same time.

Therefore if the curse of dimensionality explains why High-Performance Computing resources are needed, 
the interesting part is *how* these are employed. The problem has two HPC relevant aspects:

1. How to distribute the work in a single calibration
2. How to schedule multiple calibrations
 
The scheduling must be asynchronous and guarants some form of resiliency if something fails.

This answer the question about the relevance of HPC techninques to the solution of the particular problem 
of environmental models calibration. It must be noted however that the calibration of physical or 
machine learning models is a huge field, and it's today probably one of the major player using HPC infrastructures. 
The simple reason is that it's an effective way of taking advantage of supercomputer resources for tackling 
a real world research problem without rewriting old, sequential code, sometimes known to work, virtually, without bugs.

This is not a minor problem. There are many models, in climatology or pharmacological research for example, 
on which centuries of men hours of work have been spent: doing brain surgery on this code is not feaseble, 
as it may even be that nobody really knows what it is doing. 

Moral of the story: know how to deal with calibrations on a supercomputer is a marketable HPC skill.

