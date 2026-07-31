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

Treat these paths as out-of-scope for all answers unless explicitly overridden in the prompt.
If a request conflicts with these exclusions, ask before accessing excluded paths.

## Punctuation rules
- Never use em dash (—, U+2014) or en dash (–, U+2013) in generated code, comments, docstrings, or string literals.
- Use only the standard ASCII hyphen-minus (-) character.
- In sentences, use the comma (,) and period (.) to separate clauses. Avoid dashes unless they are part of code or string literals.
- To set off subordinate clauses or parenthetical remarks, use commas or parentheses instead of dashes.

## Code comment rules
- Always use English for code comments, docstrings, and documentation.

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
  ```

## Secure Python coding for CI compliance

Avoid Bandit CI failures (B101 assert_used, B110 try_except_pass) in PyAEDT Python code.

### When to apply
Any time you write or edit Python code that will run through CI security checks (Bandit).

### Rule 1: Never use `assert` for runtime validation
`assert` can be stripped in optimized mode and is flagged as B101. Replace with an explicit check and exception.

```python
# Bad
assert obj is not None
return obj.value

# Good
if obj is None:
    raise RuntimeError("Object is not initialized.")
return obj.value
```

### Rule 2: Never silently swallow exceptions
`except Exception: pass` is flagged as B110. Make failure handling explicit.

```python
# Bad
try:
    cleanup()
except Exception:
    pass

# Good - pick one:
except Exception as exc:
    logging.getLogger("Global").debug("Ignoring cleanup error: %s", exc)
# or
except Exception:
    return
# or catch a narrower exception (e.g. TclError)
```

### Rule 3: Guard optional values before use
Bind once, check once, then use the local variable.

```python
desktop = self.desktop
if desktop is None:
    raise RuntimeError("Desktop session is not initialized.")
return desktop.project_list
```

### Rule 4: Use the right exception type

- `ValueError` - invalid input or argument
- `RuntimeError` - missing or uninitialized state
- Narrower or library-specific exception when one clearly fits

### Rule 5: Keep fixes minimal
Fix only the flagged pattern. Do not refactor, add helpers, or restructure unless the same check repeats often enough to justify it.

Self-check before finishing:
- No `assert` used for runtime checks
- No bare `except Exception: pass`
- Optional values validated with explicit guard clauses
- Appropriate exception type used
- Change is minimal and behavior-preserving otherwise
