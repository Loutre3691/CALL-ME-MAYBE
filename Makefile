PYTHON = python3
UV = uv
SRC = src

run:
	uv run $(PYTHON) -m $(SRC)

install:
	uv sync

debug:
	@uv run $(PYTHON) -m pdb -m $(SRC) 

clean:
	@find . -type d -name "__pycache__" -exec rm -rf {} +
	@find . -name "*.pyc" -delete
	@rm -rf .mypy_cache
	@echo "all is clear"

lint:
	@uv run $(PYTHON) -m flake8 . --exclude=venv,.venv,.mypy_cache,__pycache__,llm_sdk
	@uv run $(PYTHON) -m mypy . --warn-unused-ignores --warn-return-any --exclude '(venv|llm_sdk)' --ignore-missing-imports --disallow-untyped-defs --check-untyped-defs

lint-strict:
	@uv run $(PYTHON) -m flake8 . --exclude=venv,.venv,.mypy_cache,__pycache__,llm_sdk
	@uv run $(PYTHON) -m mypy . --exclude '(venv|llm_sdk)' --strict

.PHONY: run install debug clean lint lint-strict