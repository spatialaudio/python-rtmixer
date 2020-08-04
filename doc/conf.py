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
    'sphinx.ext.intersphinx',
    'sphinx.ext.viewcode',
]

intersphinx_mapping = {
    'python': ('https://docs.python.org/3/', None),
    'numpy': ('https://numpy.org/doc/stable/', None),
    'sounddevice': ('https://python-sounddevice.readthedocs.io/', None),
}

try:
    release = check_output(['git', 'describe', '--tags', '--always'])
    release = release.decode().strip()
    today = check_output(['git', 'show', '-s', '--format=%ad', '--date=short'])
    today = today.decode().strip()
except Exception:
    release = '<unknown>'
    today = '<unknown date>'

html_theme = 'sphinx_rtd_theme'
html_domain_indices = False
html_show_copyright = False

latex_elements = {
    'papersize': 'a4paper',
    'printindex': '',
}
latex_documents = [('index', 'python-rtmixer.tex', project, authors, 'howto')]
