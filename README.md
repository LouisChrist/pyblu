# BluOS Client

[![PyPI](https://img.shields.io/pypi/v/bluos)](https://pypi.org/project/bluos/)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/bluos)](https://pypi.org/project/bluos/)
[![PyPI - License](https://img.shields.io/pypi/l/bluos)](https://github.com/LouisChrist/python-bluos/blob/main/LICENSE)

This is a Python library for interfacing with BluOS players. 
It uses the 
[BluOS API](https://bluesound-deutschland.de/wp-content/uploads/2022/01/Custom-Integration-API-v1.0_March-2021.pdf) 
to control and query the status of BluOS players.
Authentication is not required.

Documentation is available at [here](https://louischrist.github.io/python-bluos/)

```python
from bluos import Player

async def main():
    async with Player("<host>") as player:
        status = await player.status()
        print(status)
```

## Installation

```bash
pip install bluos
```


