from textx.exceptions import TextXSemanticError

from gmlang.graph.graph import Node, Edge, Graph, Hyperedge


class BasicInterpreter:
    def __init__(self):
        self.variables = {}
        self._graph = Graph()

    def set_variable(self, name: str, value: object) -> bool:
        if name not in self.variables:
            self.variables[name] = value
            return True
        return False

    def get_variable(self, name: str, forgive=False) -> object:
        got = self.variables.get(name, None)
        if got is None and not forgive:
            raise TextXSemanticError("Using a non-declared alias")
        return got

    def update_variable(self, name, value) -> bool:
        if name in self.variables:
            self.variables[name] = value
            return True
        return False

    def interpret(self, commands: list) -> None:
        print("\nInterpreting commands...")
        for command in commands:
            self._execute_command(command)

    def _execute_command(self, command) -> object:
        handler_name: str = "_interpret_" + command.__class__.__name__
        handler = getattr(self, handler_name, None)
        if handler:
            res = handler(command)
        else:
            raise NotImplementedError(
                f"No handler for command type: {command.__class__.__name__}"
            )
        
        return res

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
                        source=node1,
                        target=node2,
                        attributes=attributes,
                        directed=directed,
                    )
                )
        return edges

    def _interpret_NodeCreationCommand(
            self,
            command,
            )-> list["Node"] | None:
        nodes = []
        for node in command.nodes:
            node_obj: Node = Node(id=node, attributes=command.attributes)
            nodes.append(node_obj)
            ok = self.set_variable(node, node_obj)
            if not ok:
                raise TextXSemanticError(f"Node '{node}' already exists.")
            self._graph.add_node(node_obj)

        print(f"Creating nodes {[node for node in command.nodes]}")
        return nodes

    def _interpret_StandardConnectionCommand(self, command) -> list[Edge]:

        for inner in (command.first, command.second):
            if inner.__class__.__name__.endswith("Command"):
                self._execute_command(inner)

        directed = command.operator in ("->", "<-", "<>")

        source_nodes = []
        target_nodes = []
        if command.operator in ("--", "->", "<>"):
            source_nodes.extend(
                [self.get_variable(node) for node in command.first.nodes]
            )
            target_nodes.extend(
                [self.get_variable(node) for node in command.second.nodes]
            )

        elif command.operator in ("<-", "<>"):
            source_nodes.extend(
                [self.get_variable(node) for node in command.second.nodes]
            )
            target_nodes.extend(
                [self.get_variable(node) for node in command.first.nodes]
            )

        edges = self._create_edges(
            source_nodes,
            target_nodes,
            directed,
            command.attributes,
        )
        for edge in edges:
            self._graph.add_edge(edge)

        return edges

    def _interpret_InfixConnectionCommand(self, command) -> list[Edge]:

        for inner in (command.first, command.second):
            if inner.__class__.__name__.endswith("Command"):
                self._execute_command(inner)

        directed = command.operator in ("->", "<-", "<>")
        source_nodes = []
        target_nodes = []
        if command.operator in ("--", "->", "<>"):
            source_nodes.extend(
                [self.get_variable(node) for node in command.first.nodes]
            )
            target_nodes.extend(
                [self.get_variable(node) for node in command.second.nodes]
            )
        elif command.operator in ("<-", "<>"):
            source_nodes.extend(
                [self.get_variable(node) for node in command.second.nodes]
            )
            target_nodes.extend(
                [self.get_variable(node) for node in command.first.nodes]
            )
        edges = self._create_edges(
            source_nodes,
            target_nodes,
            directed,
            command.attributes,
        )
        for edge in edges:
            self._graph.add_edge(edge)
        
        return edges

    def _interpret_HyperEdgeChain(self, command) -> Hyperedge:
        for inner in command.inners:
            if inner.__class__.__name__.endswith("Command"):
                self._execute_command(inner)
        if command.contents["undirected"]:
            source = [
                self.get_variable(node) for node in command.contents["undirected"]
            ]
            target = []
        else:
            source = [self.get_variable(node) for node in command.contents["source"]]
            target = [self.get_variable(node) for node in command.contents["target"]]
        he = Hyperedge(source, target, command.attributes)
        self._graph.add_hyperedge(he)

        return he
    
    def _interpret_LetStatement(self, command) -> object:
        if command.expr.__class__.__name__.endswith("Command"):
            value = self._execute_command(command.expr)
        else:
            value = command.expr
        self.set_variable(command.name, value)
        print("SACUVANO JE IME ", command.name, "I VREDNOST ", end="")
        print(self.get_variable(command.name))
        return value

