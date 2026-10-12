"""Normalized syntax models consumed by the interpreter."""

from dataclasses import dataclass, field


@dataclass(frozen=True)
class SourceSpan:
    start: int
    end: int
    file_name: str | None = None


@dataclass(kw_only=True)
class SyntaxNode:
    span: SourceSpan | None = field(default=None, compare=False)


@dataclass
class File(SyntaxNode):
    commands: list = field(default_factory=list)


@dataclass
class NodeSet(SyntaxNode):
    nodes: set[str] = field(default_factory=set)


@dataclass
class NodeCreationCommand(NodeSet):
    attributes: dict = field(default_factory=dict)


@dataclass
class StandardConnectionCommand(SyntaxNode):
    first: NodeSet
    operator: str
    second: NodeSet
    attributes: dict = field(default_factory=dict)


@dataclass
class InfixConnectionCommand(StandardConnectionCommand):
    pass


@dataclass
class HyperEdgeChain(SyntaxNode):
    inners: list[NodeSet] = field(default_factory=list)
    contents: dict[str, set[str]] = field(default_factory=dict)
    attributes: dict = field(default_factory=dict)


@dataclass
class GraphContextCommand(SyntaxNode):
    subcommand: str
    args: list[str | int | float] = field(default_factory=list)
    kwargs: dict = field(default_factory=dict)
    flags: set[str] = field(default_factory=set)


@dataclass
class LetStatement(SyntaxNode):
    name: str
    expr: NodeCreationCommand | StandardConnectionCommand | HyperEdgeChain


@dataclass
class AsStatement(LetStatement):
    pass


AST_TYPES = {
    cls.__name__: cls
    for cls in (
        File,
        NodeSet,
        NodeCreationCommand,
        StandardConnectionCommand,
        InfixConnectionCommand,
        HyperEdgeChain,
        GraphContextCommand,
        LetStatement,
        AsStatement,
    )
}
