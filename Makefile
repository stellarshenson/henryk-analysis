.PHONY: clean data lint requirements sync_data_to_s3 sync_data_from_s3 test

#################################################################################
# GLOBALS                                                                       #
#################################################################################

PROJECT_DIR := $(shell dirname $(realpath $(lastword $(MAKEFILE_LIST))))
BUCKET = [OPTIONAL] your-bucket-for-syncing-data (do not include 's3://')
PROFILE = default
PROJECT_NAME = henryk-analysis
MODULE_NAME = lib_henryk
PYTHON_INTERPRETER = python3

ifeq (,$(shell which conda))
HAS_CONDA=False
else
HAS_CONDA=True
endif

PYTHON3_VERSION=3.11


#################################################################################
# COMMANDS                                                                      #
#################################################################################

## Install Python Dependencies
requirements: test_environment
	$(PYTHON_INTERPRETER) -m pip install -U pip setuptools wheel
	$(PYTHON_INTERPRETER) -m pip install -r requirements.txt

## Make Dataset
data: requirements
	$(PYTHON_INTERPRETER) src/lib_henryk/data/make_dataset.py data/raw data/processed

## Delete all compiled Python files
clean:
	@echo "removing cache and compiled files"
	@find . -type f -name "*.py[co]" -delete
	@find . -type d -name "__pycache__" -delete
	@rm -rf `find . -type d -name "*.egg-info"`
	@echo "removing dist and build directory"
	@rm -rf build dist
	@echo 'uninstalling local library'
	@pip uninstall -y $(MODULE_NAME)

## Lint using flake8
lint:
	flake8 src

## Run python tests
test:
	@echo "executing python tests"
	pytest -v

## Upload Data to S3
sync_data_to_s3:
ifeq (default,$(PROFILE))
	aws s3 sync data/ s3://$(BUCKET)/data/
else
	aws s3 sync data/ s3://$(BUCKET)/data/ --profile $(PROFILE)
endif

## Download Data from S3
sync_data_from_s3:
ifeq (default,$(PROFILE))
	aws s3 sync s3://$(BUCKET)/data/ data/
else
	aws s3 sync s3://$(BUCKET)/data/ data/ --profile $(PROFILE)
endif


## Set up python interpreter environment
create_environment:
ifeq (True,$(HAS_CONDA))
	@echo ">>> Detected conda, creating conda environment."
	conda create -y --name $(PROJECT_NAME) python=$(PYTHON3_VERSION) ipykernel
	conda env update -n $(PROJECT_NAME) --no-capture-output -f ./environment.yml
	@echo ">>> New conda env created. Activate with:\nconda activate $(PROJECT_NAME)"
else
	$(PYTHON_INTERPRETER) -m pip install -q virtualenv virtualenvwrapper
	@echo ">>> Installing virtualenvwrapper if not already installed.\nMake sure the following lines are in shell startup file\n\
	export WORKON_HOME=$$HOME/.virtualenvs\nexport PROJECT_HOME=$$HOME/Devel\nsource /usr/local/bin/virtualenvwrapper.sh\n"
	@bash -c "source `which virtualenvwrapper.sh`;mkvirtualenv $(PROJECT_NAME) --python=$(PYTHON_INTERPRETER)"
	@echo ">>> New virtualenv created. Activate with:\nworkon $(PROJECT_NAME)"
endif

## Remove previously created environment
remove_environment:
ifeq (True,$(HAS_CONDA))
	@echo ">>> Detected conda, removing conda environment."
	conda env remove -y -n $(PROJECT_NAME)
endif

## Test python environment is setup correctly
test_environment:
	$(PYTHON_INTERPRETER) test_environment.py

#################################################################################
# PROJECT RULES                                                                 #
#################################################################################

## print project libraries used by the scripts 
list_requirements:
	# get list of immediate requirements
	@pipreqs --mode no-pin --print | tr -cd '[:alnum:].[:space:]._-' | uniq > pipreqs.tmp
	# add pipreqs to the list (to make it possible to run virtual env)
	@echo 'pipreqs' >> pipreqs.tmp
	# list all pip packages along their version
	@pip list --format=freeze > pipfreeze.tmp
	# join the reqs and the pip list
	@awk -F"==" 'FNR==NR {dict[$$1]=$$1; next} {if (dict[$$1] != "") print $$0}' pipreqs.tmp pipfreeze.tmp
	@rm pipfreeze.tmp pipreqs.tmp

## saves conda environment to environment.yml
save_environment:
	# saving environment to environment.yml ...
	@conda env export > environment.yml
	# updating the requirements.txt file ...
	@cat environment.yml \
		| awk '/pip:/,EOF' \
		| grep --invert-match 'pip:' \
		| grep --invert-match 'prefix:' \
		| sed 's/^ *- //g' > requirements.txt
	@echo "saved" `cat requirements.txt | awk 'END{print NR}'` "packages" 


## Install src modules folder and its dependencies
install:
	@pip install --editable .
	@echo "you can now import '$(MODULE_NAME)' module in your notebooks and scripts"


## Install src modules without dependencies
install_no_dependencies:
	@pip install --no-dependencies --editable .
	@echo "you can now import '$(MODULE_NAME)' module in your notebooks and scripts"


## Install project and dependencies in the current environment
install_all:
	# install requirements
	@conda env update -f ./environment.yml
	@echo "project deployment dependencies have been installed"
	@echo "you can now import '$(MODULE_NAME)' module in your notebooks and scripts"


## Build package & install
build: test
	python -m build --wheel
	@echo "installing project library: $(find ./dist -name '*.whl')"
	@pip install `find ./dist -name '*.whl'`

#################################################################################
# Self Documenting Commands                                                     #
#################################################################################

.DEFAULT_GOAL := help

# Inspired by <http://marmelab.com/blog/2016/02/29/auto-documented-makefile.html>
# sed script explained:
# /^##/:
# 	* save line in hold space
# 	* purge line
# 	* Loop:
# 		* append newline + line to hold space
# 		* go to next line
# 		* if line starts with doc comment, strip comment character off and loop
# 	* remove target prerequisites
# 	* append hold space (+ newline) to line
# 	* replace newline plus comments by `---`
# 	* print line
# Separate expressions are necessary because labels cannot be delimited by
# semicolon; see <http://stackoverflow.com/a/11799865/1968>
.PHONY: help

## prints the list of available commands
help:
	@echo ""
	@echo "$$(tput bold)Available rules:$$(tput sgr0)"
	@sed -n -e "/^## / { \
		h; \
		s/.*//; \
		:doc" \
		-e "H; \
		n; \
		s/^## //; \
		t doc" \
		-e "s/:.*//; \
		G; \
		s/\\n## /---/; \
		s/\\n/ /g; \
		p; \
	}" ${MAKEFILE_LIST} \
	| LC_ALL='C' sort --ignore-case \
	| awk -F '---' \
		-v ncol=$$(tput cols) \
		-v indent=19 \
		-v col_on="$$(tput setaf 6)" \
		-v col_off="$$(tput sgr0)" \
	'{ \
		printf "%s%*s%s ", col_on, -indent, $$1, col_off; \
		n = split($$2, words, " "); \
		line_length = ncol - indent; \
		for (i = 1; i <= n; i++) { \
			line_length -= length(words[i]) + 1; \
			if (line_length <= 0) { \
				line_length = ncol - indent - length(words[i]) - 1; \
				printf "\n%*s ", -indent, " "; \
			} \
			printf "%s ", words[i]; \
		} \
		printf "\n"; \
	}' 
	@echo ""


# EOF
