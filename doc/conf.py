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

extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.intersphinx',
    'sphinx.ext.viewcode',
]

intersphinx_mapping = {
    'python': ('https://docs.python.org/3/', None),
    'numpy': ('https://docs.scipy.org/doc/numpy/', None),
    'sounddevice':
        ('http://python-sounddevice.readthedocs.io/en/latest/', None),
}

master_doc = 'index'

authors = 'Matthias Geier'
project = 'python-rtmixer'
copyright = '2017, ' + authors

try:
    release = check_output(['git', 'describe', '--tags', '--always'])
    release = release.decode().strip()
    today = check_output(['git', 'show', '-s', '--format=%ad', '--date=short'])
    today = today.decode().strip()
except Exception:
    release = '<unknown>'
    today = '<unknown date>'

pygments_style = 'sphinx'
html_theme = 'sphinx_rtd_theme'
html_domain_indices = False

latex_elements = {
    'papersize': 'a4paper',
    'printindex': '',
}
latex_documents = [('index', 'python-rtmixer.tex', project, authors, 'howto')]
