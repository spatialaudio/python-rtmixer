#!/usr/bin/env python3
"""A minimalistic sampler with an even more minimalistic GUI."""

import collections
import math
try:
    import tkinter as tk
except ImportError:
    # Python 2.x
    import Tkinter as tk

import rtmixer
from tkhelper import TkKeyEventDebouncer


HELPTEXT = 'Hold uppercase key for recording,\nlowercase for playback'
REC_OFF = '#600'
REC_ON = '#e00'
BUFFER_DURATION = 0.1  # seconds


class Sample(object):

    def __init__(self):
        elementsize = stream.samplesize[0]
        size = BUFFER_DURATION * stream.samplerate
        # Python 2.x doesn't have math.log2(), and it needs int():
        size = 2**int(math.ceil(math.log(size, 2)))
        self.ringbuffer = rtmixer.RingBuffer(elementsize, size)
        self.buffer = bytearray()
        self.action = None


class MiniSampler(tk.Tk, TkKeyEventDebouncer):

    def __init__(self, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)
        TkKeyEventDebouncer.__init__(self)
        self.title('MiniSampler')
        tk.Label(self, text=HELPTEXT).pack(ipadx=20, ipady=20)
        self.rec_display = tk.Label(self, text='recording')
        self.rec_counter = tk.IntVar()
        self.rec_counter.trace(mode='w', callback=self.update_rec_display)
        self.rec_counter.set(0)
        self.rec_display.pack(padx=10, pady=10, ipadx=5, ipady=5)
        self.samples = collections.defaultdict(Sample)

    def update_rec_display(self, *args):
        if self.rec_counter.get() == 0:
            self.rec_display['bg'] = REC_OFF
        else:
            self.rec_display['bg'] = REC_ON

    def on_key_press(self, event):
        ch = event.char
        if ch.isupper():
            sample = self.samples[ch.lower()]
            # TODO: check if we are already recording? check action?
            sample.ringbuffer.flush()
            sample.action = stream.record_ringbuffer(sample.ringbuffer)
            del sample.buffer[:]
            self.rec_counter.set(self.rec_counter.get() + 1)
            self.poll_ringbuffer(sample)
        elif ch in self.samples:
            sample = self.samples[ch]
            # TODO: can it be still recording or already playing?
            if sample.action in stream.actions:
                # TODO: the CANCEL action might still be active, which
                #       shouldn't be a problem, right?
                print(ch, 'action still running:', sample.action.type)
            if ((sample.action is not None and
                    sample.action.type != rtmixer._lib.CANCEL) or
                    not sample.buffer):
                print(sample.action.type, len(sample.buffer))
                raise RuntimeError('Unable to play')
            sample.action = stream.play_buffer(sample.buffer, channels=1)
        else:
            # TODO: handle special keys?
            pass

    def on_key_release(self, event):
        # NB: State of "shift" button may change between key press and release!
        ch = event.char.lower()
        if ch not in self.samples:
            return
        sample = self.samples[ch]
        # TODO: fade out (both recording and playback)?
        # TODO: is it possible that there is no action?
        assert sample.action
        # TODO: create a public API for that?
        if sample.action.type == rtmixer._lib.RECORD_RINGBUFFER:
            # TODO: check for errors/xruns? check for rinbuffer overflow?
            # Stop recording
            sample.action = stream.cancel(sample.action)
            # A CANCEL action is returned which is checked by poll_ringbuffer()
        elif sample.action.type == rtmixer._lib.PLAY_BUFFER:
            # TODO: check for errors/xruns?
            # Stop playback
            sample.action = stream.cancel(sample.action)
            # TODO: do something with sample.action?
        elif sample.action.type == rtmixer._lib.CANCEL:
            print('key {!r} released during CANCEL'.format(event.char))
        else:
            print(event.char, sample.action)
            assert False

    def poll_ringbuffer(self, sample):
        # TODO: check for errors? is everything still working OK?
        assert sample.action, sample.action
        assert sample.action.type in (rtmixer._lib.RECORD_RINGBUFFER,
                                      rtmixer._lib.CANCEL), sample.action.type
        chunk = sample.ringbuffer.read()
        if chunk:
            sample.buffer.extend(chunk)

        if (sample.action.type == rtmixer._lib.CANCEL and
                sample.action not in stream.actions):
            # TODO: check for errors in CANCEL action?
            sample.action = None
            self.rec_counter.set(self.rec_counter.get() - 1)
        else:
            # Set polling rate based on input latency (which may change!):
            self.after(int(stream.latency[0] * 1000),
                       self.poll_ringbuffer, sample)


app = MiniSampler()
with rtmixer.MixerAndRecorder(channels=1) as stream:
    app.mainloop()
