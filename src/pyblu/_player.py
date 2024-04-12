from typing import TypeVar, Union, Callable, TypeAlias

import aiohttp
import xmltodict

from pyblu._entities import Status, Volume, SyncStatus, PairedPlayer

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


class Player:
    def __init__(self, host: str, port: int = 11000, session: aiohttp.ClientSession = None):
        """Client for a BluOS player. Uses the HTTP API of the BluOS players to control it.

        The passed sessions will not be closed when the player is closed and has to be closed by the caller.
        If no session is passed, a new session will be created and closed when the player is closed.

        *Player* is an async context manager and can be used with *async with*.

        :param host: The hostname or IP address of the player.
        :param port: The port of the player. Default is 11000.
        :param session: An optional aiohttp.ClientSession to use for requests.

        :return: A new Player.
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

    async def status(self, etag: str | None = None, timeout: int = 30) -> Status:
        """Get the current status of the player.

        This endpoint supports long polling. If **etag** is set, the server will wait until the status changes or the timeout is reached.
        **etag** has to be the last etag received from the server.

        :param etag: The last etag received from the server. Triggers long polling if set.
        :param timeout: The timeout in seconds for long polling.

        :return: The current status of the player. Only selected fields are returned.
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

    async def sync_status(self, etag: str | None = None, timeout: int = 30) -> SyncStatus:
        """Get the SyncStatus of the player.

        This endpoint supports long polling. If **etag** is set, the server will wait until the status changes or the timeout is reached.
        **etag** has to be the last etag received from the server.

        :param etag: The last etag received from the server. Triggers long polling if set.
        :param timeout: The timeout in seconds for long polling.

        :return: The SyncStatus of the player.
        """
        params = {}
        if etag:
            params["etag"] = etag
            params["timeout"] = timeout
        async with self._session.get(f"{self.base_url}/SyncStatus", params=params) as response:
            response.raise_for_status()
            response_data = await response.text()
            response_dict = xmltodict.parse(response_data)

            master_ip = chained_get(response_dict, "SyncStatus", "master", "#text")
            master_port = chained_get(response_dict, "SyncStatus", "master", "@port")
            master = PairedPlayer(ip=master_ip, port=int(master_port)) if master_ip and master_port else None

            slaves_raw = chained_get(response_dict, "SyncStatus", "slave")
            slaves = _parse_slave_list(slaves_raw)

            sync_status = SyncStatus(
                etag=chained_get(response_dict, "SyncStatus", "@etag"),
                sync_stat=chained_get(response_dict, "SyncStatus", "@syncStat"),
                id=chained_get(response_dict, "SyncStatus", "@id"),
                mac=chained_get(response_dict, "SyncStatus", "@mac"),
                name=chained_get(response_dict, "SyncStatus", "@name"),
                icon_url=chained_get(response_dict, "SyncStatus", "@icon"),
                initialized=chained_get(response_dict, "SyncStatus", "@initialized") == "true",
                group=chained_get(response_dict, "SyncStatus", "@group"),
                master=master,
                slaves=slaves,
                zone=chained_get(response_dict, "SyncStatus", "@zone"),
                zone_master=chained_get(response_dict, "SyncStatus", "@zoneMaster") == "true",
                zone_slave=chained_get(response_dict, "SyncStatus", "@zoneSlave") == "true",
                brand=chained_get(response_dict, "SyncStatus", "@brand"),
                model=chained_get(response_dict, "SyncStatus", "@model"),
                model_name=chained_get(response_dict, "SyncStatus", "@modelName"),
                mute_volume_db=chained_get(response_dict, "SyncStatus", "@muteDb", _map=int),
                mute_volume=chained_get(response_dict, "SyncStatus", "@muteVolume", _map=int),
                volume_db=chained_get(response_dict, "SyncStatus", "@db", _map=int),
                volume=chained_get(response_dict, "SyncStatus", "@volume", _map=int),
                schema_version=chained_get(response_dict, "SyncStatus", "@schemaVersion", _map=int),
            )

            return sync_status

    async def volume(self, level: int = None, mute: bool = None, tell_slaves: bool = None) -> Volume:
        """Get or set the volume of the player.
        Call without parameters to get the current volume. Call with parameters to set the volume.

        :param level: The volume level to set. Range is 0-100.
        :param mute: Whether to mute the player.
        :param tell_slaves: Whether to tell grouped speakers to change their volume as well.

        :return: The current volume of the player.
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
        """Start playing the current track. Can also be used to seek within the current track.
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
        """Pause the current track. **toggle** can be used to toggle between playing and pause.

        :param toggle: Toggle between playing and pause.

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
        """Stop the current track. Stopped playback cannot be resumed.

        :return: The playback state after command execution.
        """
        async with self._session.get(f"{self.base_url}/Stop") as response:
            response.raise_for_status()
            response_data = await response.text()
            response_dict = xmltodict.parse(response_data)

            return chained_get(response_dict, "state")

    async def skip(self) -> None:
        """Skip to the next track."""
        async with self._session.get(f"{self.base_url}/Skip") as response:
            response.raise_for_status()

    async def back(self) -> None:
        """Go back to the previous track."""
        async with self._session.get(f"{self.base_url}/Back") as response:
            response.raise_for_status()

    async def add_slave(self, ip: str, port: int = 11000) -> list[PairedPlayer]:
        """Add a secondary player to the current player as a slave.
        If it fails the player won't be in the returned list.

        :param ip: The IP address of the player to add.
        :param port: The port of the player to add. Default is 11000.

        :return: The list of slaves of the player.
        """
        params = {
            "slave": ip,
            "port": port,
        }
        async with self._session.get(f"{self.base_url}/AddSlave", params=params) as response:
            response.raise_for_status()
            response_data = await response.text()
            response_dict = xmltodict.parse(response_data)

            slaves_raw = chained_get(response_dict, "addSlave", "slave")
            slaves = _parse_slave_list(slaves_raw)

            return slaves

    async def add_slaves(self, slaves: list[PairedPlayer]) -> list[PairedPlayer]:
        """Add a list of secondary players to the current player as slaves.
        If it fails the player won't be in the returned list.

        Same as *add_slave* but with a list of players. Makes only one request to player.

        :param slaves: The list of players to add.

        :return: The list of slaves of the player.
        """
        params = {
            "slaves": ",".join(x.ip for x in slaves),
            "ports": ",".join(str(x.port) for x in slaves),
        }
        async with self._session.get(f"{self.base_url}/AddSlave", params=params) as response:
            response.raise_for_status()
            response_data = await response.text()
            response_dict = xmltodict.parse(response_data)

            slaves_raw = chained_get(response_dict, "addSlave", "slave")
            slaves = _parse_slave_list(slaves_raw)

            return slaves


def _parse_slave_list(slaves_raw: list[dict[str, str]]) -> list[PairedPlayer] | None:
    match slaves_raw:
        case {"@id": ip, "@port": port}:
            return [PairedPlayer(ip=ip, port=int(port))]
        case [*slaves_raw]:
            return [PairedPlayer(ip=slave["@id"], port=int(slave["@port"])) for slave in slaves_raw]
        case _:
            return None
