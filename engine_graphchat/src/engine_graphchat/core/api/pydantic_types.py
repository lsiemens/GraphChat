from pydantic import BaseModel, ConfigDict

from engine_graphchat.core.dag import node


# TODO check can I add code to validate that the classes here match the ones in `api_types.py`
class PromptAPI(BaseModel):
    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    model: str
    upstream: list[str]
    context: list[str]
    timestamp: str
    content: str

    def to_NodeData(self):
        node_request = node.NodeRequest(self.timestamp, self.context, self.content)
        node_data = node.NodeData(None, self.model, self.upstream, node_request, None)
        return node_data


class NodeDataAPI(BaseModel):
    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    id: str
    upstream: list[str]
    context: list[str]
    request: str
    reply: str
    model: str
    costUSD: float | None

    def from_NodeData(self, node_data: node.NodeData):
        self.id = node_data.id
        self.upstream = node_data.upstream
        self.context = node_data.request.context
        self.request = node_data.request.content
        self.reply = node_data.reply.content
        self.model = node_data.model
        self.costUSD = node_data.reply.usage.cost_USD


class NodeIDsAPI(BaseModel):
    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    ids: list[str] = []

    def from_strings(self, ids: list[str]):
        self.ids = ids


class ModelNamesAPI(BaseModel):
    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    models: list[str] = []

    def from_strings(self, models: list[str]):
        self.models = models
