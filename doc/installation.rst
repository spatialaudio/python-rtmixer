Installation
============

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
