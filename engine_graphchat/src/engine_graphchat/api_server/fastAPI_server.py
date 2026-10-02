from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from engine_graphchat.api_server import server_core
from engine_graphchat.core.api import pydantic_types


_BASE_URL = "/api/v1"
origins = ["http://localhost:5173"]


api = FastAPI()
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

# General info
@api.get(_BASE_URL + "/system/models")
def GET_system_models():
    reply_models = _server_core.GET_system_models()
    models_api = pydantic_types.ModelNamesAPI()
    models_api.from_strings(reply_models)

    return models_api
