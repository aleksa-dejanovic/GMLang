from textx.exceptions import TextXSemanticError


def assert_hyperedge_chain(
    hyperedge_chain,
    expected_contents,
    expected_attributes,
):
    contents = {"undirected": set(), "source": set(), "target": set()}
    contents.update(expected_contents)
    assert (
        hyperedge_chain.contents == contents
    ), f"Expected contents {contents}, got {hyperedge_chain.contents}"
    assert (
        hyperedge_chain.attributes == expected_attributes
    ), f"Expected attributes {expected_attributes}, got {hyperedge_chain.attributes}"


def test_undirected(metamodel):
    try:
        model = metamodel.model_from_str(
            """
            *-- {A, B, C}
            *--{ Node1, Node2  }
            *-- (node A, B ,    C) [node_type: "letter"]
            *-- {G, B, C} *-- {D, E} *-- (node X) *-- {Y, Z}
            """
        )
    except Exception as e:
        assert False, f"Model parsing failed with exception: {e}"
    commands = model.commands
    assert len(commands) == 4, "Expected 4 commands in the model"
    assert_hyperedge_chain(
        commands[0],
        expected_contents={"undirected": {"A", "B", "C"}},
        expected_attributes={},
    )
    assert_hyperedge_chain(
        commands[1],
        expected_contents={"undirected": {"Node1", "Node2"}},
        expected_attributes={},
    )
    assert_hyperedge_chain(
        commands[2],
        expected_contents={"undirected": {"A", "B", "C"}},
        expected_attributes={"node_type": "letter"},
    )
    assert_hyperedge_chain(
        commands[3],
        expected_contents={
            "undirected": {"G", "B", "C", "D", "E", "X", "Y", "Z"},
        },
        expected_attributes={},
    )


def test_directed(metamodel):
    try:
        model = metamodel.model_from_str(
            """
            *-> {A, B, C}
            *<-{ Node1, Node2  }
            *-> (node A, B ,    C) [node_type: "letter"]
            *-> {G, B, C} *<- {D, E} *-> (node X) *<- {Y, Z}
            """
        )
    except Exception as e:
        assert False, f"Model parsing failed with exception: {e}"
    commands = model.commands
    assert len(commands) == 4, "Expected 4 commands in the model"
    assert_hyperedge_chain(
        commands[0],
        expected_contents={"target": {"A", "B", "C"}},
        expected_attributes={},
    )
    assert_hyperedge_chain(
        commands[1],
        expected_contents={"source": {"Node1", "Node2"}},
        expected_attributes={},
    )
    assert_hyperedge_chain(
        commands[2],
        expected_contents={"target": {"A", "B", "C"}},
        expected_attributes={"node_type": "letter"},
    )
    assert_hyperedge_chain(
        commands[3],
        expected_contents={
            "target": {"G", "B", "C", "X"},
            "source": {"D", "E", "Y", "Z"},
        },
        expected_attributes={},
    )


def test_mixed(metamodel):
    try:
        model = metamodel.model_from_str(
            """
            *-- {A, B} *-> {C, D} *<- (node E)
            *<- {X, Y} *-- {Z} *-> (node W)
            """
        )
        assert False, "Model parsing should have failed due to mixed hyperedge types"
    except Exception as e:
        assert isinstance(
            e, TextXSemanticError
        ), f"Model parsing failed with exception: {e}"
