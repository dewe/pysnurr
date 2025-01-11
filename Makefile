.PHONY: help clean test typecheck dev-install lint version

VERSION := $(shell grep "__version__ = " pysnurr/__init__.py | cut -d'"' -f2)

help: ## Show this help message
	@echo 'Usage: make [target]'
	@echo ''
	@echo 'Targets:'
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "  %-20s %s\n", $$1, $$2}' $(MAKEFILE_LIST)

clean: ## Clean cache files
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

dev-install: ## Install package in editable mode with development dependencies
	pip install -e ".[test]"

typecheck: ## Run type checking
	mypy pysnurr

lint: ## Run code style checks
	black --check pysnurr tests
	ruff check pysnurr tests

test: typecheck ## Run tests
	pytest tests/ -v

version: ## Show current version
	@echo "Current version: $(VERSION)"
