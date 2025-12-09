import json
from typing import Any

from gmlang.graph.graph import Edge, Graph, Hyperedge, Node


class GraphJSONEncoder(json.JSONEncoder):
    def default(self, obj: Any):
        if isinstance(obj, Graph):
            return {
                "nodes": {
                    nid: {
                        "attributes": dict(n.attributes),
                        "edges": [self.default(e) for e in n.edges],
                    }
                    for nid, n in obj.nodes.items()
                }
            }
        elif isinstance(obj, Edge):
            return {
                "type": "edge",
                "source": obj.source.id,
                "target": obj.target.id,
                "attributes": dict(obj.attributes),
                "directed": obj.directed,
            }
        elif isinstance(obj, Hyperedge):
            return {
                "type": "hyperedge",
                "source": [n.id for n in obj.source],
                "target": [n.id for n in obj.target],
                "attributes": dict(obj.attributes),
            }
        elif isinstance(obj, Node):
            return {
                "id": obj.id,
                "attributes": dict(obj.attributes),
                "edges": [self.default(e) for e in obj.edges],
            }
        return super().default(obj)


class GraphJSONDecoder(json.JSONDecoder):
    def __init__(self, *args, **kwargs):
        super().__init__(object_hook=self.object_hook, *args, **kwargs)
        self.nodes_map = {}

    def object_hook(self, obj: dict[str, Any]):
        if "nodes" in obj:  # Graph object
            g = Graph()
            for nid, nd in obj["nodes"].items():
                g.nodes[nid] = Node(id=nid, attributes=nd.get("attributes", {}))
            self.nodes_map = g.nodes
            for nid, nd in obj["nodes"].items():
                node = g.nodes[nid]
                for e_data in nd.get("edges", []):
                    if e_data["type"] == "edge":
                        edge = Edge(
                            source=self.nodes_map[e_data["source"]],
                            target=self.nodes_map[e_data["target"]],
                            attributes=e_data.get("attributes", {}),
                            directed=e_data.get("directed", False),
                        )
                    elif e_data["type"] == "hyperedge":
                        edge = Hyperedge(
                            source=[self.nodes_map[nid] for nid in e_data["source"]],
                            target=[self.nodes_map[nid] for nid in e_data["target"]],
                            attributes=e_data.get("attributes", {}),
                        )
                    node.edges.append(edge)
            return g
        return obj
