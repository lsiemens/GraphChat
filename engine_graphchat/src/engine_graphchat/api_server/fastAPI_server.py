from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from engine_graphchat.api_server import server_core
from engine_graphchat.core.api import pydantic_types


api = FastAPI()
_server_core = server_core.ServerCore()

origins = ["http://localhost:5173"]

api.add_middleware(CORSMiddleware,
                   allow_origins=origins,
                   allow_methods=["GET", "POST"],
                   allow_headers=["Content-Type"])


@api.post("/api")
def create_node(prompt_api: pydantic_types.PromptAPI):
    reply_node_data = _server_core.POST_prompt(prompt_api)
    node_data_api = pydantic_types.NodeDataApi()
    node_data_api.from_NodeData(reply_node_data)

    return node_data_api
