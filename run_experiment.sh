#!/bin/bash

for experiment in evaluation/*/; do
  for tests in {1,5}; do
    bash run_seeds.sh $experiment $tests
  done
done
