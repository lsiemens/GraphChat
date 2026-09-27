"""
Classes defining a chat Node
"""
import hashlib


class NodeData:
    _ENCODING = "utf-8"

    def __init__(self, id, model, upstream, request, reply):
        self.id = id
        self.model = model
        self.upstream = upstream
        self.request = request
        self.reply = reply

    def hash(self):
        if self.model is None:
            raise ValueError("Can not generate node ID, model is None")
        if self.upstream is None:
            raise ValueError("Can not generate node ID, upstream is None")
        if self.request is None:
            raise ValueError("Can not generate node ID, request is None")
        if self.request.content is None:
            raise ValueError("Can not generate node ID, request.content is None")
        if self.reply is None:
            raise ValueError("Can not generate node ID, reply is None")
        if self.reply.content is None:
            raise ValueError("Can not generate node ID, reply.content is None")

        identifying_data = f"{self.model}|{self.request.content}|{self.upstream}|{self.reply.content}"
        identifying_data = identifying_data.encode(self._ENCODING)

        return hashlib.sha256(identifying_data).hexdigest()

    def validate(self):
        return self.id == self.hash()

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
