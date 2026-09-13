# pyblu

[![PyPI](https://img.shields.io/pypi/v/pyblu)](https://pypi.org/project/pyblu/)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/pyblu)](https://pypi.org/project/pyblu/)
[![PyPI - License](https://img.shields.io/pypi/l/pyblu)](https://github.com/LouisChrist/pyblu/blob/main/LICENSE)

This is a Python library for interfacing with BluOS players. 
It uses the 
[BluOS API](https://bluos.io/wp-content/uploads/2025/06/BluOS-Custom-Integration-API_v1.7.pdf) 
to control and query the status of BluOS players.
Authentication is not required.

Documentation is available at [here](https://louischrist.github.io/pyblu/)

```python
from pyblu import Player


async def main():
    async with Player("<host>") as player:
        status = await player.status()
        print(status)
```

## Installation

```bash
pip install pyblu
```

## Audio settings

Audio settings are exposed through `player.settings`:

| Settings | `get()` result | Mutation |
| --- | --- | --- |
| `listening_mode`, `subwoofer_mode`, `replay_gain`, `output_mode` | Active display name | `set(raw_name)` |
| `tone_controls`, `centre_channel`, `stereo_surround`, `digital_passthrough`, `fixed_volume`, `audio_clock_trim` | `bool` | `set(True)` / `set(False)` |
| `treble`, `bass`, `balance`, `centre_volume_trim`, `crossover` | `float` | `set(value)` |
| `volume_limits` | `(minimum, maximum)` in dB | `set(minimum, maximum)` |

All settings support `is_available(timeout=...)`. Readable settings return `None`
when absent. Availability means the setting is advertised by the player, not that
its prerequisites are satisfied. For backward compatibility, listening/subwoofer
modes also require at least one choice to report availability, and their `values()`
methods retain the original `ListeningModeValue` (with `icon`) and
`SubwooferModeValue` types. No prerequisite settings are automatically changed.

For choices, `values()` returns entries with `name`, `display_name`, and `active`;
pass `name` to `set()`. For ranges, `values()` returns a `SettingRange` with
`minimum`, `maximum`, optional `step`, `units`, and `minimum_range` (dual ranges).
Consult these device-specific limits before setting a numeric value; setters do
not fetch or enforce the advertised limits. Every operation accepts `timeout`.

```python
# Read-only examples:
controls_enabled = await player.settings.tone_controls.get()
bass_limits = await player.settings.bass.values()
replay_gain_choices = await player.settings.replay_gain.values()
```

The settings implementation is based on the saved N130/N331 responses in
`api-responses/settings/audio`. Mutation requests are tested with mocks, not live
hardware. Settings without a URL use the parent menu's `/audiomodes` URL.
The reset action advertised in the responses is intentionally not exposed.

## Development

For information on contributing and releasing new versions, see the [Development Guide](development.md).


