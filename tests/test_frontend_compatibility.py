"""Recorded TextX 4.2.3 public ASTs, independent of TextX at test time."""

import json
from pathlib import Path

import pytest

from gmlang.errors import GMLangSemanticError, GMLangSyntaxError
from gmlang.parser import create_parser

FIELDS = {
    "File": ["commands"],
    "NodeSet": ["nodes"],
    "NodeCreationCommand": ["nodes", "attributes"],
    "StandardConnectionCommand": ["first", "second", "operator", "attributes"],
    "InfixConnectionCommand": ["first", "second", "operator", "attributes"],
    "HyperEdgeChain": ["inners", "contents", "attributes"],
    "GraphContextCommand": ["subcommand", "args", "kwargs", "flags"],
    "LetStatement": ["name", "expr"],
    "AsStatement": ["name", "expr"],
}


def canonical(value):
    if isinstance(value, set):
        return {"set": sorted(value)}
    if isinstance(value, list):
        return [canonical(v) for v in value]
    if isinstance(value, dict):
        return {k: canonical(v) for k, v in value.items()}
    if isinstance(value, (int, float)):
        return {"type": type(value).__name__, "value": value}
    name = type(value).__name__
    if name in FIELDS:
        return {"class": name, **{k: canonical(getattr(value, k)) for k in FIELDS[name]}}
    return value


BASELINE = json.loads(Path(__file__).with_name("legacy_frontend.json").read_text())
# User-approved syntax change: connection aliases require parentheses around
# the complete connection expression, including any connection attributes/tag.
ALIAS_CHANGES = {
    "A -- B tag as Alias\n",
    "A -- B as as Alias\n",
    "(A -- B) as Alias\n",
    "(A -- B tag) as Alias\n",
}


@pytest.fixture(scope="module")
def parser():
    return create_parser()


@pytest.mark.parametrize("case", BASELINE, ids=lambda case: repr(case["source"]))
def test_recorded_frontend(parser, case):
    if case["source"] in ALIAS_CHANGES:
        if case["source"].startswith("("):
            command = parser.parse(case["source"]).commands[0]
            assert type(command).__name__ == "AsStatement"
            assert command.name == "Alias"
        else:
            with pytest.raises(GMLangSyntaxError):
                parser.parse(case["source"])
    elif case.get("error") == "syntax":
        with pytest.raises(GMLangSyntaxError):
            parser.parse(case["source"])
    elif case.get("error") == "semantic":
        with pytest.raises(GMLangSemanticError) as error:
            parser.parse(case["source"])
        assert error.value.message == case["message"]
    else:
        assert canonical(parser.parse(case["source"])) == case["model"]
