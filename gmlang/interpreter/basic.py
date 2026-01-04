import contextlib
from typing import Literal, overload

from textx.exceptions import TextXSemanticError

from gmlang.graph.graph import Edge, Graph, Hyperedge, Node


class BasicInterpreter:
    def __init__(self, verbose=False):
        self._verbose = verbose
        self._variables = {}
        self._graph = Graph()

    def _set_variable(self, name: str, value: object) -> None:
        if name not in self._variables:
            if self._verbose:
                print(f"Setting variable name {name} to value {value}")
            self._variables[name] = value
        else:
            raise TextXSemanticError(f"Overwriting an existing alias {name}")

    @overload
    def get_variable(self, name: str, forgive: Literal[False] = False) -> object: ...
    @overload
    def get_variable(self, name: str, forgive: Literal[True]) -> object | None: ...

    def get_variable(self, name: str, forgive: bool = False) -> object | None:
        try:
            got = self._variables[name]
            if self._verbose:
                print(f"Getting variable {name}, got {got}")
            return got
        except KeyError as e:
            if forgive:
                return None
            raise TextXSemanticError(f"Using a non-declared alias {name}") from e


    def interpret(self, commands: list) -> None:
        print("\nInterpreting commands...")
        for command in commands:
            self._execute_command(command)

    def _execute_command(self, command) -> object:
        handler_name: str = "_interpret_" + command.__class__.__name__
        handler = getattr(self, handler_name, None)
        if handler:
            if self._verbose:
                print(f"Calling method {handler_name}")
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
            self._set_variable(node, node_obj)
            self._graph.add_node(node_obj)
        if self._verbose:
            print(f"Creating nodes {[node for node in command.nodes]}")
        return nodes

    def _interpret_StandardConnectionCommand(self, command) -> list[Edge]:

        for inner in (command.first, command.second):
            with contextlib.suppress(NotImplementedError):
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
            with contextlib.suppress(NotImplementedError):
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
            with contextlib.suppress(NotImplementedError):
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
        try:
            value = self._execute_command(command.expr)
        except NotImplementedError:
            value = command.expr
        self._set_variable(command.name, value)
        return value
    
    def _interpret_AsStatement(self, command) -> object:
        try:
            value = self._execute_command(command.expr)
        except NotImplementedError:
            value = command.expr
        self._set_variable(command.name, value)
        return value