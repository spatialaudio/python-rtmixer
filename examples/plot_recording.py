#!/usr/bin/env python3

import time

import matplotlib.pyplot as plt
import numpy as np
import rtmixer

channels = 1
start = 3.5
duration = 3
samplerate = 48000
blocksize = 0
latency = 'low'
sleeptime = 0.1

buffer = np.zeros([int(duration * samplerate), channels],
                  dtype='float32', order='C')
t = np.arange(len(buffer)) / samplerate
t += start

with rtmixer.Recorder(channels=channels, blocksize=blocksize,
                      samplerate=samplerate, latency=latency) as m:
    start += m.time
    action = m.record_buffer(buffer, channels, start)
    try:
        while True:
            remaining = start - m.time
            if remaining < sleeptime:
                break
            if remaining % 1 < sleeptime:
                tick = int(remaining)
            else:
                tick = '.'
            print(tick, end='', flush=True)
            time.sleep(sleeptime)
        print(' recording! (press Ctrl+C to stop)', end='', flush=True)
        while action in m.actions:
            print('.', end='', flush=True)
            time.sleep(sleeptime)
        print(' done.')
    except KeyboardInterrupt:
        m.cancel(action)
        print(' canceled.')
        m.wait(action)
        buffer = buffer[:action.done_frames]
        t = t[:action.done_frames]

print('Input overflows during recording:', action.stats.input_overflows)

if len(buffer):
    plt.plot(t, buffer)
    plt.xlabel('Time / seconds')
    plt.show()
else:
    print('Nothing was recorded.')
