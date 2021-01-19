#! /usr/bin/env bash

export MHPCPROJECT_ROOT=/scratch/$USER/MHPC-project
export PYTHONPATH=$MHPCPROJECT_ROOT
export DASK_CONFIG=$MHPCPROJECT_ROOT/config/dask

TIMEOUT=200

cd "$MHPCPROJECT_ROOT" || exit

# Testbed calibration strong scaling
SITE=testbed
PARAMETERS_PATH="$MHPCPROJECT_ROOT/data/parameters/testbed.csv"
ALGORITHM=NGO
POPSIZE=256
NUM_GENERATIONS=16
REPETITIONS=3
OUTPUT="$MHPCPROJECT_ROOT/runs/scaling"
for NUM_NODES in 4 8 12 16 20 24 28 32
do
  if [[ $NUM_NODES -le 16 ]]
  then
    PARTITION=regular2
    TIME=6:00:00
  else
    PARTITION=wide2
    TIME=4:00:00
  fi
  for n in $(seq $REPETITIONS)
  do
    sbatch -p "$PARTITION" -J "scaling_$SITE" -N "$NUM_NODES" -t "$TIME" \
      ./scripts/run.slurm "$SITE" "$PARAMETERS_PATH" "$ALGORITHM" "$POPSIZE" "$NUM_GENERATIONS" "$TIMEOUT" "$OUTPUT"
  done
done

# Testbed parameters calibration for all sites
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
    ./scripts/run.slurm "$SITE" "$PARAMETERS_PATH" "$ALGORITHM" "$POPSIZE" "$NUM_GENERATIONS" "$TIMEOUT" "$OUTPUT"
done

# All parameters calibration for all sites
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
    ./scripts/run.slurm "$SITE" "$PARAMETERS_PATH" "$ALGORITHM" "$POPSIZE" "$NUM_GENERATIONS" "$TIMEOUT" "$OUTPUT"
done

# Testbed calibration using different algorithms
SITE=testbed
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
    ./scripts/run.slurm "$SITE" "$PARAMETERS_PATH" "$ALGORITHM" "$POPSIZE" "$NUM_GENERATIONS" "$TIMEOUT" "$OUTPUT"
done


