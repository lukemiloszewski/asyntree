# Asyntree

Syntax trees and file utilities.

## Commands

```python
uv venv .venv --python 3.12

# create lock file
uv lock

# check if lock file is up to date
uv lock --check

# upgrade deps in lock file
uv lock --upgrade

# sync .venv with lock file
uv sync --all-extras

uv export --format requirements-txt
```
