# Tools

```{epigraph}

Talk is cheap, show me the code.

-- Linus Torvalds
```

## The Python Programming Language

Python is an open-source, cross-platform, scripting, high-level, duck-typed language (footnote: however type annotations are available in recent versions) with a terse syntax, which allows for the fast pace development. The reference implementation, CPython, can be easily integrated with pre-existing C and Fortran codebases; indeed, Python is sometimes referred to as a glue language. Moreover, it has a rich standard library and a full gamut of third-party libraries and tools. Python is the third language in the Tiobe index in 2020 and continues to grow steadily because of its popularity in machine learning and artificial intelligence. 

The usage of Python in scientific computing is nowadays a consolidated practice. Among its reasons, there is the existence of mature, fully-featured, and open-source libraries like Numpy, Matplotlib, and Pandas, respectively, for numerical computing, plotting, and manipulation of tabular data. Thanks to these libraries, in some contexts,  Python was able to overtake the proprietary programming language MATLAB and the open-source one R, which, being a programming language specifically though for statistics, has its quirks. 

Indeed, the characteristics listed above make Python a right candidate when choosing a programming language in which writing code powerful and extensible, yet to be used by scientists without formal training in computer science. In that sense, Python is a glue language in terms of the developers' level of expertise. However, when it comes to the typical workloads of numerical computing (CPU-bounded applications, the so-called number-crunching), Python shows the same shortcoming of MATLAB. Due to the dynamic nature of the language, repeated floating-point operations on contiguous memory or other kinds of tight loops, which are very fast on x86 architectures, take far longer than compiled languages. Although comparing programming languages is a bit like comparing apples and oranges, a quick look at the computer language benchmarks game tells us that is reasonable to expect that a pure Python implementation of some algorithm is between ten and one thousand times slower than one in C. So how come that Python is widely adopted in numerical computing? The answer is similar to the one for the case of MATLAB. In both cases, the dynamic programming language overcomes these shortcomings by wrapping and calling some more efficient code, usually written in Fortran, C or C++. It is possible to do so because number-crunching codes' profile often follows a Pareto distribution: 80% of the time is spent on 20% of the code. The whole situation is typically referred to as the two-language problem. There are many ancillary problems related to the two-language one and to solve them, a new programming language, Julia, has been developed. Julia will probably become the dominant language in scientific computing soon. However, the scientific computing community's inertia means that Python will remain the way to go for new projects if they depend on existing libraries that don't have a Julia equivalent. 

The discussion above covers briefly the topic of Python's usage in scientific computing, but is Python used in high-performance computing? And how? 


