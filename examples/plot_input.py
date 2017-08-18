#!/usr/bin/env python3
"""Plot the live microphone signal(s) with matplotlib.

Matplotlib and NumPy have to be installed.

"""
import math
from matplotlib.animation import FuncAnimation
import matplotlib.pyplot as plt
import numpy as np
import rtmixer
import sounddevice as sd


window = 200  # ms
interval = 30  # ms
blocksize = 0
latency = 'low'
device = None
samplerate = None
downsample = 10  # Plot every ...th frame
qsize = 8  # Power of 2
channels = 2


def update_plot(frame):
    global plotdata
    while q.read_available >= stepsize:
        # The ring buffer's size is a multiple of stepsize, therefore we know
        # that the data is contiguous in memory (= the 2nd buffer is empty):
        read, buf1, buf2 = q.get_read_buffers(stepsize)
        assert read == stepsize
        assert not buf2
        buffer = np.frombuffer(buf1, dtype='float32')
        buffer.shape = -1, channels
        buffer = buffer[::downsample]
        # BTW, "buffer" still uses the ring buffer's memory:
        assert buffer.base.base == buf1
        shift = len(buffer)
        plotdata = np.roll(plotdata, -shift, axis=0)
        plotdata[-shift:, :] = buffer
        q.advance_read_index(stepsize)
    for column, line in enumerate(lines):
        line.set_ydata(plotdata[:, column])
    return lines


if samplerate is None:
    device_info = sd.query_devices(device, 'input')
    samplerate = device_info['default_samplerate']

length = int(window * samplerate / (1000 * downsample))
# Round down to a power of two:
stepsize = 2**int(math.log2(interval * samplerate / 1000))

plotdata = np.zeros((length, channels))

fig, ax = plt.subplots()
lines = ax.plot(plotdata)
if channels > 1:
    ax.legend(['channel {}'.format(c + 1) for c in range(channels)],
              loc='lower left', ncol=channels)
ax.axis((0, len(plotdata), -1, 1))
ax.set_yticks([0])
ax.yaxis.grid(True)
ax.tick_params(bottom='off', top='off', labelbottom='off',
               right='off', left='off', labelleft='off')
fig.tight_layout(pad=0)

stream = rtmixer.Recorder(
    device=device, channels=channels, blocksize=blocksize,
    latency=latency, samplerate=samplerate)
ani = FuncAnimation(fig, update_plot, interval=interval, blit=True)
with stream:
    elementsize = channels * stream.samplesize
    q = rtmixer.RingBuffer(elementsize, stepsize * qsize)
    action = stream.record_ringbuffer(q)
    plt.show()
# TODO: check for ringbuffer errors?
print('Input overflows:', action.stats.input_overflows)
