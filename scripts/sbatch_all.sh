#! /usr/bin/env bash

ALGORITHM=$1
POPSIZE=$2
NUM_GENERATIONS=$3
TIMEOUT=$4
PARTITION=$5
NUM_NODES=$6
TIME=$7

export MHPCPROJECT_ROOT=/scratch/$USER/MHPC-project
export PYTHONPATH=$MHPCPROJECT_ROOT
export DASK_CONFIG=$MHPCPROJECT_ROOT/config/dask

cd "$MHPCPROJECT_ROOT" || exit
for SITE in DOMEF DOMES DOPAS Kaltern Latsch "Matsch B2" "Matsch P2" NEPAS
do
  sbatch -p "$PARTITION" -J "$SITE" -N "$NUM_NODES" -t "$TIME" \
    ./scripts/run.slurm "$SITE" \
    "$ALGORITHM" "$POPSIZE" "$NUM_GENERATIONS" "$TIMEOUT" \
    "/scratch/$USER/MHPC-project_outputs"
done
