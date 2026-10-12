#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"

# Export the parser automaton using production literal recognizers.
uv run --frozen python - <<'PY'
from parglare.export import grammar_pda_export
from gmlang import create_parser

grammar_pda_export(create_parser()._parser.table, "parser-automaton.dot")
PY

if command -v dot >/dev/null 2>&1; then
    dot -Tpng parser-automaton.dot -o parser-automaton.png
else
    printf '%s\n' 'Created parser-automaton.dot; install Graphviz to render the PNG.'
fi
