Playing sources and browse actions
===================================

BluOS exposes two different kinds of URL-like values. They are invoked differently.

Source URLs
-----------

:meth:`Player.play_url <pyblu.Player.play_url>` accepts a stream URL or BluOS source identifier and constructs a
``/Play?url=...`` request. The ``url`` values returned by :meth:`Player.inputs <pyblu.Player.inputs>` and
:meth:`Player.presets <pyblu.Player.presets>` are source URLs:

.. code-block:: python

   inputs = await player.inputs()
   await player.play_url(inputs[0].url)

   presets = await player.presets()
   await player.play_url(presets[0].url)

   await player.play_url("https://example.com/radio.mp3")

Browse action URLs
------------------

The browse API instead returns complete, opaque action URIs. These values may start with ``/Play``, ``/Add``, or
another endpoint, and may contain service-specific query parameters. Pass them unchanged to
:meth:`Player.execute_action <pyblu.Player.execute_action>`; do not pass them to
:meth:`Player.play_url <pyblu.Player.play_url>`.

A :class:`BrowseItem <pyblu.BrowseItem>` may provide two playback actions:

``play_action_url``
   The item's default play action.

``autoplay_action_url``
   An optional auto-fill action. Depending on the service and item, it may play the item and add subsequent tracks
   from the containing album, playlist, or other object to the auto-fill section of the play queue.

Both fields are optional, so check for ``None`` before invoking them:

.. code-block:: python

   root = await player.browse()
   browse_item = next(item for item in root.items if item.browse_key is not None)
   result = await player.browse(key=browse_item.browse_key)
   item = result.items[0]

   if item.play_action_url is not None:
       await player.execute_action(item.play_action_url)

   # Use this instead when the service provides an auto-fill action.
   if item.autoplay_action_url is not None:
       await player.execute_action(item.autoplay_action_url)

For example, an action URI might be ``/Add?service=Service&albumid=1&playnow=1``. It is already a complete player
request. Calling ``player.play_url(item.play_action_url)`` would incorrectly place that complete URI inside a second
``/Play?url=...`` request.

Context-menu actions
--------------------

Context-menu action URLs use the same execution method. Actions can start playback, modify the play queue, add a
preset, or change a service favorite.

Actions can be requested lazily using an item's ``context_menu_key``:

.. code-block:: python

   if item.context_menu_key is not None:
       actions = await player.context_menu(item.context_menu_key)
       for action in actions:
           print(action.text, action.type)

       if actions:
           await player.execute_action(actions[0].action_url)

Alternatively, request inline actions while browsing:

.. code-block:: python

   root = await player.browse()
   browse_item = next(item for item in root.items if item.browse_key is not None)
   result = await player.browse(
       key=browse_item.browse_key,
       with_context_menu_items=True,
   )
   item = result.items[0]

   if item.context_menu:
       await player.execute_action(item.context_menu[0].action_url)

Browse keys and all action URLs are opaque. Do not parse, decode, reconstruct, or otherwise modify them before
passing them back to the same player that returned them.
