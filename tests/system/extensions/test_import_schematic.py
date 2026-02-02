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

import os
from pathlib import Path
import tempfile
import tkinter

import pytest

from ansys.aedt.core import Circuit
from ansys.aedt.core.extensions.circuit.import_schematic import ImportSchematicData
from ansys.aedt.core.extensions.circuit.import_schematic import ImportSchematicExtension
from ansys.aedt.core.extensions.circuit.import_schematic import main


def create_temp_file(suffix, content: str="*"):
    fd, path = tempfile.mkstemp(suffix=suffix)
    with os.fdopen(fd, "w") as f:
        f.write(content)
    return path


def test_import_schematic_nonexistent_file(add_app) -> None:
    """Test import_schematic main with a non-existent file."""
    app = add_app(application=Circuit)
    data = ImportSchematicData(file_extension="/nonexistent/file.asc")
    with pytest.raises(FileNotFoundError):
        main(data)
    app.close_project(app.project_name, save=False)


def test_import_schematic_generate_button_with_circuit(add_app, test_tmp_dir) -> None:
    """Test pressing the Import button and running main with a real Circuit instance."""
    app = add_app(application=Circuit)
    # Create a temp file to simulate user input
    path = test_tmp_dir / "test_schematic.asc"
    path.write_text("*")

    # Insert the file path into the text widget as a user would
    extension = ImportSchematicExtension(withdraw=True)
    extension._text_widget.insert(tkinter.END, path)
    import_button = extension.root.nametowidget("!button2")
    import_button.invoke()
    data = extension.data
    assert isinstance(data, ImportSchematicData)
    assert Path(data.file_extension) == path
    # Now run the main logic with the data and the Circuit instance
    assert main(data) is True
    app.close_project(app.project_name, save=False)
