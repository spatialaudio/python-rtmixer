#!/usr/bin/env python3
"""Play some random bleeps.

This example shows the feature of playing a buffer at a given absolute time.
Since all play_buffer() invocations are (deliberately) done at once, this puts
some strain on the "action queue".
The "qsize" has to be increased in order to handle this.

This example also shows that NumPy arrays can be used, as long as they are
C-contiguous and use the 'float32' data type.

"""

from __future__ import division  # Only needed for Python 2.x
import numpy as np
import rtmixer
import sounddevice as sd

seed = 99

device = None
blocksize = 0
latency = 'low'
samplerate = 44100

bleeps = 300
qsize = 512  # Must be a power of 2

attack = 0.005
release = 0.1
pitch_min = 40
pitch_max = 80
duration_min = 0.2
duration_max = 0.6
amplitude_min = 0.05
amplitude_max = 0.15
start_min = 0
start_max = 10
channels = None

if duration_min < max(attack, release):
    raise ValueError('minimum duration is too short')

fade_in = np.linspace(0, 1, num=int(samplerate * attack))
fade_out = np.linspace(1, 0, num=int(samplerate * release))

r = np.random.RandomState(seed)

bleeplist = []

if channels is None:
    channels = sd.default.channels['output']
    if channels is None:
        channels = sd.query_devices(device, 'output')['max_output_channels']

for _ in range(bleeps):
    duration = r.uniform(duration_min, duration_max)
    amplitude = r.uniform(amplitude_min, amplitude_max)
    pitch = r.uniform(pitch_min, pitch_max)
    # Convert MIDI pitch (https://en.wikipedia.org/wiki/MIDI_Tuning_Standard)
    frequency = 2 ** ((pitch - 69) / 12) * 440
    t = np.arange(int(samplerate * duration)) / samplerate
    bleep = amplitude * np.sin(2 * np.pi * frequency * t, dtype='float32')
    bleep[:len(fade_in)] *= fade_in
    bleep[-len(fade_out):] *= fade_out

    # Note: Arrays must be 32-bit float and C contiguous!
    assert bleep.dtype == 'float32'
    assert bleep.flags.c_contiguous
    bleeplist.append(bleep)

actionlist = []
with rtmixer.Mixer(device=device, channels=channels, blocksize=blocksize,
                   samplerate=samplerate, latency=latency, qsize=qsize) as m:
    start_time = m.time
    actionlist = [
        m.play_buffer(bleep,
                      channels=[r.randint(channels) + 1],
                      start=start_time + r.uniform(start_min, start_max),
                      allow_belated=False)
        for bleep in bleeplist
    ]
    while m.actions:
        sd.sleep(100)
print('{0} buffer underflows in {1} processed audio blocks'.format(
    m.stats.output_underflows, m.stats.blocks))

belated = 0
min_delay = np.inf
max_delay = -np.inf
for action in actionlist:
    assert action.type == rtmixer.PLAY_BUFFER
    # NB: action.allow_belated might have been invalidated
    assert action.requested_time != 0
    if not action.actual_time:
        belated += 1
        assert action.done_frames == 0
        continue
    assert action.done_frames == action.total_frames
    delay = action.actual_time - action.requested_time
    if delay > max_delay:
        max_delay = delay
    if delay < min_delay:
        min_delay = delay

print('total number of bleeps:', len(actionlist))
print('belated bleeps (not played):', belated)
print('maxiumum delay (in usec):', max_delay * 1000 * 1000)
print('maxiumum negative delay: ', -min_delay * 1000 * 1000)
print('half sampling period:    ', 0.5 * 1000 * 1000 / samplerate)
