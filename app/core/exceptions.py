class UnauthorizedError(Exception):
    """Authorization error (HTTP 401)."""

    status_code = 401

    def __init__(self, message="Unauthorized", *, detail=None):
        self.message = message
        self.detail = detail
        super().__init__(message)


class NotFoundError(Exception):
    """Resource not found error (HTTP 404)."""

    status_code = 404

    def __init__(self, message="Not Found", *, detail=None):
        self.message = message
        self.detail = detail
        super().__init__(message)


class BadRequestError(Exception):
    """Bad request error (HTTP 400)."""

    status_code = 400

    def __init__(self, message="Bad Request", *, detail=None):
        self.message = message
        self.detail = detail
        super().__init__(message)
