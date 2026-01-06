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
            return "cp310", "abi3", plat

        return python, abi, plat


setup(
    version=__version__,
    package_dir={'': 'src'},
    py_modules=['rtmixer'],
    cffi_modules=['rtmixer_build.py:ffibuilder'],  # sets Py_LIMITED_API for us
    cmdclass={"bdist_wheel": bdist_wheel_abi3},
)
