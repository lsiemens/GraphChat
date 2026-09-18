
"""GraphChat Proof of Concept

A graph based chat client. Inital code is partially based on
xai-sdk-python/examples/sync/chat.py script.
"""

import keyring
import xai_sdk

_DEFAULT_SYSTEM_PROMPT = """You are a precise, highly analytical research
assistant. Provide accurate, well-sourced, and nuanced information. Prioritize
clarity, depth and intellectual honesty. Be concise and to the point."""

_MODEL = "grok-4.20-non-reasoning"

class AuthError(Exception):
    """Authentication error!"""

class xAI_Core:
    """Manage xAI on a linear thread
    """

    _service="GraphChatCli"
    _API_key_name="API_key"

    def __init__(self, messages):
        self.llm_client = self._initalize_client()

        self._chat = self.llm_client.chat.create(model=_MODEL,
                                                 store_messages=False,
                                                 messages=messages)

    def get_response(self, user_msg):
        """Non streaming chat responce"""

        self._chat.append(user_msg)
        response = self._chat.sample()
        self._chat.append(response)
        return response

    def TUI_chat_loop(self):
        total_cost_usd = 0.0

        print("Start TUI chat with grok!")
        while True:
            try:
                prompt = input("\nYou: ")
            except KeyboardInterrupt:
                break

            # some manual commands
            if prompt.lower() == "exit":
                print("Exiting chat!")
                break

            if prompt.lower() == "clear keys":
                self._clear_API_key()
                print("Exiting chat!")
                break

            try:
                response = self.get_response(xai_sdk.chat.user(prompt))
                print(f"\nGrok: {response.content}")
                total_cost_usd += response.cost_usd or 0.0
            except KeyboardInterrupt:
                print("Exiting chat!\nThe cost of the last query is unknown!")
                break

        print(f"\nTotal cost: ${total_cost_usd:.4f}")

    def _save_API_key(self, API_key):
        if API_key is None:
            raise AuthError("Failed to save API keys to the keyring!")
        keyring.set_password(self._service, self._API_key_name, API_key)

    def _clear_API_key(self):
        keyring.delete_password(self._service, self._API_key_name)

        if keyring.get_password(self._service, self._API_key_name) is not None:
            raise AuthError("Failed to clear the API key!")

    def _initalize_client(self):
        API_key = keyring.get_password(self._service, self._API_key_name)

        if API_key is None:
            print("The API key is not in your key ring.")
            while (API_key is None):
                API_key = input("Enter your API key: ").strip()
                if API_key == "":
                    print("  The key can not be empty.")
                    API_key = None

            self._save_API_key(API_key)

        return xai_sdk.Client(api_key=API_key)

if __name__ == "__main__":
    LLM_core = xAI_Core([xai_sdk.chat.system(_DEFAULT_SYSTEM_PROMPT)])
    LLM_core.TUI_chat_loop()

