#!/bin/bash

for seed in $1/*/; do   
  sbatch run_dags.sh $seed $2
done
