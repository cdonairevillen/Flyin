#Config
PYTHON      := python3
VENV        := .venv
VENV_BIN    := $(VENV)/bin
PIP         := $(VENV_BIN)/pip
PY          := $(VENV_BIN)/python

REQ         := requirements/requirements.txt
INSTALL_STAMP	:= $(VENV)/.deps_installed

MYPY_FLAGS  := --warn-return-any \
			   --warn-unused-ignores \
			   --ignore-missing-imports \
			   --disallow-untyped-defs \
			   --check-untyped-defs


# Rules
all: run

$(VENV_BIN)/activate:
	$(PYTHON) -m venv $(VENV)

$(INSTALL_STAMP): $(VENV_BIN)/activate $(REQ)
	$(PIP) install --upgrade pip
	$(PIP) install --no-cache-dir -r $(REQ)

install: $(INSTALL_STAMP)

run: install
	$(PY) main.py

debug: install
	$(PY) -m pdb main.py

lint: install
	$(PY) -m flake8 . --exclude .venv
	$(PY) -m mypy . $(MYPY_FLAGS) --exclude .venv

lint-strict: install
	$(PY) -m flake8 . --exclude .venv
	$(PY) -m mypy . --strict $(MYPY_FLAGS) --exclude .venv

clean:
	rm -rf $(VENV)
	rm -rf .pytest_cache
	rm -rf .mypy_cache
	rm -rf dist
	find . -type d -name "__pycache__" -exec rm -rf {} +

re: clean run

help:
	@echo "make run          -> Run project"
	@echo "make install         -> Install dependencies"
	@echo "make lint         -> Run linters"
	@echo "make clean        -> Clean project"

.PHONY: all install run debug clean lint lint-strict help re