"""Settings tests use saved responses and strict mocks, never a real player."""

from dataclasses import dataclass
from pathlib import Path
from unittest.mock import AsyncMock

import aiohttp
import pytest
from mocket import Mocket, async_mocketize
from mocket.mocks.mockhttp import Entry
from mocket.plugins.aiohttp_connector import MocketTCPConnector

from pyblu import ListeningModeValue, Player, SettingRange, SettingValue, SubwooferModeValue
from pyblu.errors import PlayerUnexpectedResponseError, PlayerUnreachableError
from pyblu.parse import parse_audio_setting
from pyblu.settings import ListeningMode, Settings, SubwooferMode

RESPONSES = Path(__file__).resolve().parents[1] / "api-responses/settings/audio"


@dataclass(frozen=True)
class SettingCase:
    name: str
    setting_id: str
    endpoint: str
    set_args: tuple[str | bool | float, ...]
    encoded_value: str
    n130_value: str | bool | float | tuple[float, float] | None
    n331_value: str | bool | float | tuple[float, float] | None


SETTINGS = [
    SettingCase(
        name="listening_mode",
        setting_id="preset",
        endpoint="/alsa_setting",
        set_args=("MUSIC",),
        encoded_value="MUSIC",
        n130_value=None,
        n331_value="Movie",
    ),
    SettingCase(
        name="subwoofer_mode",
        setting_id="subwoofer",
        endpoint="/audiomodes",
        set_args=("withsub",),
        encoded_value="withsub",
        n130_value="Off",
        n331_value="On",
    ),
    SettingCase(
        name="tone_controls",
        setting_id="eq-switch",
        endpoint="/alsa_setting",
        set_args=(True,),
        encoded_value="ON",
        n130_value=False,
        n331_value=False,
    ),
    SettingCase(
        name="treble",
        setting_id="eq-treble",
        endpoint="/alsa_setting",
        set_args=(1.5,),
        encoded_value="1.5",
        n130_value=0.0,
        n331_value=0.0,
    ),
    SettingCase(
        name="bass",
        setting_id="eq-bass",
        endpoint="/alsa_setting",
        set_args=(-2.5,),
        encoded_value="-2.5",
        n130_value=0.0,
        n331_value=0.0,
    ),
    SettingCase(
        name="balance",
        setting_id="eq-balance",
        endpoint="/alsa_setting",
        set_args=(-1,),
        encoded_value="-1",
        n130_value=None,
        n331_value=0.0,
    ),
    SettingCase(
        name="centre_channel",
        setting_id="centre",
        endpoint="/setting",
        set_args=(False,),
        encoded_value="OFF",
        n130_value=None,
        n331_value=True,
    ),
    SettingCase(
        name="centre_volume_trim",
        setting_id="eq-centre-trim",
        endpoint="/alsa_setting",
        set_args=(0.5,),
        encoded_value="0.5",
        n130_value=None,
        n331_value=0.0,
    ),
    SettingCase(
        name="crossover",
        setting_id="eq-crossover",
        endpoint="/alsa_setting",
        set_args=(100,),
        encoded_value="100",
        n130_value=80.0,
        n331_value=80.0,
    ),
    SettingCase(
        name="replay_gain",
        setting_id="replayGainMode",
        endpoint="/audiomodes",
        set_args=("album",),
        encoded_value="album",
        n130_value="Disabled",
        n331_value="Disabled",
    ),
    SettingCase(
        name="output_mode",
        setting_id="channelMode",
        endpoint="/audiomodes",
        set_args=("mono",),
        encoded_value="mono",
        n130_value="Stereo",
        n331_value="Stereo",
    ),
    SettingCase(
        name="stereo_surround",
        setting_id="ears",
        endpoint="/audiomodes",
        set_args=(True,),
        encoded_value="ON",
        n130_value=None,
        n331_value=False,
    ),
    SettingCase(
        name="digital_passthrough",
        setting_id="mqaDisable",
        endpoint="/audiomodes",
        set_args=(True,),
        encoded_value="ON",
        n130_value=False,
        n331_value=None,
    ),
    SettingCase(
        name="fixed_volume",
        setting_id="fixedVolume",
        endpoint="/audiomodes",
        set_args=(True,),
        encoded_value="ON",
        n130_value=False,
        n331_value=None,
    ),
    SettingCase(
        name="volume_limits",
        setting_id="volumeLimits",
        endpoint="/audiomodes",
        set_args=(-60, -10),
        encoded_value="-60,-10",
        n130_value=(-44.0, 0.0),
        n331_value=(-90.0, 0.0),
    ),
    SettingCase(
        name="audio_clock_trim",
        setting_id="enableClockTrim",
        endpoint="/audiomodes",
        set_args=(False,),
        encoded_value="OFF",
        n130_value=True,
        n331_value=None,
    ),
]


@pytest.mark.parametrize("case", SETTINGS, ids=[case.name for case in SETTINGS])
@pytest.mark.parametrize("model", ["n130", "n331"])
@pytest.mark.parametrize("operation", ["get", "is_available"])
@async_mocketize(strict_mode=True)
async def test_read_settings(case: SettingCase, model, operation):
    expected = case.n130_value if model == "n130" else case.n331_value
    body = (RESPONSES / f"bluesound_{model}.xml").read_bytes()
    Entry.single_register(Entry.GET, "http://node:11000/Settings?id=audio", status=200, body=body)
    async with aiohttp.ClientSession(connector=MocketTCPConnector()) as session:
        async with Player("node", session=session) as player:
            setting = getattr(player.settings, case.name)
            if operation == "is_available":
                assert await setting.is_available() is (expected is not None)
            else:
                assert await setting.get() == expected
    assert len(Mocket.request_list()) == 1


@pytest.mark.parametrize("case", SETTINGS, ids=[case.name for case in SETTINGS])
@async_mocketize(strict_mode=True)
async def test_set_settings(case):
    Entry.single_register(Entry.GET, f"http://node:11000{case.endpoint}?{case.setting_id}={case.encoded_value}", status=200, body="<ok/>")
    async with aiohttp.ClientSession(connector=MocketTCPConnector()) as session:
        async with Player("node", session=session) as player:
            setting = getattr(player.settings, case.name)
            await setting.set(*case.set_args, timeout=3)
    assert len(Mocket.request_list()) == 1


@pytest.mark.parametrize("case", SETTINGS, ids=[case.name for case in SETTINGS])
async def test_timeouts_and_errors(case):
    get = AsyncMock(return_value=(RESPONSES / "bluesound_n331.xml").read_bytes())
    setting = getattr(Settings(get), case.name)
    await setting.is_available(timeout=2)
    get.assert_awaited_once_with("/Settings?id=audio", timeout=2)
    get.reset_mock()
    await setting.set(*case.set_args, timeout=3)
    get.assert_awaited_once_with(case.endpoint, params={case.setting_id: case.encoded_value}, timeout=3)
    get.side_effect = PlayerUnreachableError("offline")
    with pytest.raises(PlayerUnreachableError):
        await setting.is_available()


@pytest.mark.parametrize("case", SETTINGS, ids=[case.name for case in SETTINGS])
async def test_missing_settings(case):
    setting = getattr(Settings(AsyncMock(return_value=b"<settings/>")), case.name)
    assert not await setting.is_available()
    assert await setting.get() is None
    if hasattr(setting, "values"):
        assert await setting.values() in (None, [])


@pytest.mark.parametrize("case", [case for case in SETTINGS if isinstance(case.set_args[0], bool)], ids=lambda case: case.name)
@pytest.mark.parametrize("enabled", [True, False])
async def test_boolean_round_trip(case, enabled):
    value = "ON" if enabled else "OFF"
    body = f'<settings><menuGroup><setting id="{case.setting_id}" class="boolean" value="{value}"/></menuGroup></settings>'.encode()
    get = AsyncMock(return_value=body)
    setting = getattr(Settings(get), case.name)
    assert await setting.get(timeout=2) is enabled
    get.assert_awaited_once_with("/Settings?id=audio", timeout=2)
    get.reset_mock()
    await setting.set(enabled, timeout=3)
    get.assert_awaited_once_with(case.endpoint, params={case.setting_id: value}, timeout=3)


@pytest.mark.parametrize("name,setting_id", [("replay_gain", "replayGainMode"), ("output_mode", "channelMode")])
async def test_unknown_active_choice(name, setting_id):
    body = (
        f'<settings><menuGroup><setting id="{setting_id}" class="list" value="new">' '<value name="old" displayName="Old"/></setting></menuGroup></settings>'
    ).encode()
    setting = getattr(Settings(AsyncMock(return_value=body)), name)
    assert await setting.get() is None
    assert await setting.is_available()
    assert await setting.values() == [SettingValue("old", "Old", False)]


@pytest.mark.parametrize(
    "name,setting_id,endpoint,expected",
    [
        ("listening_mode", "preset", "/alsa_setting", ListeningModeValue("raw", "Display", "/icon.png", True)),
        ("subwoofer_mode", "subwoofer", "/audiomodes", SubwooferModeValue("raw", "Display", True)),
    ],
)
async def test_original_mode_api(name, setting_id, endpoint, expected):
    # No class attribute was required by the original parsers. Preserve that too.
    body = (
        f'<settings><menuGroup><setting id="{setting_id}" value="raw">'
        '<value name="raw" displayName="Display" icon="/icon.png"/>'
        '<dependsOn name="other" value="OFF"/></setting></menuGroup></settings>'
    ).encode()
    get = AsyncMock(return_value=body)
    setting = getattr(Settings(get), name)
    assert isinstance(setting, ListeningMode if name == "listening_mode" else SubwooferMode)
    values = await setting.values(timeout=2)
    assert values == [expected]
    assert type(values[0]) is type(expected)
    get.assert_awaited_once_with("/Settings?id=audio", timeout=2)
    assert await setting.get(timeout=2) == "Display"
    assert await setting.is_available(timeout=2)
    get.reset_mock()
    await setting.set(mode="raw", timeout=3)
    get.assert_awaited_once_with(endpoint, params={setting_id: "raw"}, timeout=3)

    get.return_value = body.replace(b'value="raw"', b'value="unknown"')
    assert await setting.get() is None
    assert await setting.is_available()
    assert not (await setting.values())[0].active

    get.return_value = f'<settings><setting id="{setting_id}" value="raw"/></settings>'.encode()
    assert await setting.values() == []
    assert await setting.get() is None
    assert not await setting.is_available()


async def test_choices_and_ranges():
    settings = Settings(AsyncMock(return_value=(RESPONSES / "bluesound_n130.xml").read_bytes()))
    assert await settings.replay_gain.values() == [
        SettingValue("none", "Disabled", True),
        SettingValue("track", "Track gain", False),
        SettingValue("album", "Album gain", False),
        SettingValue("smart", "Smart gain", False),
    ]
    assert await settings.output_mode.values() == [
        SettingValue("default", "Stereo", True),
        SettingValue("left", "Left", False),
        SettingValue("right", "Right", False),
        SettingValue("mono", "Mono", False),
    ]
    assert await settings.treble.values() == SettingRange(-6, 6, 0.5, "dB")
    assert await settings.bass.values() == SettingRange(-6, 6, 0.5, "dB")
    assert await settings.crossover.values() == SettingRange(40, 200, 10, "Hz")
    assert await settings.volume_limits.values() == SettingRange(-90, 0, units="dB", minimum_range=30)
    settings = Settings(AsyncMock(return_value=(RESPONSES / "bluesound_n331.xml").read_bytes()))
    assert await settings.balance.values() == SettingRange(-7, 7, 0.5)
    assert await settings.centre_volume_trim.values() == SettingRange(-10, 10, 0.5)


def test_dependencies_are_not_choices():
    setting = parse_audio_setting((RESPONSES / "bluesound_n130.xml").read_bytes(), "replayGainMode", "list")
    assert setting is not None
    assert setting.dependencies == {"mqaDisable": "OFF"}
    assert len(setting.values) == 4


@pytest.mark.parametrize(
    "kind,body",
    [
        ("boolean", b"not xml"),
        ("boolean", b'<settings><menuGroup><setting id="test" class="boolean" value="invalid"/></menuGroup></settings>'),
        ("range", b'<settings><menuGroup><setting id="test" class="range" value="invalid"/></menuGroup></settings>'),
        ("dual-range", b'<settings><menuGroup><setting id="test" class="dual-range" value="1,2,3"/></menuGroup></settings>'),
        ("list", b'<settings><menuGroup><setting id="test" class="list"/></menuGroup></settings>'),
    ],
)
def test_malformed_settings(kind, body):
    with pytest.raises(PlayerUnexpectedResponseError):
        parse_audio_setting(body, "test", kind)


@pytest.mark.parametrize(
    "name,args",
    [
        ("tone_controls", ("OFF",)),
        ("treble", (float("nan"),)),
        ("bass", (float("inf"),)),
        ("balance", (True,)),
        ("volume_limits", (0, -90)),
        ("volume_limits", (float("-inf"), 0)),
    ],
)
async def test_invalid_values_do_not_send_requests(name, args):
    get = AsyncMock()
    with pytest.raises(ValueError):
        await getattr(Settings(get), name).set(*args)
    get.assert_not_awaited()
