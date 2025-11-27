def process_attributes(cmd):

    def list_to_dict(l):
        dic = {}
        for elem in l:
            key = elem.key
            value = elem.value
            dic[key] = value
        return dic

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
