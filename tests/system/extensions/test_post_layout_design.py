# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 - 2025 ANSYS, Inc. and/or its affiliates.
# SPDX-License-Identifier: MIT
#
# Permission is hereby granted, free of charge, to any person obtaining a
# copy of this software and associated documentation files (the
# "Software"), to deal in the Software without restriction, including
# without limitation the rights to use, copy, modify, merge, publish,
# distribute, sublicense, and/or sell copies of the Software, and to permit
# persons to whom the Software is furnished to do so, subject to the
# following conditions:
#
# The above copyright notice and this permission notice shall be included
# in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS
# OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
# IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY
# CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT,
# TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
# SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

from pathlib import Path

import pytest

from ansys.aedt.core import Hfss3dLayout
from ansys.aedt.core import Q3d
from ansys.aedt.core.extensions.hfss3dlayout.post_layout_design import PostLayoutDesignExtension
from ansys.aedt.core.extensions.hfss3dlayout.post_layout_design import PostLayoutDesignExtensionData
from ansys.aedt.core.extensions.hfss3dlayout.post_layout_design import main
from ansys.aedt.core.internal.errors import AEDTRuntimeError


def test_post_layout_design_antipad_operation(add_app):
    """Test the antipad operation in Post Layout Design extension."""
    data = PostLayoutDesignExtensionData(
        operation="antipad", via_selections=["via1", "via2"], radius="0.75mm", race_track=True
    )

    aedt_app = add_app(application=Hfss3dLayout, project_name="post_layout", design_name="antipad_test")

    # Create a simple test layout with vias
    edb = aedt_app.modeler.primitives.edb

    # Create basic stackup and nets
    edb.stackup.add_layer("TOP", thickness="0.035mm")
    edb.stackup.add_layer("BOTTOM", thickness="0.035mm")

    _net1 = edb.nets.create("VCC")
    _net2 = edb.nets.create("GND")

    # Create padstack definition
    _padstack_def = edb.padstacks.create("test_via")

    # Create via instances
    _via1 = edb.padstacks.place(position=[0, 0], definition_name="test_via", net_name="VCC", via_name="via1")

    _via2 = edb.padstacks.place(position=[0.001, 0], definition_name="test_via", net_name="GND", via_name="via2")

    # Test that the extension can be instantiated
    extension = PostLayoutDesignExtension(withdraw=True)
    extension.root.nametowidget("generate")
    extension.root.destroy()

    # Test the main function
    assert main(data) is True


def test_post_layout_design_microvia_operation(add_app):
    """Test the micro via operation in Post Layout Design extension."""
    data = PostLayoutDesignExtensionData(
        operation="microvia", padstack_selections=["test_padstack"], etching_angle=60.0, signal_only=True
    )

    aedt_app = add_app(application=Hfss3dLayout, project_name="post_layout", design_name="microvia_test")

    # Create a simple test layout
    edb = aedt_app.modeler.primitives.edb

    # Create basic stackup and nets
    edb.stackup.add_layer("TOP", thickness="0.035mm")
    edb.stackup.add_layer("BOTTOM", thickness="0.035mm")

    _signal_net = edb.nets.create("SIGNAL")

    # Create padstack definition
    _padstack_def = edb.padstacks.create("test_padstack")

    # Create via instance
    _via = edb.padstacks.place(position=[0, 0], definition_name="test_padstack", net_name="SIGNAL")

    # Test the main function
    result = main(data)
    assert isinstance(result, str)  # Should return new EDB path
    assert Path(result).exists()


def test_post_layout_design_exceptions(add_app):
    """Test exceptions thrown by the Post Layout Design extension."""
    # Test invalid operation
    data = PostLayoutDesignExtensionData(operation="invalid_op")
    with pytest.raises(AEDTRuntimeError, match="Invalid operation specified"):
        main(data)

    # Test antipad with wrong number of vias
    data = PostLayoutDesignExtensionData(
        operation="antipad",
        via_selections=["via1"],  # Only one via
    )
    with pytest.raises(AEDTRuntimeError, match="Exactly two vias must be selected"):
        main(data)

    # Test microvia with empty padstack selection
    data = PostLayoutDesignExtensionData(operation="microvia", padstack_selections=[])
    with pytest.raises(AEDTRuntimeError, match="At least one padstack definition must be selected"):
        main(data)

    # Test with wrong design type
    _aedt_app = add_app(application=Q3d, project_name="post_layout", design_name="wrong_design")

    data = PostLayoutDesignExtensionData(operation="antipad", via_selections=["via1", "via2"], radius="0.5mm")

    with pytest.raises(AEDTRuntimeError, match="This extension only works with HFSS 3D Layout Design"):
        main(data)


def test_post_layout_design_extension_ui_workflow(add_app):
    """Test the complete UI workflow of the extension."""
    aedt_app = add_app(application=Hfss3dLayout, project_name="post_layout", design_name="ui_test")

    # Create basic setup
    edb = aedt_app.modeler.primitives.edb
    edb.stackup.add_layer("TOP", thickness="0.035mm")
    _net = edb.nets.create("TEST_NET")
    _padstack_def = edb.padstacks.create("test_via")

    _via = edb.padstacks.place(position=[0, 0], definition_name="test_via", net_name="TEST_NET")

    # Test extension instantiation
    extension = PostLayoutDesignExtension(withdraw=True)

    # Verify UI elements exist
    assert extension.notebook is not None
    assert extension.via_selections_entry is not None
    assert extension.radius_entry is not None
    assert extension.race_track_var is not None
    assert extension.padstack_selections_entry is not None
    assert extension.etching_angle_entry is not None
    assert extension.signal_only_var is not None

    # Test get_aedt_selections method
    selections = extension.get_aedt_selections()
    assert isinstance(selections, list)

    extension.root.destroy()


def test_post_layout_design_backend_classes(add_app):
    """Test the backend classes functionality."""
    aedt_app = add_app(application=Hfss3dLayout, project_name="post_layout", design_name="backend_test")

    # Create test setup
    edb = aedt_app.modeler.primitives.edb
    edb.stackup.add_layer("TOP", thickness="0.035mm")
    edb.stackup.add_layer("BOTTOM", thickness="0.035mm")

    _net1 = edb.nets.create("NET1")
    _net2 = edb.nets.create("NET2")

    _padstack_def = edb.padstacks.create("test_via")

    _via1 = edb.padstacks.place(position=[0, 0], definition_name="test_via", net_name="NET1", via_name="via1")

    _via2 = edb.padstacks.place(position=[0.001, 0], definition_name="test_via", net_name="NET2", via_name="via2")

    # Test antipad creation
    data_antipad = PostLayoutDesignExtensionData(
        operation="antipad", via_selections=["via1", "via2"], radius="0.5mm", race_track=False
    )

    result = main(data_antipad)
    assert result is True

    # Create new app for microvia test
    aedt_app2 = add_app(application=Hfss3dLayout, project_name="post_layout2", design_name="microvia_backend")

    edb2 = aedt_app2.modeler.primitives.edb
    edb2.stackup.add_layer("TOP", thickness="0.035mm")
    _signal_net = edb2.nets.create("SIGNAL")
    _padstack_def2 = edb2.padstacks.create("micro_via")

    _via3 = edb2.padstacks.place(position=[0, 0], definition_name="micro_via", net_name="SIGNAL")

    # Test microvia creation
    data_microvia = PostLayoutDesignExtensionData(
        operation="microvia", padstack_selections=["micro_via"], etching_angle=75.0, signal_only=True
    )

    result = main(data_microvia)
    assert isinstance(result, str)
    assert Path(result).exists()
