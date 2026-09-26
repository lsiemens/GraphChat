"""
A commandline chat client
"""

import logging
try:
    import prompt_toolkit
except ImportError:
    prompt_toolkit = None
    print("Warning: Could not import \"prompt_toolkit\", multiline input will not be available")

try:
    import rich.console
    import rich.markdown
except ImportError:
    rich = None
    print("Warning: Could not import \"rich\", formatting of markdown will not be available")

from engine_graphchat.core.dialogue import dialogue_manager
from engine_graphchat.core.dag import utils


logger = logging.getLogger(__name__)


class Chat_TUI:
    _model_name = "grok-4.20-0309-non-reasoning"
    _agent_name = "Grok"

    def __init__(self):
        self.DM = dialogue_manager.DialogueManager(model_name=self._model_name)
        self._greeting = f"Connected to {self._agent_name}!"

        self.stats = {"cost": 0, "prompt_tokens": 0, "reasoning_tokens": 0, "completion_tokens": 0, "cached_tokens": 0}

        if prompt_toolkit is not None:

            kb = prompt_toolkit.key_binding.KeyBindings()

            @kb.add("enter")
            def _(event):
                event.current_buffer.validate_and_handle()

            @kb.add("escape", "enter")
            def _(event):
                event.current_buffer.insert_text('\n')

            prompt_msg = prompt_toolkit.formatted_text.HTML("<ansicyan><b>You:</b></ansicyan> ")
            self._session = prompt_toolkit.PromptSession(prompt_msg,
                                                         multiline=True,
                                                         key_bindings=kb)

        if rich is not None:
            self._console = rich.console.Console()

        if prompt_toolkit is not None:
            if rich is not None:
                # format as a markdown new line
                self._greeting += "  "
            self._greeting += "\nUse Alt+Enter to make a new line."

    def get_input(self):
        if prompt_toolkit is not None:
            return self._session.prompt()
        else:
            return input("You: ").strip()

    def print(self, string):
        if rich is not None:
            self._console.print(rich.markdown.Markdown(string))
        else:
            print(string)

    def start(self):
        self.print(f"{self._greeting}\n")

        try:
            while True:
                prompt = self.get_input()

                if prompt == "":
                    continue

                if prompt == "exit":
                    break

                prompt_data_node = utils.node_from_string(prompt,
                                                          self._model_name,
                                                          self.DM.active_id)
                _, reply_data_node = self.DM.turn(prompt_data_node)

                self.print(f"  \n\n{self._agent_name}: {reply_data_node.reply.content}  \n")
                usage = reply_data_node.reply.usage
                self.stats["cost"] += usage.cost_USD
                self.stats["prompt_tokens"] += usage.prompt_tokens
                self.stats["completion_tokens"] += usage.completion_tokens
                self.stats["cached_tokens"] += usage.cached_prompt_text_tokens
                self.print(f"> **REPLY**: ${usage.cost_USD:.4f}, **tokens**: [{usage.prompt_tokens}, {usage.completion_tokens}], cache ({usage.cached_prompt_text_tokens}) \n\n---\n\n")
        except KeyboardInterrupt:
            pass

        self.print(f">> **STATS**: Total cost: ${self.stats['cost']:.4f}, **Total tokens**: [{self.stats['prompt_tokens']}, {self.stats['completion_tokens']}] cache ({self.stats['cached_tokens']})\n")


if __name__ == "__main__":
    #import os
    #os.environ["USE_MOCK_LLM_SDK"] = "True"
    logging.basicConfig(filename="chat_tui.log", level=logging.INFO)
    TUI = Chat_TUI()
    TUI.start()
