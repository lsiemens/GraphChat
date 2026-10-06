"""
Directed Acyclic Graph of NodeData
"""

from engine_graphchat.core import exceptions


class Graph:
    """Directed Acyclic Graph

    A Directed Acyclic Graph of node data. While it may in some cases be
    necessary to verify that the existing nodes remain a DAG. As long as the
    existing nodes are immutable and every new node only refers to existing
    nodes in the graph then after the addition the graph will still be a DAG.
    """

    def __init__(self):
        self.nodes = {}
        self.views = {"simple_dfs": self.topological_ordering}

    def add_node(self, node):
        for upstream_id in node.upstream:
            if upstream_id not in self.nodes:
                raise exceptions.NotFoundError("Upstream node does not exist in the graph")

        self.nodes[node.id] = node

    def validate(self):
        for node in self.nodes.values():
            if not node.validate():
                return False
        return True

    def topological_ordering(self, upstream):
        """List ancestor nodes subject to a topological sort

        Select the upstream subgraph (all nodes that the current node is
        dependent on). Including the target point this necessarily forms a
        connected DAG. Return the ids of the nodes in this graph subject to a
        topological sort. This topological sort uses a DFS (Cormen, Tarjan)

        Parameters
        ----------
        upstream : [string]
            A list of ids for upstream nodes.

        Returns
        -------
        Nodes : [NodeData]
            A list of NodeData with a topological ordering.
        """

        ordered = []
        visited = set()

        def visit(node_id):
            if node_id not in self.nodes:
                raise exceptions.NotFoundError("Upstream node does not exist in the graph")

            node = self.nodes[node_id]
            if node_id in ordered:
                return

            if node_id in visited:
                raise exceptions.InvalidGraphError("Cycle detected: the graph is not a DAG!")

            visited.add(node_id)

            for p_node_id in node.upstream:
                visit(p_node_id)

            visited.remove(node_id)
            ordered.append(node_id)

        for upstream_node_id in upstream:
            visit(upstream_node_id)

        return ordered

    def terminal_nodes(self, node_id):
        """Find the terminal descendant nodes
        """

        children = {}
        for c_node_id, node in self.nodes.items():
            for p_node_id in node.upstream:
                if p_node_id not in children:
                    children[p_node_id] = [c_node_id]
                else:
                    children[p_node_id] += [c_node_id]

        # BFS
        terminal_node_id = set()
        test_node_id = [node_id]

        while len(test_node_id) != 0:
            node_id = test_node_id.pop(0)

            if node_id not in children:
                terminal_node_id.add(node_id)
                continue

            test_node_id += children[node_id]

        return list(terminal_node_id)

    def is_topological_ordering(self, context):
        """Check if a proposed context is topologically ordered
        """
        partial_context = []
        for node_id in context:
            if node_id not in self.nodes:
                raise exceptions.NotFoundError("Context node does not exist in the graph")

            for upstream_id in self.nodes[node_id].upstream:
                if upstream_id not in partial_context:
                    return False
            partial_context.append(node_id)
        return True

    def is_valid_context(self, upstream, context):
        """Check that the upstream and context are compatible
        """

        if len(set(context)) != len(context):
            return False

        traversable = set()

        # DFS
        def visit(node_id):
            if node_id not in self.nodes:
                raise exceptions.NotFoundError("Upstream node does not exist in the graph")

            if node_id in traversable:
                return

            node = self.nodes[node_id]
            for p_node_id in node.upstream:
                visit(p_node_id)

            traversable.add(node_id)

        for p_node_id in upstream:
            visit(p_node_id)

        if traversable != set(context):
            return False

        return True
