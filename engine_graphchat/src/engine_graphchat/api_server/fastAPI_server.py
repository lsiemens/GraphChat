import contextlib

from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

from engine_graphchat.core import exceptions, logger_config
from engine_graphchat.api_server import server_core
from engine_graphchat.core.api import pydantic_types


_BASE_URL = "/api/v1"
origins = ["http://localhost:5173"]


@contextlib.asynccontextmanager
async def lifespan(app: FastAPI):
    logger_config.configure(__name__, "fastAPI_server.log")
    yield

api = FastAPI(lifespan=lifespan)
_server_core = server_core.ServerCore()

api.add_middleware(CORSMiddleware,
                   allow_origins=origins,
                   allow_methods=["GET", "POST"],
                   allow_headers=["Content-Type"])

# Graphs


# Nodes
@api.post(_BASE_URL + "/graphs/{graph_id}/nodes")
def POST_graphs_F_nodes(graph_id: str, prompt_api: pydantic_types.PromptAPI):
    reply_node_data = _server_core.POST_graphs_F_nodes(prompt_api)
    node_data_api = pydantic_types.NodeDataAPI()
    node_data_api.from_NodeData(reply_node_data)

    return node_data_api


@api.get(_BASE_URL + "/graphs/{graph_id}/nodes")
def GET_graphs_F_nodes(graph_id: str):
    reply_node_ids = _server_core.GET_graphs_F_nodes()
    node_ids_api = pydantic_types.NodeIDsAPI()
    node_ids_api.from_strings(reply_node_ids)

    return node_ids_api


@api.get(_BASE_URL + "/graphs/{graph_id}/nodes/{node_id}")
def GET_graphs_F_nodes_F(graph_id: str, node_id: str):
    reply_node_data = _server_core.GET_graphs_F_nodes_F(node_id)
    node_data_api = pydantic_types.NodeDataAPI()
    node_data_api.from_NodeData(reply_node_data)

    return node_data_api


@api.get(_BASE_URL + "/graphs/{graph_id}/nodes/{node_id}/info")
def GET_graphs_F_nodes_F_info(graph_id: str, node_id: str):
    raise HTTPException(status_code=501)


# Views
@api.get(_BASE_URL + "/graphs/{graph_id}/views")
def GET_graphs_F_views(graph_id: str):
    reply_view_names = _server_core.GET_graphs_F_views()
    view_names_api = pydantic_types.ViewNamesAPI()
    view_names_api.from_strings(reply_view_names)

    return view_names_api


@api.post(_BASE_URL + "/graphs/{graph_id}/views/{view_name}")
def POST_graphs_F_views_F(graph_id: str, view_name: str, view_upstream_api: pydantic_types.ViewUpstreamAPI):
    view_upstream = view_upstream_api.to_strings()
    reply_view_context = _server_core.POST_graphs_F_views_F(view_name, view_upstream)
    view_context_api = pydantic_types.ViewContextAPI()
    view_context_api.from_strings(reply_view_context)

    return view_context_api


# General info
@api.get(_BASE_URL + "/system/models")
def GET_system_models():
    reply_models = _server_core.GET_system_models()
    models_api = pydantic_types.ModelNamesAPI()
    models_api.from_strings(reply_models)

    return models_api


# General configuration
@api.exception_handler(exceptions.GraphChatError)
async def exception_handler(request: Request, exc: exceptions.GraphChatError):
    status, message = _server_core.exception_handler(exc)
    content = {"message": message}
    return JSONResponse(status_code=status, content=content)

# TODO add error logging for when pydantic fails to validate response or reply object
