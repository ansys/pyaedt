# Minimal makefile for Sphinx documentation
#

# You can set these variables from the command line, and also
# from the environment for the first two.
SPHINXOPTS    ?= -j auto --color -w build_errors.txt
SPHINXBUILD   ?= sphinx-build
SOURCEDIR     = source
BUILDDIR      = _build
LINKCHECKDIR  = $(BUILDDIR)/linkcheck
LINKCHECKOPTS = -d $(BUILDDIR)/.doctrees -W --keep-going --color

# Put it first so that "make" without argument is like "make help".
help:
	@$(SPHINXBUILD) -M help "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)

.PHONY: help Makefile

.install-deps:
	@pip freeze | grep -q "vtk-osmesa" && is_vtk_osmesa_installed="yes" || is_vtk_osmesa_installed="no"
	@if [ "${ON_CI}" = "True" ] && [ "$$is_vtk_osmesa_installed" != "yes" ]; then \
		@echo "Removing package(s) to avoid conflicts with package(s) needed for CI/CD"; \
		pip uninstall --yes vtk; \
		@echo "Installing CI/CD required package(s)"; \
		pip install --index-url https://wheels.vtk.org vtk-osmesa==9.3.1; \
	fi

# Catch-all target: route all unknown targets to Sphinx using the new
# "make mode" option.  $(O) is meant as a shortcut for $(SPHINXOPTS).
%: .install-deps Makefile
	@$(SPHINXBUILD) -M $@ "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)

clean: .install-deps
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

html: .install-deps
	@echo "Building HTML pages."
	@# FIXME: currently linkcheck freezes and further investigation must be performed
	@# @$(SPHINXBUILD) -M linkcheck "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(LINKCHECKOPTS) $(O)
	@$(SPHINXBUILD) -M html "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)
	@echo
	@echo "Build finished. The HTML pages are in $(BUILDDIR)."

pdf: .install-deps
	@echo "Building PDF pages."
	@$(SPHINXBUILD) -M latex "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)
	cd $(BUILDDIR)/latex && latexmk -r latexmkrc -pdf *.tex -interaction=nonstopmode || true
	(test -f $(BUILDDIR)/latex/pyaedt.pdf && echo pdf exists) || exit 1
	@echo "Build finished. The PDF pages are in $(BUILDDIR)."
