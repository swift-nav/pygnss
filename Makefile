SHELL := bash
RUN := uv run

PRIMARY_BRANCH := main

SOURCES_TEST := tests
SOURCES_MAIN := gnss

TESTS_PATTERN := $(SOURCES_TEST)/test_*.py

SOURCES := $(SOURCES_MAIN) $(SOURCES_TEST)

SOURCES_TYPE_CHECK := $(SOURCES)
SOURCES_FORMAT_LINT := $(SOURCES)

REPO_NAME ?= $(notdir $(shell git rev-parse --show-toplevel))
TAG_NAME ?= $(shell git describe --tags --always)

install-deps:
ifeq (, $(shell which uv))
	@echo "No uv installation found in current path. Installing..."
	curl -LsSf https://astral.sh/uv/install.sh | sh
else
	@echo "uv installation found. Skipping install."
endif

install:
	uv sync
	uv run pre-commit install

test tests:
	MYPYPATH=src $(RUN) coverage run -m pytest --junitxml=test-results.xml --mypy $(TESTS_PATTERN) -vvv -o log_cli_level=CRITICAL --durations=10
	
test-coverage tests-coverage: test
	$(RUN) coverage xml

test-coverage-html tests-coverage-html: test
	$(RUN) coverage html

type-check:
	$(RUN) mypy $(SOURCES_TYPE_CHECK)

format-lint-check:
	# Check format
	$(RUN) ruff format --check $(SOURCES_FORMAT_LINT)
	# Check lints + import sorting
	$(RUN) ruff check $(SOURCES_FORMAT_LINT)

format-lint:
	# Format code
	$(RUN) ruff format $(SOURCES_FORMAT_LINT)
	# Lint code + import sorting
	$(RUN) ruff check --fix $(SOURCES_FORMAT_LINT)

lint-fix:	
	$(RUN) ruff check --fix $(SOURCES_FORMAT_LINT)

build wheel:
	uv build

build-clean clean-build:
	rm -rf dist

clean: clean-build

shell: install
	source .venv/bin/activate

.PHONY: test tests format-lint-check format-lint lint-fix \
	lint shell type-check wheel build build-clean
