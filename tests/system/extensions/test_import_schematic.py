# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 - 2025 ANSYS, Inc. and/or its affiliates.
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
import tempfile
import tkinter

import pytest

from ansys.aedt.core.extensions.circuit.import_schematic import ImportSchematicData
from ansys.aedt.core.extensions.circuit.import_schematic import ImportSchematicExtension
from ansys.aedt.core.extensions.circuit.import_schematic import main


def create_temp_file(suffix, content="*"):
    fd, path = tempfile.mkstemp(suffix=suffix)
    with os.fdopen(fd, "w") as f:
        f.write(content)
    return path


def test_import_schematic_nonexistent_file():
    """Test import_schematic main with a non-existent file."""

    data = ImportSchematicData(file_extension="/nonexistent/file.asc")
    with pytest.raises(FileNotFoundError):
        main(data)


def test_import_schematic_generate_button_with_circuit(add_app):
    """Test pressing the Import button and running main with a real Circuit instance."""

    # Create a temp file to simulate user input
    path = create_temp_file(".asc")

    # Insert the file path into the text widget as a user would
    extension = ImportSchematicExtension(withdraw=True)
    extension._text_widget.insert(tkinter.END, path)
    import_button = extension.root.nametowidget("!button2")
    import_button.invoke()
    data = extension.data
    assert isinstance(data, ImportSchematicData)
    assert data.file_extension == path
    # Now run the main logic with the data and the Circuit instance
    assert main(data) is True
    os.remove(path)
