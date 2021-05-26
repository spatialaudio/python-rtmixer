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

``channels``
   This can be either the desired number of channels or a list of (1-based)
   channel numbers that is used as a channel map for playback/recording.

``allow_belated``
   Use ``False`` to cancel the command in case the requested time cannot be met.
   The ``actual_time`` field will be set to ``0.0`` in this case.
   Use ``True`` to execute the command nevertheless.
   Even if the requested time was met, the ``actual_time`` might be slightly
   different due to rounding to the next audio sample.

All commands return a corresponding "action", which can be compared against the
active `actions`, and can be used  as input for `cancel()` and `wait()`.
The fields of action objects are defined in C but can be accessed with
Python (e.g. ``my_action.stats.min_blocksize``)
*after* the command is finished:

.. literalinclude:: ../src/rtmixer.h
   :language: c
   :start-at: struct action
   :end-at: flexible array member
   :append: };

The ``stats`` field contains some statistics collected during playback/recording
(again, *after* the command is finished):

.. literalinclude:: ../src/rtmixer.h
   :language: c
   :start-at: struct stats
   :end-at: }

These statistics are also collected for the whole runtime of a stream,
where they are available as `stats` attribute (but only if the stream is
*inactive*).  The statistics of an *active* stream can be obtained
(and at the same time reset) with `fetch_and_reset_stats()`.

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
