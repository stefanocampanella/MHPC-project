#! /usr/bin/env bash

export MHPCPROJECT_ROOT=/scratch/$USER/MHPC-project
export PYTHONPATH=$MHPCPROJECT_ROOT
export DASK_DASK__TEMPORARY_DIRECTORY="/tmp/dask-worker-space"
export DASK_DISTRIBUTED__COMM__RETRY__COUNT=4
export DASK_DISTRIBUTED__COMM__OFFLOAD=false
export DASK_DISTRIBUTED__COMM__SOCKET_BACKLOG=4096
export DASK_DISTRIBUTED__COMM__TIMEOUTS__CONNECT="60s"
export DASK_DISTRIBUTED__COMM__TIMEOUTS__TCP="90s"
export DASK_DISTRIBUTED__SCHEDULER__UNKOWN_TASK-DURATION="180s"
export DASK_DISTRIBUTED__LOGGING__DISTRIBUTED="info"
export DASK_DISTRIBUTED__LOGGING__BOKEH="critical"
export DASK_DISTRIBUTED__LOGGING__TORNADO="critical"
export DASK_DISTRIBUTED__WORKER__USE_FILE-LOCKING=false

cd "$MHPCPROJECT_ROOT" || exit
mkdir -p "slurm_outputs"

echo "==== Submitting testbed calibration strong scaling jobs ===="
SITE=testbed
TIMEOUT=300
PARAMETERS_PATH="$MHPCPROJECT_ROOT/data/parameters/testbed.csv"
ALGORITHM=NGO
POPSIZE=512
NUM_GENERATIONS=8
REPETITIONS=8
OUTPUT="$MHPCPROJECT_ROOT/runs/scaling"
for NUM_NODES in 4 8 12 16 20 24 28 32
do
  if [[ $NUM_NODES -eq 4 ]]
  then
    PARTITION=regular2
    TIME=4:00:00
  elif [[ $NUM_NODES -eq 8 ]]
  then
    PARTITION=regular2
    TIME=3:00:00
  elif [[ $NUM_NODES -le 16 ]]
  then
    PARTITION=regular2
    TIME=2:00:00
  else
    PARTITION=wide2
    TIME=2:00:00
  fi
  for n in $(seq $REPETITIONS)
  do
    sbatch -p "$PARTITION" -J "scaling_$SITE" -N "$NUM_NODES" -t "$TIME" \
           -o "slurm_outputs/%x-%j.out"  -e "slurm_outputs/%x-%j.err" \
      ./scripts/run.slurm "$SITE" "$PARAMETERS_PATH" "$ALGORITHM" "$POPSIZE" "$NUM_GENERATIONS" "$TIMEOUT" "$OUTPUT"
  done
done

echo "==== Submitting all-sites calibration of testbed parameters jobs ===="
TIMEOUT=360
PARAMETERS_PATH="$MHPCPROJECT_ROOT/data/parameters/testbed.csv"
ALGORITHM=NGO
POPSIZE=1024
NUM_GENERATIONS=64
PARTITION=wide2
NUM_NODES=32
TIME=8:00:00
OUTPUT="$MHPCPROJECT_ROOT/runs/testbed"
for SITE in DOMEF DOMES DOPAS Kaltern Latsch "Matsch B2" "Matsch P2" NEPAS
do
  sbatch -p "$PARTITION" -J "testbed_$SITE" -N "$NUM_NODES" -t "$TIME" \
         -o "slurm_outputs/%x-%j.out"  -e "slurm_outputs/%x-%j.err" \
    ./scripts/run.slurm "$SITE" "$PARAMETERS_PATH" "$ALGORITHM" "$POPSIZE" "$NUM_GENERATIONS" "$TIMEOUT" "$OUTPUT"
done

echo "==== Submitting all-sites calibration of full set of parameters jobs ===="
TIMEOUT=360
PARAMETERS_PATH="$MHPCPROJECT_ROOT/data/parameters/all.csv"
ALGORITHM=NGO
POPSIZE=1024
NUM_GENERATIONS=64
PARTITION=wide2
NUM_NODES=32
TIME=8:00:00
OUTPUT="$MHPCPROJECT_ROOT/runs/all"
for SITE in DOMEF DOMES DOPAS Kaltern Latsch "Matsch B2" "Matsch P2" NEPAS
do
  sbatch -p "$PARTITION" -J "all_$SITE" -N "$NUM_NODES" -t "$TIME" \
         -o "slurm_outputs/%x-%j.out"  -e "slurm_outputs/%x-%j.err" \
    ./scripts/run.slurm "$SITE" "$PARAMETERS_PATH" "$ALGORITHM" "$POPSIZE" "$NUM_GENERATIONS" "$TIMEOUT" "$OUTPUT"
done

echo "==== Submitting different algorithms testbed calibration jobs ===="
SITE=testbed
TIMEOUT=360
PARAMETERS_PATH="$MHPCPROJECT_ROOT/data/parameters/testbed.csv"
POPSIZE=1024
NUM_GENERATIONS=64
PARTITION=wide2
NUM_NODES=32
TIME=8:00:00
OUTPUT="$MHPCPROJECT_ROOT/runs/algorithms"
for ALGORITHM in NGO PSO Random
do
  sbatch -p "$PARTITION" -J "algorithms_$SITE" -N "$NUM_NODES" -t "$TIME" \
         -o "slurm_outputs/%x-%j.out"  -e "slurm_outputs/%x-%j.err" \
    ./scripts/run.slurm "$SITE" "$PARAMETERS_PATH" "$ALGORITHM" "$POPSIZE" "$NUM_GENERATIONS" "$TIMEOUT" "$OUTPUT"
done


