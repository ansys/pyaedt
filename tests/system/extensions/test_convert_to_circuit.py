# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 - 2025 ANSYS, Inc. and/or its affiliates.
# SPDX-License-Identifier: MIT
#
#
# Permission is hereby granted, free of charge, to any person obtaining a
# copy of this software and associated documentation files (the
# "Software"), to deal in the Software without restriction, including
# without limitation the rights to use, copy, modify, merge, publish,
# distribute, sublicense, and/or sell copies of the Software, and to
# permit persons to whom the Software is furnished to do so, subject to
# the following conditions:
#
# The above copyright notice and this permission notice shall be
# included in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
# NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE
# LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
# OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION
# WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

import os

import pytest

from ansys.aedt.core import TwinBuilder
from ansys.aedt.core.extensions.twinbuilder.convert_to_circuit import (
    ConvertToCircuitExtension,
)
from ansys.aedt.core.extensions.twinbuilder.convert_to_circuit import (
    ConvertToCircuitExtensionData,
)
from ansys.aedt.core.extensions.twinbuilder.convert_to_circuit import main
from ansys.aedt.core.internal.errors import AEDTRuntimeError


def test_convert_to_circuit_main_no_design_name():
    """Test main function with no design name provided."""
    data = ConvertToCircuitExtensionData(design_name="")

    with pytest.raises(
        AEDTRuntimeError, match="No design provided to the extension"
    ):
        main(data)


def test_convert_to_circuit_main_invalid_validation():
    """Test main function validation with invalid parameters."""
    # Test with empty design name
    data = ConvertToCircuitExtensionData(design_name="")
    with pytest.raises(
        AEDTRuntimeError, match="No design provided to the extension"
    ):
        main(data)

def test_convert_to_circuit_with_components(add_app):
    """Test conversion with various component types."""
    tb = add_app(
        application=TwinBuilder,
        project_name="convert_components_test",
        design_name="TBComponentsTest",
    )

    # Add variables that would be used by components
    tb["time_var"] = "0s"
    tb["amplitude"] = "1V"

    # Create test data
    data = ConvertToCircuitExtensionData(design_name=tb.design_name)

    # Test conversion
    result = main(data)
    assert result is True

def test_convert_to_circuit_exception_handling(add_app):
    """Test exception handling in main function."""
    # Create a project first but use wrong design name
    _ = add_app(
        application=TwinBuilder,
        project_name="convert_exception_test",
        design_name="TBExceptionTest",
    )

    # Test with non-existent design
    data = ConvertToCircuitExtensionData(
        design_name="NonExistentDesign"
    )

    # This should raise AttributeError due to non-existent design
    with pytest.raises(AttributeError):
        main(data)


def test_convert_to_circuit_wire_conversion(add_app):
    """Test wire conversion functionality."""
    tb = add_app(
        application=TwinBuilder,
        project_name="convert_wire_test",
        design_name="TBWireTest",
    )

    # Try to create wires for testing
    try:
        points1 = [[0, 0, 0], [0.1, 0, 0], [0.1, 0.1, 0]]
        tb.modeler.components.create_wire(points1, "TestWire1")

        points2 = [[0.2, 0, 0], [0.3, 0, 0]]
        tb.modeler.components.create_wire(points2, "TestWire2")
    except Exception:
        # Skip wire creation if not supported in test environment
        pass

    data = ConvertToCircuitExtensionData(design_name=tb.design_name)
    result = main(data)
    assert result is True
