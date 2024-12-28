.PHONY: help clean build test publish typecheck check-version dev-install lint

VERSION := $(shell grep "__version__ = " pysnurr/__init__.py | cut -d'"' -f2)

help: ## Show this help message
	@echo 'Usage: make [target]'
	@echo ''
	@echo 'Targets:'
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "  %-20s %s\n", $$1, $$2}' $(MAKEFILE_LIST)

clean: ## Clean build artifacts and cache files
	rm -rf dist/
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

build: clean ## Build distribution packages
	python -m build

check-version: ## Check if version tag already exists
	@if git rev-parse "v$(VERSION)" >/dev/null 2>&1; then \
		echo "Error: Git tag v$(VERSION) already exists"; \
		exit 1; \
	fi

check-git: ## Check for uncommitted changes
	@if [ -n "$$(git status --porcelain)" ]; then \
		echo "Error: Working directory is not clean. Commit or stash changes first."; \
		exit 1; \
	fi

check-twine: ## Check if twine is installed
	@which twine > /dev/null || (echo "Error: twine is not installed. Run: pip install twine" && exit 1)

publish: check-git check-version check-twine build ## Build and publish to PyPI with git tag
	python -m twine upload dist/* && \
	git tag -a "v$(VERSION)" -m "Release v$(VERSION)" && \
	git push origin "v$(VERSION)"

version: ## Show current version
	@echo "Current version: $(VERSION)"
