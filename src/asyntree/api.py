from typing import Any, Dict

from asyntree.visitor import Visitor


def process_ast(tree: Any, visitor: Visitor) -> Dict[str, int]:
    rv = dict(visitor.run(tree))
    return rv
