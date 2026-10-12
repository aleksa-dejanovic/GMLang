# Graph-manipulation-language

[![Tests](https://github.com/aleksa-dejanovic/GMLang/actions/workflows/pytest.yml/badge.svg)](https://github.com/aleksa-dejanovic/GMLang/actions)

A language for graph definition and manipulation using parglare. Requires Python 3.13+.

```python
from gmlang import create_parser
from gmlang.interpreter.basic import BasicInterpreter

parser = create_parser()
model = parser.model_from_str('node A, B\n(A -> B [weight: 2]) as Link\n')
interpreter = BasicInterpreter()
interpreter.interpret(model.commands)
```

Commands must end with a newline. Node aliases use `node A as Alias`.
Connection aliases require parentheses around the complete edge expression,
including its tag or attributes: `(A -- B tag) as Alias`,
`(A -- B [weight: 2]) as Alias`, or `(*<- A *-> B) as Alias`.
Unparenthesized connection aliases are rejected. `let Alias be A -- B` remains valid.

Inline node attributes are greedy: in `node A -- node B [color: "red"]`,
the attributes belong to B. Use `node A -- (node B) [weight: 2]` to attach
attributes to the edge. Existing keyword-prefix syntax such as `nodeA` and
`graphcmd` remains accepted for compatibility.

`create_parser()` returns a sequentially reusable parser with
`model_from_str(text, file_name=...)`, `model_from_file(path)`, and public AST
class lookup through `parser["NodeCreationCommand"]`. `parse` and `parse_file`
are aliases for the model methods. Empty and whitespace-only input returns
`File(commands=[])`. Models use explicit dataclasses with source spans;
TextX navigation metadata and its metamodel registry are no longer provided.
The ordinary `gmlang_language()` factory remains as a compatibility alias.
Use separate parser instances for concurrent parsing.

Catch `GMLangSyntaxError`, `GMLangSemanticError`, or `GMLangAmbiguityError`
from `gmlang`; all derive from `GMLangError`. Syntax errors expose `file_name`,
`start_position`, `end_position`, `line`, `column`, and `expected` token names.
Line and column numbers are one-based; source offsets are zero-based.
The original parglare syntax exception is available through `__cause__`.

Graph execution remains separate from parsing. Existing `<>` execution behavior
and the interpreter's unsupported graph-context commands remain unchanged.

## Development

```bash
uv sync --frozen --group test
uv run --frozen --group test pytest
uv build
./generate_representation.sh
```

The representation script writes `parser-automaton.dot` and, when Graphviz's
`dot` is installed, `parser-automaton.png`. This depicts the GLR parser automaton,
not the former TextX metamodel/class diagram. It loads the same grammar and
custom literal recognizers as the parser. Parsing uses an in-memory grammar and
does not write parser-table caches beside installed package resources.

`tests/legacy_frontend.json` records 151 TextX 4.2.3 acceptance/error and public
AST cases from head `a9a59b5`. Tests retain numeric types, list order, sets,
attribute ownership, and semantic errors, with explicit exceptions for the
parenthesized connection-alias syntax. Empty models are normalized to a File.
