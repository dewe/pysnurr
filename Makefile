.PHONY: clean build test publish typecheck

clean:
	rm -rf dist/
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

typecheck:
	mypy pysnurr

test: typecheck
	pytest tests/ -v

build: clean
	python -m build

publish: build
	@if [ "$$(grep '__version__ = ' pysnurr/__init__.py | cut -d'"' -f2)" != "$$(grep '^version = ' pyproject.toml | cut -d'"' -f2)" ]; then \
		echo "Error: Version mismatch between pyproject.toml and pysnurr/__init__.py"; \
		exit 1; \
	fi
	python -m twine upload dist/*

version:
	@echo "Current version: $$(grep "^version = " pyproject.toml | cut -d'"' -f2)"
