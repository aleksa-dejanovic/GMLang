def test_simple_node_creation(metamodel):
    try:
        model = metamodel.model_from_str(
            """
            node NodeA
            node Node_B
            node Node123
            node AnotherNode_456
            """
        )
    except Exception as e:
        assert False, f"Model parsing failed with exception: {e}"

    nodes = [cmd.node.value for cmd in model.commands]
    print(nodes)

    assert len(nodes) == 4, "Expected 4 nodes in the model"

    assert "NodeA" in nodes, "Node 'NodeA' not found"
    assert "Node_B" in nodes, "Node 'Node_B' not found"
    assert "Node123" in nodes, "Node 'Node123' not found"
    assert "AnotherNode_456" in nodes, "Node 'AnotherNode_456' not found"


def test_creation_with_invalid_names(metamodel):
    invalid_names = ["1Node", "Node-Name", "Node Name", "Node@123"]
    for name in invalid_names:
        try:
            model = metamodel.model_from_str(f"node {name}")
            assert (
                False
            ), f"Model parsing should have failed for invalid node name: {name}"
        except Exception:
            pass  # Expected exception for invalid names


def test_creation_with_edge_case_names(metamodel):
    try:
        model = metamodel.model_from_str(
            """
            node _NodeStartingWithUnderscore
            node NodeEndingWithUnderscore_
            node N
            node Node_With_Multiple_Underscores_123
            """
        )
    except Exception as e:
        assert False, f"Model parsing failed with exception: {e}"

    nodes = [cmd.node.value for cmd in model.commands]
    print(nodes)

    assert len(nodes) == 4, "Expected 4 nodes in the model"

    assert (
        "_NodeStartingWithUnderscore" in nodes
    ), "Node '_NodeStartingWithUnderscore' not found"
    assert (
        "NodeEndingWithUnderscore_" in nodes
    ), "Node 'NodeEndingWithUnderscore_' not found"
    assert "N" in nodes, "Node 'N' not found"
    assert (
        "Node_With_Multiple_Underscores_123" in nodes
    ), "Node 'Node_With_Multiple_Underscores_123' not found"


def test_node_creation_with_attributes(metamodel):

    def process_attributes(cmd):

        def list_to_dict(l):
            dic = {}
            for elem in l:
                key = elem.key
                value = elem.value
                dic[key] = value
            return dic

        attr_list = cmd.attr_list.attributes if cmd.attr_list else []
        cmd.attributes = list_to_dict(attr_list)
        return cmd

    metamodel.register_obj_processors({"NodeCreationCommand": process_attributes})
    try:
        model = metamodel.model_from_str(
            """
            node NodeA [size: 10, color : "red"]
            node NodeB [size: 20, color :"blue"]
            node NodeC [size     :15, color:      "green"]
            node NodeD []
            node NodeE [size:30,color:"yellow", extra: "data"]
            node NodeF [size: "big", "key with spaces": "value with spaces"]
            """
        )
    except Exception as e:
        assert False, f"Model parsing failed with exception: {e}"
    nodes = {cmd.node.value: cmd.attributes for cmd in model.commands}
    assert len(nodes) == 6, "Expected 6 nodes in the model"
    assert "NodeA" in nodes, "Node 'NodeA' not found"
    assert nodes["NodeA"]["size"] == 10, "NodeA size attribute incorrect"
    assert nodes["NodeA"]["color"] == "red", "NodeA color attribute incorrect"
    assert "NodeB" in nodes, "Node 'NodeB' not found"
    assert nodes["NodeB"]["size"] == 20, "NodeB size attribute incorrect"
    assert nodes["NodeB"]["color"] == "blue", "NodeB color attribute incorrect"
    assert "NodeC" in nodes, "Node 'NodeC' not found"
    assert nodes["NodeC"]["size"] == 15, "NodeC size attribute incorrect"
    assert nodes["NodeC"]["color"] == "green", "NodeC color attribute incorrect"
    assert "NodeD" in nodes, "Node 'NodeD' not found"
    assert nodes["NodeD"] == {}, "NodeD should have no attributes"
    assert "NodeE" in nodes, "Node 'NodeE' not found"
    assert nodes["NodeE"]["size"] == 30, "NodeE size attribute incorrect"
    assert nodes["NodeE"]["color"] == "yellow", "NodeE color attribute incorrect"
    assert nodes["NodeE"]["extra"] == "data", "NodeE extra attribute incorrect"
    assert "NodeF" in nodes, "Node 'NodeF' not found"
    assert nodes["NodeF"]["size"] == "big", "NodeF size attribute incorrect"
    assert (
        nodes["NodeF"]["key with spaces"] == "value with spaces"
    ), "NodeF key with spaces attribute incorrect"
