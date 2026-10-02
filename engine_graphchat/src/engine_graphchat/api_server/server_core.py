import logging

from engine_graphchat.core.dialogue import dialogue_manager


logger = logging.getLogger(__name__)


class CoreError(Exception):
    pass


class ServerCore:
    def __init__(self):
        self.DM = dialogue_manager.DialogueManager(model_name=None)

    def POST_graphs_F_nodes(self, prompt_api):
        # TODO get proper model names from the client
        # self.DM.set_model(prompt_api.model)
        self.DM.set_upstream(prompt_api.upstream)
        self.DM.set_prompt(prompt_api.content, prompt_api.timestamp)

        reply_node_data = self.DM.COMMIT()

        return reply_node_data

    def GET_graphs_F_nodes(self):
        return list(self.DM.graph.nodes.keys())

    def GET_graphs_F_nodes_F(self, node_id):
        if node_id not in self.DM.graph.nodes:
            raise CoreError(f"The node id {node_id} is not in the graph")

        return self.DM.graph.nodes[node_id]

    def GET_graphs_F_nodes_F_info(self, graph_id, node_id):
        pass

    def GET_system_models(self):
        return self.DM.llm_service.get_model_names()
