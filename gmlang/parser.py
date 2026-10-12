"""Small parsing facade with explicit compatibility disambiguation."""

from importlib.resources import files
from pathlib import Path

from parglare import GLRParser, Grammar
from parglare import SyntaxError as ParglareSyntaxError

from gmlang.actions import ACTIONS
from gmlang.ast import AST_TYPES
from gmlang.errors import GMLangSyntaxError
from gmlang.literals import RECOGNIZERS


def create_grammar():
    return Grammar.from_string(
        files("gmlang").joinpath("grammar", "grammar.pg").read_text(encoding="utf-8"),
        recognizers=RECOGNIZERS,
    )


class GMLangParser:
    """Reusable sequential parser; use separate instances for concurrent parses."""

    def __init__(self):
        self._parser = GLRParser(
            create_grammar(),
            actions=ACTIONS,
            ws="\t \r",
            consume_input=True,
            lexical_disambiguation=False,
            prefer_shifts=False,
            prefer_shifts_over_empty=False,
            error_recovery=False,
        )

    def model_from_str(self, text, *, file_name=None):
        try:
            forest = self._parser.parse(text, file_name=file_name)
        except ParglareSyntaxError as exc:
            start = exc.location.start_position
            raise GMLangSyntaxError(
                str(exc),
                file_name=file_name,
                start_position=start,
                end_position=exc.location.end_position,
                line=text.count("\n", 0, start) + 1,
                column=start - text.rfind("\n", 0, start),
                expected=sorted(s.name for s in exc.symbols_expected),
            ) from exc
        from gmlang.disambiguation import select_legacy_tree

        return self._parser.call_actions(select_legacy_tree(forest))

    def model_from_file(self, file_name):
        path = Path(file_name)
        # Preserve CRLF offsets rather than using universal newline translation.
        with path.open(encoding="utf-8", newline="") as stream:
            return self.model_from_str(stream.read(), file_name=str(path))

    def __getitem__(self, name):
        return AST_TYPES[name]

    parse = model_from_str
    parse_file = model_from_file


def create_parser():
    return GMLangParser()
