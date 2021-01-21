#! /usr/bin/env bash

export MHPCPROJECT_ROOT=/scratch/$USER/MHPC-project
export PYTHONPATH=$MHPCPROJECT_ROOT
export DASK_CONFIG=$MHPCPROJECT_ROOT/config/dask

cd "$MHPCPROJECT_ROOT" || exit
mkdir -p "slurm_outputs"

echo "==== Submitting test jobs ===="
SITE=testbed
TIMEOUT=180
PARAMETERS_PATH="$MHPCPROJECT_ROOT/data/parameters/testbed.csv"
ALGORITHM=NGO
POPSIZE=64
NUM_GENERATIONS=8
OUTPUT="$MHPCPROJECT_ROOT/runs/scaling"
for NUM_NODES in  4 8 16 32
do
  if [[ $NUM_NODES -eq 2 ]]
  then
    PARTITION=regular2
    TIME=6:00:00
  elif [[ $NUM_NODES -eq 4 ]]
  then
    PARTITION=regular2
    TIME=3:00:00
  elif [[ $NUM_NODES -le 16 ]]
  then
    PARTITION=regular2
    TIME=1:30:00
  else
    PARTITION=wide2
    TIME=1:30:00
  fi
  sbatch -p "$PARTITION" -J "scaling_$SITE" -N "$NUM_NODES" -t "$TIME" \
         -o "slurm_outputs/%x-%j.out"  -e "slurm_outputs/%x-%j.err" \
    ./scripts/run.slurm "$SITE" "$PARAMETERS_PATH" "$ALGORITHM" "$POPSIZE" "$NUM_GENERATIONS" "$TIMEOUT" "$OUTPUT"
done

