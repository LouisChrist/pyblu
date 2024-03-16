BluOS Client
============

This is a Python library for interfacing with BlueOS device. It uses the 
`BlueOS API <https://bluesound-deutschland.de/wp-content/uploads/2022/01/Custom-Integration-API-v1.0_March-2021.pdf>`_ 
to control and query the status of BlueOS devices.

Basic usage example:

.. code-block:: python

   from blueos import BluOSDevice

   async def main():
      async with BluOSDevice("<host>") as device:
         status = await device.status()
         print(status)

.. toctree::
   :maxdepth: 2

   api
