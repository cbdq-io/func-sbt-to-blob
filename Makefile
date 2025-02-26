.EXPORT_ALL_VARIABLES:

TAG = 0.1.0

all: lint clean build test

build:
	docker build -t sbt-to-blob:latest .
	docker compose build

clean:
	docker compose down -t 0 --remove-orphans

lint:
	docker run --rm -i hadolint/hadolint < Dockerfile
	yamllint -s .
	isort -v .
	flake8

tag:
	@echo $(TAG)

test:
	docker compose run emulators
	PYTHONPATH=. pytest

prereqs:
	docker run mcr.microsoft.com/azure-functions/python:4-python3.12 pip freeze > constraints.txt
	pip install -Uc constraints.txt -r requirements.txt -r requirements-dev.txt
	pip check
