"""Validate untrusted settings responses without contacting a player."""

from unittest.mock import AsyncMock

import pytest

import pyblu
from pyblu.errors import PlayerUnexpectedResponseError
from pyblu.parse import parse_audio_setting
from pyblu.settings import Settings


@pytest.mark.parametrize(
    "name,setting_id",
    [
        ("tone_controls", "eq-switch"),
        ("treble", "eq-treble"),
        ("bass", "eq-bass"),
        ("balance", "eq-balance"),
        ("centre_channel", "centre"),
        ("centre_volume_trim", "eq-centre-trim"),
        ("crossover", "eq-crossover"),
        ("replay_gain", "replayGainMode"),
        ("output_mode", "channelMode"),
        ("stereo_surround", "ears"),
        ("digital_passthrough", "mqaDisable"),
        ("fixed_volume", "fixedVolume"),
        ("volume_limits", "volumeLimits"),
        ("audio_clock_trim", "enableClockTrim"),
    ],
)
async def test_wrong_setting_class_is_not_exposed(name, setting_id):
    # Well-formed XML and a value, but not the class promised by the public API.
    body = f'<settings><menuGroup><setting id="{setting_id}" class="text" value="ON"/></menuGroup></settings>'.encode()
    setting = getattr(Settings(AsyncMock(return_value=body)), name)
    for operation in ("get", "is_available", "values"):
        if hasattr(setting, operation):
            with pytest.raises(PlayerUnexpectedResponseError, match="Expected .* setting, got text"):
                await getattr(setting, operation)()


@pytest.mark.parametrize(
    "kind,value,children",
    [
        ("boolean", "ON", '<value name="ON" displayName="On"/>'),
        ("range", "nan", '<value min="-6" max="6"/>'),
        ("range", "inf", '<value min="-6" max="6"/>'),
        ("range", "-inf", '<value min="-6" max="6"/>'),
        ("range", "0", ""),
        ("range", "0", '<value min="-6" max="6"/><value min="-6" max="6"/>'),
        ("range", "0", '<value max="6"/>'),
        ("range", "0", '<value min="-6"/>'),
        ("range", "0", '<value min="nan" max="6"/>'),
        ("range", "0", '<value min="-6" max="inf"/>'),
        ("range", "0", '<value min="6" max="-6"/>'),
        ("range", "0", '<value min="-6" max="6" step="0"/>'),
        ("range", "0", '<value min="-6" max="6" step="-1"/>'),
        ("range", "0", '<value min="-6" max="6" step="nan"/>'),
        ("dual-range", "0,-90", '<value min="-90" max="0"/>'),
        ("dual-range", "nan,0", '<value min="-90" max="0"/>'),
        ("dual-range", "-90,inf", '<value min="-90" max="0"/>'),
        ("dual-range", "-90", '<value min="-90" max="0"/>'),
        ("dual-range", "-90,0", '<value min="-90" max="0" minRange="-1"/>'),
        ("dual-range", "-90,0", '<value min="-90" max="0" minRange="91"/>'),
        ("dual-range", "-90,0", '<value min="-90" max="0" minRange="inf"/>'),
        ("list", "raw", '<value name="raw"/>'),
        ("list", "raw", '<value displayName="Display"/>'),
        ("boolean", "ON", '<dependsOn name="other"/>'),
        ("boolean", "ON", '<dependsOn value="OFF"/>'),
    ],
)
def test_invalid_values_and_metadata(kind, value, children):
    body = f'<settings><menuGroup><setting id="test" class="{kind}" value="{value}">{children}</setting></menuGroup></settings>'.encode()
    with pytest.raises(PlayerUnexpectedResponseError):
        parse_audio_setting(body, "test", kind)


@pytest.mark.parametrize(
    "element",
    [
        '<setting id="test" value="ON"/>',
        '<setting id="test" class="boolean"/>',
        '<setting id="test" class="boolean" value="ON"/>' * 2,
    ],
)
def test_missing_attributes_and_duplicate_settings(element):
    body = f"<settings><menuGroup>{element}</menuGroup></settings>".encode()
    with pytest.raises(PlayerUnexpectedResponseError):
        parse_audio_setting(body, "test", "boolean")


def test_audio_setting_is_not_public():
    assert "AudioSetting" not in pyblu.__all__
    assert not hasattr(pyblu, "AudioSetting")


@pytest.mark.parametrize("name", ["treble", "bass", "balance", "centre_volume_trim", "crossover"])
@pytest.mark.parametrize("value", [True, False, float("nan"), float("inf"), float("-inf")])
async def test_numeric_setter_rejects_values_not_excluded_by_float_annotation(name, value):
    get = AsyncMock()
    with pytest.raises(ValueError):
        await getattr(Settings(get), name).set(value)
    get.assert_not_awaited()


@pytest.mark.parametrize("value", [True, False, float("nan"), float("inf"), float("-inf")])
@pytest.mark.parametrize("position", ["minimum", "maximum"])
async def test_volume_limits_reject_invalid_numbers(position, value):
    get = AsyncMock()
    limits = {"minimum": -90.0, "maximum": 0.0, position: value}
    with pytest.raises(ValueError):
        await Settings(get).volume_limits.set(**limits)
    get.assert_not_awaited()
