# Asyntree

## Overview

Related Libraries:

- `ast` - [docs](https://docs.python.org/3/library/ast.html)
- `inspect` - [docs](https://docs.python.org/3/library/inspect.html)
- `Green Tree Snakes` - [docs](https://greentreesnakes.readthedocs.io/en/latest/index.html)

## Inspect with Rich

- if object is a callable, extracts the signature for the object
- <https://github.com/Textualize/rich/blob/2be0fc905fafb208df05dfc52d8295bc2b854e43/rich/>__init__.py#L119

## API Reference

```shell
# summarised analysis of operations
asyntree <MODULE_NAME>

# detailed analysis of operations
asyntree <MODULE_NAME> --verbose
```

## Notes

- programattic way to understand source code
- source code, machine code, instructions, statements
- each statement is a node, and each node may be comprised of other nodes

### Types of Nodes

Python's abstract syntax tree represents each element of code as an object. Each object is an instance of some subclass of the base AST node class. These objects are referred to as nodes, and there are various types of nodes that exist.

- literals
- variables
- statements
  - an instruction that a Python interpreter can execute
  - blocks of code are statements
- expressions
  - evaluate to some value
  - any expression is a standalone statement
- control flow
- function and class definitions
- async and await
- top level nodes
  - modules
    - files that can be run by Python

### Context

### Garbage Collection, Variables, Values

So Python is a reference-counted, garbage collected language. For each variable that points to a value, the reference count of that value increases. When the reference count reaches zero, the value is freed.

- values are objects in memory
- variables are pointers to values (objects in memory)

### Use Cases

- determine the imports, and therefore the dependencies used within a module
- <https://www.mattlayman.com/blog/2018/decipher-python-ast/>
