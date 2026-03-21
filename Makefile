VENV_NAME = .venv
PYTHON = $(VENV_NAME)/bin/python3
PIP = $(PYTHON) -m pip
REQ_FILE = requirements.txt
MAP ?=  maps/easy/01_linear_path.txt
MAIN_FILE = fly_in.py
MAIN_M = fly_in

.PHONY: all install run debug lint clean

all: install run

$(VENV_NAME):
	python3 -m venv $(VENV_NAME)
	$(PIP) install --upgrade pip

install: $(VENV_NAME)
	$(PIP) install -r $(REQ_FILE)
	$(PIP) install flake8 mypy pytest
	@touch $(VENV_NAME)

run: $(VENV_NAME)
	@$(PYTHON) $(MAIN_FILE) $(MAP)

debug: $(VENV_NAME)
	@$(PYTHON) -m pdb $(MAIN_FILE)

clean:
	@find . -type d -name "__pycache__" -exec rm -rf {} +
	@rm -rf .mypy_cache .pytest_cache $(VENV_NAME)

lint: $(VENV_NAME)
	@$(PYTHON) -m flake8 --exclude=$(VENV_NAME) $(MAIN_FILE) src
	@$(PYTHON) -m mypy $(MAIN_FILE) src \
		--explicit-package-bases\
		--warn-return-any \
		--warn-unused-ignores \
		--ignore-missing-imports \
		--disallow-untyped-defs \
		--check-untyped-defs
