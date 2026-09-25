"""
Interface for a  MOCK LLM service

a mock interface based on the xAI-SDK
"""

import os


def use_MOCK_llm_sdk():
    return os.getenv("USE_MOCK_LLM_SDK", "0").lower() in ["true", "yes", "on", "1"]


class MOCK_Model:
    def __init__(self, name):
        self.name = name
        self.aliases = [name + ".1", name + ".2"]


class MOCK_Models:
    def __init__(self):
        pass

    def list_language_models(self):
        return [MOCK_Model("Mock-1"), MOCK_Model("Model-2")]


class MOCK_Usage:
    def __init__(self):
        self.cached_prompt_text_tokens = 0
        self.completion_tokens = 0
        self.prompt_text_tokens = 0
        self.prompt_tokens = 0
        self.reasoning_tokens = 0
        self.total_tokens = 0


class MOCK_Reply:
    def __init__(self, content, finish_reason="REASON_STOP"):
        self.content = content
        self.finish_reason = finish_reason
        self.cost_usd = 0
        self.usage = MOCK_Usage()


class MOCK_Chat:
    def __init__(self):
        self.messages = []

    def create(self, model, messages, conversation_id="", reasoning_effort="low", store_messages=True):
        self.messages = messages
        self._model = model
        return self

    def append(self, message):
        self.messages.append(message)

    def sample(self):
        return MOCK_Reply(f"MOCK: This reply comes from the MOCK LLM \"{self._model}\"")


class MOCK_Client:
    def __init__(self, api_key, management_api_key=None, api_host=None, management_host = None):
        self.models = MOCK_Models()
        self.chat = MOCK_Chat()

        print("Connected to MOCK LLM service")

    def close(self):
        pass
