# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 - 2026 ANSYS, Inc. and/or its affiliates.
# SPDX-License-Identifier: MIT
#
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

"""Test utility functions of PyAEDT."""

import os
import time
from unittest.mock import MagicMock
from unittest.mock import PropertyMock
from unittest.mock import patch

import pytest

from ansys.aedt.core.generic.general_methods import pyaedt_function_handler
from ansys.aedt.core.generic.settings import ALLOWED_AEDT_ENV_VAR_SETTINGS
from ansys.aedt.core.generic.settings import ALLOWED_GENERAL_SETTINGS
from ansys.aedt.core.generic.settings import ALLOWED_GRPC_SETTINGS
from ansys.aedt.core.generic.settings import ALLOWED_LOG_SETTINGS
from ansys.aedt.core.generic.settings import ALLOWED_LSF_SETTINGS
from ansys.aedt.core.generic.settings import Settings
from ansys.aedt.core.generic.settings import settings
from ansys.aedt.core.internal.checks import AEDTRuntimeError
from ansys.aedt.core.internal.checks import min_aedt_version

SETTINGS_RELEASE_ON_EXCEPTION = settings.release_on_exception
SETTINGS_ENABLE_ERROR_HANDLER = settings.enable_error_handler
ERROR_MESSAGE = "Dummy message."
TOML_DATA = {"key_0": "dummy", "key_1": 12, "key_2": [1, 2], "key_3": {"key_4": 42}}
CURRENT_YEAR = current_year = time.localtime().tm_year
CURRENT_YEAR_VERSION = f"{CURRENT_YEAR}.2"
NEXT_YEAR_VERSION = f"{CURRENT_YEAR + 1}.2"
PREVIOUS_YEAR_VERSION = f"{CURRENT_YEAR - 1}.2"


@pytest.fixture(scope="module", autouse=True)
def desktop() -> None:
    """Override the desktop fixture to DO NOT open the Desktop when running this test class"""
    return


@pyaedt_function_handler()
def foo(trigger_exception: bool=True):
    """Some dummy function used for testing."""
    if trigger_exception:
        raise Exception(ERROR_MESSAGE)


@patch.object(Settings, "logger", new_callable=PropertyMock)
@patch("ansys.aedt.core.internal.desktop_sessions._desktop_sessions")
def test_handler_release_on_exception_called(mock_sessions, mock_logger) -> None:
    """Test handler while activating error handler."""
    mock_session = MagicMock()
    mock_sessions.values.return_value = [mock_session]
    mock_logger.return_value = MagicMock()
    settings.enable_error_handler = True

    # Check that release desktop is called once
    foo()
    assert mock_session.release_desktop.assert_called_once

    # Teardown
    settings.enable_error_handler = SETTINGS_ENABLE_ERROR_HANDLER
    settings.release_on_exception = SETTINGS_RELEASE_ON_EXCEPTION


@patch.object(Settings, "logger", new_callable=PropertyMock)
@patch("ansys.aedt.core.internal.desktop_sessions._desktop_sessions")
def test_handler_release_on_exception_not_called(mock_sessions, mock_logger) -> None:
    """Test handler while deactivating error handler."""
    mock_session = MagicMock()
    mock_sessions.values.return_value = [mock_session]
    mock_logger.return_value = MagicMock()
    settings.enable_error_handler = True
    settings.release_on_exception = False

    # Check that release desktop is not called
    foo()
    assert not mock_session.release_desktop.assert_not_called()

    # Teardown
    settings.enable_error_handler = SETTINGS_ENABLE_ERROR_HANDLER
    settings.release_on_exception = SETTINGS_RELEASE_ON_EXCEPTION


@patch.object(Settings, "logger", new_callable=PropertyMock)
def test_handler_enable_error_handler(mock_logger) -> None:
    """Test handler while activating/deactivating error handler."""
    mock_logger.return_value = MagicMock()
    settings.enable_error_handler = True
    assert not foo()

    settings.enable_error_handler = False
    with pytest.raises(Exception) as exec_info:
        foo()
    assert str(exec_info.value) == ERROR_MESSAGE

    # Teardown
    settings.enable_error_handler = SETTINGS_ENABLE_ERROR_HANDLER


def test_handler_deprecation_log_warning() -> None:
    """Test handler deprecation argument mechanism."""
    with pytest.raises(Exception, match=ERROR_MESSAGE):
        foo(trigger_exception=True)


def test_settings_load_yaml(test_tmp_dir) -> None:
    """Test loading a configure file with correct input."""
    default_settings = Settings()

    # Create temporary YAML configuration file
    yaml_path = test_tmp_dir / "pyaedt_settings.yaml"
    yaml_path.write_text(
        """
    log:
        global_log_file_name: 'dummy'
    lsf:
        lsf_ram : 50
    general:
        desktop_launch_timeout: 12
        num_cores: 12
    """
    )

    default_settings.load_yaml_configuration(str(yaml_path))

    assert default_settings.global_log_file_name == "dummy"
    assert default_settings.num_cores == 12
    assert default_settings.desktop_launch_timeout == 12
    assert default_settings.lsf_ram == 50


def test_settings_load_yaml_with_non_allowed_attribute_key(tmp_path) -> None:
    """Test loading a configuration file with invalid key."""
    default_settings = Settings()

    # Create temporary YAML configuration file
    yaml_path = tmp_path / "pyaedt_settings.yaml"
    yaml_path.write_text(
        """
    # Valid key
    log:
        enable_debug_edb_logger: false
    # Invalid key
    general:
        dummy: 12.0
    """
    )

    default_settings.load_yaml_configuration(str(yaml_path), raise_on_wrong_key=False)
    assert not hasattr(default_settings, "dummy")

    with pytest.raises(KeyError) as excinfo:
        default_settings.load_yaml_configuration(str(yaml_path), raise_on_wrong_key=True)
        assert str(excinfo) in "Key 'dummy' is not part of the allowed keys"


def test_settings_load_yaml_with_non_allowed_env_variable_key(tmp_path) -> None:
    """Test loading a configuration file with invalid key."""
    default_settings = Settings()

    # Create temporary YAML configuration file
    yaml_path = tmp_path / "pyaedt_settings.yaml"
    yaml_path.write_text(
        """
    # Valid key
    log:
        enable_debug_edb_logger: false
    # Invalid key
    aedt_env_var:
        AEDT_DUMMY: 12.0
    """
    )

    default_settings.load_yaml_configuration(str(yaml_path), raise_on_wrong_key=False)
    assert "AEDT_DUMMY" in default_settings.aedt_environment_variables

    with pytest.raises(KeyError) as excinfo:
        default_settings.load_yaml_configuration(str(yaml_path), raise_on_wrong_key=True)
        assert str(excinfo) in "An environment variable key is not part of the allowed keys."


def test_settings_attributes() -> None:
    """Test accessing settings attributes."""
    default_settings = Settings()

    for attr in ALLOWED_LOG_SETTINGS + ALLOWED_GENERAL_SETTINGS + ALLOWED_LSF_SETTINGS:
        _ = getattr(default_settings, attr)
    for attr in ALLOWED_AEDT_ENV_VAR_SETTINGS:
        if os.name != "posix" and attr == "ANS_NODEPCHECK":
            continue
        _ = getattr(default_settings, "aedt_environment_variables")[attr]


def test_settings_check_allowed_properties() -> None:
    """Test that every non python setting is an allowed settings."""
    import inspect

    default_settings = Settings()
    # All allowed attributes
    allowed_properties_expected = (
        ALLOWED_LOG_SETTINGS
        + ALLOWED_GENERAL_SETTINGS
        + ALLOWED_LSF_SETTINGS
        + ALLOWED_GRPC_SETTINGS
        + ["aedt_environment_variables"]
    )
    # Check attributes that are not related to Python objects (otherwise they are not 'allowed')
    properties_ignored = ["formatter", "logger", "remote_rpc_session", "time_tick", "public_dir"]

    def get_properties(obj):
        return [name for name, _ in inspect.getmembers(type(obj), lambda v: isinstance(v, property))]

    settings_properties = get_properties(default_settings)
    settings_properties = filter(lambda attr: attr not in properties_ignored, settings_properties)

    assert sorted(set(allowed_properties_expected)) == sorted(settings_properties)


def test_settings_check_allowed_env_variables() -> None:
    """Test that known environment variables are allowed."""
    default_settings = Settings()
    env_variables = default_settings.aedt_environment_variables.keys()
    allowed_env_var_expected = ALLOWED_AEDT_ENV_VAR_SETTINGS
    if os.name != "posix":
        allowed_env_var_expected.remove("ANS_NODEPCHECK")

    assert sorted(allowed_env_var_expected) == sorted(env_variables)


def test_read_toml(tmp_path) -> None:
    """Test loading a TOML file."""
    from ansys.aedt.core.generic.file_utils import read_toml

    file_path = tmp_path / "dummy.toml"
    content = """
    key_0 = 'dummy'
    key_1 = 12
    key_2 = [1,2]
    [key_3]
    key_4 = 42
    """
    file_path.write_text(content, encoding="utf-8")

    res = read_toml(file_path)
    assert TOML_DATA == res


def test_write_toml(tmp_path) -> None:
    """Test writing a TOML file."""
    from ansys.aedt.core.generic.file_utils import _create_toml_file

    file_path = tmp_path / "dummy.toml"
    _create_toml_file(TOML_DATA, file_path)

    assert file_path.exists()


def test_min_aedt_version_success_with_common_attributes_names() -> None:
    class Dummy:
        """Dummy class to test min version with common attribute."""

        odesktop = MagicMock()
        odesktop.GetVersion.return_value = CURRENT_YEAR_VERSION

        @min_aedt_version(PREVIOUS_YEAR_VERSION)
        def old_method(self) -> None:
            pass

    dummy = Dummy()
    dummy.old_method()


def test_min_aedt_version_success_with_app_private_attribute() -> None:
    class Dummy:
        """Dummy class to test min version with __app attribute."""

        odesktop = MagicMock()
        odesktop.GetVersion.return_value = CURRENT_YEAR_VERSION
        __app = odesktop

        @min_aedt_version(PREVIOUS_YEAR_VERSION)
        def old_method(self) -> None:
            pass

    dummy = Dummy()
    dummy.old_method()


def test_min_aedt_version_success_with_desktop_class() -> None:
    class Dummy:
        """Dummy class to test min version with __app attribute."""

        odesktop = MagicMock()
        odesktop.GetVersion.return_value = CURRENT_YEAR_VERSION
        desktop_class = MagicMock()
        desktop_class.odesktop = odesktop

        @min_aedt_version(PREVIOUS_YEAR_VERSION)
        def old_method(self) -> None:
            pass

    dummy = Dummy()
    dummy.old_method()


def test_min_aedt_version_raise_error_on_future_version() -> None:
    class Dummy:
        """Dummy class to test min version."""

        odesktop = MagicMock()
        odesktop.GetVersion.return_value = CURRENT_YEAR_VERSION

        @min_aedt_version(NEXT_YEAR_VERSION)
        def future_method(self) -> None:
            pass

    dummy = Dummy()
    pattern = (
        f"The method 'future_method' requires a minimum Ansys release version of {NEXT_YEAR_VERSION}, "
        "but the current version used is .+"
    )

    with pytest.raises(AEDTRuntimeError, match=pattern):
        dummy.future_method()


def test_min_aedt_version_raise_error_on_non_decorable_object() -> None:
    class Dummy:
        @min_aedt_version(PREVIOUS_YEAR_VERSION)
        def dummy_method(self) -> None:
            pass

    dummy = Dummy()

    with pytest.raises(AEDTRuntimeError, match="The AEDT desktop object is not available."):
        dummy.dummy_method()
