import json

import pytest

from gmlang.graph.graph import Edge, Graph, Hyperedge, Node
from gmlang.graph.json_encoder import GraphJSONDecoder, GraphJSONEncoder


def make_graph() -> tuple[Graph, Node, Node, Node]:
    graph = Graph()
    nodes = Node("a"), Node("b"), Node("c")
    for node in nodes:
        graph.add_node(node)
    return graph, *nodes


def test_edges_are_listed_once_and_self_loop_is_attached_once():
    graph, a, b, _ = make_graph()
    edge = Edge(a, b)
    loop = Edge(a, a, directed=True)

    graph.add_edge(edge)
    graph.add_edge(loop)

    assert graph.get_edges() == [edge, loop]
    assert a.edges == [edge, loop]
    assert b.edges == [edge]


def test_remove_node_removes_edges_but_shrinks_hyperedges():
    graph, a, b, c = make_graph()
    first = Edge(a, b)
    second = Edge(a, c)
    hyperedge = Hyperedge([a, b], [c])
    graph.add_edge(first)
    graph.add_edge(second)
    graph.add_hyperedge(hyperedge)

    assert graph.remove_node("a")
    assert not graph.remove_node("missing")
    assert graph.get_edges() == [hyperedge]
    assert tuple(hyperedge.source) == (b,)
    assert tuple(hyperedge.target) == (c,)
    assert b.edges == [hyperedge]
    assert c.edges == [hyperedge]


def test_remove_only_hyperedge_member_removes_hyperedge():
    graph, a, _, _ = make_graph()
    hyperedge = Hyperedge([a])
    graph.add_hyperedge(hyperedge)

    assert graph.remove_node("a")
    assert graph.get_edges() == []


def test_remove_node_can_leave_directed_hyperedge_partition_empty():
    graph, a, b, c = make_graph()
    hyperedge = Hyperedge([a], [b, c])
    graph.add_hyperedge(hyperedge)

    assert graph.remove_node("a")
    assert tuple(hyperedge.source) == ()
    assert tuple(hyperedge.target) == (b, c)
    assert hyperedge.is_directed
    assert b.edges == [hyperedge]
    assert c.edges == [hyperedge]


def test_remove_only_target_preserves_hyperedge_direction():
    graph, a, b, c = make_graph()
    hyperedge = Hyperedge([a, b], [c])
    graph.add_hyperedge(hyperedge)

    assert graph.remove_node("c")
    assert tuple(hyperedge.source) == (a, b)
    assert tuple(hyperedge.target) == ()
    assert hyperedge.is_directed


def test_hyperedge_materialises_iterables_and_reports_direction():
    graph, a, b, c = make_graph()
    directed = Hyperedge((node for node in [a, b]), (node for node in [c]))
    undirected = Hyperedge([a, b], [])

    assert directed.is_directed
    assert directed.directed
    assert directed.ends() == (a, b, c)
    assert not undirected.is_directed

    graph.add_hyperedge(directed)
    assert all(node.edges == [directed] for node in (a, b, c))


def test_graph_rejects_duplicate_nodes_and_foreign_endpoints():
    graph, a, _, _ = make_graph()

    with pytest.raises(ValueError, match="different node"):
        graph.add_node(Node("a"))
    with pytest.raises(ValueError, match="not the node registered"):
        graph.add_edge(Edge(a, Node("foreign")))


def test_node_comparison_with_another_type_is_false():
    assert Node("a") != "a"


def test_json_round_trip_preserves_shared_connection_identity():
    graph, a, b, c = make_graph()
    edge = Edge(a, b, {"weight": 2}, directed=True)
    hyperedge = Hyperedge([a, b], [c], {"label": "many"})
    graph.add_edge(edge)
    graph.add_hyperedge(hyperedge)

    encoded = json.dumps(graph, cls=GraphJSONEncoder)
    raw = json.loads(encoded)
    decoded = json.loads(encoded, cls=GraphJSONDecoder)

    assert len(raw["edges"]) == 2
    assert all("edges" not in node for node in raw["nodes"].values())
    assert len(decoded.get_edges()) == 2
    decoded_edge, decoded_hyperedge = decoded.get_edges()
    assert decoded.nodes["a"].edges == [decoded_edge, decoded_hyperedge]
    assert decoded.nodes["b"].edges == [decoded_edge, decoded_hyperedge]
    assert decoded.nodes["c"].edges == [decoded_hyperedge]
    assert decoded_edge.attributes == {"weight": 2}
    assert decoded_edge.directed
    assert decoded_hyperedge.attributes == {"label": "many"}


def test_decoder_reads_legacy_graph_without_duplicate_edges():
    edge = {
        "type": "edge",
        "source": "a",
        "target": "b",
        "attributes": {},
        "directed": False,
    }
    legacy = {
        "nodes": {
            "a": {"attributes": {}, "edges": [edge]},
            "b": {"attributes": {}, "edges": [edge]},
        }
    }

    graph = json.loads(json.dumps(legacy), cls=GraphJSONDecoder)

    assert len(graph.get_edges()) == 1
    assert graph.nodes["a"].edges[0] is graph.nodes["b"].edges[0]


def test_decoder_rejects_unknown_endpoint():
    data = {
        "type": "graph",
        "nodes": {"a": {"attributes": {}}},
        "edges": [
            {"type": "edge", "source": "a", "target": "missing"},
        ],
    }
    with pytest.raises(ValueError, match="unknown node"):
        json.loads(json.dumps(data), cls=GraphJSONDecoder)
