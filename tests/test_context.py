def test_create_graph_command(metamodel):
    try:
        model = metamodel.model_from_str(
            """
            graphs create MyGraph
            graphs create MyOther_graph123
            """
        )
    except Exception as e:
        assert False, f"Model parsing failed with exception: {e}"

    commands = model.commands
    assert len(commands) == 2, "Expected 2 commands in the model"

    create_cmd = commands[0]
    use_cmd = commands[1]

    assert (
        create_cmd.__class__.__name__ == "CreateGraphCommand"
    ), "First command should be CreateGraphCommand"
    assert create_cmd.graph_name == "MyGraph", "Graph name MyGraph does not match"

    assert (
        use_cmd.__class__.__name__ == "CreateGraphCommand"
    ), "Second command should be CreateGraphCommand"
    assert (
        use_cmd.graph_name == "MyOther_graph123"
    ), "Graph name MyOther_graph123 does not match"


def test_use_graph_command(metamodel):
    try:
        model = metamodel.model_from_str(
            """
            graphs use TestGraph
            graphs use AnotherGraph_456
            """
        )
    except Exception as e:
        assert False, f"Model parsing failed with exception: {e}"

    commands = model.commands
    assert len(commands) == 2, "Expected 2 commands in the model"

    use_cmd1 = commands[0]
    use_cmd2 = commands[1]

    assert (
        use_cmd1.__class__.__name__ == "UseGraphCommand"
    ), "First command should be UseGraphCommand"
    assert use_cmd1.graph_name == "TestGraph", "Graph name TestGraph does not match"

    assert (
        use_cmd2.__class__.__name__ == "UseGraphCommand"
    ), "Second command should be UseGraphCommand"
    assert (
        use_cmd2.graph_name == "AnotherGraph_456"
    ), "Graph name AnotherGraph_456 does not match"


def test_list_graphs_command(metamodel):
    try:
        model = metamodel.model_from_str(
            """
            graphs list
            graphs list
            """
        )
    except Exception as e:
        assert False, f"Model parsing failed with exception: {e}"

    """
    commands = model.commands
    assert len(commands) == 2, "Expected 2 commands in the model"

    list_cmd1 = commands[0]
    list_cmd2 = commands[1]

    name1 = list_cmd1.__class__.__name__
    name2 = list_cmd2.__class__.__name__

    assert (
        name1 == "ListGraphsCommand"
    ), f"First command should be ListGraphsCommand and not {commands}"

    assert (
        name2 == "ListGraphsCommand"
    ), f"Second command should be ListGraphsCommand and not {name2}"
    """


def test_drop_graph_command(metamodel):
    try:
        model = metamodel.model_from_str(
            """
            graphs drop OldGraph
            graphs drop AnotherOldGraph_789
            """
        )
    except Exception as e:
        assert False, f"Model parsing failed with exception: {e}"

    commands = model.commands
    assert len(commands) == 2, "Expected 2 commands in the model"

    drop_cmd1 = commands[0]
    drop_cmd2 = commands[1]

    assert (
        drop_cmd1.__class__.__name__ == "DropGraphCommand"
    ), "First command should be DropGraphCommand"
    assert drop_cmd1.graph_name == "OldGraph", "Graph name OldGraph does not match"

    assert (
        drop_cmd2.__class__.__name__ == "DropGraphCommand"
    ), "Second command should be DropGraphCommand"
    assert (
        drop_cmd2.graph_name == "AnotherOldGraph_789"
    ), "Graph name AnotherOldGraph_789 does not match"
