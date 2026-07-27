# Copilot workspace instructions

## Hard exclusions
Never read, search, summarize, or reference anything under:

- `doc/`
- `LICENSES/`
- `.venv/`
- `.github/actions/`
- `.github/ISSUE_TEMPLATE/`
- `.github/workflows/`
- `.reuse/`
- `.ci/`
- `.claude-plugin/`
- `.git/`
- `.idea/`
- `.vscode/`
- `.pytest_cache/`
- `.ruff_cache/`

Never read, search, summarize, or reference any of these root files:

- `AUTHORS`
- `batch.log`
- `CHANGELOG.md`
- `CODE_OF_CONDUCT.md`
- `CONTRIBUTING.md`
- `CONTRIBUTORS.md`
- `ignore_words.txt`
- `LICENSE`
- `Makefile`
- `MANIFEST.in`
- `README.md`
- `README_CN.md`
- `SECURITY.md`
- `uv.lock`
- `.codacy.yml`
- `.git-blame-ignore-revs`
- `.gitattributes`
- `.gitignore`
- `.pre-commit-config.yaml`

Treat these paths as out-of-scope for all answers unless I explicitly override in the prompt.
If a request conflicts with these exclusions, ask before accessing excluded paths.

## Punctuation rules
- Never use em dash (—, U+2014) or en dash (–, U+2013) in generated code, comments, docstrings, or string literals.
- Use only the standard ASCII hyphen-minus (-) character.
- In sentences, use the comma (,) and period (.) to separate periods. Avoid dash unless they are part of the code or string literals.
- To set off subordinate clauses or parenthetical remarks, use commas or parentheses instead of dashes.


## Testing guidelines

### Test framework
- Always use `pytest`. Never use `unittest` as the test framework (using `unittest.mock` for mocking is allowed).
- Place tests in the correct directory:
  - `tests/unit/` for unit tests (no AEDT connection, no I/O)
  - `tests/integration/` for integration tests (real AEDT connection required)
  - `tests/system/` for system tests (real AEDT connection required)

### Mocking AEDT communication
- In `tests/unit/` only, mock all communication with AEDT. Never open a real AEDT session.
- Use `unittest.mock.patch`, `unittest.mock.MagicMock`, or `unittest.mock.patch.object` for mocking.
- To suppress the desktop fixture in a unit test module, override it explicitly:

  ```python
  @pytest.fixture(scope="module", autouse=True)
  def desktop() -> None:
      """Override the desktop fixture to not open the Desktop when running this test module."""
      return
