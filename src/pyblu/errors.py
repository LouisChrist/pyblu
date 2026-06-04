from collections.abc import Awaitable, Callable
from typing import ParamSpec, TypeVar

from functools import wraps

import aiohttp

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


def _wrap_in_unreachable_error(func: Callable[P, Awaitable[R]]) -> Callable[P, Awaitable[R]]:
    @wraps(func)
    async def wrapped(*args: P.args, **kwargs: P.kwargs) -> R:
        try:
            return await func(*args, **kwargs)
        except TimeoutError as e:
            raise PlayerUnreachableError(f"Timout during request: {e}") from e
        except aiohttp.ClientConnectionError as e:
            raise PlayerUnreachableError(f"Connection error: {e}") from e

    return wrapped
