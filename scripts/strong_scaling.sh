#! /usr/bin/env bash

export MHPCPROJECT_ROOT=/scratch/$USER/MHPC-project

cd "$MHPCPROJECT_ROOT" || exit
mkdir -p "slurm_outputs"

SITE=testbed
TIMEOUT=150
PARAMETERS_PATH="$MHPCPROJECT_ROOT/data/parameters/testbed.csv"
ALGORITHM=NGO
POPSIZE=512
NUM_GENERATIONS=8
REPETITIONS=16
OUTPUT="$MHPCPROJECT_ROOT/runs/strong_scaling"

echo "==== Submitting testbed calibration strong scaling jobs ===="
for NUM_NODES in 32 28 24 20 16 12 8 4 2 1
do
  if [[ $NUM_NODES -eq 1 ]]
  then
    PARTITION=regular2
    TIME=12:00:00
  elif [[ $NUM_NODES -eq 2 ]]
  then
    PARTITION=regular2
    TIME=6:00:00
  elif [[ $NUM_NODES -eq 4 ]]
  then
    PARTITION=regular2
    TIME=3:00:00
  elif [[ $NUM_NODES -eq 8 ]]
  then
    PARTITION=regular2
    TIME=2:00:00
  elif [[ $NUM_NODES -le 16 ]]
  then
    PARTITION=regular2
    TIME=1:30:00
  else
    PARTITION=wide2
    TIME=1:30:00
  fi
  for n in $(seq $REPETITIONS)
  do
    sbatch -p "$PARTITION" -J "strong_scaling_$NUM_NODES" -N "$NUM_NODES" -t "$TIME" --output "slurm_outputs/%x-%j.out" \
      ./scripts/run.slurm "$SITE" "$PARAMETERS_PATH" "$ALGORITHM" "$POPSIZE" "$NUM_GENERATIONS" "$TIMEOUT" "$OUTPUT"
  done
done

