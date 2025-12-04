def assert_connection(
    command,
    expected_first_nodes,
    expected_second_nodes,
    expected_attributes,
    expected_operator,
):
    assert (
        command.first.nodes == expected_first_nodes
    ), f"First nodes mismatch, got {command.first.nodes}, expected {expected_first_nodes}"
    assert (
        command.second.nodes == expected_second_nodes
    ), f"Second nodes mismatch, got {command.second.nodes}, expected {expected_second_nodes}"
    assert (
        command.attributes == expected_attributes
    ), f"Attributes mismatch, got {command.attributes}, expected {expected_attributes}"
    assert (
        command.operator == expected_operator
    ), f"Operator mismatch, got {command.operator}, expected {expected_operator}"


def test_simple(metamodel):
    try:
        model = metamodel.model_from_str(
            """
            node A -- node B
            node Node123 -> node Else
            C <- node D
            """
        )
    except Exception as e:
        assert False, f"Model parsing failed with exception: {e}"

    commands = model.commands
    assert len(commands) == 3, "Expected 3 commands in the model"
    assert all(
        isinstance(cmd, metamodel["StandardConnectionCommand"]) for cmd in commands
    ), f"All commands should be StandardConnectionCommand but are \
        {[type(command) for command in commands]}"

    assert all(
        len(cmd.first.nodes) == 1 and len(cmd.second.nodes) == 1 for cmd in commands
    ), f"Each command should connect exactly one node on each side \
        {[(cmd.first.nodes, cmd.second.nodes) for cmd in commands]}"

    assert all(
        isinstance(inner, (metamodel["NodeCreationCommand"], metamodel["NodeSet"]))
        for cmd in commands
        for inner in [cmd.first, cmd.second]
    ), "Each side of the connection should be a NodeCreationCommand or NodeSet"

    assert_connection(
        commands[0],
        expected_first_nodes={"A"},
        expected_second_nodes={"B"},
        expected_attributes={},
        expected_operator="--",
    )
    assert_connection(
        commands[1],
        expected_first_nodes={"Node123"},
        expected_second_nodes={"Else"},
        expected_attributes={},
        expected_operator="->",
    )
    assert_connection(
        commands[2],
        expected_first_nodes={"C"},
        expected_second_nodes={"D"},
        expected_attributes={},
        expected_operator="<-",
    )


def test_attributed(metamodel):
    try:
        model = metamodel.model_from_str(
            """
            node A -- (node B) [tag1: "value1", tag2: "value2"]
            node Node123 -> Else [relation:"friend"]
            C <- (node D) sibling
            """
        )
    except Exception as e:
        assert False, f"Model parsing failed with exception: {e}"

    commands = model.commands
    assert len(commands) == 3, "Expected 3 commands in the model"

    assert_connection(
        commands[0],
        expected_first_nodes={"A"},
        expected_second_nodes={"B"},
        expected_attributes={"tag1": "value1", "tag2": "value2"},
        expected_operator="--",
    )
    assert_connection(
        commands[1],
        expected_first_nodes={"Node123"},
        expected_second_nodes={"Else"},
        expected_attributes={"relation": "friend"},
        expected_operator="->",
    )
    assert_connection(
        commands[2],
        expected_first_nodes={"C"},
        expected_second_nodes={"D"},
        expected_attributes={"tag": "sibling"},
        expected_operator="<-",
    )
