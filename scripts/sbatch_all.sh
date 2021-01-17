#! /usr/bin/env bash

export MHPCPROJECT_ROOT=/scratch/$USER/MHPC-project
export PYTHONPATH=$MHPCPROJECT_ROOT
export DASK_CONFIG=$MHPCPROJECT_ROOT/config/dask

TIMEOUT=180
REPETITIONS=3
OUTPUT="$MHPCPROJECT_ROOT/runs"

cd "$MHPCPROJECT_ROOT" || exit
for ALGORITHM in NGO PSO Random
do
  for POPSIZE in 64 128 256 512
  do
    for NUM_GENERATIONS in 8 16 32 64
    do
      for NUM_NODES in 4 8 12 16 20 24 28 32
      do
        for SITE in DOMEF DOMES DOPAS Kaltern Latsch "Matsch B2" "Matsch P2" NEPAS
        do
          SECONDS=$((60 * NUM_GENERATIONS * POPSIZE / NUM_NODES))
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
            TIME=$(date -d@$SECONDS -u "+%H:%M:%S")
            for n in $(seq $REPETITIONS)
            do
              sbatch -p "$PARTITION" -J "$SITE" -N "$NUM_NODES" -t "$TIME" \
                ./scripts/run.slurm "$SITE" "$ALGORITHM" "$POPSIZE" "$NUM_GENERATIONS" "$TIMEOUT" "$OUTPUT"
            done
          fi
        done
      done
    done
  done
done
