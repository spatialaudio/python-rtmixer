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
    setup_requires=['CFFI>=1.4.0', 'pa_ringbuffer'],
    cffi_modules=['rtmixer_build.py:ffibuilder'],
    install_requires=['sounddevice>0.3.6', 'pa_ringbuffer'],
    author='Matthias Geier',
    author_email='Matthias.Geier@gmail.com',
    description='Reliable low-latency audio playback and recording',
    long_description=open('README.rst').read(),
    license='MIT',
    keywords='sound audio PortAudio realtime low-latency'.split(),
    #url='http://python-rtmixer.readthedocs.io/',
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
