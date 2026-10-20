# This is used to create the _rtmixer extension module (see setup.py).

import sys
from cffi import FFI
import pa_ringbuffer

RINGBUFFER_CDEF = pa_ringbuffer.cdef()

ffibuilder = FFI()
ffibuilder.cdef(RINGBUFFER_CDEF)
ffibuilder.cdef("""

/* From limits.h: */

#define ULONG_MAX ...

""")
ffibuilder.cdef(open('src/rtmixer.h').read())
# '-Wconversion'
extra_compile_args = list()
if sys.platform == "linux":
    extra_compile_args.append("--std=c99")
extra_kwargs = dict()
# cffi sets py_limited_api=True by default, which setuptools >= 84.1 no longer
# ignores for PyPy on Windows (giving an untagged, unimportable "_rtmixer.pyd")
if sys.implementation.name != 'cpython':
    extra_kwargs['py_limited_api'] = False
ffibuilder.set_source(
    '_rtmixer',
    RINGBUFFER_CDEF + open('src/rtmixer.c').read(),
    include_dirs=['src', 'portaudio/include'],
    sources=['portaudio/src/common/pa_ringbuffer.c'],
    extra_compile_args=extra_compile_args,
    # TODO: release mode by default, option for using debug mode
    undef_macros=[
        # 'NDEBUG'
    ],
    **extra_kwargs,
)

if __name__ == '__main__':
    ffibuilder.compile(verbose=True)
