# Changelog

## 1.0.0 - 2026-06-04

### Added
- Initial release of the loggingx library.
- `setup_logger` exposed directly from `loggingx/__init__.py` for simplified, INI-driven logging configuration.
- `_find_logging_ini` helper that walks the directory tree upward to locate a `logging.ini` file.
- Module-level `_resolved_log_ini` cache to avoid repeated file-system searches on subsequent `setup_logger` calls.
- Falls back to `logging.basicConfig` at `INFO` level when no configuration file is found.
- `logging.ini` bundled with console (`StreamHandler`) and file (`FileHandler`) logging handlers.
