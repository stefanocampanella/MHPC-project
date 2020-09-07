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
PARAMETERS_FILE=$WORKING_DIR/parameters.yaml
DATE=$(date +%F_%H-%M)
OUTPUT_DIR=$WORKING_DIR/outputs

OPTIONS="--no-progress-bar -p basename $OUTPUT_DIR/$DATE -f $PARAMETERS_FILE --cwd $WORKING_DIR"
COMMAND="pipenv run papermill $OPTIONS $WORKING_DIR/notebook.ipynb $OUTPUT_DIR/$DATE.ipynb"

mkdir -p $OUTPUT_DIR
srun $COMMAND
