import logging

from engine_graphchat.core.dialogue import dialogue_manager


logger = logging.getLogger(__name__)


class ServerCore:
    def __init__(self):
        self.DM = dialogue_manager.DialogueManager(model_name=None)

    def POST_prompt(self, prompt_api):
        # TODO get proper model names from the client
        # self.DM.set_model(prompt_api.model)
        self.DM.set_upstream(prompt_api.upstream)
        self.DM.set_prompt(prompt_api.content, prompt_api.timestamp)

        reply_node_data = self.DM.COMMIT()

        return reply_node_data
