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

import pytest

from ansys.aedt.core import Hfss
from ansys.aedt.core import Maxwell3d
from ansys.aedt.core.extensions.hfss.shielding_effectiveness import ShieldingEffectivenessExtension
from ansys.aedt.core.extensions.hfss.shielding_effectiveness import ShieldingEffectivenessExtensionData
from ansys.aedt.core.extensions.hfss.shielding_effectiveness import main
from ansys.aedt.core.generic.settings import is_linux
from ansys.aedt.core.internal.errors import AEDTRuntimeError

FIELDS_CALCULATOR = "fields_calculator_solved"
TEST_SUBFOLDER = "T45"


@pytest.mark.skipif(is_linux, reason="Long test for Linux VM.")
def test_shielding_effectiveness_generate_button(add_app):
    """Test the Generate button in the Shielding Effectiveness extension."""
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

    aedt_app = add_app(application=Hfss)

    aedt_app.modeler.create_waveguide(origin=[0, 0, 0], wg_direction_axis=0)

    extension = ShieldingEffectivenessExtension(withdraw=True)
    extension.root.nametowidget("generate").invoke()

    assert data == extension.data
    assert main(extension.data)

    # Verify that the dipole sphere was created
    assert "dipole" in aedt_app.modeler.object_names

    # Verify that a setup was created
    assert len(aedt_app.setups) > 0
    aedt_app.close_project(save=False)


def test_shielding_effectiveness_exceptions(add_app):
    """Test exceptions thrown by the Shielding Effectiveness extension."""
    # Test with no sphere size
    data = ShieldingEffectivenessExtensionData(sphere_size=-0.01)
    with pytest.raises(AEDTRuntimeError):
        main(data)

    # Test with invalid frequency range
    data = ShieldingEffectivenessExtensionData(sphere_size=0.01, start_frequency=2.0, stop_frequency=1.0)
    with pytest.raises(AEDTRuntimeError):
        main(data)

    # Test with wrong application type (Maxwell3d instead of HFSS)
    aedt_app = add_app(application=Maxwell3d)

    aedt_app.modeler.create_box(
        origin=["-0.1", "-0.1", "-0.1"], sizes=["0.2", "0.2", "0.2"], name="test_enclosure", material="aluminum"
    )

    data = ShieldingEffectivenessExtensionData(
        sphere_size=0.01,
        dipole_type="Electric",
        frequency_units="GHz",
        start_frequency=0.1,
        stop_frequency=1.0,
        points=10,
        cores=4,
    )

    with pytest.raises(AEDTRuntimeError):
        main(data)
    aedt_app.close_project(save=False)
