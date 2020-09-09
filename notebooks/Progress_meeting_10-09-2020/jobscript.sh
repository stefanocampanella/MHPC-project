#! /usr/bin/env bash
#
#SBATCH --job-name=mhpc_progress_meeting
#SBATCH --partition regular2
#SBATCH --time=1:30:00
#SBATCH --time-min=1:00:00
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
WORKING_DIR=$ROOT/notebooks/Progress_meeting_10-09-2020
OUTPUT_DIR=$WORKING_DIR/data/outputs
OPTIONS="--no-progress-bar -f $WORKING_DIR/parameters.yaml --cwd $WORKING_DIR"

mkdir -p $OUTPUT_DIR
srun pipenv run papermill $OPTIONS $WORKING_DIR/notebook.ipynb $OUTPUT_DIR/$(date +%F_%H-%M).ipynb
