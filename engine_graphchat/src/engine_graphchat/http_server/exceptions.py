"""Common exceptions for the HTTP server
"""


class HTTPError(Exception):
    """A generic HTTP server error

    The base class for HTTP errors.
    """

    def format(self, message):
        if not isinstance(message, str):
            raise TypeError("Error message must be a string")

        if message.strip() == "":
            raise ValueError("Error message must not be empty")

        return {"type": type(self).__name__, "message": message}


class NotFoundError(HTTPError):
    """Raised when an object or resource can not be found"""


class ParseError(HTTPError):
    """Raised when an object can not be parsed"""


class RequestProtocolError(ParseError):
    """Raised when an request violates defined protocols"""


class SerializeError(HTTPError):
    """Raised when an object can not be serialized"""


class ReplyProtocolError(SerializeError):
    """Raised when an reply violates defined protocols"""
