#! /usr/bin/env bash

ALGORITHM=$1
POPSIZE=$2
NUM_GENERATIONS=$3
TIMEOUT=$4
NUM_NODES=$5
TIME=$6

export MHPCPROJECT_ROOT=/scratch/$USER/MHPC-project
export PYTHONPATH=$MHPCPROJECT_ROOT
export DASK_CONFIG=$MHPCPROJECT_ROOT/config/dask

cd "$MHPCPROJECT_ROOT" || exit
for SITE in DOMEF DOMES DOPAS Kaltern Latsch "Matsch B2" "Matsch P2" NEPAS
do
  sbatch -J "$SITE" -N "$NUM_NODES" -t "$TIME" \
    ./scripts/calibration "$SITE" \
    "$ALGORITHM" "$POPSIZE" "$NUM_GENERATIONS" "$TIMEOUT" \
    "/scratch/$USER/MHPC-project_outputs"
done
