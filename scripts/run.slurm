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
TIMEOUT=$4
OUTPUT_DIR=$5

SCHEDULER_FILE="$(mktemp -p "${MHPCPROJECT_ROOT}" scheduler-XXX.json)"
MODEL_PATH="${MHPCPROJECT_ROOT}/data/${SITE}/inputs"
OBSERVATIONS_PATH="${MHPCPROJECT_ROOT}/data/${SITE}/observations/obs.csv"
NUM_WORKERS=$((SLURM_CPUS_PER_TASK * SLURM_NTASKS))
BUDGET=$((GENERATIONS * NUM_WORKERS))
INPUT="${MHPCPROJECT_ROOT}/notebooks/calibration.ipynb"
mkdir -p "${OUTPUT_DIR}"
OUTPUT="$(mktemp -p "${OUTPUT_DIR}" "${SITE}-${ALGORITHM}-${BUDGET}-${NUM_WORKERS}-XXX.ipynb")"


export NUMEXPR_NUM_THREADS=1
export NUMEXPR_MAX_THREADS=1
export OMP_NUM_THREADS=1
export TMPDIR=/dev/shm

dask-scheduler --scheduler-file="${SCHEDULER_FILE}" \
               --interface=ib0 &
sleep 120

srun dask-worker --scheduler-file="${SCHEDULER_FILE}" \
                 --nprocs=1 \
                 --nthreads="${SLURM_CPUS_PER_TASK}" \
                 --interface=ib0 &
sleep 60

papermill --no-progress-bar \
          -p model_path "${MODEL_PATH}" \
          -p observations_path "${OBSERVATIONS_PATH}" \
          -p algorithm "${ALGORITHM}" \
          -p num_workers ${NUM_WORKERS} \
          -p budget ${BUDGET} \
          -p timeout "${TIMEOUT}" \
          -p scheduler_file "${SCHEDULER_FILE}" \
          "${INPUT}" "${OUTPUT}"
rm "${SCHEDULER_FILE}"

exit