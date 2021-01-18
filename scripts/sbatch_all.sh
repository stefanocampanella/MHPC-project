#! /usr/bin/env bash

export MHPCPROJECT_ROOT=/scratch/$USER/MHPC-project
export PYTHONPATH=$MHPCPROJECT_ROOT
export DASK_CONFIG=$MHPCPROJECT_ROOT/config/dask

TIMEOUT=200

cd "$MHPCPROJECT_ROOT" || exit

# Strong scaling
SITE=testbed
PARAMETERS_PATH="$MHPCPROJECT_ROOT/data/parameters/testbed.csv"
ALGORITHM=NGO
POPSIZE=128
NUM_GENERATIONS=16
REPETITIONS=4
OUTPUT="$MHPCPROJECT_ROOT/runs/scaling"
for NUM_NODES in 4 8 12 16 20 24 28 32
do
  SECONDS=$((600 + 30 * NUM_GENERATIONS * POPSIZE / NUM_NODES))
  if [[ $SECONDS -gt 43200 ]]
  then
    PARTITION=long2
  elif [[ $NUM_NODES -gt 16 ]]
  then
    PARTITION=wide2
  elif [[ $SECONDS -gt 43200 ]] && [[ $NUM_NODES -gt 16 ]]
  then
    PARTITION=""
  else
    PARTITION=regular2
  fi
  if [[ -n $PARTITION ]]
  then
    for n in $(seq $REPETITIONS)
    do
      TIME=$(date -d@$SECONDS -u "+%H:%M:%S")
      sbatch -p "$PARTITION" -J "scaling_$SITE" -N "$NUM_NODES" -t "$TIME" \
        ./scripts/run.slurm "$SITE" "$PARAMETERS_PATH" "$ALGORITHM" "$POPSIZE" "$NUM_GENERATIONS" "$TIMEOUT" "$OUTPUT"
    done
  fi
done

# Testbed parameters calibration for all sites
PARAMETERS_PATH="$MHPCPROJECT_ROOT/data/parameters/testbed.csv"
ALGORITHM=NGO
POPSIZE=256
NUM_GENERATIONS=64
PARTITION=wide2
NUM_NODES=32
OUTPUT="$MHPCPROJECT_ROOT/runs/testbed"
for SITE in DOMEF DOMES DOPAS Kaltern Latsch "Matsch B2" "Matsch P2" NEPAS
do
  SECONDS=$((600 + 45 * NUM_GENERATIONS * POPSIZE / NUM_NODES))
  TIME=$(date -d@$SECONDS -u "+%H:%M:%S")
  sbatch -p "$PARTITION" -J "testbed_$SITE" -N "$NUM_NODES" -t "$TIME" \
    ./scripts/run.slurm "$SITE" "$PARAMETERS_PATH" "$ALGORITHM" "$POPSIZE" "$NUM_GENERATIONS" "$TIMEOUT" "$OUTPUT"
done

# All parameters calibration for all sites
PARAMETERS_PATH="$MHPCPROJECT_ROOT/data/parameters/all.csv"
ALGORITHM=NGO
POPSIZE=256
NUM_GENERATIONS=64
PARTITION=wide2
NUM_NODES=32
OUTPUT="$MHPCPROJECT_ROOT/runs/all"
for SITE in DOMEF DOMES DOPAS Kaltern Latsch "Matsch B2" "Matsch P2" NEPAS
do
  SECONDS=$((600 + 45 * NUM_GENERATIONS * POPSIZE / NUM_NODES))
  TIME=$(date -d@$SECONDS -u "+%H:%M:%S")
  sbatch -p "$PARTITION" -J "all_$SITE" -N "$NUM_NODES" -t "$TIME" \
    ./scripts/run.slurm "$SITE" "$PARAMETERS_PATH" "$ALGORITHM" "$POPSIZE" "$NUM_GENERATIONS" "$TIMEOUT" "$OUTPUT"
done

# For some algorithms
SITE=testbed
PARAMETERS_PATH="$MHPCPROJECT_ROOT/data/parameters/testbed.csv"
POPSIZE=128
NUM_GENERATIONS=32
PARTITION=regular2
NUM_NODES=8
OUTPUT="$MHPCPROJECT_ROOT/runs/algorithms"
for ALGORITHM in NGO PSO Random
do
  SECONDS=$((600 + 45 * NUM_GENERATIONS * POPSIZE / NUM_NODES))
  TIME=$(date -d@$SECONDS -u "+%H:%M:%S")
  sbatch -p "$PARTITION" -J "algorithms_$SITE" -N "$NUM_NODES" -t "$TIME" \
    ./scripts/run.slurm "$SITE" "$PARAMETERS_PATH" "$ALGORITHM" "$POPSIZE" "$NUM_GENERATIONS" "$TIMEOUT" "$OUTPUT"
done


