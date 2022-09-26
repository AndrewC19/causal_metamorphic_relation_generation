#!/bin/bash
#SBATCH --ntasks=1
#SBATCH --time=01:00:00
#SBATCH --mem-per-cpu=4000
export SLURM_EXPORT_ENV=ALL
module load Anaconda3/5.3.0

# We assume that the conda environment 'venv' has already been created
source activate venv

cd $1
rm *.sqlite report.html *.json
sed -i '' -e "s/-t.*/-t $2\"/" mutation_config.toml
cosmic-ray init ./mutation_config.toml ./mutation_config_t${2}.sqlite
cosmic-ray --verbosity=INFO baseline ./mutation_config.toml
cosmic-ray exec ./mutation_config.toml ./mutation_config_t${2}.sqlite
python ../../../../../result_cleanup.py -r . -db mutation_config_t${2}.sqlite -o results_t${2}.json
#python ../../../../../process_seed_results.py -s ../../ -r results_t${2}
