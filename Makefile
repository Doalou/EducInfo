.PHONY: install test lint run docker

install:
	python -m pip install -e ".[dev]"

test:
	python -m pytest

lint:
	ruff check .
	ruff format --check .

run:
	APP_ENV=development flask --app run:app run --debug

docker:
	docker compose up --build
