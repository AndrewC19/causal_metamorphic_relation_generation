rm *.sqlite report.html
cosmic-ray init ./mutation_config.toml ./mutation_config.sqlite
cosmic-ray --verbosity=INFO baseline ./mutation_config.toml
cosmic-ray exec ./mutation_config.toml ./mutation_config.sqlite
cr-html ./mutation_config.sqlite > report.html
