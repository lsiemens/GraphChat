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

    def __str__(self):
        string = f"NodeData: id:{self.id}, " \
                 f"model: {self.model}, " \
                 f"upstream: {self.upstream}, " \
                 f"Request: {self.request}, " \
                 f"Reply: {self.reply}"
        return string


class NodeRequest:
    def __init__(self, timestamp, content):
        self.timestamp = timestamp
        self.content = content

    def __str__(self):
        return f"NodeRequest: timestamp: {self.timestamp}, " \
               f"content: {self.content}"


class NodeReply:
    def __init__(self, timestamp, content, finish_reason, usage):
        self.timestamp = timestamp
        self.content = content
        self.finish_reason = finish_reason
        self.usage = usage

    def __str__(self):
        return f"NodeReply: timestamp: {self.timestamp}, " \
               f"content: {self.content}, " \
               f"finish reason: {self.finish_reason}, " \
               f"Usage: {self.usage}"


class NodeUsage:
    def __init__(self, cached_prompt_text_tokens, prompt_tokens,
                 reasoning_tokens, completion_tokens, cost_USD):
        self.cached_prompt_text_tokens = cached_prompt_text_tokens
        self.prompt_tokens = prompt_tokens
        self.reasoning_tokens = reasoning_tokens
        self.completion_tokens = completion_tokens
        self.cost_USD = cost_USD

    def __str__(self):
        return f"NodeUsage: tokens: <{self.prompt_tokens}, {self.reasoning_tokens}, {self.completion_tokens}> " \
               f"[{self.cached_prompt_text_tokens}], cost USD: ${self.cost_USD}"
