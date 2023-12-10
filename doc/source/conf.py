"""Sphinx documentation configuration file."""
from datetime import datetime
import json
import os
from pathlib import Path

from ansys_sphinx_theme import (
    ansys_favicon,
    ansys_logo_white,
    ansys_logo_white_cropped,
    get_version_match,
    latex,
    pyansys_logo_black,
    watermark,
)
import sys
import warnings

import pyvista
from importlib import import_module
from pprint import pformat
from docutils.parsers.rst import Directive
from docutils import nodes
from sphinx import addnodes
import shutil

import requests

from pyaedt import __version__

# <-----------------Override the sphinx pdf builder---------------->
# Some pages do not render properly as per the expected Sphinx LaTeX PDF signature.
# This issue can be resolved by migrating to the autoapi format.
# Additionally, when documenting images in formats other than the supported ones, 
# make sure to specify their types.
from sphinx.builders.latex import LaTeXBuilder
LaTeXBuilder.supported_image_types = ["image/png", "image/pdf", "image/svg+xml", "image/webp" ]

from sphinx.writers.latex import CR
from sphinx.writers.latex import LaTeXTranslator
from docutils.nodes import Element

def visit_desc_content(self, node: Element) -> None:
    self.body.append(CR + r'\pysigstopsignatures')
    self.in_desc_signature = False
LaTeXTranslator.visit_desc_content = visit_desc_content

# <----------------- End of sphinx pdf builder override---------------->


# Project information
project = "PyAEDT"
copyright = f"(c) {datetime.now().year} ANSYS, Inc. All rights reserved"
author = "Ansys Inc."
release = version = __version__
# FIXME: change default to "aedt.docs.pyansys.com" ?
cname = os.getenv("DOCUMENTATION_CNAME", "nocname.com")
switcher_version = get_version_match(__version__)

os.environ["PYAEDT_NON_GRAPHICAL"] = "1"
os.environ["PYAEDT_DOC_GENERATION"] = "1"

# Check if Pandoc is already in the Path. Only add it to the path if it is not found.
if "Pandoc" not in os.environ['PATH']:
    os.environ['PATH'] = os.environ['PATH'] + ";" + os.path.join(os.environ['LOCALAPPDATA'], "Pandoc")

# <----------------- Options for HTML output ----------------->

# Select logo, theme, and declare the html title
html_logo = pyansys_logo_black
html_theme = "ansys_sphinx_theme"
html_short_title = html_title = "PyAEDT"

# Specify the location of the github repo
html_context = {
    "github_user": "ansys",
    "github_repo": "pyaedt",
    "github_version": "main",
    "doc_path": "doc/source",
}

html_theme_options = {
    "switcher": {
        "json_url": f"https://{cname}/versions.json",
        "version_match": switcher_version,
    },
    "check_switcher": False,
    "github_url": "https://github.com/ansys/pyaedt",
    "show_prev_next": False,
    "show_breadcrumbs": True,
    "collapse_navigation": True,
    "use_edit_page_button": True,
    "additional_breadcrumbs": [
        ("PyAnsys", "https://docs.pyansys.com/"),
    ],
    "icon_links": [
        {
            "name": "Support",
            "url": "https://github.com/ansys/pyaedt/discussions",
            "icon": "fa fa-comment fa-fw",
        },
        {
            "name": "Download documentation in PDF",
            "url": f"https://{cname}/version/{switcher_version}/_static/assets/download/pyaedt.pdf",  # noqa: E501
            "icon": "fa fa-file-pdf fa-fw",
        },
    ],
    "use_meilisearch": {
        "api_key": os.getenv("MEILISEARCH_PUBLIC_API_KEY", ""),
        "index_uids": {
            f"pyaedt-v{get_version_match(__version__).replace('.', '-')}": "PyAEDT",
            f"pyedb-v{get_version_match(__version__).replace('.', '-')}": "EDB API",
        },
    },
}

# Sphinx extensions
extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.intersphinx",
    "sphinx_copybutton",
    "nbsphinx",
    "myst_parser",
    "jupyter_sphinx",
    "sphinx_design",
    "sphinx_jinja",
    "sphinx.ext.autosummary",
    "numpydoc",
]

# Intersphinx mapping
intersphinx_mapping = {
    "python": ("https://docs.python.org/3.11", None),
    "numpy": ("https://numpy.org/doc/stable", None),
    # "scipy": ("https://docs.scipy.org/doc/scipy/", None),
    "pyvista": ("https://docs.pyvista.org/version/stable", None),
    "imageio": ("https://imageio.readthedocs.io/en/stable", None),
    "matplotlib": ("https://matplotlib.org/stable", None),
    "imageio": ("https://imageio.readthedocs.io/en/stable", None),
    "pandas": ("https://pandas.pydata.org/pandas-docs/stable", None),
    "pytest": ("https://docs.pytest.org/en/stable", None),
}

toc_object_entries_show_parents = "hide"

html_show_sourcelink = True


# numpydoc configuration
numpydoc_use_plots = True
numpydoc_show_class_members = False
numpydoc_xref_param_type = True

# Consider enabling numpydoc validation. See:
# https://numpydoc.readthedocs.io/en/latest/validation.html#
numpydoc_validate = True
numpydoc_validation_checks = {
    # General
    "GL06",  # Found unknown section
    "GL07",  # Sections are in the wrong order.
    "GL08",  # The object does not have a docstring
    "GL09",  # Deprecation warning should precede extended summary
    "GL10",  # reST directives {directives} must be followed by two colons
    # Return
    "RT04", # Return value description should start with a capital letter"
    "RT05", # Return value description should finish with "."
    # Summary
    "SS01",  # No summary found
    "SS02",  # Summary does not start with a capital letter
    "SS03",  # Summary does not end with a period
    "SS04",  # Summary contains heading whitespaces
    "SS05",  # Summary must start with infinitive verb, not third person
    # Parameters
    "PR10",  # Parameter "{param_name}" requires a space before the colon
    # separating the parameter name and type",
}

# Static path
html_static_path = ["_static"]

# These paths are either relative to html_static_path or fully qualified paths (eg. https://...)
html_css_files = [
    'custom.css',
]

html_favicon = ansys_favicon

# Add any paths that contain templates here, relative to this directory.
templates_path = ["_templates"]

# The suffix(es) of source filenames.
source_suffix = {
    ".rst": "restructuredtext",
    ".mystnb": "jupyter_notebook",
    ".md": "markdown",
}

# The master toctree document.
master_doc = "index"

# Manage errors
pyvista.set_error_output_file("errors.txt")

# Ensure that offscreen rendering is used for docs generation
pyvista.OFF_SCREEN = True

# Preferred plotting style for documentation
# pyvista.set_plot_theme('document')

# must be less than or equal to the XVFB window size
pyvista.global_theme["window_size"] = [1024, 768]

# Save figures in specified directory
pyvista.FIGURE_PATH = os.path.join(os.path.abspath("./images/"), "auto-generated/")
if not os.path.exists(pyvista.FIGURE_PATH):
    os.makedirs(pyvista.FIGURE_PATH)

# Examples gallery customization
nbsphinx_execute = "always"
nbsphinx_custom_formats = {
    ".mystnb": ["jupytext.reads", {"fmt": "mystnb"}],
}
nbsphinx_thumbnails = {
    "examples/00_EDB/00_create_via": "_static/diff_via.png",
}
nbsphinx_epilog = """
----

.. admonition:: Download this example

    Download this example as a `Jupyter Notebook <{cname_pref}/{ipynb_file_loc}>`_
    or as a `Python script <{cname_pref}/{py_file_loc}>`_.

""".format(
    cname_pref=f"https://{cname}/version/{switcher_version}",
    ipynb_file_loc="{{ env.docname }}.ipynb",
    py_file_loc="{{ env.docname }}.py",
)

nbsphinx_prolog = """

.. admonition:: Download this example

    Download this example as a `Jupyter Notebook <{cname_pref}/{ipynb_file_loc}>`_
    or as a `Python script <{cname_pref}/{py_file_loc}>`_.

----
""".format(
    cname_pref=f"https://{cname}/version/{switcher_version}",
    ipynb_file_loc="{{ env.docname }}.ipynb",
    py_file_loc="{{ env.docname }}.py",
)

typehints_defaults = "comma"
simplify_optional_unions = False

# -- Options for LaTeX output ------------------------------------------------
# additional logos for the latex coverpage
latex_additional_files = [watermark, ansys_logo_white, ansys_logo_white_cropped]

# change the preamble of latex with customized title page
# variables are the title of pdf, watermark
latex_elements = {"preamble": latex.generate_preamble(html_title)}

# Grouping the document tree into LaTeX files. List of tuples
# (source start file, target name, title,
#  author, documentclass [howto, manual, or own class]).
latex_documents = [
    (
        master_doc,
        f"{project}-Documentation-{__version__}.tex",
        f"{project} Documentation",
        author,
        "manual",
    ),
]

# linkcheck_exclude_documents = ["index", "getting_started/local/index", "assets"]
# linkcheck_ignore = [r"https://github.com/ansys/pyansys-geometry-binaries/.*"]

# -- Declare the Jinja context -----------------------------------------------
exclude_patterns = []
BUILD_API = True if os.environ.get("BUILD_API", "true") == "true" else False
if not BUILD_API:
    exclude_patterns.append("autosummary")

BUILD_EXAMPLES = True if os.environ.get("BUILD_EXAMPLES", "true") == "true" else False
if not BUILD_EXAMPLES:
    exclude_patterns.append("examples/**")
    exclude_patterns.append("examples.rst")

jinja_contexts = {
    "main_toctree": {
        "build_api": BUILD_API,
        "build_examples": BUILD_EXAMPLES,
    },
}

def prepare_jinja_env(jinja_env) -> None:
    """
    Customize the jinja env.

    Notes
    -----
    See https://jinja.palletsprojects.com/en/3.0.x/api/#jinja2.Environment
    """
    jinja_env.globals["project_name"] = project


nitpick_ignore_regex = [
    # Ignore typing
    (r"py:.*", r"optional"),
    # (r"py:.*", r"beartype.typing.*"),
    # (r"py:.*", r"ansys.geometry.core.typing.*"),
    (r"py:.*", r"Real.*"),
    (r"py:.*", r"SketchObject"),
    # Ignore API package
    # (r"py:.*", r"ansys.api.geometry.v0.*"),
    # (r"py:.*", r"GRPC.*"),
    (r"py:.*", r"method"),
    # Python std lib errors
    (r"py:obj", r"logging.PercentStyle"),
]
