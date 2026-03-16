UV = uv
PYTHON = $(UV) run python

all: run

run: $(PYTHON) -m fly
	@$(PYTHON) -m main

debug: $(PYTHON) -m pdb -m fly
	@$(PYTHON) -m pdb -m main

lint: $(PYTHON) -m black --check src
	@$(PYTHON) -m flake8 main
	@$(PYTHON) -m mypy main \
		--warn-return-any \
		--warn-unused-ignores \
		--ignore-missing-imports \
		--disallow-untyped-defs \
		--check-untyped-defs
clean:
	@rm -rf .mypy_cache
	@find . -type d -name "__pycache__" -exec rm -rf {} +

fclean: clean
	@rm -rf $(VENV_DIR) $(INSTALLED_FLAG)