init:
	uv venv .venv
	uv sync --all-extras

test:
	uv run pytest tests -v --cov

lint:
	uv run ruff check src tests
	uv run ruff format src tests --check
	uv run deptry src tests

format:
	uv run ruff check src tests --fix
	uv run ruff format src tests

deps:
	uv lock --check
	uv lock --upgrade
	uv export --format requirements.txt --output-file requirements.txt --no-hashes

publish:
	uv build
	uv publish --index pypi --token ...
