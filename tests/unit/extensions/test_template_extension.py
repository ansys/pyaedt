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

from unittest.mock import MagicMock
from unittest.mock import patch

from ansys.aedt.core.extensions.misc import MOON
from ansys.aedt.core.extensions.misc import NO_ACTIVE_PROJECT
from ansys.aedt.core.extensions.misc import SUN
from ansys.aedt.core.extensions.templates.template_get_started import EXTENSION_TITLE
from ansys.aedt.core.extensions.templates.template_get_started import ExtensionData
from ansys.aedt.core.extensions.templates.template_get_started import TemplateExtension

MOCK_PATH = "/mock/path/file.aedt"


@patch("ansys.aedt.core.extensions.misc.active_sessions")
@patch("ansys.aedt.core.extensions.misc.Desktop")
def test_template_extension_default(mock_desktop, mock_active_sessions):
    """Test instantiation of the default extension."""
    mock_desktop_instance = MagicMock()
    mock_desktop_instance.active_project.return_value = None
    mock_desktop.return_value = mock_desktop_instance
    mock_active_sessions.return_value = {0: 0}

    extension = TemplateExtension()

    assert EXTENSION_TITLE == extension.root.title()
    assert "light" == extension.root.theme
    assert NO_ACTIVE_PROJECT == extension.active_project_name

    extension.root.destroy()


@patch("ansys.aedt.core.extensions.misc.active_sessions")
@patch("ansys.aedt.core.extensions.misc.Desktop")
def test_template_extension_toggle_theme(mock_desktop, mock_active_sessions):
    """Test toggling the theme of the extension."""
    mock_active_sessions.return_value = {0: 0}

    extension = TemplateExtension()

    extension.toggle_theme()
    assert "dark" == extension.root.theme
    assert MOON == extension.change_theme_button.cget("text")

    extension.toggle_theme()
    assert "light" == extension.root.theme
    assert SUN == extension.change_theme_button.cget("text")

    extension.root.destroy()


@patch("tkinter.filedialog.askopenfilename")
@patch("ansys.aedt.core.extensions.misc.active_sessions")
@patch("ansys.aedt.core.extensions.misc.Desktop")
def test_template_extension_with_modified_values(mock_desktop, mock_active_sessions, mock_askopenfilename):
    """Test that the modified values of the UI are returned correctly."""
    EXPECTED_RESULT = ExtensionData(0.0, 0.0, 0.0, 1.0, MOCK_PATH)
    mock_askopenfilename.return_value = MOCK_PATH
    mock_active_sessions.return_value = {0: 0}

    extension = TemplateExtension()
    extension.browse_button.invoke()

    from ansys.aedt.core.extensions.templates.template_get_started import result

    assert EXPECTED_RESULT == result
