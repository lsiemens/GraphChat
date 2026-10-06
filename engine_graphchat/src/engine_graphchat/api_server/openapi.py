OPENAPI_VERSION = "3.1.1"


def get_servers(host, port):
    servers = [
        {"url": f"http://{host}:{port}/api/v1"},
    ]
    return servers


def ref(name, component_type="schemas"):
    return {"$ref": f"#/components/{component_type}/{name}"}


def array_of(name):
    return {"type": "array", "items": ref(name)}


def object(name, properties):
    return {
        name: {
            "type": "object",
            "properties": properties,
            "required": list(properties.keys()),
            "additionalProperties": False,
        }
    }


def json_response(name, type_ref, description):
    return {
        name: {
            "description": description,
            "content": {
                "application/json": {
                    "schema": ref(type_ref),
                },
            },
        },
    }


INFO = {
    "title": "engine_graphchat",
    "version": "1",
}


GET_SYSTEM_MODELS = {
    "/system/models": {
        "get": {
            "operationId": "GET_system_models",
            "responses": {
                "200": ref("ModelNamesAPI", "responses"),
            },
        },
    },
}


SCHEMAS = {
    **object("ModelNamesAPI", {"models": array_of("ModelName")}),
    "ModelName": {
        "type": "string",
        "pattern": "^[!-~]+$",
    },
}


RESPONSES = {
    **json_response("ModelNamesAPI", "ModelNamesAPI", "List available LLM models"),
}


def get_openapi():
    host = "0.0.0.0"
    port = "8000"

    schema = {
        "openapi": OPENAPI_VERSION,
        "info": INFO,
        "servers": get_servers(host, port),
        "paths": {**GET_SYSTEM_MODELS},
        "components": {"schemas": SCHEMAS, "responses": RESPONSES}}

    return schema
