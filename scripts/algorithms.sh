#! /usr/bin/env bash

export MHPCPROJECT_ROOT=/scratch/$USER/MHPC-project

cd "$MHPCPROJECT_ROOT" || exit
mkdir -p "slurm_outputs"

SITE="Matsch B2"
TIMEOUT=150
PARAMETERS_PATH="$MHPCPROJECT_ROOT/data/parameters/all.csv"
POPSIZE=1024
NUM_GENERATIONS=32
PARTITION=wide2
NUM_NODES=32
TIME=8:00:00
OUTPUT="$MHPCPROJECT_ROOT/runs/algorithms"

echo "==== Submitting different algorithms calibration jobs ===="
for ALGORITHM in NGO TwoPointsDE CMA TBPSA PSO ScrHammersleySearchPlusMiddlePoint Random
do
  sbatch -p "$PARTITION" -J "$ALGORITHM" -N "$NUM_NODES" -t "$TIME" --output "slurm_outputs/%x-%j.out" \
    ./scripts/run.slurm "$SITE" "$PARAMETERS_PATH" "$ALGORITHM" "$POPSIZE" "$NUM_GENERATIONS" "$TIMEOUT" "$OUTPUT"
done


