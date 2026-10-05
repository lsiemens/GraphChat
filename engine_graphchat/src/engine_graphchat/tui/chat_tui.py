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


logger = logging.getLogger(__name__)

class Chat_TUI:
    _model_name = "grok-4.20-0309-non-reasoning"
    _agent_name = "Grok"
    _ID_chars = 10

    def __init__(self):
        self.DM = dialogue_manager.DialogueManager(model_name=self._model_name)
        self._greeting = f"Connected to {self._agent_name}!"
        self.show_ids = False

        self.stats = {"cost": 0, "prompt_tokens": 0, "reasoning_tokens": 0, "completion_tokens": 0, "cached_tokens": 0}

        self._setup_print_and_input()

    def command(self, prompt):
        if prompt.lower() == "toggle ids":
            self.show_ids = not self.show_ids
            return True

        if prompt.lower() == "refresh":
            for node_id in self.DM.LOG():
                self.print_node(self.DM.graph.nodes[node_id], reply_only=False)
            return True

        if prompt.lower().startswith("merge "):
            targets = prompt.split(" ")[1:]
            self.DM.MERGE(targets)
            return True

        if prompt.lower().startswith("checkout "):
            target = prompt.split(" ", 1)[1]
            self.DM.CHECKOUT(target)
            return True

        if prompt.lower() == "show nodes":
            node_text = "Chat Nodes  \n"
            for node_id in self.DM.graph.nodes:
                node = self.DM.graph.nodes[node_id]
                node_text += f"> Node: `{node_id[:self._ID_chars]}`  \n"
                for i, p_node_id in enumerate(node.upstream):
                    node_text += f">> Upstream: `{p_node_id[:self._ID_chars]}`  \n"
                node_text += "\n"

            self.print(node_text)
            return True

        if prompt.lower() == "status":
            node_text = f"`Proposed Node`: `Model`: \"{self.DM._state.model}\"  \n"
            node_text += f"`Upstream`: {[node_id[:self._ID_chars] for node_id in self.DM._state.upstream]}  \n"
            node_text += f"`Context`: {[node_id[:self._ID_chars] for node_id in self.DM.LOG()]}  \n"
            node_text += f"`Prompt`: \"{self.DM._state.request.content[:100]}\"  \n"
            if self.DM._HEAD is not None:
                node_text += f"`HEAD`: {self.DM._HEAD[:self._ID_chars]}"

            self.print(node_text)
            return True

        if prompt.lower() == "help":
            help_text = "> Commands:  \n"
            help_text += "- `toggle ids`: Show node IDs  \n"
            help_text += "- `refresh`: Refresh screen  \n"
            help_text += "- `merge <node ID> <node ID> ...`: Merge into the working node  \n"
            help_text += "- `checkout <node ID>`: Checkout existing node  \n"
            help_text += "- `status`: Show the working node  \n"

            self.print(help_text)
            return True
        return False

    def start(self):
        self.print(f"{self._greeting}\n")

        try:
            while True:
                prompt = self.get_input()

                if prompt == "":
                    continue

                if prompt[0] == ":":
                    if self.command(prompt[1:]):
                        continue
                    else:
                        self.print(f"`Command`: \"{prompt[1:]}\" not recognized. For help enter \":help\"  \n")
                        continue

                if prompt.lower() == "exit":
                    break

                self.DM.set_prompt(prompt)
                data_node = self.DM.COMMIT()

                self.print_node(data_node, reply_only=True)

                usage = data_node.reply.usage
                self.stats["cost"] += usage.cost_USD
                self.stats["prompt_tokens"] += usage.prompt_tokens
                self.stats["completion_tokens"] += usage.completion_tokens
                self.stats["cached_tokens"] += usage.cached_prompt_text_tokens
        except KeyboardInterrupt:
            pass

        self.print(f">> **STATS**: Total cost: ${self.stats['cost']:.4f}, **Total tokens**: [{self.stats['prompt_tokens']}, {self.stats['completion_tokens']}] cache ({self.stats['cached_tokens']})\n")

    def _setup_print_and_input(self):
        if prompt_toolkit is not None:

            kb = prompt_toolkit.key_binding.KeyBindings()

            @kb.add("enter")
            def _(event):
                event.current_buffer.validate_and_handle()

            @kb.add("escape", "enter")
            def _(event):
                event.current_buffer.insert_text('\n')

            prompt_msg = prompt_toolkit.formatted_text.HTML("<ansicyan><b>You:</b></ansicyan> ")
            self._session = prompt_toolkit.PromptSession(prompt_msg, multiline=True, key_bindings=kb)

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

    def print_node(self, data_node, reply_only=True):
        if not reply_only:
            self.print(f"You: {data_node.request.content}")

        self.print(f"  \n\n{self._agent_name}: {data_node.reply.content}  \n")
        if self.show_ids:
            self.print(f"Node ID: `{data_node.id[:self._ID_chars]}`")
        usage = data_node.reply.usage
        self.print(f"> **REPLY**: ${usage.cost_USD:.4f}, **tokens**: [{usage.prompt_tokens}, {usage.completion_tokens}], cache ({usage.cached_prompt_text_tokens}) \n\n---\n\n")


if __name__ == "__main__":
    #import os
    #os.environ["USE_MOCK_LLM_SDK"] = "True"
    logging.basicConfig(filename="chat_tui.log", level=logging.INFO)
    TUI = Chat_TUI()
    TUI.start()
