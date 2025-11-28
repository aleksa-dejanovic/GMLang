def test_create_graph_command(metamodel):
    try:
        model = metamodel.model_from_str(
            """
            graph create MyGraph
            graph create MyOther_graph123
            """
        )
    except Exception as e:
        assert False, f"Model parsing failed with exception: {e}"

    commands = model.commands

    assert len(commands) == 2, "Expected 2 commands in the model"

    assert all(
        cmd.__class__.__name__ == "GraphContextCommand" for cmd in commands
    ), "All commands should be GraphContextCommand"

    assert all(
        cmd.subcommand == "create" for cmd in commands
    ), "All commands should have subcommand 'create'"

    create_cmd = commands[0]
    use_cmd = commands[1]

    assert create_cmd.args == ["MyGraph"], "First command graph name does not match"
    assert use_cmd.args == [
        "MyOther_graph123"
    ], "Second command graph name does not match"


def test_use_graph_command(metamodel):
    try:
        model = metamodel.model_from_str(
            """
            graph use TestGraph
            graph use AnotherGraph_456
            """
        )
    except Exception as e:
        assert False, f"Model parsing failed with exception: {e}"

    commands = model.commands
    assert len(commands) == 2, "Expected 2 commands in the model"

    assert all(
        cmd.__class__.__name__ == "GraphContextCommand" for cmd in commands
    ), "All commands should be GraphContextCommand"
    assert all(
        cmd.subcommand == "use" for cmd in commands
    ), "All commands should have subcommand 'use'"

    use_cmd1 = commands[0]
    use_cmd2 = commands[1]

    assert use_cmd1.args == ["TestGraph"], "First command graph name does not match"
    assert use_cmd2.args == [
        "AnotherGraph_456"
    ], "Second command graph name does not match"


def test_list_graphs_command(metamodel):
    try:
        model = metamodel.model_from_str(
            """
            graph list
            graph list
            """
        )
    except Exception as e:
        assert False, f"Model parsing failed with exception: {e}"

    commands = model.commands
    assert len(commands) == 2, "Expected 2 commands in the model"

    assert all(
        cmd.__class__.__name__ == "GraphContextCommand" for cmd in commands
    ), "All commands should be GraphContextCommand"
    assert all(
        cmd.subcommand == "list" for cmd in commands
    ), "All commands should have subcommand 'list'"
    assert all(
        cmd.args == [] for cmd in commands
    ), "All list commands should have no arguments"


def test_drop_graph_command(metamodel):
    try:
        model = metamodel.model_from_str(
            """
            graph drop OldGraph
            graph drop AnotherOldGraph_789
            """
        )
    except Exception as e:
        assert False, f"Model parsing failed with exception: {e}"

    commands = model.commands
    assert len(commands) == 2, "Expected 2 commands in the model"

    assert all(
        cmd.__class__.__name__ == "GraphContextCommand" for cmd in commands
    ), "All commands should be GraphContextCommand"
    assert all(
        cmd.subcommand == "drop" for cmd in commands
    ), "All commands should have subcommand 'drop'"

    drop_cmd1 = commands[0]
    drop_cmd2 = commands[1]

    assert drop_cmd1.args == ["OldGraph"], "First command graph name does not match"
    assert drop_cmd2.args == [
        "AnotherOldGraph_789"
    ], "Second command graph name does not match"
