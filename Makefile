.PHONY: setup
setup:
	pip install -r requirements/python-dev.txt
	pre-commit install

.PHONY: lint
lint: format
	mypy wabucketref setup.py

.PHONY: format
format:
	pre-commit run --all-files --show-diff-on-failure
