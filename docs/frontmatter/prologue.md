# Prologue

```{epigraph}
It just happened to be an unusual experience. By training I was a scientist: by vocation I was a writer.

-- C. P. Snow, _The Two Cultures_
```

The subject of this thesis is my final project for the 2019/20 edition of the Master in High-Performance Computing at SISSA and ICTP. In this preliminary material, I will briefly present the content of the thesis, its purpose and approach.

## Summary and Outline of the Thesis

Proper characterization of uncertainty remains a major research and operational challenge in Earth and environmental systems models. In fact, model calibration is often more an art than a science: one must make several discretionary choices, guided more by his own experience and intuition than by the scientific method. In practice, this means that the result of calibration could be suboptimal. 

One of the challenges of calibration of these models is the large number of parameters involved. For this reason, preliminary sensitivity analysis may be used to reduce this number and select the relevant parameters. Still, the computational load of sensitivity analysis and calibration is high.

In this work I used High-Performance Computing solutions to calibrate GEOtop {cite}`rigon2006geotop,endrizzi2014geotop`, a complex, over parameterized hydrological model. I used the derivative-free optimization algorithms implemented in the Facebook Nevergrad Python library {cite}`nevergrad`, and run them on the Ulysses v2 HPC cluster, thanks to the Dask framework {cite}`dask`.

GEOtop has been used to simulate the time evolution of variables as soil water content and evapotranspiration of mountain agricultural sites in South Tyrol with different elevations, land cover (pasture, meadow, orchard), and soil types. In these simulations GEOtop solved the energy and water budget equations on a one-dimensional domain, i.e. on a column of soil and neglecting the lateral fluxes. Even in the simplified case of a homogeneous column of soil, one has tens of parameters. These parameters control the soil and vegetation properties, but only a few of them are experimentally available, hence the need for calibration.

The computational aspects of GEOtop calibration have been examined, and the important issue of robustness against model convergence failures has been addressed. Finally, the scaling of calibration time has been measured up to 1024 cores for the case of covariance matrix adaptation evolution strategy.


The outline of the thesis is the following:

1. **Introduction and motivations.** Where I introduce relevant information about the GEOtop model. I also discuss the problem of GEOtop calibration, and the need for High-Performance Computing.
2. **Problem, methodology and implementation.** Where I state the problem in mathematical terms, but without mathematical rigour. Afterwards, I discuss the tools and implementation details of calibration.
3. **Results and conclusions.** Finally, I present the results of calibration, focusing on the HPC content.


## Nature of this Work

This project is faceted, and placed at the intersection of hydrology, black-box optimization and HPC. For reasons of space (and time), I will concentrate on the last.

Furthermore, I believe that the purpose of this document should go beyond presenting results: it should also document the code with which is bundled. 

In many research fields, articles, reviews, and conference proceedings account only for a part of the writing duty of researchers, the other being computer programs. Nonetheless, this is something for which they are not always given the proper credit. Furthermore, code is not always published, and its quality is not always at best. However, if programming is theory-building {cite}`naur1985programming`, then we need to consider code as literature and write correct, clear, reusable and extensively documented code to make real scientific progress and not waste our collective efforts.

The issue is not just the consideration we have for programming as an intellectual activity. If one wants to apply the scientific method to numerical experiments, he has to attain the same standards used for laboratory experiments: in other words, they must be reproducible. Hence, the reason of the importance of documentation in scientific computing is that it is part of the reproducibility effort.

## Apology of the Thoughtful Dabbler

Given the diversity of topics involved, the extent of the material, the time assigned to this project, its focus on HPC, and finally my background, I had to _use_ some tools (algorithms, concepts, etc.) without fully mastering them. This unavoidable fact is reflected in the frugality of the bibliography and in their presentation, which occasionally could be sloppy or contain plain errors. The responsibility for those is mine and mine only. However, I hope that the material presented here, if not the subject for more in-depth and broader research by the author, will be at least a prompt for more expert readers.

The growth of complexity in science, to which specialism was the universal response, is not going to decline; but maybe the compartmentalization of specialism will. When we will seek for systematic answers to the problems posed by this Cambrian explosion, one place to look will be Computer Science, which under many regards is the art of managing complexity by the human mind through abstractions. The simplest and most ubiquitous abstraction is the black box, and hence there is no shame in using black boxes when dealing with problems outside our competence. However, in order to make scientific statements about them, neglecting their inner workings, one needs the strictest rigour on the assumptions on their inputs and outputs.
 
It is unlikely that scientists will be replaced by scientific programmers in the future. However, good scientists surely will also be good programmers, i.e. they will be able to express elegantly both declarative knowledge by means of equations and of procedural knowledge, with the help of a computer.


```{bibliography}
:filter: docname in docnames
```
