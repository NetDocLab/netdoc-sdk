# Makefile
.PHONY: install uninstall check coverage fmt lint tests

install:
	poetry install --no-interaction --no-ansi
	poetry run pre-commit install
	poetry run pre-commit install --hook-type commit-msg

uninstall:
	poetry run pre-commit uninstall
	poetry run pre-commit uninstall --hook-type commit-msg

check: ## Run all pre-commit tests
	poetry run pre-commit run --all-files

coverage:  ## run tests and show coverage report
	poetry run pytest tests --cov=netdoc_sdk --cov-report=term-missing --cov-fail-under=80

fmt:   ## Code formatting
	poetry run ruff format .

lint:  ## Code linting (check only)
	poetry run ruff check . --no-fix
	poetry run mypy src/

tests:  ## Run tests (pytest only)
	poetry run pytest tests -v --tb=short
