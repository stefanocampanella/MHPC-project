#! /usr/bin/env bash

export MHPCPROJECT_ROOT=/scratch/$USER/MHPC-project

cd "$MHPCPROJECT_ROOT" || exit
mkdir -p "slurm_outputs"

TIMEOUT=150
PARAMETERS_PATH="$MHPCPROJECT_ROOT/data/parameters/all.csv"
ALGORITHM=NGO
POPSIZE=1024
NUM_GENERATIONS=32
PARTITION=wide2
NUM_NODES=32
TIME=8:00:00
OUTPUT="$MHPCPROJECT_ROOT/runs/full"

echo "==== Submitting all-sites calibration of full set of parameters jobs ===="
for SITE in DOMEF DOMES DOPAS Kaltern Latsch "Matsch B2" "Matsch P2" NEPAS
do
  sbatch -p "$PARTITION" -J "all_$SITE" -N "$NUM_NODES" -t "$TIME"  --output "slurm_outputs/%x-%j.out" \
    ./scripts/run.slurm "$SITE" "$PARAMETERS_PATH" "$ALGORITHM" "$POPSIZE" "$NUM_GENERATIONS" "$TIMEOUT" "$OUTPUT"
done