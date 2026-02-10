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
import re
import shutil

import pytest

try:
    from IPython.display import Image

    ipython_available = True
except ImportError:
    ipython_available = False

from ansys.aedt.core import Maxwell3d
from ansys.aedt.core.generic.constants import Axis
from ansys.aedt.core.generic.constants import Plane
from ansys.aedt.core.generic.constants import SolutionsMaxwell3D
from ansys.aedt.core.generic.file_utils import generate_unique_name
from ansys.aedt.core.generic.file_utils import get_dxf_layers
from ansys.aedt.core.generic.general_methods import is_linux
from ansys.aedt.core.internal.errors import AEDTRuntimeError
from ansys.aedt.core.modeler.geometry_operators import GeometryOperators
from ansys.aedt.core.modules.boundary.maxwell_boundary import MaxwellForce
from ansys.aedt.core.modules.boundary.maxwell_boundary import MaxwellLayoutForce
from ansys.aedt.core.modules.boundary.maxwell_boundary import MaxwellMatrix
from ansys.aedt.core.modules.boundary.maxwell_boundary import MaxwellTorque
from tests import TESTS_GENERAL_PATH
from tests.conftest import DESKTOP_VERSION
from tests.conftest import NON_GRAPHICAL

TEST_SUBFOLDER = "TMaxwell"

CYL_GAP_NAME = "Motor3D_cyl_gap"

LAYOUT_COMPONENT_NAME = "LayoutForce"


@pytest.fixture
def m3d_app(add_app):
    app = add_app(application=Maxwell3d)
    yield app
    app.close_project(app.project_name, save=False)


@pytest.fixture
def maxwell_versioned():
    return SolutionsMaxwell3D


@pytest.fixture
def layout_comp(add_app_example):
    app = add_app_example(application=Maxwell3d, project=LAYOUT_COMPONENT_NAME, subfolder=TEST_SUBFOLDER)
    yield app
    app.close_project(app.project_name, save=False)


@pytest.mark.skipif(NON_GRAPHICAL, reason="Test is failing on build machine")
def test_display(m3d_app):
    img = m3d_app.post.nb_display(show_axis=True, show_grid=True, show_ruler=True)
    assert isinstance(img, Image)


def test_litz_wire(m3d_app):
    m3d_app.materials["magnesium"].stacking_type = "Litz Wire"
    m3d_app.materials["magnesium"].wire_type = "Round"
    m3d_app.materials["magnesium"].strand_number = 3
    m3d_app.materials["magnesium"].wire_diameter = "1mm"
    assert m3d_app.materials["magnesium"].stacking_type == "Litz Wire"
    assert m3d_app.materials["magnesium"].wire_type == "Round"
    assert m3d_app.materials["magnesium"].strand_number == 3
    assert m3d_app.materials["magnesium"].wire_diameter == "1mm"

    m3d_app.materials["magnesium"].wire_type = "Square"
    m3d_app.materials["magnesium"].wire_width = "2mm"
    assert m3d_app.materials["magnesium"].wire_type == "Square"
    assert m3d_app.materials["magnesium"].wire_width == "2mm"

    m3d_app.materials["magnesium"].wire_type = "Rectangular"
    m3d_app.materials["magnesium"].wire_width = "2mm"
    m3d_app.materials["magnesium"].wire_thickness = "1mm"
    m3d_app.materials["magnesium"].wire_thickness_direction = "V(2)"
    m3d_app.materials["magnesium"].wire_width_direction = "V(3)"
    assert m3d_app.materials["magnesium"].wire_type == "Rectangular"
    assert m3d_app.materials["magnesium"].wire_width == "2mm"
    assert m3d_app.materials["magnesium"].wire_thickness == "1mm"
    assert m3d_app.materials["magnesium"].wire_thickness_direction == "V(2)"
    assert m3d_app.materials["magnesium"].wire_width_direction == "V(3)"


def test_lamination(m3d_app):
    m3d_app.materials["titanium"].stacking_type = "Lamination"
    m3d_app.materials["titanium"].stacking_factor = "0.99"
    m3d_app.materials["titanium"].stacking_direction = "V(3)"
    m3d_app.materials["titanium"].stacking_direction = "V(2)"
    assert m3d_app.materials["titanium"].stacking_type == "Lamination"
    assert m3d_app.materials["titanium"].stacking_factor == "0.99"
    assert m3d_app.materials["titanium"].stacking_direction == "V(2)"


def test_assign_winding(m3d_app):
    coil_hole = m3d_app.modeler.create_box([-50, -50, 0], [100, 100, 100], name="Coil_Hole")
    coil = m3d_app.modeler.create_box([-100, -100, 0], [200, 200, 100], name="Coil")
    m3d_app.modeler.subtract([coil], [coil_hole])

    m3d_app.modeler.section(["Coil"], Plane.ZX)
    m3d_app.modeler.separate_bodies(["Coil_Section1"])
    face_id = m3d_app.modeler["Coil_Section1"].faces[0].id
    assert m3d_app.assign_winding(face_id)
    bounds = m3d_app.assign_winding(assignment=face_id, current=20e-3)
    assert bounds.props["Current"] == "0.02A"
    bounds = m3d_app.assign_winding(assignment=face_id, current="20e-3A")
    assert bounds.props["Current"] == "20e-3A"
    bounds = m3d_app.assign_winding(assignment=face_id, resistance="1ohm")
    assert bounds.props["Resistance"] == "1ohm"
    bounds = m3d_app.assign_winding(assignment=face_id, inductance="1H")
    assert bounds.props["Inductance"] == "1H"
    bounds = m3d_app.assign_winding(assignment=face_id, voltage="10V")
    assert bounds.props["Voltage"] == "10V"
    bounds_name = generate_unique_name("Winding")
    bounds = m3d_app.assign_winding(assignment=face_id, name=bounds_name)
    assert bounds_name == bounds.name


def test_assign_coil(m3d_app):
    coil_hole = m3d_app.modeler.create_box([-50, -50, 0], [100, 100, 100], name="Coil_Hole")
    coil = m3d_app.modeler.create_box([-100, -100, 0], [200, 200, 100], name="Coil")
    m3d_app.modeler.subtract([coil], [coil_hole])
    m3d_app.modeler.section(["Coil"], Plane.ZX)
    m3d_app.modeler.separate_bodies(["Coil_Section1"])
    face_id = m3d_app.modeler["Coil_Section1"].faces[0].id
    bound = m3d_app.assign_coil(assignment=face_id)
    assert bound.props["Conductor number"] == "1"
    assert not bound.props["Point out of terminal"]
    bound = m3d_app.assign_coil(assignment=face_id, polarity="Positive")
    assert bound.props["Conductor number"] == "1"
    assert not bound.props["Point out of terminal"]
    bound = m3d_app.assign_coil(assignment=face_id, polarity="Negative")
    assert bound.props["Conductor number"] == "1"
    assert bound.props["Point out of terminal"]
    bound_name = generate_unique_name("Coil")
    bound = m3d_app.assign_coil(assignment=face_id, name=bound_name)
    assert bound_name == bound.name


def test_create_air_region(m3d_app):
    region = m3d_app.modeler.create_air_region(*[300] * 6)
    assert region.material_name == "air"


def test_eddy_effects_on(m3d_app, maxwell_versioned):
    m3d_app.solution_type = maxwell_versioned.EddyCurrent
    plate_vacuum = m3d_app.modeler.create_box([-3, -3, 0], [1.5, 1.5, 0.4], name="Plate_vaccum")
    with pytest.raises(AEDTRuntimeError, match="No conductors defined in active design."):
        m3d_app.eddy_effects_on(plate_vacuum, enable_eddy_effects=True)
    plate = m3d_app.modeler.create_box([-1, -1, 0], [1.5, 1.5, 0.4], name="Plate", material="copper")
    assert m3d_app.eddy_effects_on(plate, enable_eddy_effects=True)
    if DESKTOP_VERSION >= "2025.2":
        assert m3d_app.oboundary.GetEddyEffect("Plate")
        assert m3d_app.oboundary.GetDisplacementCurrent("Plate")
    m3d_app.eddy_effects_on(["Plate"], enable_eddy_effects=False)
    if DESKTOP_VERSION >= "2025.2":
        assert not m3d_app.oboundary.GetEddyEffect("Plate")
        assert not m3d_app.oboundary.GetDisplacementCurrent("Plate")


def test_create_parametrics(m3d_app):
    m3d_app.create_setup()
    m3d_app["w1"] = "10mm"
    m3d_app["w2"] = "2mm"
    setup_parametrics = m3d_app.parametrics.add("w1", 0.1, 20, 0.2, "LinearStep")
    assert setup_parametrics.props["Sweeps"]["SweepDefinition"]["Variable"] == "w1"
    assert setup_parametrics.props["Sweeps"]["SweepDefinition"]["Data"] == "LIN 0.1mm 20mm 0.2mm"
    assert setup_parametrics.add_calculation(
        calculation="SolidLoss",
        ranges={},
        report_type="Magnetostatic",
        solution=m3d_app.existing_analysis_sweeps[0],
    )


@pytest.mark.skipif(is_linux, reason="Crashing on Linux")
def test_expression_cache(m3d_app):
    setup = m3d_app.create_setup()
    setup.props["MaximumPasses"] = 12
    setup.props["MinimumPasses"] = 2
    setup.props["MinimumConvergedPasses"] = 1
    setup.props["PercentRefinement"] = 30
    setup.props["Frequency"] = "200Hz"
    setup.update()
    assert setup.enable_expression_cache(["CoreLoss"], "Fields", "Phase='0deg' ", True)


def test_assign_length_mesh(m3d_app):
    plate = m3d_app.modeler.create_box([0, 0, 0], [1.5, 1.5, 0.5], name="Plate")
    assert m3d_app.mesh.assign_length_mesh(plate)
    assert m3d_app.mesh.assign_length_mesh(plate, maximum_length=1, maximum_elements=1200)
    assert m3d_app.mesh.assign_length_mesh(plate, name="test_mesh")
    assert m3d_app.mesh.assign_length_mesh(plate, name="test_mesh")


def test_assign_skin_depth(m3d_app):
    plate = m3d_app.modeler.create_box([0, 0, 0], [1.5, 1.5, 0.5], name="Plate")
    mesh = m3d_app.mesh.assign_skin_depth(plate, "1mm")
    assert mesh
    mesh.delete()
    mesh = m3d_app.mesh.assign_skin_depth(plate, "1mm", 1000)
    assert mesh
    mesh.delete()
    mesh = m3d_app.mesh.assign_skin_depth(plate.faces[0].id, "1mm")
    assert mesh
    mesh.delete()
    mesh = m3d_app.mesh.assign_skin_depth(plate, "1mm")
    assert mesh


def test_assign_curvilinear_elements(m3d_app):
    box = m3d_app.modeler.create_box([30, 0, 0], [40, 10, 5])
    assert m3d_app.mesh.assign_curvilinear_elements(box, "1mm")
    assert m3d_app.mesh.assign_curvilinear_elements(box, "1mm", name="test")
    assert m3d_app.mesh.assign_curvilinear_elements(box, "1mm", name="test")


def test_assign_edge_cut(m3d_app):
    m3d_app.modeler.model_units = "mm"
    box = m3d_app.modeler.create_box([30, 0, 0], [40, 10, 5])
    assert m3d_app.mesh.assign_edge_cut(box)
    assert m3d_app.mesh.assign_edge_cut(box, name="edge_cute")


def test_assign_density_control(m3d_app):
    box = m3d_app.modeler.create_box([30, 0, 0], [40, 10, 5])
    assert m3d_app.mesh.assign_density_control(box, maximum_element_length="2mm", layers_number="3")
    assert m3d_app.mesh.assign_density_control(
        box, maximum_element_length="2mm", layers_number="3", name="density_ctrl"
    )
    assert m3d_app.mesh.assign_density_control(
        box, maximum_element_length="2mm", layers_number="3", name="density_ctrl"
    )


def test_assign_rotational_layer(m3d_app):
    box = m3d_app.modeler.create_box([30, 0, 0], [40, 10, 5])
    assert m3d_app.mesh.assign_rotational_layer(box)
    assert m3d_app.mesh.assign_rotational_layer(box, name="my_rotational")
    assert m3d_app.mesh.assign_rotational_layer(box, name="my_rotational")


def test_assign_initial_mesh_slider(m3d_app):
    assert m3d_app.mesh.assign_initial_mesh_from_slider(4)


def test_assign_initial_mesh(m3d_app):
    assert m3d_app.mesh.assign_initial_mesh(surface_deviation="2mm")


@pytest.mark.skipif(is_linux, reason="Crashing on Linux")
def test_create_udp(m3d_app):
    my_udp = [
        ["DiaGap", "102mm"],
        ["Length", "100mm"],
        ["Poles", "8"],
        ["EmbraceTip", "0.29999999999999999"],
        ["EmbraceRoot", "1.2"],
        ["ThickTip", "5mm"],
        ["ThickRoot", "10mm"],
        ["ThickShoe", "8mm"],
        ["DepthSlot", "12mm"],
        ["ThickYoke", "10mm"],
        ["LengthPole", "90mm"],
        ["LengthMag", "0mm"],
        ["SegAngle", "5deg"],
        ["LenRegion", "200mm"],
        ["InfoCore", "0"],
    ]

    # Test udp with a custom name.
    my_udpName = "MyClawPoleCore"
    udp = m3d_app.modeler.create_udp(dll="RMxprt/ClawPoleCore", parameters=my_udp, library="syslib", name=my_udpName)

    assert udp
    assert udp.name == "MyClawPoleCore"
    assert "MyClawPoleCore" in udp._primitives.object_names
    assert int(udp.bounding_dimension[2]) == 100

    # Modify one of the 'MyClawPoleCore' udp properties.
    assert m3d_app.modeler.update_udp(
        assignment="MyClawPoleCore", operation="CreateUserDefinedPart", parameters=[["Length", "110mm"]]
    )

    assert int(udp.bounding_dimension[0]) == 102
    assert int(udp.bounding_dimension[1]) == 102
    assert int(udp.bounding_dimension[2]) == 110

    # Test udp with default name -None-.
    second_udp = m3d_app.modeler.create_udp(dll="RMxprt/ClawPoleCore", parameters=my_udp, library="syslib")

    assert second_udp
    assert second_udp.name == "ClawPoleCore"
    assert "ClawPoleCore" in udp._primitives.object_names

    # Modify two of the 'MyClawPoleCore' udp properties.
    assert m3d_app.modeler.update_udp(
        assignment="ClawPoleCore",
        operation="CreateUserDefinedPart",
        parameters=[["Length", "110mm"], ["DiaGap", "125mm"]],
    )

    assert int(second_udp.bounding_dimension[0]) == 125
    assert int(second_udp.bounding_dimension[1]) == 125
    assert int(second_udp.bounding_dimension[2]) == 110

    # Create an udp from a *.py file.
    python_udp_parameters = []
    udp_data = ["Xpos", "0mm"]
    python_udp_parameters.append(udp_data)
    udp_data = ["Ypos", "0mm"]
    python_udp_parameters.append(udp_data)
    udp_data = ["Dist", "5mm"]
    python_udp_parameters.append(udp_data)
    udp_data = ["Turns", "2"]
    python_udp_parameters.append(udp_data)
    udp_data = ["Width", "2mm"]
    python_udp_parameters.append(udp_data)
    udp_data = ["Thickness", "1mm"]
    python_udp_parameters.append(udp_data)
    python_udp_parameters.append(udp_data)

    udp_from_python = m3d_app.modeler.create_udp(
        dll="Examples/RectangularSpiral.py", parameters=python_udp_parameters, name="PythonSpiral"
    )

    assert udp_from_python
    assert udp_from_python.name == "PythonSpiral"
    assert "PythonSpiral" in udp_from_python._primitives.object_names
    assert int(udp_from_python.bounding_dimension[0]) == 22.0
    assert int(udp_from_python.bounding_dimension[1]) == 22.0


@pytest.mark.skipif(is_linux, reason="Feature not supported in Linux")
def test_create_udm(m3d_app):
    my_udm = [
        ["ILD Thickness (ILD)", "0.006mm"],
        ["Line Spacing (LS)", "0.004mm"],
        ["Line Thickness (LT)", "0.005mm"],
        ["Line Width (LW)", "0.004mm"],
        ["No. of Turns (N)", 2],
        ["Outer Diameter (OD)", "0.15mm"],
        ["Substrate Thickness", "0.2mm"],
        [
            "Inductor Type",
            '"Square,Square,Octagonal,Circular,Square-Differential,Octagonal-Differential,Circular-Differential"',
        ],
        ["Underpass Thickness (UT)", "0.001mm"],
        ["Via Thickness (VT)", "0.001mm"],
    ]

    assert m3d_app.modeler.create_udm(
        udm_full_name="Maxwell3D/OnDieSpiralInductor.py", parameters=my_udm, library="syslib"
    )


def test_assign_torque(m3d_app):
    coil = m3d_app.modeler.create_box([-100, -100, 0], [200, 200, 100], name="Coil")
    torque = m3d_app.assign_torque(coil)
    assert isinstance(torque, MaxwellTorque)
    assert torque.type == "Torque"
    assert torque.props["Objects"][0] == "Coil"
    assert torque.props["Is Positive"]
    assert torque.props["Is Virtual"]
    assert torque.props["Coordinate System"] == "Global"
    assert torque.props["Axis"] == "Z"
    assert torque.delete()
    torque = m3d_app.assign_torque(assignment="Coil", is_positive=False, torque_name="Torque_Test")
    assert not torque.props["Is Positive"]
    assert torque.name == "Torque_Test"
    m3d_app.solution_type = SolutionsMaxwell3D.ACConduction
    with pytest.raises(AEDTRuntimeError):
        m3d_app.assign_torque(coil)


def test_assign_force(m3d_app):
    coil = m3d_app.modeler.create_box([-100, -100, 0], [200, 200, 100], name="Coil")
    force = m3d_app.assign_force(coil)
    assert isinstance(force, MaxwellForce)
    assert force.type == "Force"
    assert force.props["Objects"][0] == "Coil"
    assert force.props["Reference CS"] == "Global"
    assert force.props["Is Virtual"]
    assert force.delete()
    force = m3d_app.assign_force(assignment="Coil", is_virtual=False, force_name="Force_Test")
    assert force.name == "Force_Test"
    assert not force.props["Is Virtual"]
    m3d_app.solution_type = SolutionsMaxwell3D.ACConduction
    with pytest.raises(AEDTRuntimeError):
        m3d_app.assign_torque(coil)


def test_assign_translate_motion(m3d_app, maxwell_versioned):
    m3d_app.solution_type = maxwell_versioned.Transient
    m3d_app.modeler.create_box([0, 0, 0], [10, 10, 10], name="Inner_Box")
    m3d_app.modeler.create_box([0, 0, 0], [30, 20, 20], name="Outer_Box")
    bound = m3d_app.assign_translate_motion("Outer_Box", velocity=1, mechanical_transient=True)
    assert bound
    assert bound.props["Velocity"] == "1m_per_sec"


def test_set_core_losses(m3d_app, maxwell_versioned):
    m3d_app.solution_type = maxwell_versioned.EddyCurrent
    m3d_app.modeler.create_box([0, 0, 0], [10, 10, 10], name="my_box", material="Material_3F3")
    assert m3d_app.set_core_losses(["my_box"])
    assert m3d_app.set_core_losses(["my_box"], True)


def test_assign_matrix_ac_magnetic_aphi(m3d_app):
    m3d_app.solution_type = SolutionsMaxwell3D.ACMagneticAPhi

    box1 = m3d_app.modeler.create_box([0.5, 1.5, 0.5], [2.5, 5, 5])
    box2 = m3d_app.modeler.create_box([9, 1.5, 0.5], [2.5, 5, 5])

    current1 = m3d_app.assign_current(box1.top_face_z, amplitude=1, name="Current1")
    current2 = m3d_app.assign_current(box2.top_face_z, amplitude=1, name="Current2")
    current3 = m3d_app.assign_current(box1.bottom_face_z, amplitude=1, name="Current3", swap_direction=True)
    current4 = m3d_app.assign_current(box2.bottom_face_z, amplitude=1, name="Current4", swap_direction=True)

    rl_source = MaxwellMatrix.RLSourceACMagneticAPhi(
        signal_sources=[current1.name],
        ground_sources=[current3.name],
    )
    gc_source = MaxwellMatrix.GCSourceACMagneticAPhi(
        signal_sources=[current2.name],
        ground_sources=[current4.name],
    )

    args = MaxwellMatrix.MatrixACMagneticAPhi(
        rl_sources=[rl_source],
        gc_sources=[gc_source],
        matrix_name="test_matrix",
    )

    matrix = m3d_app.assign_matrix(args)
    assert isinstance(matrix, MaxwellMatrix)
    assert len(matrix.rl_sources) == 1
    assert len(matrix.gc_sources) == 1
    assert matrix.rl_sources[0].signal_sources == [current1.name]
    assert matrix.rl_sources[0].ground_sources == [current3.name]
    assert matrix.gc_sources[0].signal_sources == [current2.name]
    assert matrix.gc_sources[0].ground_sources == [current4.name]


def test_assign_matrix_ac_magnetic(m3d_app):
    m3d_app.solution_type = SolutionsMaxwell3D.ACMagnetic

    box1 = m3d_app.modeler.create_box([0.5, 1.5, 0.5], [2.5, 5, 5], material="copper")
    box2 = m3d_app.modeler.create_box([9, 1.5, 0.5], [2.5, 5, 5], material="copper")

    current1 = m3d_app.assign_current(box1.top_face_z, amplitude=1, name="Current1")
    current2 = m3d_app.assign_current(box2.top_face_z, amplitude=1, name="Current2")
    m3d_app.assign_current(box1.bottom_face_z, amplitude=1, name="Current3", swap_direction=True)
    m3d_app.assign_current(box2.bottom_face_z, amplitude=1, name="Current4", swap_direction=True)

    signal_source_1 = MaxwellMatrix.SourceACMagnetic(name=current1.name)
    signal_source_2 = MaxwellMatrix.SourceACMagnetic(name=current2.name)
    matrix_args = MaxwellMatrix.MatrixACMagnetic(
        signal_sources=[signal_source_1, signal_source_2],
    )
    matrix = m3d_app.assign_matrix(matrix_args)
    assert isinstance(matrix, MaxwellMatrix)
    assert len(matrix.signal_sources) == 2
    assert matrix.signal_sources[0].name == current1.name
    assert matrix.signal_sources[1].name == current2.name


def test_assign_matrix_magnetostatic(m3d_app):
    m3d_app.solution_type = SolutionsMaxwell3D.Magnetostatic

    box1 = m3d_app.modeler.create_box([0.5, 1.5, 0.5], [2.5, 5, 5], material="copper")
    box2 = m3d_app.modeler.create_box([9, 1.5, 0.5], [2.5, 5, 5], material="copper")

    current1 = m3d_app.assign_current(box1.top_face_z, amplitude=1, name="Current1")
    current2 = m3d_app.assign_current(box2.top_face_z, amplitude=1, name="Current2")
    current3 = m3d_app.assign_current(box1.bottom_face_z, amplitude=1, name="Current3", swap_direction=True)
    m3d_app.assign_current(box2.bottom_face_z, amplitude=1, name="Current4", swap_direction=True)
    signal_source_1 = MaxwellMatrix.SourceMagnetostatic(
        name=current1.name,
        return_path=current3.name,
        turns_number=5,
    )

    signal_source_2 = MaxwellMatrix.SourceMagnetostatic(
        name=current2.name,
        turns_number=2,
    )

    group_source = MaxwellMatrix.GroupSourcesMagnetostatic(
        source_names=[current1.name, current2.name],
        branches_number=7,
        name="test_group",
    )

    matrix_args = MaxwellMatrix.MatrixMagnetostatic(
        signal_sources=[signal_source_1, signal_source_2],
        group_sources=[group_source],
        matrix_name="test_matrix",
    )
    matrix = m3d_app.assign_matrix(matrix_args)
    assert isinstance(matrix, MaxwellMatrix)
    assert len(matrix.signal_sources) == 2
    assert matrix.signal_sources[0].name == current1.name
    assert matrix.signal_sources[0].return_path == current3.name
    assert matrix.signal_sources[0].turns_number == 5
    assert matrix.signal_sources[1].name == current2.name
    assert matrix.group_sources[0].name == "test_group"
    assert matrix.group_sources[0].branches_number == 7


def test_available_quantities_categories(m3d_app, maxwell_versioned):
    m3d_app.solution_type = maxwell_versioned.ElectroStatic

    box1 = m3d_app.modeler.create_box([0.5, 1.5, 0.5], [2.5, 5, 5])
    voltage1 = m3d_app.assign_voltage(box1.top_face_z, amplitude=1, name="Voltage1")

    setup = m3d_app.create_setup(MaximumPasses=2)
    m3d_app.analyze(setup=setup.name)

    matrix_args = MaxwellMatrix.MatrixElectric(
        signal_sources=[voltage1.name],
        matrix_name="test_matrix",
    )

    matrix = m3d_app.assign_matrix(matrix_args)
    cat = m3d_app.post.available_quantities_categories(context=matrix.name)
    assert isinstance(cat, list)
    assert "C" in cat


def test_available_report_quantities(m3d_app, maxwell_versioned):
    m3d_app.solution_type = maxwell_versioned.ElectroStatic

    box1 = m3d_app.modeler.create_box([0.5, 1.5, 0.5], [2.5, 5, 5])
    voltage1 = m3d_app.assign_voltage(box1.top_face_z, amplitude=1, name="Voltage1")

    setup = m3d_app.create_setup(MaximumPasses=2)
    m3d_app.analyze(setup=setup.name)

    matrix_args = MaxwellMatrix.MatrixElectric(
        signal_sources=[voltage1.name],
        matrix_name="test_matrix",
    )

    matrix = m3d_app.assign_matrix(matrix_args)
    quantities = m3d_app.post.available_report_quantities(
        display_type="Data Table", quantities_category="C", context=matrix.name
    )
    assert isinstance(quantities, list)
    report = m3d_app.post.create_report(
        expressions=quantities,
        plot_type="Data Table",
        context=matrix.name,
        primary_sweep_variable="X",
        variations={"X": "All"},
    )
    assert quantities == report.expressions
    assert report.matrix == matrix.name
    assert matrix.delete()


def test_reduced_matrix(m3d_app, maxwell_versioned):
    m3d_app.solution_type = SolutionsMaxwell3D.ACMagnetic

    box1 = m3d_app.modeler.create_box([0.5, 1.5, 0.5], [2.5, 5, 5], material="copper")
    box2 = m3d_app.modeler.create_box([9, 1.5, 0.5], [2.5, 5, 5], material="copper")
    box3 = m3d_app.modeler.create_box([16.5, 1.5, 0.5], [2.5, 5, 5], material="copper")

    current1 = m3d_app.assign_current([box1.top_face_z], amplitude=1, name="Current1")
    current2 = m3d_app.assign_current([box2.top_face_z], amplitude=1, name="Current2")
    current3 = m3d_app.assign_current([box3.top_face_z], amplitude=1, name="Current3")
    m3d_app.assign_current([box1.bottom_face_z], amplitude=1, name="Current4", swap_direction=True)
    m3d_app.assign_current([box2.bottom_face_z], amplitude=1, name="Current5", swap_direction=True)
    m3d_app.assign_current([box3.bottom_face_z], amplitude=1, name="Current6", swap_direction=True)

    signal_source_1 = MaxwellMatrix.SourceACMagnetic(name=current1.name)
    signal_source_2 = MaxwellMatrix.SourceACMagnetic(name=current2.name)
    signal_source_3 = MaxwellMatrix.SourceACMagnetic(name=current3.name)

    matrix_args = MaxwellMatrix.MatrixACMagnetic(
        signal_sources=[signal_source_1, signal_source_2, signal_source_3],
        matrix_name="test_matrix",
    )

    matrix = m3d_app.assign_matrix(matrix_args)
    assert not matrix.reduced_matrices
    m3d_app.solution_type = SolutionsMaxwell3D.Magnetostatic
    with pytest.raises(AEDTRuntimeError):
        matrix.join_series(sources=["Current1", "Current2"], matrix_name="ReducedMatrix3")
    m3d_app.solution_type = SolutionsMaxwell3D.ACMagnetic
    reduced_matrix = matrix.join_series(sources=["Current1", "Current2", "Current3"], matrix_name="ReducedMatrix1")
    assert reduced_matrix.name == "ReducedMatrix1"
    assert reduced_matrix.parent_matrix.name == matrix.name
    assert "Current1" in reduced_matrix.operations_reduction[0].sources
    reduced_matrix_1 = matrix.join_parallel(["Current1", "Current3"], matrix_name="ReducedMatrix2")
    assert reduced_matrix_1.name == "ReducedMatrix2"
    assert reduced_matrix_1.parent_matrix.name == matrix.name
    sources = reduced_matrix_1.operations_reduction[0].sources
    assert "Current1" in sources
    # update name of join series operation
    join_operation = reduced_matrix_1.update(
        name=reduced_matrix_1.operations_reduction[0].name, operation_type="series", new_name="my_op"
    )
    assert join_operation.sources == sources
    assert join_operation.name == "my_op"
    # update sources of join series operation
    new_sources = ["Current2", "Current3"]
    join_operation_1 = reduced_matrix_1.update(
        name=join_operation.name, operation_type="series", new_sources=new_sources
    )
    assert join_operation_1.sources == new_sources
    with pytest.raises(AEDTRuntimeError):
        reduced_matrix_1.update(name="invalid", operation_type="series")
    with pytest.raises(AEDTRuntimeError):
        reduced_matrix_1.update(name=join_operation.name, operation_type="invalid")
    with pytest.raises(AEDTRuntimeError):
        reduced_matrix_1.delete(name="invalid")
    assert reduced_matrix_1.delete(name="my_op")
    assert len(matrix.reduced_matrices) == 1


def test_initial_mesh_settings(m3d_app):
    assert m3d_app.mesh.initial_mesh_settings
    assert m3d_app.mesh.initial_mesh_settings.props


def test_assign_voltage_drop(m3d_app, maxwell_versioned):
    m3d_app.solution_type = maxwell_versioned.Magnetostatic

    circle = m3d_app.modeler.create_circle(origin=[10, 10, 0], radius=5, orientation="XY")
    v_drop = m3d_app.assign_voltage_drop([circle.faces[0]])
    assert v_drop.props["Faces"][0] == circle.faces[0].id
    assert v_drop.props["Voltage Drop"] == "1mV"


def test_assign_symmetry(m3d_app):
    box = m3d_app.modeler.create_box([0, 1.5, 0], [1, 2.5, 5], name="Coil_1", material="aluminum")
    symmetry = m3d_app.assign_symmetry([box.faces[0]], "symmetry_test")
    assert symmetry
    assert symmetry.props["Faces"][0] == box.faces[0].id
    assert symmetry.props["Name"] == "symmetry_test"
    assert symmetry.props["IsOdd"]
    symmetry_1 = m3d_app.assign_symmetry([box.faces[1]], "symmetry_test_1", False)
    assert symmetry_1
    assert symmetry_1.props["Faces"][0] == box.faces[1].id
    assert symmetry_1.props["Name"] == "symmetry_test_1"
    assert not symmetry_1.props["IsOdd"]
    assert all([bound.type == "Symmetry" for bound in m3d_app.boundaries])


def test_set_bp_curve_loss(m3d_app):
    bp_curve_box = m3d_app.modeler.create_box([0, 0, 0], [10, 10, 10], name="bp_curve_box")
    bp_curve_box.material = "magnesium"
    assert m3d_app.materials["magnesium"].set_bp_curve_coreloss(
        [[0, 0], [0.6, 1.57], [1.0, 4.44], [1.5, 20.562], [2.1, 44.23]],
        kdc=0.002,
        cut_depth=0.0009,
        units="w/kg",
        bunit="tesla",
        frequency=50,
        thickness="0.5mm",
    )


def test_assign_insulating(m3d_app):
    box = m3d_app.modeler.create_box([50, 0, 50], [294, 294, 19], name="box")
    insulating_assignment = m3d_app.assign_insulating(box.name, "insulating")
    assert insulating_assignment.name == "insulating"
    insulating_assignment.name = "insulating_update"
    assert insulating_assignment.update()
    assert insulating_assignment.name == "insulating_update"
    insulating_assignment_face = m3d_app.assign_insulating(box.faces[0], "insulating_2")
    assert insulating_assignment_face.name == "insulating_2"
    insulating_assignment_comb = m3d_app.assign_insulating([box.name, box.faces[0]], "insulating_3")
    assert insulating_assignment_comb.name == "insulating_3"


def test_assign_current_density(m3d_app, maxwell_versioned):
    box = m3d_app.modeler.create_box([50, 0, 50], [294, 294, 19], name="box")
    box1 = m3d_app.modeler.create_box([50, 0, 50], [294, 294, 19], name="box1")

    bound = m3d_app.assign_current_density(box.name, "current_density")
    assert bound
    assert bound.props["Objects"] == [box.name]
    assert bound.props["CurrentDensityX"] == "0"
    assert bound.props["CurrentDensityY"] == "0"
    assert bound.props["CurrentDensityZ"] == "0"
    assert bound.props["CoordinateSystem Name"] == "Global"
    assert bound.props["CoordinateSystem Type"] == "Cartesian"

    m3d_app.solution_type = maxwell_versioned.EddyCurrent
    bound = m3d_app.assign_current_density(
        box.name, "current_density_1", "40deg", current_density_x="3", current_density_y="4"
    )
    assert bound
    assert bound.props["Objects"] == [box.name]
    assert bound.props["Phase"] == "40deg"
    assert bound.props["CurrentDensityX"] == "3"
    assert bound.props["CurrentDensityY"] == "4"
    assert bound.props["CurrentDensityZ"] == "0"
    assert bound.props["CoordinateSystem Name"] == "Global"
    assert bound.props["CoordinateSystem Type"] == "Cartesian"

    bound = m3d_app.assign_current_density([box.name, box1.name], "current_density_2")
    assert bound
    assert bound.props[bound.name]["Objects"] == [box.name, box1.name]
    assert bound.props[bound.name]["Phase"] == "0deg"
    assert bound.props[bound.name]["CurrentDensityX"] == "0"
    assert bound.props[bound.name]["CurrentDensityY"] == "0"
    assert bound.props[bound.name]["CurrentDensityZ"] == "0"
    assert bound.props[bound.name]["CoordinateSystem Name"] == "Global"

    with pytest.raises(ValueError, match="Invalid coordinate system."):
        m3d_app.assign_current_density(box.name, "current_density_3", coordinate_system_type="test")
    with pytest.raises(ValueError, match="Invalid phase unit."):
        m3d_app.assign_current_density(box.name, "current_density_4", phase="5ang")


def test_assign_current_density_terminal(m3d_app, maxwell_versioned):
    box = m3d_app.modeler.create_box([50, 0, 50], [294, 294, 19], name="box")
    density_name = "current_density_t_1"
    assert m3d_app.assign_current_density_terminal(box.faces[0], density_name)
    with pytest.raises(AEDTRuntimeError):
        m3d_app.assign_current_density_terminal(box.faces[0], density_name)
    assert m3d_app.assign_current_density_terminal([box.faces[0], box.faces[1]], "current_density_t_2")
    m3d_app.solution_type = maxwell_versioned.Transient
    with pytest.raises(AEDTRuntimeError):
        m3d_app.assign_current_density_terminal(box.faces[0], "current_density_t_3")


def test_assign_impedance(m3d_app, maxwell_versioned):
    m3d_app.solution_type = maxwell_versioned.Transient

    impedance_box = m3d_app.modeler.create_box([-50, -50, -50], [294, 294, 19], name="impedance_box")
    assert m3d_app.assign_impedance(impedance_box.faces, "copper")
    assert m3d_app.assign_impedance(impedance_box, "copper")
    impedance_assignment = m3d_app.assign_impedance(
        impedance_box.name, permeability=1.3, conductivity=42000000, impedance="ImpedanceExample"
    )
    assert impedance_assignment.name == "ImpedanceExample"
    impedance_assignment.name = "ImpedanceExampleModified"
    assert impedance_assignment.update()

    # Add an impedance using an existing material.
    impedance_box_copper = m3d_app.modeler.create_box([-50, -300, -50], [294, 294, 19], name="impedance_box_copper")
    impedance_assignment_copper = m3d_app.assign_impedance(
        impedance_box_copper.name, material_name="copper", impedance="ImpedanceExampleCopper"
    )
    assert impedance_assignment_copper.name == "ImpedanceExampleCopper"
    impedance_assignment_copper.name = "ImpedanceExampleCopperModified"
    assert impedance_assignment_copper.update()

    # Add an impedance using an existing material with non-linear permeability and
    # modifying its conductivity.
    impedance_box_copper_non_liear = m3d_app.modeler.create_box(
        [-50, -600, -50], [294, 294, 19], name="impedance_box_copper_non_liear"
    )
    impedance_assignment_copper = m3d_app.assign_impedance(
        impedance_box_copper_non_liear.name,
        material_name="copper",
        conductivity=47000000,
        non_linear_permeability=True,
        impedance="ImpedanceExampleCopperNonLinear",
    )
    assert impedance_assignment_copper.name == "ImpedanceExampleCopperNonLinear"
    impedance_assignment_copper.name = "ImpedanceExampleCopperNonLinearModified"
    assert impedance_assignment_copper.update()


@pytest.mark.skipif(DESKTOP_VERSION < "2023.1", reason="Method implemented in AEDT 2023R1")
def test_conduction_paths(m3d_app):
    m3d_app.modeler.create_box([0, 0, 0], [10, 10, 1], material="copper")
    m3d_app.modeler.create_box([0, 0, 0], [-10, 10, 1], material="copper")
    m3d_app.modeler.create_box([-50, -50, -50], [1, 1, 1], material="copper")
    assert len(m3d_app.get_conduction_paths()) == 2


def test_assign_independent_dependent(m3d_app):
    box = m3d_app.modeler.create_box([0, 0, 0], [10, 10, 1], material="copper")
    independent, dependent = m3d_app.assign_master_slave(
        independent=box.faces[1],
        dependent=box.faces[5],
        u_vector_origin_coordinates_master=["0mm", "0mm", "0mm"],
        u_vector_pos_coordinates_master=["10mm", "0mm", "0mm"],
        u_vector_origin_coordinates_slave=["10mm", "0mm", "0mm"],
        u_vector_pos_coordinates_slave=["10mm", "10mm", "0mm"],
    )
    assert independent
    assert dependent
    with pytest.raises(
        ValueError, match=re.escape("Elements of coordinates system must be strings in the form of ``value+unit``.")
    ):
        m3d_app.assign_master_slave(
            independent=box.faces[1],
            dependent=box.faces[5],
            u_vector_origin_coordinates_master=[0, "0mm", "0mm"],
            u_vector_pos_coordinates_master=["10mm", "0mm", "0mm"],
            u_vector_origin_coordinates_slave=["10mm", "0mm", "0mm"],
            u_vector_pos_coordinates_slave=["10mm", "10mm", "0mm"],
        )
    with pytest.raises(
        ValueError, match=re.escape("Elements of coordinates system must be strings in the form of ``value+unit``.")
    ):
        m3d_app.assign_master_slave(
            independent=box.faces[1],
            dependent=box.faces[5],
            u_vector_origin_coordinates_master=["0mm", "0mm", "0mm"],
            u_vector_pos_coordinates_master=[10, "0mm", "0mm"],
            u_vector_origin_coordinates_slave=["10mm", "0mm", "0mm"],
            u_vector_pos_coordinates_slave=["10mm", "10mm", "0mm"],
        )
    with pytest.raises(
        ValueError, match=re.escape("Elements of coordinates system must be strings in the form of ``value+unit``.")
    ):
        m3d_app.assign_master_slave(
            independent=box.faces[1],
            dependent=box.faces[5],
            u_vector_origin_coordinates_master=["0mm", "0mm", "0mm"],
            u_vector_pos_coordinates_master=["10mm", "0mm", "0mm"],
            u_vector_origin_coordinates_slave=[10, "0mm", "0mm"],
            u_vector_pos_coordinates_slave=["10mm", "10mm", "0mm"],
        )
    with pytest.raises(
        ValueError, match=re.escape("Elements of coordinates system must be strings in the form of ``value+unit``.")
    ):
        m3d_app.assign_master_slave(
            independent=box.faces[1],
            dependent=box.faces[5],
            u_vector_origin_coordinates_master=["0mm", "0mm", "0mm"],
            u_vector_pos_coordinates_master=["10mm", "0mm", "0mm"],
            u_vector_origin_coordinates_slave=["10mm", "0mm", "0mm"],
            u_vector_pos_coordinates_slave=[10, "10mm", "0mm"],
        )
    with pytest.raises(ValueError, match="Please provide a list of coordinates for U vectors."):
        m3d_app.assign_master_slave(
            independent=box.faces[1],
            dependent=box.faces[5],
            u_vector_origin_coordinates_master="0mm",
            u_vector_pos_coordinates_master=["10mm", "0mm", "0mm"],
            u_vector_origin_coordinates_slave=["10mm", "0mm", "0mm"],
            u_vector_pos_coordinates_slave=["10mm", "10mm", "0mm"],
        )


def test_add_mesh_link(m3d_app, test_tmp_dir, maxwell_versioned):
    m3d_app.solution_type = maxwell_versioned.Transient
    m3d_app.create_setup()
    m3d_app.duplicate_design(m3d_app.design_name)
    m3d_app.set_active_design(m3d_app.design_list[1])
    m3d_app["test"] = "2deg"
    assert m3d_app.setups[0].add_mesh_link(design=m3d_app.design_list[0])
    meshlink_props = m3d_app.setups[0].props["MeshLink"]
    assert meshlink_props["Project"] == "This Project*"
    assert meshlink_props["PathRelativeTo"] == "TargetProject"
    assert meshlink_props["Design"] == m3d_app.design_list[0]
    assert meshlink_props["Soln"] == m3d_app.nominal_adaptive
    assert not m3d_app.setups[0].add_mesh_link(design="invalid")
    assert not m3d_app.setups[0].add_mesh_link(design=m3d_app.design_list[0], solution="invalid")
    nominal_values = m3d_app.available_variations.nominal_variation(dependent_params=False)
    assert m3d_app.setups[0].add_mesh_link(design=m3d_app.design_list[0], parameters=nominal_values)
    example_project = test_tmp_dir / "test.aedt"
    m3d_app.save_project(str(example_project))
    example_project_copy = test_tmp_dir / "test_copy.aedt"
    shutil.copyfile(example_project, example_project_copy)
    assert m3d_app.setups[0].add_mesh_link(design=m3d_app.design_list[0], project=str(example_project_copy))


def test_set_variable(m3d_app):
    m3d_app.variable_manager.set_variable("var_test", expression="123")
    m3d_app["var_test"] = "234"
    assert "var_test" in m3d_app.variable_manager.design_variable_names
    assert m3d_app.variable_manager.design_variables["var_test"].expression == "234"


def test_cylindrical_gap(m3d_app):
    inner_cylinder = m3d_app.modeler.create_cylinder(Axis.Z, [0, 0, 0], 5, 10, 0, "inner")
    outer_cylinder = m3d_app.modeler.create_cylinder(Axis.Z, [0, 0, 0], 7, 12, 0, "outer")
    assert m3d_app.mesh.assign_cylindrical_gap(outer_cylinder.name, name="cyl_gap_test")
    assert not m3d_app.mesh.assign_cylindrical_gap([inner_cylinder.name, outer_cylinder.name])
    assert not m3d_app.mesh.assign_cylindrical_gap(outer_cylinder.name)
    [
        x.delete()
        for x in m3d_app.mesh.meshoperations[:]
        if x.type == "Cylindrical Gap Based" or x.type == "CylindricalGap"
    ]
    assert m3d_app.mesh.assign_cylindrical_gap(outer_cylinder.name, name="cyl_gap_test", clone_mesh=True)
    [
        x.delete()
        for x in m3d_app.mesh.meshoperations[:]
        if x.type == "Cylindrical Gap Based" or x.type == "CylindricalGap"
    ]
    assert not m3d_app.mesh.assign_cylindrical_gap(
        outer_cylinder.name, name="cyl_gap_test", band_mapping_angle=5, clone_mesh=True
    )
    assert not m3d_app.mesh.assign_cylindrical_gap(
        outer_cylinder.name, name="cyl_gap_test", band_mapping_angle=2, clone_mesh=True, moving_side_layers=0
    )
    assert not m3d_app.mesh.assign_cylindrical_gap(
        outer_cylinder.name, name="cyl_gap_test", band_mapping_angle=2, clone_mesh=True, static_side_layers=0
    )


def test_objects_segmentation(m3d_app):
    cylinder = m3d_app.modeler.create_cylinder(Axis.Z, [0, 0, 0], 5, 10, 0, "cyl")
    segments_number = 5
    sheets = m3d_app.modeler.objects_segmentation(assignment=cylinder, segments=segments_number, apply_mesh_sheets=True)
    assert isinstance(sheets, tuple)
    assert isinstance(sheets[0], dict)
    assert isinstance(sheets[1], dict)
    assert isinstance(sheets[0][cylinder.name], list)
    assert len(sheets[0][cylinder.name]) == segments_number - 1

    cylinder = m3d_app.modeler.create_cylinder(Axis.Z, [1, 0, 0], 5, 10, 0, "cyl")
    segments_number = 4
    mesh_sheets_number = 3
    sheets = m3d_app.modeler.objects_segmentation(
        cylinder.id, segments=segments_number, apply_mesh_sheets=True, mesh_sheets=mesh_sheets_number
    )
    assert isinstance(sheets, tuple)
    assert isinstance(sheets[0][cylinder.name], list)
    assert len(sheets[0][cylinder.name]) == segments_number - 1
    assert isinstance(sheets[1][cylinder.name], list)
    assert len(sheets[1][cylinder.name]) == mesh_sheets_number

    cylinder = m3d_app.modeler.create_cylinder(Axis.Z, [2, 0, 0], 5, 10, 0, "cyl")
    segmentation_thickness = 1
    sheets = m3d_app.modeler.objects_segmentation(
        cylinder, segmentation_thickness=segmentation_thickness, apply_mesh_sheets=True
    )
    assert isinstance(sheets, tuple)
    assert isinstance(sheets[0][cylinder.name], list)
    segments_number = round(
        GeometryOperators.points_distance(cylinder.top_face_z.center, cylinder.bottom_face_z.center)
        / segmentation_thickness
    )
    assert len(sheets[0][cylinder.name]) == segments_number - 1
    assert not m3d_app.modeler.objects_segmentation(cylinder.name)
    assert not m3d_app.modeler.objects_segmentation(
        cylinder.name, segmentation_thickness=segmentation_thickness, segments=segments_number
    )

    cylinder = m3d_app.modeler.create_cylinder(Axis.Z, [3, 0, 0], 5, 10, 0, "cyl")
    segments_number = 10
    sheets = m3d_app.modeler.objects_segmentation(cylinder.name, segments=segments_number)
    assert isinstance(sheets, dict)
    assert isinstance(sheets[cylinder.name], list)
    assert len(sheets[cylinder.name]) == segments_number - 1


def test_import_dxf(m3d_app):
    dxf_file = os.path.join(TESTS_GENERAL_PATH, "example_models", "cad", "DXF", "dxf2.dxf")
    dxf_layers = get_dxf_layers(dxf_file)
    assert isinstance(dxf_layers, list)
    assert m3d_app.import_dxf(dxf_file, dxf_layers)
    assert m3d_app.import_dxf(dxf_file, dxf_layers, self_stitch_tolerance=0.2)


def test_assign_flux_tangential(m3d_app):
    box = m3d_app.modeler.create_box([50, 0, 50], [294, 294, 19], name="Box")
    with pytest.raises(AEDTRuntimeError):
        m3d_app.assign_flux_tangential(box.faces[0])
    m3d_app.solution_type = "TransientAPhiFormulation"
    assert m3d_app.assign_flux_tangential(box.faces[0], "FluxExample")
    assert m3d_app.assign_flux_tangential(box.faces[0].id, "FluxExample")


def test_assign_tangential_h_field(m3d_app, maxwell_versioned):
    box = m3d_app.modeler.create_box([0, 0, 0], [10, 10, 10])
    assert m3d_app.assign_tangential_h_field(box.bottom_face_x, 1, 0, 2, 0)
    rect = m3d_app.modeler.create_rectangle(2, [0, 0, 0], [5, 5])
    assert m3d_app.assign_tangential_h_field(rect.name, 1, 0, 1, 0, u_pos=["5mm", "0mm", "0mm"])
    m3d_app.solution_type = maxwell_versioned.EddyCurrent
    assert m3d_app.assign_tangential_h_field(box.bottom_face_x, 1, 0, 2, 0)
    m3d_app.solution_type = maxwell_versioned.Transient
    with pytest.raises(
        AEDTRuntimeError,
        match="Tangential H Field is applicable only to Magnetostatic and EddyCurrent or AC Magnetic solution types.",
    ):
        m3d_app.assign_tangential_h_field(box.bottom_face_x, 1, 0, 2, 0)


def test_assign_zero_tangential_h_field(m3d_app, maxwell_versioned):
    box = m3d_app.modeler.create_box([0, 0, 0], [10, 10, 10])
    with pytest.raises(
        AEDTRuntimeError,
        match="Tangential H Field is applicable only to EddyCurrent or AC Magnetic solution types.",
    ):
        m3d_app.assign_zero_tangential_h_field(box.top_face_z)
    m3d_app.solution_type = maxwell_versioned.EddyCurrent
    assert m3d_app.assign_zero_tangential_h_field(box.top_face_z)


def test_assign_radiation(m3d_app, maxwell_versioned):
    rect = m3d_app.modeler.create_rectangle(0, [0, 0, 0], [5, 5], material="aluminum")
    rect2 = m3d_app.modeler.create_rectangle(0, [15, 20, 0], [5, 5], material="aluminum")
    box = m3d_app.modeler.create_box([15, 20, 0], [5, 5, 5], material="aluminum")
    box2 = m3d_app.modeler.create_box([150, 20, 0], [50, 5, 10], material="aluminum")
    with pytest.raises(
        AEDTRuntimeError, match="Excitation applicable only to Eddy Current or AC Magnetic solution types."
    ):
        m3d_app.assign_radiation([rect, rect2, box, box2.faces[0]])
    m3d_app.solution_type = maxwell_versioned.EddyCurrent
    bound = m3d_app.assign_radiation([rect, rect2, box, box2.faces[0]])
    assert bound
    bound2 = m3d_app.assign_radiation([rect, rect2, box, box2.faces[0]], "my_rad")
    assert bound2
    bound3 = m3d_app.assign_radiation([rect, rect2, box, box2.faces[0]], "my_rad")
    assert bound2.name != bound3.name


def test_solution_types_setup(m3d_app, maxwell_versioned):
    setup = m3d_app.create_setup(setup_type=m3d_app.solution_type)
    assert setup
    setup.delete()
    m3d_app.solution_type = maxwell_versioned.Transient
    setup = m3d_app.create_setup(setup_type=m3d_app.solution_type)
    assert setup
    setup.delete()
    m3d_app.solution_type = maxwell_versioned.EddyCurrent
    setup = m3d_app.create_setup(setup_type=m3d_app.solution_type)
    assert setup
    setup.delete()
    m3d_app.solution_type = maxwell_versioned.ElectroStatic
    setup = m3d_app.create_setup(setup_type=m3d_app.solution_type)
    assert setup
    setup.delete()
    m3d_app.solution_type = maxwell_versioned.DCConduction
    setup = m3d_app.create_setup(setup_type=m3d_app.solution_type)
    assert setup
    setup.delete()
    m3d_app.solution_type = maxwell_versioned.ACConduction
    setup = m3d_app.create_setup(setup_type=m3d_app.solution_type)
    assert setup
    setup.delete()
    if DESKTOP_VERSION < "2025.2":
        m3d_app.solution_type = maxwell_versioned.ElectroDCConduction
    else:
        m3d_app.solution_type = maxwell_versioned.ElectricDCConduction
    setup = m3d_app.create_setup(setup_type=m3d_app.solution_type)
    assert setup
    setup.delete()
    m3d_app.solution_type = maxwell_versioned.ElectricTransient
    setup = m3d_app.create_setup(setup_type=m3d_app.solution_type)
    assert setup
    setup.delete()
    if DESKTOP_VERSION < "2025.2":
        m3d_app.solution_type = maxwell_versioned.TransientAPhiFormulation
    else:
        m3d_app.solution_type = maxwell_versioned.TransientAPhi
    setup = m3d_app.create_setup(setup_type=m3d_app.solution_type)
    assert setup
    setup.delete()


def test_assign_floating(m3d_app, maxwell_versioned):
    box = m3d_app.modeler.create_box([0, 0, 0], [10, 10, 10], name="Box1")
    with pytest.raises(
        AEDTRuntimeError,
        match="Assign floating excitation is only valid for electrostatic or electric transient solvers.",
    ):
        m3d_app.assign_floating(assignment=box, charge_value=3)
    m3d_app.solution_type = maxwell_versioned.ElectroStatic
    floating = m3d_app.assign_floating(assignment=box, charge_value=3)
    assert floating
    assert floating.props["Objects"][0] == box.name
    assert floating.props["Value"] == "3"
    floating1 = m3d_app.assign_floating(assignment=[box.faces[0], box.faces[1]], charge_value=3)
    assert floating1


def test_assign_resistive_sheet(m3d_app, maxwell_versioned):
    m3d_app.solution_type = maxwell_versioned.EddyCurrent
    m3d_app.modeler.create_box(origin=[0, 0, 0], sizes=[0.4, -1, 0.8], name="my_box", material="copper")
    my_rectangle = m3d_app.modeler.create_rectangle(orientation=1, origin=[0, 0, 0.8], sizes=[-1, 0.4], name="my_rect")
    # From 2025.1, this boundary can only be assigned to Sheets that touch conductor Solids.
    bound = m3d_app.assign_resistive_sheet(assignment=my_rectangle.faces[0], resistance="3ohm")
    assert bound
    assert bound.props["Faces"][0] == my_rectangle.faces[0].id
    assert bound.props["Resistance"] == "3ohm"
    m3d_app.solution_type = maxwell_versioned.Magnetostatic
    bound = m3d_app.assign_resistive_sheet(assignment=my_rectangle.name, non_linear=True)
    assert bound.props["Nonlinear"]
    assert bound.props["Objects"][0] == my_rectangle.name
    m3d_app.solution_type = maxwell_versioned.ACConduction
    with pytest.raises(AEDTRuntimeError):
        m3d_app.assign_resistive_sheet(assignment=my_rectangle, resistance="3ohm")


def test_assign_layout_force(layout_comp):
    nets_layers = {
        "<no-net>": ["<no-layer>", "TOP", "UNNAMED_000", "UNNAMED_002"],
        "GND": ["BOTTOM", "Region", "UNNAMED_010", "UNNAMED_012"],
        "V3P3_S5": ["LYR_1", "LYR_2", "UNNAMED_006", "UNNAMED_008"],
    }
    layout_force = layout_comp.assign_layout_force(nets_layers, "LC1_1")
    assert layout_force
    assert isinstance(layout_force, MaxwellLayoutForce)
    with pytest.raises(AEDTRuntimeError, match="Provided component name doesn't exist in current design."):
        layout_comp.assign_layout_force(nets_layers, "LC1_3")
    nets_layers = {"1V0": "Bottom Solder"}
    assert layout_comp.assign_layout_force(nets_layers, "LC1_1")


@pytest.mark.skipif(is_linux, reason="EDB object is not loaded.")
def test_enable_harmonic_force_layout(layout_comp):
    comp = layout_comp.modeler.user_defined_components["LC1_1"]
    layers = list(comp.layout_component.layers.keys())
    nets = list(comp.layout_component.nets.keys())
    layout_comp.enable_harmonic_force_on_layout_component(
        comp.name,
        {nets[0]: layers[1::2], nets[1]: layers[1::2]},
        force_type=2,
        window_function="Rectangular",
        use_number_of_last_cycles=True,
        last_cycles_number=1,
        calculate_force="Harmonic",
        start_time="10us",
        stop_time="20us",
        use_number_of_cycles_for_stop_time=True,
        number_of_cycles_for_stop_time=1,
    )
    layout_comp.solution_type = "Magnetostatic"
    with pytest.raises(
        AEDTRuntimeError, match="This methods work only with Maxwell TransientAPhiFormulation Analysis."
    ):
        layout_comp.enable_harmonic_force_on_layout_component(comp.name, {nets[0]: layers[1::2], nets[1]: layers[1::2]})


@pytest.mark.skipif(
    DESKTOP_VERSION < "2025.1",
    reason="Not working in non-graphical in version lower than 2025.1",
)
def test_order_coil_terminals(m3d_app):
    m3d_app.solution_type = "TransientAPhiFormulation"
    c1 = m3d_app.modeler.create_cylinder(
        orientation=Axis.Z, origin=[-3, 0, 0], radius=1, height=10, name="Cylinder1", material="copper"
    )

    c2 = m3d_app.modeler.create_cylinder(
        orientation=Axis.Z, origin=[0, 0, 0], radius=1, height=10, name="Cylinder2", material="copper"
    )

    c3 = m3d_app.modeler.create_cylinder(
        orientation=Axis.Z, origin=[3, 0, 0], radius=1, height=10, name="Cylinder3", material="copper"
    )

    m3d_app.assign_coil(assignment=[c1.top_face_z], name="CoilTerminal1")
    m3d_app.assign_coil(assignment=[c1.bottom_face_z], name="CoilTerminal2", polarity="Negative")

    m3d_app.assign_coil(assignment=[c2.top_face_z], name="CoilTerminal3", polarity="Negative")
    m3d_app.assign_coil(assignment=[c2.bottom_face_z], name="CoilTerminal4")

    m3d_app.assign_coil(assignment=[c3.top_face_z], name="CoilTerminal5")
    m3d_app.assign_coil(assignment=[c3.bottom_face_z], name="CoilTerminal6", polarity="Negative")

    m3d_app.assign_winding(is_solid=True, current="1A", name="Winding1")

    terminal_list_order = [
        "CoilTerminal1",
        "CoilTerminal2",
        "CoilTerminal3",
        "CoilTerminal4",
        "CoilTerminal5",
        "CoilTerminal6",
    ]

    m3d_app.add_winding_coils(assignment="Winding1", coils=terminal_list_order)

    terminal_list_order = [
        "CoilTerminal1",
        "CoilTerminal2",
        "CoilTerminal4",
        "CoilTerminal3",
        "CoilTerminal5",
        "CoilTerminal6",
    ]
    assert m3d_app.order_coil_terminals(winding_name="Winding1", list_of_terminals=terminal_list_order)
    m3d_app.solution_type = "Transient"
    with pytest.raises(AEDTRuntimeError, match="Only available in Transient A-Phi Formulation solution type."):
        m3d_app.order_coil_terminals(winding_name="Winding1", list_of_terminals=terminal_list_order)


def test_assign_sink(m3d_app, maxwell_versioned):
    m3d_app.solution_type = maxwell_versioned.DCConduction
    m3d_app.modeler.create_cylinder(
        orientation="Z", origin=[0, 0, 0], radius=2, height=1, name="mycyl", material="copper"
    )
    face_sink = m3d_app.modeler.get_faceid_from_position(position=[0, 0, 1], assignment="mycyl")
    bound = m3d_app.assign_sink(assignment=face_sink, name="my_sink")
    assert bound
    assert bound.name == "my_sink"
    m3d_app.solution_type = maxwell_versioned.Magnetostatic
    with pytest.raises(AEDTRuntimeError):
        m3d_app.assign_sink(assignment=face_sink, name="my_sink")
