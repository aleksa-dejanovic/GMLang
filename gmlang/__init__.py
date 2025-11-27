import os
from textx import language, metamodel_from_file

from gmlang import obj_processors

__version__ = "0.1.0.dev"


@language("gmlang", "*.gml")
def gmlang_language():
    "gmlang language"
    current_dir = os.path.dirname(__file__)
    mm = metamodel_from_file(os.path.join(current_dir, "grammar", "grammar.tx"))

    # Here if necessary register object processors or scope providers
    # http://textx.github.io/textX/stable/metamodel/#object-processors
    # http://textx.github.io/textX/stable/scoping/

    mm.register_obj_processors(
        {
            "StandardConnectionCommand": obj_processors.process_attributes,
            "InfixConnectionCommand": obj_processors.process_tag,
        }
    )

    return mm
