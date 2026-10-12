"""GMLang graph definition and manipulation language."""

from gmlang.errors import (
    GMLangAmbiguityError,
    GMLangError,
    GMLangSemanticError,
    GMLangSyntaxError,
)
from gmlang.parser import GMLangParser, create_parser

__version__ = "0.1.0.dev"
__all__ = [
    "GMLangParser",
    "create_parser",
    "gmlang_language",
    "GMLangError",
    "GMLangSyntaxError",
    "GMLangSemanticError",
    "GMLangAmbiguityError",
]


def gmlang_language():
    """Compatibility factory; use create_parser() for new callers."""
    return create_parser()
