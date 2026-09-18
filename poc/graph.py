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
        return self._user_msg.content

    @property
    def reply_txt(self):
        return self._reply_msg.content

class Graph:
    """Contain a conversation graph
    """

    def __init__(self):
        # dict of nodes indexed by their IDs
        self._nodes = {}

        # dicts defining the graph connectivity. Each dict is indexed by the
        # node ID and contains a list of parent/child IDs
        self._children = {}
        self._parents = {}

        self.current_ID = None
        self.llm_core = xai_core.xAI_Core()

    def TUI_chat_loop(self):
        total_cost_usd = 0.0

        print("Start graph TUI chat with grok!")
        while True:
            try:
                prompt = input("\nYou: ")
            except KeyboardInterrupt:
                break

            #some manual commands
            if prompt.lower() == "exit":
                break

            try:
                self.add_node(prompt)
                reply_txt = self._nodes[self.current_ID].reply_txt
                print(f"\nNode [{self.current_ID}], Grok: {reply_txt}")
            except KeyboardInterrupt:
                break

        print("\nExiting chat!")

    def add_node(self, user_txt):
        node = Node(user_txt)

        node.generate_reply(self.llm_core)

        if node.id in self._nodes:
            raise GraphError("A node with this ID already exists in the graph.")

        self._nodes[node.id] = node

        if self.current_ID is not None:
            if self.current_ID in self._children:
                self._children[self.current_ID].append(node.id)
            else:
                self._children[self.current_ID] = [node.id]

            if node.id in self._parents:
                self._parents[node.id].append(self.current_ID)
            else:
                self._parents[node.id] = [self.current_ID]

        self.current_ID = node.id

if __name__ == "__main__":
    graph = Graph()
    graph.TUI_chat_loop()
