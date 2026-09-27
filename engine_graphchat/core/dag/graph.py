"""
Directed Acyclic Graph of NodeData
"""


class GraphError(Exception):
    pass


class Graph:
    """Directed Acyclic Graph

    A Directed Acyclic Graph of node data. While it may in some cases be
    nessissary to varify that the existing nodes remain a DAG. As long as the
    existing nodes are imutable and every new node only refers to existing
    nodes in the graph then after the addition the graph will still be a DAG.
    """

    def __init__(self):
        self.nodes = {}

    def add_node(self, node):
        for upstream_id in node.upstream:
            if upstream_id not in self.nodes:
                raise GraphError("Error: Upstream node does not exist!")

        self.nodes[node.id] = node

    def topological_ordering(self, upstream):
        """List ancestor nodes subject to a toplological sort

        Select the upstream subgraph (all nodes that the current node is
        dependent on). Including the target point this necessarily forms a
        connected DAG. Return the ids of the nodes in this graph subject to a
        topological sort. This topological sort uses a DFS (Corment et al)

        Parameters
        ----------
        upstream : [string]
            A list of ids for upstream nodes.

        Returns
        -------
        Nodes : [NodeData]
            A list of NodeData with a topological ordering.
        """

        L = []
        visited = set()

        def visit(node_id):
            if node_id not in self.nodes:
                raise GraphError("Nodes reference elements not in the DAG.")

            node = self.nodes[node_id]
            if node_id in L:
                return

            if node_id in visited:
                raise GraphError("Cycle detected, the graph is not a DAG!")

            visited.add(node_id)

            for p_node_id in node.upstream:
                visit(p_node_id)

            visited.remove(node_id)
            L.append(node_id)

        for upstream_node_id in upstream:
            visit(upstream_node_id)

        return [self.nodes[node_id] for node_id in L]

    def terminal_nodes(self, node_id):
        """Find the terminal decendant nodes
        """

        children = {}
        for node_id, node in self.nodes.items():
            for p_node_id in node.upstream:
                if p_node_id not in children:
                    children[p_node_id] = [node_id]
                else:
                    children[p_node_id] += [node_id]

        # BFS
        terminal_node_id = set()
        test_node_id = [node_id]

        while len(test_node_id) != 0:
            node_id = test_node_id.pop(0)

            if node_id not in children:
                terminal_node_id.add(node_id)
                continue

            test_node_id += children[node_id]
        return [self.nodes[node_id] for node_id in terminal_node_id]
