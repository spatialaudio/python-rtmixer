#!/usr/bin/env python3

# Executing this script creates the _rtmixer extension module (see rtmixer.py).

from cffi import FFI

ffibuilder = FFI()
ffibuilder.cdef("""

/* From portaudio.h: */

typedef double PaTime;
typedef struct
{
  PaTime inputBufferAdcTime;
  PaTime currentTime;
  PaTime outputBufferDacTime;
} PaStreamCallbackTimeInfo;
typedef unsigned long PaStreamCallbackFlags;

/* Declaration for rtmixer.c */

int callback(const void* input, void* output, unsigned long frames
  , const PaStreamCallbackTimeInfo* time, PaStreamCallbackFlags status
  , void* userdata);
""")
ffibuilder.set_source('_rtmixer', open('rtmixer.c').read())

if __name__ == '__main__':
    ffibuilder.compile(verbose=True)
