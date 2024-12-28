.PHONY: clean build test publish

clean:
	rm -rf dist/
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

test:
	pytest tests/

build: clean
	python -m build

publish: build
	python -m twine upload dist/*
