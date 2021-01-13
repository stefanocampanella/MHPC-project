#! /usr/bin/env bash
#SBATCH --partition=regular2
#SBATCH --nodes=8
#SBATCH --tasks-per-node=1
#SBATCH --cpus-per-task=32
#SBATCH --mem-per-cpu=400MB
#SBATCH --hint=nomultithread
#SBATCH --hint=compute_bound
#SBATCH --mail-type=ALL
#SBATCH --verbose

INPUT=$1
OUTPUT=$2
PARAMETERS_FILE=$4

export NUMEXPR_NUM_THREADS=1
export NUMEXPR_MAX_THREADS=1
export OMP_NUM_THREADS=1
export TMPDIR=/dev/shm

dask-scheduler --scheduler-file "${MHPCPROJECT_ROOT}"/scheduler.json --interface ib0 &
sleep 10

srun dask-worker "tcp://$(hostname):8786" --nprocs="${SLURM_TASKS_PER_NODE}" --nthreads="${SLURM_CPUS_PER_TASK}" --interface ib0 &
sleep 10

mkdir -p "$(dirname "${OUTPUT}")"
OPTIONS="--no-progress-bar \
         --cwd $(dirname "${PARAMETERS_FILE}") \
         -p popsize $((SLURM_CPUS_PER_TASK * SLURM_NTASKS)) \
         -p address $(hostname):8786 \
         -f ${PARAMETERS_FILE}"

papermill "${OPTIONS}" "${INPUT}" "${OUTPUT}"
