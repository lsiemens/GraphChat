from engine_graphchat.core.dag import node


class PromptAPI:
    model: str
    upstream: list[str]
    timestamp: str
    content: str

    def __init__(self):
        self.model = None
        self.upstream = None
        self.timestamp = None
        self.content = None

    def to_NodeData(self):
        node_request = node.NodeRequest(self.timestamp, self.content)
        node_data = node.NodeData(None, self.model, self.upstream, node_request, None)
        return node_data


class NodeDataApi:
    id: str
    upstream: list[str]
    request: str
    reply: str
    model: str
    costUSD: float

    def __init__(self):
        self.id = None
        self.ustream = None
        self.request = None
        self.reply = None
        self.model = None
        self.costUSD = None

    def from_NodeData(self, node_data):
        self.id = node_data.id
        self.upstream = node_data.upstream
        self.request = node_data.request.content
        self.reply = node_data.reply.content
        self.model = node_data.model
        self.costUSD = node_data.reply.usage.cost_USD
