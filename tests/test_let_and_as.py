from textx.metamodel import TextXMetaModel


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

    


    