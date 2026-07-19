import json
from typing import Any

from gmlang.graph.graph import Edge, Graph, Hyperedge, Node


def _encode_connection(connection: Edge | Hyperedge) -> dict[str, Any]:
    if isinstance(connection, Edge):
        return {
            "type": "edge",
            "source": connection.source.id,
            "target": connection.target.id,
            "attributes": dict(connection.attributes),
            "directed": connection.directed,
        }
    return {
        "type": "hyperedge",
        "source": [node.id for node in connection.source],
        "target": [node.id for node in connection.target],
        "attributes": dict(connection.attributes),
        "directed": connection.is_directed,
    }


class GraphJSONEncoder(json.JSONEncoder):
    """Serialize graph objects without duplicating adjacency-list entries."""

    def default(self, obj: Any) -> Any:
        if isinstance(obj, Graph):
            return {
                "format": "gmlang.graph",
                "version": 1,
                "type": "graph",
                "nodes": {
                    node_id: {"attributes": dict(node.attributes)}
                    for node_id, node in obj.nodes.items()
                },
                "edges": [_encode_connection(edge) for edge in obj.get_edges()],
            }
        if isinstance(obj, (Edge, Hyperedge)):
            return _encode_connection(obj)
        if isinstance(obj, Node):
            return {
                "type": "node",
                "id": obj.id,
                "attributes": dict(obj.attributes),
            }
        return super().default(obj)


class GraphJSONDecoder(json.JSONDecoder):
    """Decode the v1 graph format and the original per-node-edge format."""

    def decode(self, s: str, _w: Any = ...) -> Any:
        value = super().decode(s)
        if not isinstance(value, dict):
            return value
        if value.get("type") == "node" and "id" in value:
            return Node(value["id"], attributes=value.get("attributes", {}))
        if value.get("type") == "graph" or "nodes" in value:
            return self._decode_graph(value)
        return value

    @staticmethod
    def _decode_graph(data: dict[str, Any]) -> Graph:
        raw_nodes = data.get("nodes")
        if not isinstance(raw_nodes, dict):
            raise ValueError("Graph JSON field 'nodes' must be an object")

        graph = Graph()
        for node_id, node_data in raw_nodes.items():
            if not isinstance(node_data, dict):
                raise ValueError(f"Node {node_id!r} must be an object")
            graph.add_node(Node(node_id, attributes=node_data.get("attributes", {})))

        raw_edges = data.get("edges")
        legacy = raw_edges is None
        if legacy:
            raw_edges = []
            # Old files repeat a connection in every endpoint's adjacency list.
            # A structural key collapses those repetitions. Truly identical
            # parallel edges were ambiguous in that old representation.
            seen: set[str] = set()
            for node_data in raw_nodes.values():
                for edge_data in node_data.get("edges", []):
                    key = json.dumps(edge_data, sort_keys=True, separators=(",", ":"))
                    if key not in seen:
                        raw_edges.append(edge_data)
                        seen.add(key)

        if not isinstance(raw_edges, list):
            raise ValueError("Graph JSON field 'edges' must be an array")
        for edge_data in raw_edges:
            GraphJSONDecoder._add_connection(graph, edge_data)
        return graph

    @staticmethod
    def _node(graph: Graph, node_id: Any) -> Node:
        if not isinstance(node_id, str) or node_id not in graph.nodes:
            raise ValueError(f"Connection references unknown node {node_id!r}")
        return graph.nodes[node_id]

    @staticmethod
    def _add_connection(graph: Graph, data: Any) -> None:
        if not isinstance(data, dict):
            raise ValueError("Each graph edge must be an object")
        edge_type = data.get("type")
        attributes = data.get("attributes", {})
        if edge_type == "edge":
            edge = Edge(
                source=GraphJSONDecoder._node(graph, data.get("source")),
                target=GraphJSONDecoder._node(graph, data.get("target")),
                attributes=attributes,
                directed=bool(data.get("directed", False)),
            )
            graph.add_edge(edge)
            return
        if edge_type == "hyperedge":
            source = data.get("source", [])
            target = data.get("target", [])
            if not isinstance(source, list) or not isinstance(target, list):
                raise ValueError("Hyperedge source and target must be arrays")
            hyperedge = Hyperedge(
                source=[GraphJSONDecoder._node(graph, item) for item in source],
                target=[GraphJSONDecoder._node(graph, item) for item in target],
                attributes=attributes,
                directed=bool(data.get("directed", False)),
            )
            graph.add_hyperedge(hyperedge)
            return
        raise ValueError(f"Unknown graph edge type {edge_type!r}")
