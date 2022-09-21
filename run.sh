cd $1
rm *.sqlite report.html *.json
sed -i "s/-t.*/-t $2\"/" mutation_config.toml
cosmic-ray init ./mutation_config.toml ./mutation_config.sqlite
cosmic-ray --verbosity=INFO baseline ./mutation_config.toml
cosmic-ray exec ./mutation_config.toml ./mutation_config.sqlite
cr-html ./mutation_config.sqlite > report.html
python ../../../../../result_cleanup.py -r . -o results.json
## echo "[" > mutation_config.json
## cosmic-ray dump mutation_config.sqlite | sed '$!s/$/,/' >> mutation_config.json
## echo "]" >> mutation_config.json
