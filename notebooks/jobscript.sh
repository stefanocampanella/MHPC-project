#! /usr/bin/env bash
#SBATCH --partition=regular2
#SBATCH --nodes=2
#SBATCH --tasks-per-node=1
#SBATCH --cpus-per-task=32
#SBATCH --exclusive=user
#SBATCH --hint=nomultithread
#SBATCH --hint=compute_bound
#SBATCH --mail-type=ALL
#SBATCH --verbose

module load singularity

INPUT=$1
OUTPUT=$2
CONTAINER=$3
PARAMETERS_FILE=$4

singularity exec $CONTAINER dask-scheduler
sleep 30

srun singularity exec $CONTAINER dask-worker tcp://`hostname`:8786 --nprocs=$SLURM_CPUS_PER_TASK --nthreads=1
sleep 30

mkdir -p $(dirname $OUTPUT)
singularity run $CONTAINER $INPUT $OUTPUT $TOTAL_CORES $ADDRESS $PARAMETERS_FILE

