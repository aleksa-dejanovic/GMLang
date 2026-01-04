def assert_connection(
    command,
    expected_first_nodes,
    expected_second_nodes,
    expected_attributes,
    expected_operator,
    expected_first_attrs=None,
    expected_second_attrs=None,
):
    if expected_second_attrs is None:
        expected_second_attrs = {}
    if expected_first_attrs is None:
        expected_first_attrs = {}
    assert (
        command.first.nodes == expected_first_nodes
    ), (
        f"First nodes mismatch, got {command.first.nodes}, "
        f"expected {expected_first_nodes}"
    )
    assert (
        command.second.nodes == expected_second_nodes
    ), (
        f"Second nodes mismatch, got {command.second.nodes}, "
        f"expected {expected_second_nodes}"
    )
    assert (
        command.attributes == expected_attributes
    ), f"Attributes mismatch, got {command.attributes}, expected {expected_attributes}"
    assert (
        command.operator == expected_operator
    ), f"Operator mismatch, got {command.operator}, expected {expected_operator}"
    assert (
        getattr(command.first, "attributes", {}) == expected_first_attrs
    ), f"First nodes attributes mismatch \
        got {getattr(command.first, "attributes", {})} \
        expected {expected_first_attrs}"
    assert (
        getattr(command.second, "attributes", {}) == expected_second_attrs
    ), f"Second nodes attributes mismatch \
        got {getattr(command.second, "attributes", {})} \
        expected {expected_second_attrs}"


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
        raise AssertionError(f"Model parsing failed with exception: {e}") from e

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
        raise AssertionError(f"Model parsing failed with exception: {e}") from e

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


def test_mixed_node_sets(metamodel):
    try:
        model = metamodel.model_from_str(
            """
            node A, B -- {C, D} [tag: "group_connection"]
            {E, F} -> (node G) [relation: "leader"]
            H <> {I, J} team
            (K -- node L) [tag: "extra_connection"]
            (node M [tag: "isolated_node"] <> node N [tag: "isolated_node_2"]) [tag: "isolated_connection"]
            """
        )
    except Exception as e:
        raise AssertionError(f"Model parsing failed with exception: {e}") from e

    commands = model.commands
    assert len(commands) == 5, "Expected 5 commands in the model"

    assert_connection(
        commands[0],
        expected_first_nodes={"A", "B"},
        expected_second_nodes={"C", "D"},
        expected_attributes={"tag": "group_connection"},
        expected_operator="--",
    )
    assert_connection(
        commands[1],
        expected_first_nodes={"E", "F"},
        expected_second_nodes={"G"},
        expected_attributes={"relation": "leader"},
        expected_operator="->",
    )
    assert_connection(
        commands[2],
        expected_first_nodes={"H"},
        expected_second_nodes={"I", "J"},
        expected_attributes={"tag": "team"},
        expected_operator="<>",
    )
    assert_connection(
        commands[3],
        expected_first_nodes={"K"},
        expected_second_nodes={"L"},
        expected_attributes={"tag": "extra_connection"},
        expected_operator="--",
    )
    assert_connection(
        commands[4],
        expected_first_nodes={"M"},
        expected_second_nodes={"N"},
        expected_attributes={"tag": "isolated_connection"},
        expected_operator="<>",
        expected_first_attrs={"tag": "isolated_node"},
        expected_second_attrs={"tag": "isolated_node_2"},
    )


def test_infix_connections(metamodel):
    try:
        model = metamodel.model_from_str(
            """
            node A < friend > node B
            {X, Y} - parent - (node Z)
            P - sibling > {Q, R}
            """
        )
    except Exception as e:
        raise AssertionError(f"Model parsing failed with exception: {e}") from e

    commands = model.commands
    assert len(commands) == 3, "Expected 3 commands in the model"

    assert_connection(
        commands[0],
        expected_first_nodes={"A"},
        expected_second_nodes={"B"},
        expected_attributes={"tag": "friend"},
        expected_operator="<>",
    )
    assert_connection(
        commands[1],
        expected_first_nodes={"X", "Y"},
        expected_second_nodes={"Z"},
        expected_attributes={"tag": "parent"},
        expected_operator="--",
    )
    assert_connection(
        commands[2],
        expected_first_nodes={"P"},
        expected_second_nodes={"Q", "R"},
        expected_attributes={"tag": "sibling"},
        expected_operator="->",
    )
