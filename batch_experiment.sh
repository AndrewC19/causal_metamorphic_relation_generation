#!/bin/bash

for experiment in evaluation/*/; do
  for seed in $experiment/*/; do
    find run.sh "${seed}/dags" -maxdepth 1 -mindepth 1 -type d | xargs -I {} sbatch run.sh "{}" $1
  done
done
