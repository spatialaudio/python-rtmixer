from subprocess import check_output

needs_sphinx = '1.3'  # for sphinx.ext.napoleon

extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.intersphinx',
    'sphinx.ext.viewcode',
    'sphinx.ext.napoleon',  # support for NumPy-style docstrings
]

autoclass_content = 'init'
autodoc_member_order = 'bysource'

napoleon_google_docstring = False
napoleon_numpy_docstring = True
napoleon_include_private_with_doc = False
napoleon_include_special_with_doc = False
napoleon_use_admonition_for_examples = False
napoleon_use_admonition_for_notes = False
napoleon_use_admonition_for_references = False
napoleon_use_ivar = False
napoleon_use_param = False
napoleon_use_rtype = False

intersphinx_mapping = {
    'python': ('https://docs.python.org/3/', None),
    'numpy': ('https://docs.scipy.org/doc/numpy/', None),
    'sounddevice': ('http://python-sounddevice.readthedocs.io/en/latest/',
                    None),
}

source_suffix = '.rst'
master_doc = 'index'

authors = 'Matthias Geier'
project = 'python-rtmixer'
copyright = '2017, ' + authors

try:
    release = check_output(['git', 'describe', '--tags', '--always'])
    release = release.decode().strip()
except Exception:
    release = '<unknown>'

pygments_style = 'sphinx'
html_theme = 'sphinx_rtd_theme'
html_domain_indices = False

latex_elements = {
    'papersize': 'a4paper',
    'printindex': '',
}
latex_documents = [('index', 'python-rtmixer.tex', project, authors, 'howto')]
