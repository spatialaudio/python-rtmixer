API Documentation
=================

.. module:: rtmixer

.. autosummary::
   :nosignatures:

   Mixer
   Recorder
   MixerAndRecorder
   RingBuffer

Common parameters that are shared by most commands:

``start``
   Desired time at which the playback/recording should be started.
   The actual time will be stored in the ``actual_time`` field of the
   returned action.

``time``
   Desired time at which the command should be executed.
   The actual time will be stored in the ``actual_time`` field of the
   returned action.

``allow_belated``
   Use ``False`` to cancel the command in case the requested time cannot be met.
   The ``actual_time`` field will be set to ``0.0`` in this case.
   Use ``True`` to execute the command nevertheless.
   Even if the requested time was met, the ``actual_time`` might be slightly
   different due to rounding.

All commands return a corresponding "action", which can be compared against the
active `actions`, and can be used  as input for `cancel()` and `wait()`.


.. autoclass:: Mixer
   :members: play_buffer, play_ringbuffer, actions, cancel, wait, stats,
             fetch_and_reset_stats
   :undoc-members:

.. autoclass:: Recorder
   :members:
   :undoc-members:

.. autoclass:: MixerAndRecorder
   :members:
   :undoc-members:

.. autoclass:: RingBuffer
   :inherited-members:
