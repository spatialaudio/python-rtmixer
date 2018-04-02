#!/usr/bin/env python3
"""Play back whatever comes in, with a given delay."""
import math
import rtmixer

delay = 1.5
channels = 1
blocksize = 0
latency = 'low'
samplerate = 48000
safety = 0.001  # Increase if Python interpreter is slow

rb_size = 2**math.ceil(math.log2(delay * samplerate))

stream = rtmixer.MixerAndRecorder(
    channels=channels, blocksize=blocksize, samplerate=samplerate,
    latency=latency)
with stream:
    samplesize = 4
    assert {samplesize} == set(stream.samplesize)
    print('  input latency:', stream.latency[0])
    print(' output latency:', stream.latency[1])
    print('            sum:', sum(stream.latency))
    print('requested delay:', delay)
    rb = rtmixer.RingBuffer(samplesize * channels, rb_size)
    start = stream.time + safety
    record_action = stream.record_ringbuffer(rb, start=start,
                                             allow_belated=False)
    play_action = stream.play_ringbuffer(rb, start=start + delay,
                                         allow_belated=False)
    # Dummy recording to wait until "start" has passed:
    stream.wait(stream.record_buffer(b'', channels=1, start=start))
    if record_action not in stream.actions:
        if record_action.actual_time == 0:
            raise RuntimeError('Increase "safety"')
        else:
            # TODO: could there be another error?
            raise RuntimeError('Ring buffer overflow (increase "delay"?)')
    # Dummy playback to wait until "start + delay" has passed:
    stream.wait(stream.play_buffer(b'', channels=1, start=start + delay))
    if play_action not in stream.actions:
        if play_action.actual_time == 0:
            raise RuntimeError('Increase "safety" or "delay"')
        else:
            # TODO: could there be another error?
            raise RuntimeError('Ring buffer underflow (increase "delay"?)')
    print('#' * 80)
    print('press Return to quit')
    print('#' * 80)
    input()
print('input underflows:', stream.stats.input_underflows)
print('input overflows:', stream.stats.input_overflows)
print('output underflows:', stream.stats.output_underflows)
