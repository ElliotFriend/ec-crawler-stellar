# default target does nothing
.DEFAULT_GOAL: default
default: ;

validate:
	@echo ✅ validate package
	poetry run python -c 'import crawler; print(crawler.__package__ + " successfully imported")'
.PHONY: validate

test:
	@echo 🧪 Type Checks with MyPy
	poetry run mypy crawler/
.PHONY: test

format:
	pre-commit run --all-file
.PHONY: format

docs:
	poetry run pdoc ./crawler -o ./docs
.PHONY: docs

lint:
	@echo ♻️ Reformatting Code
	poetry run black .
	@echo ✅  Style Checks with PyLint
	poetry run pylint ./crawler/**/*.py
.PHONY: lint

all: validate test lint
