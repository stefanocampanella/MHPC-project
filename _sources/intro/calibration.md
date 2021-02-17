# GEOtop calibration

```{epigraph}
When a program grows in power by an evolution of partially‑understood patches and fixes, the programmer begins to lose track of internal details and can no longer predict what will happen—and begins to hope instead of know, watching the program as though it were an individual of unpredictable behavior.

--Marvin Minsky, _Why programming is a good medium for expressing poorly understood and sloppily formulated ideas_
```

## Brief Introduction to GEOtop

GEOtop is a model of the mass and energy balance of the hydrological cycle aimed for simulations of small catchments. It is a distributed model and can simulate the evolution of snow cover, soil temperature and moisture. GEOtop takes into account vegetation processes, such as evapotranspiration, to correctly describe the water and energy exchange with atmosphere. 

A GEOtop simulation requires some input data, parameters and settings. The meteorological data strictly necessary to run the model consist of: air temperature, relative humidity (air water content, air vapor pressure, or dew point), wind speed, shortwave radiation, pressure, and precipitation. The meteorological time series must come from at least one station with a resolution of at least one hour. 

Parameters can be divided into surface parameters, which values are single numbers of each point of the catchment, and soil parameters, that may vary with depth. The first ones are related to energy fluxes, as the albedo, and vegetation properties, as vegetation height and leaf area index, which may vary with time. The seconds can be either thermodynamical properties of the soil, as its thermal conductivity and capacity, or hydraulic properties. The latter are crucial for determination of the soil moisture content, and some of them appear in phenomenological relations which are highly non-linear, as the Van Genuchten equation. Small changes in these parameters correspond to very different behaviours of soil retention. Putting all together, there are around thirty parameters that describe a single point of the simulated catchment. However, soil parameters are arrays since different layers of soil can have different properties. This means that the total number of values that can be used to characterize a point of a basin, including default values, can exceed one hundred.

TODO input files

The core of a simulation is the solution of the system of coupled partial differential equations that describes the flow and diffusion of water, and thermodynamical properties of soil. GEOtop solves a finite difference approximation of this system of equations. It uses a fixed time-step length and a three-dimensional grid, whose upper bound is given by a digital elevation model of the catchment, and the lower one is at a specified varying depth.

The two main equations are the water and energy balance equations with appropriate source and sink terms. The water balance equation also includes a diffusive term, as the soil is a porous medium. At each time-step, GEOtop uses an iterative method to solve these discretized equations. The number of iterations is determined by the residual, which must be under a user-defined threshold. Since the number of iteration is not fixed, the number of CPU cycles required to simulate the same time interval can vary and even diverge. GEOtop has several settings to limit the number of iterations of its internal routines. Nonetheless, it may be necessary to use an external timeout when dealing with batch executions of GEOtop.

TODO outputs

## Model Calibration

As discussed in the previous section, GEOtop has many free parameters. Their large number is the result of assembling many different submodels of various nature. Not all of them can be directly measured with an instrument or inferred in some other way than calibration. This fact is especially actual for the ones found in phenomenological relations, think for example to the Van Genuchten equation for soil retention. Furthermore, even when there is a straightforward experimental procedure to determine them, their value is affected by uncertainties, which could be large.

One could think that default values of the parameters exist, which describe the average system, and that any further adjustment of the parameters describes small deviations from it. Unfortunately, this is not the case, and parameters do not simply need fine-tuning.

Indeed, the outputs of a simulation can change wildly, and without carefully chosen values of the parameters, the results are entirely meaningless. Hence, the predictive power of GEOtop is strictly related to good calibration.

What it means to calibrate the model? The intuitive idea of "finding the values of the inputs with best outputs" contains a certain degree of hand waving. Practically, one should answer the following questions:

1. How do I compare the time series produced by the model with the experimental data?
2. How do I choose how many and which input parameters I need to calibrate?
3. Which optimization algorithm and hyperparameters should I choose?
4. How much computational resources do I need?
5. How long should I wait for the results?
6. Are they meaningful?
7. And finally, is there a way to get the same or better results with fewer resources, i.e. waiting less or using less
 computational power?

The task of model calibration is more an art than a science. Still, it would be useful to have hints and heuristics. The analyses in this work answer only a few of the previous questions. However, the developed code enable making further experiments and empirical studies on the subject. Let's consider the challenges that calibration entail.

The multitude of parameters translates into dimensionality curse, that is the exponential growth of the volume of the search space with respect to the number of parameters. However, the dimensionality curse is not an obstacle per se, take the example of neural networks. Yet, neural networks have two peculiar properties. On the one hand, the derivatives of the objective function with respect to the model parameters can be easily calculated. On the other, it turns out that wherever you start from in the search space, there is always a good set of parameters nearby.

```{note}
As noted in a [recent article](https://news.ycombinator.com/item?id=24835336) posted on Hacker News on our intuition around neural networks, it is implausible that local optima exist in such high dimensional spaces. Endowed with the gargantuan dimensionality of models like GTP3, the concept of direction (and distance) assumes a statistical meaning: just by chance, there will always be a direction along which you could move to smaller values of the cost function.
```

Leaving out categorical parameters, in the case of GEOtop, the first point is not a real impediment. In principle, we could use a numerical differentiation scheme (supposing that there are no threats of numerical instability and that the objective function is smooth enough). However, the second point has no similar in GEOtop.

If one could put himself in the parameters space of GEOtop, and look at the cost function, he would see hills and canyons, craters where the model crashes, swamps where it doesn't converge, mirages of oasis with unphysical parameters, and deadly desert plateaus where one moves from meaningless outputs to equally meaningless outputs. 

In this lumpy and bumpy landscape, moving towards the direction of the steepest descent would lead, in the best scenario, to a useless local optimum.

```{note}
However, at the end of a good calibration, we might have a good prior. In this case, it would make sense to perform a local optimization search. In principle, this would boost the performance of the calibration strategy. Unfortunately, there was no time to develop this idea.
```

Hence, if we want to find the holy grail of global optimum, we need to roam and wander, jumping here and there, with increasing confidence on our next guess as we grasp some (statistical) knowledge of the shape of the objective function. However, this process is very time-consuming: for the kind of simulations with which we are involved, each sampling takes about one minute, hence serial computations are not feasible.

The results of calibration strongly suggest that a global optimum does not exist. Instead, the objective has a plethora of equivalent local minima. This is an interesting feature of the model, and a strong indication that it is over-parametrized. Indeed, this open the possibility for further analysis of the data collected during calibration.

