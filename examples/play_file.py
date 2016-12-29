#!/usr/bin/env python3

import sys

import rtmixer
import soundfile as sf

filename = sys.argv[1]
blocksize = 1024

with sf.SoundFile(filename) as f:
    with rtmixer.RtMixer(device=0, channels=f.channels, blocksize=blocksize,
                         samplerate=f.samplerate) as m:
        for block in f.blocks(blocksize=m.blocksize, dtype='float32',
                              always_2d=True, fill_value=0):
            assert len(block) == blocksize
            m.enqueue_numpy(block)
        input()
