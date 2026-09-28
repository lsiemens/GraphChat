"""
Manage the dialogue between the user and LLM agent
"""

import logging

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
        self._messages = []

        if model_name is None:
            model_name = self.llm_service.get_model_names()[0]

        self._state = graph_utils.empty_node(model_name)

    def COMMIT(self):
        """Commit the current state

        Generate a response from the LLM and as a node to the graph.
        """
        self.chat = self.llm_service.new_chat(self._state.model, self._messages)
        reply = self.chat.send_node_request(self._state.request)
        self._state.reply = reply
        self._state.id = self._state.hash()

        self._HEAD = None
        node_data = self._state
        self.graph.add_node(node_data)
        self._state = graph_utils.empty_node(node_data.model)
        self._state.upstream = [node_data.id]
        self._update()
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
                raise ValueError("_HEAD is not in the graph!")

            tip_nodes = self.graph.terminal_nodes(self._HEAD)
            if len(tip_nodes) != 1:
                raise ValueError("No unique tip node")
            tip_node = tip_nodes[0]

            # configure the state like just after a commit
            self._HEAD = None
            self._state = graph_utils.empty_node(tip_node.model)
            self._state.upstream = [tip_node.id]
            self._update()
            return

        node = self.graph.nodes[self._get_ID(target)]

        self._HEAD = node.id
        self._state = graph_utils.copy_node(node)
        self._update()

    def MERGE(self, target):
        """Merge nodes

        Parameters
        ----------
        target : string or list
            If `target` is a single string, the node with that ID or ID prefix
            will be merged into the current state. If `target` is a list, then
            each node IDs or ID prefixes will be merged into the current state.
        """
        if isinstance(target, list):
            self._state.upstream += [self._get_ID(id_prefix) for id_prefix in target]
        else:
            self._state.upstream.append(self._get_ID(target))
        self._update()

    def LOG(self):
        return self.graph.topological_ordering(self._state.upstream)

    def set_prompt(self, prompt, timestamp=None):
        self._state.request.content = prompt

        if timestamp is None:
            self._state.request.timestamp = llm_utils.get_timestamp()
        else:
            self._state.request.timestamp = timestamp

    def set_model(self, model_name):
        self._state.model = model_name

    def set_upstream(self, upstream):
        upstream = [self._get_ID(id_prefix) for id_prefix in upstream]

        self._HEAD = None
        self._state.upstream = upstream
        self._update()

    def _update(self):
        """Keep _messages up to date with the current settings
        """
        self._messages = []
        sorted_nodes = self.graph.topological_ordering(self._state.upstream)
        for node in sorted_nodes:
            self._messages += llm_service.node_to_xAI_messages(node)

    def _get_ID(self, target):
        target = target.strip()

        if target in self.graph.nodes:
            return target

        options = [node_id for node_id in self.graph.nodes if node_id.startswith(target)]

        if len(options) == 0:
            raise ValueError(f"Node ID \"{target}\" did not match any know nodes")

        if len(options) > 1:
            raise ValueError(f"Node ID \"{target}\" match was not unique, use a longer prefix")

        return options[0]
