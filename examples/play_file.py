#!/usr/bin/env python3

from __future__ import division  # Only needed for Python 2.x
import sys

import rtmixer
import sounddevice as sd
import soundfile as sf

filename = sys.argv[1]
playback_blocksize = 256
latency = 0
reading_blocksize = 1024
reading_qsize = 16  # Number of blocks, has to be power of two

with sf.SoundFile(filename) as f:
    with rtmixer.RtMixer(device=0, channels=f.channels,
                         blocksize=playback_blocksize,
                         samplerate=f.samplerate, latency=latency) as m:
        # TODO: indexing not necessary for output-only mixer object:
        elementsize = f.channels * m.samplesize[1]
        q = rtmixer.RingBuffer(elementsize, reading_blocksize * reading_qsize)
        # TODO: pre-fill ringbuffer
        m.play_ringbuffer(q)  # TODO: return value?
        while True:
            # TODO: use buffer_read_into() instead, to directly write into rb
            buffer = f.buffer_read(reading_blocksize, ctype='float')
            if not buffer:
                break
            while q.write_available < reading_blocksize * elementsize:
                sd.sleep(int(1000 * reading_blocksize * elementsize /
                             f.samplerate))
            ret = q.write(buffer)
            assert ret == len(buffer) / elementsize
        input()
        # TODO: wait until playback is finished
        # TODO: check for xruns
