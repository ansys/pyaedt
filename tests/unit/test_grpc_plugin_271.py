import sys
from types import ModuleType
from unittest.mock import MagicMock

from ansys.aedt.core.internal.grpc_plugin_271 import AEDT


def test_aedt_release_clears_cached_scriptenv_connection(monkeypatch):
    script_env = ModuleType("ScriptEnv")
    channel = MagicMock()
    release = MagicMock()
    script_env.Release = release
    script_env.gChannel = channel
    script_env.gDesktop = MagicMock()
    script_env.gSSLClientCredentials = MagicMock()
    monkeypatch.setitem(sys.modules, "ScriptEnv", script_env)

    aedt = AEDT("installer_path")
    aedt._odesktop = MagicMock()
    aedt.Release()

    release.assert_called_once_with()
    channel.close.assert_called_once_with()
    assert script_env.gChannel is None
    assert script_env.gDesktop is None
    assert script_env.gSSLClientCredentials is None
    assert aedt.odesktop is None


def test_aedt_release_clears_connection_when_scriptenv_release_fails(monkeypatch):
    script_env = ModuleType("ScriptEnv")
    channel = MagicMock()
    script_env.Release = MagicMock(side_effect=RuntimeError("release failed"))
    script_env.gChannel = channel
    script_env.gDesktop = MagicMock()
    script_env.gSSLClientCredentials = MagicMock()
    monkeypatch.setitem(sys.modules, "ScriptEnv", script_env)

    aedt = AEDT("installer_path")
    aedt._odesktop = MagicMock()
    try:
        aedt.Release()
    except RuntimeError as error:
        assert str(error) == "release failed"
    else:
        raise AssertionError("ScriptEnv.Release errors should be propagated")

    channel.close.assert_called_once_with()
    assert script_env.gChannel is None
    assert script_env.gDesktop is None
    assert script_env.gSSLClientCredentials is None
    assert aedt.odesktop is None
