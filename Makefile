CURRENT_COMMIT = $(shell git rev-parse HEAD)

.PHONY: setup
setup:
	pip install -r requirements/python-dev.txt
	pre-commit install
	pip install -e .

.PHONY: lint
lint: format
	mypy wabucketref tests setup.py

.PHONY: format
format:
	pre-commit run --all-files

.PHONY: image
image:
	git push
	neuro-extras image build . image:wabucketref:$(CURRENT_COMMIT) --build-arg COMMIT_SHA=$(CURRENT_COMMIT)

.PHONY: test
test:
	pytest -vv tests

.PHONY: changelog-draft
changelog-draft: docs
	towncrier --draft --name `python setup.py --name` --version v`python setup.py --version`

.PHONY: changelog
changelog: docs
	towncrier --name `python setup.py --name` --version v`python setup.py --version`

.PHONY: docs
docs:
	build-tools/cli-help-generator.py build-tools/CLI.in.md CLI.md
