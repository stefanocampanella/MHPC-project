# GEOtop calibration

```{epigraph}
When a program grows in power by an evolution of partially‑understood patches and fixes, the programmer begins to lose track of internal details and can no longer predict what will happen—and begins to hope instead of know, watching the program as though it were an individual of unpredictable behavior.

--Marvin Minsky, _Why programming is a good medium for expressing poorly understood and sloppily formulated ideas_
```

## Brief Introduction to GEOtop

What the model do, why simulation time is random, inputs and outputs

## Model Calibration

As previously discussed, GEOtop has many parameters. Their large number is the result of assembling many different submodels of statistical, physical (i.e. from first principles) and phenomenological nature. Not all of these parameters can be directly measured with an instrument or inferred in some other way than calibration. This fact is especially actual for the ones found in phenomenological relations, think for example to the Van Genuchten equation for soil retention. Furthermore, even when there is a straightforward experimental procedure to determine them, their value is affected by uncertainties, which could be large.

One could think that there exist some default values which describe the average system and that, with due exceptions, these values would produce meaningful results once fed into the model or, in short, that these parameters simply need fine-tuning. However, he would fool himself.

Indeed, GEOtop is very sensitive to the values of its parameters: the outputs of a simulation can change wildly, and without carefully chosen parameters, the results are entirely meaningless. Hence its predictive power is strictly related to a good calibration.

But what it means to calibrate the model? In the intuitive idea of "finding the values of the inputs whose outputs better reproduce the observations" there is a certain degree of hand waving. From a practical point of view, one faces himself with the following questions:

1. How do I compare the time series produced by the model with the experimental data?
2. How do I choose how many and which input parameters I need to calibrate?
3. Which optimization algorithm and hyperparameters should I choose?
4. How much computational resources do I need?
5. How long should I wait for the results?
6. Are they meaningful?
7. And finally, is there a way to get the same or better ones with fewer resources, i.e. waiting less or using less
 computational power?

This task, namely the calibration of a model, is more an art than a science. But if it can't be a science, then it would be nice at least to have some hints and heuristics. Indeed, this is precisely the purpose of this work: trying to understand and automate the calibration process or some parts of it. Before diving in, let's consider the challenges that calibration entail.

The multitude of parameters translates into dimensionality curse, i.e. the exponential growth of the volume of the search space with respect to the number of parameters. However, the dimensionality curse is not an obstacle per se; think of neural networks. Yet, neural networks have two peculiar properties. On the one hand, they are easily differentiable with respect to their parameters; on the other wherever you start from, there is always a good set of parameters nearby.

```{note}
As noted in a [recent article](https://news.ycombinator.com/item?id=24835336) posted on Hacker News on our intuition around neural networks, it is implausible that local optima exist in such high dimensional spaces. Endowed with the gargantuan dimensionality of models like GTP3, the concept of direction (and distance) assumes a statistical meaning: just by chance, there will always be a direction along which you could move to smaller values of the cost function.
```

The first point is not a real impediment if we neglect the categorical parameters on which GEOtop might depend. Indeed, we could always use some numerical differentiation scheme (supposing that there are no threats of numerical instability). However, the second is much more peculiar. Indeed the situation for GEOtop is very different[^hyperopt].

[^hyperopt]: But there is a connection with some tasks in Machine Learning that will come up later.

If one could put himself in the parameters space of GEOtop, and look at the cost function, he would see hills and canyons, craters where the model crashes, swamps where it doesn't converge, mirages of oasis with unphysical parameters, and deadly desert plateaus where one moves from meaningless outputs to equally meaningless outputs. 

In this lumpy and bumpy landscape, moving towards the direction of steepest descent would lead, in the best scenario, to a useless local optimum.

```{note}
However, at the end of a good calibration, we might have a good prior. In this case, it would make sense to perform a local optimization search. In principle, this would boost the performance of the calibration strategy. Unfortunately, there was no time to develop this idea.
```

Hence if we want to find the holy grail of global optimum (or a local minimum with decent performance), we need to roam and wander, jumping here and there, with increasing confidence on our next guess as we grasp some (statistical) knowledge of the shape of the loss function.

However, this process is very much time consuming: for the kind of simulations with which we are involved, each sampling takes about one minute, which leads to the next chapter.


