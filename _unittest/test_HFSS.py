import os
# Setup paths for module imports
from .conftest import scratch_path, module_path
import gc
# Import required modules
from pyaedt import Hfss
from pyaedt.generic.filesystem import Scratch

test_project_name = "coax_HFSS"


class TestHFSS:
    def setup_class(self):
        #self.desktop = Desktop(desktopVersion, NonGraphical, NewThread)
        # set a scratch directory and the environment / test data
        with Scratch(scratch_path) as self.local_scratch:
            self.aedtapp = Hfss()

    def teardown_class(self):
        assert self.aedtapp.close_project(self.aedtapp.project_name)
        #self.desktop.force_close_desktop()
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
        id1 = self.aedtapp.modeler.primitives.create_cylinder(self.aedtapp.CoordinateSystemPlane.XYPlane, udp, 3, coax_dimension,
                                                         0, "inner")
        assert isinstance(id1, int)
        id2 = self.aedtapp.modeler.primitives.create_cylinder(self.aedtapp.CoordinateSystemPlane.XYPlane, udp, 10, coax_dimension,
                                                         0, "outer")
        assert isinstance(id2, int)
        assert self.aedtapp.modeler.subtract(id2, id1, True)

    def test_03_1_load_material(self):
        material_database = os.path.join(module_path, 'pyaedt', 'misc', 'amat.xml')
        assert self.aedtapp.materials.load_from_file(material_database)

    def test_03_2_assign_material(self):
        udp = self.aedtapp.modeler.Position(0, 0, 0)
        coax_dimension = 150
        id1 = self.aedtapp.modeler.primitives.get_obj_id("inner")
        id2 = self.aedtapp.modeler.primitives.create_cylinder(self.aedtapp.CoordinateSystemPlane.XYPlane, udp, 10,
                                                              coax_dimension, 0, "die")
        assert self.aedtapp.modeler.subtract("die", "inner", True)
        assert self.aedtapp.assignmaterial([id1], "Copper")
        assert self.aedtapp.assignmaterial(id2, "teflon_based")
        assert self.aedtapp.assignmaterial("outer", "Copper")
        pass

    def test_04_assign_coating(self):
        id1 = self.aedtapp.modeler.primitives.get_obj_id("inner")
        coat = self.aedtapp.assigncoating([id1], "copper")
        assert coat
        assert coat.name

    def test_05_create_wave_port_from_sheets(self):
        udp = self.aedtapp.modeler.Position(0, 0, 0)
        id5 = self.aedtapp.modeler.primitives.create_circle(self.aedtapp.CoordinateSystemPlane.YZPlane,udp,10, name="sheet1")
        self.aedtapp.solution_type ="DrivenTerminal"
        ports = self.aedtapp.create_wave_port_from_sheet(id5, 5, self.aedtapp.AxisDir.XNeg, 40, 2, "sheet1_Port", True)
        assert ports[0].name == "sheet1_Port"
        assert ports[0].name in [i.name for i in self.aedtapp.boundaries]
        self.aedtapp.solution_type ="DrivenModal"
        udp = self.aedtapp.modeler.Position(5, 0, 0)
        id6 = self.aedtapp.modeler.primitives.create_circle(self.aedtapp.CoordinateSystemPlane.YZPlane,udp,10, name="sheet2")
        ports = self.aedtapp.create_wave_port_from_sheet(id6, 5, self.aedtapp.AxisDir.XPos, 40, 2, "sheet2_Port", True)
        assert ports[0].name == "sheet2_Port"
        assert ports[0].name in [i.name for i in self.aedtapp.boundaries]

        id6 = self.aedtapp.modeler.primitives.create_box([20,20,20], [10,10,2],matname="Copper", name="My_Box")
        id7 = self.aedtapp.modeler.primitives.create_box([20,25,30], [10,2,2],matname="Copper")
        rect = self.aedtapp.modeler.primitives.create_rectangle(self.aedtapp.CoordinateSystemPlane.YZPlane,[20,25,20],[2,10])
        ports = self.aedtapp.create_wave_port_from_sheet(rect, 5, self.aedtapp.AxisDir.ZNeg, 40, 2, "sheet3_Port", True)
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
        assert self.aedtapp.create_discrete_sweep("MySetup")

    def test_06B_setup_exists(self):
        assert self.aedtapp.analysis_setup is not None
        assert self.aedtapp.nominal_sweep is not None

    def test_06b_create_linear_count_sweep(self):
        assert self.aedtapp.create_linear_count_sweep(setupname="MySetup", sweepname=None,
                                                      unit="MHz", freqstart=1.1e3, freqstop=1200.1,
                                                      num_of_freq_points=1658)

    def test_06c_create_linear_step_sweep(self):
        assert self.aedtapp.create_linear_step_sweep(setupname="MySetup", sweepname=None,
                                                     unit="MHz", freqstart=1.1e3, freqstop=1200.1,
                                                     step_size=153.8)

    def test_06z_validate_setup(self):
        list, ok = self.aedtapp.validate_full_design(ports=5)
        assert ok
        pass

    def test_07_set_power(self):
        id1 = self.aedtapp.modeler.primitives.get_obj_id("inner")
        assert self.aedtapp.edit_source("sheet1_Port" + ":1", "10W")

    def test_08_create_circuit_port_from_edges(self):
        plane = self.aedtapp.CoordinateSystemPlane.XYPlane
        rectid1 = self.aedtapp.modeler.primitives.create_rectangle(plane, [10, 10, 10], [10, 10], name="rect1_for_port")
        edges1 = self.aedtapp.modeler.primitives.get_object_edges(rectid1)
        e1 = edges1[0]
        rectid2 = self.aedtapp.modeler.primitives.create_rectangle(plane, [30, 10, 10], [10, 10], name="rect2_for_port")
        edges2 = self.aedtapp.modeler.primitives.get_object_edges(rectid2)
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
        box2 = self.aedtapp.modeler.primitives.create_box([0, 0, 10], [10, 10, 5], "BoxWG2", "copper")
        self.aedtapp.assignmaterial("BoxWG2", "Copper")
        port = self.aedtapp.create_wave_port_between_objects("BoxWG1", "BoxWG2", self.aedtapp.AxisDir.XNeg, 50, 1, "Wave1",
                                                             False)
        assert port.name == "Wave1"
        port2 = self.aedtapp.create_wave_port_between_objects("BoxWG1", "BoxWG2", self.aedtapp.AxisDir.XPos, 25, 2,
                                                           "Wave1", True, 5)
        assert port2.name != "Wave1" and "Wave1" in port2.name

    def test_10_create_lumped_on_objects(self):
        box1 = self.aedtapp.modeler.primitives.create_box([0, 0, 50], [10, 10, 5], "BoxLumped1")
        self.aedtapp.assignmaterial("BoxLumped1", "Copper")
        box2 = self.aedtapp.modeler.primitives.create_box([0, 0, 60], [10, 10, 5], "BoxLumped2")
        self.aedtapp.assignmaterial("BoxLumped2", "Copper")
        port = self.aedtapp.create_lumped_port_between_objects("BoxLumped1", "BoxLumped2", self.aedtapp.AxisDir.XNeg, 50,
                                                            "Lump1", True, False)
        assert port == "Lump1"

    def test_11_create_circuit_on_objects(self):
        box1 = self.aedtapp.modeler.primitives.create_box([0, 0, 80], [10, 10, 5], "BoxCircuit1","Copper")
        box2 = self.aedtapp.modeler.primitives.create_box([0, 0, 100], [10, 10, 5], "BoxCircuit2", "copper")
        self.aedtapp.assignmaterial("BoxCircuit2", "Copper")
        port = self.aedtapp.create_circuit_port_between_objects("BoxCircuit1", "BoxCircuit2", self.aedtapp.AxisDir.XNeg,
                                                                50, "Circ1", True, 50, False)
        assert port == "Circ1"

    def test_12_create_perfects_on_objects(self):
        box1 = self.aedtapp.modeler.primitives.create_box([0,0,0], [10,10,5], "p1", "Copper")
        box2 = self.aedtapp.modeler.primitives.create_box([0, 0, 10], [10, 10, 5], "p2", "copper")
        pe = self.aedtapp.create_perfecth_from_objects("p1","p2",self.aedtapp.AxisDir.ZPos,)
        ph = self.aedtapp.create_perfecte_from_objects("p1","p2",self.aedtapp.AxisDir.ZNeg)
        assert pe.name in self.aedtapp.modeler.get_boundaries_name()
        assert ph.name in self.aedtapp.modeler.get_boundaries_name()

    def test_13_create_impedance_on_objects(self):
        box1 = self.aedtapp.modeler.primitives.create_box([0,0,0], [10,10,5], "imp1", "Copper")
        box2 = self.aedtapp.modeler.primitives.create_box([0, 0, 10], [10, 10, 5], "imp2", "copper")
        imp = self.aedtapp.create_impedance_between_objects("imp1", "imp2", self.aedtapp.AxisDir.XPos, "TL2", 50, 25)
        assert imp.name in self.aedtapp.modeler.get_boundaries_name()

    def test_14_create_lumpedrlc_on_objects(self):
        box1 = self.aedtapp.modeler.primitives.create_box([0,0,0], [10,10,5], "rlc1", "Copper")
        box2 = self.aedtapp.modeler.primitives.create_box([0, 0, 10], [10, 10, 5], "rlc2", "copper")
        imp = self.aedtapp.create_lumped_rlc_between_objects("rlc1","rlc2",self.aedtapp.AxisDir.XPos,Rvalue=50,Lvalue=1e-9)
        assert imp.name in self.aedtapp.modeler.get_boundaries_name()

    def test_15_create_perfects_on_sheets(self):
        rect = self.aedtapp.modeler.primitives.create_rectangle(self.aedtapp.CoordinateSystemPlane.XYPlane, [0, 0, 0],
                                                                [10, 2], "RectBound", "Copper")
        pe = self.aedtapp.assign_perfecte_to_sheets("RectBound")
        assert pe.name in self.aedtapp.modeler.get_boundaries_name()
        ph = self.aedtapp.assign_perfecth_to_sheets("RectBound")
        assert ph.name in self.aedtapp.modeler.get_boundaries_name()

    def test_16_create_impedance_on_sheets(self):
        rect = self.aedtapp.modeler.primitives.create_rectangle(self.aedtapp.CoordinateSystemPlane.XYPlane, [0, 0, 0],
                                                                [10, 2], "ImpBound", "Copper")
        imp = self.aedtapp.assign_impedance_to_sheet("imp1", "TL2", 50, 25)
        assert imp.name in self.aedtapp.modeler.get_boundaries_name()

    def test_17_create_lumpedrlc_on_sheets(self):
        rect = self.aedtapp.modeler.primitives.create_rectangle(self.aedtapp.CoordinateSystemPlane.XYPlane, [0, 0, 0],
                                                                [10, 2], "rlcBound", "Copper")
        imp = self.aedtapp.assign_lumped_rlc_to_sheet("rlcBound", self.aedtapp.AxisDir.XPos,Rvalue=50,Lvalue=1e-9)
        names = self.aedtapp.modeler.get_boundaries_name()
        assert imp.name in self.aedtapp.modeler.get_boundaries_name()
        bound = self.aedtapp.assign_perfecth_to_sheets(self.aedtapp.modeler.primitives["My_Box"].faces[0].id)
        assert bound
        bound.props["Faces"].append(self.aedtapp.modeler.primitives["My_Box"].faces[1])
        bound.update_assignment()
        bound.props["Faces"] = "rlcBound"
        bound.update_assignment()


    def test_18_create_sources_on_objects(self):
        box1 = self.aedtapp.modeler.primitives.create_box([30,0,0], [40,10,5], "BoxVolt1", "Copper")
        box2 = self.aedtapp.modeler.primitives.create_box([30, 0, 10], [40, 10, 5], "BoxVolt2", "Copper")
        port = self.aedtapp.create_voltage_source_from_objects("BoxVolt1", "BoxVolt2", self.aedtapp.AxisDir.XNeg, "Volt1")
        assert port in self.aedtapp.modeler.get_excitations_name()
        port = self.aedtapp.create_current_source_from_objects("BoxVolt1", "BoxVolt2", self.aedtapp.AxisDir.XPos, "Curr1")
        assert port in self.aedtapp.modeler.get_excitations_name()

    def test_19_create_lumped_on_sheet(self):
        rect = self.aedtapp.modeler.primitives.create_rectangle(self.aedtapp.CoordinateSystemPlane.XYPlane, [0, 0, 0],
                                                                [10, 2], "lump_port", "Copper")
        port = self.aedtapp.create_lumped_port_to_sheet("lump_port", self.aedtapp.AxisDir.XNeg, 50,
                                                            "Lump_sheet", True, False)
        assert port+":1" in self.aedtapp.modeler.get_excitations_name()

    def test_20_create_voltage_on_sheet(self):
        rect = self.aedtapp.modeler.primitives.create_rectangle(self.aedtapp.CoordinateSystemPlane.XYPlane, [0, 0, 0],
                                                                [10, 2], "lump_volt", "Copper")
        port = self.aedtapp.assig_voltage_source_to_sheet("lump_volt", self.aedtapp.AxisDir.XNeg,  "LumpVolt1")
        assert port in self.aedtapp.modeler.get_excitations_name()

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
        mesh = self.aedtapp.mesh.appy_curvilinear_elements(["BoxCircuit2"])
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
        assert setup1.add_calculation(calculation="dB(S(1,1))", calculation_value="2.5GHz", reporttype="Modal Solution Data")

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
        ms = self.aedtapp.modeler.primitives.create_box([4,5,0],[1,100,0.2],name="MS1", matname="copper")
        sub = self.aedtapp.modeler.primitives.create_box([0,5,-2],[20,100,2],name="SUB1", matname="FR4_epoxy")
        gnd = self.aedtapp.modeler.primitives.create_box([0,5,-2.2],[20,100,0.2],name="GND1", matname="FR4_epoxy")
        port = self.aedtapp.create_wave_port_microstrip_between_objects("GND1", "MS1",   portname="MS1", axisdir=1)
        assert port.name == "MS1"
