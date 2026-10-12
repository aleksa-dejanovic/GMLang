import pytest
from parglare import GLRParser, Grammar

from gmlang import (
    GMLangAmbiguityError,
    GMLangSemanticError,
    GMLangSyntaxError,
    create_parser,
    gmlang_language,
)
from gmlang.ast import AsStatement, File, NodeSet
from gmlang.disambiguation import select_legacy_tree
from gmlang.interpreter.basic import BasicInterpreter


@pytest.fixture
def parser():
    return create_parser()


@pytest.mark.parametrize("text", ["", " \t\r", "\n\n", "\r\n \t"])
def test_empty_file(parser, text):
    assert isinstance(parser.parse(text), File)
    assert parser.parse(text).commands == []


def test_reuse_after_errors(parser):
    first = parser.parse("node A [x:1]\n")
    with pytest.raises(GMLangSyntaxError):
        parser.parse("node B")
    with pytest.raises(GMLangSemanticError):
        parser.parse("*-- A *-> B\n")
    second = parser.parse("node B []\n")
    second.commands[0].attributes["other"] = 2
    assert first.commands[0].nodes == {"A"}
    assert first.commands[0].attributes == {"x": 1}
    assert parser["NodeSet"] is NodeSet
    assert isinstance(gmlang_language().parse(""), File)


def test_file_location_and_spans(parser, tmp_path):
    path = tmp_path / "example.gml"
    path.write_bytes(b"node A\r\nnode 1Bad\r\n")
    with pytest.raises(GMLangSyntaxError) as caught:
        parser.parse_file(path)
    error = caught.value
    assert error.file_name == str(path)
    assert error.start_position == 13
    assert error.line == 2
    assert error.column == 6
    assert "Identifier" in error.expected
    assert error.__cause__ is not None
    path.write_bytes(b"node A\r\nnode B\r\n")
    model = parser.parse_file(path)
    assert model.commands[1].span.start == 8
    assert model.commands[1].span.file_name == str(path)


@pytest.mark.parametrize(
    "expression",
    [
        "A -- B",
        "A -- B tag",
        "A -> B [weight:2]",
        "A <tag> B",
        "*<- A *-> B",
        "node A -- node B [x:1]",
    ],
)
def test_connection_alias_requires_complete_parentheses(parser, expression):
    with pytest.raises(GMLangSyntaxError):
        parser.parse(f"{expression} as Alias\n")
    statement = parser.parse(f"({expression}) as Alias\n").commands[0]
    assert isinstance(statement, AsStatement)
    assert statement.name == "Alias"


def test_parenthesized_alias_executes(parser):
    model = parser.parse("node A,B\n(A -- B [x:1]) as EdgeAlias\n")
    interpreter = BasicInterpreter()
    interpreter.interpret(model.commands)
    edges = interpreter.get_variable("EdgeAlias")
    assert len(edges) == 1
    assert edges[0].attributes == {"x": 1}


def test_many_ambiguities_are_pruned_locally(parser, monkeypatch):
    text = 'node A -- node B [kind:"x"]\n' * 100
    forest = parser._parser.parse(text)
    assert forest.solutions == 2**100
    # Fail immediately if the selector attempts whole-forest enumeration.
    monkeypatch.setattr(type(forest), "__iter__", lambda self: pytest.fail("enumeration"))
    tree = select_legacy_tree(forest)
    assert forest.solutions == 1
    model = parser._parser.call_actions(tree)
    assert len(model.commands) == 100
    assert all(c.attributes == {} for c in model.commands)
    assert all(c.second.attributes == {"kind": "x"} for c in model.commands)


def test_ownership_is_independent_of_candidate_order(parser):
    from parglare.glr import Parent
    from parglare.trees import visitor

    forest = parser._parser.parse('*-> node B [kind:"x"]\n')

    def reverse(node, _, depth):
        if isinstance(node, Parent):
            node.possibilities.reverse()

    visitor(forest.result, iter, reverse)
    model = parser._parser.call_actions(select_legacy_tree(forest))
    command = model.commands[0]
    assert command.attributes == {}
    assert command.inners[0].attributes == {"kind": "x"}


def test_unknown_ambiguity_is_rejected():
    grammar = Grammar.from_string("S: A | B; A: 'x'; B: 'x';")
    forest = GLRParser(grammar, prefer_shifts=False).parse("x")
    with pytest.raises(GMLangAmbiguityError, match="Unresolved syntax ambiguity"):
        select_legacy_tree(forest)
