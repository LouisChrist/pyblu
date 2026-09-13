pyblu
============

This is an Python library for interfacing with BluOS player. It uses the
`BluOS API <https://bluos.io/wp-content/uploads/2025/06/BluOS-Custom-Integration-API_v1.7.pdf>`_
to control and query the status of BluOS players.

Basic usage example:

.. code-block:: python

   from pyblu import Player

   async def main():
      async with Player("<host>") as player:
         status = await player.status()
         print(status)

.. toctree::
   :maxdepth: 2

   usage
   api
