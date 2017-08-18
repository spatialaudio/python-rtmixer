#!/usr/bin/env python3
"""Example that shows how to use fetch_and_reset_stats().

"""
import rtmixer
import sounddevice as sd


blocksize = 0
latency = 0
device = None
samplerate = None
channels = 1


def print_stats(obj):
    print('  blocks:', obj.stats.blocks)
    print('  overflows:', obj.stats.input_overflows)


stream = rtmixer.Recorder(
    device=device, channels=channels, blocksize=blocksize,
    latency=latency, samplerate=samplerate)

buffer = bytearray(10 * int(stream.samplerate) * stream.samplesize)
ringbuffer = rtmixer.RingBuffer(stream.samplesize * channels, 128)

print('checking stats before opening stream:')
print_stats(stream)
assert stream.stats.blocks == 0
assert stream.stats.input_overflows == 0

with stream:
    print('waiting a few seconds')
    sd.sleep(3 * 1000)
    print('checking stats:')
    action = stream.fetch_and_reset_stats()
    stream.wait(action)
    print_stats(action)
    print('starting recording to buffer')
    action = stream.record_buffer(buffer, channels=channels)
    # TODO: check if recording started successfully
    stream.wait(action)
    print('stats from finished recording:')
    print_stats(action)
    print('starting recording to ringbuffer')
    action = stream.record_ringbuffer(ringbuffer, channels=channels)
    # TODO: check if recording started successfully
    # TODO: record ringbuffer, but don't read from it (detect overflow)
    sd.sleep(3 * 1000)
    print('checking stats:')
    action = stream.fetch_and_reset_stats()
    stream.wait(action)
    print_stats(action)

print('checking stats after closing stream:')
print_stats(stream)
