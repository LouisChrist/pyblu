# BluOS Client

[![PyPI](https://img.shields.io/pypi/v/bluos)](https://pypi.org/project/bluos/)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/bluos)](https://pypi.org/project/bluos/)
[![PyPI - License](https://img.shields.io/pypi/l/bluos)](https://github.com/LouisChrist/python-bluos/blob/main/LICENSE)

This is a Python library for interfacing with BlueOS devices. 
It uses the 
[BlueOS API](https://bluesound-deutschland.de/wp-content/uploads/2022/01/Custom-Integration-API-v1.0_March-2021.pdf) 
to control and query the status of BlueOS devices.
Authentication is not required.

Documentation is available at [here](https://louischrist.github.io/python-bluos/)

```python
from blueos import BluOSDevice

async def main():
    async with BluOSDevice("<host>") as device:
        status = await device.status()
        print(status)
```

## Installation

```bash
pip install blueos
```


