from collections.abc import Callable
from typing import ParamSpec, TypeVar

from functools import wraps

__all__ = ["PlayerError", "PlayerUnreachableError", "PlayerUnexpectedResponseError"]

P = ParamSpec("P")
R = TypeVar("R")


class PlayerError(Exception):
    """Base class for exceptions in this package."""

    def __init__(self, message: str):
        super().__init__(message)


class PlayerUnreachableError(PlayerError):
    """Exception raised when the player is not reachable.

    This could be due to a timeout or the player being offline.
    """


class PlayerUnexpectedResponseError(PlayerError):
    """Exception raised when the player returns an unexpected response. This is likely a bug in this library."""


def _wrap_in_unxpected_response_error(func: Callable[P, R]) -> Callable[P, R]:
    @wraps(func)
    def wrapped(*args: P.args, **kwargs: P.kwargs) -> R:
        try:
            return func(*args, **kwargs)
        except Exception as e:
            raise PlayerUnexpectedResponseError(f"Unexpected response from player: {e}") from e

    return wrapped
