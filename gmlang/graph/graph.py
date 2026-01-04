from __future__ import annotations
from dataclasses import dataclass, field
from typing import Iterable

import json


@dataclass
class Node:
    id: str
    edges: list[Edge] = field(default_factory=list)
    attributes: dict[str, str] = field(default_factory=dict)

    def __repr__(self):
        return f"Node({self.id}, attributes={self.attributes})"

    def __eq__(self, other: Node):
        return self.id == other.id and self.attributes == other.attributes


@dataclass
class Edge:
    source: Node
    target: Node
    attributes: dict[str, str] = field(default_factory=dict)
    directed: bool = False

    def ends(self) -> tuple[Node]:
        return (self.source, self.target)

    def __repr__(self):
        dir_symbol = "->" if self.directed else "--"
        return f"Edge({self.source.id} {dir_symbol} {self.target.id}, attributes={self.attributes})"


@dataclass
class Hyperedge:
    source: Iterable[Node]
    target: Iterable[Node]
    attributes: dict[str, str] = field(default_factory=dict)

    @property
    def is_directed(self):
        return self.target == []

    def ends(self) -> set[Node]:
        return self.source + self.target


@dataclass
class Graph:
    nodes: dict[str, Node] = field(default_factory=dict)

    def __repr__(self):
        return (
            f"Graph(nodes:\n{"\n".join(str(node) for node in self.get_nodes())}\n"
            f"edges:\n{"\n".join(str(edge) for edge in self.get_edges())}\n)"
        )

    def add_node(self, node: Node) -> None:
        self.nodes[node.id] = node

    def add_edge(self, edge: Edge) -> None:
        for node in edge.ends():
            node.edges.append(edge)

    def get_node(self, node_id: str) -> Node | None:
        return self.nodes.get(node_id, None)

    def remove_node(self, node_id: str) -> bool:
        if node_id in self.nodes:
            node = self.nodes[node_id]
            # Remove all edges connected to this node
            for edge in node.edges:
                self.remove_edge(edge)
            del self.nodes[node_id]
            return True
        return False

    def remove_edge(self, edge: Edge) -> bool:
        removed = False
        for node in edge.ends():
            if edge in node.edges:
                node.edges.remove(edge)
                removed = True
        return removed

    def add_hyperedge(self, edge: Hyperedge) -> None:
        for node in edge.ends():
            node.edges.append(edge)

    def remove_hyperedge(self, edge: Hyperedge) -> bool:
        removed = False
        for node in edge.ends():
            if edge in node.edges:
                node.edges.remove(edge)
                removed = True
        return removed

    def get_nodes(self) -> list[Node]:
        return list(self.nodes.values())

    def get_edges(self) -> list[Edge]:
        edges = []
        for node in self.nodes.values():
            for edge in node.edges:
                edges.append(edge)
        return list(edges)
