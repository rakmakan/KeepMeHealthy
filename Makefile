PYTHON ?= python

.PHONY: install dev lint format type test run

install:
	$(PYTHON) -m pip install --upgrade pip
	$(PYTHON) -m pip install .

dev:
	$(PYTHON) -m pip install -e ".[dev]"

lint:
	ruff check .

format:
	ruff format .

type:
	mypy .

test:
	pytest

run:
	streamlit run app.py
