.EXPORT_ALL_VARIABLES:

COMPOSE_FILE = tests/resources/docker-compose.yaml
TAG = 0.2.0

all: lint clean build test

build:
	docker build -t sbt-to-blob:latest .
	docker compose build

clean:
	docker compose down -t 0 --remove-orphans

cleanall: clean
	docker system prune -a --volumes --force

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
