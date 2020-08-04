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

Online documentation
    https://python-rtmixer.readthedocs.io/

Source code repository
    https://github.com/spatialaudio/python-rtmixer

Somewhat similar projects
    * https://github.com/nwhitehead/swmixer
    * https://github.com/nvahalik/PyAudioMixer
    * http://www.pygame.org/docs/ref/mixer.html

.. _PortAudio: http://portaudio.com/
.. _sounddevice: https://python-sounddevice.readthedocs.io/
.. _CFFI: https://cffi.readthedocs.io/
