"""
Utility functions for ./graph
"""

from . import node
from engine_graphchat.core.llm import utils


def empty_node(model_name):
    node_request = node.NodeRequest(utils.get_timestamp(), "")
    node_data = node.NodeData(None, model_name, [], node_request, None)
    return node_data


def copy_node(target_node):
    node_request = node.NodeRequest(utils.get_timestamp(), target_node.request.content)
    node_data = node.NodeData(None, target_node.model, target_node.upstream, node_request, None)
    return node_data


def node_from_string(content, model_name, previous_node_id=None):
    upstream = []

    if previous_node_id is not None:
        upstream = [previous_node_id]

    node_request = node.NodeRequest(utils.get_timestamp(), content)

    node_data = node.NodeData(None, model_name, upstream, node_request, None)
    return node_data
