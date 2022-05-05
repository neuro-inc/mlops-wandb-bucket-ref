CURRENT_COMMIT = $(shell git rev-parse HEAD)

.PHONY: setup
setup:
	pip install -r requirements/python-dev.txt
	pre-commit install
	pip install -e .

.PHONY: lint
lint: format
	mypy wabucketref setup.py

.PHONY: format
format:
	pre-commit run --all-files

.PHONY: image
image:
	git push
	neuro-extras image build . image:wabucketref:$(CURRENT_COMMIT) --build-arg COMMIT_SHA=$(CURRENT_COMMIT)
