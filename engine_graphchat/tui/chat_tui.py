"""
A commandline chat client
"""

from engine_graphchat.core.dialogue import dialogue_manager
from engine_graphchat.core.dag import utils


class Chat_TUI:
    _model_name = ""

    def __init__(self):
        self.DM = dialogue_manager.DialogueManager()

    def start(self):
        print("Connected to chat!")

        try:
            while True:
                prompt = input("You: ").strip()

                if prompt == "":
                    continue

                prompt_data_node = utils.node_from_string(prompt,
                                                          self._model_name,
                                                          self.DM.active_id)
                _, reply_data_node = self.DM.turn(prompt_data_node)

                print(f"\nGrok: {reply_data_node.reply.content}")
        except KeyboardInterrupt:
            pass


if __name__ == "__main__":
    TUI = Chat_TUI()
    TUI.start()
