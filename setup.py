import sys
import sysconfig

from setuptools import setup

__version__ = 'unknown'

# "import" __version__
for line in open('src/rtmixer.py'):
    if line.startswith('__version__'):
        exec(line)
        break


# Adapted from
# https://github.com/joerick/python-abi3-package-sample/blob/main/setup.py
# On CPython our wheels are abi3. Free-threaded builds support the limited API
# (as abi3t, PEP 803) only from 3.15 on, so 3.14t gets a version-specific
# wheel.
options = {}
if sys.implementation.name == 'cpython':
    if not sysconfig.get_config_var('Py_GIL_DISABLED'):
        options['bdist_wheel'] = {'py_limited_api': 'cp310'}
    elif sys.version_info >= (3, 15):
        options['bdist_wheel'] = {'py_limited_api': 'cp315'}


setup(
    version=__version__,
    package_dir={'': 'src'},
    py_modules=['rtmixer'],
    cffi_modules=['rtmixer_build.py:ffibuilder'],  # sets Py_LIMITED_API for us
    options=options,
)
