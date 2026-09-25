try:
    from uuid import uuid7
except ImportError:
    from uuid6 import uuid7


from engine_graphchat.core.dag import graph
from engine_graphchat.core.llm import llm_service


class DialogueManager:
    def __init__(self):
        self.graph = graph.Graph()
        self.llm_service = llm_service.LLM_Service()
        self.active_id = None

        model_name = self.llm_service.get_model_names()[0]
        self.chat = self.llm_service.new_chat(model_name, [])

    def turn(self, node_data):
        #all other paths require restructuring the contex

        if self.active_id is None:
            if len(node_data.upstream) == 0:
                temp_id = node_data

                reply = self.chat.send_node_request(node_data.request)
                node_data.reply = reply
                node_data.id = uuid7().hex

                self.graph.add_node(node_data)
                self.active_id = node_data.id
                return temp_id, node_data

        if len(node_data.upstream) == 1:
            if node_data.upstream[0] == self.active_id:
                temp_id = node_data.id

                reply = self.chat.send_node_request(node_data.request)
                node_data.reply = reply
                node_data.id = uuid7().hex

                self.graph.add_node(node_data)
                self.active_id = node_data.id
                return temp_id, node_data

        raise ValueError("Requires managin history")
