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
| `listening_mode`, `subwoofer_mode`, `replay_gain`, `output_mode` | Active display name | `set(name)` |
| `tone_controls`, `centre_channel`, `stereo_surround`, `digital_passthrough`, `fixed_volume`, `audio_clock_trim` | `bool` | `set(True)` / `set(False)` |
| `treble`, `bass`, `balance`, `centre_volume_trim`, `crossover` | `float` | `set(value)` |
| `volume_limits` | `(minimum, maximum)` in dB | `set(minimum, maximum)` |

Inside the `async with` block, you can read settings and their available values:

```python
controls_enabled = await player.settings.tone_controls.get()
bass_limits = await player.settings.bass.values()
replay_gain_choices = await player.settings.replay_gain.values()
```

- `get()` returns `None` if the setting is missing or no choice is active.
- `is_available()` checks whether the player lists the setting. For listening
  and subwoofer modes, it also requires at least one choice. This does not check
  whether other settings need to be enabled first; pyblu won't change them for you.
- For settings with choices, `values()` returns entries with `name`,
  `display_name`, and `active`. Pass the entry's `name` to `set()`, not its
  display name.
- For numeric settings, `values()` returns a `SettingRange`, or `None` if the
  setting is missing. It contains `minimum`, `maximum`, and optional `step`,
  `units`, and `minimum_range` (for volume limits). Check these limits before
  changing a value: `set()` does not fetch or enforce them.

All settings methods accept a `timeout` in seconds.

## Development

See the [development guide](development.md) for setup, checks, and releases.
