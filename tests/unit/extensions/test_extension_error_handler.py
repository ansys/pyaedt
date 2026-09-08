# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 - 2026 Synopsys, Inc. and ANSYS, Inc. All rights reserved.
# SPDX-License-Identifier: MIT

from types import SimpleNamespace

from ansys.aedt.core.extensions.templates import extension_error_handler


def test_main_inherits_stderr(monkeypatch):
    """The script stderr must remain connected to the interactive console."""
    run_calls = []

    def mock_run(*args, **kwargs):
        run_calls.append((args, kwargs))
        return SimpleNamespace(returncode=0)

    monkeypatch.setattr(extension_error_handler.subprocess, "run", mock_run)
    monkeypatch.setattr(extension_error_handler.sys, "argv", ["handler", "--script", "extension.py"])

    extension_error_handler.main()

    assert run_calls == [
        (
            ([extension_error_handler.sys.executable, "extension.py"],),
            {"env": extension_error_handler.os.environ.copy(), "text": True},
        )
    ]
