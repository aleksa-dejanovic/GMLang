#!/bin/bash

# This script generates a representation of the current language structure

textx generate --target PlantUML ./gmlang/grammar/grammar.tx -o .

plantuml grammar.pu

rm grammar.pu