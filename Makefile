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

.PHONY: image
image:
	git push
	neuro-extras image build . image:wabucketref -F --build-arg COMMIT_SHA=$(shell git rev-parse HEAD)
