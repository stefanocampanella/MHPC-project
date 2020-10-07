#! /usr/bin/env bash
#SBATCH --partition regular2
#SBATCH --nodes 2
#SBATCH --cpus-per-task 32
#SBATCH --mem-per-cpu 1GB
#SBATCH --exclusive user
#SBATCH --hint nomultithread
#SBATCH --hint compute_bound
#SBATCH --mail-type ALL
#SBATCH --verbose

module load gnu8
spack load python@3.8.3

let "worker_num=(${SLURM_NTASKS} - 1)"
let "total_cores=${SLURM_NTASKS} * ${SLURM_CPUS_PER_TASK}"
port='6379'
ip_head=`hostname`:$port
export ip_head

ROOT=$HOME/MHPC-project
WORKING_DIR=$ROOT/notebooks
OUTPUT_DIR=$WORKING_DIR/outputs

INPUT=$WORKING_DIR/$1.ipynb
OUTPUT=$OUTPUT_DIR/$1_$(date +%F_%H-%M).ipynb
OPTIONS="--no-progress-bar --cwd $WORKING_DIR"
if [[ ! -z "$2" ]]
then
  OPTIONS="$OPTIONS -f $2 -p num_workers total_cores -p address $ip_head "
fi

export NUMEXPR_NUM_THREADS=1
export NUMEXPR_MAX_THREADS=1
export OMP_NUM_THREADS=1

cd $ROOT

srun --nodes=1 --ntasks=1 --cpus-per-task=${SLURM_CPUS_PER_TASK} --nodelist=`hostname` pipenv run ray start --head --dashboard-host 0.0.0.0 --port=$port --num-cpus ${SLURM_CPUS_PER_TASK}
srun --nodes=${worker_num} --ntasks=${worker_num} --cpus-per-task=${SLURM_CPUS_PER_TASK} --exclude=`hostname` pipenv run ray start --address $ip_head --num-cpus ${SLURM_CPUS_PER_TASK}

mkdir -p $OUTPUT_DIR
pipenv run papermill $OPTIONS $INPUT $OUTPUT && \
pipenv run jupyter nbconvert $OUTPUT --to html --output-dir $OUTPUT_DIR && \
rm $OUTPUT 
