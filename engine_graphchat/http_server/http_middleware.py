"""
Middleware for processing HTTP replies from requests
"""

import urllib.parse
import os.path

from . import http_message


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


def set_content_type_from_ext(ext, HTTP_reply):
    MIME_string = "application/octet-stream"
    if ext in MIME:
        MIME_string = MIME[ext]
    else:
        if isinstance(HTTP_reply.body, str):
            MIME_string = "text/plain"

    HTTP_reply.headers["content-type"] = MIME_string


def set_content_type_from_path(path, HTTP_reply):
    if HTTP_reply.status_code is not None:
        return

    _, ext = os.path.splitext(path)
    set_content_type_from_ext(ext, HTTP_reply)


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
        page_404 = make_simple_page(404, "Page not found!")
        set_simple_reply(404, page_404, ".html", HTTP_reply)
        return

    with open(path, "rb") as fin:
        HTTP_reply.body = fin.read()
    return path


def configure_CORS(allow_origins, allow_methods, allow_headers, expose_headers, max_age):
    all_allowed_methods = ["GET", "HEAD", "POST"] + allow_methods
    # TODO add processing for "*"
    def set_CORS_headers(HTTP_request, HTTP_reply):
        if HTTP_reply.status_code is not None:
            # HTTP_request and HTTP_reply can not be trusted
            return

        method, _, _ = HTTP_request.request_line

        if "origin" not in HTTP_request.headers:
            return

        origin = HTTP_request.headers["origin"]

        if origin not in allow_origins:
            set_simple_reply(403, "", "", HTTP_reply)
            return

        # CORS preflight request
        if (method == "OPTIONS") and ("access-control-request-method" in HTTP_request.headers):
            request_method = HTTP_request.headers["access-control-request-method"]
            HTTP_reply.headers["access-control-allow-origin"] = origin
            HTTP_reply.headers["vary"] = "origin"
            HTTP_reply.headers["access-control-allow-methods"] = ", ".join(allow_methods)
            HTTP_reply.headers["access-control-allow-headers"] = ", ".join(allow_headers)
            HTTP_reply.headers["access-control-max-age"] = str(max_age)
            set_simple_reply(204, "", "", HTTP_reply)
            return

        # From the specifications GET, HEAD and POST are CORS-safelisted
        if method not in all_allowed_methods:
            set_simple_reply(403, "", "", HTTP_reply)
            return

        HTTP_reply.headers["access-control-allow-origin"] = origin
        if len(expose_headers) > 0:
            HTTP_reply.headers["access-control-expose-headers"] = ", ".join(expose_headers)

    return set_CORS_headers

def set_simple_reply(status_code, body, ext, HTTP_reply):
    if HTTP_reply.status_code is not None:
        return

    HTTP_reply.status_code = status_code
    HTTP_reply.body = body

    try:
        if len(HTTP_reply.body) != 0:
            set_content_type_from_ext(ext, HTTP_reply)
    except TypeError:
        raise http_message.HTTPError("ERROR: body must be a string or bytes")
    HTTP_reply.headers["connection"] = "close"


def make_simple_page(title, content):
    page = "<!DOCTYPE html>" \
           "<html>" \
          f"<head><title>{title}</title></head>" \
           "<body style=\"text-align:center;\">" \
          f"<h1>{title}</h1>" \
          f"<div>{content}</div>" \
           "</body>" \
           "</html>"
    return page
