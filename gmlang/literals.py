"""TextX 4.2.3-compatible literal recognition and conversion."""

import re

_STRING = re.compile(r"""("(\\"|[^"])*")|('(\\'|[^'])*')""")
_FLOAT = re.compile(
    r"[+-]?(((\d+\.(\d*)?|\.\d+)([eE][+-]?\d+)?)|"
    r"((\d+)([eE][+-]?\d+)))(?<=[\w\.])(?![\w\.])"
)
_INT = re.compile(r"[-+]?[0-9]+")


def recognize_string(text, position):
    match = _STRING.match(text, position)
    return match.group() if match else None


def recognize_number(text, position):
    match = _FLOAT.match(text, position) or _INT.match(text, position)
    return match.group() if match else None


def string_value(context, value):
    return value[1:-1].replace(r"\"", '"').replace(r"\'", "'")


def number_value(context, value):
    return float(value) if _FLOAT.fullmatch(value) else int(value)


RECOGNIZERS = {"STRING": recognize_string, "NUMBER": recognize_number}
