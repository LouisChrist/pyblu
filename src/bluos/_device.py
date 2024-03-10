from typing import TypeVar, Union, Callable, TypeAlias

import aiohttp
import xmltodict

from bluos._entities import Status, Volume

StringDict: TypeAlias = dict[str, Union[str, "StringDict"]]
# pylint: disable=invalid-name
T: TypeAlias = TypeVar("T")


def chained_get(data: StringDict, *keys, _map: Callable[[str], T] = lambda x: x) -> T | None:
    local_data = data
    for key in keys:
        local_data = local_data.get(key)
        if not local_data:
            return None
    return _map(local_data)


class BluOSDevice:
    def __init__(self, host: str, port: int = 11000, session: aiohttp.ClientSession = None):
        """Represents a BluOS device.

        The passed sessions will not be closed when the device is closed.

        :param host: The hostname or IP address of the device.
        :param port: The port of the device. Default is 11000.
        :param session: An optional aiohttp.ClientSession to use for requests. If not set, a new session will be created.

        :return: A new BluOS device.
        """
        self.base_url = f"http://{host}:{port}"
        if session:
            self._session_owned = False
            self._session = session
        else:
            self._session_owned = True
            self._session = aiohttp.ClientSession()

    async def close(self):
        if self._session_owned:
            await self._session.close()

    async def __aenter__(self):
        return self

    async def __aexit__(self, *args):
        await self.close()

    async def status(self, etag: str = None, timeout: int = 30) -> Status:
        """Get the current status of the device. Uses the /Status endpoint.

        This endpoint supports long polling. If etag is set, the server will wait until the status changes or the timeout is reached.

        :param etag: The last etag received from the server. Triggers long polling if set.
        :param timeout: The timeout in seconds for long polling.

        :return: The current status of the device. Only selected fields are returned.
        """
        params = {}
        if etag:
            params["etag"] = etag
            params["timeout"] = timeout
        async with self._session.get(f"{self.base_url}/Status", params=params) as response:
            response.raise_for_status()
            response_data = await response.text()
            response_dict = xmltodict.parse(response_data)

            status = Status(
                etag=chained_get(response_dict, "status", "@etag"),
                state=chained_get(response_dict, "status", "state"),
                album=chained_get(response_dict, "status", "album"),
                artist=chained_get(response_dict, "status", "artist"),
                name=chained_get(response_dict, "status", "title1"),
                image=chained_get(response_dict, "status", "image"),
                volume=chained_get(response_dict, "status", "volume", _map=int),
                mute=chained_get(response_dict, "status", "mute") == "1",
                seconds=chained_get(response_dict, "status", "secs", _map=int),
                total_seconds=chained_get(response_dict, "status", "totlen", _map=float),
            )

            return status

    async def mac(self) -> str:
        """Get the MAC address of the device. Uses the /SyncStatus endpoint.

        :return: The MAC address of the device as string.
        """
        async with self._session.get(f"{self.base_url}/SyncStatus") as response:
            response.raise_for_status()
            response_data = await response.text()
            response_dict = xmltodict.parse(response_data)

            return chained_get(response_dict, "SyncStatus", "@mac")

    async def volume(self, level: int = None, mute: bool = None, tell_slaves: bool = None) -> Volume:
        """Get or set the volume of the device. Uses the /Volume endpoint.
        Call without parameters to get the current volume. Call with parameters to set the volume.

        :param level: The volume level to set. Range is 0-100.
        :param mute: Whether to mute the device.
        :param tell_slaves: Whether to tell grouped speakers to change their volume as well.

        :return: The current volume of the device.
        """
        params = {}
        if level:
            params["level"] = level
        if mute:
            params["mute"] = "1" if mute else "0"
        if tell_slaves:
            params["tell_slaves"] = "1" if tell_slaves else "0"

        async with self._session.get(f"{self.base_url}/Volume", params=params) as response:
            response.raise_for_status()
            response_data = await response.text()
            response_dict = xmltodict.parse(response_data)

            volume = Volume(
                volume=chained_get(response_dict, "volume", "#text", _map=int),
                db=chained_get(response_dict, "volume", "@db", _map=float),
                mute=chained_get(response_dict, "volume", "@mute") == "1",
            )

            return volume

    async def play(self, seek: int = None) -> str:
        """Start playing the current track. Uses the /Play endpoint. Can also be used to seek within the current track.
        Works only when paused, not when stopped.

        :param seek: The position in seconds to seek to.
        :return: The playback state after command execution.
        """
        params = {}
        if seek:
            params["seek"] = seek

        async with self._session.get(f"{self.base_url}/Play", params=params) as response:
            response.raise_for_status()
            response_data = await response.text()
            response_dict = xmltodict.parse(response_data)

            return chained_get(response_dict, "state")

    async def pause(self, toggle: bool = None) -> str:
        """Pause or unpause the current track. Uses the /Pause endpoint.
        :param toggle: Toggle between pause and unpause.

        :return: The playback state after command execution.
        """
        params = {}
        if toggle:
            params["toggle"] = "1"

        async with self._session.get(f"{self.base_url}/Pause", params=params) as response:
            response.raise_for_status()
            response_data = await response.text()
            response_dict = xmltodict.parse(response_data)

            return chained_get(response_dict, "state")

    async def stop(self) -> str:
        """Stop the current track. Uses the /Stop endpoint. Stopped playback cannot be resumed.

        :return: The playback state after command execution.
        """
        async with self._session.get(f"{self.base_url}/Stop") as response:
            response.raise_for_status()
            response_data = await response.text()
            response_dict = xmltodict.parse(response_data)

            return chained_get(response_dict, "state")

    async def skip(self) -> None:
        """Skip to the next track. Uses the /Skip endpoint."""
        async with self._session.get(f"{self.base_url}/Skip") as response:
            response.raise_for_status()

    async def back(self) -> None:
        """Go back to the previous track. Uses the /Back endpoint."""
        async with self._session.get(f"{self.base_url}/Back") as response:
            response.raise_for_status()
