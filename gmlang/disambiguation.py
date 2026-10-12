"""Local packed-forest pruning for greedy inline-node attribute ownership.

Only the known node/outer-connection ownership conflict is resolved. Unrecognized
ambiguities fail explicitly, before any AST or interpreter actions run.
"""

from parglare.glr import Parent

from gmlang.errors import GMLangAmbiguityError


def _profile(root):
    tokens, declarations, attributes = [], [], []
    stack = [(root, None)]
    while stack:
        node, owner = stack.pop()
        if isinstance(node, Parent):
            if len(node.possibilities) != 1:
                return None
            stack.append((node.possibilities[0], owner))
            continue
        if node.is_term():
            tokens.append((node.symbol.name, node.start_position, node.value))
            continue
        name = node.symbol.name
        if name in ("NodeCreationCommand", "StandardConnectionCommand", "HyperEdgeChain"):
            owner = (name, node.start_position)
        if name == "NodeCreationCommand":
            declarations.append((node.start_position, node.end_position))
        if name == "AttributeList":
            attributes.append((node.start_position, node.end_position, owner))
            continue
        stack.extend((child, owner) for child in reversed(node.children))
    return tokens, declarations, attributes


def _prune(parent):
    candidates = parent.possibilities
    names = {node.symbol.name for node in candidates}
    profiles = [_profile(node) for node in candidates]
    known = names in ({"StandardConnectionCommand"}, {"HyperEdgeChain"})
    if known and all(profile is not None for profile in profiles):
        tokens, declarations, attributes = profiles[0]
        same_syntax = all(
            p[0] == tokens
            and [start for start, _ in p[1]] == [start for start, _ in declarations]
            and [(a, b) for a, b, _ in p[2]] == [(a, b) for a, b, _ in attributes]
            for p in profiles
        )
        changed = []
        if same_syntax:
            for index, (start, end, _) in enumerate(attributes):
                owners = {p[2][index][2] for p in profiles}
                if len(owners) > 1:
                    outer = (next(iter(names)), parent.start_position)
                    inner = [o for o in owners if o[0] == "NodeCreationCommand"]
                    # The same list may move only between the outer command and
                    # its final unparenthesized inline declaration.
                    if len(owners) != 2 or outer not in owners or len(inner) != 1:
                        same_syntax = False
                        break
                    node_start = inner[0][1]
                    for p in profiles:
                        node_end = dict(p[1])[node_start]
                        owns = p[2][index][2] == inner[0]
                        if (owns and node_end != end) or (not owns and node_end > start):
                            same_syntax = False
                    changed.append(index)
        if same_syntax and changed:
            ranks = [tuple((start, -end) for start, end in p[1]) for p in profiles]
            best = min(ranks)
            winners = [
                c for c, rank in zip(candidates, ranks, strict=True) if rank == best
            ]
            if len(winners) == 1:
                parent.possibilities[:] = winners
                return
    raise GMLangAmbiguityError(
        "Unresolved syntax ambiguity: " + ", ".join(sorted(names)),
        file_name=parent.file_name,
        start_position=parent.start_position,
        end_position=parent.end_position,
    )


def select_legacy_tree(forest):
    # disambiguate visits packed nodes bottom-up with memoization; it does not
    # enumerate the product of whole-document alternatives.
    forest.disambiguate(_prune)
    if forest.solutions != 1:
        raise GMLangAmbiguityError("Expected one syntax interpretation after pruning")
    return forest.get_tree()
