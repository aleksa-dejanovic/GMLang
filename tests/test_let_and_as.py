from textx.metamodel import TextXMetaModel


def test_let_nodes(metamodel: TextXMetaModel):
    model = metamodel.model_from_str(
        """
        let SomeNode be node A
        let OtherNode be node Ba [key:34]
        let subgraph be node n1,n2,n3
        """
    )

    assert all(
        cmd.__class__.__name__ == "LetStatement" for cmd in model.commands
    ), "All commands should be LetStatement"

    expected = [("SomeNode", set(["A"])), ("OtherNode", set(["Ba"])),
                ("subgraph", set(["n1", "n2", "n3"]))]

    assert all(cmd.name == name and cmd.expr.nodes == nodes for ((name, nodes), cmd) in
               zip(expected, model.commands, strict=True))





def test_let_edges(metamodel: TextXMetaModel):
    model = metamodel.model_from_str(
            """
            let edge1 be A -- B
            let edge2 be B -> A someTag
            let edge3 be B <- A [attr1:"value1", attr2: 35]
            """
    )

    expected = [("edge1", {}), ("edge2", {"tag": "someTag"}),
                ("edge3", {"attr1": "value1", "attr2": 35})]

    assert all(
        cmd.__class__.__name__ == "LetStatement" for cmd in model.commands
    ), "All commands should be LetStatement"


    assert all(cmd.name == name and cmd.expr.attributes == attrs for ((name, attrs), cmd)
        in zip(expected, model.commands, strict=True))
    

def test_as_nodes(metamodel):
    model = metamodel.model_from_str(
        """
        node A as SomeNode
        node Ba [key:34] as OtherNode
        node n1,n2,n3 as subgraph
        """
    )

    assert all(
        cmd.__class__.__name__ == "AsStatement" for cmd in model.commands
    ), "All commands should be AsStatement"

    expected = [("SomeNode", set(["A"])), ("OtherNode", set(["Ba"])),
                ("subgraph", set(["n1", "n2", "n3"]))]

    assert all(cmd.name == name and cmd.expr.nodes == nodes for ((name, nodes), cmd) in
               zip(expected, model.commands, strict=True))
    