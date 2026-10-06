"""
Manage the dialogue between the user and LLM agent
"""

import logging

from engine_graphchat.core import exceptions
from engine_graphchat.core.dag import graph
from engine_graphchat.core.dag import utils as graph_utils
from engine_graphchat.core.llm import llm_service
from engine_graphchat.core.llm import utils as llm_utils


logger = logging.getLogger(__name__)


class DialogueManager:
    """Manage the interaction between the user, graph and LLM agent

    Due to similarities in the underlying model this class will be based on Git
    semantics.
    """

    def __init__(self, model_name):
        self.graph = graph.Graph()
        self.llm_service = llm_service.LLM_Service()
        self._chat = None

        self._HEAD = None

        if model_name is None:
            model_name = self.llm_service.get_model_names()[0]

        self._state = graph_utils.empty_node(model_name)

    def COMMIT(self):
        """Commit the current state

        Generate a response from the LLM and as a node to the graph.
        """
        messages = []
        for node_id in self._state.request.context:
            node = self.graph.nodes[node_id]
            # note node_to_xAI_messages produces a pair of messages but messages
            # for new_chat must be a flat list
            messages += llm_service.node_to_xAI_messages(node)

        self.chat = self.llm_service.new_chat(self._state.model, messages)
        reply = self.chat.send_node_request(self._state.request)
        self._state.reply = reply
        self._state.id = self._state.hash()

        self._HEAD = None
        node_data = self._state
        self.graph.add_node(node_data)

        self._state = graph_utils.empty_node(node_data.model)
        upstream = [node_data.id]
        context = node_data.request.context + [node_data.id]
        self.set_context(upstream, context)

        return node_data

    def CHECKOUT(self, target):
        """Checkout a node

        Parameters
        ----------
        target : string
            The ID or ID prefix of the node to checkout
        """
        # checkout TIP
        if target.strip() == "tip":
            if self._HEAD is None:
                # you are already at a tip
                return

            if self._HEAD not in self.graph.nodes:
                raise exceptions.NotFoundError("_HEAD node does not exist in the graph")

            tip_node_ids = self.graph.terminal_nodes(self._HEAD)
            if len(tip_node_ids) == 0:
                raise exceptions.NotFoundError("No tip node found")
            if len(tip_node_ids) > 1:
                raise exceptions.InvalidGraphError(f"Tip node is not unique: the graph branches into {len(tip_node_ids)} possible tips")
            tip_node = self.graph.nodes[tip_node_ids[0]]

            # configure the state like just after a commit
            self._HEAD = None
            self._state = graph_utils.empty_node(tip_node.model)

            upstream = [tip_node.id]
            context = tip_node.request.context + [tip_node.id]
            self.set_context(upstream, context)
            return

        node = self.graph.nodes[self._get_ID(target)]

        self._HEAD = node.id
        self._state = graph_utils.copy_node(node)

    def MERGE(self, target):
        """Merge nodes

        Parameters
        ----------
        target : string or list
            If `target` is a single string, the node with that ID or ID prefix
            will be merged into the current state. If `target` is a list, then
            each node IDs or ID prefixes will be merged into the current state.
        """
        upstream = self._state.upstream[:]
        if isinstance(target, list):
            upstream += [self._get_ID(id_prefix) for id_prefix in target]
        else:
            upstream.append(self._get_ID(target))

        self.set_upstream(upstream)

    def LOG(self):
        return self._state.request.context

    def set_prompt(self, prompt, timestamp=None):
        self._state.request.content = prompt

        if timestamp is None:
            self._state.request.timestamp = llm_utils.get_timestamp()
        else:
            self._state.request.timestamp = timestamp

    def set_model(self, model_name):
        self._state.model = model_name

    def set_context(self, upstream, context):
        upstream = [self._get_ID(id_prefix) for id_prefix in upstream]
        context = [self._get_ID(id_prefix) for id_prefix in context]

        if not self.graph.is_valid_context(upstream, context):
            raise exceptions.InvalidNodeError("The context is incompatible with the provided upstream nodes")

        if not self.graph.is_topological_ordering(context):
            raise exceptions.InvalidNodeError("The context must be topologically ordered")

        self._HEAD = None
        self._state.upstream = upstream
        self._state.request.context = context

    def set_upstream(self, upstream):
        upstream = [self._get_ID(id_prefix) for id_prefix in upstream]
        context = self.graph.topological_ordering(upstream)

        self.set_context(upstream, context)

    def _get_ID(self, target):
        target = target.strip()

        if target in self.graph.nodes:
            return target

        options = [node_id for node_id in self.graph.nodes if node_id.startswith(target)]

        if len(options) == 0:
            raise exceptions.NotFoundError(f"Node ID \"{target}\" did not match any know nodes")

        if len(options) > 1:
            raise exceptions.NotFoundError(f"Node ID \"{target}\" match was not unique, use a longer prefix")

        return options[0]
