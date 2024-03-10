# BluOS Client

This is a Python library for interfacing with BlueOS devices. 
It uses the 
[BlueOS API](https://bluesound-deutschland.de/wp-content/uploads/2022/01/Custom-Integration-API-v1.0_March-2021.pdf) 
to control and query the status of BlueOS devices.
Authentication is not required.

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


