from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass, field
from typing import Any

Attributes = dict[str, Any]


@dataclass
class Node:
    id: str
    edges: list[Edge | Hyperedge] = field(default_factory=list, repr=False, compare=False)
    attributes: Attributes = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not isinstance(self.id, str) or not self.id:
            raise ValueError("A node id must be a non-empty string")

    def __repr__(self) -> str:
        return f"Node({self.id!r}, attributes={self.attributes!r})"

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Node):
            return NotImplemented
        return self.id == other.id and self.attributes == other.attributes


@dataclass(eq=False)
class Edge:
    source: Node
    target: Node
    attributes: Attributes = field(default_factory=dict)
    directed: bool = False

    def ends(self) -> tuple[Node, Node]:
        return self.source, self.target

    def __repr__(self) -> str:
        direction = "->" if self.directed else "--"
        return (
            f"Edge({self.source.id!r} {direction} {self.target.id!r}, "
            f"attributes={self.attributes!r})"
        )


@dataclass(eq=False)
class Hyperedge:
    source: Iterable[Node]
    target: Iterable[Node] = field(default_factory=tuple)
    attributes: Attributes = field(default_factory=dict)
    directed: bool = False

    def __post_init__(self) -> None:
        # Materialise arbitrary iterables once. This also makes serialization and
        # repeated endpoint traversal deterministic.
        self.source = tuple(self.source)
        self.target = tuple(self.target)
        if not self.source and not self.target:
            raise ValueError("A hyperedge must have at least one endpoint")
        self.directed = bool(self.target)

    @property
    def is_directed(self) -> bool:
        return bool(self.directed)

    def ends(self) -> tuple[Node, ...]:
        # Preserve endpoint order but do not attach an edge twice when a node is
        # present in both partitions (or repeated in one partition).
        result: list[Node] = []
        seen: set[int] = set()
        for node in (*self.source, *self.target):
            if id(node) not in seen:
                result.append(node)
                seen.add(id(node))
        return tuple(result)

    def __repr__(self) -> str:
        source = ", ".join(node.id for node in self.source)
        if self.is_directed:
            target = ", ".join(node.id for node in self.target)
            endpoints = f"{{{source}}} -> {{{target}}}"
        else:
            endpoints = f"{{{source}}}"
        return f"Hyperedge({endpoints}, attributes={self.attributes!r})"


Connection = Edge | Hyperedge


@dataclass
class Graph:
    nodes: dict[str, Node] = field(default_factory=dict)

    def __post_init__(self) -> None:
        for node_id, node in self.nodes.items():
            if node_id != node.id:
                raise ValueError(
                    f"Node mapping key {node_id!r} does not match id {node.id!r}"
                )

    def __repr__(self) -> str:
        nodes = "\n".join(repr(node) for node in self.get_nodes())
        edges = "\n".join(repr(edge) for edge in self.get_edges())
        return f"Graph(nodes:\n{nodes}\nedges:\n{edges}\n)"

    def add_node(self, node: Node) -> None:
        existing = self.nodes.get(node.id)
        if existing is not None and existing is not node:
            raise ValueError(f"A different node with id {node.id!r} already exists")
        self.nodes[node.id] = node

    def _validate_endpoints(self, connection: Connection) -> None:
        for node in connection.ends():
            if self.nodes.get(node.id) is not node:
                raise ValueError(
                    f"Endpoint {node.id!r} is not the node registered in this graph"
                )

    def _add_connection(self, connection: Connection) -> None:
        self._validate_endpoints(connection)
        for node in connection.ends():
            if not any(current is connection for current in node.edges):
                node.edges.append(connection)

    def add_edge(self, edge: Edge) -> None:
        self._add_connection(edge)

    def add_hyperedge(self, edge: Hyperedge) -> None:
        self._add_connection(edge)

    def get_node(self, node_id: str) -> Node | None:
        return self.nodes.get(node_id)

    def remove_node(self, node_id: str) -> bool:
        node = self.nodes.get(node_id)
        if node is None:
            return False
        # Copy because removing or shrinking connections mutates node.edges.
        for connection in list(node.edges):
            if isinstance(connection, Hyperedge) and len(connection.ends()) > 1:
                connection.source = tuple(
                    endpoint for endpoint in connection.source if endpoint is not node
                )
                connection.target = tuple(
                    endpoint for endpoint in connection.target if endpoint is not node
                )
                self._detach_connection(node, connection)
            else:
                self._remove_connection(connection)
        del self.nodes[node_id]
        return True

    @staticmethod
    def _detach_connection(node: Node, connection: Connection) -> bool:
        removed = False
        for index in range(len(node.edges) - 1, -1, -1):
            if node.edges[index] is connection:
                del node.edges[index]
                removed = True
        return removed

    def _remove_connection(self, connection: Connection) -> bool:
        removed = False
        for node in connection.ends():
            removed = self._detach_connection(node, connection) or removed
        return removed

    def remove_edge(self, edge: Edge) -> bool:
        return self._remove_connection(edge)

    def remove_hyperedge(self, edge: Hyperedge) -> bool:
        return self._remove_connection(edge)

    def get_nodes(self) -> list[Node]:
        return list(self.nodes.values())

    def get_edges(self) -> list[Connection]:
        result: list[Connection] = []
        seen: set[int] = set()
        for node in self.nodes.values():
            for edge in node.edges:
                if id(edge) not in seen:
                    result.append(edge)
                    seen.add(id(edge))
        return result
