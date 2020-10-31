#! /usr/bin/env bash
#SBATCH --partition=wide2
#SBATCH --nodes=32
#SBATCH --tasks-per-node=1
#SBATCH --cpus-per-task=4
#SBATCH --mem-per-cpu=500MB
#SBATCH --hint=nomultithread
#SBATCH --hint=compute_bound
#SBATCH --mail-type=ALL
#SBATCH --verbose

module load singularity

INPUT=$1
OUTPUT_DIR=$2
CONTAINER=$3
PARAMETERS_FILE=$4

singularity exec ${CONTAINER} dask-scheduler --interface ib0 &>scheduler.log &
sleep 30

srun singularity exec ${CONTAINER} dask-worker tcp://`hostname`:8786 --nprocs=$SLURM_CPUS_PER_TASK --nthreads=1 --interface ib0 &>workers.log &
sleep 30

mkdir -p $(dirname ${OUTPUT})
OPTIONS="--no-progress-bar \
  --cwd $(dirname ${INPUT}) \
  --report-mode \
  -p num_workers $(($SLURM_CPUS_PER_TASK * $SLURM_NTASKS)) \
  -p output_dir ${OUTPUT_DIR} 
  -p address `hostname`:8786"

if [ ! -z "${PARAMETERS_FILE}" ]
then
  OPTIONS="${OPTIONS} -f ${PARAMETERS_FILE}"
fi

OUTPUT_IPYNB=$(mktemp -d)/$(basename ${INPUT})

singularity exec ${CONTAINER} papermill ${OPTIONS} ${INPUT} ${OUTPUT_IPYNB}
singularity exec ${CONTAINER} jupyter nbconvert --no-input --to html --output-dir=${OUTPUT_DIR} ${OUTPUT_IPYNB}
rm -r $(dirname ${OUTPUT_IPYNB})
