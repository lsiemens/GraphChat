from engine_graphchat.core.dag import node


class PromptAPI:
    model: str
    upstream: list[str]
    context: list[str]
    timestamp: str
    content: str

    def __init__(self):
        self.model = None
        self.upstream = None
        self.context = None
        self.timestamp = None
        self.content = None

    def to_NodeData(self):
        node_request = node.NodeRequest(self.timestamp, self.context, self.content)
        node_data = node.NodeData(None, self.model, self.upstream, node_request, None)
        return node_data


class NodeDataApi:
    id: str
    upstream: list[str]
    context: list[str]
    request: str
    reply: str
    model: str
    costUSD: float

    def __init__(self):
        self.id = None
        self.upstream = None
        self.context = None
        self.request = None
        self.reply = None
        self.model = None
        self.costUSD = None

    def from_NodeData(self, node_data):
        self.id = node_data.id
        self.upstream = node_data.upstream
        self.context = node_data.request.context
        self.request = node_data.request.content
        self.reply = node_data.reply.content
        self.model = node_data.model
        self.costUSD = node_data.reply.usage.cost_USD


class NodeIDsAPI:
    ids: list[str]

    def __init__(self):
        self.ids = None

    def from_strings(self, ids):
        self.ids = ids


class ModelNamesAPI:
    models: list[str]

    def __init__(self):
        self.models = None

    def from_strings(self, models):
        self.models = models
