#!/usr/bin/env python3
"""How to do "live" signal processing with ring buffers."""
import math
import time

import numpy as np
import rtmixer

device = None
latency = 'low'
samplerate = 48000
channels = 1
sleeptime = 0.001  # To avoid busy-waiting
dsp_size = 4096
# Simulated processing time in seconds:
dsp_duration = 0.8 * (dsp_size / samplerate)
# Buffer for hypothetical fixed-blocksize DSP algorithm:
dsp_buffer = np.zeros((dsp_size, channels), dtype='float32')
dsp_calls = 0

# This value adds to the overall latency
pre_filling = 2 * dsp_size


def hypothetical_dsp_algorithm(buffer):
    assert len(buffer) == dsp_size
    time.sleep(dsp_duration)
    global dsp_calls
    dsp_calls += 1


def nextpow2(x):
    return 2**math.ceil(math.log2(x))


buffersize_in = nextpow2(0.5 * samplerate)
buffersize_out = nextpow2(0.5 * samplerate)

stream = rtmixer.MixerAndRecorder(
    device=device, channels=channels, blocksize=0, latency=latency,
    samplerate=samplerate)

print('  input latency:', stream.latency[0])
print(' output latency:', stream.latency[1])
print('            sum:', sum(stream.latency))
print('       DSP size:', dsp_size)

samplesize = 4
assert stream.dtype == ('float32', 'float32')
assert stream.samplesize == (samplesize, samplesize)

q_in = rtmixer.RingBuffer(samplesize * channels, buffersize_in)
q_out = rtmixer.RingBuffer(samplesize * channels, buffersize_out)

# Pre-fill output queue:
q_out.write(np.zeros((pre_filling, channels), dtype='float32'))

try:
    with stream:
        assert dsp_buffer.dtype == 'float32'
        assert dsp_buffer.flags.c_contiguous
        record_action = stream.record_ringbuffer(q_in)
        play_action = stream.play_ringbuffer(q_out)
        print('=== Start Processing')
        while True:
            while (q_in.read_available < dsp_size
                   and record_action in stream.actions):
                time.sleep(sleeptime)
            if record_action not in stream.actions:
                raise RuntimeError('Input ringbuffer overflow')
            frames = q_in.readinto(dsp_buffer)
            assert frames == dsp_size

            hypothetical_dsp_algorithm(dsp_buffer)

            while (q_out.write_available < dsp_size
                   and play_action in stream.actions):
                time.sleep(sleeptime)
            if play_action not in stream.actions:
                raise RuntimeError('Output ringbuffer underflow')
            frames = q_out.write(dsp_buffer)
            assert frames == dsp_size
        print('=== Stop Processing')
except KeyboardInterrupt:
    print('\n=== Interrupted by User')
except RuntimeError as e:
    print('=== Error:', e)

print('  recorded blocks:', record_action.stats.blocks)
print('    played blocks:', play_action.stats.blocks)
print('        DSP calls:', dsp_calls)
print(' input underflows:', stream.stats.input_underflows)
print(' input  overflows:', stream.stats.input_overflows)
print('output underflows:', stream.stats.output_underflows)
print('output  overflows:', stream.stats.output_overflows)
