# default target does nothing
.DEFAULT_GOAL: default
default: ;

validate:
	@echo ✅ validate package
	uv run python -c 'import crawler; print(crawler.__package__ + " successfully imported")'
.PHONY: validate

test:
	@echo 🧪 Type Checks with MyPy
	uv run mypy crawler/
.PHONY: test

format:
	pre-commit run --all-file
.PHONY: format

docs:
	uv run pdoc ./crawler -o ./docs
.PHONY: docs

lint:
	@echo ♻️ Reformatting Code
	uv run black .
	@echo ✅  Style Checks with PyLint
	uv run pylint ./crawler/**/*.py
.PHONY: lint

all: validate test lint
