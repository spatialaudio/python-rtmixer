#!/usr/bin/env python3
"""Play back whatever comes in, with a given delay."""
import math
import rtmixer

delay = 1.5
channels = 1
blocksize = 0
latency = 'low'
samplerate = 48000
safety = 0.1  # Shouldn't be less than the duration of an audio block

rb_size = 2**math.ceil(math.log2((delay + safety) * samplerate))

stream = rtmixer.MixerAndRecorder(
    channels=channels, blocksize=blocksize, samplerate=samplerate,
    latency=latency)
with stream:
    samplesize = 4
    assert {samplesize} == set(stream.samplesize)
    rb = rtmixer.RingBuffer(samplesize * channels, rb_size)
    start = stream.time + safety
    stream.record_ringbuffer(rb, start=start, allow_belated=False)
    stream.play_ringbuffer(rb, start=start + delay, allow_belated=False)
    # TODO: check if start was successful
    print('#' * 80)
    print('press Return to quit')
    print('#' * 80)
    input()
print('input underflows:', stream.stats.input_underflows)
print('input overflows:', stream.stats.input_overflows)
print('output underflows:', stream.stats.output_underflows)
