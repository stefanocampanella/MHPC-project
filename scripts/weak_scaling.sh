#! /usr/bin/env bash

export MHPCPROJECT_ROOT=/scratch/$USER/MHPC-project

cd "$MHPCPROJECT_ROOT" || exit
mkdir -p "slurm_outputs"

SITE=testbed
TIMEOUT=150
PARAMETERS_PATH="$MHPCPROJECT_ROOT/data/parameters/testbed.csv"
ALGORITHM=NGO
NUM_GENERATIONS=8
REPETITIONS=8
TIME=1:30:00
OUTPUT="$MHPCPROJECT_ROOT/runs/weak_scaling"

echo "==== Submitting testbed calibration weak scaling jobs ===="
for NUM_NODES in 1 2 4 8 12 16 20 24 28 32
do
  if [[ $NUM_NODES -le 16 ]]
  then
    PARTITION=regular2
  else
    PARTITION=wide2
  fi
  for n in $(seq $REPETITIONS)
  do
    POPSIZE=$((32 * NUM_NODES))
    sbatch -p "$PARTITION" -J "weak_scaling_$NUM_NODES" -N "$NUM_NODES" -t "$TIME" --output "slurm_outputs/%x-%j.out" \
      ./scripts/run.slurm "$SITE" "$PARAMETERS_PATH" "$ALGORITHM" "$POPSIZE" "$NUM_GENERATIONS" "$TIMEOUT" "$OUTPUT"
  done
done

