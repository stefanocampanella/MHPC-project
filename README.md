# MHPC Final Project
## High-Performance Derivative Free Optimization for the Calibration of the GEOtop Model

This repository contains notebooks, code and documentation related to my final project for the 2019/20 edition of the MHPC. The thesis will be hosted here, as well. 

In this project, I will try to get some insights into high-performance derivative-free optimization and exploit HPC for the calibration of parameters of the [GEOtop model](https://geotopmodel.github.io/geotop). The topic is interesting both from a scientific and technological point of view; you can find more information [here](https://stefanocampanella.github.io/MHPC_project_meeting).

Eventually, the code for the project will consist of three packages. These will be a GEOtop wrapper ([GEOtoPy](https://github.com/stefanocampanella/GEOtoPy)), an optimizer (most probably a fork of [Nevergrad](https://github.com/facebookresearch/nevergrad)), and a GEOtop calibration tool, which will make use of the previous two. From a design point of view, the goal is non-trivial. On the one hand, the calibration utility should be simple to use and automate most of the work. On the other, it must be general enough to be used on the full gamut of real-world applications.

At present, the content of this repository is somewhat provisional and exploratory in nature. It contains preliminary analysis and experiments with the interface and the optimizer. At the end of the project, it will host an application to a case study and reports.  

Nonetheless, since the very beginning, a special effort has been made to provide the code and documentation to set-up an easily reproducible environment. Hence, to execute the notebooks in this repo, use the instructions below. 


## Prerequisites

* Python 2 (>=2.6) or 3 (>=3.5) to run Spack
* A C/C++ compiler for building
* The `make` executable for building
* The `git` and `curl` commands for fetching

If you are on an HPC cluster, load the needed modules via `module load module1 module2 ...`.


## Installation

This project uses Pipenv to manage dependencies. Pipenv will create a virtual environment, download and install the required Python packages for you. 

In turn, Pipenv can be installed using Pip, which should be provided by most Python installations. However, this project uses a relatively recent version of Python, which may not be available on your system (especially if you are working on an HPC cluster). In this case, you will need to install Python 3.8, before using Pip and then Pipenv. The following instructions should work on most systems.

### Python 3.8

Install Spack with
```
$ git clone https://github.com/spack/spack.git
$ cd spack
$ git checkout v0.15.3
```
then add to your `.bashrc` 
```
export SPACK_ROOT=/path/to/spack
. $SPACK_ROOT/share/spack/setup-env.sh
```
and source it. 

You may want to use a different compiler than the default one. To list the available compilers use
```
$ spack compiler list
```

If the desired compiler is not in the list, try
```
$ spack compiler find
```

Now install and load Python via Spack. At the time of writing, the latest version of Python is the 3.8.3.
```
$ spack install python@3.8.3
$ spack load python@3.8.3
```
### Pipenv

Unfortunately, Pip is not bundled with Python 3.8.3 in Spack. Although there is the package `py-pip`, it uses a previous version of Python which will not make for us. Therefore, if you have installed Python 3.8 using the instructions above, install Pip with
```
$ curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py
$ python get-pip.py
```

Afterwards, install Pipenv
```
$ pip install --local pipenv
```

Finally, clone the project, `cd` into it, and use Pipenv
```
# clone also submodules, see previous section
$ git clone --recurse-submodules https://github.com/stefanocampanella/MHPC-project.git
$ cd MHPC-project

# include pre-release to avoid errors
$ pipenv install --pre
```

### GEOtop

This project uses GEOtoPy, which does not bundle a GEOtop executable. For this reason, currently GEOtop is provided as a Git submodule of this repository and you will need to build it manually. In the future a Spack package for GEOtop may be provided.

First install and load Meson and Ninja via Spack
```
$ spack install meson ninja
$ spack load meson ninja
```

Then `cd` into `geotop` and checkout the latest release
```
$ cd geotop
$ git checkout v3.0_paper
```

Create the build directory, configure, and build the project
```
$ mkdir build
$ meson build
$ cd build
$ meson configure -DMATH_OPTIM=true -DMUTE_GEOLOG=true -DMUTE_GEOTIMER=true -Db_lto=true
$ ninja geotop
```

## Usage

After login, remember to load the Python module from Spack
```
$ spack load python@3.8.3
```

Now you can run a command within the virtual environment created by Pipenv with `pipenv run command` or open a shell using `pipenv shell`.

To run a notebook under `notebook/foo/bar.ipynb` and save the output in `baz.ipynb` using Papermill issue

```
# from the root of the project
$ pipenv run papermill --cwd notebooks/foo notebooks/foo/bar.ipynb baz.ipynb
```

or, if you are on a cluster using Slurm
```
$ srun pipenv run papermill --cwd notebooks/foo notebooks/foo/bar.ipynb baz.ipynb
```


## License

Distributed under the GPL3 License. See LICENSE for more information.