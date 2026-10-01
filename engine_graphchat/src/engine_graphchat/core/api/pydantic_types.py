from pydantic import BaseModel, ConfigDict

from engine_graphchat.core.dag import node


class PromptAPI(BaseModel):
    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    # TODO check can I add code to validate that the classes here match the ones in `api_types.py`
    model: str = ""
    upstream: list[str] = []
    timestamp: str = ""
    content: str = ""

    def to_NodeData(self):
        node_request = node.NodeRequest(self.timestamp, self.content)
        node_data = node.NodeData(None, self.model, self.upstream, node_request, None)
        return node_data


class NodeDataAPI(BaseModel):
    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    # TODO check can I add code to validate that the classes here match the ones in `api_types.py`
    id: str = ""
    upstream: list[str] = []
    request: str = ""
    reply: str = ""
    model: str = ""
    costUSD: float = 0.0

    def from_NodeData(self, node_data: node.NodeData):
        self.id = node_data.id
        self.upstream = node_data.upstream
        self.request = node_data.request.content
        self.reply = node_data.reply.content
        self.model = node_data.model
        self.costUSD = node_data.reply.usage.cost_USD


class NodeIDsAPI(BaseModel):
    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    # TODO check can I add code to validate that the classes here match the ones in `api_types.py`
    ids: list[str] = []

    def from_strings(self, strings: list[str]):
        self.ids = strings
