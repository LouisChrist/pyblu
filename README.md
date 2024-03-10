# BluOS Client

This is a Python library for interfacing with BlueOS devices. 

```python
from blueos import BlueOSDevice

async def main():
    async with BlueOSDevice("<host>") as device:
        status = await device.status()
        print(status)
```

## Installation

```bash
pip install blueos
```


