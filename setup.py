from setuptools import setup

__version__ = 'unknown'

# "import" __version__
for line in open('src/rtmixer.py'):
    if line.startswith('__version__'):
        exec(line)
        break

setup(
    name='rtmixer',
    version=__version__,
    package_dir={'': 'src'},
    py_modules=['rtmixer'],
    cffi_modules=['rtmixer_build.py:ffibuilder'],
    python_requires='>=2.6',
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
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 3',
        'Topic :: Multimedia :: Sound/Audio',
    ],
)
