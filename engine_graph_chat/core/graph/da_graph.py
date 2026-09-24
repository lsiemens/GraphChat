"""
Directed Acyclic Graph of NodeData
"""

#try:
#    from uuid import uuid7
#except ImportError:
#    from uuid6 import uuid7


class GraphError(Exception):
    pass


class DAGraph:
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
