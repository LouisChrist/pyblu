from collections.abc import Awaitable, Callable

from pyblu.entities import ListeningModeValue, SubwooferModeValue
from pyblu.parse import parse_listening_modes, parse_subwoofer_modes


class ListeningMode:
    def __init__(self, get: Callable[..., Awaitable[bytes]]):
        self._get = get

    async def _query_endpoint(self, timeout: float | None = None) -> list[ListeningModeValue]:
        data = await self._get("/Settings?id=audio", timeout=timeout)
        return parse_listening_modes(data)

    async def get(self, timeout: float | None = None) -> str | None:
        for val in await self._query_endpoint(timeout):
            if val.active:
                return val.display_name
        return None

    async def set(self, mode: str, timeout: float | None = None) -> None:
        await self._get("/alsa_setting", params={"preset": mode}, timeout=timeout)

    async def is_available(self, timeout: float | None = None) -> bool:
        return len(await self._query_endpoint(timeout)) > 0

    async def values(self, timeout: float | None = None) -> list[ListeningModeValue]:
        return await self._query_endpoint(timeout)


class SubwooferMode:
    def __init__(self, get: Callable[..., Awaitable[bytes]]):
        self._get = get

    async def _query_endpoint(self, timeout: float | None = None) -> list[SubwooferModeValue]:
        data = await self._get("/Settings?id=audio", timeout=timeout)
        return parse_subwoofer_modes(data)

    async def get(self, timeout: float | None = None) -> str | None:
        for val in await self._query_endpoint(timeout):
            if val.active:
                return val.display_name
        return None

    async def set(self, mode: str, timeout: float | None = None) -> None:
        await self._get("/audiomodes", params={"subwoofer": mode}, timeout=timeout)

    async def is_available(self, timeout: float | None = None) -> bool:
        return len(await self._query_endpoint(timeout)) > 0

    async def values(self, timeout: float | None = None) -> list[SubwooferModeValue]:
        return await self._query_endpoint(timeout)


class Settings:  # pylint: disable=too-few-public-methods
    def __init__(self, get: Callable[..., Awaitable[bytes]]):
        self.listening_mode = ListeningMode(get)
        self.subwoofer_mode = SubwooferMode(get)
