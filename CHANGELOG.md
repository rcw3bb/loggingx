# Changelog

## 1.0.1 - 2026-06-07

### Changed
- `_find_logging_ini` now bounds upward directory traversal to the current working directory (CWD); search stops at CWD and will not climb above it.
- When `start_dir` is outside CWD, only that single directory is inspected instead of traversing all the way to the filesystem root.

## 1.0.0 - 2026-06-04

### Added
- Initial release of the logenrich library.
- `setup_logger` exposed directly from `logenrich/__init__.py` for simplified, INI-driven logging configuration.
- `_find_logging_ini` helper that walks the directory tree upward to locate a `logging.ini` file.
- Module-level `_resolved_log_ini` cache to avoid repeated file-system searches on subsequent `setup_logger` calls.
- Falls back to `logging.basicConfig` at `INFO` level when no configuration file is found.
- `logging.ini` bundled with console (`StreamHandler`) and file (`FileHandler`) logging handlers.
