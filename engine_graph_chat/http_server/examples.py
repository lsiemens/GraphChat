import os.path

import http_server
import http_middleware


def HTML_server_core(root_target="./html"):
    root = os.path.realpath(root_target)

    def process_file_server(HTTP_request, HTTP_reply):
        method, target, _ = HTTP_request.request_line

        if method != "GET":
            HTTP_reply.status_code = 501
            HTTP_reply.headers["connection"] = "close"
            return

        http_middleware.load_file_from_target(root, HTTP_request, HTTP_reply)
        http_middleware.set_content_type_from_target(HTTP_request, HTTP_reply)
        HTTP_reply.status_code = 200
        HTTP_reply.headers["connection"] = "close"
    return process_file_server


if __name__ == "__main__":
    root = input("Enter path to site root: ")
    core = HTML_server_core(root)
    server = http_server.HTTPServer("0.0.0.0", 8000, core)
    server.start()
