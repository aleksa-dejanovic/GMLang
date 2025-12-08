from textx.exceptions import TextXSemanticError

from gmlang.graph.graph import Node, Edge, Graph


class BasicInterpreter:
    def __init__(self):
        self.variables = {}
        self._graph = Graph()

    def set_variable(self, name: str, value: object) -> bool:
        if name not in self.variables:
            self.variables[name] = value
            return True
        return False

    def get_variable(self, name: str) -> object:
        return self.variables.get(name, None)

    def update_variable(self, name, value) -> bool:
        if name in self.variables:
            self.variables[name] = value
            return True
        return False

    def interpret(self, commands: list) -> None:
        print("\nInterpreting commands...")
        for command in commands:
            self._execute_command(command)

    def _execute_command(self, command) -> None:
        handler_name: str = "_interpret_" + command.__class__.__name__
        handler = getattr(self, handler_name, None)
        if handler:
            handler(command)
        else:
            raise NotImplementedError(
                f"No handler for command type: {command.__class__.__name__}"
            )

    def _create_edges(
        self,
        source_nodes: list[Node],
        target_nodes: list[Node],
        directed: bool,
        attributes: dict[str, str],
    ) -> list[Edge]:
        edges = []
        for node1 in source_nodes:
            for node2 in target_nodes:
                edges.append(
                    Edge(
                        source=[node1],
                        target=[node2],
                        attributes=attributes,
                        directed=directed,
                    )
                )
        return edges

    def _interpret_NodeCreationCommand(self, command) -> None:
        for node in command.nodes:
            node_obj: Node = Node(id=node, attributes=command.attributes)
            ok = self.set_variable(node, node_obj)
            if not ok:
                raise TextXSemanticError(f"Node '{node}' already exists.")
            self._graph.add_node(node_obj)

        print(f"Creating nodes {[node for node in command.nodes]}")

    def _interpret_StandardConnectionCommand(self, command) -> None:

        for inner in (command.first, command.second):
            if inner.__class__.__name__.endswith("Command"):
                self._execute_command(inner)

        directed = (
            command.operator == "->"
            or command.operator == "<-"
            or command.operator == "<>"
        )
        if (
            command.operator == "--"
            or command.operator == "->"
            or command.operator == "<>"
        ):
            source_nodes = [self.get_variable(node) for node in command.first.nodes]
            target_nodes = [self.get_variable(node) for node in command.second.nodes]
        elif command.operator == "<-" or command.operator == "<>":
            source_nodes = [self.get_variable(node) for node in command.second.nodes]
            target_nodes = [self.get_variable(node) for node in command.first.nodes]
        edges = self._create_edges(
            source_nodes,
            target_nodes,
            directed,
            command.attributes,
        )
        if command.operator == "<>":
            edges += self._create_edges(
                target_nodes,
                source_nodes,
                directed,
                command.attributes,
            )
        for edge in edges:
            self._graph.add_edge(edge)
