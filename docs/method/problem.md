# Derivative-free Optimization

```{epigraph}
My children, the only true technology is nature. All the other forms of manmade technology are perversions.

--Ralph Bakshi, Wizards
```

## Random Search

In this chapter, I would like to pinpoint in mathematical terms the ideas behind the numerical experiments with which this thesis is concerned. The following is far from a rigorous treatment, may seem pretentious or naive, and probably it is. Nonetheless, I think it's helpful to have a mental model of the computations that are going to be performed.

As more thoroughly explained in the previous chapters, we are concerned with the calibration of the GEOtop hydrological model. Calibration means to find the values of the input parameters that one has to set to obtain the best possible overlapping between the outputs of a simulation and the experimental data.

"Overlapping" is not a precise term, but for the moment let's suppose that we have a pure function, the cost function, which takes the value of the parameters as arguments, runs a simulation, and returns a real number representing the discrepancy with observations: higher values mean worst overlap, and 0 means perfection. We will consider only continuous parameters, and suppose that you can get arbitrarily small differences by evaluating the cost function with " close enough" arguments, which we can image as points of the parameter/search space.

Therefore, we can model our cost function as lower bounded, continuous function $f: D \subseteq \mathbb{R}^n \mapsto [0, +\infty)$, where the search space $D$ is compact such that we know that there exist one or more global minima. We should consider an extension of $[0, +\infty)$ that includes failing computations, when the model crashes or fails to converge, something like bottom in Haskell. Let's forget about it though, and consider this information encoded in the domain $D$, within which our computation acts like a real mathematical function.

A black box optimizer is an iterator that at each step returns the approximate location of the minimum (referred to as recommendation or candidate), with increasing precision as the iterations go by. In this innocent statement lingers the assumption that it exists only one global minimum, assumption which for the moment we will ignore. In particular, we will consider only randomized algorithms which return a different sequence of points at each execution.

Therefore, we can define an optimizer as a random process $X_i: \Omega \mapsto D$ that gives better and better recommendations, that is $\forall \omega \in \Omega. \: f\left(X_i(\omega)\right) \leq f\left(X_{i-1}(\omega)\right)$.

The first optimizer we consider is random search, in which we sample the search space uniformly at each step and recommend the best result to that point. Let $U_i: \Omega \mapsto D$ a sequence of iid random variables uniformly distributed on $D$ (that is compact, hence has finite Lebesgue measure), then we can define the random search $X_i$ as follows

$$ \forall \omega \in \Omega. \: X_0(\omega) = U_0(\omega), \, X_i(\omega) = \begin{cases} U_i & \text{if } f(U_i(\omega)) \leq f(X_{i-1}(\omega)) \\ X_{i-1}(\omega) & \text{otherwise} \end{cases}.$$

In this way, the sequence of losses $Y_i = f(X_i)$ (which are random variables themselves) is point-wise monotonically decreasing, so it converges point-wise to a random variable $Y = \lim\limits_{i \rightarrow \infty} Y_i$. It is easy to show that $Y = \min\limits_{x \in D} f(x)$ almost everywhere.

Random search doesn't perform poorly at all in the long run, and, if we could wait forever and sample infinite points of the search space, it would be a good option. Therefore, when we ask another optimizer $X'_i$ to "outperform random search" what we mean is that, on average, we want smaller losses $Y'_i$ after a finite number of steps: $\mathbf{E}[Y'_i] \leq \mathbf{E}[Y_i]$.

To this purpose, other optimizers use a more refined strategy. At each step, they sample from random variables $U'_i$ whose distribution is inferred from previous steps, and which usually converge to some a posteriori $U'$. In this way, these algorithms super-sample the region of the search space where, based on their assumptions, it is more probable to find a global minimum and accelerate the convergence of the best candidate $X'_i$. It is crucial to note that while they focus on a particular minimum (global or local), they subsample the rest of the search space.

In other words, if a heuristic algorithm converges, usually it does rapidly to a minimum and then sits there, with minimal chances to discover different minima. Therefore, these algorithms typically have a parameter that can be tweaked to explore more the search space (e.g. the population size in evolutionary algorithms), but which slows convergence: exploration vs exploitation.

## Evolutionary Algorithms

