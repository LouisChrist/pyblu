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

## Development

For information on contributing and releasing new versions, see the [Development Guide](development.md).


