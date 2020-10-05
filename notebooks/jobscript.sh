#! /usr/bin/env bash
#SBATCH --partition regular2
#SBATCH --nodes 2
#SBATCH --cpus-per-task 32
#SBATCH --mem-per-cpu 1GB
#SBATCH --hint compute_bound
#SBATCH --mail-type ALL
#SBATCH --verbose

module load gnu8 openmpi3
spack load python@3.8.3

ROOT=$HOME/MHPC-project
WORKING_DIR=$ROOT/notebooks
OUTPUT_DIR=$WORKING_DIR/outputs

INPUT=$WORKING_DIR/$1.ipynb
OUTPUT=$OUTPUT_DIR/$1_$(date +%F_%H-%M).ipynb
OPTIONS="--no-progress-bar --cwd $WORKING_DIR -p num_workers 64"
if [[ ! -z "$2" ]]
then
  OPTIONS="$OPTIONS -f $2.yaml"
fi

export OMPI_UNIVERSE_SIZE=64
export NUMEXPR_NUM_THREADS=1
export NUMEXPR_MAX_THREADS=1
export OMP_NUM_THREADS=1

cd $ROOT

mkdir -p $OUTPUT_DIR
mpirun -n 1 pipenv run papermill $OPTIONS  $INPUT $OUTPUT && \
pipenv run jupyter nbconvert $OUTPUT --to html --output-dir $OUTPUT_DIR && \
rm $OUTPUT 
