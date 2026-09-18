"""GraphChat Proof of Concept

Driving code for the directed acyclic graph
"""

from xai_sdk.chat import user, assistant, system
import xai_core

class GraphError(Exception):
    """Graph Error!"""

class Node:
    """Contain a conversation node

    This consists of a user prompt and the LLMs responce.
    """
    _next_id = 0

    def __init__(self, user_txt):
        self._id = Node._next_id
        Node._next_id += 1

        self._user_msg = user(user_txt)
        self._reply_msg = None

    def generate_reply(self, llm_core):
        if self._reply_msg is not None:
            raise GraphError(f"The node with ID={self.id} already has a reply!")

        self._reply_msg = llm_core.get_response(self._user_msg)

    @property
    def id(self):
        return self._id

    @property
    def user_txt(self):
        return self._user_msg.content[0].text

    @property
    def reply_txt(self):
        return self._reply_msg.content

class Graph:
    """Contain a conversation graph
    """

    _sys_prompt = system(xai_core._DEFAULT_SYSTEM_PROMPT)

    def __init__(self):
        # dict of nodes indexed by their IDs
        self._nodes = {}

        # dicts defining the graph connectivity. Each dict is indexed by the
        # node ID and contains a list of parent/child IDs
        self._children = {}
        self._parents = {}

        self._current_ID = None
        self.llm_core = xai_core.xAI_Core([self._sys_prompt])

    def TUI_chat_loop(self):
        total_cost_usd = 0.0

        print("Start graph TUI chat with grok!")
        while True:
            try:
                prompt = input("\nYou: ")
            except KeyboardInterrupt:
                break

            # -- BEGIN -- some manual commands
            if prompt.lower() == "exit":
                break

            if prompt.lower() == "show graph":
                print(f"Node IDs: {self._nodes.keys()}")
                for node_id in self._nodes.keys():
                    print(f"  Node [{node_id}]: ", end="")
                    if node_id in self._children:
                        print(f" children = {self._children[node_id]}", end="")
                    else:
                        print(" children = []", end="")

                    if node_id in self._parents:
                        print(f", parents = {self._parents[node_id]}")
                    else:
                        print(", parents = []")
                continue

            command = "set current_id = "
            if prompt.lower()[:len(command)] == command:
                try:
                    new_id = int(prompt[len(command):])
                except ValueError:
                    print(f"Invalid integer literal \"{prompt[len(command):]}\"")
                    continue

                print(f"new current_ID == {new_id}")
                if new_id not in self._nodes:
                    print(f"That is an invalid node id! The current_ID = {self._current_ID}!")
                    continue

                print(f"\nYou [{new_id}]: {self._nodes[new_id].user_txt}")
                print(f"\nNode [{new_id}], Grok: {self._nodes[new_id].reply_txt}")

                self.set_current_ID(new_id)
                continue

            # -- END -- some manual commands

            try:
                self.add_node(prompt)
                reply_txt = self._nodes[self._current_ID].reply_txt
                print(f"\nNode [{self._current_ID}], Grok: {reply_txt}")
            except KeyboardInterrupt:
                break

        print("\nExiting chat!")

    def add_node(self, user_txt):
        node = Node(user_txt)

        node.generate_reply(self.llm_core)

        if node.id in self._nodes:
            raise GraphError("A node with this ID already exists in the graph.")

        self._nodes[node.id] = node

        if self._current_ID is not None:
            if self._current_ID in self._children:
                self._children[self._current_ID].append(node.id)
            else:
                self._children[self._current_ID] = [node.id]

            if node.id in self._parents:
                self._parents[node.id].append(self._current_ID)
            else:
                self._parents[node.id] = [self._current_ID]

        self._current_ID = node.id

    def set_current_ID(self, target_ID):
        if target_ID not in self._nodes:
            raise GraphError("Can not set current_ID to {target_ID}, no node with that id exists.")

        new_context_IDs = [target_ID]
        node_ID = target_ID
        while (node_ID in self._parents):
            node_ID = self._parents[node_ID][0]
            new_context_IDs.append(node_ID)

        messages = [self._sys_prompt]
        for node_id in new_context_IDs[::-1]:
            messages.append(user(self._nodes[node_id].user_txt))
            messages.append(assistant(self._nodes[node_id].reply_txt))

        self._current_ID = target_ID
        self.llm_core = xai_core.xAI_Core(messages)

    @property
    def current_ID(self):
        return self._current_ID

if __name__ == "__main__":
    graph = Graph()
    graph.TUI_chat_loop()
