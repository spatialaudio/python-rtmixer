Features
========

* playback of multiple signals at the same time (that's why it's called "mixer")

* play from buffer, play from ringbuffer

* record into buffer, record into ringbuffer

* multichannel support

* NumPy arrays with data type ``'float32'`` can be easily used (via the buffer
  protocol) as long as they are C-contiguous

* fixed latency playback, (close to) no jitter (optional)

  * to be verified ...

* sample-accurate playback/recording (with known offset)

  * to be verified ...

* non-blocking callback function, using PortAudio ringbuffers

* all memory allocations/deallocations happen outside the audio callback


Planned Features
----------------

* meticulous reporting of overruns/underruns

* loopback tests to verify correct operation and accurate latency values

* fade in/out?

* loop?

* playlist/queue?


Out Of Scope
------------

* reading from/writing to files (use e.g. the soundfile_ module instead)

* realtime signal processing inside the audio callback
  (ring buffers can be used as a work-around,
  see the signal_processing.py_ example)

* signal generators

* multiple mixer instances (some PortAudio host APIs only support one stream at
  a time)

* resampling (apart from what PortAudio does)

* fast forward/rewind

* panning/balance

* audio/video synchronization

.. _soundfile: https://python-soundfile.readthedocs.io/
.. _signal_processing.py: https://github.com/spatialaudio/python-rtmixer/
   blob/master/examples/signal_processing.py
