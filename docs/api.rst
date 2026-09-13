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