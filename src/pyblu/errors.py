from typing import Awaitable, Callable, TypeVar, Any, cast

from functools import wraps

import aiohttp

__all__ = ["PlayerError", "PlayerUnreachableError", "PlayerUnexpectedResponseError"]

FuncT = TypeVar("FuncT", bound=Callable[..., Any])
AsyncFuncT = TypeVar("AsyncFuncT", bound=Callable[..., Awaitable[Any]])


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


def _wrap_in_unxpected_response_error(func: FuncT) -> FuncT:
    @wraps(func)
    def wrapped(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            raise PlayerUnexpectedResponseError(f"Unexpected response from player: {e}") from e

    return cast(FuncT, wrapped)


def _wrap_in_unreachable_error(func: AsyncFuncT) -> AsyncFuncT:
    @wraps(func)
    async def wrapped(*args, **kwargs):
        try:
            return await func(*args, **kwargs)
        except TimeoutError as e:
            raise PlayerUnreachableError(f"Timout during request: {e}") from e
        except aiohttp.ClientConnectionError as e:
            raise PlayerUnreachableError(f"Connection error: {e}") from e

    return cast(AsyncFuncT, wrapped)
