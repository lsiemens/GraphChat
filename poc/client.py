import keyring
import xai_sdk

class AuthError(Exception):
    """Authentication error!"""

class ChatClient:
    """Manage the LLM API
    """

    _service="GraphChatCli"
    _API_key_name="API_key"

    def __init__(self):
        self.llm_client = self._initalize_client()

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
                api_key = input("Enter your XAI api key: ").strip()
                if api_key == "":
                    print("  The key can not be empty.")
                    api_key = None

            self._save_api_key(api_key)

        return xai_sdk.Client(api_key=api_key)

graph_cli = ChatClient()
chat = graph_cli.llm_client.chat.create(model="grok-4.6")
chat.append(xai_sdk.chat.user("Hello this is a test chat from the python xai_sdk interface. Say hello"))

print(chat.sample().content)
