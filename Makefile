init:
	poetry run pre-commit install --hook-type pre-commit --install-hooks

test:
	poetry run pytest tests -v --cov

publish:
	poetry publish --build

requirements:
	poetry export -f requirements.txt --output requirements.txt

lint: flake8 mypy pydocstyle

format: isort black
