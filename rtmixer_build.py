#!/usr/bin/env python3

# Executing this script creates the _rtmixer extension module (see rtmixer.py).

from cffi import FFI
import platform

if platform.system() == 'Darwin':
    ring_buffer_size_t = 'int32_t'
else:
    ring_buffer_size_t = 'long'

ffibuilder = FFI()
ffibuilder.cdef("""

/* From portaudio.h: */

typedef struct PaStreamCallbackTimeInfo PaStreamCallbackTimeInfo;
typedef unsigned long PaStreamCallbackFlags;

/* From pa_ringbuffer.h: */

typedef %(ring_buffer_size_t)s ring_buffer_size_t;
typedef struct PaUtilRingBuffer
{
    ring_buffer_size_t  bufferSize;
    volatile ring_buffer_size_t writeIndex;
    volatile ring_buffer_size_t readIndex;
    ring_buffer_size_t bigMask;
    ring_buffer_size_t smallMask;
    ring_buffer_size_t elementSizeBytes;
    char* buffer;
} PaUtilRingBuffer;
ring_buffer_size_t PaUtil_InitializeRingBuffer(PaUtilRingBuffer* rbuf, ring_buffer_size_t elementSizeBytes, ring_buffer_size_t elementCount, void* dataPtr);
void PaUtil_FlushRingBuffer(PaUtilRingBuffer* rbuf);
ring_buffer_size_t PaUtil_GetRingBufferWriteAvailable(const PaUtilRingBuffer* rbuf);
ring_buffer_size_t PaUtil_GetRingBufferReadAvailable(const PaUtilRingBuffer* rbuf);
ring_buffer_size_t PaUtil_WriteRingBuffer(PaUtilRingBuffer* rbuf, const void* data, ring_buffer_size_t elementCount);
ring_buffer_size_t PaUtil_ReadRingBuffer(PaUtilRingBuffer* rbuf, void* data, ring_buffer_size_t elementCount);
""" % locals())
ffibuilder.cdef(open('rtmixer.h').read())
ffibuilder.set_source(
    '_rtmixer',
    open('rtmixer.c').read(),
    include_dirs=['.', 'portaudio/include', 'portaudio/src/common'],
    sources=['portaudio/src/common/pa_ringbuffer.c'],
)

if __name__ == '__main__':
    ffibuilder.compile(verbose=True)
