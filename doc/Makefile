# Minimal makefile for Sphinx documentation
#

# You can set these variables from the command line, and also
# from the environment for the first two.
SPHINXOPTS    ?= -j auto --color
SPHINXBUILD   ?= sphinx-build
SOURCEDIR     = source
BUILDDIR      = _build
LINKCHECKDIR  = $(BUILDDIR)/linkcheck
LINKCHECKOPTS = -d $(BUILDDIR)/.doctrees -W --keep-going --color

# Put it first so that "make" without argument is like "make help".
help:
	@$(SPHINXBUILD) -M help "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)

.PHONY: help Makefile

# Catch-all target: route all unknown targets to Sphinx using the new
# "make mode" option.  $(O) is meant as a shortcut for $(SPHINXOPTS).
%: Makefile
	@$(SPHINXBUILD) -M $@ "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)

clean:
	@echo "Cleaning everything."
	rm -rf $(BUILDDIR)/*
	rm -rf examples/
	find . -type d -name "_autosummary" -exec rm -rf {} +

# FIXME: currently linkcheck freezes and further investigation must be performed
# linkcheck:
# 	@echo "Checking links."
# 	@$(SPHINXBUILD) -M linkcheck "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(LINKCHECKOPTS) -vv
# 	@echo
# 	@echo "Check finished. Report is in $(LINKCHECKDIR)."

html-noexamples:
	@echo "Building HTML pages without running examples."
	export PYAEDT_DOC_RUN_EXAMPLES="0"
	@# FIXME: currently linkcheck freezes and further investigation must be performed
	@# @$(SPHINXBUILD) -M linkcheck "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(LINKCHECKOPTS) $(O)
	@$(SPHINXBUILD) -M html "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)
	@echo
	@echo "Build finished. The HTML pages are in $(BUILDDIR)."

# Build PDF pages
pdf:
	@echo "Building PDF pages."
	@$(SPHINXBUILD) -M latex "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)
	cd $(BUILDDIR)/latex && latexmk -r latexmkrc -pdf *.tex -interaction=nonstopmode || true
	(test -f $(BUILDDIR)/latex/pyaedt.pdf && echo pdf exists) || exit 1

# Build documentation as it is done in CI/CD
cibuild: clean
	mkdir source/examples -p
	echo $'Examples\n========' > doc/source/examples/index.rst
	$(MAKE) html-noexamples
	# python print_errors.py
