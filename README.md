# Asyntree

Syntax trees and file utilities.

## Usage

As a cli:

```shell
# help
uvx run asyntree --help

# available commands
uvx run asyntree describe .
uvx run asyntree to-tree .
uvx run asyntree to-llm .
uvx run asyntree to-requirements .
```

As a library:

```python
import asyntree as at

requirements = at.to_requirements("...")
```

## Development

```shell
# install project
make init

# run linting 
make lint

# run formatting
make format

# run tests
make test
```
