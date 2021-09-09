============
Contributing
============

We welcome all code contributions and hope that this guide facilitate an understanding of the PyAEDT code repository. It is important to note that while the PyAEDT software package is maintained by Ansys and all submissions are reviewed thoroughly before merging, our goal is to foster a community that can support user questions and develop new features to make PyAEDT a powerful tool for all users. As such, we welcome and encourage the submittal of questions and code to this repository.

Cloning the Source Repository
--------------------------------
You can clone the source repository from PyAEDT GitHub and install the latest version in development mode by running:

.. code::

    git clone https://github.com/pyansys/pyaedt
    cd pyaedt
    pip install -e .



Questions
----------

For general or technical questions about pyAEDT, its applications, or about software usage, you can create issues at `PyAEDT Issues
<https://github.com/pyansys/PyAEDT/issues>`_, where the community or PyAEDT developers can collectively address them. The project support team can be reached at massimo.capodiferro@ansys.com.

By posting on the PyAEDT Issues page, community members with the needed expertise can address your questions, and this information is then available to all users.

Reporting Bugs
--------------------

If you encounter a bug or crash while using PyAEDT, on the PyAEDT Issues page, create an issue with an appropriate label so that it can be promptly addressed. When reporting an issue, be as descriptive as possible so that the issue can be reproduced. Whenever possible, provide tracebacks, screenshots, and sample files to help us address the issue.

Feature Requests
----------------

We encourage users to submit ideas for improvements to PyAEDT. To suggest an improvement, create an issue on the PyAEDT Issues page with a ``Feature Request`` label. Use a descriptive title and provide ample background information to help the community implement the desired functionality. For example, if you would like a reader for a specific file format, provide a link to documentation of this file format and possibly provide some sample files and screenshots. We will use the issue thread as a place to discuss and provide feedback.

Contributing New Code
-----------------------

If you have an idea for improving PyAEDT, consider first creating an issue as a feature request. We will then use this thread to discuss how best to implement the contribution.

Once you are ready to start coding, see the ``Development Practices`` section for more information.

Licensing
---------

All contributed code will be licensed under the MIT License found in the repository. If you did not write the code yourself, it is your responsibility to ensure that the existing license is compatible and included in the contributed files. You must obtain permission from the original author to relicense the code.

Development Practices
---------------------

Follow these practices when contributing directly to the PyAEDT repository.

1. Follow the Zen of Python. As silly as core Python developers are sometimes, there's much to be gained by following the basic guidelines listed in PEP 20. Without repeating them here, focus on making your additions intuitive, novel, and helpful for PyAEDT and its users.

2. Document your contributions. Include a docstring for any added function, method, or class, following numpy docstring guidelines. Always provide at least one simple use case for a new feature.

3. Test it. Because Python is an interperted language, if it's not tested, it's probably broken. At the minimum, include a unit test for each new feature within the ``tests`` directory. Ensure that each new method, class, or function has reasonable (>90% coverage).

4. Do not include any datasets for which a license is not available or commercial use is prohibited.

5. Review our Code of Conduct.

Contributing to PyAEDT through GitHub
-------------------------------------

To submit new code to PyAEDT:

1. Fork the PyAEDT GitHub repository and then clone the forked repository to your computer. 

2. In your local repository, create a new branch based on the ``Branch Naming Conventions`` section.

3. Add your new feature and commit it locally. Be sure to commit frequently as the ability to revert to past commits is often helpful, especially if your change is complex. 

4. Test often. See the ``Testing`` section for automating testing.

5. When you are ready to submit your code, create a pull request by following the steps in the ``Creating a New Pull Request`` section.

Creating a New Pull Request
~~~~~~~~~~~~~~~~~~~~~~~~~~~

Once you have tested your branch locally, create a pull request on PyAEDT and target your merge to ``main``. This will automatically run continuous integration (CI) testing and verify your changes will work across all supported platforms.

For code verification, someone from the PyAnsys development team will review your code to verify that it meets our standards. Once your code is approved, if you have write permission, you may merge the PR branch. If you don't have write permission, the reviewer or someone else with write permission will merge and delete the PR branch.

If your PR branch is a ``fix/`` branch, do not delete it because it may be necessary to merge your PR branch with the current release branch. See the next section for branch naming conventions.

Branch Naming Conventions
~~~~~~~~~~~~~~~~~~~~~~~~~

To streamline development, we have the following requirements for naming branches. These requirements help the core developers know what kind of changes any given branch is introducing before looking at the code.

-  ``fix/``: any bug fixes, patches, or experimental changes that are
   minor
-  ``feat/``: any changes that introduce a new feature or significant
   addition
-  ``junk/``: for any experimental changes that can be deleted if gone
   stale
-  ``maint/``: for general maintenance of the repository or CI routines
-  ``doc/``: for any changes only pertaining to documentation
-  ``no-ci/``: for low-impact activity that should not trigger the CI
   routines
-  ``testing/``: improvements or changes to testing
-  ``release/``: releases (see below)

Testing
~~~~~~~
When making changes, periodically test locally before creating a pull request. Because the following tests are executed after any commit or pull request, we ask that you perform the following sequence locally to track down any new issues from your changes.

. code::

    pip install -r requirements_test.txt

Run the primary test suite and generate a coverage report with:

.. code::

    pytest -v --cov _unittest

Spelling and Code Style
~~~~~~~~~~~~~~~~~~~~~~~
If you are using Linux or Mac OS, run spelling and coding style checks with:


.. code::

    cd <local pyvista root directory>
    pip install -r requirements_style.txt
    make

Any misspelled words will be reported. You can add words to be ignored to `ignore_words.txt`

Documentation
-------------
Documentation for PyAEDT is generated from three sources:

- Docstrings from the classes, functions, and modules of PyAEDT using `sphinx.ext.autodoc`.
- reStructuredText (RST) files from ``doc/``
- Examples from `examples/`

General usage and API descriptions should be placed within ``doc/source`` and method docstrings. Full examples should be placed in ``examples/``.

Documentation Style and Organization
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Docstrings should follow the numpy guidelines. Documentation from ``doc/`` use reStructuredText format. Examples from ``examples/`` should be PEP8 compliant and will be compiled dynamically during the build process. Always ensure that they run properly locally as they will be verified through the continuous integration performed on GitHub Actions.

Documentation for the latest stable release of PyAEDT is hosted at
`PyAEDT Documentation <https://aedtdocs.pyansys.com>`_.  The latest development version tracking the `main` branch can be found found at `Development PyAEDT Documentation <https://dev.aedtdocs.pyansys.com/>`_, which is kept up-to-date automatically via GitHub actions.


Building the Documentation Locally
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
You can build and verify the HTML documentation locally by installing
Sphinx and the other documentation build dependencies.

First, optionally install PyAEDT in development mode with:

.. code::

   pip install -e .

Then, install the build requirements for documentation with:

.. code::

   pip install -r requirements_docs.txt


Next, if running Linux/Mac OS, build the documentation with:

.. code::

    make -C doc html

Otherwise, if running Windows, build the documentation by running:

.. code::

   cd doc
   make.bat html

After the documentation builds successfully, you can open the local build by opening in your brower the file ``index.html`` in ``doc/_build/html/``.

Continuous Integration and Continuous Delivery (CI/CD)
------------------------------------------------------

The PyAEDT project uses continuous integration and delivery (CI/CD) to automate the building, testing, and deployment tasks. The CI pipeline is deployed on both GitHub Actions and Azure Pipelines and performs the following tasks:

- Module wheel build
- Core API testing
- Spelling and style verification
- Documentation build

Branching Model
~~~~~~~~~~~~~~~

This project has a branching model that enables rapid development of features without sacrificing stability. This branching model closely follows the trunk-based development approach.

- The ``main`` branch is the main development branch. All features, patches, and other branches should be merged here. While all PRs should pass all applicable CI checks, this branch may be functionally unstable as changes might have introduced unintended side-effects or bugs that were not caught through unit testing.
- There will be one or many release/ branches based on minor releases (for example ``release/0.2``) that contain a stable version of the code base, which is also reflected on ``PyPi/``. Hotfixes from ``fix/`` branches should be merged both to ``main`` and to these branches. When create a new patch release is necessary, these release branches will have their `__version__.py` updated and be tagged with a patched semantic version (for example ``0.2.1``). This triggers CI to push to PyPi, and allows us to rapidly push hotfixes for past versions of PyAEDT without having to worry about untested features.
- When a minor release candidate is ready, a new release branch will be created from ``main`` with the next incremented minor version (for example release/0.2), which will be thoroughly tested. When deemed stable, the release branch will be tagged with the version (``0.2.0`` in this case), and if necessary merged with ``main`` if any changes were pushed to it. Feature development then continues on ``main`` and any hotfixes will now be merged with this release. Older release branches should not be deleted so they can be patched if needed.

Minor Release Steps
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Minor releases are feature and bug releases that improve the functionality and stability of PyAEDT. Before crfeating a minor release, do the following:

1. Create a new branch from the ``main`` branch with name ``release/``MAJOR.MINOR (for example ``release/0.2``).

2. Locally run all tests as outlined in the ``Testing`` section and ensure that all are passing.

3. Locally test and build the documentation with link checking to make sure that no links are outdated. Be sure to run ``make clean`` to ensure that no results are cached.

    .. code::

        cd docs
        make clean  # deletes the sphinx-gallery cache
        make html -b linkcheck

4. After building the documentation, open the local build and examine the examples gallery for any obvious issues.

5. Update the version numbers in ``pyaedt/version.txt`` and commit this file. Push the branch to GitHub and create a new PR for this release that merges it to ``main``. While effort is focused on the release, development to ``main`` should be limited.

6. Wait for the PyAEDT community and developers to functionally test the new release. 

   Testers should locally install this branch and use it in production. Any bugs that they  identify should have their hotfixes pushed to this release branch.

   When the branch is deemed as stable for public release, the PR will be merged to ``main`` and the ``main`` branch will be tagged with a MAJOR.MINOR.0 release. The release
   branch will not be deleted. 

7. Tag the release with:

    .. code::

	git tag <MAJOR.MINOR.0>
        git push origin --tags

8. Create a list of all changes for the release. It is often helpful to leverage GitHub's compare feature to see the differences from the last tag and the ``main`` branch. Be sure to acknowledge new contributors by their GitHub username and place mentions where appropriate if specific contributors are to be thanked for new features.

9. Place your release notes from step 8 in the description within PyAEDT Releases.

Patch Release Steps
~~~~~~~~~~~~~~~~~~~

Patch releases are for critical and important bug fixes that cannot or should not wait until a minor release. Here are the steps for a patch release:

1. Push necessary bug fixes to the applicable release branch. This will generally be the latest release branch (for example ``release/0.2``).

2. Update ``version.txt`` with the next patch increment (``0.2.1`` in this case), commit it, and open a pull request to merge with the release branch.

This gives the PyAEDT developers and community a chance to validate and approve the bug fix release. Any additional hotfixes should be outside of this pull request.

3. When the pull request is approved, merge it with the release branch, but not ``main`` branch because there is no reason to increment the version of the ``main`` branch.

4. Create a tag from the release branch with the applicable version number. (See above for the correct steps.)

5. If deemed necessary, create a ``Release Notes`` page.
