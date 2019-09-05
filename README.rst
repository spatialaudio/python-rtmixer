Realtime Audio Mixer for Python
===============================

.. warning:: This is work in progress!

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

Installation
------------

On Windows, macOS, and Linux you can install a precompiled wheel with::

    python3 -m pip install rtmixer

This will install ``rtmixer`` and its dependencies, including ``sounddevice``.

.. note:: On Linux, to use ``sounddevice`` and ``rtmixer`` you will need to
          have PortAudio installed, e.g. via ``sudo apt install libportaudio2``.
          On other platforms, PortAudio comes bundled with ``sounddevice``.

Developers can install in editable mode with some variant of::

    git clone https://github.com/spatialaudio/python-rtmixer
    cd python-rtmixer
    git submodule update --init
    python3 -m pip install -e .

Usage
-----

See the list of `examples on GitHub`_.

.. _PortAudio: http://portaudio.com/
.. _sounddevice: http://python-sounddevice.readthedocs.io/
.. _CFFI: http://cffi.readthedocs.io/
.. _soundfile: http://pysoundfile.readthedocs.io/
.. _examples on GitHub: https://github.com/spatialaudio/python-rtmixer/tree/master/examples
