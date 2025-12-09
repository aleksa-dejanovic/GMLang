from textx import TextXSemanticError


def list_to_dict(l):
    return {elem.key: elem.value for elem in l}


def process_attributes(cmd):
    import pdb

    if not cmd.attr_list:
        try:
            if not cmd.tag:
                cmd.attributes = {}
            else:
                cmd.attributes = {"tag": cmd.tag}
        except AttributeError:
            cmd.attributes = {}
    else:
        attr_list = cmd.attr_list.attributes
        cmd.attributes = list_to_dict(attr_list)
        del cmd.attr_list


def process_tag(cmd):

    cmd.attributes = {"tag": cmd.tag}


def process_kwargs(cmd):
    kwargs = {elem.key: elem.value for elem in cmd.kwargs if elem.value is not None}

    cmd.flags = set(elem.key for elem in cmd.kwargs if elem.value is None)
    cmd.kwargs = kwargs


def process_node_set(node_set):
    node_set.nodes = set((node for node in node_set.nodes))


def process_nodes(cmd):
    nodes = set((node for node in cmd.nodes))
    del cmd.nodes
    return nodes


def process_infix_connection(cmd):
    cmd.operator = cmd.l_opr + cmd.r_opr
    del cmd.l_opr
    del cmd.r_opr
    process_tag(cmd)


def process_standard_connection(cmd):
    process_attributes(cmd)
    cmd.first = cmd.scc.first
    cmd.second = cmd.scc.second
    cmd.operator = cmd.scc.operator
    del cmd.scc


def process_hyperedge_chain(cmd):
    process_attributes(cmd)
    operators = {"*--": "undirected", "*->": "target", "*<-": "source"}
    cmd.inners = [edge.inner for edge in cmd.edges]
    cmd.contents = {
        op: {
            node
            for edge in cmd.edges
            for node in edge.inner.nodes
            if operators.get(edge.operator) == op
            or (edge.operator == "<*>" and op in ("source", "target"))
        }
        for op in operators.values()
    }
    del cmd.edges

    if cmd.contents["undirected"] and (
        cmd.contents["target"] or cmd.contents["source"]
    ):
        raise TextXSemanticError(
            "Hyperedge cannot have both source nodes and target/undirected nodes."
        )
