"""Common exceptions for the HTTP server
"""


class HTTPError(Exception):
    """A generic HTTP server error

    The base class for HTTP errors.
    """


class NotFoundError(HTTPError):
    """Raised when an object or resource can not be found"""


class ParseError(HTTPError):
    """Raised when an object can not be parsed"""


class ProtocolError(HTTPError):
    """Raised when an object violates defined protocols"""


class SerializeError(HTTPError):
    """Raised when an object can not be serialized"""
