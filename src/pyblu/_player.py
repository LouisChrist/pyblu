from urllib.parse import unquote

import aiohttp
import xmltodict

from pyblu._entities import Status, Volume, SyncStatus, PairedPlayer, PlayQueue, Preset, Input
from pyblu._parse import parse_slave_list, parse_sync_status, parse_status, parse_volume, chained_get, parse_play_queue, parse_presets


class Player:
    def __init__(self, host: str, port: int = 11000, session: aiohttp.ClientSession = None, default_timeout: int = 5):
        """Client for a BluOS player. Uses the HTTP API of the BluOS players to control it.

        The passed sessions will not be closed when the player is closed and has to be closed by the caller.
        If no session is passed, a new session will be created and closed when the player is closed.

        *Player* is an async context manager and can be used with *async with*.

        :param host: The hostname or IP address of the player.
        :param port: The port of the player. Default is 11000.
        :param session: An optional aiohttp.ClientSession to use for requests.
        :param default_timeout: The default timeout in seconds for requests. Can be overridden in each request.

        :return: A new Player.
        """
        self.base_url = f"http://{host}:{port}"
        self._default_timeout = default_timeout
        if session:
            self._session_owned = False
            self._session = session
        else:
            self._session_owned = True
            self._session = aiohttp.ClientSession()

    @property
    def default_timeout(self) -> int:
        return self._default_timeout

    async def close(self):
        if self._session_owned:
            await self._session.close()

    async def __aenter__(self):
        return self

    async def __aexit__(self, *args):
        await self.close()

    async def status(self, etag: str | None = None, poll_timeout: int = 30, timeout: int | None = None) -> Status:
        """Get the current status of the player.

        This endpoint supports long polling. If **etag** is set, the server will wait until the status changes or the timeout is reached.
        **etag** has to be the last etag received from the server.

        **poll_timeout** has to be smaller than **timeout**. The **default_timout** and the default value for **poll_timeout** do not fulfill this requirement.
        This means that **timeout** has to be set when using long polling in most cases.

        :param etag: The last etag received from the server. Triggers long polling if set.
        :param poll_timeout: The timeout in seconds for long polling. Has to be smaller than timeout.
        :param timeout: The timeout in seconds for the request. This overrides the default timeout. Has to be larger than poll_timeout.

        :return: The current status of the player. Only selected fields are returned.
        """
        timeout = timeout if timeout is not None else self.default_timeout

        params = {}
        if etag is not None:
            if poll_timeout >= timeout:
                raise ValueError("poll_timeout has to be smaller than timeout")
            params["etag"] = etag
            params["timeout"] = poll_timeout

        async with self._session.get(f"{self.base_url}/Status", params=params, timeout=timeout) as response:
            response.raise_for_status()
            response_data = await response.text()
            response_dict = xmltodict.parse(response_data)

            status = parse_status(response_dict)

            return status

    async def sync_status(self, etag: str | None = None, poll_timeout: int = 30, timeout: int | None = None) -> SyncStatus:
        """Get the SyncStatus of the player.

        This endpoint supports long polling. If **etag** is set, the server will wait until the status changes or the timeout is reached.
        **etag** has to be the last etag received from the server.

        **poll_timeout** has to be smaller than **timeout**. The **default_timout** and the default value for **poll_timeout** do not fulfill this requirement.
        This means that **timeout** has to be set when using long polling in most cases.

        :param etag: The last etag received from the server. Triggers long polling if set.
        :param poll_timeout: The timeout in seconds for long polling. Has to be smaller than timeout.
        :param timeout: The timeout in seconds for the request. This overrides the default timeout. Has to be larger than poll_timeout.

        :return: The SyncStatus of the player.
        """
        timeout = timeout if timeout is not None else self.default_timeout

        params = {}
        if etag is not None:
            if poll_timeout >= timeout:
                raise ValueError("poll_timeout has to be smaller than timeout")
            params["etag"] = etag
            params["timeout"] = poll_timeout

        async with self._session.get(f"{self.base_url}/SyncStatus", params=params) as response:
            response.raise_for_status()
            response_data = await response.text()
            response_dict = xmltodict.parse(response_data)

            sync_status = parse_sync_status(response_dict)

            return sync_status

    async def volume(self, level: int = None, mute: bool = None, tell_slaves: bool = None, timeout: int | None = None) -> Volume:
        """Get or set the volume of the player.
        Call without parameters to get the current volume. Call with parameters to set the volume.

        :param level: The volume level to set. Range is 0-100.
        :param mute: Whether to mute the player.
        :param tell_slaves: Whether to tell grouped speakers to change their volume as well.
        :param timeout: The timeout in seconds for the request. This overrides the default timeout.

        :return: The current volume of the player.
        """
        timeout = timeout if timeout is not None else self.default_timeout

        params = {}
        if level is not None:
            params["level"] = level
        if mute is not None:
            params["mute"] = "1" if mute else "0"
        if tell_slaves is not None:
            params["tell_slaves"] = "1" if tell_slaves else "0"

        async with self._session.get(f"{self.base_url}/Volume", params=params, timeout=timeout) as response:
            response.raise_for_status()
            response_data = await response.text()
            response_dict = xmltodict.parse(response_data)

            volume = parse_volume(response_dict)

            return volume

    async def play(self, seek: int = None, timeout: int | None = None) -> str:
        """Start playing the current track. Can also be used to seek within the current track.
        Works only when paused, not when stopped.

        :param seek: The position in seconds to seek to.
        :param timeout: The timeout in seconds for the request. This overrides the default timeout.

        :return: The playback state after command execution.
        """
        timeout = timeout if timeout is not None else self.default_timeout

        params = {}
        if seek is not None:
            params["seek"] = seek

        async with self._session.get(f"{self.base_url}/Play", params=params, timeout=timeout) as response:
            response.raise_for_status()
            response_data = await response.text()
            response_dict = xmltodict.parse(response_data)

            return chained_get(response_dict, "state")

    async def play_url(self, url: str, timeout: int | None = None) -> str:
        """Start playing a track from a URL. Can also be used to select inputs. See *inputs* for available inputs.

        :param url: The URL of the track to play.
        :param timeout: The timeout in seconds for the request. This overrides the default timeout.

        :return: The playback state after command execution.
        """
        timeout = timeout if timeout is not None else self.default_timeout

        params = {
            "url": url,
        }
        async with self._session.get(f"{self.base_url}/Play", params=params, timeout=timeout) as response:
            response.raise_for_status()
            response_data = await response.text()
            response_dict = xmltodict.parse(response_data)

            return chained_get(response_dict, "state")

    async def pause(self, toggle: bool = None, timeout: int | None = None) -> str:
        """Pause the current track. **toggle** can be used to toggle between playing and pause.

        :param toggle: Toggle between playing and pause.
        :param timeout: The timeout in seconds for the request. This overrides the default timeout.

        :return: The playback state after command execution.
        """
        timeout = timeout if timeout is not None else self.default_timeout

        params = {}
        if toggle is not None:
            params["toggle"] = "1"

        async with self._session.get(f"{self.base_url}/Pause", params=params, timeout=timeout) as response:
            response.raise_for_status()
            response_data = await response.text()
            response_dict = xmltodict.parse(response_data)

            return chained_get(response_dict, "state")

    async def stop(self, timeout: int | None = None) -> str:
        """Stop the current track. Stopped playback cannot be resumed.

        :param timeout: The timeout in seconds for the request. This overrides the default timeout.

        :return: The playback state after command execution.
        """
        timeout = timeout if timeout is not None else self.default_timeout

        async with self._session.get(f"{self.base_url}/Stop", timeout=timeout) as response:
            response.raise_for_status()
            response_data = await response.text()
            response_dict = xmltodict.parse(response_data)

            return chained_get(response_dict, "state")

    async def skip(self, timeout: int | None = None) -> None:
        """Skip to the next track.

        :param timeout: The timeout in seconds for the request. This overrides the default timeout.
        """
        timeout = timeout if timeout is not None else self.default_timeout
        async with self._session.get(f"{self.base_url}/Skip", timeout=timeout) as response:
            response.raise_for_status()

    async def back(self, timeout: int | None = None) -> None:
        """Go back to the previous track.

        :param timeout: The timeout in seconds for the request. This overrides the default timeout.
        """
        timeout = timeout if timeout is not None else self.default_timeout

        async with self._session.get(f"{self.base_url}/Back", timeout=timeout) as response:
            response.raise_for_status()

    async def add_slave(self, ip: str, port: int = 11000, timeout: int | None = None) -> list[PairedPlayer]:
        """Add a secondary player to the current player as a slave.
        If it fails the player won't be in the returned list.

        :param ip: The IP address of the player to add.
        :param port: The port of the player to add. Default is 11000.
        :param timeout: The timeout in seconds for the request. This overrides the default timeout.

        :return: The list of slaves of the player.
        """
        timeout = timeout if timeout is not None else self.default_timeout

        params = {
            "slave": ip,
            "port": port,
        }
        async with self._session.get(f"{self.base_url}/AddSlave", params=params, timeout=timeout) as response:
            response.raise_for_status()
            response_data = await response.text()
            response_dict = xmltodict.parse(response_data)

            slaves_raw = chained_get(response_dict, "addSlave", "slave")
            slaves = parse_slave_list(slaves_raw)

            return slaves

    async def add_slaves(self, slaves: list[PairedPlayer], timeout: int | None = None) -> list[PairedPlayer]:
        """Add a list of secondary players to the current player as slaves.
        If it fails the player won't be in the returned list.

        Same as *add_slave* but with a list of players. Makes only one request to player.

        :param slaves: The list of players to add.
        :param timeout: The timeout in seconds for the request. This overrides the default timeout.

        :return: The list of slaves of the player.
        """
        timeout = timeout if timeout is not None else self.default_timeout

        params = {
            "slaves": ",".join(x.ip for x in slaves),
            "ports": ",".join(str(x.port) for x in slaves),
        }
        async with self._session.get(f"{self.base_url}/AddSlave", params=params, timeout=timeout) as response:
            response.raise_for_status()
            response_data = await response.text()
            response_dict = xmltodict.parse(response_data)

            slaves_raw = chained_get(response_dict, "addSlave", "slave")
            slaves = parse_slave_list(slaves_raw)

            return slaves

    async def remove_slave(self, ip: str, port: int = 11000, timeout: int | None = None) -> SyncStatus:
        """Remove a secondary player from the group.

        :param ip: The IP address of the player to remove.
        :param port: The port of the player to remove. Default is 11000.
        :param timeout: The timeout in seconds for the request. This overrides the default timeout.

        :return: The SyncStatus of the player.
        """
        timeout = timeout if timeout is not None else self.default_timeout

        params = {
            "slave": ip,
            "port": port,
        }
        async with self._session.get(f"{self.base_url}/RemoveSlave", params=params, timeout=timeout) as response:
            response.raise_for_status()
            response_data = await response.text()
            response_dict = xmltodict.parse(response_data)

            sync_status = parse_sync_status(response_dict)

            return sync_status

    async def remove_slaves(self, slaves: list[PairedPlayer], timeout: int | None = None) -> SyncStatus:
        """Remove a list of secondary players from the group.

        Same as *remove_slave* but with a list of players. Makes only one request to player.

        :param slaves: The list of players to remove.
        :param timeout: The timeout in seconds for the request. This overrides the default timeout.

        :return: The SyncStatus of the player.
        """
        timeout = timeout if timeout is not None else self.default_timeout

        params = {
            "slaves": ",".join(x.ip for x in slaves),
            "ports": ",".join(str(x.port) for x in slaves),
        }
        async with self._session.get(f"{self.base_url}/RemoveSlave", params=params, timeout=timeout) as response:
            response.raise_for_status()
            response_data = await response.text()
            response_dict = xmltodict.parse(response_data)

            sync_status = parse_sync_status(response_dict)

            return sync_status

    async def shuffle(self, shuffle: bool, timeout: int | None = None) -> PlayQueue:
        """Set shuffle on current play queue.

        :param shuffle: Whether to shuffle the playlist.
        :param timeout: The timeout in seconds for the request. This overrides the default timeout.

        :return: The current play queue.
        """
        timeout = timeout if timeout is not None else self.default_timeout

        params = {
            "shuffle": "1" if shuffle else "0",
        }
        async with self._session.get(f"{self.base_url}/Shuffle", params=params, timeout=timeout) as response:
            response.raise_for_status()
            response_data = await response.text()
            response_dict = xmltodict.parse(response_data)

            play_queue = parse_play_queue(response_dict)

            return play_queue

    async def clear(self, timeout: int | None = None) -> PlayQueue:
        """Clear the play queue.

        :param timeout: The timeout in seconds for the request. This overrides the default timeout.

        :return: The current play queue.
        """
        timeout = timeout if timeout is not None else self.default_timeout

        async with self._session.get(f"{self.base_url}/Clear", timeout=timeout) as response:
            response.raise_for_status()
            response_data = await response.text()
            response_dict = xmltodict.parse(response_data)

            play_queue = parse_play_queue(response_dict)

            return play_queue

    async def sleep_timer(self, timeout: int | None = None) -> int:
        """Set sleep timer. Time steps are 15, 30, 45, 60, 90 minutes. Each call goes to next step.
        Resets to 0 if called when 90 minutes are set.

        :param timeout: The timeout in seconds for the request. This overrides the default timeout.

        :return: The current sleep timer in minutes. 0 if no sleep timer is set.
        """
        timeout = timeout if timeout is not None else self.default_timeout

        async with self._session.get(f"{self.base_url}/Sleep", timeout=timeout) as response:
            response.raise_for_status()
            response_data = await response.text()
            response_dict = xmltodict.parse(response_data)

            sleep_timer = chained_get(response_dict, "sleep", _map=int)
            if not sleep_timer:
                sleep_timer = 0

            return sleep_timer

    async def presets(self, timeout: int | None = None) -> list[Preset]:
        """Get the list of presets of the player.

        :param timeout: The timeout in seconds for the request. This overrides the default timeout.

        :return: The list of presets of the player.
        """
        timeout = timeout if timeout is not None else self.default_timeout

        async with self._session.get(f"{self.base_url}/Presets", timeout=timeout) as response:
            response.raise_for_status()
            response_data = await response.text()
            response_dict = xmltodict.parse(response_data)

            presets = parse_presets(response_dict)

            return presets

    async def load_preset(self, preset_id: int, timeout: int | None = None) -> None:
        """Load a preset by ID.

        :param timeout: The timeout in seconds for the request. This overrides the default timeout.

        :param preset_id: The ID of the preset to load.
        """
        timeout = timeout if timeout is not None else self.default_timeout

        params = {
            "id": preset_id,
        }
        async with self._session.get(f"{self.base_url}/Preset", params=params, timeout=timeout) as response:
            response.raise_for_status()

    async def inputs(self, timeout: int | None = None) -> list[Input]:
        """List all available inputs.

        :param timeout: The timeout in seconds for the request. This overrides the default timeout.

        :return: The list of inputss of the player.
        """
        timeout = timeout if timeout is not None else self.default_timeout

        params = {"service": "Capture"}
        async with self._session.get(f"{self.base_url}/RadioBrowse", params=params, timeout=timeout) as response:
            response.raise_for_status()
            response_data = await response.text()
            response_dict = xmltodict.parse(response_data)

            inputs_raw = chained_get(response_dict, "radiotime", "item")

            if not isinstance(inputs_raw, list):
                inputs_raw = [inputs_raw]

            inputs = [
                Input(
                    id=chained_get(x, "@id"),
                    text=chained_get(x, "@text"),
                    image=chained_get(x, "@image"),
                    url=chained_get(x, "@URL", _map=unquote),
                )
                for x in inputs_raw
            ]

            return inputs
