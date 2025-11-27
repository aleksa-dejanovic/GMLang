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

    connected = [(cmd.first.value, cmd.second.value) for cmd in model.commands]
    operators = [cmd.operator for cmd in model.commands]

    assert len(connected) == 4, "Expected 4 connections in the model"

    assert ("One", "Two") in connected, "Connection between 'One' and 'Two' not found"
    assert (
        "Something",
        "SomethingElse",
    ) in connected, "Connection between 'Something' and 'SomethingElse' not found"
    assert (
        "One123",
        "Two456",
    ) in connected, "Connection between 'One123' and 'Two456' not found"
    assert (
        "Something_New",
        "sOmEtHinG123_123_Else2",
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

    connected = [(cmd.first.value, cmd.second.value) for cmd in model.commands]
    operators = [cmd.operator for cmd in model.commands]

    assert len(connected) == 4, "Expected 4 connections in the model"

    assert ("A", "B") in connected, "Connection between 'A' and 'B' not found"
    assert ("X", "Y") in connected, "Connection between 'X' and 'Y' not found"
    assert (
        "Node_1",
        "Node2",
    ) in connected, "Connection between 'Node_1' and 'Node2' not found"
    assert (
        "StartNode",
        "End_Node123",
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

    connected = [(cmd.first.value, cmd.second.value) for cmd in model.commands]
    operators = [cmd.operator for cmd in model.commands]

    assert len(connected) == 4, "Expected 4 connections in the model"

    assert (
        "first",
        "second",
    ) in connected, "Connection between 'first' and 'second' not found"
    assert (
        "alpha",
        "beta",
    ) in connected, "Connection between 'alpha' and 'beta' not found"
    assert (
        "NodeA",
        "NodeB",
    ) in connected, "Connection between 'NodeA' and 'NodeB' not found"
    assert (
        "Source_Node",
        "Ta_rgetNode456",
    ) in connected, "Connection between 'Source_Node' and 'Ta_rgetNode456' not found"

    assert all(op == "<-" for op in operators), "All operators should be '<-'"


def test_simple_attributed_connection(metamodel):
    def process_attributes(cmd):

        def list_to_dict(l):
            dic = {}
            for elem in l:
                key = elem.key
                value = elem.value
                dic[key] = value
            return dic

        if not cmd.attr_list:
            cmd.attributes = {"tag": cmd.tag}
        else:
            attr_list = cmd.attr_list.attributes
            cmd.attributes = list_to_dict(attr_list)
            del cmd.attr_list
        return cmd

    metamodel.register_obj_processors({"StandardConnectionCommand": process_attributes})
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
            cmd.first.value,
            cmd.second.value,
            cmd.attributes,
        )
        for cmd in model.commands
    ]

    assert len(connections) == 3, "Expected 3 connections in the model"

    conn_dict = {(first, second): attrs for first, second, attrs in connections}

    assert ("A", "B") in conn_dict, "Connection between 'A' and 'B' not found"
    assert conn_dict[("A", "B")] == {
        "tag": "friend"
    }, "Attributes for connection between 'A' and 'B' do not match"

    assert ("X", "Y") in conn_dict, "Connection between 'X' and 'Y' not found"
    assert conn_dict[("X", "Y")] == {
        "tag": "parent"
    }, "Attributes for connection between 'X' and 'Y' do not match"

    assert ("P", "Q") in conn_dict, "Connection between 'P' and 'Q' not found"
    assert conn_dict[("P", "Q")] == {
        "tag": "sister"
    }, "Attributes for connection between 'P' and 'Q' do not match"


def test_infix_attributed_connection(metamodel):
    def process_attributes(cmd):

        cmd.attributes = {"tag": cmd.tag}
        return cmd

    metamodel.register_obj_processors({"InfixConnectionCommand": process_attributes})
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
            cmd.first.value,
            cmd.second.value,
            cmd.attributes,
        )
        for cmd in model.commands
    ]

    assert len(connections) == 3, "Expected 3 connections in the model"

    conn_dict = {(first, second): attrs for first, second, attrs in connections}

    assert ("A", "B") in conn_dict, "Connection between 'A' and 'B' not found"
    assert conn_dict[("A", "B")] == {
        "tag": "brother"
    }, "Attributes for connection between 'A' and 'B' do not match"

    assert ("X", "Y") in conn_dict, "Connection between 'X' and 'Y' not found"
    assert conn_dict[("X", "Y")] == {
        "tag": "lives_in"
    }, "Attributes for connection between 'X' and 'Y' do not match"

    assert ("P", "Q") in conn_dict, "Connection between 'P' and 'Q' not found"
    assert conn_dict[("P", "Q")] == {
        "tag": "mother"
    }, "Attributes for connection between 'P' and 'Q' do not match"


def test_attributed_connection(metamodel):

    def process_attributes(cmd):

        def list_to_dict(l):
            dic = {}
            for elem in l:
                key = elem.key
                value = elem.value
                dic[key] = value
            return dic

        if not cmd.attr_list:
            cmd.attributes = {"tag": cmd.tag}
        else:
            attr_list = cmd.attr_list.attributes
            cmd.attributes = list_to_dict(attr_list)
            del cmd.attr_list
        return cmd

    metamodel.register_obj_processors({"StandardConnectionCommand": process_attributes})

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
            cmd.first.value,
            cmd.second.value,
            cmd.attributes,
        )
        for cmd in model.commands
    ]

    assert len(connections) == 4, "Expected 3 connections in the model"

    conn_dict = {(first, second): attrs for first, second, attrs in connections}

    assert (
        "Node1",
        "Node2",
    ) in conn_dict, "Connection between 'Node1' and 'Node2' not found"
    assert conn_dict[("Node1", "Node2")] == {
        "weight": 10,
        "label": "A to B",
    }, "Attributes for connection between 'Node1' and 'Node2' do not match"

    assert (
        "Alpha",
        "Beta",
    ) in conn_dict, "Connection between 'Alpha' and 'Beta' not found"
    assert conn_dict[("Alpha", "Beta")] == {
        "capacity": 100
    }, "Attributes for connection between 'Alpha' and 'Beta' do not match"

    assert ("X", "Y") in conn_dict, "Connection between 'X' and 'Y' not found"
    assert conn_dict[("X", "Y")] == {
        "type": "undirected",
        "status": "active",
    }, "Attributes for connection between 'X' and 'Y' do not match"
    assert (
        "Source",
        "Target",
    ) in conn_dict, "Connection between 'Source' and 'Target' not found"
    assert conn_dict[("Source", "Target")] == {
        "attributeOnlyKey": "attributeOnlyValue"
    }, "Attributes for connection between 'Source' and 'Target' do not match"
