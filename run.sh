#!/bin/bash

cd $1
mkdir "t${2}"
cp mutation_config.toml "./t${2}/mutation_config.toml"
cp ../../program.py "./t${2}/program.py"
cd "t${2}"
#rm *.sqlite report.html *.json
sed -i '' -e "s/-t.*/-t $2\"/" mutation_config.toml
cosmic-ray init ./mutation_config.toml mutation_config.sqlite
cosmic-ray --verbosity=INFO baseline ./mutation_config.toml
cosmic-ray exec ./mutation_config.toml mutation_config.sqlite
python ../../../../../../result_cleanup.py -r . -db mutation_config.sqlite -o results.json
