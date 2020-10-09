#! /usr/bin/env bash
#SBATCH --partition=regular2
#SBATCH --nodes=2
#SBATCH --tasks-per-node=1
#SBATCH --cpus-per-task=32
#SBATCH --mem-per-cpu=1GB
#SBATCH --exclusive=user
#SBATCH --hint=nomultithread
#SBATCH --hint=compute_bound
#SBATCH --mail-type=ALL
#SBATCH --verbose

let "WORKER_NUM=($SLURM_NTASKS - 1)"
let "TOTAL_CORES=$SLURM_NTASKS * $SLURM_CPUS_PER_TASK"
PORT='6379'

export ADDRESS=`hostname`:$PORT

INPUT=$1
OUTPUT=$2
CONTAINER=$3
PARAMETERS_FILE=$4

singularity instance start $CONTAINER headnode head $PORT $SLURM_CPUS_PER_TASK

if [[ $SLURM_JOB_NUM_NODES -gt 1 ]]
then
  srun --nodes=$WORKER_NUM --exclude=`hostname` \
    singularity instance start $CONTAINER workernode worker $ADDRESS $SLURM_CPUS_PER_TASK
fi

mkdir -p $(dirname $OUTPUT)
singularity run $CONTAINER $INPUT $OUTPUT $TOTAL_CORES $ADDRESSS $PARAMETERS_FILE
singularity instance stop --all

