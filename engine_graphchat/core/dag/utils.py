"""
Utility functions for ./graph
"""

from . import node
from engine_graphchat.core.llm import utils


def node_from_string(content, model_name, previous_node_id=None):
    upstream = []
    if previous_node_id is not None:
        upstream = [previous_node_id]

    node_request = node.NodeRequest(utils.get_timestamp(), content)

    node_data = node.NodeData("", model_name, upstream, node_request, None)
    return node_data
