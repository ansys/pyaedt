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

import pytest

from ansys.aedt.core import Hfss
from ansys.aedt.core.extensions.hfss.shielding_effectiveness import ShieldingEffectivenessExtension
from ansys.aedt.core.extensions.hfss.shielding_effectiveness import ShieldingEffectivenessExtensionData
from ansys.aedt.core.extensions.hfss.shielding_effectiveness import main
from ansys.aedt.core.internal.errors import AEDTRuntimeError

fields_calculator = "fields_calculator_solved"
test_subfolder = "T45"


def test_shielding_effectiveness_generate_button(add_app):
    """Test the Generate button in the Shielding Effectiveness
    extension."""
    data = ShieldingEffectivenessExtensionData(
        sphere_size=0.01,
        x_pol=0.0,
        y_pol=0.0,
        z_pol=1.0,
        dipole_type="Electric",
        frequency_units="GHz",
        start_frequency=0.1,
        stop_frequency=1,
        points=10,
        cores=4,
    )
    aedt_app = add_app(application=Hfss, project_name="shielding_test", design_name="generate")

    # Create a test object (box) to serve as the shielding enclosure
    aedt_app.modeler.create_box(
        origin=["-0.1", "-0.1", "-0.1"], sizes=["0.2", "0.2", "0.2"], name="test_enclosure", material="aluminum"
    )

    extension = ShieldingEffectivenessExtension(withdraw=True)

    extension.root.nametowidget("generate").invoke()

    # Instead of comparing object references, compare to a new default instance
    assert data == extension.data
    assert main(extension.data)

    # Verify that the dipole sphere was created
    assert "dipole" in aedt_app.modeler.object_names

    # Verify that a setup was created
    assert len(aedt_app.setups) > 0


def test_shielding_effectiveness_parameter_validation(add_app):
    """Test parameter validation in the Shielding Effectiveness
    extension."""

    # Test negative sphere size
    data = ShieldingEffectivenessExtensionData(sphere_size=-0.01)
    with pytest.raises(AEDTRuntimeError, match="Sphere size must be greater than zero"):
        main(data)

    # Test zero sphere size
    data = ShieldingEffectivenessExtensionData(sphere_size=0.0)
    with pytest.raises(AEDTRuntimeError, match="Sphere size must be greater than zero"):
        main(data)

    # Test invalid frequency range (start >= stop)
    data = ShieldingEffectivenessExtensionData(sphere_size=0.01, start_frequency=2.0, stop_frequency=1.0)
    with pytest.raises(AEDTRuntimeError, match="Start frequency must be less than stop frequency"):
        main(data)

    # Test equal start and stop frequencies
    data = ShieldingEffectivenessExtensionData(sphere_size=0.01, start_frequency=1.0, stop_frequency=1.0)
    with pytest.raises(AEDTRuntimeError, match="Start frequency must be less than stop frequency"):
        main(data)

    # Test negative points
    data = ShieldingEffectivenessExtensionData(sphere_size=0.01, points=-5)
    with pytest.raises(AEDTRuntimeError, match="Points must be greater than zero"):
        main(data)

    # Test zero points
    data = ShieldingEffectivenessExtensionData(sphere_size=0.01, points=0)
    with pytest.raises(AEDTRuntimeError, match="Points must be greater than zero"):
        main(data)

    # Test negative cores
    data = ShieldingEffectivenessExtensionData(sphere_size=0.01, cores=-2)
    with pytest.raises(AEDTRuntimeError, match="Cores must be greater than zero"):
        main(data)

    # Test zero cores
    data = ShieldingEffectivenessExtensionData(sphere_size=0.01, cores=0)
    with pytest.raises(AEDTRuntimeError, match="Cores must be greater than zero"):
        main(data)


def test_shielding_effectiveness_no_objects(add_app):
    """Test exception when no objects exist in design."""
    add_app(application=Hfss, project_name="shielding_test", design_name="empty_design")

    # Don't create any objects - design should be empty

    with pytest.raises(AEDTRuntimeError, match="There should be only one object in the design"):
        ShieldingEffectivenessExtension(withdraw=True)


def test_shielding_effectiveness_multiple_objects(add_app):
    """Test exception when multiple objects exist in design."""
    aedt_app = add_app(application=Hfss, project_name="shielding_test", design_name="multi_object_design")

    # Create multiple objects
    aedt_app.modeler.create_box(origin=["-0.1", "-0.1", "-0.1"], sizes=["0.2", "0.2", "0.2"], name="test_enclosure1")

    aedt_app.modeler.create_box(origin=["0.2", "0.2", "0.2"], sizes=["0.1", "0.1", "0.1"], name="test_enclosure2")

    with pytest.raises(AEDTRuntimeError, match="There should be only one object in the design"):
        ShieldingEffectivenessExtension(withdraw=True)


def test_shielding_effectiveness_magnetic_dipole(add_app):
    """Test shielding effectiveness with magnetic dipole."""
    aedt_app = add_app(application=Hfss, project_name="shielding_test", design_name="magnetic_dipole")

    # Create a test object
    aedt_app.modeler.create_cylinder(
        orientation="Z",
        origin=["0", "0", "-0.05"],
        radius="0.08",
        height="0.1",
        name="cylindrical_enclosure",
        material="copper",
    )

    data = ShieldingEffectivenessExtensionData(
        sphere_size=0.015,
        x_pol=0.0,
        y_pol=1.0,
        z_pol=0.0,
        dipole_type="Magnetic",
        frequency_units="MHz",
        start_frequency=100,
        stop_frequency=1000,
        points=8,
        cores=1,
    )

    assert main(data)

    # Verify that the correct dipole type was used
    assert "dipole" in aedt_app.modeler.object_names

    # Verify setup properties
    assert len(aedt_app.setups) > 0
    setup = aedt_app.setups[0]
    assert "MHz" in setup.properties["Solution Freq"]
