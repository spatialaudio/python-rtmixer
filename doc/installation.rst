Installation
============

On Windows, macOS and Linux you can install a precompiled "wheel" package with::

    python3 -m pip install rtmixer

This will install ``rtmixer`` and its dependencies, including ``sounddevice``.

Depending on your Python installation,
you may have to use ``python`` instead of ``python3``.
If you have installed the module already,
you can use the ``--upgrade`` flag to get the newest release.
    
.. note:: On Linux, to use ``sounddevice`` and ``rtmixer`` you will need to
          have PortAudio installed, e.g. via ``sudo apt install libportaudio2``.
          On other platforms, PortAudio comes bundled with ``sounddevice``.
