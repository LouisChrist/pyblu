# pyblu

[![PyPI](https://img.shields.io/pypi/v/pyblu)](https://pypi.org/project/pyblu/)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/pyblu)](https://pypi.org/project/pyblu/)
[![PyPI - License](https://img.shields.io/pypi/l/pyblu)](https://github.com/LouisChrist/pyblu/blob/main/LICENSE)

pyblu is an async Python library for controlling BluOS players and reading their
status. It connects directly to a player using the
[BluOS HTTP API](https://bluos.io/wp-content/uploads/2025/06/BluOS-Custom-Integration-API_v1.7.pdf),
with no authentication required.

## Installation

Requires Python 3.12 or newer.

```bash
pip install pyblu
```

## Quick start

Replace `<host>` with your player's hostname or IP address:

```python
import asyncio

from pyblu import Player


async def main():
    async with Player("<host>") as player:
        status = await player.status()
        print(status)


asyncio.run(main())
```

The connection uses port 11000 by default. Using `async with` closes the client's
HTTP session when you're done.

See the [documentation](https://louischrist.github.io/pyblu/) for playback,
volume, browsing, play queues, and player grouping.

## Audio settings

Use `player.settings` to read or change audio settings. Which settings are
available depends on your player.

| Settings | `get()` result | How to change it |
| --- | --- | --- |
| `listening_mode`, `subwoofer_mode` (legacy) | Active display name | `set(name)` |
| `replay_gain`, `output_mode` | Raw active name | `set(name)` |
| `tone_controls`, `centre_channel`, `stereo_surround`, `digital_passthrough`, `fixed_volume`, `audio_clock_trim` | `bool` | `set(True)` / `set(False)` |
| `treble`, `bass`, `balance`, `centre_volume_trim`, `crossover` | `float` | `set(value)` |
| `volume_limits` | `(minimum, maximum)` in dB | `set(minimum, maximum)` |

Inside the `async with` block, you can read settings and their available values:

```python
controls_enabled = await player.settings.tone_controls.get()
bass_limits = await player.settings.bass.range()
replay_gain_choices = await player.settings.replay_gain.choices()
```

- `get()` returns `None` if the setting is missing. For `replay_gain` and
  `output_mode`, it returns the raw active name even if not listed in `choices()`.
- `is_available()` checks whether the player lists the setting. For listening
  and subwoofer modes, it also requires at least one choice.
- For `replay_gain` and `output_mode`, `choices()` returns entries with `name`,
  `display_name`, and `active`. Both `get()` and `set()` use raw names;
  use `display_name` for presentation.
- The legacy `listening_mode` and `subwoofer_mode` APIs retain `values()` and
  display-name getters. Their `get()` also returns `None` if no choice matches;
  pass a `values()` entry's `name` to `set()`, not the display name.
- For numeric settings, `range()` returns a `SettingRange`, or `None` if the
  setting is missing. It contains `minimum`, `maximum`, and optional `step`,
  `units`, and `minimum_range` (for volume limits). Check these limits before
  changing a value: `set()` does not fetch or enforce them.

All settings methods accept a `timeout` in seconds.

### Legacy choice settings

`listening_mode` and `subwoofer_mode` preserve their original API for backward
compatibility. They differ from the newer choice settings:

| Behavior | `listening_mode`, `subwoofer_mode` | `replay_gain`, `output_mode` |
| --- | --- | --- |
| `get()` | Display label, e.g. `"Movie"` or `"Off"` | Raw name, e.g. `"none"` or `"default"` |
| `set(name)` | Raw name, **not** the display label | Raw name, same representation as `get()` |
| List choices | `values()` | `choices()` |
| Active name not in choices | `get()` returns `None` | `get()` returns the raw name |
| `is_available()` | Requires at least one choice | Requires the setting to be present |

**Do not pass a legacy setting's `get()` result to `set()`.** Obtain its raw
name from the active entry in `values()` instead:

```python
choices = await player.settings.subwoofer_mode.values()
original_name = next((choice.name for choice in choices if choice.active), None)
# If restoring later, pass original_name to set(), not the display label "Off".
```

Legacy listening-mode choices are `ListeningModeValue` objects (including an
`icon`); subwoofer choices are `SubwooferModeValue` objects. New choice settings
return `SettingValue` objects. All three expose `name`, `display_name`, and `active`.

## Development

See the [development guide](development.md) for setup, checks, and releases.
