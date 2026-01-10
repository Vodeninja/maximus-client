from .api import (
    MaxApiError,
    MaxBadRequestError,
    MaxNotFoundError,
    MaxUnauthorizedError,
    MaxTooManyRequestsError,
    MaxServiceUnavailableError,
)
from .base import MaximusError
from .connection import ConnectionError
from .auth import AuthError

__all__ = (
    "MaximusError",
    "MaxApiError",
    "MaxBadRequestError", 
    "MaxNotFoundError",
    "MaxUnauthorizedError",
    "MaxTooManyRequestsError",
    "MaxServiceUnavailableError",
    "ConnectionError",
    "AuthError",
)