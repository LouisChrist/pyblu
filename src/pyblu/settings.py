from math import isfinite
from typing import Protocol

from pyblu.entities import _AudioSetting, ListeningModeValue, SettingRange, SettingValue, SubwooferModeValue
from pyblu.errors import PlayerUnexpectedResponseError
from pyblu.parse import parse_audio_setting, parse_listening_modes, parse_subwoofer_modes

type QueryParams = dict[str, str | int]


class _HttpGet(Protocol):  # pylint: disable=too-few-public-methods
    async def __call__(
        self,
        path: str,
        params: QueryParams | None = None,
        timeout: float | None = None,
    ) -> bytes: ...


class ListeningMode:
    """Listening mode; accessed through ``player.settings.listening_mode``.

    See :class:`Settings` for request and availability semantics.
    """

    def __init__(self, get: _HttpGet):
        self._get = get

    async def _query_endpoint(self, timeout: float | None = None) -> list[ListeningModeValue]:
        data = await self._get("/Settings?id=audio", timeout=timeout)
        return parse_listening_modes(data)

    async def get(self, timeout: float | None = None) -> str | None:
        """Return the active display name, or None if absent or no choice matches."""
        for val in await self._query_endpoint(timeout):
            if val.active:
                return val.display_name
        return None

    async def set(self, mode: str, timeout: float | None = None) -> None:
        """Set a raw choice name, not the display name returned by get().

        Choices are not checked locally.
        """
        await self._get("/alsa_setting", params={"preset": mode}, timeout=timeout)

    async def is_available(self, timeout: float | None = None) -> bool:
        """Return whether the player advertises this setting."""
        return len(await self._query_endpoint(timeout)) > 0

    async def values(self, timeout: float | None = None) -> list[ListeningModeValue]:
        """Return choices with raw names for set(), or an empty list if absent."""
        return await self._query_endpoint(timeout)


class SubwooferMode:
    """Subwoofer mode; accessed through ``player.settings.subwoofer_mode``.

    See :class:`Settings` for request and availability semantics.
    """

    def __init__(self, get: _HttpGet):
        self._get = get

    async def _query_endpoint(self, timeout: float | None = None) -> list[SubwooferModeValue]:
        data = await self._get("/Settings?id=audio", timeout=timeout)
        return parse_subwoofer_modes(data)

    async def get(self, timeout: float | None = None) -> str | None:
        """Return the active display name, or None if absent or no choice matches."""
        for val in await self._query_endpoint(timeout):
            if val.active:
                return val.display_name
        return None

    async def set(self, mode: str, timeout: float | None = None) -> None:
        """Set a raw choice name, not the display name returned by get().

        Choices are not checked locally.
        """
        await self._get("/audiomodes", params={"subwoofer": mode}, timeout=timeout)

    async def is_available(self, timeout: float | None = None) -> bool:
        """Return whether the player advertises this setting."""
        return len(await self._query_endpoint(timeout)) > 0

    async def values(self, timeout: float | None = None) -> list[SubwooferModeValue]:
        """Return choices with raw names for set(), or an empty list if absent."""
        return await self._query_endpoint(timeout)


class ToneControls:
    """Tone controls; accessed through ``player.settings.tone_controls``.

    See :class:`Settings` for request and availability semantics.
    """

    def __init__(self, get: _HttpGet):
        self._get = get

    async def _query_endpoint(self, timeout: float | None = None) -> _AudioSetting | None:
        data = await self._get("/Settings?id=audio", timeout=timeout)
        return parse_audio_setting(data, "eq-switch", "boolean")

    async def get(self, timeout: float | None = None) -> bool | None:
        """Return whether enabled, or None if absent from the player."""
        setting = await self._query_endpoint(timeout)
        if setting is None:
            return None
        if not isinstance(setting.value, bool):
            raise PlayerUnexpectedResponseError("Expected boolean setting value")
        return setting.value

    async def set(self, enabled: bool, timeout: float | None = None) -> None:
        """Enable or disable this setting.

        :raises ValueError: If enabled is not a bool.
        """
        if not isinstance(enabled, bool):
            raise ValueError("enabled must be a bool")
        await self._get("/alsa_setting", params={"eq-switch": "ON" if enabled else "OFF"}, timeout=timeout)

    async def is_available(self, timeout: float | None = None) -> bool:
        """Return whether the player advertises this setting."""
        return await self._query_endpoint(timeout) is not None


class Treble:
    """Treble level in dB; accessed through ``player.settings.treble``.

    See :class:`Settings` for request and availability semantics.
    """

    def __init__(self, get: _HttpGet):
        self._get = get

    async def _query_endpoint(self, timeout: float | None = None) -> _AudioSetting | None:
        data = await self._get("/Settings?id=audio", timeout=timeout)
        return parse_audio_setting(data, "eq-treble", "range")

    async def get(self, timeout: float | None = None) -> float | None:
        """Return the current numeric value, or None if absent from the player."""
        setting = await self._query_endpoint(timeout)
        if setting is None:
            return None
        if not isinstance(setting.value, float):
            raise PlayerUnexpectedResponseError("Expected range setting value")
        return setting.value

    async def set(self, value: float, timeout: float | None = None) -> None:
        """Set a finite numeric value.

        Player-advertised bounds and step sizes are not checked locally.

        :raises ValueError: If value is a bool or is not finite.
        """
        if isinstance(value, bool) or not isfinite(value):
            raise ValueError("value must be a finite number")
        await self._get("/alsa_setting", params={"eq-treble": f"{value:g}"}, timeout=timeout)

    async def is_available(self, timeout: float | None = None) -> bool:
        """Return whether the player advertises this setting."""
        return await self._query_endpoint(timeout) is not None

    async def values(self, timeout: float | None = None) -> SettingRange | None:
        """Return advertised bounds, or None if absent; these are not enforced by set()."""
        setting = await self._query_endpoint(timeout)
        return setting.range if setting else None


class Bass:
    """Bass level in dB; accessed through ``player.settings.bass``.

    See :class:`Settings` for request and availability semantics.
    """

    def __init__(self, get: _HttpGet):
        self._get = get

    async def _query_endpoint(self, timeout: float | None = None) -> _AudioSetting | None:
        data = await self._get("/Settings?id=audio", timeout=timeout)
        return parse_audio_setting(data, "eq-bass", "range")

    async def get(self, timeout: float | None = None) -> float | None:
        """Return the current numeric value, or None if absent from the player."""
        setting = await self._query_endpoint(timeout)
        if setting is None:
            return None
        if not isinstance(setting.value, float):
            raise PlayerUnexpectedResponseError("Expected range setting value")
        return setting.value

    async def set(self, value: float, timeout: float | None = None) -> None:
        """Set a finite numeric value.

        Player-advertised bounds and step sizes are not checked locally.

        :raises ValueError: If value is a bool or is not finite.
        """
        if isinstance(value, bool) or not isfinite(value):
            raise ValueError("value must be a finite number")
        await self._get("/alsa_setting", params={"eq-bass": f"{value:g}"}, timeout=timeout)

    async def is_available(self, timeout: float | None = None) -> bool:
        """Return whether the player advertises this setting."""
        return await self._query_endpoint(timeout) is not None

    async def values(self, timeout: float | None = None) -> SettingRange | None:
        """Return advertised bounds, or None if absent; these are not enforced by set()."""
        setting = await self._query_endpoint(timeout)
        return setting.range if setting else None


class Balance:
    """Left/right balance; accessed through ``player.settings.balance``.

    See :class:`Settings` for request and availability semantics.
    """

    def __init__(self, get: _HttpGet):
        self._get = get

    async def _query_endpoint(self, timeout: float | None = None) -> _AudioSetting | None:
        data = await self._get("/Settings?id=audio", timeout=timeout)
        return parse_audio_setting(data, "eq-balance", "range")

    async def get(self, timeout: float | None = None) -> float | None:
        """Return the current numeric value, or None if absent from the player."""
        setting = await self._query_endpoint(timeout)
        if setting is None:
            return None
        if not isinstance(setting.value, float):
            raise PlayerUnexpectedResponseError("Expected range setting value")
        return setting.value

    async def set(self, value: float, timeout: float | None = None) -> None:
        """Set a finite numeric value.

        Player-advertised bounds and step sizes are not checked locally.

        :raises ValueError: If value is a bool or is not finite.
        """
        if isinstance(value, bool) or not isfinite(value):
            raise ValueError("value must be a finite number")
        await self._get("/alsa_setting", params={"eq-balance": f"{value:g}"}, timeout=timeout)

    async def is_available(self, timeout: float | None = None) -> bool:
        """Return whether the player advertises this setting."""
        return await self._query_endpoint(timeout) is not None

    async def values(self, timeout: float | None = None) -> SettingRange | None:
        """Return advertised bounds, or None if absent; these are not enforced by set()."""
        setting = await self._query_endpoint(timeout)
        return setting.range if setting else None


class CentreChannel:
    """Centre channel; accessed through ``player.settings.centre_channel``.

    See :class:`Settings` for request and availability semantics.
    """

    def __init__(self, get: _HttpGet):
        self._get = get

    async def _query_endpoint(self, timeout: float | None = None) -> _AudioSetting | None:
        data = await self._get("/Settings?id=audio", timeout=timeout)
        return parse_audio_setting(data, "centre", "boolean")

    async def get(self, timeout: float | None = None) -> bool | None:
        """Return whether enabled, or None if absent from the player."""
        setting = await self._query_endpoint(timeout)
        if setting is None:
            return None
        if not isinstance(setting.value, bool):
            raise PlayerUnexpectedResponseError("Expected boolean setting value")
        return setting.value

    async def set(self, enabled: bool, timeout: float | None = None) -> None:
        """Enable or disable this setting.

        :raises ValueError: If enabled is not a bool.
        """
        if not isinstance(enabled, bool):
            raise ValueError("enabled must be a bool")
        await self._get("/setting", params={"centre": "ON" if enabled else "OFF"}, timeout=timeout)

    async def is_available(self, timeout: float | None = None) -> bool:
        """Return whether the player advertises this setting."""
        return await self._query_endpoint(timeout) is not None


class CentreVolumeTrim:
    """Centre-channel volume trim; accessed through ``player.settings.centre_volume_trim``.

    See :class:`Settings` for request and availability semantics.
    """

    def __init__(self, get: _HttpGet):
        self._get = get

    async def _query_endpoint(self, timeout: float | None = None) -> _AudioSetting | None:
        data = await self._get("/Settings?id=audio", timeout=timeout)
        return parse_audio_setting(data, "eq-centre-trim", "range")

    async def get(self, timeout: float | None = None) -> float | None:
        """Return the current numeric value, or None if absent from the player."""
        setting = await self._query_endpoint(timeout)
        if setting is None:
            return None
        if not isinstance(setting.value, float):
            raise PlayerUnexpectedResponseError("Expected range setting value")
        return setting.value

    async def set(self, value: float, timeout: float | None = None) -> None:
        """Set a finite numeric value.

        Player-advertised bounds and step sizes are not checked locally.

        :raises ValueError: If value is a bool or is not finite.
        """
        if isinstance(value, bool) or not isfinite(value):
            raise ValueError("value must be a finite number")
        await self._get("/alsa_setting", params={"eq-centre-trim": f"{value:g}"}, timeout=timeout)

    async def is_available(self, timeout: float | None = None) -> bool:
        """Return whether the player advertises this setting."""
        return await self._query_endpoint(timeout) is not None

    async def values(self, timeout: float | None = None) -> SettingRange | None:
        """Return advertised bounds, or None if absent; these are not enforced by set()."""
        setting = await self._query_endpoint(timeout)
        return setting.range if setting else None


class Crossover:
    """Subwoofer crossover frequency in Hz; accessed through ``player.settings.crossover``.

    See :class:`Settings` for request and availability semantics.
    """

    def __init__(self, get: _HttpGet):
        self._get = get

    async def _query_endpoint(self, timeout: float | None = None) -> _AudioSetting | None:
        data = await self._get("/Settings?id=audio", timeout=timeout)
        return parse_audio_setting(data, "eq-crossover", "range")

    async def get(self, timeout: float | None = None) -> float | None:
        """Return the current numeric value, or None if absent from the player."""
        setting = await self._query_endpoint(timeout)
        if setting is None:
            return None
        if not isinstance(setting.value, float):
            raise PlayerUnexpectedResponseError("Expected range setting value")
        return setting.value

    async def set(self, value: float, timeout: float | None = None) -> None:
        """Set a finite numeric value.

        Player-advertised bounds and step sizes are not checked locally.

        :raises ValueError: If value is a bool or is not finite.
        """
        if isinstance(value, bool) or not isfinite(value):
            raise ValueError("value must be a finite number")
        await self._get("/alsa_setting", params={"eq-crossover": f"{value:g}"}, timeout=timeout)

    async def is_available(self, timeout: float | None = None) -> bool:
        """Return whether the player advertises this setting."""
        return await self._query_endpoint(timeout) is not None

    async def values(self, timeout: float | None = None) -> SettingRange | None:
        """Return advertised bounds, or None if absent; these are not enforced by set()."""
        setting = await self._query_endpoint(timeout)
        return setting.range if setting else None


class ReplayGain:
    """Replay-gain mode; accessed through ``player.settings.replay_gain``.

    See :class:`Settings` for request and availability semantics.
    """

    def __init__(self, get: _HttpGet):
        self._get = get

    async def _query_endpoint(self, timeout: float | None = None) -> _AudioSetting | None:
        data = await self._get("/Settings?id=audio", timeout=timeout)
        return parse_audio_setting(data, "replayGainMode", "list")

    async def get(self, timeout: float | None = None) -> str | None:
        """Return the active display name, or None if absent or no choice matches."""
        for val in await self.values(timeout):
            if val.active:
                return val.display_name
        return None

    async def set(self, mode: str, timeout: float | None = None) -> None:
        """Set a raw choice name, not the display name returned by get().

        Choices are not checked locally.
        """
        await self._get("/audiomodes", params={"replayGainMode": mode}, timeout=timeout)

    async def is_available(self, timeout: float | None = None) -> bool:
        """Return whether the player advertises this setting."""
        return await self._query_endpoint(timeout) is not None

    async def values(self, timeout: float | None = None) -> list[SettingValue]:
        """Return choices with raw names for set(), or an empty list if absent."""
        setting = await self._query_endpoint(timeout)
        return setting.values if setting else []


class OutputMode:
    """Output channel mode; accessed through ``player.settings.output_mode``.

    See :class:`Settings` for request and availability semantics.
    """

    def __init__(self, get: _HttpGet):
        self._get = get

    async def _query_endpoint(self, timeout: float | None = None) -> _AudioSetting | None:
        data = await self._get("/Settings?id=audio", timeout=timeout)
        return parse_audio_setting(data, "channelMode", "list")

    async def get(self, timeout: float | None = None) -> str | None:
        """Return the active display name, or None if absent or no choice matches."""
        for val in await self.values(timeout):
            if val.active:
                return val.display_name
        return None

    async def set(self, mode: str, timeout: float | None = None) -> None:
        """Set a raw choice name, not the display name returned by get().

        Choices are not checked locally.
        """
        await self._get("/audiomodes", params={"channelMode": mode}, timeout=timeout)

    async def is_available(self, timeout: float | None = None) -> bool:
        """Return whether the player advertises this setting."""
        return await self._query_endpoint(timeout) is not None

    async def values(self, timeout: float | None = None) -> list[SettingValue]:
        """Return choices with raw names for set(), or an empty list if absent."""
        setting = await self._query_endpoint(timeout)
        return setting.values if setting else []


class StereoSurround:
    """Stereo surround; accessed through ``player.settings.stereo_surround``.

    See :class:`Settings` for request and availability semantics.
    """

    def __init__(self, get: _HttpGet):
        self._get = get

    async def _query_endpoint(self, timeout: float | None = None) -> _AudioSetting | None:
        data = await self._get("/Settings?id=audio", timeout=timeout)
        return parse_audio_setting(data, "ears", "boolean")

    async def get(self, timeout: float | None = None) -> bool | None:
        """Return whether enabled, or None if absent from the player."""
        setting = await self._query_endpoint(timeout)
        if setting is None:
            return None
        if not isinstance(setting.value, bool):
            raise PlayerUnexpectedResponseError("Expected boolean setting value")
        return setting.value

    async def set(self, enabled: bool, timeout: float | None = None) -> None:
        """Enable or disable this setting.

        :raises ValueError: If enabled is not a bool.
        """
        if not isinstance(enabled, bool):
            raise ValueError("enabled must be a bool")
        await self._get("/audiomodes", params={"ears": "ON" if enabled else "OFF"}, timeout=timeout)

    async def is_available(self, timeout: float | None = None) -> bool:
        """Return whether the player advertises this setting."""
        return await self._query_endpoint(timeout) is not None


class DigitalPassthrough:
    """Digital passthrough; accessed through ``player.settings.digital_passthrough``.

    See :class:`Settings` for request and availability semantics.
    """

    def __init__(self, get: _HttpGet):
        self._get = get

    async def _query_endpoint(self, timeout: float | None = None) -> _AudioSetting | None:
        data = await self._get("/Settings?id=audio", timeout=timeout)
        return parse_audio_setting(data, "mqaDisable", "boolean")

    async def get(self, timeout: float | None = None) -> bool | None:
        """Return whether enabled, or None if absent from the player."""
        setting = await self._query_endpoint(timeout)
        if setting is None:
            return None
        if not isinstance(setting.value, bool):
            raise PlayerUnexpectedResponseError("Expected boolean setting value")
        return setting.value

    async def set(self, enabled: bool, timeout: float | None = None) -> None:
        """Enable or disable this setting.

        :raises ValueError: If enabled is not a bool.
        """
        if not isinstance(enabled, bool):
            raise ValueError("enabled must be a bool")
        await self._get("/audiomodes", params={"mqaDisable": "ON" if enabled else "OFF"}, timeout=timeout)

    async def is_available(self, timeout: float | None = None) -> bool:
        """Return whether the player advertises this setting."""
        return await self._query_endpoint(timeout) is not None


class FixedVolume:
    """Fixed output level; accessed through ``player.settings.fixed_volume``.

    See :class:`Settings` for request and availability semantics.
    """

    def __init__(self, get: _HttpGet):
        self._get = get

    async def _query_endpoint(self, timeout: float | None = None) -> _AudioSetting | None:
        data = await self._get("/Settings?id=audio", timeout=timeout)
        return parse_audio_setting(data, "fixedVolume", "boolean")

    async def get(self, timeout: float | None = None) -> bool | None:
        """Return whether enabled, or None if absent from the player."""
        setting = await self._query_endpoint(timeout)
        if setting is None:
            return None
        if not isinstance(setting.value, bool):
            raise PlayerUnexpectedResponseError("Expected boolean setting value")
        return setting.value

    async def set(self, enabled: bool, timeout: float | None = None) -> None:
        """Enable or disable this setting.

        :raises ValueError: If enabled is not a bool.
        """
        if not isinstance(enabled, bool):
            raise ValueError("enabled must be a bool")
        # No setting URL: use the parent menuGroup URL.
        await self._get("/audiomodes", params={"fixedVolume": "ON" if enabled else "OFF"}, timeout=timeout)

    async def is_available(self, timeout: float | None = None) -> bool:
        """Return whether the player advertises this setting."""
        return await self._query_endpoint(timeout) is not None


class VolumeLimits:
    """Volume limits in dB; accessed through ``player.settings.volume_limits``.

    See :class:`Settings` for request and availability semantics.
    """

    def __init__(self, get: _HttpGet):
        self._get = get

    async def _query_endpoint(self, timeout: float | None = None) -> _AudioSetting | None:
        data = await self._get("/Settings?id=audio", timeout=timeout)
        return parse_audio_setting(data, "volumeLimits", "dual-range")

    async def get(self, timeout: float | None = None) -> tuple[float, float] | None:
        """Return (minimum, maximum) in dB, or None if absent from the player."""
        setting = await self._query_endpoint(timeout)
        if setting is None:
            return None
        if not isinstance(setting.value, tuple):
            raise PlayerUnexpectedResponseError("Expected dual-range setting value")
        return setting.value

    async def set(self, minimum: float, maximum: float, timeout: float | None = None) -> None:
        """Set volume limits in dB.

        Player-advertised bounds and minimum span are not checked locally.

        :raises ValueError: If limits are bools, non-finite, or not ascending.
        """
        if any(isinstance(val, bool) or not isfinite(val) for val in (minimum, maximum)) or minimum > maximum:
            raise ValueError("limits must be finite numbers in ascending order")
        # No setting URL: use the parent menuGroup URL.
        await self._get("/audiomodes", params={"volumeLimits": f"{minimum:g},{maximum:g}"}, timeout=timeout)

    async def is_available(self, timeout: float | None = None) -> bool:
        """Return whether the player advertises this setting."""
        return await self._query_endpoint(timeout) is not None

    async def values(self, timeout: float | None = None) -> SettingRange | None:
        """Return advertised bounds, or None if absent; these are not enforced by set()."""
        setting = await self._query_endpoint(timeout)
        return setting.range if setting else None


class AudioClockTrim:
    """Audio clock trim; accessed through ``player.settings.audio_clock_trim``.

    See :class:`Settings` for request and availability semantics.
    """

    def __init__(self, get: _HttpGet):
        self._get = get

    async def _query_endpoint(self, timeout: float | None = None) -> _AudioSetting | None:
        data = await self._get("/Settings?id=audio", timeout=timeout)
        return parse_audio_setting(data, "enableClockTrim", "boolean")

    async def get(self, timeout: float | None = None) -> bool | None:
        """Return whether enabled, or None if absent from the player."""
        setting = await self._query_endpoint(timeout)
        if setting is None:
            return None
        if not isinstance(setting.value, bool):
            raise PlayerUnexpectedResponseError("Expected boolean setting value")
        return setting.value

    async def set(self, enabled: bool, timeout: float | None = None) -> None:
        """Enable or disable this setting.

        :raises ValueError: If enabled is not a bool.
        """
        if not isinstance(enabled, bool):
            raise ValueError("enabled must be a bool")
        await self._get("/audiomodes", params={"enableClockTrim": "ON" if enabled else "OFF"}, timeout=timeout)

    async def is_available(self, timeout: float | None = None) -> bool:
        """Return whether the player advertises this setting."""
        return await self._query_endpoint(timeout) is not None


class Settings:  # pylint: disable=too-few-public-methods,too-many-instance-attributes
    """Audio settings accessed through ``player.settings``.

    Each get(), values(), or is_available() call fetches a fresh audio settings
    response. Availability means the player advertises the setting, not that it
    is currently enabled. Setters send one command and do not validate against
    advertised choices/ranges or read back the result.

    All methods accept an optional timeout in seconds; None uses the player's
    default. Transport failures raise :class:`~pyblu.errors.PlayerUnreachableError`;
    malformed setting responses raise
    :class:`~pyblu.errors.PlayerUnexpectedResponseError`.
    """

    def __init__(self, get: _HttpGet):
        self.listening_mode = ListeningMode(get)
        self.subwoofer_mode = SubwooferMode(get)
        self.tone_controls = ToneControls(get)
        self.treble = Treble(get)
        self.bass = Bass(get)
        self.balance = Balance(get)
        self.centre_channel = CentreChannel(get)
        self.centre_volume_trim = CentreVolumeTrim(get)
        self.crossover = Crossover(get)
        self.replay_gain = ReplayGain(get)
        self.output_mode = OutputMode(get)
        self.stereo_surround = StereoSurround(get)
        self.digital_passthrough = DigitalPassthrough(get)
        self.fixed_volume = FixedVolume(get)
        self.volume_limits = VolumeLimits(get)
        self.audio_clock_trim = AudioClockTrim(get)
