import os
import uvicorn


def dev():
    os.environ["USE_MOCK_LLM_SDK"] = "YES"

    uvicorn.run("engine_graphchat.api_server.fastAPI_server:api",
                host="127.0.0.1",
                port=8000,
                reload=True,
                reload_dirs=["src"])


def serve():
    os.environ["USE_MOCK_LLM_SDK"] = "NO"

    uvicorn.run("engine_graphchat.api_server.fastAPI_server:api",
                host="0.0.0.0",
                port=8000,
                reload=False)
