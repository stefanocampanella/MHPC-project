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

PORT=6379

INPUT=$1
OUTPUT=$2
CONTAINER=$3
PARAMETERS_FILE=$4

ray start --head --port=$PORT --num-cpus=$SLURM_CPUS_PER_TASK
sleep 30

# Implementation using srun, use instead:
# scontrol show hostnames $SLURM_JOB_NODELIST 
# to iterate through and ssh into nodes
if [[ $SLURM_JOB_NUM_NODES -gt 1 ]]
then
  srun --nodes=$(($SLURM_NTASKS - 1)) --exclude=`hostname` \
    ray start --address=`hostname`:$PORT --num-cpus=$SLURM_CPUS_PER_TASK
  sleep 30
fi

mkdir -p $(dirname $OUTPUT)
singularity run $CONTAINER $INPUT $OUTPUT $TOTAL_CORES $ADDRESS $PARAMETERS_FILE

