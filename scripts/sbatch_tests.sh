#! /usr/bin/env bash

export MHPCPROJECT_ROOT=/scratch/$USER/MHPC-project

cd "$MHPCPROJECT_ROOT" || exit
mkdir -p "slurm_outputs"

SITE=testbed
TIMEOUT=150
PARAMETERS_PATH="$MHPCPROJECT_ROOT/data/parameters/testbed.csv"
ALGORITHM=NGO
POPSIZE=64
NUM_GENERATIONS=4
OUTPUT="$MHPCPROJECT_ROOT/runs/tests"

echo "==== Submitting test jobs ===="
for NUM_NODES in  4 8 16 32
do
  if [[ $NUM_NODES -eq 4 ]]
  then
    PARTITION=regular2
    TIME=1:00:00
  elif [[ $NUM_NODES -le 16 ]]
  then
    PARTITION=regular2
    TIME=30:00
  else
    PARTITION=wide2
    TIME=30:00
  fi
  sbatch -p "$PARTITION" -J "test_$NUM_NODES" -N "$NUM_NODES" -t "$TIME" --output "slurm_outputs/%x-%j.out" \
    ./scripts/run.slurm "$SITE" "$PARAMETERS_PATH" "$ALGORITHM" "$POPSIZE" "$NUM_GENERATIONS" "$TIMEOUT" "$OUTPUT"
done

