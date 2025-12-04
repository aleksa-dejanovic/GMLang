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
    node_set.nodes = set((node.value for node in node_set.nodes))


def process_nodes(cmd):
    nodes = set((node.value for node in cmd.nodes))
    del cmd.nodes
    return nodes


def process_infix_connection(cmd):
    cmd.operator = cmd.l_opr + cmd.r_opr
    del cmd.l_opr
    del cmd.r_opr
    process_tag(cmd)
