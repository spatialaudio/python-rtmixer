"""Reliable low-latency audio playback and recording."""

__version__ = '0.0.0'

import sounddevice as _sd
from pa_ringbuffer import init as _init_ringbuffer
from _rtmixer import ffi as _ffi, lib as _lib
RingBuffer = _init_ringbuffer(_ffi, _lib)


class _Base(_sd._StreamBase):
    """Base class for Mixer et al."""

    def __init__(self, kind, qsize=16, **kwargs):
        callback = _ffi.addressof(_lib, 'callback')

        self._action_q = RingBuffer(_ffi.sizeof('struct action*'), qsize)
        self._result_q = RingBuffer(_ffi.sizeof('struct action*'), qsize)
        self._state = _ffi.new('struct state*', dict(
            input_channels=0,
            output_channels=0,
            samplerate=0,
            action_q=self._action_q.ptr,
            result_q=self._result_q.ptr,
            actions=_ffi.NULL,
        ))
        _sd._StreamBase.__init__(
            self, kind=kind, dtype='float32',
            callback=callback, userdata=self._state, **kwargs)
        self._state.samplerate = self.samplerate

        self._actions = set()
        self._temp_action_ptr = _ffi.new('struct action**')

    @property
    def actions(self):
        """The set of active "actions"."""
        self._drain_result_q()
        return self._actions

    def cancel(self, action, time=0, allow_belated=True):
        """Initiate stopping a running action.

        This creates another action that is sent to the callback in
        order to stop the given *action*.

        This function typically returns before the *action* is actually
        stopped.  Use `wait()` to wait until it's done.

        """
        cancel_action = _ffi.new('struct action*', dict(
            type=_lib.CANCEL,
            allow_belated=allow_belated,
            requested_time=time,
            action=action,
        ))
        self._enqueue(cancel_action)
        return cancel_action

    def wait(self, action, sleeptime=10):
        """Wait for *action* to be finished.

        Between repeatedly checking if the action is finished, this
        waits for *sleeptime* milliseconds.

        """
        while action in self.actions:
            _sd.sleep(sleeptime)

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

    def _enqueue(self, action):
        self._drain_result_q()
        self._temp_action_ptr[0] = action
        ret = self._action_q.write(self._temp_action_ptr)
        if ret != 1:
            raise RuntimeError('Action queue is full')
        self._actions.add(action)

    def _drain_result_q(self):
        """Get actions from the result queue and discard them."""
        while self._result_q.read(self._temp_action_ptr):
            try:
                self._actions.remove(self._temp_action_ptr[0])
            except KeyError:
                assert False


class Mixer(_Base):
    """PortAudio output stream for realtime mixing."""

    def __init__(self, **kwargs):
        """Create a realtime mixer object.

        Takes the same keyword arguments as `sounddevice.OutputStream`,
        except *callback* and *dtype*.

        Uses default values from `sounddevice.default`.

        """
        _Base.__init__(self, kind='output', **kwargs)
        self._state.output_channels = self.channels

    def play_buffer(self, buffer, channels, start=0, allow_belated=True):
        """Send a buffer to the callback to be played back.

        After that, the *buffer* must not be written to anymore.

        """
        channels, mapping = self._check_channels(channels, 'output')
        buffer = _ffi.from_buffer(buffer)
        _, samplesize = _sd._split(self.samplesize)
        action = _ffi.new('struct action*', dict(
            type=_lib.PLAY_BUFFER,
            allow_belated=allow_belated,
            requested_time=start,
            buffer=_ffi.cast('float*', buffer),
            total_frames=len(buffer) // channels // samplesize,
            channels=channels,
            mapping=mapping,
        ))
        self._enqueue(action)
        return action

    def play_ringbuffer(self, ringbuffer, channels=None, start=0,
                        allow_belated=True):
        """Send a ring buffer to the callback to be played back.

        By default, the number of channels is obtained from the ring
        buffer's *elementsize*.

        """
        _, samplesize = _sd._split(self.samplesize)
        if channels is None:
            channels = ringbuffer.ptr.elementSizeBytes // samplesize
        channels, mapping = self._check_channels(channels, 'output')
        if ringbuffer.ptr.elementSizeBytes != samplesize * channels:
            raise ValueError('Incompatible elementsize')
        action = _ffi.new('struct action*', dict(
            type=_lib.PLAY_RINGBUFFER,
            allow_belated=allow_belated,
            requested_time=start,
            ringbuffer=ringbuffer.ptr,
            total_frames=_lib.ULONG_MAX,
            channels=channels,
            mapping=mapping,
        ))
        self._enqueue(action)
        return action


class Recorder(_Base):
    """PortAudio input stream for realtime recording."""

    def __init__(self, **kwargs):
        """Create a realtime recording object.

        Takes the same keyword arguments as `sounddevice.InputStream`,
        except *callback* and *dtype*.

        Uses default values from `sounddevice.default`.

        """
        _Base.__init__(self, kind='input', **kwargs)
        self._state.input_channels = self.channels

    def record_buffer(self, buffer, channels, start=0, allow_belated=True):
        """Send a buffer to the callback to be recorded into.

        """
        channels, mapping = self._check_channels(channels, 'input')
        buffer = _ffi.from_buffer(buffer)
        samplesize, _ = _sd._split(self.samplesize)
        action = _ffi.new('struct action*', dict(
            type=_lib.RECORD_BUFFER,
            allow_belated=allow_belated,
            requested_time=start,
            buffer=_ffi.cast('float*', buffer),
            total_frames=len(buffer) // channels // samplesize,
            channels=channels,
            mapping=mapping,
        ))
        self._enqueue(action)
        return action

    def record_ringbuffer(self, ringbuffer, channels=None, start=0,
                          allow_belated=True):
        """Send a ring buffer to the callback to be recorded into.

        By default, the number of channels is obtained from the ring
        buffer's *elementsize*.

        """
        samplesize, _ = _sd._split(self.samplesize)
        if channels is None:
            channels = ringbuffer.ptr.elementSizeBytes // samplesize
        channels, mapping = self._check_channels(channels, 'input')
        if ringbuffer.ptr.elementSizeBytes != samplesize * channels:
            raise ValueError('Incompatible elementsize')
        action = _ffi.new('struct action*', dict(
            type=_lib.RECORD_RINGBUFFER,
            allow_belated=allow_belated,
            requested_time=start,
            ringbuffer=ringbuffer.ptr,
            total_frames=_lib.ULONG_MAX,
            channels=channels,
            mapping=mapping,
        ))
        self._enqueue(action)
        return action


class MixerAndRecorder(Mixer, Recorder):
    """PortAudio stream for realtime mixing and recording."""

    def __init__(self, **kwargs):
        """Create a realtime mixer object with recording capabilities.

        Takes the same keyword arguments as `sounddevice.Stream`,
        except *callback* and *dtype*.

        Uses default values from `sounddevice.default`.

        """
        _Base.__init__(self, kind='duplex', **kwargs)
        self._state.input_channels = self.channels[0]
        self._state.output_channels = self.channels[1]
