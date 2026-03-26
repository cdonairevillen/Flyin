#Config
PYTHON      := python3
VENV        := .venv
VENV_BIN    := $(VENV)/bin
PIP         := $(VENV_BIN)/pip
PY          := $(VENV_BIN)/python

REQ         := requirements/requirements.txt
DEPS_STAMP	:= $(VENV)/.deps_installed

MYPY_FLAGS  := --warn-return-any \
			   --warn-unused-ignores \
			   --ignore-missing-imports \
			   --disallow-untyped-defs \
			   --check-untyped-defs


# Rules
all: run

$(VENV_BIN)/activate:
	$(PYTHON) -m venv $(VENV)

$(DEPS_STAMP): $(VENV_BIN)/activate $(REQ)
	$(PIP) install --upgrade pip
	$(PIP) install --no-cache-dir -r $(REQ)

deps: $(DEPS_STAMP)

run: deps
	$(PY) main.py

debug: deps
	$(PY) -m pdb main.py

lint: deps
	$(PY) -m flake8 . --exclude .venv
	$(PY) -m mypy . $(MYPY_FLAGS) --exclude .venv

lint-strict: deps
	$(PY) -m flake8 . --exclude .venv
	$(PY) -m mypy . --strict $(MYPY_FLAGS) --exclude .venv

clean:
	rm -rf $(VENV)
	rm -rf .pytest_cache
	rm -rf .mypy_cache
	rm -rf dist
	rm -rf output.txt
	find . -type d -name "__pycache__" -exec rm -rf {} +

re: clean run

help:
	@echo "make run          -> Run project"
	@echo "make deps         -> Install dependencies"
	@echo "make lint         -> Run linters"
	@echo "make clean        -> Clean project"

.PHONY: all deps run debug clean lint lint-strict help re