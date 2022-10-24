#!/bin/bash
#SBATCH --ntasks=1
#SBATCH --time=5:00:00
#SBATCH --mem-per-cpu=4000
export SLURM_EXPORT_ENV=ALL
module load Anaconda3/5.3.0

# We assume that the conda environment 'venv' has already been created
source activate venv

find "${1}/dags" -maxdepth 1 -mindepth 1 -type d | xargs -I {} bash run.sh "{}" $2
python process_seed_results.py -s $1 -r "t${2}/results.json" -t $2
find "${1}/dags" -maxdepth 1 -mindepth 1 -type d | xargs -I {} rm -r "{}/t${2}"
