"""
The interface with xAI using the xai-sdk
"""

import xai_sdk

from core.llm import utils, api_keys
from core.graph import node


class LLM_ERROR(Exception):
    pass


class LLM_Service:
    """
    Manage the connection to an LLM service providing multiple language models.
    """

    def __init__(self):
        self._client = api_keys.initialize_client(xai_sdk.Client)

        # Cached info
        self._info_models = None

    def get_model_names(self):
        if self._info_models is None:
            self._info_models = self._client.models.list_language_models()

        names = []
        for model in self._info_models:
            names.append(model.name)
        return names

    def new_chat(self, model_name, messages):
        chat = self._client.chat.create(model_name, messages=messages,
                                        store_messages=False)
        return LLM_Chat(chat)


class LLM_Chat:
    """
    Manage a chat with language model from a LLM service
    """

    def __init__(self, chat):
        self._chat = chat

    def send_node_request(self, node_request):
        user_msg = xai_sdk.chat.user(node_request.content)
        self._chat.append(user_msg)

        reply = self._chat.sample()

        if reply.finish_reason != "REASON_STOP":
            raise LLM_ERROR("LLM: Failed to generate a full reply!")

        assistant_msg = xai_sdk.chat.assistant(reply.content)
        self._chat.append(assistant_msg)

        usage = node.NodeUsage(reply.usage.cached_prompt_text_tokens,
                               reply.usage.prompt_tokens,
                               reply.usage.reasoning_tokens,
                               reply.usage.completion_tokens,
                               reply.cost_usd)

        node_reply = node.NodeReply(utils.get_timestamp(),
                                    reply.content,
                                    reply.finish_reason,
                                    usage)

        return node_reply
