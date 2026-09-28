import logging
import os.path

from . import http_server
from . import http_middleware


def HTML_server_core(root_target="./html"):
    root = os.path.realpath(root_target)

    def process_file_server(HTTP_request, HTTP_reply):
        if HTTP_reply.status_code is not None:
            return

        method, target, _ = HTTP_request.request_line

        if method != "GET":
            http_middleware.set_simple_reply(501, "", "", HTTP_reply)
            return

        path = http_middleware.load_file_from_target(root, HTTP_request, HTTP_reply)
        http_middleware.set_content_type_from_path(path, HTTP_reply)

        if HTTP_reply.status_code is None:
            HTTP_reply.status_code = 200
        HTTP_reply.headers["connection"] = "close"
    return process_file_server


def reflect_json_core(allow_origins, allow_methods, allow_headers, expose_headers, max_age):
    CORS_options = (allow_origins, allow_methods, allow_headers, expose_headers, max_age)
    set_CORS_headers = http_middleware.configure_CORS(*CORS_options)

    def process_backend_reflect(HTTP_request, HTTP_reply):
        if HTTP_reply.status_code is not None:
            return

        method, target, _ = HTTP_request.request_line
        set_CORS_headers(HTTP_request, HTTP_reply)

        match method:
            case "GET":
                http_middleware.set_simple_reply(200, "", "", HTTP_reply)
                return
            case "POST":
                if len(HTTP_request.body) != 0:
                    if "content-type" in HTTP_request.headers:
                        if HTTP_request.headers["content-type"] == "application/json":
                            http_middleware.set_simple_reply(200, HTTP_request.body, ".json", HTTP_reply)
                            return
                http_middleware.set_simple_reply(400, "", "", HTTP_reply)
                return
            case "DELETE":
                http_middleware.set_simple_reply(201, "Content deleted", ".txt", HTTP_reply)
            case _:
                http_middleware.set_simple_reply(501, "", "", HTTP_reply)
                pass
    return process_backend_reflect


if __name__ == "__main__":
    IS_TEST_FILE_SERVER = False
    logging.basicConfig(filename="examples.log", level=logging.INFO)

    core = None
    if IS_TEST_FILE_SERVER:
        print("Static File server")
        root = input("Enter path to site root: ")
        core = HTML_server_core(root)
    else:
        print("API server: reflect all requests.")
        core = reflect_json_core(["http://localhost:5173"], [], ["content-type"], [], 600)
    server = http_server.HTTPServer("0.0.0.0", 8000, core)
    server.start()

