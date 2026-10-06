"""
Classes defining a chat Node
"""
import hashlib

from engine_graphchat.core import exceptions


class NodeData:
    _ENCODING = "utf-8"

    def __init__(self, id, model, upstream, request, reply):
        self.id = id
        self.model = model
        self.upstream = upstream
        self.request = request
        self.reply = reply

    def hash(self):
        if not isinstance(self.model, str):
            raise exceptions.InvalidNodeError("Failed to generate node ID: model must be a string")

        if not isinstance(self.upstream, list):
            raise exceptions.InvalidNodeError("Failed to generate node ID: upstream must be a list")
        if not all(isinstance(node_id, str) for node_id in self.upstream):
            raise exceptions.InvalidNodeError("Failed to generate node ID: all items in upstream must be strings")

        if not isinstance(self.request, NodeRequest):
            raise exceptions.InvalidNodeError("Failed to generate node ID: request must be a NodeRequest")
        if not isinstance(self.request.context, list):
            raise exceptions.InvalidNodeError("Failed to generate node ID: request.context must be a list")
        if not all(isinstance(node_id, str) for node_id in self.request.context):
            raise exceptions.InvalidNodeError("Failed to generate node ID: all items in request.context must be strings")
        if not isinstance(self.request.content, str):
            raise exceptions.InvalidNodeError("Failed to generate node ID: request.content must be a string")

        if not isinstance(self.reply, NodeReply):
            raise exceptions.InvalidNodeError("Failed to generate node ID: reply must be a NodeReply")
        if not isinstance(self.reply.content, str):
            raise exceptions.InvalidNodeError("Failed to generate node ID: reply.content must be a string")

        identifying_data = f"{self.model}|{self.upstream}|{self.request.context}|{self.request.content}|{self.reply.content}"
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
    def __init__(self, timestamp, context, content):
        self.timestamp = timestamp
        self.context = context
        self.content = content

    def __str__(self):
        return f"NodeRequest: timestamp: {self.timestamp}, " \
               f"context: {self.context}, " \
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
