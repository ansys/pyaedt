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

import logging

import pytest

from ansys.aedt.core import Hfss
from ansys.aedt.core import Icepak
from ansys.aedt.core.aedt_logger import AedtLogger
from ansys.aedt.core.generic.settings import settings
from tests.conftest import NON_GRAPHICAL

LOGGER = logging.getLogger(__name__)


@pytest.fixture
def icepak_app(add_app):
    app = add_app(application=Icepak)
    yield app
    app.close_project(app.project_name, save=False)


def test_global_messenger() -> None:
    msg = AedtLogger()
    with pytest.raises(ValueError):
        msg.add_logger("Projectt")
    msg.clear_messages()

    # Add messages at different levels
    msg.add_info_message("Test desktop level - Info")
    msg.add_info_message("Test desktop level - Info", level="Design")
    msg.add_info_message("Test desktop level - Info", level="Project")
    msg.add_info_message("Test desktop level - Info", level="Global")

    # Verify messages were added
    assert len(msg._messages) == 4, "Expected 4 messages"

    # Verify all messages are info type (type 0)
    for message in msg._messages:
        assert message[0] == 0, "Expected info type (0)"
        assert "Test desktop level - Info" in message[1]

    # Verify messages can be retrieved
    messages = msg.get_messages()
    assert len(messages.info_level) >= 4

    msg.clear_messages(level=0)
    msg.clear_messages(level=3)


@pytest.mark.skipif(NON_GRAPHICAL, reason="Messages not functional in non-graphical mode")
def test_get_messages(add_app, icepak_app, test_tmp_dir) -> None:  # pragma: no cover
    app = add_app(application=Hfss, close_projects=False)
    settings.enable_desktop_logs = True
    msg = app.logger
    msg.clear_messages(level=3)
    msg.add_info_message("Test Info design level")
    msg.add_info_message("Test Info project level", "Project")
    msg.add_info_message("Test Info", "Global")
    assert msg.info_messages
    assert msg.aedt_info_messages
    assert len(msg.messages.info_level) >= 1
    assert len(msg.aedt_messages.project_level) >= 1
    box = icepak_app.modeler.create_box([0, 0, 0], [1, 1, 1])
    icepak_app.modeler.create_3dcomponent(str(test_tmp_dir / "test_m.a3dcomp"))
    box.delete()
    cmp = icepak_app.modeler.insert_3d_component(str(test_tmp_dir / "test_m.a3dcomp"))
    ipk_app_comp = cmp.edit_definition()
    msg_comp = ipk_app_comp.logger
    msg_comp.add_info_message("3dcomp, Test Info design level")
    # In 3DComponents, only Global and info level available.
    assert len(msg_comp.messages.info_level) >= 1
    ipk_app_comp.close_project()
    settings.enable_desktop_logs = False


def test_messaging(icepak_app) -> None:  # pragma: no cover
    settings.enable_desktop_logs = True
    msg = icepak_app.logger
    msg.clear_messages(level=3)
    msg.log_on_desktop = False
    assert not msg.log_on_desktop
    msg.log_on_desktop = True
    assert msg.log_on_desktop
    msg.log_on_stdout = False
    assert not msg.log_on_stdout
    msg.log_on_stdout = True
    assert msg.log_on_stdout
    msg.log_on_file = False
    assert not msg.log_on_file
    msg.log_on_file = True
    assert msg.log_on_file
    msg.add_info_message("Test Info")
    msg.add_info_message("Test Info", "Project")
    msg.add_info_message("Test Info", "Global")
    msg.add_warning_message("Test Warning at Design Level")
    msg.add_warning_message("Test Warning at Project Level", "Project")
    msg.add_warning_message("Test Warning at Global Level", "Global")
    assert msg.warning_messages
    assert msg.aedt_warning_messages
    msg.add_error_message("Test Error at Design Level")
    msg.add_error_message("Test Error at Project Level", "Project")
    msg.add_error_message("Test Error at Global Level", "Global")
    assert msg.error_messages
    assert msg.aedt_error_messages
    msg.add_info_message("Test Debug")
    msg.add_info_message("Test Debug", "Project")
    msg.add_info_message("Test Debug", "Global")
    assert len(msg.messages.info_level) > 0
    with msg.suspend_logging():
        msgs = icepak_app.logger.get_messages(level=0, aedt_messages=True)
        start_counts = [len(msgs.info_level), len(msgs.warning_level), len(msgs.error_level)]
        msg.add_info_message("Test Debug 2")
        msg.add_warning_message("Test Debug 2")
        msg.add_error_message("Test Debug 2")
        msgs = icepak_app.logger.get_messages(level=0, aedt_messages=True)
        end_counts = [len(msgs.info_level), len(msgs.warning_level), len(msgs.error_level)]
        assert start_counts == end_counts
    assert len(msg.aedt_messages.global_level) >= 4
    assert len(msg.aedt_messages.project_level) >= 4
    assert len(msg.aedt_messages.design_level) >= 4
    settings.enable_desktop_logs = False

    assert icepak_app.desktop.messenger
    assert icepak_app.desktop.clear_messages()
