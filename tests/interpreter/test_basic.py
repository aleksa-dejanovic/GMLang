import json

from textx import TextXSemanticError

from gmlang.graph.json_encoder import GraphJSONEncoder
from gmlang.interpreter.basic import BasicInterpreter


def canonicalize(value):
    if isinstance(value, dict):
        return {key: canonicalize(item) for key, item in sorted(value.items())}
    if isinstance(value, list):
        items = [canonicalize(item) for item in value]
        return sorted(items, key=lambda item: json.dumps(item, sort_keys=True))
    return value


def check_graph(graph, snapshot):
    graph_data = GraphJSONEncoder().default(graph)
    assert canonicalize(graph_data) == snapshot


def test_basic(metamodel, snapshot, interpret_v):
    text = """
    node A
    node B
    A -> B
    node A1, B1, C -- node D
    """
    model = metamodel.model_from_str(text)
    interpreter = BasicInterpreter(verbose=interpret_v)
    interpreter.interpret(model.commands)
    graph = interpreter._graph
    check_graph(graph, snapshot)


def test_connection_types(metamodel, snapshot, interpret_v):
    text = """
    node X, Y
    X -- Y
    X -> Y
    X <- Y
    node M, N, O <> node P
    """
    model = metamodel.model_from_str(text)
    interpreter = BasicInterpreter(verbose=interpret_v)
    interpreter.interpret(model.commands)
    graph = interpreter._graph
    check_graph(graph, snapshot)


def test_infix_connections(metamodel, snapshot, interpret_v):
    text = """
    node A <sister> node B
    node C -friend- node D
    node E, F -colleague> node G, H
    """
    model = metamodel.model_from_str(text)
    interpreter = BasicInterpreter(verbose=interpret_v)
    interpreter.interpret(model.commands)
    graph = interpreter._graph
    check_graph(graph, snapshot)


def test_hyperedge_connections(metamodel, snapshot, interpret_v):
    text = """
    node A, B, C, D, E
    *-- {A, B, C}
    *<- {A} *-> {D, E} *<- {B} *<- {C}
    """
    model = metamodel.model_from_str(text)
    interpreter = BasicInterpreter(verbose=interpret_v)
    interpreter.interpret(model.commands)
    graph = interpreter._graph
    check_graph(graph, snapshot)


def test_hyperedge_chain(metamodel, snapshot, interpret_v):
    text = """
    *<- node A *-> node D, E *<- node B *<- node C
    """
    model = metamodel.model_from_str(text)
    interpreter = BasicInterpreter(verbose=interpret_v)
    interpreter.interpret(model.commands)
    graph = interpreter._graph
    check_graph(graph, snapshot)


def test_hyperedge_non_declared(metamodel):
    text = """
    *<- node A *-> node D, E *<- B *<- node C
    """
    model = metamodel.model_from_str(text)
    interpreter = BasicInterpreter()
    try:
        interpreter.interpret(model.commands)
    except TextXSemanticError:
        return

    raise AssertionError("Interpreting should have failed due to undeclared aliases")


def test_duplicate_alias(metamodel):
    text = """
    node A
    node B
    A -- B
    node C
    node A
    """
    model = metamodel.model_from_str(text)
    interpreter = BasicInterpreter()
    try:
        interpreter.interpret(model.commands)
    except TextXSemanticError:
        return

    raise AssertionError("Interpreting should have failed due to duplicate aliases")

def test_let_node(metamodel):
    text = """
    let SomeName be node A
    let podgraf be node B, C, D
    """

    model = metamodel.model_from_str(text)
    interpreter = BasicInterpreter()
    interpreter.interpret(model.commands)

def test_as_node(metamodel):
    text = """
    node A as SomeName
    node B, C, D as podgraf
    """

    model = metamodel.model_from_str(text)
    interpreter = BasicInterpreter()
    interpreter.interpret(model.commands)
