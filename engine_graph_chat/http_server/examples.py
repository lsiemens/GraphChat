import urllib.parse
import os.path

import http_server


def HTML_server_core(root_target="./html"):
    root = os.path.realpath(root_target)

    def process_file_server(HTTP_request, HTTP_reply):
        method, target, _ = HTTP_request.first_line

        target = urllib.parse.unquote(target)
        if target == "/":
            target = "/index.html"
        path = os.path.realpath(os.path.join(root, target.lstrip("/")))

        is_valid_path = True
        if not os.path.exists(path):
            print(f"ERROR: path \"{path}\" does not exist!")
            is_valid_path = False

        if not os.path.isfile(path):
            print(f"ERROR: path \"{path}\" is not a file!")
            is_valid_path = False

        if os.path.commonpath([root, path]) != root:
            print(f"ERROR: path \"{path}\" is outside of \"{root_target}\"")
            is_valid_path = False

        if not is_valid_path:
            HTTP_reply.status_code = 404
            HTTP_reply.headers["connection"] = "close"
            return

        if method != "GET":
            HTTP_reply.status_code = 501
            HTTP_reply.headers["connection"] = "close"
            return

        body = None
        with open(path, "r") as fin:
            body = fin.read()

        HTTP_reply.status_code = 200
        HTTP_reply.headers["connection"] = "close"
        HTTP_reply.headers["content-type"] = "text/html"
        HTTP_reply.body = body
    return process_file_server


if __name__ == "__main__":
    root = input("Enter path to site root: ")
    core = HTML_server_core(root)
    server = http_server.HTTPServer("0.0.0.0", 8000, core)
    server.start()
