# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 - 2024 ANSYS, Inc. and/or its affiliates.
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

# import os
# import shutil

# from ansys.aedt.core import Maxwell3d
from ansys.aedt.core.generic.constants import SOLUTIONS
from ansys.aedt.core.generic.general_methods import generate_unique_name
from ansys.aedt.core.generic.general_methods import is_linux
import pytest

# from tests import TESTS_GENERAL_PATH
from tests.system.general.conftest import config

# from tests.system.general.conftest import desktop_version

try:
    from IPython.display import Image

    ipython_available = True
except ImportError:
    ipython_available = False

test_subfolder = "TMaxwell"

transient = "Transient_StrandedWindings"

cyl_gap_name = "Motor3D_cyl_gap"

layout_component_name = "LayoutForce"

# @pytest.fixture(scope="class")
# def m3dtransient(add_app):
#     app = add_app(application=Maxwell3d, project_name=transient, subfolder=test_subfolder)
#     yield app
#     app.close_project(app.project_name)

#
# @pytest.fixture(scope="class")
# def cyl_gap(add_app):
#     app = add_app(application=Maxwell3d, project_name=cyl_gap_name, subfolder=test_subfolder)
#     return app
#
#
# @pytest.fixture(scope="class")
# def layout_comp(add_app):
#     if desktop_version > "2023.1":
#         app = add_app(application=Maxwell3d, project_name=layout_component_name, subfolder=test_subfolder)
#     else:
#         app = None
#     return app


class TestClass:

    @pytest.mark.skipif(config["NonGraphical"], reason="Test is failing on build machine")
    def test_display(self, m3d_app):
        img = m3d_app.post.nb_display(show_axis=True, show_grid=True, show_ruler=True)
        assert isinstance(img, Image)

    def test_litz_wire(self, m3d_app):
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

    def test_lamination(self, m3d_app):
        m3d_app.materials["titanium"].stacking_type = "Lamination"
        m3d_app.materials["titanium"].stacking_factor = "0.99"
        m3d_app.materials["titanium"].stacking_direction = "V(3)"
        m3d_app.materials["titanium"].stacking_direction = "V(2)"
        assert m3d_app.materials["titanium"].stacking_type == "Lamination"
        assert m3d_app.materials["titanium"].stacking_factor == "0.99"
        assert m3d_app.materials["titanium"].stacking_direction == "V(2)"

    def test_coil_terminals(self, m3d_app):
        coil_hole = m3d_app.modeler.create_box([-50, -50, 0], [100, 100, 100], name="Coil_Hole")
        coil = m3d_app.modeler.create_box([-100, -100, 0], [200, 200, 100], name="Coil")
        m3d_app.modeler.subtract([coil], [coil_hole])

        m3d_app.modeler.section(["Coil"], m3d_app.PLANE.ZX)
        m3d_app.modeler.separate_bodies(["Coil_Section1"])
        assert m3d_app.assign_current(["Coil_Section1"], amplitude=2472)
        assert m3d_app.assign_voltage(m3d_app.modeler["Coil_Section1_Separate1"].faces[0].id, amplitude=1)
        m3d_app.solution_type = "Magnetostatic"
        assert m3d_app.assign_current(["Coil_Section1"], amplitude=2472)
        assert m3d_app.assign_voltage(m3d_app.modeler["Coil_Section1_Separate1"].faces[0].id, amplitude=1)

    def test_assign_winding(self, m3d_app):
        coil_hole = m3d_app.modeler.create_box([-50, -50, 0], [100, 100, 100], name="Coil_Hole")
        coil = m3d_app.modeler.create_box([-100, -100, 0], [200, 200, 100], name="Coil")
        m3d_app.modeler.subtract([coil], [coil_hole])

        m3d_app.modeler.section(["Coil"], m3d_app.PLANE.ZX)
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

    def test_assign_coil(self, m3d_app):
        coil_hole = m3d_app.modeler.create_box([-50, -50, 0], [100, 100, 100], name="Coil_Hole")
        coil = m3d_app.modeler.create_box([-100, -100, 0], [200, 200, 100], name="Coil")
        m3d_app.modeler.subtract([coil], [coil_hole])
        m3d_app.modeler.section(["Coil"], m3d_app.PLANE.ZX)
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

    def test_create_air_region(self, m3d_app):
        region = m3d_app.modeler.create_air_region(*[300] * 6)
        assert region.material_name == "air"

    def test_eddy_effects_on(self, m3d_app):
        m3d_app.solution_type = SOLUTIONS.Maxwell3d.EddyCurrent
        plate_vacuum = m3d_app.modeler.create_box([-3, -3, 0], [1.5, 1.5, 0.4], name="Plate_vaccum")
        assert not m3d_app.eddy_effects_on(plate_vacuum, enable_eddy_effects=True)
        plate = m3d_app.modeler.create_box([-1, -1, 0], [1.5, 1.5, 0.4], name="Plate", material="copper")
        assert m3d_app.eddy_effects_on(plate, enable_eddy_effects=True)
        assert m3d_app.oboundary.GetEddyEffect("Plate")
        assert m3d_app.oboundary.GetDisplacementCurrent("Plate")
        m3d_app.eddy_effects_on(["Plate"], enable_eddy_effects=False)
        assert not m3d_app.oboundary.GetEddyEffect("Plate")
        assert not m3d_app.oboundary.GetDisplacementCurrent("Plate")

    def test_create_setup(self, m3d_app):
        m3d_app.solution_type = SOLUTIONS.Maxwell3d.EddyCurrent
        setup = m3d_app.create_setup()
        setup.props["MaximumPasses"] = 12
        setup.props["MinimumPasses"] = 2
        setup.props["MinimumConvergedPasses"] = 1
        setup.props["PercentRefinement"] = 30
        setup.props["Frequency"] = "200Hz"
        dc_freq = 0.1
        stop_freq = 10
        count = 1
        assert setup.add_eddy_current_sweep("LinearStep", dc_freq, stop_freq, count, clear=True)
        assert isinstance(setup.props["SweepRanges"]["Subrange"], dict)
        assert setup.props["SaveAllFields"]
        assert setup.add_eddy_current_sweep("LinearCount", dc_freq, stop_freq, count, clear=False)
        assert isinstance(setup.props["SweepRanges"]["Subrange"], list)
        assert setup.add_eddy_current_sweep("SinglePoints", start_frequency=0.01, clear=False)
        assert setup.update()
        assert setup.enable_expression_cache(["CoreLoss"], "Fields", "Phase='0deg' ", True)
        assert setup.props["UseCacheFor"] == ["Pass", "Freq"]
        assert setup.disable()
        assert setup.enable()

    def test_create_parametrics(self, m3d_app):
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
    def test_expression_cache(self, m3d_app):
        setup = m3d_app.create_setup()
        setup.props["MaximumPasses"] = 12
        setup.props["MinimumPasses"] = 2
        setup.props["MinimumConvergedPasses"] = 1
        setup.props["PercentRefinement"] = 30
        setup.props["Frequency"] = "200Hz"
        setup.update()
        assert setup.enable_expression_cache(["CoreLoss"], "Fields", "Phase='0deg' ", True)

    def test_assign_length_mesh(self, m3d_app):
        plate = m3d_app.modeler.create_box([0, 0, 0], [1.5, 1.5, 0.5], name="Plate")
        assert m3d_app.mesh.assign_length_mesh(plate)
        assert m3d_app.mesh.assign_length_mesh(plate, maximum_length=1, maximum_elements=1200)
        assert m3d_app.mesh.assign_length_mesh(plate, name="test_mesh")
        assert m3d_app.mesh.assign_length_mesh(plate, name="test_mesh")

    def test_assign_skin_depth(self, m3d_app):
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

    def test_assign_curvilinear_elements(self, m3d_app):
        box = m3d_app.modeler.create_box([30, 0, 0], [40, 10, 5])
        assert m3d_app.mesh.assign_curvilinear_elements(box, "1mm")
        assert m3d_app.mesh.assign_curvilinear_elements(box, "1mm", name="test")
        assert m3d_app.mesh.assign_curvilinear_elements(box, "1mm", name="test")

    def test_assign_edge_cut(self, m3d_app):
        box = m3d_app.modeler.create_box([30, 0, 0], [40, 10, 5])
        assert m3d_app.mesh.assign_edge_cut(box)
        assert m3d_app.mesh.assign_edge_cut(box, name="edge_cute")
        assert m3d_app.mesh.assign_edge_cut(box, name="edge_cute")

    def test_assign_density_control(self, m3d_app):
        box = m3d_app.modeler.create_box([30, 0, 0], [40, 10, 5])
        assert m3d_app.mesh.assign_density_control(box, maximum_element_length="2mm", layers_number="3")
        assert m3d_app.mesh.assign_density_control(
            box, maximum_element_length="2mm", layers_number="3", name="density_ctrl"
        )
        assert m3d_app.mesh.assign_density_control(
            box, maximum_element_length="2mm", layers_number="3", name="density_ctrl"
        )

    def test_assign_rotational_layer(self, m3d_app):
        box = m3d_app.modeler.create_box([30, 0, 0], [40, 10, 5])
        assert m3d_app.mesh.assign_rotational_layer(box)
        assert m3d_app.mesh.assign_rotational_layer(box, name="my_rotational")
        assert m3d_app.mesh.assign_rotational_layer(box, name="my_rotational")

    def test_assign_initial_mesh_slider(self, m3d_app):
        assert m3d_app.mesh.assign_initial_mesh_from_slider(4)

    def test_assign_initial_mesh(self, m3d_app):
        assert m3d_app.mesh.assign_initial_mesh(surface_deviation="2mm")

    @pytest.mark.skipif(is_linux, reason="Crashing on Linux")
    def test_create_udp(self, m3d_app):
        my_udp = []
        udp_data = ["DiaGap", "102mm"]
        my_udp.append(udp_data)
        udp_data = ["Length", "100mm"]
        my_udp.append(udp_data)
        udp_data = ["Poles", "8"]
        my_udp.append(udp_data)
        udp_data = ["EmbraceTip", "0.29999999999999999"]
        my_udp.append(udp_data)
        udp_data = ["EmbraceRoot", "1.2"]
        my_udp.append(udp_data)
        udp_data = ["ThickTip", "5mm"]
        my_udp.append(udp_data)
        udp_data = ["ThickRoot", "10mm"]
        my_udp.append(udp_data)
        udp_data = ["ThickShoe", "8mm"]
        my_udp.append(udp_data)
        udp_data = ["DepthSlot", "12mm"]
        my_udp.append(udp_data)
        udp_data = ["ThickYoke", "10mm"]
        my_udp.append(udp_data)
        udp_data = ["LengthPole", "90mm"]
        my_udp.append(udp_data)
        udp_data = ["LengthMag", "0mm"]
        my_udp.append(udp_data)
        udp_data = ["SegAngle", "5deg"]
        my_udp.append(udp_data)
        udp_data = ["LenRegion", "200mm"]
        my_udp.append(udp_data)
        udp_data = ["InfoCore", "0"]
        my_udp.append(udp_data)

        # Test udp with a custom name.
        my_udpName = "MyClawPoleCore"
        udp = m3d_app.modeler.create_udp(
            dll="RMxprt/ClawPoleCore", parameters=my_udp, library="syslib", name=my_udpName
        )

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
    def test_create_udm(self, m3d_app):
        my_udm = []
        udm_data = ["ILD Thickness (ILD)", "0.006mm"]
        my_udm.append(udm_data)
        udm_data = ["Line Spacing (LS)", "0.004mm"]
        my_udm.append(udm_data)
        udm_data = ["Line Thickness (LT)", "0.005mm"]
        my_udm.append(udm_data)
        udm_data = ["Line Width (LW)", "0.004mm"]
        my_udm.append(udm_data)
        udm_data = ["No. of Turns (N)", 2]
        my_udm.append(udm_data)
        udm_data = ["Outer Diameter (OD)", "0.15mm"]
        my_udm.append(udm_data)
        udm_data = ["Substrate Thickness", "0.2mm"]
        my_udm.append(udm_data)
        udm_data = [
            "Inductor Type",
            '"Square,Square,Octagonal,Circular,Square-Differential,Octagonal-Differential,Circular-Differential"',
        ]
        my_udm.append(udm_data)
        udm_data = ["Underpass Thickness (UT)", "0.001mm"]
        my_udm.append(udm_data)
        udm_data = ["Via Thickness (VT)", "0.001mm"]
        my_udm.append(udm_data)

        assert m3d_app.modeler.create_udm(
            udm_full_name="Maxwell3D/OnDieSpiralInductor.py", parameters=my_udm, library="syslib"
        )

    def test_assign_torque(self, m3d_app):
        coil = m3d_app.modeler.create_box([-100, -100, 0], [200, 200, 100], name="Coil")
        torque = m3d_app.assign_torque(coil)
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

    def test_assign_force(self, m3d_app):
        coil = m3d_app.modeler.create_box([-100, -100, 0], [200, 200, 100], name="Coil")
        force = m3d_app.assign_force(coil)
        assert force.type == "Force"
        assert force.props["Objects"][0] == "Coil"
        assert force.props["Reference CS"] == "Global"
        assert force.props["Is Virtual"]
        assert force.delete()
        force = m3d_app.assign_force(assignment="Coil", is_virtual=False, force_name="Force_Test")
        assert force.name == "Force_Test"
        assert not force.props["Is Virtual"]

    def test_assign_translate_motion(self, m3d_app):
        m3d_app.solution_type = SOLUTIONS.Maxwell3d.Transient
        m3d_app.modeler.create_box([0, 0, 0], [10, 10, 10], name="Inner_Box")
        m3d_app.modeler.create_box([0, 0, 0], [30, 20, 20], name="Outer_Box")
        bound = m3d_app.assign_translate_motion("Outer_Box", velocity=1, mechanical_transient=True)
        assert bound
        assert bound.props["Velocity"] == "1m_per_sec"

    def test_set_core_losses(self, m3d_app):
        m3d_app.solution_type = SOLUTIONS.Maxwell3d.EddyCurrent
        m3d_app.modeler.create_box([0, 0, 0], [10, 10, 10], name="my_box", material="Material_3F3")
        assert m3d_app.set_core_losses(["my_box"])
        assert m3d_app.set_core_losses(["my_box"], True)

    def test_assign_matrix(self, m3d_app):
        m3d_app.solution_type = SOLUTIONS.Maxwell3d.ElectroStatic

        rectangle1 = m3d_app.modeler.create_rectangle(0, [0.5, 1.5, 0], [2.5, 5], name="Sheet1")
        rectangle2 = m3d_app.modeler.create_rectangle(0, [9, 1.5, 0], [2.5, 5], name="Sheet2")
        rectangle3 = m3d_app.modeler.create_rectangle(0, [16.5, 1.5, 0], [2.5, 5], name="Sheet3")

        m3d_app.assign_voltage(rectangle1.faces[0], amplitude=1, name="Voltage1")
        m3d_app.assign_voltage(rectangle2.faces[0], amplitude=1, name="Voltage2")
        m3d_app.assign_voltage(rectangle3.faces[0], amplitude=1, name="Voltage3")

        setup = m3d_app.create_setup(MaximumPasses=2)
        m3d_app.analyze(setup=setup.name)

        matrix = m3d_app.assign_matrix(assignment="Voltage1")
        assert matrix.props["MatrixEntry"]["MatrixEntry"][0]["Source"] == "Voltage1"
        assert matrix.props["MatrixEntry"]["MatrixEntry"][0]["NumberOfTurns"] == "1"
        matrix = m3d_app.assign_matrix(
            assignment=["Voltage1", "Voltage3"], matrix_name="Test1", group_sources="Voltage2"
        )
        assert matrix.props["MatrixEntry"]["MatrixEntry"][1]["Source"] == "Voltage3"
        assert matrix.props["MatrixEntry"]["MatrixEntry"][1]["NumberOfTurns"] == "1"
        m3d_app.solution_type = SOLUTIONS.Maxwell3d.Transient
        winding1 = m3d_app.assign_winding("Sheet1", name="Current1")
        matrix = m3d_app.assign_matrix(assignment="Current1")
        assert not matrix

    def test_available_quantities_categories(self, m3d_app):
        m3d_app.solution_type = SOLUTIONS.Maxwell3d.ElectroStatic

        rectangle1 = m3d_app.modeler.create_rectangle(0, [0.5, 1.5, 0], [2.5, 5], name="Sheet1")

        m3d_app.assign_voltage(rectangle1.faces[0], amplitude=1, name="Voltage1")

        setup = m3d_app.create_setup(MaximumPasses=2)
        m3d_app.analyze(setup=setup.name)

        matrix = m3d_app.assign_matrix(assignment="Voltage1")
        assert matrix.props["MatrixEntry"]["MatrixEntry"][0]["Source"] == "Voltage1"
        assert matrix.props["MatrixEntry"]["MatrixEntry"][0]["NumberOfTurns"] == "1"
        cat = m3d_app.post.available_quantities_categories(context=matrix.name)
        assert isinstance(cat, list)
        assert "C" in cat

    def test_available_report_categories(self, m3d_app):
        m3d_app.solution_type = SOLUTIONS.Maxwell3d.ElectroStatic

        rectangle1 = m3d_app.modeler.create_rectangle(0, [0.5, 1.5, 0], [2.5, 5], name="Sheet1")

        m3d_app.assign_voltage(rectangle1.faces[0], amplitude=1, name="Voltage1")

        setup = m3d_app.create_setup(MaximumPasses=2)
        m3d_app.analyze(setup=setup.name)

        matrix = m3d_app.assign_matrix(assignment="Voltage1")
        assert matrix.props["MatrixEntry"]["MatrixEntry"][0]["Source"] == "Voltage1"
        assert matrix.props["MatrixEntry"]["MatrixEntry"][0]["NumberOfTurns"] == "1"
        cat = m3d_app.post.available_quantities_categories(context=matrix.name)
        assert isinstance(cat, list)
        assert "C" in cat
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

    def test_reduced_matrix(self, m3d_app):
        m3d_app.solution_type = SOLUTIONS.Maxwell3d.EddyCurrent

        m3d_app.modeler.create_box([0, 1.5, 0], [1, 2.5, 5], name="Coil_1", material="aluminum")
        m3d_app.modeler.create_box([8.5, 1.5, 0], [1, 2.5, 5], name="Coil_2", material="aluminum")
        m3d_app.modeler.create_box([16, 1.5, 0], [1, 2.5, 5], name="Coil_3", material="aluminum")
        m3d_app.modeler.create_box([32, 1.5, 0], [1, 2.5, 5], name="Coil_4", material="aluminum")

        rectangle1 = m3d_app.modeler.create_rectangle(0, [0.5, 1.5, 0], [2.5, 5], name="Sheet1")
        rectangle2 = m3d_app.modeler.create_rectangle(0, [9, 1.5, 0], [2.5, 5], name="Sheet2")
        rectangle3 = m3d_app.modeler.create_rectangle(0, [16.5, 1.5, 0], [2.5, 5], name="Sheet3")

        m3d_app.assign_current(rectangle1.faces[0], amplitude=1, name="Cur1")
        m3d_app.assign_current(rectangle2.faces[0], amplitude=1, name="Cur2")
        m3d_app.assign_current(rectangle3.faces[0], amplitude=1, name="Cur3")

        matrix = m3d_app.assign_matrix(assignment=["Cur1", "Cur2", "Cur3"], matrix_name="Matrix1")
        assert not matrix.reduced_matrices
        m3d_app.solution_type = SOLUTIONS.Maxwell3d.Magnetostatic
        out = matrix.join_series(sources=["Cur1", "Cur2"], matrix_name="ReducedMatrix3")
        assert not out[0]
        assert not out[1]
        m3d_app.solution_type = SOLUTIONS.Maxwell3d.EddyCurrent
        out = matrix.join_series(sources=["Cur1", "Cur2"], matrix_name="ReducedMatrix1")
        assert matrix.reduced_matrices
        assert matrix.reduced_matrices[0].name == "ReducedMatrix1"
        assert matrix.reduced_matrices[0].parent_matrix == "Matrix1"
        assert out[1] in matrix.reduced_matrices[0].sources.keys()
        out = matrix.join_parallel(["Cur1", "Cur3"], matrix_name="ReducedMatrix2")
        assert matrix.reduced_matrices[1].name == "ReducedMatrix2"
        assert matrix.reduced_matrices[1].parent_matrix == "Matrix1"
        assert out[1] in matrix.reduced_matrices[1].sources.keys()
        out = matrix.join_parallel(["Cur5"])
        assert not out[0]

    # def test_32b_reduced_matrix(self):
    #     m3d_app.set_active_design("Matrix2")
    #     parent_matrix = [m for m in m3d_app.boundaries if m.type == "Matrix"][0]
    #     assert parent_matrix.reduced_matrices
    #     reduced_matrix_1 = parent_matrix.reduced_matrices[0]
    #     assert reduced_matrix_1.name == "ReducedMatrix1"
    #     assert reduced_matrix_1.parent_matrix == parent_matrix.name
    #     source_name = list(reduced_matrix_1.sources.keys())[0]
    #     assert reduced_matrix_1.update(old_source=source_name, source_type="series", new_source="new_series")
    #     assert list(reduced_matrix_1.sources.keys())[0] == "new_series"
    #     assert reduced_matrix_1.sources["new_series"] == "Cur1, Cur2"
    #     assert reduced_matrix_1.update(old_source="new_series", source_type="series", new_excitations="Cur2, Cur3")
    #     assert list(reduced_matrix_1.sources.keys())[0] == "new_series"
    #     assert reduced_matrix_1.sources["new_series"] == "Cur2, Cur3"
    #     assert not reduced_matrix_1.update(old_source="invalid", source_type="series", new_excitations="Cur2, Cur3")
    #     assert not reduced_matrix_1.update(old_source="new_series",
    #     source_type="invalid", new_excitations="Cur2, Cur3")
    #     assert not reduced_matrix_1.delete(source="invalid")
    #     assert reduced_matrix_1.delete(source="new_series")
    #     assert len(parent_matrix.reduced_matrices) == 1
    #
    # def test_32c_export_rl_matrix(self):
    #     m3d_app.set_active_design("Matrix2")
    #     L = m3d_app.assign_matrix(assignment=["Cur1", "Cur2", "Cur3"], matrix_name="matrix_export_test")
    #     L.join_series(["Cur1", "Cur2"], matrix_name="reduced_matrix_export_test")
    #     setup_name = "setupTestMatrixRL"
    #     setup = m3d_app.create_setup(name=setup_name)
    #     setup.props["MaximumPasses"] = 2
    #     export_path_1 = os.path.join(self.local_scratch.path, "export_rl_matrix_Test1.txt")
    #     assert not m3d_app.export_rl_matrix("matrix_export_test", export_path_1)
    #     assert not m3d_app.export_rl_matrix("matrix_export_test", export_path_1, False, 10, 3, True)
    #     m3d_app.validate_simple()
    #     m3d_app.analyze_setup(setup_name, cores=1)
    #     assert m3d_app.export_rl_matrix("matrix_export_test", export_path_1)
    #     assert not m3d_app.export_rl_matrix("abcabc", export_path_1)
    #     assert os.path.exists(export_path_1)
    #     export_path_2 = os.path.join(self.local_scratch.path, "export_rl_matrix_Test2.txt")
    #     assert m3d_app.export_rl_matrix("matrix_export_test", export_path_2, False, 10, 3, True)
    #     assert os.path.exists(export_path_2)
    #
    # def test_32d_post_processing(self):
    #     expressions = m3d_app.post.available_report_quantities(
    #         report_category="EddyCurrent", display_type="Data Table", context={"Matrix1": "ReducedMatrix1"}
    #     )
    #     assert isinstance(expressions, list)
    #     categories = m3d_app.post.available_quantities_categories(
    #         report_category="EddyCurrent", display_type="Data Table", context={"Matrix1": "ReducedMatrix1"}
    #     )
    #     assert isinstance(categories, list)
    #     assert "R" in categories
    #     assert "L" in categories
    #     categories = m3d_app.post.available_quantities_categories(
    #         report_category="EddyCurrent", display_type="Data Table", context="Matrix1"
    #     )
    #     assert isinstance(categories, list)
    #     assert "R" in categories
    #     assert "L" in categories
    #     assert "Z" in categories
    #     categories = m3d_app.post.available_quantities_categories(
    #         report_category="EddyCurrent", display_type="Data Table"
    #     )
    #     assert isinstance(categories, list)
    #     assert "R" in categories
    #     assert "L" in categories
    #     assert "Z" in categories
    #     report = m3d_app.post.create_report(
    #         expressions=expressions,
    #         context={"Matrix1": "ReducedMatrix1"},
    #         plot_type="Data Table",
    #         plot_name="reduced_matrix",
    #     )
    #     assert report.expressions == expressions
    #     assert report.matrix == "Matrix1"
    #     assert report.reduced_matrix == "ReducedMatrix1"
    #     data = m3d_app.post.get_solution_data(expressions=expressions, context={"Matrix1": "ReducedMatrix1"})
    #     assert data
    #     expressions = m3d_app.post.available_report_quantities(report_category="EddyCurrent",
    #     display_type="Data Table")
    #     assert isinstance(expressions, list)
    #     expressions = m3d_app.post.available_report_quantities(
    #         report_category="EddyCurrent", display_type="Data Table", context="Matrix1"
    #     )
    #     assert isinstance(expressions, list)
    #     report = m3d_app.post.create_report(
    #         expressions=expressions,
    #         context="Matrix1",
    #         plot_type="Data Table",
    #         plot_name="reduced_matrix",
    #     )
    #     assert report.expressions == expressions
    #     assert report.matrix == "Matrix1"
    #     assert not report.reduced_matrix
    #     data = m3d_app.post.get_solution_data(expressions=expressions, context="Matrix1")
    #     assert data
    #
    #     report = m3d_app.post.create_report(
    #         expressions="Mag_H", context="line_test", primary_sweep_variable="Distance", report_category="Fields"
    #     )
    #     assert report.expressions == ["Mag_H"]
    #     assert report.polyline == "line_test"
    #     data = m3d_app.post.get_solution_data(
    #         expressions=["Mag_H"],
    #         context="line_test",
    #         report_category="Fields",
    #         primary_sweep_variable="Distance",
    #     )
    #     assert data
    #
    # def test_33_mesh_settings(self):
    #     assert m3d_app.mesh.initial_mesh_settings
    #     assert m3d_app.mesh.initial_mesh_settings.props
    #
    # def test_34_assign_voltage_drop(self):
    #     circle = m3d_app.modeler.create_circle(position=[10, 10, 0], radius=5, cs_plane="XY")
    #     m3d_app.solution_type = "Magnetostatic"
    #     assert m3d_app.assign_voltage_drop([circle.faces[0]])
    #
    # def test_35_assign_symmetry(self):
    #     m3d_app.set_active_design("Motion")
    #     outer_box = [x for x in m3d_app.modeler.object_list if x.name == "Outer_Box"]
    #     inner_box = [x for x in m3d_app.modeler.object_list if x.name == "Inner_Box"]
    #     assert m3d_app.assign_symmetry([outer_box[0].faces[0], inner_box[0].faces[0]], "Symmetry_Test_IsOdd")
    #     assert m3d_app.assign_symmetry([outer_box[0].faces[0], inner_box[0].faces[0]])
    #     assert m3d_app.assign_symmetry([outer_box[0].faces[0], inner_box[0].faces[0]], "Symmetry_Test_IsEven", False)
    #     assert m3d_app.assign_symmetry([35, 7])
    #     assert not m3d_app.assign_symmetry([])
    #     for bound in m3d_app.boundaries:
    #         if bound.name == "Symmetry_Test_IsOdd":
    #             assert bound.type == "Symmetry"
    #             assert bound.props["IsOdd"]
    #         if bound.name == "Symmetry_Test_IsEven":
    #             assert bound.type == "Symmetry"
    #             assert not bound.props["IsOdd"]
    #
    # def test_36_set_bp_curve_loss(self):
    #     bp_curve_box = m3d_app.modeler.create_box([0, 0, 0], [10, 10, 10], name="bp_curve_box")
    #     bp_curve_box.material = "magnesium"
    #     assert m3d_app.materials["magnesium"].set_bp_curve_coreloss(
    #         [[0, 0], [0.6, 1.57], [1.0, 4.44], [1.5, 20.562], [2.1, 44.23]],
    #         kdc=0.002,
    #         cut_depth=0.0009,
    #         units="w/kg",
    #         bunit="tesla",
    #         frequency=50,
    #         thickness="0.5mm",
    #     )
    #
    # def test_37_assign_insulating(self):
    #     insulated_box = m3d_app.modeler.create_box([50, 0, 50], [294, 294, 19], name="insulated_box")
    #     insulating_assignment = m3d_app.assign_insulating(insulated_box.name, "InsulatingExample")
    #     assert insulating_assignment.name == "InsulatingExample"
    #     insulating_assignment.name = "InsulatingExampleModified"
    #     assert insulating_assignment.update()
    #     insulating_assignment_face = m3d_app.assign_insulating(insulated_box.faces[0], "InsulatingExample2")
    #     assert insulating_assignment_face.name == "InsulatingExample2"
    #     insulating_assignment_comb = m3d_app.assign_insulating(
    #         [insulated_box.name, insulated_box.faces[0]], "InsulatingExample3"
    #     )
    #     assert insulating_assignment_comb.name == "InsulatingExample3"
    #
    # def test_38_assign_current_density(self):
    #     design_to_activate = [x for x in m3d_app.design_list if x.startswith("Maxwell")]
    #     m3d_app.set_active_design(design_to_activate[0])
    #     current_box = m3d_app.modeler.create_box([50, 0, 50], [294, 294, 19], name="current_box")
    #     current_box2 = m3d_app.modeler.create_box([50, 0, 50], [294, 294, 19], name="current_box2")
    #     assert m3d_app.assign_current_density("current_box", "CurrentDensity_1")
    #     assert m3d_app.assign_current_density(
    #         "current_box", "CurrentDensity_2", "40deg", current_density_x="3", current_density_y="4"
    #     )
    #     assert m3d_app.assign_current_density(["current_box", "current_box2"], "CurrentDensity_3")
    #     assert not m3d_app.assign_current_density("current_box", "CurrentDensity_4", coordinate_system_type="test")
    #     assert not m3d_app.assign_current_density("current_box", "CurrentDensity_5", phase="5ang")
    #     for bound in m3d_app.boundaries:
    #         if bound.type == "CurrentDensity":
    #             if bound.name == "CurrentDensity_1":
    #                 assert bound.props["Objects"] == ["current_box"]
    #                 assert bound.props["Phase"] == "0deg"
    #                 assert bound.props["CurrentDensityX"] == "0"
    #                 assert bound.props["CurrentDensityY"] == "0"
    #                 assert bound.props["CurrentDensityZ"] == "0"
    #                 assert bound.props["CoordinateSystem Name"] == "Global"
    #                 assert bound.props["CoordinateSystem Type"] == "Cartesian"
    #             if bound.name == "CurrentDensity_2":
    #                 assert bound.props["Objects"] == ["current_box"]
    #                 assert bound.props["Phase"] == "40deg"
    #                 assert bound.props["CurrentDensityX"] == "3"
    #                 assert bound.props["CurrentDensityY"] == "4"
    #                 assert bound.props["CurrentDensityZ"] == "0"
    #                 assert bound.props["CoordinateSystem Name"] == "Global"
    #                 assert bound.props["CoordinateSystem Type"] == "Cartesian"
    #             if bound.name == "CurrentDensity_3":
    #                 assert bound.props["Objects"] == ["current_box", "current_box2"]
    #                 assert bound.props["Phase"] == "0deg"
    #                 assert bound.props["CurrentDensityX"] == "0"
    #                 assert bound.props["CurrentDensityY"] == "0"
    #                 assert bound.props["CurrentDensityZ"] == "0"
    #                 assert bound.props["CoordinateSystem Name"] == "Global"
    #                 assert bound.props["CoordinateSystem Name"] == "Cartesian"
    #     m3d_app.set_active_design("Motion")
    #     assert not m3d_app.assign_current_density("Circle_inner", "CurrentDensity_1")
    #
    # def test_39_assign_current_density_terminal(self):
    #     design_to_activate = [x for x in m3d_app.design_list if x.startswith("Maxwell")]
    #     m3d_app.set_active_design(design_to_activate[0])
    #     assert m3d_app.assign_current_density_terminal("Coil_Section1", "CurrentDensityTerminal_1")
    #     assert not m3d_app.assign_current_density_terminal("Coil_Section1", "CurrentDensityTerminal_1")
    #     m3d_app.set_active_design("Matrix2")
    #     assert m3d_app.assign_current_density_terminal(["Sheet1", "Sheet2"], "CurrentDensityTerminalGroup_1")
    #     assert not m3d_app.assign_current_density_terminal(["Coil_1", "Coil_2"], "CurrentDensityTerminalGroup_2")
    #     m3d_app.set_active_design("Motion")
    #     assert not m3d_app.assign_current_density_terminal("Inner_Box", "CurrentDensityTerminal_1")
    #
    # def test_40_assign_impedance(self):
    #     impedance_box = m3d_app.modeler.create_box([-50, -50, -50], [294, 294, 19], name="impedance_box")
    #     impedance_faces = m3d_app.modeler.select_allfaces_fromobjects([impedance_box.name])
    #     assert m3d_app.assign_impedance(impedance_faces, "copper")
    #     assert m3d_app.assign_impedance(impedance_box, "copper")
    #     impedance_assignment = m3d_app.assign_impedance(
    #         impedance_box.name, permeability=1.3, conductivity=42000000, impedance="ImpedanceExample"
    #     )
    #     assert impedance_assignment.name == "ImpedanceExample"
    #     impedance_assignment.name = "ImpedanceExampleModified"
    #     assert impedance_assignment.update()
    #
    #     # Add an impedance using an existing material.
    #     impedance_box_copper = m3d_app.modeler.create_box([-50, -300, -50], [294, 294, 19],
    #     name="impedance_box_copper")
    #     impedance_assignment_copper = m3d_app.assign_impedance(
    #         impedance_box_copper.name, material_name="copper", impedance="ImpedanceExampleCopper"
    #     )
    #     assert impedance_assignment_copper.name == "ImpedanceExampleCopper"
    #     impedance_assignment_copper.name = "ImpedanceExampleCopperModified"
    #     assert impedance_assignment_copper.update()
    #
    #     # Add an impedance using an existing material with non-linear permeability and
    #     # modifying its conductivity.
    #     impedance_box_copper_non_liear = m3d_app.modeler.create_box(
    #         [-50, -600, -50], [294, 294, 19], name="impedance_box_copper_non_liear"
    #     )
    #     impedance_assignment_copper = m3d_app.assign_impedance(
    #         impedance_box_copper.name,
    #         material_name="copper",
    #         conductivity=47000000,
    #         non_linear_permeability=True,
    #         impedance="ImpedanceExampleCopperNonLinear",
    #     )
    #     assert impedance_assignment_copper.name == "ImpedanceExampleCopperNonLinear"
    #     impedance_assignment_copper.name = "ImpedanceExampleCopperNonLinearModified"
    #     assert impedance_assignment_copper.update()
    #
    # @pytest.mark.skipif(desktop_version < "2023.1", reason="Method implemented in AEDT 2023R1")
    # def test_41_conduction_paths(self):
    #     m3d_app.insert_design("conduction")
    #     box1 = m3d_app.modeler.create_box([0, 0, 0], [10, 10, 1], material="copper")
    #     box1 = m3d_app.modeler.create_box([0, 0, 0], [-10, 10, 1], material="copper")
    #     box3 = m3d_app.modeler.create_box([-50, -50, -50], [1, 1, 1], material="copper")
    #     assert len(m3d_app.get_conduction_paths()) == 2
    #
    # def test_43_eddy_effect_transient(self, m3dtransient):
    #     assert m3dtransient.eddy_effects_on(["Rotor"], enable_eddy_effects=True)
    #
    # def test_44_assign_master_slave(self, m3dtransient):
    #     faces = [
    #         x.faces for x in m3dtransient.modeler.object_list if x.name == "PeriodicBC1" or x.name == "PeriodicBC2"
    #     ]
    #     assert m3dtransient.assign_master_slave(
    #         master_entity=faces[0],
    #         slave_entity=faces[1],
    #         u_vector_origin_coordinates_master=["0mm", "0mm", "0mm"],
    #         u_vector_pos_coordinates_master=["0mm", "100mm", "0mm"],
    #         u_vector_origin_coordinates_slave=["0mm", "0mm", "0mm"],
    #         u_vector_pos_coordinates_slave=["0mm", "-100mm", "0mm"],
    #     )
    #     assert m3dtransient.assign_master_slave(
    #         master_entity=faces[0],
    #         slave_entity=faces[1],
    #         u_vector_origin_coordinates_master=["0mm", "0mm", "0mm"],
    #         u_vector_pos_coordinates_master=["0mm", "100mm", "0mm"],
    #         u_vector_origin_coordinates_slave=["0mm", "0mm", "0mm"],
    #         u_vector_pos_coordinates_slave=["0mm", "-100mm", "0mm"],
    #         bound_name="test",
    #     )
    #     assert m3dtransient.assign_master_slave(
    #         master_entity=faces[0],
    #         slave_entity=faces[1],
    #         u_vector_origin_coordinates_master="0mm",
    #         u_vector_pos_coordinates_master=["0mm", "100mm", "0mm"],
    #         u_vector_origin_coordinates_slave=["0mm", "0mm", "0mm"],
    #         u_vector_pos_coordinates_slave=["0mm", "-100mm", "0mm"],
    #     ) == (False, False)
    #     assert m3dtransient.assign_master_slave(
    #         master_entity=faces[0],
    #         slave_entity=faces[1],
    #         u_vector_origin_coordinates_master=["0mm", "0mm", "0mm"],
    #         u_vector_pos_coordinates_master=[0, "100mm", "0mm"],
    #         u_vector_origin_coordinates_slave=["0mm", "0mm", "0mm"],
    #         u_vector_pos_coordinates_slave=["0mm", "-100mm", "0mm"],
    #     ) == (False, False)
    #     assert m3dtransient.assign_master_slave(
    #         master_entity=faces[0],
    #         slave_entity=faces[1],
    #         u_vector_origin_coordinates_master=["0mm", "0mm", "0mm"],
    #         u_vector_pos_coordinates_master=[0, "100mm", "0mm"],
    #         u_vector_origin_coordinates_slave=["0mm", "0mm"],
    #         u_vector_pos_coordinates_slave=["0mm", "-100mm", "0mm"],
    #     ) == (False, False)
    #
    # def test_45_add_mesh_link(self, m3dtransient):
    #     m3dtransient.duplicate_design(m3dtransient.design_name)
    #     m3dtransient.set_active_design(m3dtransient.design_list[1])
    #     assert m3dtransient.setups[0].add_mesh_link(design=m3dtransient.design_list[0])
    #     meshlink_props = m3dtransient.setups[0].props["MeshLink"]
    #     assert meshlink_props["Project"] == "This Project*"
    #     assert meshlink_props["PathRelativeTo"] == "TargetProject"
    #     assert meshlink_props["Design"] == m3dtransient.design_list[0]
    #     assert meshlink_props["Soln"] == "Setup1 : LastAdaptive"
    #     assert not m3dtransient.setups[0].add_mesh_link(design="")
    #     assert m3dtransient.setups[0].add_mesh_link(
    #         design=m3dtransient.design_list[0], solution="Setup1 : LastAdaptive"
    #     )
    #     assert not m3dtransient.setups[0].add_mesh_link(
    #         design=m3dtransient.design_list[0], solution="Setup_Test : LastAdaptive"
    #     )
    #     assert m3dtransient.setups[0].add_mesh_link(
    #         design=m3dtransient.design_list[0], parameters=m3dtransient.available_variations.nominal_w_values_dict
    #     )
    #     example_project = os.path.join(TESTS_GENERAL_PATH, "example_models", test_subfolder, transient + ".aedt")
    #     example_project_copy = os.path.join(self.local_scratch.path, transient + "_copy.aedt")
    #     shutil.copyfile(example_project, example_project_copy)
    #     assert m3dtransient.setups[0].add_mesh_link(design=m3dtransient.design_list[0], project=example_project_copy)
    #
    # def test_46_set_variable(self):
    #     m3d_app.variable_manager.set_variable("var_test", expression="123")
    #     m3d_app["var_test"] = "234"
    #     assert "var_test" in m3d_app.variable_manager.design_variable_names
    #     assert m3d_app.variable_manager.design_variables["var_test"].expression == "234"
    #
    # def test_49_cylindrical_gap(self, cyl_gap):
    #     [
    #         x.delete()
    #         for x in cyl_gap.mesh.meshoperations[:]
    #         if x.type == "Cylindrical Gap Based" or x.type == "CylindricalGap"
    #     ]
    #     assert cyl_gap.mesh.assign_cylindrical_gap("Band", name="cyl_gap_test")
    #     assert not cyl_gap.mesh.assign_cylindrical_gap(["Band", "Inner_Band"])
    #     assert not cyl_gap.mesh.assign_cylindrical_gap("Band")
    #     [
    #         x.delete()
    #         for x in cyl_gap.mesh.meshoperations[:]
    #         if x.type == "Cylindrical Gap Based" or x.type == "CylindricalGap"
    #     ]
    #     assert cyl_gap.mesh.assign_cylindrical_gap("Band", name="cyl_gap_test", band_mapping_angle=1, clone_mesh=True)
    #     [
    #         x.delete()
    #         for x in cyl_gap.mesh.meshoperations[:]
    #         if x.type == "Cylindrical Gap Based" or x.type == "CylindricalGap"
    #     ]
    #     assert cyl_gap.mesh.assign_cylindrical_gap("Band", name="cyl_gap_test", clone_mesh=False)
    #     [
    #         x.delete()
    #         for x in cyl_gap.mesh.meshoperations[:]
    #         if x.type == "Cylindrical Gap Based" or x.type == "CylindricalGap"
    #     ]
    #     assert cyl_gap.mesh.assign_cylindrical_gap("Band")
    #     assert not cyl_gap.mesh.assign_cylindrical_gap(
    #         "Band", name="cyl_gap_test", band_mapping_angle=7, clone_mesh=True
    #     )
    #     assert not cyl_gap.mesh.assign_cylindrical_gap(
    #         "Band", name="cyl_gap_test", band_mapping_angle=2, clone_mesh=True, moving_side_layers=0
    #     )
    #     assert not cyl_gap.mesh.assign_cylindrical_gap(
    #         "Band", name="cyl_gap_test", band_mapping_angle=2, clone_mesh=True, static_side_layers=0
    #     )
    #
    # def test_50_objects_segmentation(self, cyl_gap):
    #     segments_number = 5
    #     object_name = "PM_I1"
    #     sheets = cyl_gap.modeler.objects_segmentation(
    #         assignment=object_name, segments=segments_number, apply_mesh_sheets=True
    #     )
    #     assert isinstance(sheets, tuple)
    #     assert isinstance(sheets[0], dict)
    #     assert isinstance(sheets[1], dict)
    #     assert isinstance(sheets[0][object_name], list)
    #     assert len(sheets[0][object_name]) == segments_number - 1
    #     segments_number = 4
    #     mesh_sheets_number = 3
    #     object_name = "PM_I1_1"
    #     magnet_id = [obj.id for obj in cyl_gap.modeler.object_list if obj.name == object_name][0]
    #     sheets = cyl_gap.modeler.objects_segmentation(
    #         magnet_id, segments=segments_number, apply_mesh_sheets=True, mesh_sheets=mesh_sheets_number
    #     )
    #     assert isinstance(sheets, tuple)
    #     assert isinstance(sheets[0][object_name], list)
    #     assert len(sheets[0][object_name]) == segments_number - 1
    #     assert isinstance(sheets[1][object_name], list)
    #     assert len(sheets[1][object_name]) == mesh_sheets_number
    #     segmentation_thickness = 1
    #     object_name = "PM_O1"
    #     magnet = [obj for obj in cyl_gap.modeler.object_list if obj.name == object_name][0]
    #     sheets = cyl_gap.modeler.objects_segmentation(
    #         magnet, segmentation_thickness=segmentation_thickness, apply_mesh_sheets=True
    #     )
    #     assert isinstance(sheets, tuple)
    #     assert isinstance(sheets[0][object_name], list)
    #     segments_number = round(magnet.top_edge_y.length / segmentation_thickness)
    #     assert len(sheets[0][object_name]) == segments_number - 1
    #     assert not cyl_gap.modeler.objects_segmentation(object_name)
    #     assert not cyl_gap.modeler.objects_segmentation(
    #         object_name, segmentation_thickness=segmentation_thickness, segments=segments_number
    #     )
    #     object_name = "PM_O1_1"
    #     segments_number = 10
    #     sheets = cyl_gap.modeler.objects_segmentation(object_name, segments=segments_number)
    #     assert isinstance(sheets, dict)
    #     assert isinstance(sheets[object_name], list)
    #     assert len(sheets[object_name]) == segments_number - 1
    #
    # @pytest.mark.skipif(config["NonGraphical"], reason="Test fails on build machine")
    # def test_51_import_dxf(self):
    #     m3d_app.insert_design("dxf")
    #     dxf_file = os.path.join(TESTS_GENERAL_PATH, "example_models", "cad", "DXF", "dxf2.dxf")
    #     dxf_layers = m3d_app.get_dxf_layers(dxf_file)
    #     assert isinstance(dxf_layers, list)
    #     assert m3d_app.import_dxf(dxf_file, dxf_layers)
    #
    # def test_52_assign_flux_tangential(self):
    #     m3d_app.insert_design("flux_tangential")
    #     box = m3d_app.modeler.create_box([50, 0, 50], [294, 294, 19], name="Box")
    #     assert not m3d_app.assign_flux_tangential(box.faces[0])
    #     m3d_app.solution_type = "TransientAPhiFormulation"
    #     assert m3d_app.assign_flux_tangential(box.faces[0], "FluxExample")
    #     assert m3d_app.assign_flux_tangential(box.faces[0].id, "FluxExample")
    #
    # @pytest.mark.skipif(not config["use_grpc"], reason="Not running in COM mode")
    # @pytest.mark.skipif(desktop_version < "2023.2", reason="Method available in beta from 2023.2")
    # def test_53_assign_layout_force(self, layout_comp):
    #     nets_layers = {
    #         "<no-net>": ["<no-layer>", "TOP", "UNNAMED_000", "UNNAMED_002"],
    #         "GND": ["BOTTOM", "Region", "UNNAMED_010", "UNNAMED_012"],
    #         "V3P3_S5": ["LYR_1", "LYR_2", "UNNAMED_006", "UNNAMED_008"],
    #     }
    #     assert layout_comp.assign_layout_force(nets_layers, "LC1_1")
    #     assert not layout_comp.assign_layout_force(nets_layers, "LC1_3")
    #     nets_layers = {"1V0": "Bottom Solder"}
    #     assert layout_comp.assign_layout_force(nets_layers, "LC1_1")
    #
    # @pytest.mark.skipif(
    #     desktop_version < "2023.2" or is_linux, reason="Method is available in beta in 2023.2 and later."
    # )
    # @pytest.mark.skipif(is_linux, reason="EDB object is not loaded.")
    # def test_54_enable_harmonic_force_layout(self, layout_comp):
    #     comp = layout_comp.modeler.user_defined_components["LC1_1"]
    #     layers = list(comp.layout_component.layers.keys())
    #     nets = list(comp.layout_component.nets.keys())
    #     layout_comp.enable_harmonic_force_on_layout_component(
    #         comp.name,
    #         {nets[0]: layers[1::2], nets[1]: layers[1::2]},
    #         force_type=2,
    #         window_function="Rectangular",
    #         use_number_of_last_cycles=True,
    #         last_cycles_number=1,
    #         calculate_force="Harmonic",
    #         start_time="10us",
    #         stop_time="20us",
    #         use_number_of_cycles_for_stop_time=True,
    #         number_of_cycles_for_stop_time=1,
    #     )
    #     layout_comp.solution_type = "Magnetostatic"
    #     assert not layout_comp.enable_harmonic_force_on_layout_component(
    #         comp.name, {nets[0]: layers[1::2], nets[1]: layers[1::2]}
    #     )
    #
    # def test_55_tangential_h_field(self, add_app):
    #     m3d = add_app(application=Maxwell3d, solution_type="EddyCurrent")
    #     box = m3d.modeler.create_box([0, 0, 0], [10, 10, 10])
    #     assert m3d.assign_tangential_h_field(box.bottom_face_x, 1, 0, 2, 0)
    #
    # def test_56_zero_tangential_h_field(self, add_app):
    #     m3d = add_app(application=Maxwell3d, solution_type="EddyCurrent")
    #     box = m3d.modeler.create_box([0, 0, 0], [10, 10, 10])
    #     assert m3d.assign_zero_tangential_h_field(box.top_face_z)
    #
    # def test_57_radiation(self):
    #     m3d_app.insert_design("Radiation")
    #     m3d_app.solution_type = SOLUTIONS.Maxwell3d.EddyCurrent
    #     rect = m3d_app.modeler.create_rectangle(0, [0, 0, 0], [5, 5], material="aluminum")
    #     rect2 = m3d_app.modeler.create_rectangle(0, [15, 20, 0], [5, 5], material="aluminum")
    #     box = m3d_app.modeler.create_box([15, 20, 0], [5, 5, 5], material="aluminum")
    #     box2 = m3d_app.modeler.create_box([150, 20, 0], [50, 5, 10], material="aluminum")
    #     bound = m3d_app.assign_radiation([rect, rect2, box, box2.faces[0]])
    #     assert bound
    #     bound2 = m3d_app.assign_radiation([rect, rect2, box, box2.faces[0]], "my_rad")
    #     assert bound2
    #     bound3 = m3d_app.assign_radiation([rect, rect2, box, box2.faces[0]], "my_rad")
    #     assert bound2.name != bound3.name
    #     m3d_app.solution_type = SOLUTIONS.Maxwell3d.Transient
    #     assert not m3d_app.assign_radiation([rect, rect2, box, box2.faces[0]])
    #
    # def test_58_solution_types_setup(self, add_app):
    #     m3d = add_app(application=Maxwell3d, design_name="test_setups")
    #     setup = m3d.create_setup(setup_type=m3d.solution_type)
    #     assert setup
    #     setup.delete()
    #     m3d.solution_type = SOLUTIONS.Maxwell3d.Transient
    #     setup = m3d.create_setup(setup_type=m3d.solution_type)
    #     assert setup
    #     setup.delete()
    #     m3d.solution_type = SOLUTIONS.Maxwell3d.EddyCurrent
    #     setup = m3d.create_setup(setup_type=m3d.solution_type)
    #     assert setup
    #     setup.delete()
    #     m3d.solution_type = SOLUTIONS.Maxwell3d.ElectroStatic
    #     setup = m3d.create_setup(setup_type=m3d.solution_type)
    #     assert setup
    #     setup.delete()
    #     m3d.solution_type = SOLUTIONS.Maxwell3d.DCConduction
    #     setup = m3d.create_setup(setup_type=m3d.solution_type)
    #     assert setup
    #     setup.delete()
    #     m3d.solution_type = SOLUTIONS.Maxwell3d.ACConduction
    #     setup = m3d.create_setup(setup_type=m3d.solution_type)
    #     assert setup
    #     setup.delete()
    #     m3d.solution_type = SOLUTIONS.Maxwell3d.ElectroDCConduction
    #     setup = m3d.create_setup(setup_type=m3d.solution_type)
    #     assert setup
    #     setup.delete()
    #     m3d.solution_type = SOLUTIONS.Maxwell3d.ElectricTransient
    #     setup = m3d.create_setup(setup_type=m3d.solution_type)
    #     assert setup
    #     setup.delete()
    #     m3d.solution_type = SOLUTIONS.Maxwell3d.TransientAPhiFormulation
    #     setup = m3d.create_setup(setup_type=m3d.solution_type)
    #     assert setup
    #     setup.delete()
    #
    # def test_59_assign_floating(self):
    #     m3d_app.insert_design("Floating")
    #     m3d_app.solution_type = SOLUTIONS.Maxwell3d.ElectroStatic
    #     box = m3d_app.modeler.create_box([0, 0, 0], [10, 10, 10], name="Box1")
    #     floating = m3d_app.assign_floating(assignment=box, charge_value=3)
    #     assert floating
    #     assert floating.props["Objects"][0] == box.name
    #     assert floating.props["Value"] == "3"
    #     floating1 = m3d_app.assign_floating(assignment=[box.faces[0], box.faces[1]], charge_value=3)
    #     assert floating1
    #     m3d_app.solution_type = SOLUTIONS.Maxwell3d.Magnetostatic
    #     floating = m3d_app.assign_floating(assignment=box, charge_value=3)
    #     assert not floating
    #
    # def test_60_resistive_sheet(self):
    #     m3d_app.insert_design("ResistiveSheet")
    #     m3d_app.solution_type = SOLUTIONS.Maxwell3d.EddyCurrent
    #     m3d_app.modeler.create_box(origin=[0, 0, 0], sizes=[0.4, -1, 0.8], name="my_box", material="copper")
    #     my_rectangle = m3d_app.modeler.create_rectangle(
    #         orientation=1, origin=[0, 0, 0.8], sizes=[-1, 0.4], name="my_rect"
    #     )
    #
    #     # From 2025.1, this boundary can only be assigned to Sheets that touch conductor Solids.
    #     bound = m3d_app.assign_resistive_sheet(assignment=my_rectangle.faces[0], resistance="3ohm")
    #     assert bound
    #     assert bound.props["Faces"][0] == my_rectangle.faces[0].id
    #     assert bound.props["Resistance"] == "3ohm"
    #     m3d_app.solution_type = SOLUTIONS.Maxwell3d.Magnetostatic
    #     bound = m3d_app.assign_resistive_sheet(assignment=my_rectangle.name, non_linear=True)
    #     assert bound.props["Nonlinear"]
    #     assert bound.props["Objects"][0] == my_rectangle.name
    #     m3d_app.solution_type = SOLUTIONS.Maxwell3d.ACConduction
    #     assert not m3d_app.assign_resistive_sheet(assignment=my_rectangle, resistance="3ohm")
