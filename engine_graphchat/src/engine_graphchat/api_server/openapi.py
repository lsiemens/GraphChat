from engine_graphchat.core import exceptions


OPENAPI_VERSION = "3.1.1"


def get_servers(host, port):
    servers = [
        {"url": f"http://{host}:{port}/api/v1"},
    ]
    return servers


def ref(name, component_type="schemas"):
    return {"$ref": f"#/components/{component_type}/{name}"}


def array_of(schema):
    return {"type": "array", "items": schema}


def nullable(schema):
    return {"anyOf": [schema, {"type": "null"}]}


def object_schema(schema_name, properties):
    return {
        schema_name: {
            "type": "object",
            "properties": properties,
            "required": list(properties.keys()),
            "additionalProperties": False,
        }
    }


def json_response_schema(schema_name, type_ref, description):
    return {
        schema_name: {
            "description": description,
            "content": {
                "application/json": {
                    "schema": ref(type_ref),
                },
            },
        },
    }


def json_request_schema(schema_name, type_ref, description):
    return {
        schema_name: {
            "description": description,
            "content": {
                "application/json": {
                    "schema": ref(type_ref),
                },
            },
            "required": True,
        },
    }


def parameter_schema(schema_name, parameter_name, type_ref, description):
    return {
        schema_name: {
            "name": parameter_name,
            "in": "path",
            "required": True,
            "description": description,
            "schema": ref(type_ref),
        },
    }


def http_method(method, operationId, responses_type_ref, **kwargs):
    data = {
        method: {
            "operationId": operationId,
            "responses": {
                "200": ref(responses_type_ref, "responses"),
            },
        },
    }

    if "parameters" in kwargs:
        parameters = kwargs["parameters"]
        if len(parameters) > 0:
            data[method]["parameters"] = parameters

    if "request_type_ref" in kwargs:
        request_type_ref = kwargs["request_type_ref"]
        if request_type_ref is not None:
            data[method]["requestBody"] = ref(request_type_ref, "requestBodies")

    if "error_codes" in kwargs:
        error_codes = kwargs["error_codes"]
        for status_code in error_codes:
            if status_code < 400:
                raise exceptions.ContentError("openAPI: error codes are 4XX or 5XX")
            data[method]["responses"][str(status_code)] = ref("Error", "responses")

    return data


INFO = {
    "title": "engine_graphchat",
    "version": "1",
}


NODE_ENDPOINTS = {
    "/graphs/0/nodes": {
        **http_method("get", "GET_graph_node_list", "NodeIDsAPI"),
        **http_method(
            "post",
            "POST_graph_node",
            "NodeDataAPI",
            request_type_ref="PromptAPI",
            error_codes=[400, 404, 415, 422],
        ),
    },
    "/graphs/0/nodes/{node_id}": {
        **http_method(
            "get",
            "GET_graph_node",
            "NodeDataAPI",
            parameters=[ref("NodeID", "parameters")],
            error_codes=[400, 404],
        ),
    }
}


VIEW_ENDPOINTS = {
    "/graphs/0/views": {
        **http_method("get", "GET_view_name_list", "ViewNamesAPI"),
    },
    "/graphs/0/views/{view_name}": {
        **http_method(
            "post",
            "POST_view_arguments",
            "ViewContextAPI",
            request_type_ref="ViewUpstreamAPI",
            parameters=[ref("ViewName", "parameters")],
            error_codes=[400, 404, 415, 422],
        ),
    }
}


SYSTEM_ENDPOINTS = {
    "/system/models": {
        **http_method("get", "GET_system_models", "ModelNamesAPI"),
    },
}


SCHEMAS = {
    **object_schema("PromptAPI", {
        "model": ref("ModelName"),
        "upstream": array_of(ref("NodeID")),
        "context": array_of(ref("NodeID")),
        "timestamp": {"type": "string"},
        "content": {"type": "string"},
    }),
    **object_schema("NodeDataAPI", {
        "id": ref("NodeID"),
        "upstream": array_of(ref("NodeID")),
        "context": array_of(ref("NodeID")),
        "request": {"type": "string"},
        "reply": {"type": "string"},
        "model": ref("ModelName"),
        "costUSD": nullable({"type": "number"}),
    }),
    **object_schema("NodeIDsAPI", {"ids": array_of(ref("NodeID"))}),
    **object_schema("ModelNamesAPI", {"models": array_of(ref("ModelName"))}),
    **object_schema("ViewNamesAPI", {"viewNames": array_of(ref("ViewName"))}),
    **object_schema("ViewUpstreamAPI", {"upstream": array_of(ref("NodeID"))}),
    **object_schema("ViewContextAPI", {"context": array_of(ref("NodeID"))}),
    **object_schema("Error", {
        "type": {"type": "string"},
        "message": {"type": "string"},
    }),
    "GraphID": {
        "type": "string",
        "pattern": "^[0-9a-f]{32}$",
    },
    "NodeID": {
        "type": "string",
        "pattern": "^[0-9a-f]{64}$",
    },
    "ModelName": {
        "type": "string",
    },
    "ViewName": {
        "type": "string",
    },
}


RESPONSES = {
    **json_response_schema("NodeDataAPI", "NodeDataAPI", "A node in the graph"),
    **json_response_schema("NodeIDsAPI", "NodeIDsAPI", "List all of the NodeIDs in the graph"),
    **json_response_schema("ModelNamesAPI", "ModelNamesAPI", "List available LLM models"),
    **json_response_schema("ViewNamesAPI", "ViewNamesAPI", "List the available view methods"),
    **json_response_schema("ViewContextAPI", "ViewContextAPI", "The context given by the view method applied to the upstream"),
    **json_response_schema("Error", "Error", "Standard HTTP error"),
}


PARAMETERS = {
    **parameter_schema("GraphID", "graph_id", "GraphID", "Index of the desired graph"),
    **parameter_schema("NodeID", "node_id", "NodeID", "Identifier of the desired node"),
    **parameter_schema("ViewName", "view_name", "ViewName", "Name of the desired view method"),
}

REQUESTBODIES = {
    **json_request_schema("PromptAPI", "PromptAPI", "Prompt for the LLM including configuration and context"),
    **json_request_schema("ViewUpstreamAPI", "ViewUpstreamAPI", "The upstream used to calculate a valid context with a given view method"),
}


def get_openapi():
    host = "127.0.0.1"
    port = "8000"

    schema = {
        "openapi": OPENAPI_VERSION,
        "info": INFO,
        "servers": get_servers(host, port),
        "paths": {
            **NODE_ENDPOINTS,
            **VIEW_ENDPOINTS,
            **SYSTEM_ENDPOINTS,
        },
        "components": {
            "schemas": SCHEMAS,
            "responses": RESPONSES,
            "parameters": PARAMETERS,
            "requestBodies": REQUESTBODIES,
        },
    }

    return schema
