import logging

from engine_graphchat.core import exceptions
from engine_graphchat.core.dialogue import dialogue_manager


logger = logging.getLogger(__name__)


class ServerCore:
    def __init__(self):
        self.DM = dialogue_manager.DialogueManager(model_name=None)

    # Nodes
    def POST_graphs_F_nodes(self, prompt_api):
        # TODO get proper model names from the client
        self.DM.set_model(prompt_api.model)
        self.DM.set_context(prompt_api.upstream, prompt_api.context)
        self.DM.set_prompt(prompt_api.content, prompt_api.timestamp)

        reply_node_data = self.DM.COMMIT()

        return reply_node_data

    def GET_graphs_F_nodes(self):
        return list(self.DM.graph.nodes.keys())

    def GET_graphs_F_nodes_F(self, node_id):
        if node_id not in self.DM.graph.nodes:
            raise exceptions.NotFoundError(f"The node id {node_id} is not in the graph")

        return self.DM.graph.nodes[node_id]

    def GET_graphs_F_nodes_F_info(self, graph_id, node_id):
        pass

    # views
    def GET_graphs_F_views(self):
        return list(self.DM.graph.views.keys())

    def POST_graphs_F_views_F(self, view_name, upstream):
        if view_name not in self.DM.graph.views:
            raise exceptions.NotFoundError(f"The view method {view_name} is not in the graph")

        method = self.DM.graph.views[view_name]
        return method(upstream)

    # General info
    def GET_system_models(self):
        return self.DM.llm_service.get_model_names()

    def exception_handler(self, exception):
        status = 500
        if isinstance(exception, exceptions.NotFoundError):
            status = 404
        elif isinstance(exception, exceptions.ContentError):
            status = 400
        elif isinstance(exception, exceptions.UpstreamError):
            status = 502
        message = f"HTTP request failed with `{exception}`"

        logger.exception("HTTP request failed")
        return status, message
