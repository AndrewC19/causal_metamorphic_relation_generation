#!/bin/bash
##SBATCH --ntasks=1
##SBATCH --time=01:00:00
##SBATCH --mem-per-cpu=4000
#export SLURM_EXPORT_ENV=ALL
#module load Anaconda3/5.3.0
#
## We assume that the conda environment 'venv' has already been created
#source activate venv

cd $1
mkdir "t${2}"
cp mutation_config.toml "./t${2}/mutation_config.toml"
cd "t${2}"
#rm *.sqlite report.html *.json
sed -i '' -e "s/-t.*/-t $2\"/" mutation_config.toml
cosmic-ray init ./mutation_config.toml mutation_config.sqlite
cosmic-ray --verbosity=INFO baseline ./mutation_config.toml
cosmic-ray exec ./mutation_config.toml mutation_config.sqlite
python ../../../../../../result_cleanup.py -r . -db mutation_config.sqlite -o results.json
