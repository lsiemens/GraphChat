from engine_graphchat.core import exceptions, logger_config
from engine_graphchat.api_server import server_core
from engine_graphchat.core.api import api_json, api_types

from engine_graphchat.http_server import http_server, http_middleware


class GraphChatServer:
    _Base_URL = "/api/v1"

    def __init__(self, CORS_settings):
        self._server_core = server_core.ServerCore()

        self.set_CORS_headers = http_middleware.configure_CORS(*CORS_settings)

        JSON_openapi = api_json.json.dumps(self._server_core.openapi_schema)
        self.filter_openapi = http_middleware.configure_openAPI(JSON_openapi)

        route_patterns = {
            "graphs_F_nodes": "/graphs/{graph_id}/nodes",
            "graphs_F_nodes_F": "/graphs/{graph_id}/nodes/{node_id}",
            "graphs_F_nodes_F_info": "/graphs/{graph_id}/nodes/{node_id}/info",
            "graphs_F_views": "/graphs/{graph_id}/views",
            "graphs_F_views_F": "/graphs/{graph_id}/views/{view_name}",
            "system_models": "/system/models",
        }
        route_methods = {
            "graphs_F_nodes": ["GET", "POST"],
            "graphs_F_nodes_F": ["GET"],
            "graphs_F_nodes_F_info": ["GET"],
            "graphs_F_views": ["GET"],
            "graphs_F_views_F": ["POST"],
            "system_models": ["GET"],
        }
        route_patterns = {key: self._Base_URL + value for key, value in route_patterns.items()}
        self.route_URL, self.filter_allowed_route_methods = http_middleware.configure_routing(route_patterns, route_methods)

    def GET(self, HTTP_request, HTTP_reply):
        _, target, _ = HTTP_request.request_line

        label, url_parameters = self.route_URL(target)

        # --- Enter Internal CORE --- #
        JSON_reply = "{}"
        match label:
            case "graphs_F_nodes":
                reply_node_ids = self._server_core.GET_graphs_F_nodes()
                node_ids_api = api_types.NodeIDsAPI()
                node_ids_api.from_strings(reply_node_ids)
                JSON_reply = api_json.dump_JSON_as_type(node_ids_api, api_types.NodeIDsAPI)

            case "graphs_F_nodes_F":
                node_id = url_parameters["node_id"]
                reply_node_data = self._server_core.GET_graphs_F_nodes_F(node_id)
                node_data_api = api_types.NodeDataApi()
                node_data_api.from_NodeData(reply_node_data)
                JSON_reply = api_json.dump_JSON_as_type(node_data_api, api_types.NodeDataApi)

            case "graphs_F_nodes_F_info":
                http_middleware.set_error_reply(501, "GET: info handler not implemented", HTTP_reply)
                return

            case "graphs_F_views":
                reply_view_names = self._server_core.GET_graphs_F_views()
                view_names_api = api_types.ViewNamesAPI()
                view_names_api.from_strings(reply_view_names)
                JSON_reply = api_json.dump_JSON_as_type(view_names_api, api_types.ViewNamesAPI)

            case "system_models":
                reply_models = self._server_core.GET_system_models()
                models_api = api_types.ModelNamesAPI()
                models_api.from_strings(reply_models)
                JSON_reply = api_json.dump_JSON_as_type(models_api, api_types.ModelNamesAPI)

            case _:
                http_middleware.set_error_reply(500, "GET: missing endpoint handler", HTTP_reply)
                return
        # --- Exit Internal CORE --- #

        http_middleware.set_simple_reply(200, JSON_reply, ".json", HTTP_reply)

    def POST(self, HTTP_request, HTTP_reply):
        _, target, _ = HTTP_request.request_line

        if (HTTP_request.body) == 0:
            http_middleware.set_error_reply(400, "HTTP POST request must have a body", HTTP_reply)
            return

        if "content-type" not in HTTP_request.headers:
            http_middleware.set_error_reply(415, "HTTP POST request must set content-type", HTTP_reply)
            return

        if HTTP_request.headers["content-type"] != "application/json":
            http_middleware.set_error_reply(415, "HTTP POST request body must be JSON", HTTP_reply)
            return

        label, url_parameters = self.route_URL(target)
        JSON_request = HTTP_request.body

        # --- Enter Internal CORE --- #
        JSON_reply = {}
        match label:
            case "graphs_F_nodes":
                prompt_api = api_json.load_JSON_as_type(JSON_request, api_types.PromptAPI)
                reply_node_data = self._server_core.POST_graphs_F_nodes(prompt_api)
                node_data_api = api_types.NodeDataApi()
                node_data_api.from_NodeData(reply_node_data)
                JSON_reply = api_json.dump_JSON_as_type(node_data_api, api_types.NodeDataApi)

            case "graphs_F_views_F":
                view_name = url_parameters["view_name"]
                view_upstream_api = api_json.load_JSON_as_type(JSON_request, api_types.ViewUpstreamAPI)
                view_upstream = view_upstream_api.to_strings()
                reply_view_context = self._server_core.POST_graphs_F_views_F(view_name, view_upstream)
                view_context_api = api_types.NodeDataApi()
                view_context_api.from_NodeData(reply_view_context)
                JSON_reply = api_json.dump_JSON_as_type(view_context_api, api_types.ViewContextAPI)

            case _:
                http_middleware.set_error_reply(500, "POST: missing endpoint handler", HTTP_reply)
                return

        # --- Exit Internal CORE --- #

        http_middleware.set_simple_reply(200, JSON_reply, ".json", HTTP_reply)

    def DELETE(self, HTTP_request, HTTP_reply):
        http_middleware.set_error_reply(500, "DELETE not implemented", HTTP_reply)

    def process_HTTP(self, HTTP_request, HTTP_reply):
        if HTTP_reply.status_code is not None:
            return

        self.set_CORS_headers(HTTP_request, HTTP_reply)
        self.filter_openapi(HTTP_request, HTTP_reply)

        if HTTP_reply.status_code is not None:
            return

        method, target, _ = HTTP_request.request_line
        label, _ = self.route_URL(target)
        self.filter_allowed_route_methods(method, label, HTTP_reply)

        if HTTP_reply.status_code is not None:
            return

        try:
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
                    http_middleware.set_error_reply(500, "process_HTTP: Missing HTTP method handler", HTTP_reply)
                    return
        except exceptions.GraphChatError as e:
            status, body = self._server_core.exception_handler(e)
            http_middleware.set_simple_reply(status, body, ".json", HTTP_reply)
            return

        http_middleware.set_error_reply(500, "process_HTTP: Control flow failure", HTTP_reply)


if __name__ == "__main__":
    logger_config.configure("engine_graphchat", "api_server.log")

    CORS_settings = (["http://localhost:5173"], [], ["content-type"], [], 600)
    engine = GraphChatServer(CORS_settings=CORS_settings)

    core = engine.process_HTTP
    server = http_server.HTTPServer("0.0.0.0", 8000, core)
    server.start()
