# pyblu

[![PyPI](https://img.shields.io/pypi/v/pyblu)](https://pypi.org/project/pyblu/)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/pyblu)](https://pypi.org/project/pyblu/)
[![PyPI - License](https://img.shields.io/pypi/l/pyblu)](https://github.com/LouisChrist/pyblu/blob/main/LICENSE)

This is a Python library for interfacing with BluOS players. 
It uses the 
[BluOS API](https://bluesound-deutschland.de/wp-content/uploads/2022/01/Custom-Integration-API-v1.0_March-2021.pdf) 
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


