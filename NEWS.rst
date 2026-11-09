Version 0.1.8 -- unreleased
 * Fix lost results and a hanging ``wait()`` when many actions finish
   in the same audio block
 * Fix possible crashes when a stream is garbage-collected while it is
   running, or when an action is garbage-collected after being cancelled
 * Update PortAudio submodule to the current development version

Version 0.1.7 -- 2024-07-02 -- PyPI__ -- diff__
 * Restore the ``x86_64`` Linux wheels that were missing from 0.1.6

__ https://pypi.org/project/rtmixer/0.1.7/
__ https://github.com/spatialaudio/python-rtmixer/compare/0.1.6...0.1.7

Version 0.1.6 -- 2024-07-02 -- PyPI__ -- diff__
 * Build ``abi3`` wheels, so one CPython wheel per platform supports
   Python 3.8 and newer

__ https://pypi.org/project/rtmixer/0.1.6/
__ https://github.com/spatialaudio/python-rtmixer/compare/0.1.5...0.1.6

Version 0.1.5 -- 2024-06-24 -- PyPI__ -- diff__
 * Build wheels on GitHub Actions instead of Azure Pipelines
 * Add wheels for Python 3.11 and 3.12, Linux ``aarch64`` and macOS ``arm64``
 * Drop wheels for Python 3.6 and 3.7 and for 32-bit Windows

__ https://pypi.org/project/rtmixer/0.1.5/
__ https://github.com/spatialaudio/python-rtmixer/compare/0.1.4...0.1.5

Version 0.1.4 -- 2022-01-05 -- PyPI__ -- diff__
 * Add Python 3.10 support
 * Remove the ``allow_belated`` field of actions, it is now encoded in
   ``actual_time``
 * Update PortAudio submodule to version 19.7.0
 * Document common parameters and the fields of actions and statistics

__ https://pypi.org/project/rtmixer/0.1.4/
__ https://github.com/spatialaudio/python-rtmixer/compare/0.1.3...0.1.4

Version 0.1.3 -- 2021-05-05 -- PyPI__ -- diff__
 * Add Python 3.9 support by adding entries to ``azure-pipelines.yml``
   for ``cibuildwheel``

__ https://pypi.org/project/rtmixer/0.1.3/
__ https://github.com/spatialaudio/python-rtmixer/compare/0.1.2...0.1.3

Version 0.1.2 -- 2020-08-20 -- PyPI__ -- diff__
 * Clean up ``cibuildwheel``

__ https://pypi.org/project/rtmixer/0.1.2/
__ https://github.com/spatialaudio/python-rtmixer/compare/0.1.1...0.1.2

Version 0.1.1 -- 2020-06-19 -- PyPI__ -- diff__
 * Add Python 3.8 support by adding entries to ``azure-pipelines.yml``
   for ``cibuildwheel``

__ https://pypi.org/project/rtmixer/0.1.1/
__ https://github.com/spatialaudio/python-rtmixer/compare/0.1.0...0.1.1

Version 0.1.0 -- 2019-09-05 -- PyPI__
   Initial release

__ https://pypi.org/project/rtmixer/0.1.0/
