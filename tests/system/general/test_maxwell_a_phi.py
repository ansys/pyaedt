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

from ansys.aedt.core import Maxwell3d
from ansys.aedt.core.generic.constants import Axis
from ansys.aedt.core.generic.constants import SolutionsMaxwell3D
from ansys.aedt.core.internal.errors import AEDTRuntimeError
from ansys.aedt.core.modules.boundary.maxwell_boundary import GCSourceACMagneticAPhi
from ansys.aedt.core.modules.boundary.maxwell_boundary import MatrixACMagneticAPhi
from ansys.aedt.core.modules.boundary.maxwell_boundary import RLSourceACMagneticAPhi
from tests.conftest import DESKTOP_VERSION


@pytest.fixture
def m3d_app_ac(add_app):
    app = add_app(application=Maxwell3d, solution_type="AC Magnetic APhi")
    yield app
    app.close_project(app.project_name, save=False)


@pytest.fixture
def m3d_app_tran(add_app):
    app = add_app(application=Maxwell3d, solution_type="Transient APhi")
    yield app
    app.close_project(app.project_name, save=False)


# TestMaxwellACMagneticAPhi


def test_assign_current(m3d_app_ac) -> None:
    cyl = m3d_app_ac.modeler.create_cylinder(orientation="XY", origin=[0, 0, 0], radius=10, height=100)

    current1 = m3d_app_ac.assign_current(
        assignment=[cyl.top_face_z],
        amplitude="10A",
        phase="0deg",
    )
    assert current1.name in m3d_app_ac.excitation_names
    assert current1.props["Current"] == "10A"
    assert current1.props["Phase"] == "0deg"
    assert not current1.props["Point out of terminal"]
    assert current1.props["CurrentExcitationModel"] == "Single Potential"
    assert current1.props["Faces"][0] == cyl.top_face_z.id


def test_assign_assign_voltage(m3d_app_ac) -> None:
    cyl = m3d_app_ac.modeler.create_cylinder(orientation="XY", origin=[0, 0, 0], radius=10, height=100)

    m3d_app_ac.modeler.create_region([50, 50, 50, 50, 50, 50])

    voltage = m3d_app_ac.assign_voltage(
        assignment=[cyl.top_face_z], amplitude="10V", excitation_model="Double Potentials with Ground"
    )

    assert voltage.name in m3d_app_ac.excitation_names
    assert voltage.props["Voltage"] == "10V"
    assert voltage.props["Faces"][0] == cyl.top_face_z.id
    assert not voltage.props["VoltageAPhi_Point_out_of_terminal"]
    assert voltage.props["VoltageAPhiExcitationModel"] == "Double Potentials with Ground"


def test_set_core_losses(m3d_app_ac) -> None:
    m3d_app_ac.modeler.create_box([0, 0, 0], [10, 10, 10], name="my_box")
    assert m3d_app_ac.set_core_losses(["my_box"], True)


def test_eddy_effects_on(m3d_app_ac) -> None:
    box1 = m3d_app_ac.modeler.create_box([0, 0, 0], [1.5, 1.5, 0.4])
    with pytest.raises(AEDTRuntimeError, match="No conductors defined in active design."):
        m3d_app_ac.eddy_effects_on(box1, enable_eddy_effects=True)
    box1.material_name = "copper"
    box2 = m3d_app_ac.modeler.create_box([10, 10, 0], [1.5, 1.5, 0.4], material="copper")
    assert m3d_app_ac.eddy_effects_on(box1, enable_eddy_effects=False)
    # In AC Magnetic A-Phi, eddy effects are always turned on
    assert m3d_app_ac.oboundary.GetEddyEffect(box1.name)
    assert m3d_app_ac.oboundary.GetEddyEffect(box2.name)
    # In AC Magnetic A-Phi, displacement current is turned on for the whole domain
    # so it's turned on for both boxes
    assert m3d_app_ac.oboundary.GetDisplacementCurrent(box1.name)
    assert m3d_app_ac.oboundary.GetDisplacementCurrent(box2.name)
    m3d_app_ac.eddy_effects_on([box1.name], enable_eddy_effects=True, enable_displacement_current=False)
    assert m3d_app_ac.oboundary.GetEddyEffect(box1.name)
    assert m3d_app_ac.oboundary.GetEddyEffect(box2.name)
    assert not m3d_app_ac.oboundary.GetDisplacementCurrent(box1.name)
    assert not m3d_app_ac.oboundary.GetDisplacementCurrent(box2.name)


def test_assign_flux_tangential(m3d_app_ac) -> None:
    m3d_app_ac.modeler.create_cylinder(orientation="XY", origin=[0, 0, 0], radius=10, height=100)

    region = m3d_app_ac.modeler.create_region([50, 50, 50, 50, 50, 50])

    flux_tangential = m3d_app_ac.assign_flux_tangential(assignment=region.top_face_z, flux_name="my_bound")

    assert flux_tangential in m3d_app_ac.boundaries
    assert flux_tangential.name == "my_bound"
    assert flux_tangential.props["Faces"][0] == region.top_face_z.id


def test_assign_matrix(m3d_app_ac) -> None:
    cyl = m3d_app_ac.modeler.create_cylinder(
        orientation="XY", origin=[0, 0, 0], radius=10, height=100, material="copper"
    )
    cyl1 = m3d_app_ac.modeler.create_cylinder(
        orientation="XY", origin=[20, 0, 0], radius=10, height=100, material="copper"
    )

    m3d_app_ac.modeler.create_region([50, 50, 50, 50, 0, 0])

    current = m3d_app_ac.assign_current(assignment=[cyl.top_face_z])
    current1 = m3d_app_ac.assign_current(assignment=[cyl1.top_face_z])
    current2 = m3d_app_ac.assign_current(assignment=[cyl.bottom_face_z], swap_direction=True)
    current3 = m3d_app_ac.assign_current(assignment=[cyl1.bottom_face_z], swap_direction=True)

    rl_source = RLSourceACMagneticAPhi(signal_sources=[current.name], ground_sources=[current2.name])
    gc_source = GCSourceACMagneticAPhi(signal_sources=[current1.name], ground_sources=[current3.name])

    matrix_args = MatrixACMagneticAPhi(
        rl_sources=[rl_source],
        gc_sources=[gc_source],
        matrix_name="test_matrix",
    )
    matrix = m3d_app_ac.assign_matrix(matrix_args)
    assert matrix in m3d_app_ac.boundaries
    assert matrix.props["RLMatrix"]["MatrixEntry"]["MatrixEntry"][0]["Source"] == current.name
    assert matrix.props["GCMatrix"]["MatrixEntry"]["MatrixEntry"][0]["Source"] == current1.name
    assert matrix.name == "test_matrix"


def test_assign_force(m3d_app_ac) -> None:
    cyl = m3d_app_ac.modeler.create_cylinder(
        orientation="XY", origin=[0, 0, 0], radius=10, height=100, material="copper"
    )

    force = m3d_app_ac.assign_force(assignment=cyl, is_virtual=True)
    assert force in m3d_app_ac.boundaries
    assert force.props["Name"] == force.name
    assert force.props["Objects"][0] == cyl.name
    assert force.props["Reference CS"] == "Global"
    assert force.props["Is Virtual"]


def test_assign_torque(m3d_app_ac) -> None:
    cyl = m3d_app_ac.modeler.create_cylinder(
        orientation="XY", origin=[0, 0, 0], radius=10, height=100, material="copper"
    )

    torque = m3d_app_ac.assign_torque(assignment=cyl, is_positive=False, is_virtual=True)
    assert torque in m3d_app_ac.boundaries
    assert torque.props["Name"] == torque.name
    assert torque.props["Objects"][0] == cyl.name
    assert torque.props["Coordinate System"] == "Global"
    assert torque.props["Is Virtual"]
    assert not torque.props["Is Positive"]


# TestMaxwellTransientAPhi


def test_assign_voltage(m3d_app_tran) -> None:
    box1 = m3d_app_tran.modeler.create_box(origin=[0, 0, 0], sizes=[1, 1, 1], name="my_box", material="copper")
    box2 = m3d_app_tran.modeler.create_box(origin=[0, 0, 1], sizes=[1, 1, 1], name="my_box", material="copper")
    m3d_app_tran.modeler.create_air_region(x_pos=10, x_neg=10, y_pos=10, y_neg=10, is_percentage=True)
    m3d_app_tran.solution_type = SolutionsMaxwell3D.TransientAPhi

    voltage1 = m3d_app_tran.assign_voltage(
        assignment=box1.faces[4],
        amplitude=0,
        name="gnd1",
        initial_current="1A",
        has_initial_current=True,
    )

    voltage2 = m3d_app_tran.assign_voltage(
        assignment=box2.faces[0],
        amplitude=0,
        name="gnd2",
        initial_current="1A",
        has_initial_current=True,
    )

    voltage3 = m3d_app_tran.assign_voltage(
        assignment=box1.faces[0],
        amplitude=3,
        name="voltage",
        initial_current="1A",
        has_initial_current=True,
        excitation_model="Double Potentials with Ground",
        swap_direction=True,
    )

    excitation_names = []
    for excitation in m3d_app_tran.boundaries:
        excitation_names.append(excitation.name)

    assert "gnd1" in excitation_names
    assert "voltage" in excitation_names
    assert "gnd2" in excitation_names
    assert voltage1.props["VoltageAPhi"] == "0mV"
    assert voltage1.props["VoltageAPhiInitialCurrent"] == "1A"
    assert voltage2.props["VoltageAPhi"] == "0mV"
    assert voltage2.props["VoltageAPhiInitialCurrent"] == "1A"
    assert voltage3.props["VoltageAPhiExcitationModel"] == "Double Potentials with Ground"


def test_set_core_losses_transient(m3d_app_tran) -> None:
    m3d_app_tran.modeler.create_box([0, 0, 0], [10, 10, 10], name="my_box")
    assert m3d_app_tran.set_core_losses(["my_box"], True)


def test_eddy_effects_on_transient(m3d_app_tran) -> None:
    box1 = m3d_app_tran.modeler.create_box([0, 0, 0], [1.5, 1.5, 0.4])
    with pytest.raises(AEDTRuntimeError, match="No conductors defined in active design."):
        m3d_app_tran.eddy_effects_on(box1, enable_eddy_effects=True)
    box1.material_name = "copper"
    box2 = m3d_app_tran.modeler.create_box([10, 10, 0], [1.5, 1.5, 0.4], material="copper")
    assert m3d_app_tran.eddy_effects_on(box1, enable_eddy_effects=True)
    assert m3d_app_tran.oboundary.GetEddyEffect(box1.name)
    assert m3d_app_tran.oboundary.GetDisplacementCurrent(box1.name)
    assert not m3d_app_tran.oboundary.GetEddyEffect(box2.name)
    assert not m3d_app_tran.oboundary.GetDisplacementCurrent(box2.name)
    m3d_app_tran.eddy_effects_on([box1.name], enable_eddy_effects=False, enable_displacement_current=False)
    assert not m3d_app_tran.oboundary.GetEddyEffect(box1.name)
    assert not m3d_app_tran.oboundary.GetDisplacementCurrent(box1.name)
    assert not m3d_app_tran.oboundary.GetEddyEffect(box2.name)
    assert not m3d_app_tran.oboundary.GetDisplacementCurrent(box2.name)


@pytest.mark.skipif(
    DESKTOP_VERSION < "2025.1",
    reason="Not working in non-graphical in version lower than 2025.1",
)
def test_order_coil_terminals(m3d_app_tran) -> None:
    c1 = m3d_app_tran.modeler.create_cylinder(
        orientation=Axis.Z, origin=[-3, 0, 0], radius=1, height=10, name="Cylinder1", material="copper"
    )

    c2 = m3d_app_tran.modeler.create_cylinder(
        orientation=Axis.Z, origin=[0, 0, 0], radius=1, height=10, name="Cylinder2", material="copper"
    )

    c3 = m3d_app_tran.modeler.create_cylinder(
        orientation=Axis.Z, origin=[3, 0, 0], radius=1, height=10, name="Cylinder3", material="copper"
    )

    m3d_app_tran.assign_coil(assignment=[c1.top_face_z], name="CoilTerminal1")
    m3d_app_tran.assign_coil(assignment=[c1.bottom_face_z], name="CoilTerminal2", polarity="Negative")

    m3d_app_tran.assign_coil(assignment=[c2.top_face_z], name="CoilTerminal3", polarity="Negative")
    m3d_app_tran.assign_coil(assignment=[c2.bottom_face_z], name="CoilTerminal4")

    m3d_app_tran.assign_coil(assignment=[c3.top_face_z], name="CoilTerminal5")
    m3d_app_tran.assign_coil(assignment=[c3.bottom_face_z], name="CoilTerminal6", polarity="Negative")

    m3d_app_tran.assign_winding(is_solid=True, current="1A", name="Winding1")

    terminal_list_order = [
        "CoilTerminal1",
        "CoilTerminal2",
        "CoilTerminal3",
        "CoilTerminal4",
        "CoilTerminal5",
        "CoilTerminal6",
    ]

    m3d_app_tran.add_winding_coils(assignment="Winding1", coils=terminal_list_order)

    terminal_list_order = [
        "CoilTerminal1",
        "CoilTerminal2",
        "CoilTerminal4",
        "CoilTerminal3",
        "CoilTerminal5",
        "CoilTerminal6",
    ]
    assert m3d_app_tran.order_coil_terminals(winding_name="Winding1", list_of_terminals=terminal_list_order)
    m3d_app_tran.solution_type = "Transient"
    with pytest.raises(AEDTRuntimeError, match="Only available in Transient A-Phi Formulation solution type."):
        m3d_app_tran.order_coil_terminals(winding_name="Winding1", list_of_terminals=terminal_list_order)


def test_assign_flux_tangential_transient(m3d_app_tran) -> None:
    box = m3d_app_tran.modeler.create_box([0, 0, 0], [10, 10, 10], name="Box")
    flux_tangential = m3d_app_tran.assign_flux_tangential(box.top_face_z, "my_bound")
    assert flux_tangential in m3d_app_tran.boundaries
    assert flux_tangential.name == "my_bound"
    assert flux_tangential.props["Faces"][0] == box.top_face_z.id


def test_assign_insulating(m3d_app_tran) -> None:
    box = m3d_app_tran.modeler.create_box([0, 0, 0], [10, 10, 10], name="Box")
    m3d_app_tran.modeler.create_region([50, 50, 50, 50, 50, 50])
    insulating = m3d_app_tran.assign_insulating(box.top_face_z, "my_insulating")
    assert insulating in m3d_app_tran.boundaries
    assert insulating.name == "my_insulating"
    assert insulating.props["Faces"][0] == box.top_face_z.id


def test_assign_resistive_sheet(m3d_app_tran) -> None:
    box = m3d_app_tran.modeler.create_box([0, 0, 0], [10, 10, 10], name="Box", material="copper")
    m3d_app_tran.modeler.create_region([50, 50, 50, 50, 50, 50])
    resistive_sheet = m3d_app_tran.assign_resistive_sheet(box.top_face_z, resistance="10ohm")
    assert resistive_sheet in m3d_app_tran.boundaries
    assert resistive_sheet.props["Faces"][0] == box.top_face_z.id
    assert resistive_sheet.props["Resistance"] == "10ohm"


def test_assign_symmetry(m3d_app_tran) -> None:
    box = m3d_app_tran.modeler.create_box([0, 1.5, 0], [1, 2.5, 5], name="Coil_1", material="aluminum")
    symmetry = m3d_app_tran.assign_symmetry([box.faces[0]], "symmetry_test")
    assert symmetry
    assert symmetry.props["Faces"][0] == box.faces[0].id
    assert symmetry.props["Name"] == "symmetry_test"
    assert symmetry.props["IsOdd"]
    symmetry_1 = m3d_app_tran.assign_symmetry([box.faces[1]], "symmetry_test_1", False)
    assert symmetry_1
    assert symmetry_1.props["Faces"][0] == box.faces[1].id
    assert symmetry_1.props["Name"] == "symmetry_test_1"
    assert not symmetry_1.props["IsOdd"]
    assert all([bound.type == "Symmetry" for bound in m3d_app_tran.boundaries])


def test_setup(m3d_app_tran) -> None:
    setup = m3d_app_tran.create_setup()
    setup.props["TimeStep"] = "1ms"
    setup.props["TotalTime"] = "100ms"
    setup.props["MaximumPasses"] = 10
    setup.props["MinimumPasses"] = 1
    setup.props["PercentError"] = 0.5

    assert setup in m3d_app_tran.setups
    assert setup.props["TimeStep"] == "1ms"
    assert setup.props["TotalTime"] == "100ms"
    assert setup.props["MaximumPasses"] == 10
    assert setup.props["MinimumPasses"] == 1
    assert setup.props["PercentError"] == 0.5
    setup.delete()
