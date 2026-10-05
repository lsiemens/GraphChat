"""
Utility functions for ./graph
"""

from . import node
from engine_graphchat.core.llm import utils


def empty_node(model_name):
    node_request = node.NodeRequest(utils.get_timestamp(), [], "")
    node_data = node.NodeData(None, model_name, [], node_request, None)
    return node_data


def copy_node(target_node):
    model = target_node.model
    upstream = target_node.upstream[:]
    request_context = target_node.request.context[:]
    request_content = target_node.request.content

    node_request = node.NodeRequest(utils.get_timestamp(), request_context, request_content)
    node_data = node.NodeData(None, model, upstream, node_request, None)
    return node_data
