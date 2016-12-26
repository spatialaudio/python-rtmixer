import sounddevice as _sd
from _rtmixer import ffi as _ffi, lib as _lib


class RtMixer(_sd.Stream):

    def __init__(self, **kwargs):
        callback = _ffi.addressof(_lib, 'callback')
        super(RtMixer, self).__init__(callback=callback, **kwargs)
