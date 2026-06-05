"""
test___init__ module.

Tests for the loggingx package entry point: _find_logging_ini and setup_logger.

Author: Ronaldo Webb
Since: 1.0.0
"""

import logging
from unittest.mock import patch, MagicMock
import pytest
import loggingx


@pytest.fixture(autouse=True)
def reset_cache():
    """Reset the module-level cache before and after every test."""
    loggingx._resolved_log_ini = loggingx._NOT_FOUND  # pylint: disable=protected-access
    loggingx._logging_configured = False  # pylint: disable=protected-access
    yield
    loggingx._resolved_log_ini = loggingx._NOT_FOUND  # pylint: disable=protected-access
    loggingx._logging_configured = False  # pylint: disable=protected-access


# ---------------------------------------------------------------------------
# _find_logging_ini
# ---------------------------------------------------------------------------


class TestFindLoggingIni:
    """Tests for _find_logging_ini helper."""

    def test_finds_file_in_start_dir(self, tmp_path):
        """Returns the path when the file exists in the start directory."""
        ini = tmp_path / "logging.ini"
        ini.write_text("[loggers]\nkeys=root\n")
        result = loggingx._find_logging_ini(  # pylint: disable=protected-access
            str(tmp_path), "logging.ini"
        )
        assert result == str(ini)

    def test_finds_file_in_parent_dir(self, tmp_path):
        """Returns the path when the file exists one level up."""
        ini = tmp_path / "logging.ini"
        ini.write_text("[loggers]\nkeys=root\n")
        child = tmp_path / "subdir"
        child.mkdir()
        result = loggingx._find_logging_ini(  # pylint: disable=protected-access
            str(child), "logging.ini"
        )
        assert result == str(ini)

    def test_returns_none_when_not_found(self, tmp_path):
        """Returns None when the file does not exist anywhere in the tree."""
        child = tmp_path / "a" / "b"
        child.mkdir(parents=True)
        with patch("loggingx.Path.is_file", return_value=False):
            result = loggingx._find_logging_ini(  # pylint: disable=protected-access
                str(child), "logging.ini"
            )
        assert result is None

    def test_custom_filename(self, tmp_path):
        """Respects a custom filename."""
        ini = tmp_path / "custom.ini"
        ini.write_text("[loggers]\nkeys=root\n")
        result = loggingx._find_logging_ini(  # pylint: disable=protected-access
            str(tmp_path), "custom.ini"
        )
        assert result == str(ini)


# ---------------------------------------------------------------------------
# setup_logger
# ---------------------------------------------------------------------------


class TestSetupLogger:
    """Tests for setup_logger."""

    def test_returns_logger_instance(self, tmp_path):
        """setup_logger always returns a logging.Logger."""
        assert isinstance(
            loggingx.setup_logger("test", conf_dir=str(tmp_path)), logging.Logger
        )

    def test_resolves_and_caches_ini(self, tmp_path):
        """Successful resolution stores the path in _resolved_log_ini."""
        ini = tmp_path / "logging.ini"
        ini.write_text(
            "[loggers]\nkeys=root\n"
            "[handlers]\nkeys=consoleHandler\n"
            "[formatters]\nkeys=simpleFormatter\n"
            "[logger_root]\nlevel=DEBUG\nhandlers=consoleHandler\n"
            "[handler_consoleHandler]\nclass=StreamHandler\nlevel=DEBUG\n"
            "formatter=simpleFormatter\nargs=()\n"
            "[formatter_simpleFormatter]\nformat=%(levelname)s %(message)s\n"
        )
        loggingx.setup_logger("test", conf_dir=str(tmp_path))
        assert loggingx._resolved_log_ini == str(
            ini
        )  # pylint: disable=protected-access

    def test_fallback_to_basicconfig_when_not_found(self, tmp_path):
        """Falls back to basicConfig and leaves cache as None when INI is missing."""
        with patch.object(loggingx, "_find_logging_ini", return_value=None):
            with patch("logging.basicConfig") as mock_basic:
                loggingx.setup_logger("test", conf_dir=str(tmp_path))
        mock_basic.assert_called_once_with(level=logging.INFO)
        assert loggingx._resolved_log_ini is None  # pylint: disable=protected-access

    def test_cached_path_reused_on_subsequent_default_call(self, tmp_path):
        """Second call with no conf_dir/log_ini uses cache without file search."""
        ini = tmp_path / "logging.ini"
        ini.write_text(
            "[loggers]\nkeys=root\n"
            "[handlers]\nkeys=consoleHandler\n"
            "[formatters]\nkeys=simpleFormatter\n"
            "[logger_root]\nlevel=DEBUG\nhandlers=consoleHandler\n"
            "[handler_consoleHandler]\nclass=StreamHandler\nlevel=DEBUG\n"
            "formatter=simpleFormatter\nargs=()\n"
            "[formatter_simpleFormatter]\nformat=%(levelname)s %(message)s\n"
        )
        loggingx.setup_logger("first", conf_dir=str(tmp_path))

        with patch.object(loggingx, "_find_logging_ini") as mock_find:
            loggingx.setup_logger("second")
        mock_find.assert_not_called()

    def test_explicit_params_trigger_fresh_search(self, tmp_path):
        """Explicit conf_dir/log_ini always performs a fresh search."""
        loggingx._resolved_log_ini = (
            "/some/cached/path.ini"  # pylint: disable=protected-access
        )

        ini = tmp_path / "logging.ini"
        ini.write_text(
            "[loggers]\nkeys=root\n"
            "[handlers]\nkeys=consoleHandler\n"
            "[formatters]\nkeys=simpleFormatter\n"
            "[logger_root]\nlevel=DEBUG\nhandlers=consoleHandler\n"
            "[handler_consoleHandler]\nclass=StreamHandler\nlevel=DEBUG\n"
            "formatter=simpleFormatter\nargs=()\n"
            "[formatter_simpleFormatter]\nformat=%(levelname)s %(message)s\n"
        )

        with patch.object(
            loggingx,
            "_find_logging_ini",
            wraps=loggingx._find_logging_ini,  # pylint: disable=protected-access
        ) as mock_find:
            loggingx.setup_logger("test", conf_dir=str(tmp_path))
        mock_find.assert_called_once()
        assert loggingx._resolved_log_ini == str(
            ini
        )  # pylint: disable=protected-access

    def test_custom_log_ini_name(self, tmp_path):
        """Resolves a non-default INI filename when log_ini is provided."""
        ini = tmp_path / "custom.ini"
        ini.write_text(
            "[loggers]\nkeys=root\n"
            "[handlers]\nkeys=consoleHandler\n"
            "[formatters]\nkeys=simpleFormatter\n"
            "[logger_root]\nlevel=DEBUG\nhandlers=consoleHandler\n"
            "[handler_consoleHandler]\nclass=StreamHandler\nlevel=DEBUG\n"
            "formatter=simpleFormatter\nargs=()\n"
            "[formatter_simpleFormatter]\nformat=%(levelname)s %(message)s\n"
        )
        loggingx.setup_logger("test", conf_dir=str(tmp_path), log_ini="custom.ini")
        assert loggingx._resolved_log_ini == str(
            ini
        )  # pylint: disable=protected-access

    def test_no_explicit_params_no_cache_searches_cwd(self):
        """With no cache and no params, searches from os.getcwd()."""
        with patch("loggingx._find_logging_ini", return_value=None) as mock_find:
            with patch("logging.basicConfig"):
                loggingx.setup_logger("test")
        mock_find.assert_called_once()
        call_args = mock_find.call_args
        import os  # pylint: disable=import-outside-toplevel

        assert call_args[0][0] == os.getcwd()
        assert call_args[0][1] == "logging.ini"

    def test_fileconfig_called_when_ini_resolved(self, tmp_path):
        """fileConfig is called with the resolved path."""
        ini = tmp_path / "logging.ini"
        ini.write_text(
            "[loggers]\nkeys=root\n"
            "[handlers]\nkeys=consoleHandler\n"
            "[formatters]\nkeys=simpleFormatter\n"
            "[logger_root]\nlevel=DEBUG\nhandlers=consoleHandler\n"
            "[handler_consoleHandler]\nclass=StreamHandler\nlevel=DEBUG\n"
            "formatter=simpleFormatter\nargs=()\n"
            "[formatter_simpleFormatter]\nformat=%(levelname)s %(message)s\n"
        )
        with patch("logging.config.fileConfig") as mock_fc:
            loggingx.setup_logger("test", conf_dir=str(tmp_path))
        mock_fc.assert_called_once_with(str(ini), disable_existing_loggers=False)

    def test_logger_name_is_passed_through(self, tmp_path):
        """The returned logger has the name passed to setup_logger."""
        logger = loggingx.setup_logger("my.logger", conf_dir=str(tmp_path))
        assert logger.name == "my.logger"

    def test_only_log_ini_provided_triggers_search(self, tmp_path):
        """Providing only log_ini (no conf_dir) triggers a fresh search."""
        loggingx._resolved_log_ini = "/cached.ini"  # pylint: disable=protected-access
        with patch.object(
            loggingx, "_find_logging_ini", return_value=None
        ) as mock_find:
            with patch("logging.basicConfig"):
                loggingx.setup_logger("test", log_ini="other.ini")
        mock_find.assert_called_once()

    def test_only_conf_dir_provided_triggers_search(self, tmp_path):
        """Providing only conf_dir (no log_ini) triggers a fresh search."""
        loggingx._resolved_log_ini = "/cached.ini"  # pylint: disable=protected-access
        with patch.object(
            loggingx, "_find_logging_ini", return_value=None
        ) as mock_find:
            with patch("logging.basicConfig"):
                loggingx.setup_logger("test", conf_dir=str(tmp_path))
        mock_find.assert_called_once()
