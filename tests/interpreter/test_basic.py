import sys, os

from gmlang.interpreter.basic import BasicInterpreter

from gmlang.graph.graph import Graph


import os


def get_output_path(request) -> str:
    module_name = request.module.__name__.split(".")[-1]
    test_name = request.node.name
    return os.path.join("tests", "output", module_name, f"{test_name}.txt")


def generate_output(request, content: str):
    out_file = get_output_path(request)
    os.makedirs(os.path.dirname(out_file), exist_ok=True)
    with open(out_file, "w", encoding="utf-8") as f:
        f.write(content)


def read_output(request) -> str:
    out_file = get_output_path(request)
    if not os.path.exists(out_file):
        return ""
    with open(out_file, "r", encoding="utf-8") as f:
        return f.read()


def check_graph(graph, request, overwrite):
    if overwrite:
        graph_json = graph.to_json()
        generate_output(request, graph_json)
    else:
        expected = read_output(request)
        if expected == "":
            raise Exception("Output file empty")
        exp_graph = Graph.from_json(expected)
        assert graph == exp_graph, (
            f"Graph is not as expected\n"
            f"GOT:\n{repr(graph)}\n"
            f"Expected:\n{expected}"
        )


def test_basic(request, metamodel, overwrite):
    text = """
    node A
    node B
    A -> B
    node A1, B1, C -- node D
    """
    model = metamodel.model_from_str(text)
    interpreter = BasicInterpreter()
    interpreter.interpret(model.commands)
    graph = interpreter._graph
    check_graph(graph, request, overwrite)


def test_connection_types(request, metamodel, overwrite):
    text = """
    node X, Y
    X -- Y
    X -> Y
    X <- Y
    node M, N, O <> node P
    """
    model = metamodel.model_from_str(text)
    interpreter = BasicInterpreter()
    interpreter.interpret(model.commands)
    graph = interpreter._graph
    check_graph(graph, request, overwrite)


def test_infix_connections(request, metamodel, overwrite):
    text = """
    node A <sister> node B
    node C -friend- node D
    node E, F -colleague> node G, H
    """
    model = metamodel.model_from_str(text)
    interpreter = BasicInterpreter()
    interpreter.interpret(model.commands)
    graph = interpreter._graph
    check_graph(graph, request, overwrite)
