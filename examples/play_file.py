#!/usr/bin/env python3

from __future__ import division  # Only needed for Python 2.x
import sys

import rtmixer
import sounddevice as sd
import soundfile as sf

filename = sys.argv[1]
playback_blocksize = None
latency = None
reading_blocksize = 1024  # (reading_blocksize * rb_size) has to be power of 2
rb_size = 16  # Number of blocks

with sf.SoundFile(filename) as f:
    with rtmixer.Mixer(channels=f.channels,
                       blocksize=playback_blocksize,
                       samplerate=f.samplerate, latency=latency) as m:
        elementsize = f.channels * m.samplesize
        rb = rtmixer.RingBuffer(elementsize, reading_blocksize * rb_size)
        # Pre-fill ringbuffer:
        _, buf, _ = rb.get_write_buffers(reading_blocksize * rb_size)
        written = f.buffer_read_into(buf, dtype='float32')
        rb.advance_write_index(written)
        action = m.play_ringbuffer(rb)
        while True:
            while rb.write_available < reading_blocksize:
                if action not in m.actions:
                    break
                sd.sleep(int(1000 * reading_blocksize / f.samplerate))
            if action not in m.actions:
                break
            size, buf1, buf2 = rb.get_write_buffers(reading_blocksize)
            assert not buf2
            written = f.buffer_read_into(buf1, dtype='float32')
            rb.advance_write_index(written)
            if written < size:
                break
        m.wait(action)
        if action.done_frames != f.frames:
            RuntimeError('Something went wrong, not all frames were played')
        if action.stats.output_underflows:
            print('output underflows:', action.stats.output_underflows)
