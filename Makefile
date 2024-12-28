.PHONY: clean build test publish typecheck check-version

VERSION := $(shell grep "__version__ = " pysnurr/__init__.py | cut -d'"' -f2)

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

check-version:
	@if git rev-parse "v$(VERSION)" >/dev/null 2>&1; then \
		echo "Error: Git tag v$(VERSION) already exists"; \
		exit 1; \
	fi

publish: check-version build
	python -m twine upload dist/* && \
	git tag -a "v$(VERSION)" -m "Release v$(VERSION)" && \
	git push origin "v$(VERSION)"

version:
	@echo "Current version: $(VERSION)"
