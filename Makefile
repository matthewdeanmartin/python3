.EXPORT_ALL_VARIABLES:
# Get changed files

# if you wrap everything in uv run, it runs slower.
ifeq ($(origin VIRTUAL_ENV),undefined)
    VENV := uv run
else
    VENV :=
endif

uv.lock: pyproject.toml
	@echo "Installing dependencies"
	@uv sync --all-extras


# tests can't be expected to pass if dependencies aren't installed.
# tests are often slow and linting is fast, so run tests on linted code.
test: uv.lock
	@echo "Running unit tests"
	# $(VENV) pytest --doctest-modules python3
	# $(VENV) python -m unittest discover
	$(VENV) pytest test -vv --cov=python3 --cov-report=html --cov-fail-under 20 --cov-branch --cov-report=xml --junitxml=junit.xml -o junit_family=legacy


isort:
	@echo "Formatting imports"
	$(VENV) isort .

black:
	@echo "Formatting code"
	$(VENV) metametameta pep621
	$(VENV) black python3 # --exclude .venv
	$(VENV) black test # --exclude .venv


pre-commit:
	@echo "Pre-commit checks"
	$(VENV) pre-commit run --all-files

bandit:
	@echo "Security checks"
	# $(VENV)  bandit python3 -r --quiet


pylint:
	@echo "Linting with pylint"
	$(VENV) ruff check python3 --fix
	$(VENV) pylint python3 --fail-under 9.8

check: mypy test pylint bandit pre-commit

publish: test
	rm -rf dist && hatch build

mypy:
	$(VENV) echo $$PYTHONPATH
	$(VENV) mypy python3 --ignore-missing-imports --check-untyped-defs


check_docs:
	$(VENV) interrogate python3 --verbose  --fail-under 70
	$(VENV) pydoctest --config .pydoctest.json | grep -v "__init__" | grep -v "__main__" | grep -v "Unable to parse"

make_docs:
	pdoc python3 --html -o docs --force

check_md:
	$(VENV) linkcheckMarkdown README.md
	$(VENV) markdownlint README.md --config .markdownlintrc
	$(VENV) mdformat README.md docs/*.md


check_spelling:
	$(VENV) pylint python3 --enable C0402 --rcfile=.pylintrc_spell
	$(VENV) pylint docs --enable C0402 --rcfile=.pylintrc_spell
	$(VENV) codespell README.md --ignore-words=private_dictionary.txt
	$(VENV) codespell python3 --ignore-words=private_dictionary.txt
	$(VENV) codespell docs --ignore-words=private_dictionary.txt

check_changelog:
	# pipx install keepachangelog-manager
	$(VENV) changelogmanager validate

check_all_docs: check_docs check_md check_spelling check_changelog
