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
	python -m twine upload dist/*
