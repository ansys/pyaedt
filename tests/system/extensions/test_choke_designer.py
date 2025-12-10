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

from ansys.aedt.core import Hfss
from ansys.aedt.core.extensions.hfss.choke_designer import ChokeDesignerExtension
from ansys.aedt.core.extensions.hfss.choke_designer import ChokeDesignerExtensionData
from ansys.aedt.core.extensions.hfss.choke_designer import main
from ansys.aedt.core.modeler.advanced_cad.choke import Choke


def test_choke_designer_main_function(add_app):
    """Test the main function of the Choke Designer extension."""
    # Create HFSS application for testing environment
    add_app(
        application=Hfss,
        project="choke_test",
        design="design1",
    )

    # Create extension with default choke
    extension = ChokeDesignerExtension(withdraw=True)
    choke = extension.choke

    # Create data object
    data = ChokeDesignerExtensionData(choke=choke)

    # Test main function
    result = main(data)
    assert result is True

    # Note: main() creates its own HFSS instance, so we need to check that instance.
    # This test verifies that main() completes successfully


def test_choke_designer_custom_config(add_app):
    """Test Choke Designer with custom configuration."""
    # Create HFSS application for testing environment
    add_app(
        application=Hfss,
        project="choke_custom",
        design="design1",
    )

    # Create custom choke configuration
    custom_choke = Choke()
    custom_choke.core["Material"] = "custom_ferrite"
    custom_choke.core["Inner Radius"] = 15
    custom_choke.core["Outer Radius"] = 25
    custom_choke.outer_winding["Turns"] = 15
    custom_choke.outer_winding["Wire Diameter"] = 1.0

    # Create data object with custom choke
    data = ChokeDesignerExtensionData(choke=custom_choke)

    # Test main function with custom configuration
    result = main(data)
    assert result is True

    # Note: Objects are created inside main() function in its own
    # HFSS instance. This test verifies successful execution.
