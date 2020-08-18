import os
from subprocess import check_output
import sys

sys.path.insert(0, os.path.abspath('../src'))
sys.path.insert(0, os.path.abspath('.'))

# Fake imports to avoid actually loading CFFI and C extension modules
import fake_sounddevice
sys.modules['sounddevice'] = sys.modules['fake_sounddevice']
import fake_rtmixer
sys.modules['_rtmixer'] = sys.modules['fake_rtmixer']

authors = 'Matthias Geier'
project = 'python-rtmixer'

default_role = 'any'

extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.autosummary',
    'sphinx.ext.intersphinx',
    'sphinx.ext.viewcode',
    'sphinx_last_updated_by_git',
]

intersphinx_mapping = {
    'python': ('https://docs.python.org/3/', None),
    'numpy': ('https://numpy.org/doc/stable/', None),
    'sounddevice': ('https://python-sounddevice.readthedocs.io/', None),
}

nitpicky = True
nitpick_ignore = [
    ('py:class', 'optional'),
    ('py:class', 'buffer'),
    ('py:class', 'CData pointer'),
]

try:
    release = check_output(['git', 'describe', '--tags', '--always'])
    release = release.decode().strip()
    today = check_output(['git', 'show', '-s', '--format=%ad', '--date=short'])
    today = today.decode().strip()
except Exception:
    release = '<unknown>'
    today = '<unknown date>'

html_theme = 'insipid'
html_domain_indices = False
html_show_copyright = False
html_add_permalinks = '\N{SECTION SIGN}'
html_copy_source = False

latex_elements = {
    'papersize': 'a4paper',
    'printindex': '',
}
latex_documents = [('index', 'python-rtmixer.tex', project, authors, 'howto')]
