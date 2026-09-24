"""
Classes defining a chat Node
"""


class NodeData:
    def __init__(self, id, model, upstream, request, reply):
        self.id = id
        self.model = model
        self.upstream = upstream
        self.request = request
        self.reply = reply


class NodeRequest:
    def __init__(self, timestamp, content):
        self.timestamp = timestamp
        self.content = content


class NodeReply:
    def __init__(self, timestamp, content, finish_reason, usage):
        self.timestamp = timestamp
        self.content = content
        self.finish_reason = finish_reason
        self.usage = usage


class NodeUsage:
    def __init__(self, cached_prompt_text_tokens, prompt_tokens,
                 reasoning_tokens, completion_tokens, cost_USD):
        self.cached_prompt_text_tokens = cached_prompt_text_tokens
        self.prompt_tokens = prompt_tokens
        self.reasoning_tokens = reasoning_tokens
        self.completion_tokens = completion_tokens
        self.cost_USD = cost_USD
