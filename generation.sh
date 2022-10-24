#!/bin/bash
#SBATCH --ntasks=1
#SBATCH --time=01:00:00
#SBATCH --mem-per-cpu=1000
export SLURM_EXPORT_ENV=ALL
module load Anaconda3/5.3.0

# We assume that the conda environment 'venv' has already been created
source activate venv
for nn in {30,}
do
  for pe in {0.25,}
  do
    for pc in {0.25,0.5,0.75,1}
    do
      pep=$(bc <<< "$pe*100/1")
      pcp=$(bc <<< "$pc*100/1")
      srun python evaluation.py -nd $1 -nn $nn -pe $pe -pc $pc -en "evaluation/nn_${nn}_pe_${pep}_pc_${pcp}"
    done
  done
done
