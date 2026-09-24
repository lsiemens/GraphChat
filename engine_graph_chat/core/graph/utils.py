"""
Utility functions for ./graph
"""

from core.graph import node
from core.llm import utils as llm_utils

def node_from_string(content, previous_node=None):
    model_name = ""
    upstream = []
    if previous_node is not None:
        model_name = previous_node.model
        upstream = [previous_node.id]

    node_request = node.NodeRequest(llm_utils.get_timestamp(), content)

    node_data = node.NodeData("", model_name, upstream, node_request, None)
    return node_data
