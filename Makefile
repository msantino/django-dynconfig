.PHONY: help install test lint format build clean publish-test publish

help:  ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

install:  ## Install dev dependencies
	pip install -e ".[dev,encryption]"

test:  ## Run tests with coverage
	pytest --cov=dynconfig --cov-report=term-missing -q

lint:  ## Run linter
	ruff check src/ tests/

format:  ## Auto-format code
	ruff format src/ tests/
	ruff check --fix src/ tests/

build:  ## Build package (wheel + sdist)
	python -m build

clean:  ## Remove build artifacts
	rm -rf dist/ build/ src/*.egg-info

publish-test:  ## Publish to TestPyPI
	twine upload --repository testpypi dist/*

publish:  ## Publish to PyPI
	twine upload dist/*
