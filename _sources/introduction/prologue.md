# Prologue

```{epigraph}
It just happened to be an unusual experience. By training I was a scientist: by vocation I was a writer.

-- C. P. Snow, _The Two Cultures_
```

The subject of this thesis is my final project for the 2019/20 edition of the Master in High-Performance Computing held by SISSA and ICTP. In this preliminary material, I will briefly present the content, purpose and approach used in this work.

## Summary and Outline of the Thesis

Proper characterization of uncertainty remains a major research and operational challenge in Earth and Environmental Systems Models (EESMs). In fact, model calibration is often more an art than a science: one must make several discretionary choices, guided more by his own experience and intuition than by the scientific method. In practice, this means that the result of calibration (CA) could be suboptimal. One of the challenges of CA is the large number of parameters involved in EESM, which hence are usually selected with the help of a preliminary sensitivity analysis (SA). Moreover, the computational burden of EESMs models and the large volume of the search space make both SA and CA very time-consuming processes.

In this work I applied a modern HPC approach to calibrate a complex, over parameterized hydrological model. To this end, I used the derivative-free optimization algorithms implemented in the Facebook Nevergrad Python library (Rapin and Teytaud, 2018), and run them on an HPC cluster, thanks to the Dask framework (Dask Development Team, 2016).

The hydrological model considered is GEOtop (Rigon et al., 2006; Endrizzi et al., 2014), and has been used to predict the time evolution of variables as soil water content and evapotranspiration for several mountain agricultural sites in South Tyrol with different elevation, land cover (pasture, meadow, orchard), and soil types.

I performed simulations on one-dimensional domains, where the model solves the energy and water budget equations in a column of soil and neglects the lateral water fluxes. Even neglecting the distribution of parameters across layers of soil, thus considering a homogeneous column, one has tens of parameters, controlling soil and vegetation properties, where only a few of them are experimentally available.

Because the interpretation of global SA could be difficult or misleading, and the number of model evaluations needed by SA is comparable with CA, I employed the following strategy: I performed CA using all the continous parameters, and SA after CA, using the samples collected during CA, to interpret the results. However, given the above mentioned computational challenges, this strategy is possible only using HPC resources. For this reason, I focused on the computational aspects of calibration from an HPC perspective and examined the scaling of these algorithms and their implementation up to 1024 cores on a cluster. Other issues that I had to address were the complex shape of the search space and robustness of CA and SA against model convergence failure. 

The use of HPC resources and techniques allows to calibrate models with a high number of parameters within a reasonable computing time and  exploring the parameters space properly. This is particularly important with noisy, multimodal objective functions. In our case, it revealed itself essential to determine the parameters controlling the water retention curve, which is highly not linear. The developed framework, which is published and freely available on GitHub, also shows how libraries and tools used within the machine learning community coud be useful and easily adapted to EESMs CA.

The outline of the thesis is the following:

1. **Introduction and motivations.** Where I introduce the relevant pieces of information about the GEOtop model. I also discuss the problem of GEOtop calibration, and the need for High-Performance Computing.
2. **Problem, methodology and implementation.** Where I state the problem in mathematical terms, but without mathematical rigour. Afterwards, I discuss the tools and implementation details of calibration. I also try to explain how to reproduce my research and adapt it to other case study.
3. **Results and conclusions.** Finally, I present the results of calibration, focusing on the HPC content.

## Nature of this Work

This project is faceted, and placed at the intersection of hydrology, black-box optimization and HPC. For reasons of space (and time), I will concentrate on the last.

Futhermore, I believe that the purpose of this document should go beyond presenting results, and should also be documenting the code with which is bundled. Let me explain why.

In many research fields, articles, reviews, and conference proceedings account only for a part of the writing duty of researchers, the other being computer programs. Nonetheless, this is something for which they are not always given the proper credit. Furthermore, code is not always published, and its quality is not always at best. However, if programming is theory-building {cite}`naur1985programming`, then we need to consider code as literature and write correct, clear, reusable and extensively documented code to make real scientific progress and not waste our collective efforts.

The issue is not just the consideration we have for programming as an intellectual activity. If one wants to apply the scientific method to numerical experiments, he has to attain the same standards used for the experiments done in laboratories. In other words, these must be reproducible. Ideally, documentation should enable the reader to reproduce the results obtained and possibly to extend them to his case study. 


```{bibliography}
:filter: docname in docnames
```

## Apology of the Thoughtful Dabbler

Given the diversity of topics involved, the extent of the material, the time assigned to this project, its focus on HPC, and finally my background, I had to _use_ some tools (algorithms, concepts, etc.) without fully mastering them. This unavoidable fact is reflected in the frugality of the bibliography and the presentation, which occasionally could be sloppy or contain plain errors. The responsibility for those is mine and mine only. However, I hope that the material presented here, if not the subject for more in-depth and broader research by the author, will be at least a prompt for more expert readers.

The growth of complexity in science, to which specialism was the universal response, is not going to decline; but maybe the compartmentalization of specialism will. When we will seek for systematic answers to the problems posed by this Cambrian explosion, one place to look will be Computer Science, which under many regards is the art of managing complexity by the human mind through abstractions. The simplest and most ubiquitous abstraction is the black box, and hence there is no shame in using black boxes when dealing with problems outside of our competence. However, in order to make scientific statements about them, neglecting their inner workings, one needs the strictest rigour on the assumptions on their inputs and outputs.
 
It is unlikely that scientists will be replaced by scientific programmers in the future. However, good scientists surely will also be good programmers, i.e. they will be able to express elegantly both declarative knowledge by means of equations and of procedural knowledge, with the help of a computer.

## Acknowledgements

I would like to thank Giacomo Bertoldi, for trusting me in the first place and make this work possible, Alberto Sartori for his help during the whole master, Ing. Piero Calucci for his help on Ulysses, Stefano Salon for his support, and Alessandro Vuan for his patience.

I would also like to thank Nuno Carvalhais for the conversations we had and all the good ideas he gave me (all the bad ones are mine).

Finally, the OGS, Eurac and CINECA supported the research reported in this work under HPC-TRES program award number 2019-33.