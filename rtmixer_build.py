# This is used to create the _rtmixer extension module (see setup.py).

from cffi import FFI
import platform

if platform.system() == 'Darwin':
    ring_buffer_size_t = 'int32_t'
else:
    ring_buffer_size_t = 'long'

ffibuilder = FFI()
ffibuilder.cdef("""

/* From portaudio.h: */

typedef double PaTime;
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
ring_buffer_size_t PaUtil_GetRingBufferWriteRegions(PaUtilRingBuffer* rbuf, ring_buffer_size_t elementCount, void** dataPtr1, ring_buffer_size_t* sizePtr1, void** dataPtr2, ring_buffer_size_t* sizePtr2);
ring_buffer_size_t PaUtil_AdvanceRingBufferWriteIndex(PaUtilRingBuffer* rbuf, ring_buffer_size_t elementCount);
ring_buffer_size_t PaUtil_GetRingBufferReadRegions(PaUtilRingBuffer* rbuf, ring_buffer_size_t elementCount, void** dataPtr1, ring_buffer_size_t* sizePtr1, void** dataPtr2, ring_buffer_size_t* sizePtr2);
ring_buffer_size_t PaUtil_AdvanceRingBufferReadIndex(PaUtilRingBuffer* rbuf, ring_buffer_size_t elementCount);

/* From limits.h: */

#define ULONG_MAX ...
""" % locals())
ffibuilder.cdef(open('src/rtmixer.h').read())
ffibuilder.set_source(
    '_rtmixer',
    open('src/rtmixer.c').read(),
    include_dirs=['src', 'portaudio/include', 'portaudio/src/common'],
    sources=['portaudio/src/common/pa_ringbuffer.c'],
    #extra_compile_args=['-Wconversion'],
    #undef_macros=['NDEBUG'],
)

if __name__ == '__main__':
    ffibuilder.compile(verbose=True)
