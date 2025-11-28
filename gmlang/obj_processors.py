def list_to_dict(l):
    return {elem.key: elem.value for elem in l}


def process_attributes(cmd):

    if not cmd.attr_list:
        if not cmd.tag:
            cmd.attributes = {}
        else:
            cmd.attributes = {"tag": cmd.tag}
    else:
        attr_list = cmd.attr_list.attributes
        cmd.attributes = list_to_dict(attr_list)
        del cmd.attr_list
    return cmd


def process_tag(cmd):

    cmd.attributes = {"tag": cmd.tag}
    return cmd


def process_kwargs(cmd):
    kwargs = {elem.key: elem.value for elem in cmd.kwargs if elem.value is not None}

    cmd.flags = set(elem.key for elem in cmd.kwargs if elem.value is None)
    cmd.kwargs = kwargs
    return cmd
