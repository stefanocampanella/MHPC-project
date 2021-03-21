# Conclusions

In this thesis a modern HPC approach has been applied to calibrate the GEOtop hydrological model {cite}`rigon2006geotop,endrizzi2014geotop`, a complex, over parameterized hydrological model, with the aim of predicting the time evolution of variables as soil water content and evapotranspiration for several mountain agricultural sites in South Tyrol.

After developing a Python wrapper for the GEOtop code, I applied the derivative-free optimization algorithms implemented in the Facebook Nevergrad Python library {cite}`nevergrad` on a HPC cluster, thanks to the Dask framework {cite}`dask`.

Particular care has been put in the implementation in order to properly treat model failures, as the model does not produce a valid solution for all combinations of parameters.

The use of HPC solutions allowed calibrating GEOtop using HPC within a reasonable time and with acceptable results, notwithstanding the large parameters space. The code developed, which is published and freely available on GitHub, also shows how libraries and tools used within the machine learning community could be useful and address Earth-system and environmental models calibration. Finally, a simple performance model for the computation has been discussed.

Some examples of further research topics are:

* empirical studies on the choice of optimization algorithms and hyperparameters,
* determination of the optimal population size,  
* use of local optimization algorithms for refinement of the solutions, and
* interpretation and validation of the solutions from a physical point of view.
