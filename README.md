Realtime Audio Mixer for Python
===============================

WARNING: This is work in progress!

Goal: Reliable low-latency audio playback and recording with Python, using
[PortAudio][] via the [sounddevice][] module.

The audio callback is implemented in C (and compiled with the help of [CFFI][])
and doesn't invoke the Python interpreter, therefore avoiding waiting for things
like garbage collection and the GIL.

Planned features:

* playback of multiple signals at the same time (fixed maximum number?)

* fixed latency playback, no jitter (optional)

* sample-accurate playback/recording (with known offset)

* non-blocking callback function, using PortAudio ringbuffer(s)

* play from memory, play from generator

* multichannel support

* meticulous reporting of overruns/underruns

* optional NumPy support?

* playlist/queue?

Out of scope:

* reading from/writing to files (use e.g. the [soundfile][] module)

* realtime signal processing (inside the audio callback)

Somewhat similar projects:

* https://github.com/nwhitehead/swmixer
* https://github.com/nvahalik/PyAudioMixer
* http://www.pygame.org/docs/ref/mixer.html

[PortAudio]: http://portaudio.com/
[sounddevice]: http://python-sounddevice.readthedocs.io/
[CFFI]: http://cffi.readthedocs.io/
[soundfile]: http://pysoundfile.readthedocs.io/

Dependencies
------------

CFFI >= 1.4.0

sounddevice > 0.3.6

Compiling
---------

PortAudio doesn't have to be installed, but `portaudio.h` must be available.

    python3 rtmixer_build.py

Usage
-----

```python
import rtmixer
mixer = rtmixer.RtMixer()
```
