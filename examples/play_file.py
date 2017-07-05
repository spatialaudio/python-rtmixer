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
    with rtmixer.Mixer(channels=f.channels,
                       blocksize=playback_blocksize,
                       samplerate=f.samplerate, latency=latency) as m:
        elementsize = f.channels * m.samplesize
        rb = rtmixer.create_ringbuffer(elementsize,
                                       reading_blocksize * reading_qsize)
        writer = rtmixer.RingBufferWriter(rb)
        # Pre-fill ringbuffer:
        _, buf, _ = writer.get_write_buffers(reading_blocksize * reading_qsize)
        written = f.buffer_read_into(buf, dtype='float32')
        writer.advance_write_index(written)
        action = m.play_ringbuffer(rb)
        while True:
            while writer.write_available < reading_blocksize:
                if action not in m.actions:
                    break
                sd.sleep(int(1000 * reading_blocksize / f.samplerate))
            if action not in m.actions:
                break
            size, buf1, buf2 = writer.get_write_buffers(reading_blocksize)
            assert not buf2
            written = f.buffer_read_into(buf1, dtype='float32')
            writer.advance_write_index(written)
            if written < size:
                break
        m.wait(action)
        # TODO: check for xruns and ringbuffer errors
