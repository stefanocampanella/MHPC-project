# Summary and Outline

This thesis addresses my final project for the 2019/20 edition of the Master in High-Performance Computing at SISSA and ICTP. In this preliminary material, I will briefly present its content and context.

Earth-system and environmental models calibration is a complex, computationally intensive task. At present, there is no general theory of model calibration, but instead a large collection of methods, algorithms and case studies. As a result, calibration is often more an art than a science: one must make several discretionary choices, guided more by his own experience and intuition than by the scientific method. 

One of the challenges is the large number of parameters involved. For this reason, preliminary sensitivity analysis may be used to reduce this number and select the relevant parameters. Still, the computational load of sensitivity analysis and calibration is high.

In this work I used High-Performance Computing solutions to calibrate GEOtop {cite}`rigon2006geotop,endrizzi2014geotop`, a complex, over parameterized hydrological model. I used the derivative-free optimization algorithms implemented in the Facebook Nevergrad Python library {cite}`nevergrad`, and run them on the Ulysses v2 HPC cluster, thanks to the Dask framework {cite}`dask`.

GEOtop has been used to simulate the time evolution of variables as soil water content and evapotranspiration of mountain agricultural sites in South Tyrol with different elevations, land cover (pasture, meadow, orchard), and soil types. In these simulations GEOtop solved the energy and water budget equations on a one-dimensional domain, i.e. on a thin column of soil and neglecting the lateral fluxes. Even in the simplified case of homogeneous soil, one has tens of parameters. These parameters control the soil and vegetation properties, but only a few of them are experimentally available, hence the need for calibration.

The computational aspects of GEOtop calibration have been examined, and the important issue of robustness against model convergence failures has been addressed. Finally, the scaling of calibration time has been measured up to 1024 cores.

The outline of the thesis is the following:

1. **Introduction and motivations.** Where I introduce relevant information about the GEOtop model. I also discuss the problem of GEOtop calibration, and the need for High-Performance Computing.
2. **Problem, methodology and implementation.** Where I state the problem in mathematical terms, but without mathematical rigour. Afterwards, I discuss the tools and implementation details of calibration.
3. **Results and conclusions.** Finally, I present the results and scaling of calibration, focusing on the HPC content.

```{bibliography}
:filter: docname in docnames
```
