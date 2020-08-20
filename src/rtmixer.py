"""Reliable low-latency audio playback and recording.

https://python-rtmixer.readthedocs.io/

"""
__version__ = '0.1.2'

import sounddevice as _sd
from pa_ringbuffer import init as _init_ringbuffer
from _rtmixer import ffi as _ffi, lib as _lib
RingBuffer = _init_ringbuffer(_ffi, _lib)


# Get constants from C library
for _k, _v in vars(_lib).items():
    if _k.isupper():
        globals()[_k] = _v


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
            action_q=self._action_q._ptr,
            result_q=self._result_q._ptr,
            actions=_ffi.NULL,
        ))
        _sd._StreamBase.__init__(
            self, kind=kind, dtype='float32',
            callback=callback, userdata=self._state, **kwargs)
        self._state.samplerate = self.samplerate

        self._actions = {}
        self._temp_action_ptr = _ffi.new('struct action**')

    @property
    def actions(self):
        """The set of active "actions"."""
        self._drain_result_q()
        return self._actions.keys()

    @property
    def stats(self):
        """Get over-/underflow statistics from an *inactive* stream.

        To get statistics from an :attr:`~sounddevice.Stream.active`
        stream, use `fetch_and_reset_stats()`.

        """
        if self.active:
            raise RuntimeError('Accessing .stats on an active stream')
        return _ffi.new('struct stats*', self._state.stats)

    def cancel(self, action, time=0, allow_belated=True):
        """Initiate stopping a running action.

        This creates another action that is sent to the callback in
        order to stop the given *action*.

        This function typically returns before the *action* is actually
        stopped.  Use `wait()` (on either one of the two actions) to
        wait until it's done.

        """
        cancel_action = _ffi.new('struct action*', dict(
            type=CANCEL,
            allow_belated=allow_belated,
            requested_time=time,
            action=action,
        ))
        self._enqueue(cancel_action)
        return cancel_action

    def fetch_and_reset_stats(self, time=0, allow_belated=True):
        """Fetch and reset over-/underflow statistics of the stream.

        """
        action = _ffi.new('struct action*', dict(
            type=FETCH_AND_RESET_STATS,
            allow_belated=allow_belated,
            requested_time=time,
        ))
        self._enqueue(action)
        return action

    def wait(self, action=None, sleeptime=10):
        """Wait for *action* to be finished.

        Between repeatedly checking if the action is finished, this
        waits for *sleeptime* milliseconds.

        If no *action* is given, this waits for all actions.

        """
        if action is None:
            while self.actions:
                _sd.sleep(sleeptime)
        else:
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

    def _enqueue(self, action, keep_alive=None):
        self._drain_result_q()
        self._temp_action_ptr[0] = action
        ret = self._action_q.write(self._temp_action_ptr)
        if ret != 1:
            raise RuntimeError('Action queue is full')
        assert action not in self._actions
        self._actions[action] = keep_alive

    def _drain_result_q(self):
        """Get actions from the result queue and discard them."""
        while self._result_q.readinto(self._temp_action_ptr):
            try:
                del self._actions[self._temp_action_ptr[0]]
            except KeyError:
                assert False


class Mixer(_Base):
    """PortAudio output stream for realtime mixing.

    Takes the same keyword arguments as `sounddevice.OutputStream`,
    except *callback* (a callback function implemented in C is used
    internally) and *dtype* (which is always ``'float32'``).

    Uses default values from `sounddevice.default` (except *dtype*,
    which is always ``'float32'``).

    Has the same methods and attributes as `sounddevice.OutputStream`
    (except :meth:`~sounddevice.Stream.write` and
    :attr:`~sounddevice.Stream.write_available`), plus the following:

    """

    def __init__(self, **kwargs):
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
            type=PLAY_BUFFER,
            allow_belated=allow_belated,
            requested_time=start,
            buffer=_ffi.cast('float*', buffer),
            total_frames=len(buffer) // channels // samplesize,
            channels=channels,
            mapping=mapping,
        ))
        self._enqueue(action, keep_alive=buffer)
        return action

    def play_ringbuffer(self, ringbuffer, channels=None, start=0,
                        allow_belated=True):
        """Send a `RingBuffer` to the callback to be played back.

        By default, the number of channels is obtained from the ring
        buffer's :attr:`~RingBuffer.elementsize`.

        """
        _, samplesize = _sd._split(self.samplesize)
        if channels is None:
            channels = ringbuffer.elementsize // samplesize
        channels, mapping = self._check_channels(channels, 'output')
        if ringbuffer.elementsize != samplesize * channels:
            raise ValueError('Incompatible elementsize')
        action = _ffi.new('struct action*', dict(
            type=PLAY_RINGBUFFER,
            allow_belated=allow_belated,
            requested_time=start,
            ringbuffer=ringbuffer._ptr,
            total_frames=ULONG_MAX,
            channels=channels,
            mapping=mapping,
        ))
        self._enqueue(action, keep_alive=ringbuffer)
        return action


class Recorder(_Base):
    """PortAudio input stream for realtime recording.

    Takes the same keyword arguments as `sounddevice.InputStream`,
    except *callback* (a callback function implemented in C is used
    internally) and *dtype* (which is always ``'float32'``).

    Uses default values from `sounddevice.default` (except *dtype*,
    which is always ``'float32'``).

    Has the same methods and attributes as `Mixer`, except that
    `play_buffer()` and `play_ringbuffer()` are replaced by:

    """

    def __init__(self, **kwargs):
        _Base.__init__(self, kind='input', **kwargs)
        self._state.input_channels = self.channels

    def record_buffer(self, buffer, channels, start=0, allow_belated=True):
        """Send a buffer to the callback to be recorded into.

        """
        channels, mapping = self._check_channels(channels, 'input')
        buffer = _ffi.from_buffer(buffer)
        samplesize, _ = _sd._split(self.samplesize)
        action = _ffi.new('struct action*', dict(
            type=RECORD_BUFFER,
            allow_belated=allow_belated,
            requested_time=start,
            buffer=_ffi.cast('float*', buffer),
            total_frames=len(buffer) // channels // samplesize,
            channels=channels,
            mapping=mapping,
        ))
        self._enqueue(action, keep_alive=buffer)
        return action

    def record_ringbuffer(self, ringbuffer, channels=None, start=0,
                          allow_belated=True):
        """Send a `RingBuffer` to the callback to be recorded into.

        By default, the number of channels is obtained from the ring
        buffer's :attr:`~RingBuffer.elementsize`.

        """
        samplesize, _ = _sd._split(self.samplesize)
        if channels is None:
            channels = ringbuffer.elementsize // samplesize
        channels, mapping = self._check_channels(channels, 'input')
        if ringbuffer.elementsize != samplesize * channels:
            raise ValueError('Incompatible elementsize')
        action = _ffi.new('struct action*', dict(
            type=RECORD_RINGBUFFER,
            allow_belated=allow_belated,
            requested_time=start,
            ringbuffer=ringbuffer._ptr,
            total_frames=ULONG_MAX,
            channels=channels,
            mapping=mapping,
        ))
        self._enqueue(action, keep_alive=ringbuffer)
        return action


class MixerAndRecorder(Mixer, Recorder):
    """PortAudio stream for realtime mixing and recording.

    Takes the same keyword arguments as `sounddevice.Stream`, except
    *callback* (a callback function implemented in C is used internally)
    and *dtype* (which is always ``'float32'``).

    Uses default values from `sounddevice.default` (except *dtype*,
    which is always ``'float32'``).

    Inherits all methods and attributes from `Mixer` and `Recorder`.

    """

    def __init__(self, **kwargs):
        _Base.__init__(self, kind='duplex', **kwargs)
        self._state.input_channels = self.channels[0]
        self._state.output_channels = self.channels[1]
