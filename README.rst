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

* non-blocking callback function, using PortAudio ringbuffers

* play from buffer, play from ringbuffer

* multichannel support

* all memory allocations/deallocations happen outside of the audio callback

Planned features:

* fixed latency playback, no jitter (optional)

* sample-accurate playback/recording (with known offset)

* meticulous reporting of overruns/underruns

* loopback tests to verify correct operation and accurate latency values

* optional NumPy support?

* notification when playback is done?

* playlist/queue?

Out of scope:

* reading from/writing to files (use e.g. the soundfile_ module)

* realtime signal processing (inside the audio callback)

* signal generators

* multiple mixer instances (some PortAudio host APIs only support one stream at
  a time)

* resampling (apart from what PortAudio does)

* fade in/out

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
