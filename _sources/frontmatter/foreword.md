# Foreword

In this brief thesis, I will discuss my final project for the 2019/20 edition of the Master in High-Performance Computing held by SISSA and ICTP. 

The topic of this project is the exploitation of HPC for finding the best optimization strategy for the calibration of the GEOtop hydrological model and finally performing a calibration on a case study of hydrological relevance. It must be noted that the experimental procedure developed in this project could be applied in principle to any statistical or physical model, even outside environmental sciences. However, the focus of this project will be on GEOtop, in accord with statement of the fellowship sponsoring this work: "development of a High-Performance hydological model".

Being in its essence a report of experimental research, although of the kind of experiments which are done on a computer, its structure will resemble the customary one for such documents:

1. **Introduction.** Here I give some key concepts to make the reader without a background on the subject acquainted with the topics of hydrology, hydrological modeling, and the GEOtop model.
2. **Motivations.** In this part, I discuss the problem of calibrating an environmental model, and more specifically GEOtop. I also  present the analogies with hyperparameter optimization in Machine Learning and the need for High-Performance Computing. I will try to answer both questions "why is HPC needed for this research?" And "how is this research relevant for HPC?"
3. **Problem.** In this part, I give a formal statement of the problem, in mathematical terms but without mathematical rigor.
4. **Approach and procedure.** Where I discuss the implementation details and motivate them. Here I also try to explain how to reproduce my research and adapt it to your case study.
5. **Results and conclusions.** Where I present the results of the numerical experiments and discuss them, both from the hydrological and the HPC viewpoint. 

This simple premise must be followed by some further considerations. 

The first one is that the interest in this project is faceted. Indeed, It could be considered interesting both technically (or technologically) and scientificly. Within its scientific interest one could account for both its applied hydrological value and theoretical optimization one. This diversity is not a merit of this particular work or of its author, but its specific of enabling technologies, in this case High-Performance Computing resources, and their use in applied science. 

The second consideration regards the purpose of this document, as I would like it to be a documentation for the code with which is bundled. Indeed, in many research fields, articles, reviews and records of conferences account only for a part of the writing duty of the researchers, the other being computer programs, something for which they are not always given the right credit. However, if programming is really theory building (cite Naur), then we need to consider code as literature and write correct, clear, reusable and extensively documented code to make real scientific progress and not waste our collective efforts.

However, the issue is not just the consideration we have for programming as a research activity. If one wants to apply the scientific method to numerical experiments, he has to attain to the same standards used for the experiments done in laboratories. In other words, these must be reproducible. Therefore, the purpose of this document is to enable the reader to reproduce the results obtained and to extend them to his own case study. Also, although briefly, some general aspects of the choices made in the writing and deployment of the code will be discussed; such that this document could be useful also for similar research.

One last consideration is needed. Given the diversity of topics involved, the vastity of material, the time assigned to this project and its focus on HPC, and finally the background of the author, it was necessary to _use_ some tools (algorithms, concepts, etc.) without fully mastering them. This unavoidable fact is reflected in the frugality of the bibliography and in their presentation, which occasionally could be sloppy or contain plain errors. It goes without saying that the responsability for those is mine and mine only. However, my hope is that the material presented here, if not the subject for deeper and broader research by the author, will be at least a prompt for more expert readers.

A few more words on this last point. The growth of complexity in science, to which specialism was the universal response, is not going to decline; but maybe the compartmentalization of specialism will. When we will seek for systematic answers to the problems posed by this Cambrian explosion, one place to look will be Computer Science, which under many regards is the art of managing complexity by the human mind through abstractions. The simplest and most ubiquitous abstraction is the black box, and hence there is no shame in using black boxes when dealing with problems outside of our competence. However, in order to make scientific statements on them, neglecting the implementation details, one needs the strictest rigor on the assumptions, that is on their inputs and outputs.

This was the spirit of the thesis I would have liked to write, I fear unfortunately without success.

In my opinion, this is also the reason why there is little chance to see the rise of scientific programmers, but I am sure that good scientists will be also good programmers, i.e. will be able to express elegantly their thougths both in declarative form by means of equations and in procedural form, with the help of a computer.
