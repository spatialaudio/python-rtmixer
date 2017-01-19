#!/usr/bin/env python3

from __future__ import division  # Only needed for Python 2.x
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

buffer = np.zeros([int(duration * samplerate), channels],
                  dtype='float32', order='C')
t = np.arange(len(buffer)) / samplerate
t += start

with rtmixer.Recorder(channels=channels, blocksize=blocksize,
                      samplerate=samplerate, latency=latency) as m:
    start += m.time
    m.record_buffer(buffer, channels, start)
    time.sleep(max(start - m.time, 0))
    print('Recording ... ', end='', flush=True)
    # TODO: wait for recording to actually finish
    time.sleep(max(start + duration - m.time, 0))
    print('done')
    # TODO: check for xruns

plt.plot(t, buffer)
plt.xlabel('Time / seconds')
plt.show()
