"""GraphChat Proof of Concept

A graph based chat client. Inital code is partially based on
xai-sdk-python/examples/sync/chat.py script.
"""

import keyring
import xai_sdk
from xai_sdk.chat import system, user, assistant

class AuthError(Exception):
    """Authentication error!"""

class ChatClient:
    """Manage the LLM API
    """

    _service="GraphChatCli"
    _API_key_name="API_key"

    def __init__(self):
        self.llm_client = self._initalize_client()

        messages=[system("Your are a precice, highly analytical research assistant. Provide accurare, well-sourced, and nuanced information. Prioritize clarity, depth and intellectual honesty. Be concise and to the point.")]
        chat = self.llm_client.chat.create(model="grok-4.20-non-reasoning",
                                           store_messages=False,
                                           messages=messages)

        self.chat_loop(chat)


    def chat_loop(self, chat):
        """A streaming chat thread"""
        total_cost_usd = 0.0

        while True:
            prompt = input("\nYou: ")

            # some manual commands
            if prompt.lower() == "exit":
                break

            if prompt.lower() == "clear keys":
                self._clear_api_key()
                print("Exiting chat!")
                break

            # add the user prompt to the chat history
            chat.append(user(prompt))

            print("\nGrok: ", end="", flush=True)

            # generate one responce
            stream = chat.stream()
            last_response = None
            for response, chunk in stream:
                print(chunk.content, end="", flush=True)
                last_response = response
            print()
            assert last_response is not None

            # maintain chat history
            chat.append(last_response)

            total_cost_usd += last_response.cost_usd or 0.0

        print(f"Total cost: ${total_cost_usd:.4f}")

    def _save_api_key(self, api_key):
        if api_key is None:
            raise AuthError("Failed to save api keys to the keyring!")

        keyring.set_password(self._service, self._API_key_name, api_key)

    def _clear_api_key(self):
        keyring.delete_password(self._service, self._API_key_name)

        if keyring.get_password(self._service, self._API_key_name) is not None:
            raise AuthError("Failed to clear the api key!")

    def _initalize_client(self):
        api_key = keyring.get_password(self._service, self._API_key_name)

        if api_key is None:
            print("The api key is not in your key ring.")
            while (api_key is None):
                api_key = input("Enter your api key: ").strip()
                if api_key == "":
                    print("  The key can not be empty.")
                    api_key = None

            self._save_api_key(api_key)

        return xai_sdk.Client(api_key=api_key)

graph_cli = ChatClient()
