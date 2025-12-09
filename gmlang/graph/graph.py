from __future__ import annotations
from dataclasses import dataclass, field

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

    def to_json(self):
        return json.dumps(
            {
                "nodes": {
                    nid: {
                        "attributes": dict(n.attributes),
                        "edges": [
                            {
                                "source": [s.id for s in e.source],
                                "target": [t.id for t in e.target],
                                "attributes": dict(e.attributes),
                                "directed": e.directed,
                            }
                            for e in n.edges
                        ],
                    }
                    for nid, n in self.nodes.items()
                }
            },
            indent=2,
        )

    @staticmethod
    def from_json(data):
        obj = json.loads(data)
        g = Graph()
        for nid, nd in obj["nodes"].items():
            g.nodes[nid] = Node(id=nid, attributes=dict(nd["attributes"]))
        for nid, nd in obj["nodes"].items():
            n = g.nodes[nid]
            for e in nd["edges"]:
                edge = Edge(
                    source=[g.nodes[x] for x in e["source"]],
                    target=[g.nodes[x] for x in e["target"]],
                    attributes=dict(e["attributes"]),
                    directed=e["directed"],
                )
                n.edges.append(edge)
        return g

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

    def get_nodes(self) -> list[Node]:
        return list(self.nodes.values())

    def get_edges(self) -> list[Edge]:
        edges = []
        for node in self.nodes.values():
            for edge in node.edges:
                edges.append(edge)
        return list(edges)
