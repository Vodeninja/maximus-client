from .base import MaximusError


class MaxApiError(MaximusError):
    """Base API error."""
    pass


class MaxBadRequestError(MaxApiError):
    """400 Bad Request."""
    pass


class MaxUnauthorizedError(MaxApiError):
    """401 Unauthorized."""
    pass


class MaxNotFoundError(MaxApiError):
    """404 Not Found."""
    pass


class MaxTooManyRequestsError(MaxApiError):
    """429 Too Many Requests."""
    pass


class MaxServiceUnavailableError(MaxApiError):
    """503 Service Unavailable."""
    pass