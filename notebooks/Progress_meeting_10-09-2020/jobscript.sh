#! /usr/bin/env bash
#
#SBATCH --job-name=mhpc_progress_meeting
#SBATCH --partition regular2
#SBATCH --time=1:30:00
#SBATCH --time-min=1:00:00
#SBATCH --chdir=$HOME/MHPC-project
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

WORKING_DIR=notebooks/Progress_meeting_10-09-2020
PARAMETERS_FILE=$WORKING_DIR/parameters.yaml
OUTPUT_DIR=$WORKING_DIR/outputs/$(date +%F_%H-%M)

OPTIONS="--no-progress-bar -p output_path $OUTPUT_DIR -f $PARAMETERS_FILE --cwd $WORKING_DIR"

mkdir -p $OUTPUT_DIR
srun pipenv run papermill $OPTIONS $WORKING_DIR/notebook.ipynb $OUTPUT_DIR/notebook.ipynb
srun pipenv jupyter nbconvert --to html --output $OUTPUT_DIR/notebook.html $OUTPUT_DIR/notebook.ipynb
srun pipenv jupyter nbconvert --to slides --output $OUTPUT_DIR/slides.html $OUTPUT_DIR/notebook.ipynb
cp $WORKING_DIR/jobscript.sh $OUTPUT_DIR/jobscript.sh
cp $WORKING_DIR/parameters.yaml $OUTPUT_DIR/parameters.yaml
tar cfJ $OUTPUT_DIR.tar.xz $OUTPUT_DIR --remove-files
