#!/usr/bin/env python3

from __future__ import division  # Only needed for Python 2.x
import numpy as np
import rtmixer
import sounddevice as sd

seed = 99

blocksize = 0
latency = 'low'
samplerate = 44100

bleeps = 300

attack = 0.005
release = 0.1
pitch_min = 40
pitch_max = 80
duration_min = 0.2
duration_max = 0.6
amplitude_min = 0.05
amplitude_max = 0.15
sleep_min = 0
sleep_max = 0.1
channels = 1  # TODO: multichannel
sleeptime = 5

if duration_min < max(attack, release):
    raise ValueError('minimum duration is too short')

fade_in = np.linspace(0, 1, num=int(samplerate * attack))
fade_out = np.linspace(1, 0, num=int(samplerate * release))

r = np.random.RandomState(seed)

bleeplist = []

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

with rtmixer.RtMixer(channels=channels, blocksize=blocksize,
                     samplerate=samplerate, latency=latency) as m:
    for bleep in bleeplist:
        m.play_buffer(bleep)
        sleeptime = r.uniform(sleep_min, sleep_max)
        sd.sleep(int(1000 * sleeptime))
    # TODO: wait until the last bleep has finished
    sd.sleep(int(1000 * duration_max))
