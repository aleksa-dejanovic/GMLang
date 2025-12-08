from __future__ import annotations
from dataclasses import dataclass, field


@dataclass
class Node:
    id: str
    edges: list[Edge] = field(default_factory=list)
    attributes: dict[str, str] = field(default_factory=dict)


@dataclass
class Edge:
    source: list[Node] = field(default_factory=list)
    target: list[Node] = field(default_factory=list)
    attributes: dict[str, str] = field(default_factory=dict)
    directed: bool = False

    def ends(self) -> list[Node]:
        return self.source + self.target

    def __repr__(self):
        dir_symbol = "->" if self.directed else "--"
        source_ids = ",".join(node.id for node in self.source)
        target_ids = ",".join(node.id for node in self.target)
        return f"Edge({source_ids} {dir_symbol} {target_ids}, attributes={self.attributes})"


@dataclass
class Graph:
    nodes: dict[str, Node] = field(default_factory=dict)

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

    def get_nodes(self) -> list[Node]:
        return list(self.nodes.values())

    def get_edges(self) -> list[Edge]:
        edges = []
        for node in self.nodes.values():
            for edge in node.edges:
                edges.append(edge)
        return list(edges)
