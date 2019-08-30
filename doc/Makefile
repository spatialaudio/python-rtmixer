# Makefile for Sphinx documentation
#

# You can set these variables from the command line.
SPHINXOPTS    = -nT --keep-going
SPHINXBUILD   = sphinx-build
PAPER         =

# Internal variables.
PAPEROPT_a4     = -D latex_paper_size=a4
PAPEROPT_letter = -D latex_paper_size=letter
ALLSPHINXOPTS   = -d _build/doctrees $(PAPEROPT_$(PAPER)) $(SPHINXOPTS) .

.PHONY: help clean html show

# make with no arguments will build the first target by default, i.e., build standalone HTML files
first_target: html

help:
	@echo "Please use \`make <target>' where <target> is one of"
	@echo "  html             to make standalone HTML files"
	@echo "  clean            to remove the built files"
	@echo "  show             to show the resulting HTML files"

clean:
	-rm -rf _build

html:
	$(SPHINXBUILD) -b html $(ALLSPHINXOPTS) _build/html
	@echo
	@echo "Build finished. The HTML pages are in _build/html."

show:
	@python -c "import webbrowser; webbrowser.open_new_tab('file://$(PWD)/_build/html/index.html')"
