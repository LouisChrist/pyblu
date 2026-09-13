API Reference
=============

Main Classes
------------

.. autoclass:: pyblu.Player
   :members:
   :special-members: __init__

Audio Settings
--------------

Access these through ``player.settings``; do not instantiate them directly.
See :class:`pyblu.settings.Settings` for shared timeout and availability semantics.

.. important::

   ``listening_mode`` and ``subwoofer_mode`` are legacy exceptions: their
   ``get()`` methods return display labels, but ``set()`` requires raw names
   from ``values()``. Do not round-trip their getters directly into setters.
   The newer ``replay_gain`` and ``output_mode`` use raw names for both
   ``get()`` and ``set()``, and expose ``choices()`` instead of ``values()``.
   See :doc:`usage` for the full legacy comparison and a save/restore example.

.. autoclass:: pyblu.settings.Settings
   :members:

.. autoclass:: pyblu.settings.ListeningMode
   :members:

.. autoclass:: pyblu.settings.SubwooferMode
   :members:

.. autoclass:: pyblu.settings.ToneControls
   :members:

.. autoclass:: pyblu.settings.Treble
   :members:

.. autoclass:: pyblu.settings.Bass
   :members:

.. autoclass:: pyblu.settings.Balance
   :members:

.. autoclass:: pyblu.settings.CentreChannel
   :members:

.. autoclass:: pyblu.settings.CentreVolumeTrim
   :members:

.. autoclass:: pyblu.settings.Crossover
   :members:

.. autoclass:: pyblu.settings.ReplayGain
   :members:

.. autoclass:: pyblu.settings.OutputMode
   :members:

.. autoclass:: pyblu.settings.StereoSurround
   :members:

.. autoclass:: pyblu.settings.DigitalPassthrough
   :members:

.. autoclass:: pyblu.settings.FixedVolume
   :members:

.. autoclass:: pyblu.settings.VolumeLimits
   :members:

.. autoclass:: pyblu.settings.AudioClockTrim
   :members:

Data Classes
------------

.. autoclass:: pyblu.SettingValue
   :members:

.. autoclass:: pyblu.SettingRange
   :members:

.. autoclass:: pyblu.ListeningModeValue
   :members:

.. autoclass:: pyblu.SubwooferModeValue
   :members:

.. autoclass:: pyblu.Status
   :members:

.. autoclass:: pyblu.Volume
   :members:

.. autoclass:: pyblu.SyncStatus
   :members:

.. autoclass:: pyblu.PairedPlayer
   :members:

.. autoclass:: pyblu.Preset
   :members:

.. autoclass:: pyblu.PlayQueue
   :members:

.. autoclass:: pyblu.PlayQueueTrack
   :members:

.. autoclass:: pyblu.Input
   :members:

.. autoclass:: pyblu.BrowseResult
   :members:

.. autoclass:: pyblu.BrowseItem
   :members:

.. autoclass:: pyblu.BrowseCategory
   :members:

.. autoclass:: pyblu.ContextMenuAction
   :members:

Exceptions
----------

.. autoclass:: pyblu.errors.PlayerError
   :members:

.. autoclass:: pyblu.errors.PlayerUnreachableError
   :members:

.. autoclass:: pyblu.errors.PlayerUnexpectedResponseError
   :members:

.. autoclass:: pyblu.errors.PlayerCommandError
   :members:

.. autoclass:: pyblu.errors.PlayerBrowseError
   :members: