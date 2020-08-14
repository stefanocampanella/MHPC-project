#! /usr/bin/env bash
#
#SBATCH --job-name=geotop_calibration
#SBATCH --partition regular2
#SBATCH --time=1:00:00
#SBATCH --time-min=40:00
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=32
#SBATCH --hint=compute_bound
#SBATCH --mail-type=ALL
#SBATCH --exclusive=user
#SBATCH --verbose

module load gnu8
spack load python@3.8.3
export NUMEXPR_NUM_THREADS=1
export NUMEXPR_MAX_THREADS=1
export OMP_NUM_THREADS=1

ROOT=$HOME/MHPC-project
WORKING_DIR=$ROOT/notebooks/Nevergrad_example
PARAMETERS_FILE=$WORKING_DIR/parameters.yaml
OUTPUT=$ROOT/output.ipynb

OPTIONS="--no-progress-bar -f $PARAMETERS_FILE --cwd $WORKING_DIR"
COMMAND="pipenv run papermill $OPTIONS $WORKING_DIR/notebook.ipynb $OUTPUT"

srun $COMMAND
