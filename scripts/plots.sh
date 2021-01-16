#! /usr/bin/env bash

OUTPUT_DIR=$1
INPUT="${MHPCPROJECT_ROOT}/notebooks/plots.ipynb"

for SITE in DOMES DOMEF DOPAS Kaltern Latsch "Matsch B2" "Matsch P2" NEPAS
do
  MODEL_PATH="${MHPCPROJECT_ROOT}/data/${SITE}/inputs"
  OBSERVATIONS_PATH="${MHPCPROJECT_ROOT}/data/${SITE}/observations/obs.csv"
  mkdir -p "${OUTPUT_DIR}"
  OUTPUT="${OUTPUT_DIR}/${SITE}.ipynb"

  papermill --cwd "${MHPCPROJECT_ROOT}" \
            -p model_path "${MODEL_PATH}" \
            -p observations_path "${OBSERVATIONS_PATH}" \
            "${INPUT}" "${OUTPUT}"

  jupyter nbconvert --to html "${OUTPUT}"

  rm "${OUTPUT}"
done

exit