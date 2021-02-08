# Tools

```{epigraph}
Code reuse is the Holy Grail of Software Engineering

-- Douglas Crockford
```

## The Python Programming Language

Python is an interpreted, duck-typed language (footnote: however optional type annotations are available from version 3.6) with a terse syntax, allowing for fast-paced development. Python programs can easily integrate code written in other languages, such as C (the language of the reference implementation CPython), and for this reason, it is said to be a glue language. Moreover, it has a rich standard library and a full gamut of third-party libraries and tools. In 2020 Python has been the third language in the TIOBE index and its popularity has grown steadily in the past years, especially in machine learning and data science.

The usage of Python in scientific computing is nowadays a consolidated practice. Among its reasons, there is the existence of mature, fully-featured, and open-source libraries like Numpy, Matplotlib, and Pandas, respectively, for numerical computing, plotting, and manipulation of tabular data. Thanks to these libraries, Python became a popular alternative to MATLAB and R. 

Indeed, Python is a right candidate when choosing a programming language in which writing general and extensible code, yet to be used by scientists without formal training in computer science. In that sense, Python can be viewed as a glue language also in terms of the developers' and users' level of expertise. However, when it comes to the typical workloads found in numerical computing (the so-called number-crunching), Python shows the same shortcoming of MATLAB. Due to the dynamic nature of the language, repeated floating-point operations on contiguous memory or other kinds of tight loops, which can be very fast on modern CPU architectures, in Python take far longer than in other compiled languages. Although comparing different programming languages' performance is often unmeaning, a quick look at the computer language benchmarks game (TODO: put a link here) tells us that is reasonable to expect a pure Python implementation of these CPU-bounded algorithms to be between ten and one thousand times slower than the same in C. So how come that Python is widely adopted in numerical computing? 

The answer is similar to the one for the case of MATLAB. In both cases, the dynamic programming language overcomes these shortcomings by wrapping and calling some more efficient code, usually written in Fortran, C or C++. It is possible to do so because the distribution of the workload in number-crunching codes is often peaked: most of the time is spent on a small fraction of the code. Hence it is possible to optimize the whole program by rewriting a few routines in another language.  In Python, optimized mathematical routines are available in the Numpy library, and it is often possible to obtain a sensible speedup by rewriting unoptimized code in terms of these functions acting on arrays and avoiding loops (a paradigm sometimes called array programming). In worst cases, a large part of the program needs to be rewritten, and Python serves just as a prototyping language. 

This problem is typically referred to as the two-language problem, and a new programming language named Julia has been recently developed to solve this problem. The author's opinion is that Julia will probably become the dominant language in scientific computing in the future. However, this will not happen too soon because of code dependencies and users inertia.

The reasons why the Python programming language has been chosen for the project reflect the general facts listed above:
the need for a simple language known by the scientists that will continue to work with the code in the future,
the capability of working with the operating system and external processes natively,
the availability of libraries for derivative-free optimization and distributed computing.

These points will be more thoroughly discussed in the following sections.

Finally, almost all of the calibration time is spent in the execution of the model and the overhead caused by a suboptimal optimizer (footnote: sorry for the wordplay), for example, due to the programming language used, is negligible. This statement, which has been discussed in the previous chapters, will be given a quantitative meaning in the next ones.

## The Jupyter Ecosystem

The Jupyter Notebook is an open-source, interactive web application that allows writing executable documents, called notebooks, containing rich text, code and visualizations. 

Jupyter Notebook is language-agnostic and can include code written in various languages, such as Python, R, Julia or C++. The code is executed on a language-specific kernel, which is an instance of an interpreter connected to Jupyter via ZeroMQ, an asynchronous messaging library. 

Notebooks are stored as text files and the Jupyter Notebook file format is defined via a JSON schema. For historical reasons, their extension is `ipynb` (the Python kernel is called IPython). Notebooks are divided into cells, which can be of different types. Code cells can be evaluated and the value yielded by the last statement of a cell is captured by Jupyter Notebook, which by default then renders it as HTML, together with the standard output and error collected during execution. Normally, the output of a cell is stored within the notebook. Also, the order of execution of the code cells of a notebook is arbitrary, but the execution count of a cell is stored within its metadata.

The previous one is an important point: Jupyter Notebook defines both a model of execution and a file format. 

The execution of a notebook is stateful: the same notebook can be executed twice by the same kernel and obtain different results. This is because the internal state of the kernel can change between executions. Indeed, for this reason, Jupyter Notebook users often need to restart the kernel and re-evaluate the code cells. This hidden state has been criticized and other implementations of reactive notebooks exist, the most notable is `Pluto.jl` for Julia. 

Since the file format is a JSON dictionary, binary data must use a binary-to-text encoding, which introduces an overhead. Furthermore, notebooks files badly integrate with version control systems (`Pluto.jl` also tries to solve this problem).

Since late 2018, the Jupyter Notebook has been integrated into JupyterLab, an extensible IDE-like interface combining the Jupyter Notebook with a terminal, a text editor and a file browser. However, this new interface is completely backwards compatible.

Jupyter Notebook and JupyterLab are today used by a vast community of scientific programmers, data scientists, and educators. Various projects integrate and extend JupyterLab, for example, to parametrize the execution of notebooks (Papermill), retrieve data from notebooks (Scrapbook) or produce complex, publication-quality documents (Jupyter Book).

## GEOtoPy

## Calibration and Sensitivity Analysis using Nevergrad and SALib

## Parallel Computing in Python

## High-Performance Computing in Python using Dask

## Deploying Python Software on HPC

