# Derivative-free Optimization using Evolutionary Algorithms 

```{epigraph}
My children, the only true technology is nature. All the other forms of manmade technology are perversions.

--Ralph Bakshi, Wizards
```

In this chapter, I would like to pinpoint in mathematical terms the ideas behind the numerical experiments with which this thesis is concerned. The following is far from a rigorous treatment, may seem pretentious or naive, and probably it is. Nonetheless, I think it's helpful to have a mental model of the computations that are going to be performed.

As more thoroughly explained in the previous chapters, we are concerned with the calibration of the GEOtop hydrological model. Calibration means to find the values of the input parameters that one has to set to obtain the best possible overlapping between the outputs of a simulation and the experimental data.

"Overlapping" is not a precise term, but for the moment let's suppose that we have a pure function, the cost function, which takes the value of the parameters as arguments, runs a simulation, and returns a real number representing the discrepancy with observations: higher values mean worst overlap, and 0 means perfection. We will consider only continuous parameters, and suppose that you can get arbitrarily small differences by evaluating the cost function with " close enough" arguments, which we can image as points of the parameter/search space.

Therefore, we can model our cost function as lower bounded, continuous function $f: D \subseteq \mathbb{R}^n \mapsto [0, +\infty)$, where the search space $D$ is compact such that we know that there exist one or more global minima. We should consider an extension of $[0, +\infty)$ that includes failing computations, when the model crashes or fails to converge, something like bottom in Haskell. Let's forget about it though, and consider this information encoded in the domain $D$, within which our computation acts like a real mathematical function.

A black box optimizer is an iterator that at each step returns the approximate location of the minimum (referred to as recommendation or candidate), with increasing precision as the iterations go by. In this innocent statement lingers the assumption that it exists only one global minimum, assumption which for the moment we will ignore. In particular, we will consider only randomized algorithms which return a different sequence of points at each execution.

Therefore, we can define an optimizer as a random process $X_i: \Omega \mapsto D$ that gives better and better recommendations, that is $\forall \omega \in \Omega. \: f\left(X_i(\omega)\right) \leq f\left(X_{i-1}(\omega)\right)$.

The first optimizer we consider is random search, in which we sample the search space uniformly at each step and recommend the best result to that point. Let $U_i: \Omega \mapsto D$ a sequence of iid random variables uniformly distributed on $D$ (that is compact, hence has finite Lebesgue measure), then we can define the random search $X_i$ as follows

$$ \forall \omega \in \Omega. \: X_0(\omega) = U_0(\omega), \, X_i(\omega) = \begin{cases} U_i & \text{if } f(U_i(\omega)) \leq f(X_{i-1}(\omega)) \\ X_{i-1}(\omega) & \text{otherwise} \end{cases}.$$

In this way, the sequence of losses $Y_i = f(X_i)$ (which are random variables themselves) is point-wise monotonically decreasing, so it converges point-wise to a random variable $Y = \lim\limits_{i \rightarrow \infty} Y_i$.

```{admonition} To Do
It should be possible, leveraging the uniform distribution of the $X_i$ and the continuity of $f$, to prove that $Y = \min\limits_{x \in D} f(x)$ almost everywhere.
```

The random search doesn't perform poorly at all in the long run, and, if we could wait forever and sample infinite points of the search space, it would be a good option. Therefore, when we ask another optimizer $X'_i$ to "outperform random search" what we mean is that, on average, we want smaller losses $Y'_i$ after a finite number of steps: $\mathbf{E}[Y'_i] \leq \mathbf{E}[Y_i]$.

To this purpose, other optimizers use a more refined strategy. At each step, they sample from random variables $U'_i$ whose distribution is inferred from previous steps, and which usually converge to some a posteriori $U'$. In this way, these algorithms super-sample the region of the search space where, based on their assumptions, it is more probable to find a global minimum and accelerate the convergence of the best candidate $X'_i$. It is crucial to note that while they focus on a particular minimum (global or local), they subsample the rest of the search space.

In other words, if a heuristic algorithm converges, usually it does rapidly to a minimum and then sits there, with minimal chances to discover different minima. Therefore, these algorithms typically have a parameter that can be tweaked to explore more the search space (e.g. the population size in evolutionary algorithms), but which slows convergence: exploration vs exploitation.

## Hyperparameter optimization

Now we have a slightly more precise idea of the calibration process. However, from a practical point of view, there are still many unanswered questions. In the following, we will focus on "how do I choose an optimizer and its settings?", and device how to find the best optimizer in town.

To define what "best optimizer" we need a partial order, that is a way of comparing two algorithms. There are at least two grounds on which we can make this comparison: the "what" and the "how". The first is the result of calibration, and the second the resources required (time, memory or CPUs). Let's consider the first.

If we want to rank the results of a calibration process, a point in the search space, the first option is to look at the corresponding loss. However, in this way, we could get completely different results with the exact same losses. More importantly, we would not be able to discriminate between an algorithm which samples from the neighbourhood of a global minimum and one that samples from the bottom of a local minimum, where the losses have the same magnitude by luck. This because the only information we have about the cost function is what the optimizer tells us.

To circumvent this issue, we can add an assumption on the shape of the cost function and change the ranking of the results of optimizers. The new hypothesis is that the cost function has a unique global minimum at $x_\text{min}$, that is $\forall x \in D. \: f(x) \geq f(x_\text{min})$ and if $f(x) = f(x_\text{min})$ then $x = x_\text{min}$. The previous translates to a strong assumption on the model: we are saying that it could reproduce the data with fidelity and that the basic equations that describe the model allow for only one value of the parameters, which is the one we then could directly measure with some experimental procedure. We will make this simplifying assumption, although questionable (indeed, it is probably false).

Now that we know that exists a unique ground truth, we can rank the result of calibration by the distance from it. Consider the set of all possible optimizers $\{X_\lambda\}$ where $\lambda$ is an index which encodes some possibly mixed continuous and categorical hyperparameters, including the iteration at which we stop the optimizer. The new ranking $F'$ is then the Euclidean distance (or any other distance on $\mathbb{R}^n$, for that matter) between the result and the location of the minimum $x_\text{min}$

$$ F'_\lambda = \lVert X_\lambda - x_\text{min}\rVert \, ,$$

which is again a random variable.

Then, the expected value $\mathbf{E}\left[ F'_\lambda \right]$ is an estimate of how far from the optimum we are, on average, after a calibration. However, a better metrics $F$ would be how far from the optimum we are with respect to a random search after the same number of steps $X_\text{rand}$, which is our baseline

$$F_\lambda = \frac{ \lVert X_\lambda - x_\text{min}\rVert}{\mathbf{E}
\left[ \lVert X_\text{rand} - x_\text{min}\rVert \right]} \, .$$

```{admonition} To Do
In the case that the domain $D$ is a hypercube of unit side length $[0, 1]^n$, the denominator in the previous expression is a function of the number of parameters $n$ only. Find a closed formula.
``` 

The nice thing is that now our ranking is wholly detached from the original cost function. Remember that there was a little bit of hand waving in the definition of the cost function. Indeed, the output of the model is a collection of time series that must be compared with another one, the experimental data. However, there isn't a single way of measuring the discrepancy between these two. We can choose to compare the time series for a single observable quantity, a target, or aggregate more than one target by linear combination or some other mean. We can use different functions to compare the single time series, each of which may depend on parameters such as the time scale at which make the comparison.

Provided that all these possible cost functions share the same unique global minimum, which is true by the assumption previously discussed, the ranking $F$ is immune to the particular choice and tell us which optimizer makes the better guess of $x_\text{min}$. We can therefore include the cost function among the other hyperparameters of the optimizers $\lambda$ (however there is also an implicit dependency).

That's all very good, but there is a teeny-weeny problem: we don't know where $x_\text{min}$ is. Before going "hands to the sky crying, why, oh why?" (as in a song of the glorious band Tool), let's consider the options. For example, we could go on the field and measure the parameters, or we could use the values from a previous calibration which we trust. Here there is a third option.

For the previous assumption, the experimental data is equal to the output of a simulation with the right values of the parameters. By reading backwards the last statement, we conclude that the output is equal to experimental data for all matter and purpose. That solves the problem because, if we choose a random value of the parameters and run the model, we have both the data and the location of the minimum $x_\text{min}$. Now that we have some synthetic data, we can rank an optimizer using $F$.

However, we can still do better. The choice of $x_\text{min}$ usually has a great impact on the optimal value of the hyperparameters. For example, it may increase or reduce the sensitivity of a cost function to some target. Also, notice that $F$ depends explicitly (other than implicitly) on $x_\text{min}$. As a matter of fact, we can write $F$ as $F_{\lambda, x}$.

To estimate the expected value of $F_{\lambda, x}$, it is necessary to run several calibrations and then average. But nothing prevents us from drawing $x$ from another random variable $X_\text{min}$. In this case, the expected value is

$$\begin{aligned}
g(\lambda) &= \frac{ \mathbf{E} \left[ \lVert X_\lambda - X_\text{min}\rVert \right]}{\mathbf{E} \left[ \lVert X_\text{rand} - X_\text{min}\rVert \right]} \\
&= \sum\limits_\phi \phi \left( \sum\limits_x \mathbf{P}(F_{\lambda, x} = \phi \vert X = x) \mathbf{P}(X = x) \right) \\
&\approx \frac{1}{N} \sum\limits_{k = 1}^N \phi_k \, ,
\end{aligned}$$

where $\phi_k$ are samples of $F$ obtained running a calibration $N$ times, each time with $x$ drawn from $X_\text{min}$. The hope is to average the effects of the choice of $x$ and get a result that generalizes better to calibrations on real data. However, if this averaging makes real sense depends on the particular model and optimizers. Finally, what should be the distribution of $X_\text{min}$? The answer to this question is related to the typical values of the parameters encountered in applications.

Now $g(\lambda)$ is bounded from below, although it could have many global minima. Furthermore, in the considered cases, $\lambda$ parametrizes a finite set of values of some categorical hyperparameters. Hence $g$ is a suitable cost function for a further optimization process!

However, this time it will be a multi-objective optimization. Indeed, we still need to talk about the "how" mentioned in the first lines of this section. For our purpose, we will pretend to live in a world where there are no queues on supercomputers, and where each user has unlimited access to the resources of the machine. In this wonderful world, the only finite resource is time (this, unfortunately, is unavoidable even in the wildest fantasies {cite}`pievani2020finitudine`, and hence _tempori parere_ {cite}`dionigi2020segui`). Therefore the second criteria for this multi-objective optimization will be $t(\lambda)$, the average execution time of $X_\lambda$.

Finally, we can answer precisely the question of what scaling means for the calibration of GEOtop or, better, why it makes no sense to talk about scaling for this kind of applications.

When reasoning about scaling one generally assumes that exist a functional relation between the number of Concurrent Processing Units (CPUs) and the execution time. However, in our case, the second is one of the criteria of a multi-objective optimization problem. Each point of the Pareto front of this optimization problem has its value of the number of CPUs, among the other hyperparameters.

Therefore, in principle, we can select the point of the Pareto front corresponding to a particular execution time and return the number of CPUs, hence having a function. But, in general, it is not invertible: there might well be multiple optimal execution times given the same number of CPUs!

```{bibliography}
:filter: docname in docnames
```
