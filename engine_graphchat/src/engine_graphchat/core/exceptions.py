"""Common exceptions for the GraphChat engine
"""


class GraphChatError(Exception):
    """A generic GraphChat error

    The base class for GraphChat errors.
    """

    def format(self, message):
        if not isinstance(message, str):
            raise TypeError("Error message must be a string")

        if message.strip() == "":
            raise ValueError("Error message must not be empty")

        return {"type": type(self).__name__, "message": message}


class NotFoundError(GraphChatError):
    """Raised when an object or resource can not be found."""


class ContentError(GraphChatError):
    """Raised when content is missing malformed or invalid"""


class InvalidGraphError(ContentError):
    """Raised when a graph or subgraph is missing data, malformed or invalid"""


class InvalidNodeError(ContentError):
    """Raised when a node is missing data or malformed or invalid"""


class UpstreamError(GraphChatError):
    """Raised when an external system fails"""


class StorageError(UpstreamError):
    """Raised when a storage or storage like system fails"""


class ServiceError(UpstreamError):
    """Raised when an external service fails"""
