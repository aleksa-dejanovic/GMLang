def test_undirected_connection(metamodel):
    try:
        model = metamodel.model_from_str(
            """
            Something -- SomethingElse
            One -- Two
            One123 -- Two456
            Something_New -- sOmEtHinG123_123_Else2
            """
        )
    except Exception as e:
        assert False, f"Model parsing failed with exception: {e}"

    connected = [(cmd.first, cmd.second) for cmd in model.commands]
    import pprint

    pprint.pprint(connected)
    operators = [cmd.operator for cmd in model.commands]

    # Test that there are no attributes
    assert all(
        not cmd.attributes for cmd in model.commands
    ), "Expected no tags in directed connections"

    assert len(connected) == 4, "Expected 4 connections in the model"
    assert (
        {"One"},
        {"Two"},
    ) in connected, "Connection between 'One' and 'Two' not found"
    assert (
        {"Something"},
        {"SomethingElse"},
    ) in connected, "Connection between 'Something' and 'SomethingElse' not found"
    assert (
        {"One123"},
        {"Two456"},
    ) in connected, "Connection between 'One123' and 'Two456' not found"
    assert (
        {"Something_New"},
        {"sOmEtHinG123_123_Else2"},
    ) in connected, (
        "Connection between 'Something_New' and 'sOmEtHinG123_123_Else2' not found"
    )

    assert all(op == "--" for op in operators), "All operators should be '--'"


def test_directed_connection1(metamodel):
    try:
        model = metamodel.model_from_str(
            """
            A -> B
            X -> Y
            Node_1 -> Node2
            StartNode -> End_Node123
            """
        )
    except Exception as e:
        assert False, f"Model parsing failed with exception: {e}"

    connected = [(cmd.first, cmd.second) for cmd in model.commands]
    operators = [cmd.operator for cmd in model.commands]

    # Test that there are no attributes
    assert all(
        not cmd.attributes for cmd in model.commands
    ), "Expected no tags in directed connections"

    assert len(connected) == 4, "Expected 4 connections in the model"

    assert ({"A"}, {"B"}) in connected, "Connection between 'A' and 'B' not found"
    assert ({"X"}, {"Y"}) in connected, "Connection between 'X' and 'Y' not found"
    assert (
        {"Node_1"},
        {"Node2"},
    ) in connected, "Connection between 'Node_1' and 'Node2' not found"
    assert (
        {"StartNode"},
        {"End_Node123"},
    ) in connected, "Connection between 'StartNode' and 'End_Node123' not found"

    assert all(op == "->" for op in operators), "All operators should be '->'"


def test_directed_connection2(metamodel):
    try:
        model = metamodel.model_from_str(
            """
            first <- second
            alpha <- beta
            NodeA <- NodeB
            Source_Node <- Ta_rgetNode456
            """
        )
    except Exception as e:
        assert False, f"Model parsing failed with exception: {e}"

    connected = [(cmd.first, cmd.second) for cmd in model.commands]
    operators = [cmd.operator for cmd in model.commands]

    # Test that there are no attributes
    assert all(
        not cmd.attributes for cmd in model.commands
    ), "Expected no tags in directed connections"

    assert len(connected) == 4, "Expected 4 connections in the model"

    assert (
        {"first"},
        {"second"},
    ) in connected, "Connection between 'first' and 'second' not found"
    assert (
        {"alpha"},
        {"beta"},
    ) in connected, "Connection between 'alpha' and 'beta' not found"
    assert (
        {"NodeA"},
        {"NodeB"},
    ) in connected, "Connection between 'NodeA' and 'NodeB' not found"
    assert (
        {"Source_Node"},
        {"Ta_rgetNode456"},
    ) in connected, "Connection between 'Source_Node' and 'Ta_rgetNode456' not found"

    assert all(op == "<-" for op in operators), "All operators should be '<-'"


def test_simple_attributed_connection(metamodel):
    try:
        model = metamodel.model_from_str(
            """
            A -- B friend
            X -> Y parent
            P <- Q sister
            """
        )
    except Exception as e:
        assert False, f"Model parsing failed with exception: {e}"

    connections = [
        (
            cmd.first,
            cmd.second,
            cmd.attributes,
        )
        for cmd in model.commands
    ]

    assert len(connections) == 3, "Expected 3 connections in the model"

    conn_attrs = [(first, second, attrs) for first, second, attrs in connections]

    assert (
        {"A"},
        {"B"},
        {"tag": "friend"},
    ) in conn_attrs, "Connection between 'A' and 'B' not found with right attributes"

    assert (
        {"X"},
        {"Y"},
        {"tag": "parent"},
    ) in conn_attrs, "Connection between 'X' and 'Y' not found with right attributes"

    assert (
        {"P"},
        {"Q"},
        {"tag": "sister"},
    ) in conn_attrs, "Connection between 'P' and 'Q' not found with right attributes"


def test_infix_attributed_connection(metamodel):
    try:
        model = metamodel.model_from_str(
            """
            A < brother > B
            X - lives_in - Y
            P - mother > Q
            """
        )
    except Exception as e:
        assert False, f"Model parsing failed with exception: {e}"

    connections = [
        (
            cmd.first,
            cmd.second,
            cmd.attributes,
        )
        for cmd in model.commands
    ]

    assert len(connections) == 3, "Expected 3 connections in the model"

    conn_attrs = [(first, second, attrs) for first, second, attrs in connections]

    assert (
        {"A"},
        {"B"},
        {"tag": "brother"},
    ) in conn_attrs, "Connection between 'A' and 'B' not found with right attributes"

    assert (
        {"X"},
        {"Y"},
        {"tag": "lives_in"},
    ) in conn_attrs, "Connection between 'X' and 'Y' not found with right attributes"

    assert (
        {"P"},
        {"Q"},
        {"tag": "mother"},
    ) in conn_attrs, "Connection between 'P' and 'Q' not found with right attributes"


def test_attributed_connection(metamodel):

    try:
        model = metamodel.model_from_str(
            """
            Node1 -- Node2 [weight: 10, label: "A to B"]
            Alpha -> Beta [capacity: 100]
            X <- Y [type: "undirected", status: "active"]
            Source -> Target ["attributeOnlyKey": "attributeOnlyValue"]
            """
        )
    except Exception as e:
        assert False, f"Model parsing failed with exception: {e}"

    connections = [
        (
            cmd.first,
            cmd.second,
            cmd.attributes,
        )
        for cmd in model.commands
    ]

    assert len(connections) == 4, "Expected 3 connections in the model"

    conn_attrs = [(first, second, attrs) for first, second, attrs in connections]

    assert (
        {"Node1"},
        {"Node2"},
        {"weight": 10, "label": "A to B"},
    ) in conn_attrs, "Connection between 'Node1' and 'Node2' not found"

    assert (
        {"Alpha"},
        {"Beta"},
        {"capacity": 100},
    ) in conn_attrs, "Connection between 'Alpha' and 'Beta' not found"

    assert (
        {"X"},
        {"Y"},
        {"type": "undirected", "status": "active"},
    ) in conn_attrs, "Connection between 'X' and 'Y' not found"
    assert (
        {"Source"},
        {"Target"},
        {"attributeOnlyKey": "attributeOnlyValue"},
    ) in conn_attrs, "Connection between 'Source' and 'Target' not found"


def test_node_sets(metamodel):
    try:
        model = metamodel.model_from_str(
            """
            {A, B, C} -- {D, E}
            {Node1, Node2} -> {Node3, Node4, Node5}
            {X, Y, Z} <- {P, Q}
            Alice -- {Bob, Charlie}
            {Dave, Eve} -> Frank
            """
        )
    except Exception as e:
        assert False, f"Model parsing failed with exception: {e}"

    connections = [
        (
            cmd.first,
            cmd.second,
        )
        for cmd in model.commands
    ]

    assert len(connections) == 5, "Expected 5 connections in the model"
    conn_sets = [(first, second) for first, second in connections]
    assert (
        {"A", "B", "C"},
        {"D", "E"},
    ) in conn_sets, "Connection between '{A, B, C}' and '{D, E}' not found"
    assert (
        {"Node1", "Node2"},
        {"Node3", "Node4", "Node5"},
    ) in conn_sets, (
        "Connection between '{Node1, Node2}' and '{Node3, Node4, Node5}' not found"
    )
    assert (
        {"X", "Y", "Z"},
        {"P", "Q"},
    ) in conn_sets, "Connection between '{X, Y, Z}' and '{P, Q}' not found"
    assert (
        {"Alice"},
        {"Bob", "Charlie"},
    ) in conn_sets, "Connection between 'Alice' and '{Bob, Charlie}' not found"
    assert (
        {"Dave", "Eve"},
        {"Frank"},
    ) in conn_sets, "Connection between '{Dave, Eve}' and 'Frank' not found"


# TODO: Add tests for attributes and tags with node sets
