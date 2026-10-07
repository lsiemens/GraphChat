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

    def to_NodeData(self) -> node.NodeData:
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

    @classmethod
    def from_NodeData(cls, node_data: node.NodeData) -> "NodeDataAPI":
        return cls(
            id=node_data.id,
            upstream=node_data.upstream,
            context=node_data.request.context,
            request=node_data.request.content,
            reply=node_data.reply.content,
            model=node_data.model,
            costUSD=node_data.reply.usage.cost_USD)


class NodeIDsAPI(BaseModel):
    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    ids: list[str]

    @classmethod
    def from_strings(cls, ids: list[str]) -> "NodeIDsAPI":
        return cls(ids=ids)


class ModelNamesAPI(BaseModel):
    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    models: list[str]

    @classmethod
    def from_strings(cls, models: list[str]) -> "ModelNamesAPI":
        return cls(models=models)


class ViewNamesAPI(BaseModel):
    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    viewNames: list[str]

    @classmethod
    def from_strings(cls, viewNames: list[str]) -> "ViewNamesAPI":
        return cls(viewNames=viewNames)


class ViewUpstreamAPI(BaseModel):
    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    upstream: list[str]

    def to_strings(self) -> list[str]:
        return self.upstream


class ViewContextAPI(BaseModel):
    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    context: list[str]

    @classmethod
    def from_strings(cls, context: list[str]) -> "ViewContextAPI":
        return cls(context=context)
