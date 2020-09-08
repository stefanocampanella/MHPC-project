#! /usr/bin/env bash
#
#SBATCH --job-name=mhpc_progress_meeting
#SBATCH --partition regular2
#SBATCH --time=10:00
#SBATCH --time-min=5:00
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
OUTPUT_DIR=$WORKING_DIR/data/outputs/$(date +%F_%H-%M)

OPTIONS="--no-progress-bar -p output_path $OUTPUT_DIR -f $WORKING_DIR/parameters.yaml --cwd $WORKING_DIR"

mkdir -p $OUTPUT_DIR

srun pipenv run papermill $OPTIONS $WORKING_DIR/notebook.ipynb $OUTPUT_DIR/notebook.ipynb

srun pipenv run jupyter nbconvert --to html $OUTPUT_DIR/notebook.ipynb
srun pipenv run jupyter nbconvert --to slides $OUTPUT_DIR/notebook.ipynb
cp $WORKING_DIR/jobscript.sh $OUTPUT_DIR/jobscript.sh
cp $WORKING_DIR/parameters.yaml $OUTPUT_DIR/parameters.yaml

cd $OUTPUT_DIR/..
tar cfJ $(basename $OUTPUT_DIR).tar.xz $(basename $OUTPUT_DIR) --remove-files
