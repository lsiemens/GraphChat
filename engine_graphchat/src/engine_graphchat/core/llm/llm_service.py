"""
The interface with xAI using the xai-sdk
"""

import logging
import grpc
import time

import xai_sdk

from engine_graphchat.core import exceptions
from engine_graphchat.core.llm import MOCK_sdk
from engine_graphchat.core.llm import utils, api_keys
from engine_graphchat.core.dag import node


logger = logging.getLogger(__name__)


class LLM_Service:
    """
    Manage the connection to an LLM service providing multiple language models.
    """

    def __init__(self):
        if not MOCK_sdk.use_MOCK_llm_sdk():
            logger.info("Using Client from xAI-SDK.")
            Client = xai_sdk.Client
        else:
            logger.info("Using Client from MOCK SDK.")
            Client = MOCK_sdk.MOCK_Client

        self._client = api_keys.initialize_client(Client)

        # Cached info
        self._info_models = None

    def get_model_names(self):
        if self._info_models is None:
            logger.info("Cache available language models.")
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

    _MAX_RETRIES = 6

    def __init__(self, chat):
        self._chat = chat

    def _sample(self):
        """sample LLM with resource management
        """

        for attempt in range(self._MAX_RETRIES):
            # only sleep between attempts not before or after each attempt
            if attempt != 0:
                time.sleep(2**(attempt - 1))

            try:
                return self._chat.sample()
            except grpc.RpcError as e:
                if e.code() != grpc.StatusCode.RESOURCE_EXHAUSTED:
                    logger.exception("Unrecoverable RPC error")
                    raise exceptions.ServiceError("LLM service connection failure") from e
                logger.warning("RPC resource exhausted: attempt %d of %d", attempt + 1, self._MAX_RETRIES)
        logger.error("RPC resource exhausted: Reached maximum retries.")
        raise exceptions.ServiceError("LLM service rate limited: retries failed")

    def send_node_request(self, node_request):
        user_msg = xai_sdk.chat.user(node_request.content)
        self._chat.append(user_msg)

        # may raise LLM_ERROR
        reply = self._sample()

        if reply.finish_reason != "REASON_STOP":
            raise exceptions.ServiceError("LLM failed to generate a full reply")

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


def node_to_xAI_messages(node_data):
    if node_data.request is None:
        raise exceptions.InvalidNodeError("NodeData does not have a user request")
    if node_data.reply is None:
        raise exceptions.InvalidNodeError("NodeData does not have an agent reply")
    return [xai_sdk.chat.user(node_data.request.content), xai_sdk.chat.assistant(node_data.reply.content)]
