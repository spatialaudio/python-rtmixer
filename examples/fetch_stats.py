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
    print('blocks (min/max): {} ({}/{})'.format(
        obj.stats.blocks, obj.stats.min_blocksize, obj.stats.max_blocksize))
    print('       overflows:', obj.stats.input_overflows)


def print_action(action):
    print('            type:', next(
        k for k, v in vars(rtmixer).items() if v == action.type))
    print('  requested time:', action.requested_time)
    print('     actual time:', action.actual_time)
    print('    total frames:', action.total_frames)
    print('     done frames:', action.done_frames)


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
    print('waiting a few seconds ...')
    sd.sleep(3 * 1000)
    print('checking stats:')
    action = stream.fetch_and_reset_stats()
    stream.wait(action)
    print_stats(action)
    print('starting recording to buffer ...')
    action = stream.record_buffer(buffer, channels=channels)
    stream.wait(action)
    print('result:')
    print_action(action)
    print('stats from finished recording:')
    print_stats(action)
    print('starting recording to ringbuffer ...')
    action = stream.record_ringbuffer(ringbuffer, channels=channels)
    # NB: We are writing to the ringbuffer, but we are not reading from it,
    # which will lead to an overflow
    print('waiting for ring buffer to fill up ...')
    stream.wait(action)
    print('result:')
    print_action(action)
    print('recording was stopped because of ringbuffer overflow:',
          action.done_frames != action.total_frames)
    print('checking stats:')
    action = stream.fetch_and_reset_stats()
    stream.wait(action)
    print_stats(action)

print('checking stats after closing stream:')
print_stats(stream)
