from gmlang.interpreter.basic import BasicInterpreter


def test_basic(metamodel):
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
    print(graph.get_nodes())


def test_connection_types(metamodel):
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
    print(graph.get_nodes())
