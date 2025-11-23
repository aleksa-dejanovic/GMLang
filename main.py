from textx import metamodel_from_file

metamodel = metamodel_from_file("grammar.tx")

model = metamodel.model_from_file("document.dsl")

for cmd in model.commands:
    print(f"{cmd.first.value} {cmd.operator} {cmd.second.value}")
