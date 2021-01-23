#! /usr/bin/env bash
#SBATCH --tasks-per-node=1
#SBATCH --cpus-per-task=32
#SBATCH --mem-per-cpu=400MB
#SBATCH --hint=nomultithread
#SBATCH --hint=compute_bound
#SBATCH --mail-type=ALL
#SBATCH --verbose

SITE=$1
PARAMETERS_PATH=$2
ALGORITHM=$3
POPSIZE=$4
NUM_GENERATIONS=$5
TIMEOUT=$6
OUTPUT_DIR=$7

export TMPDIR=/dev/shm
export PYTHONPATH=$PYTHONPATH:$MHPCPROJECT_ROOT
export DASK_CONFIG=$MHPCPROJECT_ROOT/config/dask

INPUT="${MHPCPROJECT_ROOT}/notebooks/calibration.ipynb"
MODEL_PATH="${MHPCPROJECT_ROOT}/data/${SITE}/inputs"
OBSERVATIONS_PATH="${MHPCPROJECT_ROOT}/data/${SITE}/observations/obs.csv"
NUM_WORKERS=$((SLURM_CPUS_PER_TASK * SLURM_NTASKS))
BUDGET=$((NUM_GENERATIONS * POPSIZE))

mkdir -p "${OUTPUT_DIR}"
OUTPUT="$(mktemp -p "${OUTPUT_DIR}" "${SITE}-${ALGORITHM}-${BUDGET}-${NUM_WORKERS}-XXX.ipynb")"

mkdir -p "${MHPCPROJECT_ROOT}/scheduler_files"
SCHEDULER_FILE="$(mktemp -p "${MHPCPROJECT_ROOT}/scheduler_files" scheduler-XXX.json)"

ulimit -n 16384

dask-scheduler --scheduler-file="${SCHEDULER_FILE}" \
               --no-dashboard \
               --no-show \
               --interface=ib0 &
sleep 60

srun dask-worker --scheduler-file="${SCHEDULER_FILE}" \
                 --local-directory="/tmp" \
                 --death-timeout=180 \
                 --no-dashboard \
                 --no-show \
                 --nprocs=8 \
                 --nthreads=4 \
                 --interface=ib0 &

papermill --no-progress-bar \
          -p model_path "${MODEL_PATH}" \
          -p timeout "${TIMEOUT}" \
          -p observations_path "${OBSERVATIONS_PATH}" \
          -p parameters_path "${PARAMETERS_PATH}" \
          -p algorithm "${ALGORITHM}" \
          -p popsize "${POPSIZE}" \
          -p num_generations "${NUM_GENERATIONS}" \
          -p num_nodes "${SLURM_NTASKS}" \
          -p scheduler_file "${SCHEDULER_FILE}" \
          -p num_workers ${NUM_WORKERS} \
          -p performance_report_filename "${OUTPUT%.ipynb}-performance-report.html" \
          "${INPUT}" "${OUTPUT}"
jupyter nbconvert --to html "${OUTPUT}"
rm "${SCHEDULER_FILE}"

exit
