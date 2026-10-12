"""Construct normalized ASTs after syntax disambiguation has completed."""

from gmlang import ast
from gmlang.errors import GMLangSemanticError
from gmlang.literals import number_value, string_value


def span(context):
    return ast.SourceSpan(context.start_position, context.end_position, context.file_name)


def passthrough(context, nodes):
    return nodes[0]


def file_action(context, nodes, commands):
    return ast.File([c for c in commands if c is not None], span=span(context))


def line(context, nodes):
    return nodes[0] if len(nodes) == 2 else None


def nodes_action(context, nodes):
    return nodes[1] if len(nodes) == 3 else nodes[0]


def node_set(context, nodes, names):
    return ast.NodeSet(
        {names} if isinstance(names, str) else set(names), span=span(context)
    )


def node_creation(context, nodes, names, attr_list):
    return ast.NodeCreationCommand(names, attr_list or {}, span=span(context))


def standard(context, nodes, scc, suffix):
    return ast.StandardConnectionCommand(*scc, suffix or {}, span=span(context))


def infix(context, nodes, first, l_opr, tag, r_opr, second):
    return ast.InfixConnectionCommand(
        first, l_opr + r_opr, second, {"tag": tag}, span=span(context)
    )


def suffix(context, nodes, attributes=None, tag=None):
    return attributes if attributes is not None else {"tag": tag}


def graph_context(context, nodes, subcommand, args, options):
    return ast.GraphContextCommand(
        subcommand,
        args,
        {k: v for k, v in options if v is not None},
        {k for k, v in options if v is None},
        span=span(context),
    )


def hyperedge(context, nodes, edges, attr_list):
    partition = {"*--": "undirected", "*<-": "source", "*->": "target"}
    contents = {key: set() for key in partition.values()}
    for operator, inner in edges:
        keys = ("source", "target") if operator == "<*>" else (partition[operator],)
        for key in keys:
            contents[key].update(inner.nodes)
    if contents["undirected"] and (contents["source"] or contents["target"]):
        raise GMLangSemanticError(
            "Hyperedge cannot have both source nodes and target/undirected nodes.",
            file_name=context.file_name,
            start_position=context.start_position,
            end_position=context.end_position,
        )
    return ast.HyperEdgeChain(
        [inner for _, inner in edges], contents, attr_list or {}, span=span(context)
    )


def let_statement(context, nodes, name, expr):
    return ast.LetStatement(name, expr, span=span(context))


def as_statement(context, nodes, name, expr):
    return ast.AsStatement(name, expr, span=span(context))


ACTIONS = {
    name: passthrough
    for name in (
        "Command",
        "Expression",
        "GraphDefinitionCommand",
        "ConnectionCommand",
        "AttributeKey",
        "AttributeValue",
        "Parameter",
    )
}
ACTIONS.update(
    {
        "File": file_action,
        "Line": line,
        "Nodes": nodes_action,
        "NodeSet": node_set,
        "NodeList": lambda c, n: set(n[0]),
        "NodeCreationCommand": node_creation,
        "Attribute": lambda c, n, key, value: (key, value),
        "AttributeList": lambda c, n, attributes: dict(attributes),
        "SCCNoAttributes": lambda c, n, first, operator, second: (
            first,
            operator,
            second,
        ),
        "StandardConnectionCommand": standard,
        "InfixConnectionCommand": infix,
        "ConnectionSuffix": suffix,
        "GraphContextCommand": graph_context,
        "KWParameter": lambda c, n, key, value: (key, value),
        "HyperEdge": lambda c, n, operator, inner: (operator, inner),
        "HyperEdgeChain": hyperedge,
        "LetStatement": let_statement,
        "AsStatement": as_statement,
        "STRING": string_value,
        "NUMBER": number_value,
    }
)
