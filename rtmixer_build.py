# This is used to create the _rtmixer extension module (see setup.py).

from cffi import FFI
import _pa_ringbuffer
import _pa_ringbuffer_build

ffibuilder = FFI()
ffibuilder.include(_pa_ringbuffer_build.ffibuilder)
ffibuilder.cdef("""

/* From limits.h: */

#define ULONG_MAX ...

""")
ffibuilder.cdef(open('src/rtmixer.h').read())
ffibuilder.set_source(
    '_rtmixer',
    _pa_ringbuffer_build.RINGBUFFER_DECLARATIONS +
    open('src/rtmixer.c').read(),
    include_dirs=['src'],
    extra_objects=[_pa_ringbuffer.__file__],
    #extra_compile_args=['-Wconversion'],
    # TODO: release mode by default, option for using debug mode
    undef_macros=['NDEBUG'],
)

if __name__ == '__main__':
    ffibuilder.compile(verbose=True)
