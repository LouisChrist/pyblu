pyblu
============

This is an Python library for interfacing with BluOS player. It uses the
`BluOS API <https://bluesound-deutschland.de/wp-content/uploads/2022/01/Custom-Integration-API-v1.0_March-2021.pdf>`_
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

   api
