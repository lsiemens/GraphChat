from engine_graphchat.core.dialogue import dialogue_manager
from engine_graphchat.core.api import api_json, api_types

from engine_graphchat.http_server import http_server, http_middleware


class GraphChatServer:
    def __init__(self, CORS_settings):
        self.DM = dialogue_manager.DialogueManager()

        self.set_CORS_headers = http_middleware.configure_CORS(*CORS_settings)

    def GET(self, HTTP_request, HTTP_reply):
        http_middleware.set_simple_reply(501, "", "", HTTP_reply)

    def POST(self, HTTP_request, HTTP_reply):
        method, target, _ = HTTP_request.request_line

        if (HTTP_request.body) == 0:
            http_middleware.set_simple_reply(400, "", "", HTTP_reply)
            return

        if HTTP_request.headers["content-type"] != "application/json":
            http_middleware.set_simple_reply(400, "", "", HTTP_reply)

        JSON_request = HTTP_request.body
        prompt_api = api_json.load_JSON_as_type(JSON_request, api_types.PromptAPI)
        request_node_data = prompt_api.to_NodeData()

        # --- Enter Internal CORE --- #
        _, reply_node_data = self.DM.turn(request_node_data)
        # --- Exit Internal CORE --- #

        node_data_api = api_types.NodeDataApi()
        node_data_api.from_NodeData(reply_node_data)
        JSON_reply = api_json.dump_JSON_as_type(node_data_api, api_types.NodeDataApi)

        http_middleware.set_simple_reply(200, JSON_reply, ".json", HTTP_reply)

    def DELETE(self, HTTP_request, HTTP_reply):
        http_middleware.set_simple_reply(501, "", "", HTTP_reply)

    def process_HTTP(self, HTTP_request, HTTP_reply):
        if HTTP_reply.status_code is not None:
            return

        self.set_CORS_headers(HTTP_request, HTTP_reply)
        method, targe, _ = HTTP_request.request_line

        match method:
            case "GET":
                self.GET(HTTP_request, HTTP_reply)
                return

            case "POST":
                self.POST(HTTP_request, HTTP_reply)
                return

            case "DELETE":
                self.DELETE(HTTP_request, HTTP_reply)
                return

            case _:
                http_middleware.set_simple_reply(400, "", "", HTTP_reply)
                return

        http_middleware.set_simple_reply(500, "", "", HTTP_reply)


if __name__ == "__main__":
    import os
    os.environ["USE_MOCK_LLM_SDK"] = "TRUE"

    CORS_settings = (["http://localhost:5173"], [], ["content-type"], [], 600)
    engine = GraphChatServer(CORS_settings=CORS_settings)

    core = engine.process_HTTP
    server = http_server.HTTPServer("0.0.0.0", 8000, core)
    server.start()
