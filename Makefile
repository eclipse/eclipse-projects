# SPDX-License-Identifier: MIT
VENV := .venv
BIN := $(VENV)/bin

.PHONY: init data build serve clean

# Create the virtualenv and install the site dependencies.
init:
	python3 -m venv $(VENV)
	$(BIN)/pip install -r requirements.txt

# Fetch the project list from the PMI API into docs/projects.csv.
data:
	$(BIN)/python .github/workflows/generate.py

build: data
	$(BIN)/mkdocs build

serve: data
	$(BIN)/mkdocs serve

clean:
	rm -rf _site docs/projects.csv
