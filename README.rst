Realtime Audio Mixer for Python
===============================

**WARNING:** This is work in progress!

Goal: Reliable low-latency audio playback and recording with Python, using
PortAudio_ via the sounddevice_ module.

The audio callback is implemented in C (and compiled with the help of CFFI_)
and doesn't invoke the Python interpreter, therefore avoiding waiting for things
like garbage collection and the GIL.

All PortAudio platforms and host APIs are supported.
Runs on any Python version where CFFI is available.

Features:

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

Planned features:

* meticulous reporting of overruns/underruns

* loopback tests to verify correct operation and accurate latency values

* fade in/out?

* loop?

* playlist/queue?

Out of scope:

* reading from/writing to files (use e.g. the soundfile_ module)

* realtime signal processing (inside the audio callback)

* signal generators

* multiple mixer instances (some PortAudio host APIs only support one stream at
  a time)

* resampling (apart from what PortAudio does)

* fast forward/rewind

* panning/balance

* audio/video synchronization

Somewhat similar projects:

* https://github.com/nwhitehead/swmixer
* https://github.com/nvahalik/PyAudioMixer
* http://www.pygame.org/docs/ref/mixer.html

.. _PortAudio: http://portaudio.com/
.. _sounddevice: http://python-sounddevice.readthedocs.io/
.. _CFFI: http://cffi.readthedocs.io/
.. _soundfile: http://pysoundfile.readthedocs.io/

Installation
------------

::

    python3 setup.py develop --user

or ::

    python3 -m pip install -e . --user

Usage
-----

See the examples in the `examples/` directory.
