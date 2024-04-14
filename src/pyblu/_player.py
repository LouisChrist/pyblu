import aiohttp
import xmltodict

from pyblu._entities import Status, Volume, SyncStatus, PairedPlayer, PlayQueue
from pyblu._parse import parse_slave_list, parse_sync_status, parse_status, parse_volume, chained_get, parse_play_queue


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

            status = parse_status(response_dict)

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

            sync_status = parse_sync_status(response_dict)

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

            volume = parse_volume(response_dict)

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
            slaves = parse_slave_list(slaves_raw)

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
            slaves = parse_slave_list(slaves_raw)

            return slaves

    async def remove_slave(self, ip: str, port: int = 11000) -> SyncStatus:
        """Remove a secondary player from the group.

        :param ip: The IP address of the player to remove.
        :param port: The port of the player to remove. Default is 11000.

        :return: The SyncStatus of the player.
        """
        params = {
            "slave": ip,
            "port": port,
        }
        async with self._session.get(f"{self.base_url}/RemoveSlave", params=params) as response:
            response.raise_for_status()
            response_data = await response.text()
            response_dict = xmltodict.parse(response_data)

            sync_status = parse_sync_status(response_dict)

            return sync_status

    async def remove_slaves(self, slaves: list[PairedPlayer]) -> SyncStatus:
        """Remove a list of secondary players from the group.

        Same as *remove_slave* but with a list of players. Makes only one request to player.

        :param slaves: The list of players to remove.

        :return: The SyncStatus of the player.
        """
        params = {
            "slaves": ",".join(x.ip for x in slaves),
            "ports": ",".join(str(x.port) for x in slaves),
        }
        async with self._session.get(f"{self.base_url}/RemoveSlave", params=params) as response:
            response.raise_for_status()
            response_data = await response.text()
            response_dict = xmltodict.parse(response_data)

            sync_status = parse_sync_status(response_dict)

            return sync_status

    async def shuffle(self, shuffle: bool) -> PlayQueue:
        """Set shuffle on current play queue.

        :param shuffle: Whether to shuffle the playlist.

        :return: The current play queue.
        """
        params = {
            "shuffle": "1" if shuffle else "0",
        }
        async with self._session.get(f"{self.base_url}/Shuffle", params=params) as response:
            response.raise_for_status()
            response_data = await response.text()
            response_dict = xmltodict.parse(response_data)

            play_queue = parse_play_queue(response_dict)

            return play_queue
