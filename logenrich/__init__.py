"""
logenrich package.

A Python library that augments the standard logging module.
Exposes setup_logger for simplified, INI-driven logging configuration.

Author: Ronaldo Webb
Since: 1.0.0"""

import logging
import logging.config
import threading
from pathlib import Path

__version__ = "1.0.1"
__all__ = ["setup_logger"]

_NOT_FOUND: object = object()  # pylint: disable=invalid-name
_resolved_log_ini: str | None | object = _NOT_FOUND  # pylint: disable=invalid-name
_logging_configured: bool = False  # pylint: disable=invalid-name
_lock: threading.Lock = threading.Lock()  # pylint: disable=invalid-name


def _find_logging_ini(start_dir: str, filename: str) -> str | None:
    """
    Walk up the directory tree from start_dir looking for filename.

    Traversal is bounded by the current working directory: upward search
    continues only while start_dir (and each successive parent) is within
    the current working directory.  If start_dir is outside the current
    working directory, only that single directory is checked.

    Args:
        start_dir: Directory to begin the upward search from.
        filename: Name of the configuration file to locate.

    Returns:
        Absolute path to the first matching file found, or None.
    """
    cwd = Path.cwd().resolve()
    current = Path(start_dir).resolve()
    within_cwd = current.is_relative_to(cwd)

    while True:
        candidate = current / filename
        if candidate.is_file():
            return str(candidate)
        if not within_cwd or current == cwd:
            break
        current = current.parent
    return None


def setup_logger(
    name: str,
    conf_dir: str | None = None,
    log_ini: str | None = None,
) -> logging.Logger:
    """
    Set up and return a logger with consistent configuration.

    On first call (or when conf_dir/log_ini are provided), resolves the INI
    file by searching upward from conf_dir (defaults to the current working
    directory) for log_ini (defaults to ``logging.ini``).  The resolved path
    is cached in a module-level variable so subsequent calls with no explicit
    conf_dir or log_ini reuse it without repeating the file-system search.
    Falls back to basicConfig when no INI file can be found.

    Args:
        name: The name of the logger to create.
        conf_dir: Directory to start searching for the INI file.
            Defaults to the current working directory.
        log_ini: Name of the logging configuration file.
            Defaults to ``logging.ini``.

    Returns:
        A configured logger instance.
    """
    global _resolved_log_ini, _logging_configured  # pylint: disable=global-statement

    with _lock:
        use_cache = (
            conf_dir is None and log_ini is None and _resolved_log_ini is not _NOT_FOUND
        )
        if not use_cache:
            _resolved_log_ini = _find_logging_ini(
                conf_dir if conf_dir is not None else str(Path.cwd()),
                log_ini if log_ini is not None else "logging.ini",
            )
            _logging_configured = False

        if not _logging_configured:
            if isinstance(_resolved_log_ini, str):
                logging.config.fileConfig(
                    _resolved_log_ini, disable_existing_loggers=False
                )
            else:
                logging.basicConfig(level=logging.INFO)
            _logging_configured = True

    return logging.getLogger(name)
