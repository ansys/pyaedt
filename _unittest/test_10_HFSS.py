import os
try:
    import pytest
except ImportError:
    import _unittest_ironpython.conf_unittest as pytest
# Setup paths for module imports
from _unittest.conftest import scratch_path
import gc
# Import required modules
from pyaedt import Hfss
from pyaedt.generic.filesystem import Scratch

test_project_name = "coax_HFSS"


class TestClass:
    def setup_class(self):
        # set a scratch directory and the environment / test data
        with Scratch(scratch_path) as self.local_scratch:
            self.aedtapp = Hfss(AlwaysNew=True)

    def teardown_class(self):
        assert self.aedtapp.close_project(self.aedtapp.project_name)
        self.local_scratch.remove()
        gc.collect()

    def test_01_save(self):
        project_name = "Test_Exercse201119"
        test_project = os.path.join(self.local_scratch.path, project_name + ".aedt")
        self.aedtapp.save_project(test_project)
        assert os.path.exists(test_project)

    def test_01A_check_setup(self):
        assert self.aedtapp.analysis_setup is None

    def test_02_create_primitive(self):
        udp = self.aedtapp.modeler.Position(0, 0, 0)
        coax_dimension = 200
        o1 = self.aedtapp.modeler.primitives.create_cylinder(self.aedtapp.CoordinateSystemAxis.XAxis, udp, 3, coax_dimension,
                                                         0, "inner")
        assert isinstance(o1.id, int)
        o2 = self.aedtapp.modeler.primitives.create_cylinder(self.aedtapp.CoordinateSystemAxis.XAxis, udp, 10, coax_dimension,
                                                         0, "outer")
        assert isinstance(o2.id, int)
        assert self.aedtapp.modeler.subtract(o2, o1, True)

    def test_03_2_assign_material(self):
        udp = self.aedtapp.modeler.Position(0, 0, 0)
        coax_dimension = 200
        cyl_1 = self.aedtapp.modeler.primitives.create_cylinder(
            self.aedtapp.CoordinateSystemPlane.XYPlane, udp, 10, coax_dimension, 0, "die")
        self.aedtapp.modeler.subtract(cyl_1, "inner", True)
        self.aedtapp.modeler.primitives["inner"].material_name = "Copper"
        cyl_1.material_name = "teflon_based"
        assert self.aedtapp.modeler.primitives["inner"].material_name == "copper"
        assert cyl_1.material_name == "teflon_based"

    @pytest.mark.parametrize(
        "object_name, kwargs",
        [
            ("inner", {"mat": "copper"}),
            ("outer", {"mat": "aluminum", "usethickness": True, "thickness": "0.5mm", "istwoside": True,
                        "issheelElement": True, "usehuray": True, "radius": "0.75um", "ratio": "3"}),
            ("die", {})
        ]
    )
    def test_04_assign_coating(self, object_name, kwargs):
        id = self.aedtapp.modeler.primitives.get_obj_id(object_name)
        coat = self.aedtapp.assigncoating([id], **kwargs)
        material = coat.props.get("Material", "")
        assert material == kwargs.get("mat", "")

    def test_05_create_wave_port_from_sheets(self):
        udp = self.aedtapp.modeler.Position(0, 0, 0)
        o5 = self.aedtapp.modeler.primitives.create_circle(
            self.aedtapp.CoordinateSystemPlane.YZPlane,udp,10, name="sheet1")
        self.aedtapp.solution_type ="DrivenTerminal"
        ports = self.aedtapp.create_wave_port_from_sheet(
            o5, 5, self.aedtapp.AxisDir.XNeg, 40, 2, "sheet1_Port", True)
        assert ports[0].name == "sheet1_Port"
        assert ports[0].name in [i.name for i in self.aedtapp.boundaries]
        self.aedtapp.solution_type ="DrivenModal"
        udp = self.aedtapp.modeler.Position(200, 0, 0)
        o6 = self.aedtapp.modeler.primitives.create_circle(
            self.aedtapp.CoordinateSystemPlane.YZPlane,udp,10, name="sheet2")
        ports = self.aedtapp.create_wave_port_from_sheet(
            o6, 5, self.aedtapp.AxisDir.XPos, 40, 2, "sheet2_Port", True)
        assert ports[0].name == "sheet2_Port"
        assert ports[0].name in [i.name for i in self.aedtapp.boundaries]

        id6 = self.aedtapp.modeler.primitives.create_box(
            [20,20,20], [10,10,2],matname="Copper", name="My_Box")
        id7 = self.aedtapp.modeler.primitives.create_box([20,25,30], [10,2,2],matname="Copper")
        rect = self.aedtapp.modeler.primitives.create_rectangle(
            self.aedtapp.CoordinateSystemPlane.YZPlane,[20,25,20],[2,10])
        ports = self.aedtapp.create_wave_port_from_sheet(
            rect, 5, self.aedtapp.AxisDir.ZNeg, 40, 2, "sheet3_Port", True)
        assert ports[0].name in [i.name for i in self.aedtapp.boundaries]
        pass

    def test_06a_create_sweep(self):
        setup = self.aedtapp.create_setup("MySetup")
        setup.props["Frequency"] = "1GHz"
        setup.props["BasisOrder"] = 2
        setup.props["MaximumPasses"] = 1
        assert setup.update()
        assert self.aedtapp.create_frequency_sweep("MySetup", "GHz", 0.8, 1.2)
        assert self.aedtapp.create_frequency_sweep("MySetup", "GHz", 0.8, 1.2)
        assert self.aedtapp.create_frequency_sweep(setupname="MySetup", sweepname="MySweep", unit="MHz",
                                                   freqstart=1.1e3, freqstop=1200.1, num_of_freq_points=1234,
                                                   sweeptype="Interpolating")
        assert self.aedtapp.create_frequency_sweep(setupname="MySetup", sweepname="MySweepFast", unit="MHz",
                                                   freqstart=1.1e3, freqstop=1200.1, num_of_freq_points=1234,
                                                   sweeptype="Fast")
        assert self.aedtapp.create_single_point_sweep("MySetup")

    def test_06B_setup_exists(self):
        assert self.aedtapp.analysis_setup is not None
        assert self.aedtapp.nominal_sweep is not None

    def test_06b_create_linear_count_sweep(self):
        num_points = 1752
        freq_start = 1.1e3
        freq_stop = 1200.1
        units = "MHz"
        sweep = self.aedtapp.create_linear_count_sweep(setupname="MySetup", sweepname=None,
                                                      unit=units, freqstart=freq_start, freqstop=freq_stop,
                                                      num_of_freq_points=num_points)
        assert sweep.props["RangeCount"] == num_points
        assert sweep.props["RangeStart"] == str(freq_start)+units
        assert sweep.props["RangeEnd"] == str(freq_stop)+units

    def test_06c_create_linear_step_sweep(self):
        step_size = 153.8
        freq_start = 1.1e3
        freq_stop = 1200.1
        units = "MHz"
        sweep= self.aedtapp.create_linear_step_sweep(setupname="MySetup", sweepname=None,
                                                     unit=units, freqstart=freq_start, freqstop=freq_stop,
                                                     step_size=step_size)
        assert sweep.props["RangeStep"] == str(step_size)+units
        assert sweep.props["RangeStart"] == str(freq_start)+units
        assert sweep.props["RangeEnd"] == str(freq_stop)+units

    def test_06z_validate_setup(self):
        list, ok = self.aedtapp.validate_full_design(ports=5)
        assert ok

    def test_07_set_power(self):
        assert self.aedtapp.edit_source("sheet1_Port" + ":1", "10W")

    def test_08_create_circuit_port_from_edges(self):
        plane = self.aedtapp.CoordinateSystemPlane.XYPlane
        rect_1 = self.aedtapp.modeler.primitives.create_rectangle(
            plane, [10, 10, 10], [10, 10], name="rect1_for_port")
        edges1 = self.aedtapp.modeler.primitives.get_object_edges(rect_1.id)
        e1 = edges1[0]
        rect_2 = self.aedtapp.modeler.primitives.create_rectangle(
            plane, [30, 10, 10], [10, 10], name="rect2_for_port")
        edges2 = self.aedtapp.modeler.primitives.get_object_edges(rect_2.id)
        e2 = edges2[0]

        self.aedtapp.solution_type = "DrivenModal"
        assert self.aedtapp.create_circuit_port_from_edges(e1, e2, port_name="port10", port_impedance=50.1,
                                                           renormalize=False, renorm_impedance="50") == "port10"
        assert self.aedtapp.create_circuit_port_from_edges(e1, e2, port_name="port11", port_impedance="50+1i*55",
                                                           renormalize=True, renorm_impedance=15.4) == "port11"

        self.aedtapp.solution_type = "DrivenTerminal"
        assert self.aedtapp.create_circuit_port_from_edges(e1, e2, port_name="port20", port_impedance=50.1,
                                                           renormalize=False, renorm_impedance="50+1i*55")  == "port20"
        assert self.aedtapp.create_circuit_port_from_edges(e1, e2, port_name="port21", port_impedance="50.1",
                                                           renormalize=True) == "port21"

        self.aedtapp.solution_type = "DrivenModal"

    def test_09_create_waveport_on_objects(self):
        box1 = self.aedtapp.modeler.primitives.create_box([0,0,0], [10,10,5], "BoxWG1", "Copper")
        box2 = self.aedtapp.modeler.primitives.create_box(
            [0, 0, 10], [10, 10, 5], "BoxWG2", "copper")
        box2.material_name = "Copper"
        port = self.aedtapp.create_wave_port_between_objects("BoxWG1", "BoxWG2", self.aedtapp.AxisDir.XNeg, 50, 1, "Wave1",
                                                             False)
        assert port.name == "Wave1"
        port2 = self.aedtapp.create_wave_port_between_objects("BoxWG1", "BoxWG2", self.aedtapp.AxisDir.XPos, 25, 2,
                                                           "Wave1", True, 5)
        assert port2.name != "Wave1" and "Wave1" in port2.name

    def test_09a_create_waveport_on_true_surface_objects(self):
        cs = self.aedtapp.CoordinateSystemPlane.XYPlane
        o1 = self.aedtapp.modeler.primitives.create_cylinder(cs, [0, 0, 0], radius=5, height=100,
                                                             numSides=0, name="inner", matname="Copper")
        o3 = self.aedtapp.modeler.primitives.create_cylinder(cs, [0, 0, 0], radius=10, height=100,
                                                            numSides=0, name="outer", matname="Copper")

        port1 = self.aedtapp.create_wave_port_between_objects(
            o1.name, o3.name, axisdir=0, add_pec_cap=True, portname="P1")
        assert port1.name.startswith("P1")

    def test_10_create_lumped_on_objects(self):
        box1 = self.aedtapp.modeler.primitives.create_box([0, 0, 50], [10, 10, 5], "BoxLumped1")
        box1.material_name = "Copper"
        box2 = self.aedtapp.modeler.primitives.create_box([0, 0, 60], [10, 10, 5], "BoxLumped2")
        box2.material_name = "Copper"
        port = self.aedtapp.create_lumped_port_between_objects("BoxLumped1", "BoxLumped2", self.aedtapp.AxisDir.XNeg, 50,
                                                            "Lump1", True, False)
        assert not self.aedtapp.create_lumped_port_between_objects("BoxLumped1111", "BoxLumped2", self.aedtapp.AxisDir.XNeg, 50,
                                                            "Lump1", True, False)
        assert self.aedtapp.create_lumped_port_between_objects(
            "BoxLumped1", "BoxLumped2", self.aedtapp.AxisDir.XPos, 50)
        assert port == "Lump1"

    def test_11_create_circuit_on_objects(self):
        box1 = self.aedtapp.modeler.primitives.create_box(
            [0, 0, 80], [10, 10, 5], "BoxCircuit1","Copper")
        box2 = self.aedtapp.modeler.primitives.create_box(
            [0, 0, 100], [10, 10, 5], "BoxCircuit2", "copper")
        box2.material_name = "Copper"
        port = self.aedtapp.create_circuit_port_between_objects("BoxCircuit1", "BoxCircuit2", self.aedtapp.AxisDir.XNeg,
                                                                50, "Circ1", True, 50, False)
        assert port == "Circ1"
        assert not self.aedtapp.create_circuit_port_between_objects("BoxCircuit44", "BoxCircuit2", self.aedtapp.AxisDir.XNeg,
                                                                50, "Circ1", True, 50, False)

    def test_12_create_perfects_on_objects(self):
        box1 = self.aedtapp.modeler.primitives.create_box([0,0,0], [10,10,5], "perfect1", "Copper")
        box2 = self.aedtapp.modeler.primitives.create_box(
            [0, 0, 10], [10, 10, 5], "perfect2", "copper")
        pe = self.aedtapp.create_perfecth_from_objects(
            "perfect1","perfect2",self.aedtapp.AxisDir.ZPos,)
        ph = self.aedtapp.create_perfecte_from_objects(
            "perfect1","perfect2",self.aedtapp.AxisDir.ZNeg)
        assert pe.name in self.aedtapp.modeler.get_boundaries_name()
        assert pe.update()
        assert ph.name in self.aedtapp.modeler.get_boundaries_name()
        assert ph.update()

    def test_13_create_impedance_on_objects(self):
        box1 = self.aedtapp.modeler.primitives.create_box([0,0,0], [10,10,5], "imp1", "Copper")
        box2 = self.aedtapp.modeler.primitives.create_box([0, 0, 10], [10, 10, 5], "imp2", "copper")
        imp = self.aedtapp.create_impedance_between_objects(
            "imp1", "imp2", self.aedtapp.AxisDir.XPos, "TL2", 50, 25)
        assert imp.name in self.aedtapp.modeler.get_boundaries_name()
        assert imp.update()

    def test_14_create_lumpedrlc_on_objects(self):
        box1 = self.aedtapp.modeler.primitives.create_box([0,0,0], [10,10,5], "rlc1", "Copper")
        box2 = self.aedtapp.modeler.primitives.create_box([0, 0, 10], [10, 10, 5], "rlc2", "copper")
        imp = self.aedtapp.create_lumped_rlc_between_objects(
            "rlc1","rlc2",self.aedtapp.AxisDir.XPos,Rvalue=50,Lvalue=1e-9)
        assert imp.name in self.aedtapp.modeler.get_boundaries_name()
        assert imp.update()

    def test_15_create_perfects_on_sheets(self):
        rect = self.aedtapp.modeler.primitives.create_rectangle(self.aedtapp.CoordinateSystemPlane.XYPlane, [0, 0, 0],
                                                                [10, 2], name="RectBound", matname="Copper")
        pe = self.aedtapp.assign_perfecte_to_sheets(rect.name)
        assert pe.name in self.aedtapp.modeler.get_boundaries_name()
        ph = self.aedtapp.assign_perfecth_to_sheets(rect.name)
        assert ph.name in self.aedtapp.modeler.get_boundaries_name()

    def test_16_create_impedance_on_sheets(self):
        rect = self.aedtapp.modeler.primitives.create_rectangle(self.aedtapp.CoordinateSystemPlane.XYPlane, [0, 0, 0],
                                                                [10, 2], name="ImpBound", matname="Copper")
        imp = self.aedtapp.assign_impedance_to_sheet("imp1", "TL2", 50, 25)
        assert imp.name in self.aedtapp.modeler.get_boundaries_name()
        assert imp.update()

    def test_17_create_lumpedrlc_on_sheets(self):
        rect = self.aedtapp.modeler.primitives.create_rectangle(self.aedtapp.CoordinateSystemPlane.XYPlane, [0, 0, 0],
                                                                [10, 2], name="rlcBound", matname="Copper")
        imp = self.aedtapp.assign_lumped_rlc_to_sheet(
            rect.name, self.aedtapp.AxisDir.XPos,Rvalue=50,Lvalue=1e-9)
        names = self.aedtapp.modeler.get_boundaries_name()
        assert imp.name in self.aedtapp.modeler.get_boundaries_name()

    def test_17B_update_assignment(self):
        bound = self.aedtapp.assign_perfecth_to_sheets(
            self.aedtapp.modeler.primitives["My_Box"].faces[0].id)
        assert bound
        bound.props["Faces"].append(self.aedtapp.modeler.primitives["My_Box"].faces[1])
        assert bound.update_assignment()

    def test_18_create_sources_on_objects(self):
        box1 = self.aedtapp.modeler.primitives.create_box([30,0,0], [40,10,5], "BoxVolt1", "Copper")
        box2 = self.aedtapp.modeler.primitives.create_box(
            [30, 0, 10], [40, 10, 5], "BoxVolt2", "Copper")
        port = self.aedtapp.create_voltage_source_from_objects(
            box1.name, "BoxVolt2", self.aedtapp.AxisDir.XNeg, "Volt1")
        assert port in self.aedtapp.modeler.get_excitations_name()
        port = self.aedtapp.create_current_source_from_objects(
            "BoxVolt1", "BoxVolt2", self.aedtapp.AxisDir.XPos, "Curr1")
        assert port in self.aedtapp.modeler.get_excitations_name()

    def test_19_create_lumped_on_sheet(self):
        rect = self.aedtapp.modeler.primitives.create_rectangle(self.aedtapp.CoordinateSystemPlane.XYPlane, [0, 0, 0],
                                                                [10, 2], name="lump_port", matname="Copper")
        port = self.aedtapp.create_lumped_port_to_sheet(rect.name, self.aedtapp.AxisDir.XNeg, 50,
                                                            "Lump_sheet", True, False)
        assert port+":1" in self.aedtapp.modeler.get_excitations_name()

    def test_20_create_voltage_on_sheet(self):
        rect = self.aedtapp.modeler.primitives.create_rectangle(self.aedtapp.CoordinateSystemPlane.XYPlane, [0, 0, 0],
                                                                [10, 2], name="lump_volt", matname="Copper")
        port = self.aedtapp.assign_voltage_source_to_sheet(
            rect.name, self.aedtapp.AxisDir.XNeg,  "LumpVolt1")
        assert port in self.aedtapp.modeler.get_excitations_name()
        assert self.aedtapp.get_property_value(
            "BoundarySetup:LumpVolt1", "VoltageMag", "Excitation") == "1V"

    def test_21_create_open_region(self):
        assert self.aedtapp.create_open_region("1GHz")
        assert self.aedtapp.create_open_region("1GHz","FEBI")
        assert self.aedtapp.create_open_region("1GHz","PML",True, "-z")

    def test_22_create_length_mesh(self):
        mesh = self.aedtapp.mesh.assign_length_mesh(["BoxCircuit1"])
        assert mesh
        mesh.props["NumMaxElem"] = "10000"
        assert mesh.update()

    def test_23_create_skin_depth(self):
        mesh = self.aedtapp.mesh.assign_skin_depth(["BoxCircuit2"], "1mm")
        assert mesh
        mesh.props["SkinDepth"] = "3mm"
        assert mesh.update()

    def test_24_create_curvilinear(self):
        mesh = self.aedtapp.mesh.assign_curvilinear_elements(["BoxCircuit2"])
        assert mesh
        mesh.props["Apply"] = False
        assert mesh.update()
        assert mesh.delete()
        pass

    def test_25_create_parametrics(self):
        self.aedtapp["w1"] = "10mm"
        self.aedtapp["w2"] = "2mm"
        setup1 = self.aedtapp.opti_parametric.add_parametric_setup("w1", "LIN 0.1mm 20mm 0.2mm")
        assert setup1
        assert setup1.add_variation("w2", "LINC 0.1mm 10mm 11")
        assert setup1.add_calculation(calculation="dB(S(1,1))",
                                      calculation_value="2.5GHz", reporttype="Modal Solution Data")

    def test_26_create_optimization(self):
        setup2 = self.aedtapp.opti_optimization.add_optimization('db(S(1,1))', '2.5GHz')
        assert setup2

        assert setup2.add_goal(calculation="dB(S(1,1))", calculation_value="2.6GHz")
        assert setup2.add_goal(calculation="dB(S(1,1))", calculation_value="2.6GHz", calculation_type="rd",
                        calculation_stop="5GHz")

    def test_27_create_doe(self):
        setup2 = self.aedtapp.opti_doe.add_doe('db(S(1,1))', '2.5GHz')
        assert setup2
        assert setup2.add_goal(calculation="dB(S(1,1))", calculation_value="2.6GHz")
        assert setup2.add_calculation(calculation="dB(S(1,1))", calculation_value="2.5GHz")

    def test_28_create_dx(self):
        setup2 = self.aedtapp.opti_designxplorer.add_dx_setup(["w1","w2"], ["1mm", "2mm"])
        assert setup2
        assert setup2.add_goal(calculation="dB(S(1,1))", calculation_value="2.6GHz")

    def test_29_create_sensitivity(self):
        setup2 = self.aedtapp.opti_sensitivity.add_sensitivity('db(S(1,1))', '2.5GHz')
        assert setup2
        assert setup2.add_calculation(calculation="dB(S(1,1))", calculation_value="2.6GHz")

    def test_29_create_statistical(self):
        setup2 = self.aedtapp.opti_statistical.add_statistical('db(S(1,1))', '2.5GHz')
        assert setup2
        assert setup2.add_calculation(calculation="dB(S(1,1))", calculation_value="2.6GHz")

    def test_30_assign_initial_mesh(self):
        assert self.aedtapp.mesh.assign_initial_mesh_from_slider(6)

    def test_31_create_microstrip_port(self):
        ms = self.aedtapp.modeler.primitives.create_box(
            [4,5,0],[1,100,0.2],name="MS1", matname="copper")
        sub = self.aedtapp.modeler.primitives.create_box(
            [0,5,-2],[20,100,2],name="SUB1", matname="FR4_epoxy")
        gnd = self.aedtapp.modeler.primitives.create_box(
            [0,5,-2.2],[20,100,0.2],name="GND1", matname="FR4_epoxy")
        port = self.aedtapp.create_wave_port_microstrip_between_objects(
            gnd.name, ms.name,   portname="MS1", axisdir=1)

        assert port.name == "MS1"
        assert port.update()

    def test_32_get_property_value(self):
        assert self.aedtapp.get_property_value(
            "BoundarySetup:Coating_inner", "Inf Ground Plane", "Boundary") == "false"
        assert self.aedtapp.get_property_value(
            "AnalysisSetup:MySetup", "Solution Freq", "Setup") == "1GHz"

    def test_33_copy_solid_bodies(self):
        project_name = "HfssCopiedProject"
        design_name = "HfssCopiedBodies"
        new_design = Hfss(projectname=project_name, designname=design_name)
        num_orig_bodies = len(self.aedtapp.modeler.primitives.solid_names)
        assert new_design.copy_solid_bodies_from(self.aedtapp, no_vacuum=False, no_pec=False)
        assert len(new_design.modeler.solid_bodies) == num_orig_bodies
        new_design.delete_design(design_name)
        new_design.close_project(project_name)

    def test_34_object_material_properties(self):
        props = self.aedtapp.get_object_material_properties("MS1", "conductivity")
        assert props

    def test_35_set_export_touchstone(self):
        assert self.aedtapp.set_export_touchstone(True)
        assert self.aedtapp.set_export_touchstone(False)

    def test_36_assign_radiation_to_objects(self):
        self.aedtapp.modeler.primitives.create_box([-100,-100,-100],[200,200,200],name="Rad_box")
        assert self.aedtapp.assign_radiation_boundary_to_objects("Rad_box")

    def test_37_assign_radiation_to_objects(self):
        self.aedtapp.modeler.primitives.create_box(
            [-100, -100, -100], [200, 200, 200], name="Rad_box2")
        ids = [i.id for i in self.aedtapp.modeler.primitives["Rad_box2"].faces]
        assert self.aedtapp.assign_radiation_boundary_to_faces(ids)

    def test_38_get_all_sources(self):
        sources = self.aedtapp.get_all_sources()
        assert isinstance(sources, list)

    def test_39_set_source_contexts(self):
        assert self.aedtapp.set_source_context(["port10", "port11"])

    def test_40_assign_current_source_to_sheet(self):
        sheet = self.aedtapp.modeler.primitives.create_rectangle(self.aedtapp.CoordinateSystemPlane.XYPlane, [0, 0, 0],
                                                         [5, 1], name="RectangleForSource", matname="Copper")
        assert self.aedtapp.assign_current_source_to_sheet(sheet.name)
