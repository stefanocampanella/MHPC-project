#! /usr/bin/env bash
#SBATCH --tasks-per-node=1
#SBATCH --cpus-per-task=32
#SBATCH --mem-per-cpu=400MB
#SBATCH --hint=nomultithread
#SBATCH --hint=compute_bound
#SBATCH --mail-type=ALL
#SBATCH --verbose

SITE=$1
ALGORITHM=$2
GENERATIONS=$3
OUTPUT_DIR=$4

SCHEDULER="$(hostname):8786"
MODEL_PATH="${MHPCPROJECT_ROOT}/data/${SITE}/inputs"
OBSERVATIONS_PATH="${MHPCPROJECT_ROOT}/data/${SITE}/observations/obs.csv"
NUM_WORKERS=$((SLURM_CPUS_PER_TASK * SLURM_NTASKS))
BUDGET=$((GENERATIONS * NUM_WORKERS))
INPUT="${MHPCPROJECT_ROOT}/notebooks/calibration.ipynb"
OUTPUT="${OUTPUT_DIR}/${SITE}-${ALGORITHM}-${BUDGET}-${NUM_WORKERS} ($(date +%F-%T)).ipynb"

export NUMEXPR_NUM_THREADS=1
export NUMEXPR_MAX_THREADS=1
export OMP_NUM_THREADS=1
export TMPDIR=/dev/shm

dask-scheduler --scheduler-file "${MHPCPROJECT_ROOT}"/scheduler.json --interface ib0 &
sleep 10

srun dask-worker "${SCHEDULER}" --nprocs=1 --nthreads="${SLURM_CPUS_PER_TASK}" --interface ib0 &
sleep 10

mkdir -p "${OUTPUT_DIR}"
papermill --cwd "$(dirname "${PARAMETERS_FILE}")" \
          -p model_path "${MODEL_PATH}" \
          -p observations_path "${OBSERVATIONS_PATH}" \
          -p num_workers ${NUM_WORKERS} \
          -p algorithm "${ALGORITHM}" \
          -p budget ${BUDGET} \
          -p address "${SCHEDULER}" \
          "${INPUT}" "${OUTPUT}"
