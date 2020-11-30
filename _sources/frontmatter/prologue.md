# Prologue

```{epigraph}
It just happened to be an unusual experience. By training I was a scientist: by vocation I was a writer.

-- C. P. Snow, _The Two Cultures_
```

In this short thesis, I will discuss my final project for the 2019/20 edition of the Master in High-Performance Computing held by SISSA and ICTP. In this preliminary material, I will discuss the structure, purpose and approach used in this work.

## Outline of the Thesis

The topic of this project is the exploitation of HPC to find the best optimization strategy for the calibration of the GEOtop model, and finally performing a calibration on a case study of hydrological interest. It must be noted that the experimental procedure developed in this project, in principle, could be applied to any statistical or physical model, even outside environmental sciences. However, its focus will be on GEOtop, following the statement of the fellowship sponsoring this work "development of a High-Performance hydrological model".

Being in its essence a report of experimental research, although involved with the kind of experiments which are done on a computer, its structure will resemble the customary one for such documents:

1. **Introduction.** Where I give some key concepts to make the reader without a background on the subject acquainted with the topics of hydrology, hydrological modelling, and the GEOtop model.
2. **Motivations.** Where I discuss the problem of calibrating an environmental model, and more specifically GEOtop. I also present the analogies with hyperparameter optimization in Machine Learning and the need for High-Performance Computing. I will try to answer both questions "why is HPC needed for this research?" And "how is it relevant for HPC?"
3. **Problem.** Where I give a formal statement of the problem, in mathematical terms but without mathematical rigour.
4. **Approach and procedure.** Where I discuss the implementation details of the numerical experiments and motivate them. I also try to explain how to reproduce my research and how to adapt it to your case study.
5. **Results and conclusions.** Finally, I present the results of the numerical experiments and discuss them, both from the hydrological and the HPC viewpoint. 

## Nature of this Work

Some further considerations must follow this simple outline. 

The first one is that the interest in this project is faceted. Indeed, It could be considered both technologically and scientifically relevant. Among the reasons for its scientific interest, one could account for both the hydrological and optimization ones. This diversity is not a merit of this particular work or its author, but it's specific of enabling technologies (in this case, High-Performance Computing) and their use in applied science. 

The second consideration regards the purpose of this document, as I would like it to be documentation for the code with which is bundled. Let me explain why.

In many research fields, articles, reviews, and conference proceedings account only for a part of the writing duty of researchers, the other being computer programs. Nonetheless, this is something for which they are not always given the proper credit. Furthermore, code is not always published, and its quality is not always at best. However, if programming is theory-building {cite}`naur1985programming`, then we need to consider code as literature and write correct, clear, reusable and extensively documented code to make real scientific progress and not waste our collective efforts.

The issue is not just the consideration we have for programming as a research activity. If one wants to apply the scientific method to numerical experiments, he has to attain the same standards used for the experiments done in laboratories. In other words, these must be reproducible. Therefore, the purpose of this document is to enable the reader to reproduce the results obtained and to extend them to his case study. Also, although briefly, some general aspects of the choices made in the writing and deployment of the code will be discussed; such that this document could be a useful reference for similar research too.

One last consideration is needed. Given the diversity of topics involved, the extent of the material, the time assigned to this project and its focus on HPC, and finally the background of the author, it was necessary to _use_ some tools (algorithms, concepts, etc.) without fully mastering them. This unavoidable fact is reflected in the frugality of the bibliography and in the presentation of these tools, which occasionally could be sloppy or contain plain errors. The responsibility for those is mine and mine only. However, I hope that the material presented here, if not the subject for more in-depth and broader research by the author, will be at least a prompt for more expert readers.

```{bibliography} ../references.bib
```

## Apology of the Thoughtful Dabbler

The growth of complexity in science, to which specialism was the universal response, is not going to decline; but maybe the compartmentalization of specialism will. When we will seek for systematic answers to the problems posed by this Cambrian explosion, one place to look will be Computer Science, which under many regards is the art of managing complexity by the human mind through abstractions. The simplest and most ubiquitous abstraction is the black box, and hence there is no shame in using black boxes when dealing with problems outside of our competence. However, in order to make scientific statements about them, neglecting their inner workings, one needs the strictest rigour on the assumptions, that is on their inputs and outputs.

This was the spirit of the thesis I would have liked to write, I fear unfortunately without success.

```{margin}
Also a short philippic against the scientific programmers!
```
In my opinion, this is also the reason why there is little chance to see the rise of scientific programmers, although good scientists surely will also be good programmers, i.e. they will be able to express elegantly both declarative knowledge by means of equations and of procedural knowledge, with the help of a computer.

## Acknowledgements

OGS, Eurac and CINECA supported the research reported in this work under HPC-TRES program award number 2019-33