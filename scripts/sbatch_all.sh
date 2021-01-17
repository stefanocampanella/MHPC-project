#! /usr/bin/env bash

export MHPCPROJECT_ROOT=/scratch/$USER/MHPC-project
export PYTHONPATH=$MHPCPROJECT_ROOT
export DASK_CONFIG=$MHPCPROJECT_ROOT/config/dask

TIMEOUT=200

cd "$MHPCPROJECT_ROOT" || exit

# For all sites
ALGORITHM=NGO
POPSIZE=256
NUM_GENERATIONS=64
PARTITION=wide2
NUM_NODES=32
OUTPUT="$MHPCPROJECT_ROOT/runs/sites"
for SITE in DOMEF DOMES DOPAS Kaltern Latsch "Matsch B2" "Matsch P2" NEPAS
do
  SECONDS=$((600 + 45 * NUM_GENERATIONS * POPSIZE / NUM_NODES))
  TIME=$(date -d@$SECONDS -u "+%H:%M:%S")
  sbatch -p "$PARTITION" -J "$SITE" -N "$NUM_NODES" -t "$TIME" \
    ./scripts/run.slurm "$SITE" "$ALGORITHM" "$POPSIZE" "$NUM_GENERATIONS" "$TIMEOUT" "$OUTPUT"
done

# For some algorithms
SITE="Matsch B2"
POPSIZE=128
NUM_GENERATIONS=32
PARTITION=regular2
NUM_NODES=8
OUTPUT="$MHPCPROJECT_ROOT/runs/algorithms"
for ALGORITHM in NGO PSO Random
do
  SECONDS=$((600 + 45 * NUM_GENERATIONS * POPSIZE / NUM_NODES))
  TIME=$(date -d@$SECONDS -u "+%H:%M:%S")
  sbatch -p "$PARTITION" -J "$SITE" -N "$NUM_NODES" -t "$TIME" \
    ./scripts/run.slurm "$SITE" "$ALGORITHM" "$POPSIZE" "$NUM_GENERATIONS" "$TIMEOUT" "$OUTPUT"
done

# Strong scaling
SITE="Matsch B2"
ALGORITHM=NGO
POPSIZE=128
NUM_GENERATIONS=16
REPETITIONS=4
OUTPUT="$MHPCPROJECT_ROOT/runs/nodes"
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
      sbatch -p "$PARTITION" -J "$SITE" -N "$NUM_NODES" -t "$TIME" \
        ./scripts/run.slurm "$SITE" "$ALGORITHM" "$POPSIZE" "$NUM_GENERATIONS" "$TIMEOUT" "$OUTPUT"
    done
  fi
done

