Contributing
============

If you find bugs, errors, omissions or other things that need improvement,
please create an issue or a pull request at
https://github.com/spatialaudio/python-rtmixer/.
Contributions are always welcome!


Development Installation
------------------------

Instead of pip-installing the latest release from PyPI_, you should get the
newest development version (a.k.a. "master") with Git::

   git clone https://github.com/spatialaudio/python-rtmixer.git --recursive
   cd python-rtmixer
   python3 -m pip install -e .

... where ``-e`` stands for ``--editable``.

When installing this way, you can quickly try other Git
branches (in this example the branch is called "another-branch")::

   git checkout another-branch

If you want to go back to the "master" branch, use::

   git checkout master

To get the latest changes from Github, use::

   git pull --ff-only

If you used the ``--recursive`` option when cloning,
the ``portaudio`` submodule (which is needed for compiling the module)
will be checked out automatically.
If not, you can get the submodule with::

   git submodule update --init

.. _PyPI: https://pypi.org/project/rtmixer/


Building the Documentation
--------------------------

If you make changes to the documentation, you should create the HTML
pages locally using Sphinx and check if they look OK.

Initially, you might need to install a few packages that are needed to build the
documentation::

   python3 -m pip install -r doc/requirements.txt

To (re-)build the HTML files, use::

   python3 setup.py build_sphinx

The generated files will be available in the directory ``build/sphinx/html/``.


Creating a New Release
----------------------

New releases are made using the following steps:

#. Bump version number in ``src/rtmixer.py``
#. Update ``NEWS.rst``
#. Commit those changes as "Release x.y.z"
#. Create an (annotated) tag with ``git tag -a x.y.z``
#. Push the commit and the tag to Github
#. Wait 10 minutes for the PyPI packages to be automagically uploaded
#. On Github, `add release notes`_ containing a
   link to PyPI and the bullet points from ``NEWS.rst``
#. Check that the new release was built correctly on RTD_
   and select the new release as default version

.. _add release notes: https://github.com/spatialaudio/python-rtmixer/tags
.. _RTD: https://readthedocs.org/projects/python-rtmixer/builds/
