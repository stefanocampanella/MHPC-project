# The Needle in the Haystack: GEOtop Calibration

An environmental model like GEOtop generally possess many different parameters.
Their large number is the result of the assembling of many different submodels, 
of statistical, physical (i.e. from first principles) and phenomenological 
nature. Not all of these parameters can be measured with an instrument on the field or inferred in some other 
way than calibration. This is especially true for the ones found in phenomenological relations, think 
for example to the Van Genuchten equation for soil retention. Furthermore, 
even when there is a straightforward experimental procedure to determine them, 
their value is affected by uncertainities, which could be large.

One could think that there exist some default values which describe the average 
system and that, with due exceptions, these values would produce meaningful 
results once fed into the model. In short, that these parameters are just 
subjected to fine-tuning. However he would fool himself. Indeed these models, GEOtop making 
no exception, are very sensistive to their parameters: their outputs can change wildly and
without carefully chosen paremeters the results are completely meaningless. 

Hence their predictive power is strictly related to their calibration. But what it means 
to calibrate the model? In the intuitive idea of "finding the values of the inputs 
that better reproduce the outputs" there is a certain degree of hand waiving. From a practical 
point of view, the questions one face himself with are like the following:

1. How do I compare the time series produced by the model with the experimental data?
2. How do I choose how many and which input parameters I need to calibrate?
3. Which optimization algorithm and hyperparameters should I choose?
4. How much computational resources do I need?
5. How long should I wait for the results?
6. Are they meaningful?
7. And finally, is there a way to get the same or better ones with less resources, i.e. 
waiting less or using less computational power?

This task, namely the calibration of a model, is more an art than a science, and if it 
can't be a science, then it would be nice to turn it into magic at least. Indeed, this is 
precisely the purpose of this work: trying to understand and automate the calibration 
process or some parts of it.

Before diving in, let's consider the challenges that calibration comports. The 
multitude of parameters translates into dimensionality curse, i.e. the 
exponential growth of the volume of the parameters space with respect to
the number of parameters. This is not an obstacle per se; just think of neural 
networks. However neural networks have two strange, wonderful properties. On the 
one hand they are easily differentiable with respect to their parameters, on the 
other wherever you start from, there is always a good set of parameters nearby.

```{note}
As noted in a [recent article](https://news.ycombinator.com/item?id=24835336) 
posted on Hacker News on intuition around neural networks, it is really 
unlikely that local optima exists in such highly dimensional spaces. In the 
gargantuan dimensionality of models like GTP3, the concept of direction 
(and distance) assumes a statistical meaning: there will always be 
a direction along which you could move to smaller values of the cost function.
```

The first point is not a real impediment if we neglect the categorical parameters 
on which GEOtop might depend on. Indeed, we could always use some numerical 
differentiation scheme (supposing that there are no threats of numerical 
instability). However the second is much more peculiar, indeed the situation 
for GEOtop is very different[^hyperopt].

[^hyperopt]: But there is a connection with some tasks in Machine Learning that will come up later. 

If one could put himself in the parameters space of GEOtop, and look at the 
cost function he would see hills and canyons, craters where the model crashes, 
swamps where it doesn't converge, mirages of oasis with unphysical parameters, 
and deadly desert plateaus where one moves from meaningless outputs 
to equally meaningless outputs. 

In this lumpy and bumpy landscape, moving towards the direction of steepest 
descent would lead, in the best scenario, to a useless local optima... 
unless one is endowed with an extremely good prior! Unfortunately, we are not.

Hence if we want to find the holy grail of global optima (if it exists) we need 
to roam and wonder, jumping here and there, with increasing confidence on 
our next guess as we grasp some kind of (statistical) knowledge of the shape 
of the loss function.

```{note}
However, at the end of a good calibration we might have a good prior. In 
this case it would make sense to perform a local optimization search. In 
principle this would boost the performance of the calibration strategy.
Unfortunately there was no time to develop on this idea.
```

However, this process is very much time consuming: for the kind of 
simulations with which we are involved, each sampling takes about one minute. 
These leads to the next chapter.


