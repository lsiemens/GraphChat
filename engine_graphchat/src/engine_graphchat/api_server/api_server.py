import logging

from engine_graphchat.api_server import server_core
from engine_graphchat.core.api import api_json, api_types

from engine_graphchat.http_server import http_server, http_middleware


logger = logging.getLogger(__name__)


class GraphChatServer:
    _Base_URL = "/api/v1"

    def __init__(self, CORS_settings):
        self._server_core = server_core.ServerCore()

        self.set_CORS_headers = http_middleware.configure_CORS(*CORS_settings)

        route_patterns = {"graphs_F_nodes": "/graphs/{graph_id}/nodes",
                          "graphs_F_nodes_F": "/graphs/{graph_id}/nodes/{node_id}",
                          "graphs_F_nodes_F_info": "/graphs/{graph_id}/nodes/{node_id}/info",
                          "system_models": "/system/models"}
        route_patterns = {key: self._Base_URL + value for key, value in route_patterns.items()}
        self.rout_URL = http_middleware.configure_routing(route_patterns)

    def GET(self, HTTP_request, HTTP_reply):
        _, target, _ = HTTP_request.request_line

        label, url_parameters = self.rout_URL(target)

        # --- Enter Internal CORE --- #
        match label:
            case "graphs_F_nodes":
                #node_id_list = self._server_core.GET_graphs_F_nodes()
                #node_data_api = api_types.NodeDataApi()
                #node_data_api.from_NodeData(reply_node_data)
                #JSON_reply = api_json.dump_JSON_as_type(node_data_api, api_types.NodeDataApi)
                http_middleware.set_simple_reply(501, "", "", HTTP_reply)
                return
            case "graphs_F_nodes_F":
                http_middleware.set_simple_reply(501, "", "", HTTP_reply)
                return
            case "graphs_F_nodes_F_info":
                http_middleware.set_simple_reply(501, "", "", HTTP_reply)
                return
            case "system_models":
                http_middleware.set_simple_reply(501, "", "", HTTP_reply)
                return
            case _:
                http_middleware.set_simple_reply(501, "", "", HTTP_reply)
                return
        # --- Exit Internal CORE --- #

        JSON_reply = "{}"
        http_middleware.set_simple_reply(200, JSON_reply, ".json", HTTP_reply)

    def POST(self, HTTP_request, HTTP_reply):
        _, target, _ = HTTP_request.request_line

        if (HTTP_request.body) == 0:
            http_middleware.set_simple_reply(400, "", "", HTTP_reply)
            return

        if HTTP_request.headers["content-type"] != "application/json":
            http_middleware.set_simple_reply(400, "", "", HTTP_reply)

        label, url_parameters = self.rout_URL(target)
        JSON_request = HTTP_request.body

        # --- Enter Internal CORE --- #
        if label != "graphs_F_nodes":
            http_middleware.set_simple_reply(404, "", "", HTTP_reply)
            return

        prompt_api = api_json.load_JSON_as_type(JSON_request, api_types.PromptAPI)

        reply_node_data = self._server_core.POST_graphs_F_nodes(prompt_api)

        node_data_api = api_types.NodeDataApi()
        node_data_api.from_NodeData(reply_node_data)
        JSON_reply = api_json.dump_JSON_as_type(node_data_api, api_types.NodeDataApi)
        # --- Exit Internal CORE --- #

        http_middleware.set_simple_reply(200, JSON_reply, ".json", HTTP_reply)

    def DELETE(self, HTTP_request, HTTP_reply):
        http_middleware.set_simple_reply(501, "", "", HTTP_reply)

    def process_HTTP(self, HTTP_request, HTTP_reply):
        if HTTP_reply.status_code is not None:
            return

        self.set_CORS_headers(HTTP_request, HTTP_reply)
        method, _, _ = HTTP_request.request_line

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
    logging.basicConfig(filename="api_server.log", level=logging.INFO)

    CORS_settings = (["http://localhost:5173"], [], ["content-type"], [], 600)
    engine = GraphChatServer(CORS_settings=CORS_settings)

    core = engine.process_HTTP
    server = http_server.HTTPServer("0.0.0.0", 8000, core)
    server.start()
