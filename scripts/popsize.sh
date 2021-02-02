#! /usr/bin/env bash

export MHPCPROJECT_ROOT=/scratch/$USER/MHPC-project

cd "$MHPCPROJECT_ROOT" || exit
mkdir -p "slurm_outputs"

SITE=testbed
TIMEOUT=150
PARAMETERS_PATH="$MHPCPROJECT_ROOT/data/parameters/testbed.csv"
ALGORITHM=NGO
NUM_GENERATIONS=8
REPETITIONS=16
NUM_NODES=16
TIME=4:00:00
PARTITION=regular2
OUTPUT="$MHPCPROJECT_ROOT/runs/popsize"

echo "==== Submitting testbed calibration popsize scaling jobs ===="
for POPSIZE in 1 2 4 8 12 16 20 24 28 32
do
  for n in $(seq $REPETITIONS)
  do
    sbatch -p "$PARTITION" -J "popsize_$POPSIZE" -N "$NUM_NODES" -t "$TIME" --output "slurm_outputs/%x-%j.out" \
      ./scripts/run.slurm "$SITE" "$PARAMETERS_PATH" "$ALGORITHM" "$((32 * POPSIZE))" "$NUM_GENERATIONS" "$TIMEOUT" "$OUTPUT"
  done
done

