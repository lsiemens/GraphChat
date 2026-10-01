# API servers
Here I have code defining API servers for GraphChat using either my custom http
server `api_server.py` or using FastAPI and Pydantic `fastAPI_server.py`. The
core of the server (common to both) is `server_core.py` and should be
independent of details of the http.

# API Specification
See the [shared API interface contract](/docs/API.md) for the
specification of intended endpoints and request/response schemas.
