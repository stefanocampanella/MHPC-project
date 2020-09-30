#! /usr/bin/env bash
#
#SBATCH --partition regular2
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
WORKING_DIR=$ROOT/notebooks
OUTPUT_DIR=$WORKING_DIR/outputs

INPUT=$WORKING_DIR/$1.ipynb
OUTPUT=$OUTPUT_DIR/$1_$(date +%F_%H-%M).ipynb
OPTIONS="--no-progress-bar --cwd $WORKING_DIR"
if [[ -z ! "$2" ]]
then
  OPTIONS="$OPTIONS -f $WORKING_DIR/$2.yaml"
fi

cd $ROOT
mkdir -p $OUTPUT_DIR
srun pipenv run papermill $OPTIONS $INPUT $OUTPUT
srun pipenv run jupyter nbconvert $OUTPUT --to html --output-dir $OUTPUT_DIR
rm $OUTPUT 
