import aiohttp

from pyblu.entities import Status, Volume, SyncStatus, PairedPlayer, PlayQueue, Preset, Input
from pyblu.parse import parse_add_slave, parse_inputs, parse_sleep, parse_state, parse_sync_status, parse_status, parse_volume, parse_play_queue, parse_presets
from pyblu.errors import _wrap_in_unreachable_error


class Player:
    def __init__(self, host: str, port: int = 11000, session: aiohttp.ClientSession | None = None, default_timeout: float = 5.0):
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
    def default_timeout(self) -> float:
        return self._default_timeout

    async def close(self):
        if self._session_owned:
            await self._session.close()

    async def __aenter__(self):
        return self

    async def __aexit__(self, *args):
        await self.close()

    @_wrap_in_unreachable_error
    async def status(self, etag: str | None = None, poll_timeout: int = 30, timeout: float | None = None) -> Status:
        """Get the current status of the player.

        This endpoint supports long polling. If **etag** is set, the server will wait until the status changes or the timeout is reached.
        **etag** has to be the last etag received from the server.

        **poll_timeout** has to be smaller than **timeout**. The **default_timout** and the default value for **poll_timeout** do not fulfill this requirement.
        This means that **timeout** has to be set when using long polling in most cases.

        :param etag: The last etag received from the server. Triggers long polling if set.
        :param poll_timeout: The timeout in seconds for long polling. Has to be smaller than timeout.
        :param timeout: The timeout in seconds for the request. This overrides the default timeout. Has to be larger than poll_timeout.

        :raises PlayerUnexpectedResponseError: If the response is not as expected. This is probably a bug in the library.
        :raises PlayerUnreachableError: If the player is not reachable. Player is offline or request timed out.

        :return: The current status of the player. Only selected fields are returned.
        """
        used_timeout = timeout if timeout is not None else self._default_timeout

        params: dict[str, str] = {}
        if etag is not None:
            if poll_timeout >= used_timeout:
                raise ValueError("poll_timeout has to be smaller than timeout")
            params["etag"] = etag
            params["timeout"] = str(poll_timeout)

        async with self._session.get(f"{self.base_url}/Status", params=params, timeout=aiohttp.ClientTimeout(total=used_timeout)) as response:
            response.raise_for_status()
            response_data = await response.read()

            status = parse_status(response_data)

            return status

    @_wrap_in_unreachable_error
    async def sync_status(self, etag: str | None = None, poll_timeout: int = 30, timeout: float | None = None) -> SyncStatus:
        """Get the SyncStatus of the player.

        This endpoint supports long polling. If **etag** is set, the server will wait until the status changes or the timeout is reached.
        **etag** has to be the last etag received from the server.

        **poll_timeout** has to be smaller than **timeout**. The **default_timout** and the default value for **poll_timeout** do not fulfill this requirement.
        This means that **timeout** has to be set when using long polling in most cases.

        :param etag: The last etag received from the server. Triggers long polling if set.
        :param poll_timeout: The timeout in seconds for long polling. Has to be smaller than timeout.
        :param timeout: The timeout in seconds for the request. This overrides the default timeout. Has to be larger than poll_timeout.

        :raises PlayerUnexpectedResponseError: If the response is not as expected. This is probably a bug in the library.
        :raises PlayerUnreachableError: If the player is not reachable. Player is offline or request timed out.

        :return: The SyncStatus of the player.
        """
        used_timeout = timeout if timeout is not None else self._default_timeout

        params: dict[str, str] = {}
        if etag is not None:
            if poll_timeout >= used_timeout:
                raise ValueError("poll_timeout has to be smaller than timeout")
            params["etag"] = etag
            params["timeout"] = str(poll_timeout)

        async with self._session.get(f"{self.base_url}/SyncStatus", params=params) as response:
            response.raise_for_status()
            response_data = await response.read()

            sync_status = parse_sync_status(response_data)

            return sync_status

    @_wrap_in_unreachable_error
    async def volume(self, level: int | None = None, mute: bool | None = None, tell_slaves: bool | None = None, timeout: float | None = None) -> Volume:
        """Get or set the volume of the player.
        Call without parameters to get the current volume. Call with parameters to set the volume.

        :param level: The volume level to set. Range is 0-100.
        :param mute: Whether to mute the player.
        :param tell_slaves: Whether to tell grouped speakers to change their volume as well.
        :param timeout: The timeout in seconds for the request. This overrides the default timeout.

        :raises PlayerUnexpectedResponseError: If the response is not as expected. This is probably a bug in the library.
        :raises PlayerUnreachableError: If the player is not reachable. Player is offline or request timed out.

        :return: The current volume of the player.
        """
        used_timeout = timeout if timeout is not None else self._default_timeout

        params: dict[str, str] = {}
        if level is not None:
            params["level"] = str(level)
        if mute is not None:
            params["mute"] = "1" if mute else "0"
        if tell_slaves is not None:
            params["tell_slaves"] = "1" if tell_slaves else "0"

        async with self._session.get(f"{self.base_url}/Volume", params=params, timeout=aiohttp.ClientTimeout(total=used_timeout)) as response:
            response.raise_for_status()
            response_data = await response.read()

            volume = parse_volume(response_data)
            return volume

    @_wrap_in_unreachable_error
    async def play(self, seek: int | None = None, timeout: float | None = None) -> str:
        """Start playing the current track. Can also be used to seek within the current track.
        Works only when paused, not when stopped.

        :param seek: The position in seconds to seek to.
        :param timeout: The timeout in seconds for the request. This overrides the default timeout.

        :raises PlayerUnexpectedResponseError: If the response is not as expected. This is probably a bug in the library.
        :raises PlayerUnreachableError: If the player is not reachable. Player is offline or request timed out.

        :return: The playback state after command execution.
        """
        used_timeout = timeout if timeout is not None else self._default_timeout

        params = {}
        if seek is not None:
            params["seek"] = seek

        async with self._session.get(f"{self.base_url}/Play", params=params, timeout=aiohttp.ClientTimeout(total=used_timeout)) as response:
            response.raise_for_status()
            response_data = await response.read()

            return parse_state(response_data)

    @_wrap_in_unreachable_error
    async def play_url(self, url: str, timeout: float | None = None) -> str:
        """Start playing a track from a URL. Can also be used to select inputs. See *inputs* for available inputs.

        :param url: The URL of the track to play.
        :param timeout: The timeout in seconds for the request. This overrides the default timeout.

        :raises PlayerUnexpectedResponseError: If the response is not as expected. This is probably a bug in the library.
        :raises PlayerUnreachableError: If the player is not reachable. Player is offline or request timed out.

        :return: The playback state after command execution.
        """
        used_timeout = timeout if timeout is not None else self._default_timeout

        params = {
            "url": url,
        }
        async with self._session.get(f"{self.base_url}/Play", params=params, timeout=aiohttp.ClientTimeout(total=used_timeout)) as response:
            response.raise_for_status()
            response_data = await response.read()

            return parse_state(response_data)

    @_wrap_in_unreachable_error
    async def pause(self, toggle: bool | None = None, timeout: float | None = None) -> str:
        """Pause the current track. **toggle** can be used to toggle between playing and pause.

        :param toggle: Toggle between playing and pause.
        :param timeout: The timeout in seconds for the request. This overrides the default timeout.

        :raises PlayerUnexpectedResponseError: If the response is not as expected. This is probably a bug in the library.
        :raises PlayerUnreachableError: If the player is not reachable. Player is offline or request timed out.

        :return: The playback state after command execution.
        """
        used_timeout = timeout if timeout is not None else self._default_timeout

        params = {}
        if toggle is not None:
            params["toggle"] = "1"

        async with self._session.get(f"{self.base_url}/Pause", params=params, timeout=aiohttp.ClientTimeout(total=used_timeout)) as response:
            response.raise_for_status()
            response_data = await response.read()

            return parse_state(response_data)

    @_wrap_in_unreachable_error
    async def stop(self, timeout: float | None = None) -> str:
        """Stop the current track. Stopped playback cannot be resumed.

        :param timeout: The timeout in seconds for the request. This overrides the default timeout.

        :raises PlayerUnexpectedResponseError: If the response is not as expected. This is probably a bug in the library.
        :raises PlayerUnreachableError: If the player is not reachable. Player is offline or request timed out.

        :return: The playback state after command execution.
        """
        used_timeout = timeout if timeout is not None else self._default_timeout

        async with self._session.get(f"{self.base_url}/Stop", timeout=aiohttp.ClientTimeout(total=used_timeout)) as response:
            response.raise_for_status()
            response_data = await response.read()

            return parse_state(response_data)

    @_wrap_in_unreachable_error
    async def skip(self, timeout: float | None = None) -> None:
        """Skip to the next track.

        :param timeout: The timeout in seconds for the request. This overrides the default timeout.

        :raises PlayerUnexpectedResponseError: If the response is not as expected. This is probably a bug in the library.
        :raises PlayerUnreachableError: If the player is not reachable. Player is offline or request timed out.
        """
        used_timeout = timeout if timeout is not None else self._default_timeout
        async with self._session.get(f"{self.base_url}/Skip", timeout=aiohttp.ClientTimeout(total=used_timeout)) as response:
            response.raise_for_status()

    @_wrap_in_unreachable_error
    async def back(self, timeout: float | None = None) -> None:
        """Go back to the previous track.

        :param timeout: The timeout in seconds for the request. This overrides the default timeout.

        :raises PlayerUnexpectedResponseError: If the response is not as expected. This is probably a bug in the library.
        :raises PlayerUnreachableError: If the player is not reachable. Player is offline or request timed out.
        """
        used_timeout = timeout if timeout is not None else self._default_timeout

        async with self._session.get(f"{self.base_url}/Back", timeout=aiohttp.ClientTimeout(total=used_timeout)) as response:
            response.raise_for_status()

    @_wrap_in_unreachable_error
    async def add_slave(self, ip: str, port: int = 11000, timeout: float | None = None) -> list[PairedPlayer]:
        """Add a secondary player to the current player as a slave.
        If it fails the player won't be in the returned list.

        :param ip: The IP address of the player to add.
        :param port: The port of the player to add. Default is 11000.
        :param timeout: The timeout in seconds for the request. This overrides the default timeout.

        :raises PlayerUnexpectedResponseError: If the response is not as expected. This is probably a bug in the library.
        :raises PlayerUnreachableError: If the player is not reachable. Player is offline or request timed out.

        :return: The list of slaves of the player.
        """
        used_timeout = timeout if timeout is not None else self._default_timeout

        params: dict[str, str | int] = {
            "slave": ip,
            "port": port,
        }
        async with self._session.get(f"{self.base_url}/AddSlave", params=params, timeout=aiohttp.ClientTimeout(total=used_timeout)) as response:
            response.raise_for_status()
            response_data = await response.read()

            slaves_after_request = parse_add_slave(response_data)

            return slaves_after_request

    @_wrap_in_unreachable_error
    async def add_slaves(self, slaves: list[PairedPlayer], timeout: float | None = None) -> list[PairedPlayer]:
        """Add a list of secondary players to the current player as slaves.
        If it fails the player won't be in the returned list.

        Same as *add_slave* but with a list of players. Makes only one request to player.

        :param slaves: The list of players to add.
        :param timeout: The timeout in seconds for the request. This overrides the default timeout.

        :raises PlayerUnexpectedResponseError: If the response is not as expected. This is probably a bug in the library.
        :raises PlayerUnreachableError: If the player is not reachable. Player is offline or request timed out.

        :return: The list of slaves of the player.
        """
        used_timeout = timeout if timeout is not None else self._default_timeout

        params = {
            "slaves": ",".join(x.ip for x in slaves),
            "ports": ",".join(str(x.port) for x in slaves),
        }
        async with self._session.get(f"{self.base_url}/AddSlave", params=params, timeout=aiohttp.ClientTimeout(total=used_timeout)) as response:
            response.raise_for_status()
            response_data = await response.read()

            slaves_after_request = parse_add_slave(response_data)

            return slaves_after_request

    @_wrap_in_unreachable_error
    async def remove_slave(self, ip: str, port: int = 11000, timeout: float | None = None) -> SyncStatus:
        """Remove a secondary player from the group.

        :param ip: The IP address of the player to remove.
        :param port: The port of the player to remove. Default is 11000.
        :param timeout: The timeout in seconds for the request. This overrides the default timeout.

        :raises PlayerUnexpectedResponseError: If the response is not as expected. This is probably a bug in the library.
        :raises PlayerUnreachableError: If the player is not reachable. Player is offline or request timed out.

        :return: The SyncStatus of the player.
        """
        used_timeout = timeout if timeout is not None else self._default_timeout

        params: dict[str, str | int] = {
            "slave": ip,
            "port": port,
        }
        async with self._session.get(f"{self.base_url}/RemoveSlave", params=params, timeout=aiohttp.ClientTimeout(total=used_timeout)) as response:
            response.raise_for_status()
            response_data = await response.read()

            sync_status = parse_sync_status(response_data)

            return sync_status

    @_wrap_in_unreachable_error
    async def remove_slaves(self, slaves: list[PairedPlayer], timeout: float | None = None) -> SyncStatus:
        """Remove a list of secondary players from the group.

        Same as *remove_slave* but with a list of players. Makes only one request to player.

        :param slaves: The list of players to remove.
        :param timeout: The timeout in seconds for the request. This overrides the default timeout.

        :raises PlayerUnexpectedResponseError: If the response is not as expected. This is probably a bug in the library.
        :raises PlayerUnreachableError: If the player is not reachable. Player is offline or request timed out.

        :return: The SyncStatus of the player.
        """
        used_timeout = timeout if timeout is not None else self._default_timeout

        params = {
            "slaves": ",".join(x.ip for x in slaves),
            "ports": ",".join(str(x.port) for x in slaves),
        }
        async with self._session.get(f"{self.base_url}/RemoveSlave", params=params, timeout=aiohttp.ClientTimeout(total=used_timeout)) as response:
            response.raise_for_status()
            response_data = await response.read()

            sync_status = parse_sync_status(response_data)

            return sync_status

    @_wrap_in_unreachable_error
    async def shuffle(self, shuffle: bool, timeout: float | None = None) -> PlayQueue:
        """Set shuffle on current play queue.

        :param shuffle: Whether to shuffle the playlist.
        :param timeout: The timeout in seconds for the request. This overrides the default timeout.

        :raises PlayerUnexpectedResponseError: If the response is not as expected. This is probably a bug in the library.
        :raises PlayerUnreachableError: If the player is not reachable. Player is offline or request timed out.

        :return: The current play queue.
        """
        used_timeout = timeout if timeout is not None else self._default_timeout

        params = {
            "shuffle": "1" if shuffle else "0",
        }
        async with self._session.get(f"{self.base_url}/Shuffle", params=params, timeout=aiohttp.ClientTimeout(total=used_timeout)) as response:
            response.raise_for_status()
            response_data = await response.read()

            play_queue = parse_play_queue(response_data)

            return play_queue

    @_wrap_in_unreachable_error
    async def clear(self, timeout: float | None = None) -> PlayQueue:
        """Clear the play queue.

        :param timeout: The timeout in seconds for the request. This overrides the default timeout.

        :raises PlayerUnexpectedResponseError: If the response is not as expected. This is probably a bug in the library.
        :raises PlayerUnreachableError: If the player is not reachable. Player is offline or request timed out.

        :return: The current play queue.
        """
        used_timeout = timeout if timeout is not None else self._default_timeout

        async with self._session.get(f"{self.base_url}/Clear", timeout=aiohttp.ClientTimeout(total=used_timeout)) as response:
            response.raise_for_status()
            response_data = await response.read()

            play_queue = parse_play_queue(response_data)

            return play_queue

    @_wrap_in_unreachable_error
    async def sleep_timer(self, timeout: float | None = None) -> int:
        """Set sleep timer. Time steps are 15, 30, 45, 60, 90 minutes. Each call goes to next step.
        Resets to 0 if called when 90 minutes are set.

        :param timeout: The timeout in seconds for the request. This overrides the default timeout.

        :raises PlayerUnexpectedResponseError: If the response is not as expected. This is probably a bug in the library.
        :raises PlayerUnreachableError: If the player is not reachable. Player is offline or request timed out.

        :return: The current sleep timer in minutes. 0 if no sleep timer is set.
        """
        used_timeout = timeout if timeout is not None else self._default_timeout

        async with self._session.get(f"{self.base_url}/Sleep", timeout=aiohttp.ClientTimeout(total=used_timeout)) as response:
            response.raise_for_status()
            response_data = await response.read()

            return parse_sleep(response_data)

    @_wrap_in_unreachable_error
    async def presets(self, timeout: float | None = None) -> list[Preset]:
        """Get the list of presets of the player.

        :param timeout: The timeout in seconds for the request. This overrides the default timeout.

        :raises PlayerUnexpectedResponseError: If the response is not as expected. This is probably a bug in the library.
        :raises PlayerUnreachableError: If the player is not reachable. Player is offline or request timed out.

        :return: The list of presets of the player.
        """
        used_timeout = timeout if timeout is not None else self._default_timeout

        async with self._session.get(f"{self.base_url}/Presets", timeout=aiohttp.ClientTimeout(total=used_timeout)) as response:
            response.raise_for_status()
            response_data = await response.read()

            presets = parse_presets(response_data)

            return presets

    @_wrap_in_unreachable_error
    async def load_preset(self, preset_id: int, timeout: float | None = None) -> None:
        """Load a preset by ID.

        :param timeout: The timeout in seconds for the request. This overrides the default timeout.
        :param preset_id: The ID of the preset to load.

        :raises PlayerUnexpectedResponseError: If the response is not as expected. This is probably a bug in the library.
        :raises PlayerUnreachableError: If the player is not reachable. Player is offline or request timed out.
        """
        used_timeout = timeout if timeout is not None else self._default_timeout

        params = {
            "id": preset_id,
        }
        async with self._session.get(f"{self.base_url}/Preset", params=params, timeout=aiohttp.ClientTimeout(total=used_timeout)) as response:
            response.raise_for_status()

    @_wrap_in_unreachable_error
    async def inputs(self, timeout: float | None = None) -> list[Input]:
        """List all available inputs.

        :param timeout: The timeout in seconds for the request. This overrides the default timeout.

        :raises PlayerUnexpectedResponseError: If the response is not as expected. This is probably a bug in the library.
        :raises PlayerUnreachableError: If the player is not reachable. Player is offline or request timed out.

        :return: The list of inputs of the player.
        """
        used_timeout = timeout if timeout is not None else self._default_timeout

        params = {"service": "Capture"}
        async with self._session.get(f"{self.base_url}/RadioBrowse", params=params, timeout=aiohttp.ClientTimeout(total=used_timeout)) as response:
            response.raise_for_status()
            response_data = await response.read()

            return parse_inputs(response_data)
