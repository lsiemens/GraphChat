from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from engine_graphchat.core.api import pydantic_types
from engine_graphchat.core.dag import node


api = FastAPI()

origins = ["http://localhost:5173"]

api.add_middleware(CORSMiddleware,
                   allow_origins=origins,
                   allow_methods=[],
                   allow_headers=[])

@api.post("/api")
def create_node(prompt: pydantic_types.PromptAPI):
    usage = node.NodeUsage(0,0,0,0,0)
    reply = node.NodeReply("", "No Content", "Done", usage)
    reply_node = prompt.to_NodeData()
    reply_node.id = "No_ID"
    reply_node.reply = reply

    response = pydantic_types.NodeDataApi()
    response.from_NodeData(reply_node)

    return response
