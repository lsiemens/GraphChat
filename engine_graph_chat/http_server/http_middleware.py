"""
Middleware for processing HTTP replies from requests
"""

import urllib.parse
import os.path


MIME = {".html": "text/html", ".css": "text/css", ".js": "text/javascript",
        ".mjs": "text/javascript", ".json": "application/json",
        ".ico": "image/vnd.microsoft.icon", ".bmp": "image/bmp",
        ".jpeg": "image/jpeg", ".jpg": "image/jpeg", ".gif": "image/gif",
        ".png": "image/png", ".svg": "image/svg+xml", ".otf": "font/otf",
        ".ttf": "font/ttf", ".md": "text/markdown", ".csv": "text/csv",
        ".txt": "text/plain", ".gz": "application/gzip",
        ".tar": "application/x-tar", ".zip": "application/zip",
        ".7z": "application/x-7z-compressed", ".pdf": "application/pdf",
        ".bin": "application/octet-stream"}


def set_content_type_from_target(HTTP_request, HTTP_reply):
    if HTTP_reply.status_code is not None:
        return

    _, target, _ = HTTP_request.request_line
    _, ext = os.path.splitext(target)

    MIME_string = "application/octet-stream"
    if ext in MIME:
        MIME_string = MIME[ext]
    else:
        if isinstance(HTTP_reply.body, str):
            MIME_string = "text/plain"

    HTTP_reply.headers["content-type"] = MIME_string


def load_file_from_target(root, HTTP_request, HTTP_reply):
    if HTTP_reply.status_code is not None:
        return

    _, target, _ = HTTP_request.request_line

    target = urllib.parse.unquote(target)
    if target.endswith("/"):
        target += "index.html"
    path = os.path.realpath(os.path.join(root, target.lstrip("/")))

    is_valid_path = True
    if not os.path.exists(path):
        print(f"ERROR: path \"{path}\" does not exist!")
        is_valid_path = False

    if not os.path.isfile(path):
        print(f"ERROR: path \"{path}\" is not a file!")
        is_valid_path = False

    if os.path.commonpath([root, path]) != root:
        print(f"ERROR: path \"{path}\" is outside of \"{root}\"")
        is_valid_path = False

    if not is_valid_path:
        HTTP_reply.status_code = 404
        HTTP_reply.headers["connection"] = "close"
        return

    with open(path, "rb") as fin:
        HTTP_reply.body = fin.read()
