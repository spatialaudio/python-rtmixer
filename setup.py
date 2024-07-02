from setuptools import setup, Extension
from wheel.bdist_wheel import bdist_wheel

__version__ = 'unknown'

# "import" __version__
for line in open('src/rtmixer.py'):
    if line.startswith('__version__'):
        exec(line)
        break


# Adapted from
# https://github.com/joerick/python-abi3-package-sample/blob/main/setup.py
class bdist_wheel_abi3(bdist_wheel):
    def get_tag(self):
        python, abi, plat = super().get_tag()

        if python.startswith("cp"):
            # on CPython, our wheels are abi3 and compatible back to 3.2,
            # but let's set it to our min version anyway
            return "cp38", "abi3", plat

        return python, abi, plat


setup(
    name='rtmixer',
    version=__version__,
    package_dir={'': 'src'},
    py_modules=['rtmixer'],
    cffi_modules=['rtmixer_build.py:ffibuilder'],  # sets Py_LIMITED_API for us
    python_requires='>=3.6',
    setup_requires=[
        'CFFI>=1.4.0',
        'pa_ringbuffer',  # for cdef()
    ],
    install_requires=[
        'CFFI>=1',  # for _cffi_backend
        'pa_ringbuffer',  # for init()
        'sounddevice>0.3.9',
    ],
    author='Matthias Geier',
    author_email='Matthias.Geier@gmail.com',
    description='Reliable low-latency audio playback and recording',
    long_description=open('README.rst').read(),
    license='MIT',
    keywords='sound audio PortAudio realtime low-latency'.split(),
    url='https://python-rtmixer.readthedocs.io/',
    platforms='any',
    classifiers=[
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Topic :: Multimedia :: Sound/Audio',
    ],
    cmdclass={"bdist_wheel": bdist_wheel_abi3},
)
