#!/bin/bash

# This script generates a representation of the current language structure

textx generate --target dot ./gmlang/grammar/grammar.tx -o .

dot -Tpng grammar.dot -o grammar.png

rm grammar.dot