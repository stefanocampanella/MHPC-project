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

INPUT="$MHPCPROJECT_ROOT/notebooks/calibration.ipynb"
MODEL_PATH="$MHPCPROJECT_ROOT/data/$SITE/inputs"
OBSERVATIONS_PATH="$MHPCPROJECT_ROOT/data/$SITE/observations/obs.csv"
NUM_PROCS=4
NUM_CPUS=$((SLURM_CPUS_PER_TASK * SLURM_NTASKS))
NUM_WORKERS=$((NUM_PROCS * SLURM_NTASKS))
BUDGET=$((NUM_GENERATIONS * POPSIZE))
SCHEDULER_WAIT_RETRY_MAX=10

mkdir -p "$OUTPUT_DIR"
OUTPUT="$(mktemp -p "$OUTPUT_DIR" "$SITE-$ALGORITHM-$BUDGET-$NUM_CPUS-XXX.ipynb")"

mkdir -p "$MHPCPROJECT_ROOT/scheduler_files"
SCHEDULER_FILE="$(mktemp -p "$MHPCPROJECT_ROOT/scheduler_files" scheduler-XXX.json)"

ulimit -n 128000

dask-scheduler --scheduler-file="$SCHEDULER_FILE" \
               --no-dashboard \
               --no-show \
               --interface=ib0 &
sleep 30

SCHEDULER_WAIT_RETRY_COUNT=0
while ! python "$MHPCPROJECT_ROOT"/scripts/check_address.py "$SCHEDULER_FILE" && \
 [[ $SCHEDULER_WAIT_RETRY_COUNT -lt $SCHEDULER_WAIT_RETRY_MAX ]]
do
  SCHEDULER_WAIT_RETRY_COUNT=$((SCHEDULER_WAIT_RETRY_COUNT + 1))
  sleep 30
done
python "$MHPCPROJECT_ROOT"/scripts/check_address.py "$SCHEDULER_FILE"

srun dask-worker --scheduler-file="$SCHEDULER_FILE" \
                 --local-directory="/tmp" \
                 --death-timeout=180 \
                 --no-dashboard \
                 --no-show \
                 --nprocs=$NUM_PROCS \
                 --nthreads=$((SLURM_CPUS_PER_TASK / NUM_PROCS)) \
                 --interface=ib0 &

papermill --no-progress-bar \
          -p model_path "$MODEL_PATH" \
          -p timeout "$TIMEOUT" \
          -p observations_path "$OBSERVATIONS_PATH" \
          -p parameters_path "$PARAMETERS_PATH" \
          -p algorithm "$ALGORITHM" \
          -p popsize "$POPSIZE" \
          -p num_generations "$NUM_GENERATIONS" \
          -p scheduler_file "$SCHEDULER_FILE" \
          -p num_cpus $NUM_CPUS \
          -p num_workers $NUM_WORKERS \
          -p performance_report_filename "${OUTPUT%.ipynb}-performance-report.html" \
          "$INPUT" "$OUTPUT"
jupyter nbconvert --to html "$OUTPUT"
rm "$SCHEDULER_FILE"

exit
