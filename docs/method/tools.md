# Tools

```{epigraph}
Code reuse is the Holy Grail of Software Engineering

-- Douglas Crockford
```

## The Python Programming Language

Python is an interpreted, duck-typed language (footnote: however optional type annotations are available from version 3.6) with a terse syntax, allowing for fast-paced development. Python programs can easily integrate code written in other languages, such as C (the language of the reference implementation CPython), and for this reason, it is said to be a glue language. Moreover, it has a rich standard library and a full gamut of third-party libraries and tools. In 2020 Python has been the third language in the TIOBE index and its popularity has grown steadily in the past years, especially in machine learning and data science.

The usage of Python in scientific computing is nowadays a consolidated practice. Among its reasons, there is the existence of mature, fully-featured, and open-source libraries like Numpy, Matplotlib, and Pandas, respectively, for numerical computing, plotting, and manipulation of tabular data. Thanks to these libraries, Python became a popular alternative to MATLAB and R. 

Indeed, Python is a right candidate when choosing a programming language in which writing general and extensible code, yet to be used by scientists without formal training in computer science. In that sense, Python can be viewed as a glue language also in terms of the developers' and users' levels of expertise. However, when it comes to the typical workloads found in numerical computing (the so-called number-crunching), Python shows the same shortcoming of MATLAB. Due to the dynamic nature of the language, repeated floating-point operations on contiguous memory or other kinds of tight loops, which can be very fast on modern CPU architectures, take far longer in Python than in other compiled languages. Although comparing different programming languages' performance is often unmeaning, a quick look at the computer language benchmarks game (TODO: put a link here) tells us that a pure Python implementation of these CPU-bounded algorithms should be expected to be between ten and one thousand times slower than the same in C. So how come that Python is widely adopted in numerical computing? 

The answer is similar to the one for the case of MATLAB. In both cases, the dynamic programming language overcomes these shortcomings by wrapping and calling some more efficient code, usually written in Fortran, C or C++. It is possible to do so because the distribution of the workload in number-crunching codes is often peaked: most of the time is spent on a small fraction of the code. Hence it is possible to optimize the whole program by rewriting a few routines in another language.  In Python, optimized mathematical routines are available in the Numpy library, and it is often possible to obtain a sensible speedup by rewriting unoptimized code in terms of these functions acting on arrays and avoiding loops (a paradigm sometimes called array programming). In worst cases, a large part of the program needs to be rewritten, and Python serves just as a prototyping language. 

This problem is typically referred to as the two-language problem, and a new programming language named Julia has been recently developed to solve this problem. There is a shared opinion that Julia will probably become the dominant language in scientific computing in the future. However, this will not happen too soon because of code and users inertia.

The reasons why the Python programming language has been chosen for the project reflect the general facts listed above:
the need for a simple language known by the scientists who will work and use the code in the future,
the capability of interfacing with the operating system and external processes natively,
the availability of libraries for derivative-free optimization and distributed computing.

I will discuss the points above more thoroughly in the following sections.

Finally, almost all of the calibration time is spent executing the model and the overhead caused by a suboptimal optimizer (footnote: sorry for the wordplay), for example, due to the programming language used, is negligible. This statement, which has been discussed in the previous chapters, will be given a quantitative meaning in the next ones.

## The Jupyter Ecosystem

The Jupyter Notebook is an open-source, interactive web application that allows writing executable documents, called notebooks, containing rich text, code and visualizations. 

Jupyter Notebook is language-agnostic and can include code written in various languages, such as Python, R, Julia or C++. The code is executed on a language-specific kernel, an instance of an interpreter connected to Jupyter via ZeroMQ, an asynchronous messaging library. 

Notebooks are stored as text files, and the Jupyter Notebook file format is defined via a JSON schema. For historical reasons, notebooks extension is `ipynb` (the Python kernel is called IPython). Notebooks are divided into cells, which can be of different types. Code cells can be evaluated and the value yielded by the last statement of a cell is captured by Jupyter Notebook, which by default then renders it as HTML, together with the standard output and error collected during execution. Usually, the output of a cell is stored within the notebook. Also, the order of execution of a notebook's code cells is arbitrary, but the execution count of a cell is stored within its metadata.

Since late 2018, the Jupyter Notebook has been integrated into JupyterLab, an extensible IDE-like interface combining the Jupyter Notebook with a terminal, a text editor and a file browser. However, this new interface is entirely backwards compatible.

It is crucial to notice that Jupyter Notebook and JupyterLab define both an execution model and a file format. 

A notebook's execution is stateful: the same notebook can be executed twice by the same kernel and obtain different results because the kernel's internal state can change between executions. Indeed, for this reason, users often need to restart the kernel and re-evaluate the code cells. The hidden state problem has been criticized, and other implementations of reactive notebooks exist (such as Pluto for Julia).

Since the file format is a JSON dictionary, binary data must use a binary-to-text encoding, which introduces an overhead (of both memory and CPU cycles). Furthermore, notebook files poorly integrate with version control systems (another problem solved by Pluto).

Notwithstanding these and other problems, Jupyter has become the de-facto standard for interactive computing and visualization, and nowadays it is used by a vast community of scientific programmers, data scientists, and educators.

More recently, some initiatives within the broader context of reproducible research started targetting specifically at Jupyter (TODO: cite ten rules). Various projects integrate and extend JupyterLab, for example, to validate notebooks, to parametrize their execution (Papermill), to retrieve data from them (Scrapbook), or produce complex, publication-quality documents (Jupyter Book).

### Papermill and Scrapbook

These two lightweight Python libraries belong to the Nteract organization and have orthogonal purposes: Papermill allows to parametrize and execute notebooks, while Scrapbook allows to record data produced during execution. 

Papermill can be used via the Python API or its command-line interface. In both cases, the user must provide the path to the input notebook, the path to the output notebook, and a dictionary of parameters. The paths can be on the local filesystem or remote ones; Papermill currently can handle HTTP, HTTPS and supports additional protocols for working with the major cloud storage providers. Also, it can read and write to the standard input and output, respectively. When using the CLI, the dictionary of parameters is specified using a YAML string, a YAML file path, or the value of single parameters. When using the API, Papermill can also use a Python dictionary.

Before executing the input notebook, Papermill looks for a cell with the `parameters` tag containing the default values. It adds a new cell just below (tagged with `injected-parameters`) overwriting the value of the variables contained in the parameters dictionary. Finally, it executes the notebook and saves a copy at the output path location. The output notebook also contains Papermill execution metadata, such as the injected parameters' value and each cell's execution time. As a notebook file is a JSON, one can easily retrieve these metadata afterwards. 

The same can be obtained in other ways, for example, using NBclient. However, Papermill is more featured and integrates more easily in a data analysis pipeline. For example, it is currently employed at Netflix to schedule notebooks (TODO: quote Netflix blog post).

A cell's output is usually rendered using HTML and embedded into the notebook file as a JSON string as sketched above. However, this is only a first approximation. The actual output is a JSON dictionary with a specific structure, and its content can have an arbitrary MIME type. Nonetheless, there is no easy way to serialize an object created during execution and then include it in the cell output using Jupyter Notebook only. However, the Scrapbook library does precisely that. 

The Scrapbook library introduces a few names, quoting from the documentation page of the project
scraps: serializable data values and visualizations such as strings, lists of objects, pandas dataframes, charts, images, or data references,
notebook: a wrapped nbformat notebook object with extra methods for interacting with scraps,
scrapbook: a collection of notebooks with an interface for asking questions of the collection,
encoders: a registered translator of data to/from notebook storage formats.
Notice that Scrapbook, which was initially part of Papermill, share with the previous the capability to work with remote file systems. Also, the Scrapbook library is easily extensible. Indeed, it is possible to register new encoders for serializing Python objects, possibly using high-performance formats, such as Apache Arrow.  

The combined usage of Papermill and Scrapbook allows batch processing of notebooks, persistent storage of the results, and retrieving them, for example, for ensemble analysis. Of course, one could obtain the same in other ways, such as using Python scripts and a database. However, this way, it is possible to use the same tools for prototype and production code.

### Jupyter Book

Jupyter Book is an open-source project which leverages the Sphinx documentation system to build publication-quality documents from Jupyter notebooks and Markdown sources. It can execute and cache Jupyter notebooks, and use its outputs (including interactive widgets). Furthermore, it supports a Markdown flavour called Markedly Structured Text, providing margin notes, blocks, panels, dropdowns, etc. This document is built using Jupyter Book.

## GEOtoPy

GEOtoPy is a small Python package without external dependencies developed for this project. It contains a single module exporting a single base class `GEOtoPy.GEOtop`, which must be derived to have a functioning GEOtop wrapper. 

GEOtop allows running different types of simulations using a flexible configuration file. The model's inputs and outputs can be very diverse, and the same is true for the workflow in which one runs model. If one wants one tool able to encompass all the different scenarios, he has two options. The first is writing a very complex wrapper introducing an abstraction layer capable of handling all particular cases.  The second is writing a barebone wrapper, lacking part of the implementation, and let the user adapting it to his use case. GEOtoPy chooses this second option. 

Indeed, the purpose of GEOtoPy was more about documenting and allowing code reuse than being a full-fledged wrapper.

The central assumption of GEOtoPy is that the user workflow consists of the following steps:

1. check minimal preconditions on the inputs,
2. preprocess the inputs,
3. run the model,
4. postprocess the outputs.

The `GEOtoPy.GEOtop` constructor takes care of the first step. The other three are encapsulated in the `run_in` method of the object.

Let me recall that the GEOtop executable takes one argument, which is the path to a directory containing a `geotop.inpts` file. The `GEOtoPy.GEOtop` class constructor takes only one positional argument: the path mentioned above, which can be a string or a PathLike object. It then checks that this path points to a readable directory and contains a readable `geotop.inpts` file. It also checks that a `geotop` executable exists. If all the preconditions above stand, it reads and parses the `geotop.inpts` file. Otherwise, it throws an error. 

The constructor does not ensure that the `geotop.inpts` file is a valid configuration file. Indeed, in the case of malformed `geotop.inpts`, it just warns the user. A valid line in the configuration file can be either a comment, identified by the regex `\s*!.*\n|\s+`, or a setting, identified by the Python regex ` \s*(?P<keyword>[A-Z]\w*)\s*=\s*(?P<value>.*)(?:\n|\Z)`. Values associated with given keywords can be read from and print to strings thanks to a JSON dictionary containing the type associated with each keyword.

Correctly parsed settings are stored in a Python dictionary within the object. The constructor can also keep the whole content of the inputs directory in memory, archived into tar, using `BytesIO`.

The `run_in` method executes the model within a working directory `working_dir` with additionally provided arguments. Its purpose is to execute in sequence the preprocessing, running and postprocessing steps. It has more or less the following implementation
```python
import subprocess

def run_in(self, working_dir, *args, **kwargs):
    self.preprocess(working_dir, *args, **kwargs)
    subprocess.run([self.exe, working_dir], **self.run_args)
    output = self.postprocess(working_dir)
    return output
```
It is worth noticing a few design choices.

First, the data flow via IO. The`postprocess` method has no arguments other than the working directory. The choice of the `postprocess` signature follows from the assumption that the derived class implements the wrapper for a specific type of simulation, with a particular shape of the inputs and outputs. However, the `preprocess` method can take additional arguments to change the values of (some of) the inputs and run different simulations.

Second, since we want to run the model multiple times in a concurrent fashion, it is fundamental that different runs do not interfere with one another. If `run_in` does not change the global state but change the internal one of the object to which it belongs, it is possible to run the method on multiple copies of the same object simultaneously without data races. If we want to avoid duplicates, the `run_in` method must be a pure function: it must not have side effects. However, strictly speaking, both scenarios are impossible since GEOtop works on files, and the running step is guaranteed to do IO. 

Nonetheless, we can avoid data races by requiring that `preprocess` and `postprocess` satisfy some conditions. Unfortunately, there is no way of expressing this behaviour in Python. Hence it is the responsibility of the user to implement these methods such that they fulfil them. The methods
shall not change the state of the object,
shall not write on the inputs directory.
Indeed, it is also essential to assure that the inputs do not change from one run to another. The `run_in` method checks that `working_dir` points to a different location from the inputs directory.

By combining the previous gimmicks, we can run in parallel the GEOtop model from Python multiple times, using only one instance of the `GEOtoPy.GEOtop` class. 

A minimal functioning implementation is
```python
from geotopy import GEOtop

class Model(GEOtop):

    def preprocess(self, working_dir, *args, **kwargs):
        self.clone_into(working_dir)

    def postprocess(self, working_dir):
        return None
``` 
which populates the working directory with the input files, and always returns `None`.  

Indeed, the `GEOtoPy.GEOtop` class also provides some helper methods to implement the `preprocess` and `postprocess` ones, like `clone_into`.

## Nevergrad

The panorama of existing Python libraries for derivative-free optimization is varied, as different libraries account for different needs. However, the vast majority of these libraries are designed for hyperparameters optimization of machine learning models. Hyperparameters optimization in machine learning is a vast topic, which is difficult to summarize in a few words.  Still, the main idea is to find the optimal values of the parameters that control the learning process. For different reasons, derivative-based algorithms, such as gradient descent or BFGS, are usually not suited for searching the optimal values of model hyperparameters (for example, because there is a mixture of continuous and discrete parameters). An interesting class of algorithms is the early stopping one, especially when model training is computationally expensive. Indeed, the application of early stopping algorithms to the calibration of earth-system and environmental models might be a good research topic.

In general, derivative-free optimization libraries consist of two pieces:
    1.one to model the search space, and
    2. one to select the algorithm and perform the optimization.
Also, these libraries typically assume that the interface with the objective function is a callable object.

Nevergrad is a Python library for derivative-free optimization not explicitly targeted at hyperparameter optimization and focusing on evolutionary algorithms. It can handle continuous and discrete parameters, and Python containers, such as tuples, lists (arrays) and dictionaries. It has a wide range of preconfigured optimization algorithms, and it offers both a high level `minimize` function and a lower level ask-tell interface. Notice, that the `minimize` function is able to evaluate the objective function in parallel using the `concurrent.futures.Executor` interface.

As described in TODO, the ask-tell interface is a lower-level interface to access the optimization loop and will be discussed in the next chapter.

The Nevergrad library implements several evolutionary algorithms, such as Particle Swarm Optimization (PSO), Covariance Matrix Adaptation - Evolutionary Strategy (CMAES). It also contains one-shot algorithms, i.e. algorithms where the points of the search space which will be sampled are known from the beginning. Finally, it has two meta-algorithms, Shiva and NGO, which select an algorithm among the available ones based on the available information using empirical rules.

The algorithms implemented in Nevergrad follow the same philosophy as CMA-ES: the choice of the hyperparameters of the optimizer should be part of the algorithm's design (although it is possible to tweak and configure the optimizers if needed). The only parameters that the user must specify are the `budget` and `num_workers`. The first is, simplifying a bit, the number of allowed calls to `optimizer.ask()`. The budget is significant for some one-shot algorithms, where the optimizer must generate a low-discrepancy sequence of a given length apriori. The second is the number of objective function calls that can be evaluated in parallel, i.e. the number of CPUs. In evolutionary algorithms, the latter maps naturally to the number of individuals in a generation, the population size. In the next chapter, we will see how and why these two are involved in failing objective function evaluations.

## High-Performance Computing in Python using Dask

The previous sections leave open the question of whether it is possible to do High-Performance Computing using Python. The answer to this question is related to performing parallel computations on distributed systems using this language. It turns out that Python is indeed a useful tool for this purpose, and it is capable of scaling on large supercomputers (TODO quote Mark Coletti). Still, before moving to distributed systems, it is interesting to examine the topic of parallel computing in Python on a single shared-memory system.

### Parallel computing in Python

The reference implementation of Python, the CPython interpreter, compiles the Python code into an intermediate representation called bytecode, which runs on a virtual machine. Also, CPython uses reference counting for garbage collection. This means that there is a counter for each object created during the execution of a Python program: when a variable is bound to the object, the counter of the latter is increased, when a reference is deleted, the counter is decreased. Once the counter reaches zero, the object is deallocated, or, in C++ parlance, the destructor is called. In multi-threaded code, this form of garbage collection requires some mechanism to avoid data races. CPython opted for a global lock on the interpreter, hence called the Global Interpreter Lock or the GIL. External dependencies might or might not acquire the GIL, but when they do the interpreter cannot move to the next bytecode instruction until the GIL is released, even if the dependency spawns new threads. The reason is that Python includes several C dependencies, not all of them thread-safe.

The Python standard library provides the threading module to work with threads. However, one must always consider that the GIL prevents the interpreter to be executed by more than one thread at a time. In other terms, code written in pure Python will be executed as if there is only one CPU core, even if multiple ones are available. Of course, if the Python code running on a thread reach a C extension which releases the GIL or spawn its own threads, then the interpreter can move to the next instruction. In this way, we can have a speedup with multi-threaded code. This approach may be beneficial, for example, with Numpy routines or IO code.

The Python library also provides the multiprocessing package to do multi-processing (the clue is in the name). This module side-steps the GIL by launching several processes, each one being a full-fledged Python interpreter. The objects defined in the main process will be serialized and sent to the others. The serialization happens via the Pickle module from the standard library. However, Pickle has some limitations. For example, it is not able to serialize lambdas. If one wants to use multiprocessing he has to build his code around these limitations. Finally, multiprocessing has larger overhead than multithreading due to serialization and, on a much smaller degree and depending on the operating system, to system calls. Notice that the multiprocessing contains also the `shared_memory` module to provide direct access to shared memory across processes.

The standard library also provides some abstractions to work with these low-level tools. Among them, there is the `concurrent.futures` module. Promises and futures are constructs used in some concurrency models. They represent values that will eventually become available and are usually the result of a remote computation. They can be viewed as queues of size one: producers make promises while consumers wait for futures. These constructs are supported by many languages. The `concurrent.futures` module defines the `Executor` abstract class that provides methods to execute calls asynchronously, such as `submit` and `map`. The `submit(fn, *args, **kwargs)` method returns immediately a `Future` object. Afterwards, it is possible to call the `result` method on a `Future` object, which will block and return the value of `fn(*args, **kwargs)` as soon as it has been evaluated. The concrete classes `ThreadPoolExecutor` and `ProcessPoolExecutor`, derived from `Executor`, use a pool of threads and processes respectively to evaluate the result (again, the clue is in the name).

Finally, it should be noted that Python supports non-preemptive threading natively with `asyncio`, and, while `asyncio.Future` objects are awaitable, `concurrent.futures.Future` ones are not. 

### Distributed Computing with Dask

Dask is a library for parallel computing in Python which consists of two components: a scheduler and a collection of data structures with an interface familiar to Numpy and Pandas users. Indeed, it is possible to enable parallelism simply using Dask arrays and dataframes as a drop-in replacement for their Numpy and Pandas equivalent. Also, Dask can do out-of-core computations and exploit distributed systems. Since the application we are concerned with is CPU bounded, I will focus on the second. 

In Dask, operations on the above-mentioned data structures are divided into smaller tasks, and the dependency relations among the tasks is encoded into a task graph. Afterwards, the scheduler use the task graph to distribute the work among different processing units. Moreover, the intermediate representation of a computation as a graph allows for some optimizations.

Therefore, Dask fits naturally the domain of computations that can be efficiently expressed using array programming and involving large amounts of data. However, it also provides interfaces to interact directly with the scheduler, adapting to more general cases. One of them is the futures interface, which extends `concurrent.future` from the standard library. I briefly described the futures abstraction in the previous section and some further details will be discussed in the next chapter on implementation.

Dask has different scheduler implementations, and it's responsability of the user to choose and setup the right one. All the implementations share the concept of worker: a piece of software that takes a task, performs some computations and returns the results. Tasks are scheduled for execution on a pool of workers. Different workers might be executed concurrently on different CPU cores, thus achieving parallelism (or serially for debug purposes). 

Currently, there are four scheduler implementations available.

1. Local Threads. Tasks are executed on separate threads, and the implementation internally uses `multiprocessing.pool.ThreadPool`. Given the above discussion on multi-threading in Python, this scheduler must be chosen only when the tasks release the GIL, such as for Numpy or Pandas. Also, the overhead per task is small.
2. Local Processes. Tasks are executed on separate processes, and the implementation internally uses `multiprocessing.Pool`. There is a large communication overhead compared to threads, but pure Python tasks can be executed concurrently.
3. Single thread. Tasks are executed in the local thread, for debug purposes.
4. Dask Distributed. Tasks are executed by workers that runs as server applications.
   
Dask Distributed requires a runtime both for the scheduler and the workers, both running as separate daemon processes, and called `dask-scheduler` and `dask-worker`. It bundles an API to connect to `dask-scheduler` from Python via the `dask.distributed` module. However, it is possible to use this implementation on a single machine in the same fashion of the implementations, avoiding the setup and letting Dask Distributed manage the runtime. Using Dask Distributed on a single machine offers more advanced features than using local processes, such as profiling. For this reason, it is the recommended way of running Dask in most of the situations where using local threads is not.

In a Dask Distributed setup, there can be $N$ `dask-worker` processes, each internally running a pool of $T$ threads using`multiprocessing.pool.ThreadPool`. This means that at most $N \times T$ tasks can be executed in parallel, if there are enough CPU cores are available. Choosing the right combination of processes and threads is part of performance tuning, and it is specific to the kind of workload considered.

In a Dask cluster, there is one `dask-scheduler` and (possibly) multiple `dask-worker` processes. These processes do not need to be executed on the same machine, however, they must be on the same network, since the need to communicate one another. Communications among processes happens via TCP/IP, but UDP protocol is available and there is experimental support for Nvidia UCX. When starting the cluster the user must provide to each worker the address of the scheduler. The scheduler takes care of collecting and distributing the addresses of the workers on the network, so that point to point communications are possible without passing throught the scheduler.
