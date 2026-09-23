import os.path

import http_server
import http_middleware


def HTML_server_core(root_target="./html"):
    root = os.path.realpath(root_target)

    def process_file_server(HTTP_request, HTTP_reply):
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


def backend_reflect(HTTP_request, HTTP_reply):
    method, target, _ = HTTP_request.request_line

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
        case _:
            http_middleware.set_simple_reply(501, "", "", HTTP_reply)
            pass


if __name__ == "__main__":
    #root = input("Enter path to site root: ")
    #core = HTML_server_core(root)
    core = backend_reflect
    server = http_server.HTTPServer("0.0.0.0", 8000, core)
    server.start()

