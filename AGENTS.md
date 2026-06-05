# AGENTS.md

## Purpose

`logenrich` is a Python library (v1.0.0) that augments the standard `logging` module with simplified, INI-driven configuration. It targets Python `^3.14` and is managed with Poetry 2.2 (PEP 621 pyproject.toml). The library exposes `setup_logger` directly from `logenrich/__init__.py`; it discovers and applies `logging.ini` automatically, caching the resolved path for subsequent calls. Formatting and linting: `poetry run black logenrich; poetry run pylint logenrich`. Tests with coverage: `poetry run pytest --cov=logenrich tests --cov-report html`. Pylint must always score 10/10; minimum test coverage is 80%.

## Tree

- `logenrich/` — main package; all new modules go here
- `logenrich/__init__.py` — package entry point; hosts `setup_logger`, `_find_logging_ini`, and the `_resolved_log_ini` cache
- `tests/` — test suite mirroring `logenrich/` structure; files named `test_*.py`
- `tests/__init__.py` — test package marker
- `tests/test___init__.py` — tests for `logenrich/__init__.py`
- `.github/workflows/ci.yml` — GitHub Actions CI: lint (pylint 10/10) then test with ≥90% coverage gate
- `logging.ini` — logging configuration (console + file handlers); log file is `logenrich.log`
- `pyproject.toml` — Poetry/PEP 621 project manifest and dev dependencies
- `CHANGELOG.md` — version history in Keep a Changelog format
- `README.md` — project overview

## Rules

- Before adding a new module, check `logenrich/__init__.py` to decide what to expose publicly.
- Place all new source modules in `logenrich/`; place matching tests in `tests/` mirroring the package path.
- Use relative imports within `logenrich/` when importing from sibling modules.
- Always add module-level docstring with `Author: Ronaldo Webb` and `Since: <version>`. For new methods/classes added to existing modules on versions > 1.0.0, add author and since tags to those members.
- Use type hints on all method signatures; use `collections.abc` types instead of deprecated `typing` equivalents.
- Follow SOLID: one responsibility per class, depend on abstractions not concretions.
- Follow DRY: extract shared logic into utilities; never duplicate business logic.
- Prefer composition over inheritance; use dependency injection where applicable.
- Name conventions: `snake_case` for functions/variables, `PascalCase` for classes, `UPPER_CASE` for constants. Prefix private/protected members with `_`.
- Decompose large methods into smaller private methods.
- Never bypass `poetry` — use `poetry add` / `poetry add --dev` to manage dependencies.
- Keep version numbers consistent across `pyproject.toml`, `README.md`, and `logenrich/__init__.py` (`__version__`). Update all three together on every version bump.
- Never modify `logging.ini` or `pyproject.toml` without confirming with me first.
- After every code change, run format + lint and verify the 10/10 Pylint score before finalising.
- When you create or discover new files/folders, update the Tree above.

## Note-taking

- After each task, log any correction, preference, or pattern learned.
- Write to the relevant section above; if none fits, add to Rules. One dated line, plain language.
  e.g. "`setup_logger` must tolerate missing `logging.ini` gracefully (learned 6/5)"
- 3+ related notes on the same topic → create a `docs/` context file, move the notes there, update the Tree. Keep this file under 100 lines.
