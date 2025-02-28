.PHONY: clean data lint requirements build sync_data_to_s3 sync_data_from_s3 sync test

#################################################################################
# GLOBALS                                                                       #
#################################################################################

PROJECT_DIR := $(shell dirname $(realpath $(lastword $(MAKEFILE_LIST))))
BUCKET = [OPTIONAL] your-bucket-for-syncing-data (do not include 's3://')
PROFILE = default
PROJECT_NAME = henryk-analysis
MODULE_NAME = lib_henryk
CONDA_FLAGS= --no-capture-output
CONDA_ENV_NAME = henryk
PYTHON_INTERPRETER = python3
PYTHON3_VERSION= 3.11

#################################################################################
# TESTS                                                                         #
#################################################################################

# styles and colors
MSG_PREFIX = \033[1m\033[36m>>>\033[0m
WARN_PREFIX = \033[33m>>>\033[0m
ERR_PREFIX = \033[31m>>>\033[0m
WARN_STYLE = \033[33m
ERR_STYLE = \033[31m
HIGHLIGHT_STYLE = \033[1m\033[94m
OK_STYLE = \033[92m
NO_STYLE = \033[0m

# additional settings
CLEAN_REMOVES_LIBRARY = False

# checks if conda is present
ifeq (,$(shell which conda))
HAS_CONDA=False
else
HAS_CONDA=True
endif

# checks if environment was installed
ifeq (,$(shell conda env list | grep $(PROJECT_NAME)))
HAS_CONDA_ENV=False
else
HAS_CONDA_ENV=True
endif


#################################################################################
# COMMANDS                                                                      #
#################################################################################

## Install Python Dependencies
requirements: test_environment check_conda
	@echo "${MSG_PREFIX} installing requirements for  ${HIGHLIGHT_STYLE}${CONDA_ENV_NAME}${NO_STYLE} environment"
	conda run --name ${CONDA_ENV_NAME} ${CONDA_FLAGS} $(PYTHON_INTERPRETER) -m pip install -U pip setuptools wheel
	conda run --name ${CONDA_ENV_NAME} ${CONDA_FLAGS} $(PYTHON_INTERPRETER) -m pip install -r requirements.txt

## Make Dataset
data: requirements check_conda
	@echo "${MSG_PREFIX} generating dataset"
	conda run --name ${CONDA_ENV_NAME} ${CONDA_FLAGS} $(PYTHON_INTERPRETER) src/${MODULE_NAME}/data/make_dataset.py data/raw data/processed

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

## Upload runtime data to s3
sync: 
	@echo "${MSG_PREFIX} sync artifacts and models to s3"
ifeq (default,$(PROFILE))
	aws s3 rm s3://$(BUCKET)/artifacts/ --recursive --include='*'
	aws s3 sync models/ s3://$(BUCKET)/models/
	aws s3 sync artifacts s3://$(BUCKET)/artifacts/
else
	aws s3 rm s3://$(BUCKET)/artifacts/ --recursive --include='*' --profile $(PROFILE)
	aws s3 sync models/ s3://$(BUCKET)/models/ --profile $(PROFILE)
	aws s3 sync artifacts s3://$(BUCKET)/artifacts/ --profile $(PROFILE)
endif


# Set up python interpreter environment
create_environment: check_conda
ifeq (True,$(HAS_CONDA))
	@echo "${MSG_PREFIX} detected conda. Checking if environment ${CONDA_ENV_NAME} exists."
	@if conda info --envs | grep -q "^${CONDA_ENV_NAME}"; then \
		echo "${MSG_PREFIX} conda environment ${CONDA_ENV_NAME} already exists. Skipping creation."; \
	else \
		echo "${MSG_PREFIX} creating new conda environment ${HIGHLIGHT_STYLE}${CONDA_ENV_NAME}${NO_STYLE}"; \
		conda create -y --name ${CONDA_ENV_NAME} python=${PYTHON3_VERSION}; \
		conda env update --name ${CONDA_ENV_NAME} -f environment.yml; \
 		echo "${MSG_PREFIX} new conda env created successfully. Activate with: ${HIGHLIGHT_STYLE}conda activate ${CONDA_ENV_NAME}${NO_STYLE}"; \
	        conda run --name ${CONDA_ENV_NAME} ${CONDA_FLAGS} nbdime config-git --enable --global; \
 		echo "${MSG_PREFIX} environment ${CONDA_ENV_NAME} was configured to integrate git with jupyter notebooks"; \
	fi
endif

## Remove previously created environment
remove_environment: check_conda
ifeq (True,$(HAS_CONDA))
	@echo "${MSG_PREFIX} detected conda, removing ${HIGHLIGHT_STYLE}${CONDA_ENV_NAME}${NO_STYLE} conda environment."
	conda run --name base conda env remove -y -n ${CONDA_ENV_NAME}
endif

# check conda
check_conda:
ifeq (False,$(HAS_CONDA))
	@echo "${ERR_PREFIX} ${ERR_STYLE}ERROR: conda not installed${NO_STYLE}"
	@echo "${ERR_PREFIX} ${ERR_STYLE}install anaconda or miniforge from https://github.com/conda-forge/miniforge${NO_STYLE}"
	@exit 1
endif


## Test python environment is setup correctly
test_environment: check_conda
	@echo "${MSG_PREFIX} testing environment ${HIGHLIGHT_STYLE}${CONDA_ENV_NAME}${NO_STYLE} if ready"
	conda run --name ${CONDA_ENV_NAME} ${CONDA_FLAGS} $(PYTHON_INTERPRETER) test_environment.py

#################################################################################
# PROJECT RULES                                                                 #
#################################################################################

## Delete all compiled Python files
clean: check_conda
	@echo "${MSG_PREFIX} removing cache and compiled files"
	@find . -type f -name "*.py[co]" -delete
	@find . -type d -name '__pycache__' -exec rm -r {} +
	@find . -type d -name '*.egg-info'  -exec rm -r {} +
	@find . -type d -name '.ipynb_checkpoints' -exec rm -r {} +
	@find . -type d -name '.pytest_cache' -exec rm -r {} +
	@echo "${MSG_PREFIX} removing dist and build directory"
	@rm -rf build dist
ifeq (True,$(CLEAN_REMOVES_LIBRARY))
	@echo "${MSG_PREFIX} uninstalling ${MODULE_NAME} library"
	@conda run --name ${CONDA_ENV_NAME} ${CONDA_FLAGS} pip uninstall -y $(MODULE_NAME) || true
endif

## Install src modules without dependencies
install: check_conda clean create_environment
	@echo "${MSG_PREFIX} installing ${MODULE_NAME} in the ${CONDA_ENV_NAME} environment ${OK_STYLE}EDITABLE${NO_STYLE}"
	@conda run --name ${CONDA_ENV_NAME} ${CONDA_FLAGS} pip install --editable .
	@echo "${MSG_PREFIX} fixing issues with jupyterlab 'jump to definition' by installing package in (base)"
	@conda run --name base pip install --no-dependencies --editable .
	@echo "${MSG_PREFIX} you can now import ${HIGHLIGHT_STYLE}$(MODULE_NAME)${NO_STYLE} module in your notebooks and scripts\n"

## Build package & install
build: check_conda pyproject.toml install test increment_build_number
	@echo "${MSG_PREFIX} building ${MODULE_NAME}" 
	@conda run --name ${CONDA_ENV_NAME} ${CONDA_FLAGS} ${PYTHON_INTERPRETER} -m build --wheel

# Increment build number
increment_build_number: check_conda
	@echo "${MSG_PREFIX} incrementing build number"
	@conda run --name ${CONDA_ENV_NAME} ${CONDA_FLAGS} ${PYTHON_INTERPRETER} -c "import toml; data=toml.load('pyproject.toml'); ver=data['project']['version'].split('.'); ver[-1]=str(int(ver[-1])+1); data['project']['version']='.'.join(ver); f=open('pyproject.toml','w'); toml.dump(data,f); f.close(); print('New version:',data['project']['version'])"

## Lint using flake8
lint: check_conda
	@echo "${MSG_PREFIX} linting the sourcecode"
	@conda run --name ${CONDA_ENV_NAME} ${CONDA_FLAGS} flake8 src

## Run python tests
test: check_conda
	@echo "${MSG_PREFIX} checking for tests"
	@conda run --name ${CONDA_ENV_NAME} ${CONDA_FLAGS} pytest --collect-only > /dev/null 2>&1; RESULT="$$?"; \
	if [ "$$RESULT" != "5" ]; then \
		echo "${MSG_PREFIX} executing python tests"; \
		conda run --name ${CONDA_ENV_NAME} ${CONDA_FLAGS} pytest -v --cov; \
	else \
		echo "${WARN_PREFIX} ${WARN_STYLE}WARNING: no tests present${NO_STYLE}"; \
	fi

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

