"""Public parser and interpreter errors, independent of the frontend library."""


class GMLangError(Exception):
    def __init__(
        self,
        message,
        *,
        file_name=None,
        start_position=None,
        end_position=None,
        line=None,
        column=None,
        expected=(),
    ):
        super().__init__(message)
        self.message = message
        self.file_name = file_name
        self.start_position = start_position
        self.end_position = end_position
        self.line = line
        self.column = column
        self.expected = tuple(expected)


class GMLangSyntaxError(GMLangError):
    pass


class GMLangSemanticError(GMLangError):
    pass


class GMLangAmbiguityError(GMLangError):
    pass
