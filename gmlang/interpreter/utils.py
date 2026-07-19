from typing import TypeGuard

from gmlang.graph.graph import Node


def only_nodes(
    xs: list[object],
) -> TypeGuard[list[Node]]:
    return all(isinstance(x, Node) for x in xs)
