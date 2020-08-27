Installation
============

On Windows, macOS and Linux you can install a precompiled "wheel" package with::

    python3 -m pip install rtmixer --user

This will install ``rtmixer`` and its dependencies, including ``sounddevice``.

Depending on your Python installation,
you may have to use ``python`` instead of ``python3``.
If you want to install the module system-wide for all users
(assuming you have the necessary rights),
you should drop the ``--user`` flag.
If you are using a `virtual environment`_,
you should also drop the ``--user`` flag
(otherwise you'll get an error like
``ERROR: Can not perform a '--user' install.
User site-packages are not visible in this virtualenv.``).
If you have installed the module already,
you can use the ``--upgrade`` flag to get the newest release.
    
.. _`virtual environment`: https://docs.python.org/3/tutorial/venv.html

.. note:: On Linux, to use ``sounddevice`` and ``rtmixer`` you will need to
          have PortAudio installed, e.g. via ``sudo apt install libportaudio2``.
          On other platforms, PortAudio comes bundled with ``sounddevice``.
