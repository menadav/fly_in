VENV_NAME = .venv
PYTHON = $(VENV_NAME) run python
PIP = $(PYTHON) -m pip
REQ_FILE = requirements.txt
MAIN_FILE = fly_in.py


all: install run

$(VENV_NAME):
	python3 -m venv $(VENV_NAME)
	$(PIP) install --upgrade pip

install: $(VENV_NAME)
	$(PIP) install -r $(REQ_FILE)
	$(PIP) install flake8 mypy pytest
	@touch $(VENV_NAME)

run: $(VENV_NAME)
	$(PYTHON) $(MAIN_FILE)

debug: $(VENV_NAME)
	$(PYTHON) -m pdb $(MAIN_FILE)

lint: $(VENV_NAME)
	@$(PYTHON) -m flake8 main
	@$(PYTHON) -m mypy main \
		--warn-return-any \
		--warn-unused-ignores \
		--ignore-missing-imports \
		--disallow-untyped-defs \
		--check-untyped-defs
clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	rm -rf .mypy_cache .pytest_cache $(VENV_NAME)

.PHONY: all run clean lint
