# MHPC Final Project
## High-Performance Derivative Free Optimization for the Calibration of the GEOtop Model

This repository contains notebooks, code and documentation related to my final project for the 2019/20 edition of the MHPC. The thesis will be hosted here, as well. 

In my project I tried to get some insights into high-performance derivative-free optimization and exploit HPC for benchmarking various algorithms for the calibration of parameters of the [GEOtop model](https://geotopmodel.github.io/geotop). The topic is interesting both from a scientific and technical point of view; you can find more information [here](https://stefanocampanella.github.io/MHPC_project_meeting).

The code developed for the project consist of a GEOtop wrapper ([GEOtoPy](https://github.com/stefanocampanella/GEOtoPy)) and various notebooks and scripts, which leverage third party libraries such as [Nevergrad](https://facebookresearch.github.io/nevergrad) for optimization and [SALib](https://salib.github.io/SALib).

At present, the content of this repository is somewhat provisional and exploratory in nature. It contains preliminary analysis and experiments with the interface and the optimizer(s). At the end of the project, it will host an application to a case study and reports.  

Nonetheless, since the very beginning, a special effort has been made to provide the code and documentation to set-up an easily reproducible environment. Once you have `conda` on your system, you can install the environment with just `conda env create -f config/environment.yaml` from the root of this repository.

## License

Distributed under the GPL3 License. See LICENSE for more information.
