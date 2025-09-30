.PHONY: lint typecheck test all format

lint:
@ruff check .
@black --check .

format:
@black .

typecheck:
@mypy .

test:
@pytest

all: lint typecheck test
