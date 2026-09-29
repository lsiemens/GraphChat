# API servers
Here I have code defining API servers for GraphChat using either my custom http
server `api_server.py` or using FastAPI and Pydantic `fastAPI_server.py`. The
core of the server (common to both) is `server_core.py` and should be
independent of details of the http.

## API Interface
This listed interface if provisional and may not match the implemented
interfaces. The base URL is `/api/v1`

### Graphs
Optional for the future, allow for more than one graph, that can be switched by
the user. For now lets fix graph_id to be zero.

- GET  /graphs : List all available graphs
- POST /graphs : Create new graph
- GET  /graphs/{graph_id} : Get metadata (title, description, ...)

### Nodes

- POST /graphs/{graph_id}/nodes : Create a new node using a prompt
- GET  /graphs/{graph_id}/nodes : List the node ids in the graph
- GET  /graphs/{graph_id}/nodes/{node_id} : Get a given node
- GET  /graphs/{graph_id}/nodes/{node_id}/info : Get metadata for the node (tokens uesd, ...)

### View

- GET /graphs/{graph_id}/view : Optional for the future. Generate a topologically ordered view of the traversable subgraph

### General

- GET /system/models : Get available models
- GET /graphs/{graph_id}/stats : Get graph wide usage and statistics (total cost, tokens)
