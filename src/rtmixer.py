"""Reliable low-latency audio playback and recording."""
__version__ = '0.0.0'

import sounddevice as _sd
from _rtmixer import ffi as _ffi, lib as _lib


class _Base(_sd._StreamBase):
    """Base class for Mixer et al."""

    def __init__(self, kind, **kwargs):
        callback = _ffi.addressof(_lib, 'callback')

        # TODO: parameter for ring buffer size
        self._action_q = RingBuffer(_ffi.sizeof('struct action*'), 512)
        self._userdata = _ffi.new('struct state*', dict(
            action_q=self._action_q._ptr,
        ))
        _sd._StreamBase.__init__(
            self, kind=kind, dtype='float32',
            callback=callback, userdata=self._userdata, **kwargs)
        self._userdata.samplerate = self.samplerate

        self._actions = []

    def _check_channels(self, channels, kind):
        """Check if number of channels or mapping was given."""
        assert kind in ('input', 'output')
        try:
            channels, mapping = len(channels), channels
        except TypeError:
            mapping = tuple(range(1, channels + 1))
        max_channels = _sd._split(self.channels)[kind == 'output']
        if max(mapping) > max_channels:
            raise ValueError('Channel number too large')
        if min(mapping) < 1:
            raise ValueError('Channel numbers start with 1')
        return channels, mapping


class Mixer(_Base):
    """PortAudio output stream for realtime mixing."""

    def __init__(self, **kwargs):
        """Create a realtime mixer object.

        Takes the same keyword arguments as `sounddevice.OutputStream`,
        except *callback* and *dtype*.

        Uses default values from `sounddevice.default`.

        """
        _Base.__init__(self, kind='output', **kwargs)
        self._userdata.input_channels = 0
        self._userdata.output_channels = self.channels

    def play_buffer(self, buffer, channels, start=0):
        """Send a buffer to the callback to be played back.

        After that, the *buffer* must not be written to anymore.

        """
        # TODO: drain result_q?
        channels, mapping = self._check_channels(channels, 'output')
        buffer = _ffi.from_buffer(buffer)
        _, samplesize = _sd._split(self.samplesize)
        action = _ffi.new('struct action*', dict(
            actiontype=_lib.PLAY_BUFFER,
            requested_time=start,
            # Cast to float* to allow playing bytes objects:
            buffer=_ffi.cast('float*', buffer),
            total_frames=len(buffer) // channels // samplesize,
            channels=channels,
            mapping=mapping,
        ))
        # TODO: avoid code duplication with other functions:
        if not self._action_q.write_available:
            raise RuntimeError('Action queue is full!')
        ret = self._action_q.write(_ffi.new('struct action**', action))
        assert ret == 1
        self._actions.append(action)  # TODO: Better way to keep alive?

    def play_ringbuffer(self, ringbuffer, channels=None, start=0):
        """Send a ring buffer to the callback to be played back.

        By default, the number of channels is obtained from the ring
        buffer's *elementsize*.

        """
        # TODO: drain result_q?
        _, samplesize = _sd._split(self.samplesize)
        if channels is None:
            channels = ringbuffer.elementsize // samplesize
        channels, mapping = self._check_channels(channels, 'output')
        if ringbuffer.elementsize != samplesize * channels:
            raise ValueError('Incompatible elementsize')
        action = _ffi.new('struct action*', dict(
            actiontype=_lib.PLAY_RINGBUFFER,
            requested_time=start,
            ringbuffer=ringbuffer._ptr,
            channels=channels,
            mapping=mapping,
        ))
        if not self._action_q.write_available:
            raise RuntimeError('Action queue is full!')
        ret = self._action_q.write(_ffi.new('struct action**', action))
        assert ret == 1
        self._actions.append(action)  # TODO: Better way to keep alive?
        # TODO: block until playback has finished (optional)?
        # TODO: return something that allows stopping playback?


class Recorder(_Base):
    """PortAudio input stream for realtime recording."""

    def __init__(self, **kwargs):
        """Create a realtime recording object.

        Takes the same keyword arguments as `sounddevice.InputStream`,
        except *callback* and *dtype*.

        Uses default values from `sounddevice.default`.

        """
        _Base.__init__(self, kind='input', **kwargs)
        self._userdata.input_channels = self.channels
        self._userdata.output_channels = 0

    def record_buffer(self, buffer, channels, start=0):
        """Send a buffer to the callback to be recorded into.

        """
        # TODO: drain result_q?
        channels, mapping = self._check_channels(channels, 'input')
        buffer = _ffi.from_buffer(buffer)
        samplesize, _ = _sd._split(self.samplesize)
        action = _ffi.new('struct action*', dict(
            actiontype=_lib.RECORD_BUFFER,
            requested_time=start,
            buffer=buffer,
            total_frames=len(buffer) // channels // samplesize,
            channels=channels,
            mapping=mapping,
        ))
        if not self._action_q.write_available:
            raise RuntimeError('Action queue is full!')
        ret = self._action_q.write(_ffi.new('struct action**', action))
        assert ret == 1
        self._actions.append(action)  # TODO: Better way to keep alive?

    def record_ringbuffer(self, ringbuffer, channels=None, start=0):
        """Send a ring buffer to the callback to be recorded into.

        By default, the number of channels is obtained from the ring
        buffer's *elementsize*.

        """
        # TODO: drain result_q?

        # TODO: avoid code duplication
        samplesize, _ = _sd._split(self.samplesize)
        if channels is None:
            channels = ringbuffer.elementsize // samplesize
        channels, mapping = self._check_channels(channels, 'input')
        if ringbuffer.elementsize != samplesize * channels:
            raise ValueError('Incompatible elementsize')
        action = _ffi.new('struct action*', dict(
            actiontype=_lib.RECORD_RINGBUFFER,
            requested_time=start,
            ringbuffer=ringbuffer._ptr,
            channels=channels,
            mapping=mapping,
        ))
        if not self._action_q.write_available:
            raise RuntimeError('Action queue is full!')
        ret = self._action_q.write(_ffi.new('struct action**', action))
        assert ret == 1
        self._actions.append(action)  # TODO: Better way to keep alive?
        # TODO: block until playback has finished (optional)?
        # TODO: return something that allows stopping playback?


class MixerAndRecorder(Mixer, Recorder):
    """PortAudio stream for realtime mixing and recording."""


class RingBuffer(object):
    """Wrapper for PortAudio's ring buffer.

    See __init__().

    """

    def __init__(self, elementsize, size):
        """Create an instance of PortAudio's ring buffer.

        Parameters
        ----------
        elementsize : int
            The size of a single data element in bytes.
        size : int
            The number of elements in the buffer (must be a power of 2).

        """
        self._ptr = _ffi.new('PaUtilRingBuffer*')
        self._data = _ffi.new('unsigned char[]', size * elementsize)
        res = _lib.PaUtil_InitializeRingBuffer(
            self._ptr, elementsize, size, self._data)
        if res != 0:
            assert res == -1
            raise ValueError('size must be a power of 2')
        assert self._ptr.bufferSize == size
        assert self._ptr.elementSizeBytes == elementsize

    def flush(self):
        """Reset buffer to empty.

        Should only be called when buffer is NOT being read or written.

        """
        _lib.PaUtil_FlushRingBuffer(self._ptr)

    @property
    def write_available(self):
        """Number of elements available in the ring buffer for writing."""
        return _lib.PaUtil_GetRingBufferWriteAvailable(self._ptr)

    @property
    def read_available(self):
        """Number of elements available in the ring buffer for reading."""
        return _lib.PaUtil_GetRingBufferReadAvailable(self._ptr)

    def write(self, data, size=-1):
        """Write data to the ring buffer.

        Parameters
        ----------
        data : CData pointer or buffer or bytes
            Data to write to the buffer.
        size : int, optional
            The number of elements to be written.

        Returns
        -------
        int
            The number of elements written.

        """
        try:
            data = _ffi.from_buffer(data)
        except TypeError:
            pass  # input is not a buffer
        if size < 0:
            size, rest = divmod(_ffi.sizeof(data), self._ptr.elementSizeBytes)
            if rest:
                raise ValueError('data size must be multiple of elementsize')
        return _lib.PaUtil_WriteRingBuffer(self._ptr, data, size)

    def read(self, data, size=-1):
        """Read data from the ring buffer.

        Parameters
        ----------
        data : CData pointer or buffer
            The memory where the data should be stored.
        size : int, optional
            The number of elements to be read.

        Returns
        -------
        int
            The number of elements read.

        """
        try:
            data = _ffi.from_buffer(data)
        except TypeError:
            pass  # input is not a buffer
        if size < 0:
            size, rest = divmod(len(data), self._ptr.elementSizeBytes)
            if rest:
                raise ValueError('data size must be multiple of elementsize')
        return _lib.PaUtil_ReadRingBuffer(self._ptr, data, size)

    def get_write_buffers(self, size):
        """Get buffer(s) to which we can write data.

        Parameters
        ----------
        size : int
            The number of elements desired.

        Returns
        -------
        int
            The room available to be written or the given *size*,
            whichever is smaller.
        buffer
            The first buffer.
        buffer
            The second buffer.

        """
        ptr1 = _ffi.new('void**')
        ptr2 = _ffi.new('void**')
        size1 = _ffi.new('ring_buffer_size_t*')
        size2 = _ffi.new('ring_buffer_size_t*')
        return (_lib.PaUtil_GetRingBufferWriteRegions(
                    self._ptr, size, ptr1, size1, ptr2, size2),
                _ffi.buffer(ptr1[0], size1[0] * self.elementsize),
                _ffi.buffer(ptr2[0], size2[0] * self.elementsize))

    def advance_write_index(self, size):
        """Advance the write index to the next location to be written.

        Parameters
        ----------
        size : int
            The number of elements to advance.

        Returns
        -------
        int
            The new position.

        """
        return _lib.PaUtil_AdvanceRingBufferWriteIndex(self._ptr, size)

    def get_read_buffers(self, size):
        """Get buffer(s) from which we can read data.

        Parameters
        ----------
        size : int
            The number of elements desired.

        Returns
        -------
        int
            The number of elements available for reading.
        buffer
            The first buffer.
        buffer
            The second buffer.

        """
        ptr1 = _ffi.new('void**')
        ptr2 = _ffi.new('void**')
        size1 = _ffi.new('ring_buffer_size_t*')
        size2 = _ffi.new('ring_buffer_size_t*')
        return (_lib.PaUtil_GetRingBufferReadRegions(
                    self._ptr, size, ptr1, size1, ptr2, size2),
                _ffi.buffer(ptr1[0], size1[0] * self.elementsize),
                _ffi.buffer(ptr2[0], size2[0] * self.elementsize))

    def advance_read_index(self, size):
        """Advance the read index to the next location to be read.

        Parameters
        ----------
        size : int
            The number of elements to advance.

        Returns
        -------
        int
            The new position.

        """
        return _lib.PaUtil_AdvanceRingBufferReadIndex(self._ptr, size)

    @property
    def elementsize(self):
        """Element size in bytes."""
        return self._ptr.elementSizeBytes
