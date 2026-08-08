.. _developer_notes:

===============
Developer notes
===============

This section provides additional guidance for developers contributing to PyAEDT,
including information about working with Testmon, tracking coverage, and handling
edge cases during development.

Tracking coverage locally
-------------------------

Due to limitations with Testmon and coverage tracking in the CI/CD pipeline, developers must
track test coverage locally before submitting pull requests. While the CI/CD uses Testmon to
selectively run affected tests for faster feedback, coverage is only tracked comprehensively
during nightly runs.

Why track coverage locally?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

- **CI limitation**: Testmon's selective test execution means only tests affected by your changes
  run in the PR workflow, which doesn't provide complete coverage metrics for your changes.
- **Nightly validation**: Full coverage is checked nightly to ensure overall project health.
- **Your responsibility**: Contributors must verify that new code has adequate coverage
  (minimum 85% for all new code) before submitting PRs.

Running tests with coverage locally
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

To measure coverage for your changes, run pytest with coverage tracking. You can use either
your IDE's built-in coverage tools or the command line.

**Using pytest-cov (command line):**

1. Install pytest-cov if not already installed:

   .. code:: bash

      pip install pytest-cov

2. Run tests with coverage for the specific test suites related to your changes:

   .. code:: bash

      # For unit tests
      pytest tests/unit --cov=ansys.aedt.core --cov-report=term-missing --cov-report=html

      # For system tests
      pytest tests/system --cov=ansys.aedt.core --cov-report=term-missing --cov-report=html

3. Review the coverage report:

   - **Terminal output**: Shows coverage percentage and lists uncovered lines with ``--cov-report=term-missing``
   - **HTML report**: Open ``htmlcov/index.html`` in a browser for detailed, navigable coverage information

**Using VSCode:**

1. Install the Python extension if not already installed.
2. Open the Testing sidebar (beaker icon).
3. Click "Run Test with Coverage" button in the Test Explorer toolbar.
4. After tests complete, view:

   - Coverage summary in the Test Explorer (percentage by file)
   - Highlighted covered/uncovered lines in the editor

**Using PyCharm:**

1. Configure pytest as the test runner: **Settings** → **Tools** → **Python Integrated Tools** → **Default test runner** → **pytest**
2. Right-click a test file or configuration and choose **Run with Coverage**.
3. View coverage summary and highlighted lines in the editor.

Best practices for coverage tracking
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

- **Run coverage before pushing**: Always check coverage locally before pushing your changes.
- **Target 85% minimum**: Ensure new code has at least 85% test coverage.
- **Focus on relevant tests**: Run coverage for the specific modules you've modified rather than the entire test suite.
- **Use HTML reports**: The HTML coverage report (``htmlcov/index.html``) provides the most detailed view of what's covered.
- **Test both unit and system**: Depending on your changes, run coverage for both unit and system tests to ensure comprehensive coverage.
- **Isolate your changes**: To see coverage specifically for your modifications, run tests only for the modules you've changed.

Testmon considerations
~~~~~~~~~~~~~~~~~~~~~~

Edge cases and considerations
------------------------------

This section covers common edge cases and considerations when working with PyAEDT's CI/CD pipeline
and Testmon integration.

Multiple open pull requests
~~~~~~~~~~~~~~~~~~~~~~~~~~~

When multiple PRs are open simultaneously, each PR:

- Restores the same baseline cache from ``main``.
- Runs only tests affected by its own changes.
- Does not interfere with other PRs since no PR modifies the shared cache.

This design ensures isolation between concurrent PR workflows.

Cache update in progress while PR runs
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

If a PR workflow starts while the ``update-testmondata-cache.yml`` workflow is running on ``main``:

- The PR workflow **waits** for up to 10 minutes for the cache update to complete.
- If the cache update succeeds, the PR uses the fresh cache.
- If the cache update fails or times out, the PR workflow **fails** with an error message instructing the user to relaunch the cache update workflow.

This mechanism prevents PRs from running with stale or inconsistent cache data.

Cache update workflow fails
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

If the ``update-testmondata-cache.yml`` workflow fails:

- Subsequent PRs fail at the "Wait for master cache update" step.
- The error message directs users to relaunch the workflow at:
  ``https://github.com/ansys/pyaedt/actions/workflows/update-testmondata-cache.yml``
- Once the cache update completes successfully, PR workflows can proceed.

Pruning Testmon caches
~~~~~~~~~~~~~~~~~~~~~~~

A separate workflow (``prune-testmon-caches.yml``) can be manually triggered to delete all Testmon
caches. This is useful when:

- Cache corruption is suspected.
- A major refactoring requires rebuilding the dependency graph from scratch.
- Cache storage limits are approached.

Keeping PRs updated with main
------------------------------

.. important::

   **PRs must be updated to the latest ``main`` branch before merging.**

This requirement ensures that:

1. **Cache consistency**: The pull request's Testmon run is validated against the same codebase state that the cache was built from. If a PR is behind ``main``, its Testmon data may not accurately reflect which tests need to run.

2. **Merge conflicts**: Updating ensures merge conflicts are resolved before merging.

3. **Test coverage**: Tests that were added or modified in ``main`` since the PR was created are
   executed against the pull request's changes.

How to update your PR
~~~~~~~~~~~~~~~~~~~~~

Use one of the following methods to update your PR with the latest ``main`` branch:

**Command line:**

.. code:: bash

   git fetch origin main
   git merge main
   # Resolve any conflicts if they occur
   git push

**GitHub UI:**

Use the "Update branch" button if available on your pull request page.

.. note::

   Always verify that your tests still pass and coverage remains adequate after updating your branch.
