import os
import tempfile
import time

from _unittest.conftest import config
from _unittest.conftest import local_path
import pytest

from pyaedt import Hfss3dLayout
from pyaedt import Maxwell3d
from pyaedt.generic.general_methods import generate_unique_name
from pyaedt.generic.general_methods import is_linux

test_subfolder = "T41"
test_project_name = "Test_RadioBoard"
test_rigid_flex = "demo_flex"
test_post = "test_post_processing"
if config["desktopVersion"] > "2022.2":
    diff_proj_name = "differential_pairs_t41_231"
else:
    diff_proj_name = "differential_pairs_t41"


@pytest.fixture(scope="class")
def aedtapp(add_app):
    app = add_app(project_name=test_project_name, application=Hfss3dLayout)
    return app


@pytest.fixture(scope="class")
def hfss3dl(add_app):
    app = add_app(project_name=diff_proj_name, application=Hfss3dLayout, subfolder=test_subfolder)
    return app


@pytest.fixture(scope="class", autouse=True)
def examples(local_scratch):
    example_project = os.path.join(local_path, "../_unittest/example_models", test_subfolder, "Package.aedb")
    target_path = os.path.join(local_scratch.path, "Package_test_41.aedb")
    local_scratch.copyfolder(example_project, target_path)
    return target_path, None


class TestClass:
    @pytest.fixture(autouse=True)
    def init(self, aedtapp, local_scratch, examples):
        self.aedtapp = aedtapp
        self.local_scratch = local_scratch
        self.target_path = examples[0]

    def test_01_creatematerial(self):
        mymat = self.aedtapp.materials.add_material("myMaterial")
        mymat.permittivity = 4.1
        mymat.conductivity = 100
        mymat.youngs_modulus = 1e10
        assert mymat.permittivity.value == 4.1
        assert mymat.conductivity.value == 100
        assert mymat.youngs_modulus.value == 1e10
        assert len(self.aedtapp.materials.material_keys) == 3

    def test_02_stackup(self):
        s1 = self.aedtapp.modeler.layers.add_layer(
            layername="Bottom", layertype="signal", thickness="0.035mm", elevation="0mm", material="iron"
        )
        s1.color = [220, 10, 10]
        s1.is_visible = False
        assert not s1._is_visible
        s1.is_visible = True
        assert s1._is_visible

        s1.is_visible_shape = False
        assert not s1._is_visible_shape
        s1.is_visible_shape = True
        assert s1._is_visible_shape

        s1.is_visible_component = False
        assert not s1._is_visible_component
        s1.is_visible_component = True
        assert s1._is_visible_component

        s1.is_visible_hole = False
        assert not s1._is_visible_hole
        s1.is_visible_hole = True
        assert s1._is_visible_hole

        s1.is_mesh_background = False
        assert not s1._is_mesh_background
        s1.is_mesh_background = True
        assert s1._is_mesh_background

        s1.is_mesh_overlay = False
        assert not s1._is_mesh_overlay
        s1.is_mesh_overlay = True
        assert s1._is_mesh_overlay

        assert not s1.locked
        s1.locked = True
        assert s1.locked
        s1.locked = False

        assert s1.draw_override == 0
        s1.draw_override = 1
        assert s1.draw_override == 1
        s1.draw_override = 0

        assert s1.pattern == 1
        s1.pattern = 0
        assert s1.pattern == 0
        s1.pattern = 1

        assert s1.lower_elevation == "0mm" or s1.lower_elevation == 0.0
        s1.lower_elevation = 1
        assert s1.lower_elevation == 1
        s1.lower_elevation = 0

        assert s1.top_bottom == "neither"
        s1.top_bottom = "top"
        assert s1.top_bottom == "top"
        s1.top_bottom = "neither"

        assert s1.thickness == "0.035mm" or s1.thickness == 3.5e-5
        assert s1.material == "iron"
        assert s1.use_etch is False
        assert s1.user is False
        assert s1.usp is False
        s1.material = "copper"
        s1.fill_material = "glass"
        assert s1.material == "copper"
        assert s1.fill_material == "glass"
        s1.use_etch = True
        s1.etch = 1.2
        s1.user = True
        s1.usp = True
        s1.hfss_solver_settings["dt"] = 1
        s1.planar_em_solver_settings["ifg"] = True
        s1.update_stackup_layer()
        assert s1.use_etch is True
        assert s1.etch == 1.2
        assert s1.user is True
        assert s1.usp is True
        assert s1.hfssSp["dt"] == 1
        assert s1.planaremSp["ifg"] is True
        s1.side_model = "Huray"
        s1.top_model = "Huray"
        s1.bottom_model = "Huray"
        s1.side_nodule_radius = 0.3
        s1.top_nodule_radius = 0.2
        s1.bottom_nodule_radius = 0.1
        s1.side_huray_ratio = 3
        s1.top_huray_ratio = 2.2
        s1.bottom_huray_ratio = 2.5
        assert s1._SHRatio == 3
        assert s1._SNR == 0.3
        assert s1._SRMdl == "Huray"
        assert s1._BRMdl == "Huray"
        assert s1._RMdl == "Huray"
        assert s1._NR == 0.2
        assert s1._BNR == 0.1

        d1 = self.aedtapp.modeler.layers.add_layer(
            layername="Diel3", layertype="dielectric", thickness="1.0mm", elevation="0.035mm", material="plexiglass"
        )
        assert d1.material == "plexiglass"
        assert d1.thickness == "1.0mm" or d1.thickness == 1e-3
        assert d1.transparency == 60
        d1.material = "fr4_epoxy"
        d1.transparency = 23

        assert d1.material == "fr4_epoxy"
        assert d1.transparency == 23
        s2 = self.aedtapp.modeler.layers.add_layer(
            layername="Top",
            layertype="signal",
            thickness=3.5e-5,
            elevation="1.035mm",
            material="copper",
            isnegative=True,
        )
        assert s2.name == "Top"
        assert s2.type == "signal"
        assert s2.material == "copper"
        assert s2.thickness == "0.035mm" or s2.thickness == 3.5e-5
        assert s2._is_negative is True
        s2.is_negative = False
        assert s2._is_negative is False

        s1 = self.aedtapp.modeler.layers.layers[self.aedtapp.modeler.layers.layer_id("Bottom")]
        assert s1.thickness == "0.035mm" or s1.thickness == 3.5e-5
        assert s1.material == "copper"
        assert s1.fill_material == "glass"
        assert s1.use_etch is True
        assert s1.etch == 1.2
        assert s1.user is True
        d1 = self.aedtapp.modeler.layers.layers[self.aedtapp.modeler.layers.layer_id("Diel3")]
        assert d1.material == "fr4_epoxy"
        assert d1.thickness == "1.0mm" or d1.thickness == 1e-3
        s2 = self.aedtapp.modeler.layers.layers[self.aedtapp.modeler.layers.layer_id("Top")]
        assert s2.name == "Top"
        assert s2.type == "signal"
        assert s2.material == "copper"
        assert s2.thickness == 3.5e-5
        assert s2._is_negative is False

        s1.use_etch = False
        s1.user = False
        s1.usp = False

    def test_03_create_circle(self):
        n1 = self.aedtapp.modeler.create_circle("Top", 0, 5, 40, "mycircle")
        assert n1.name == "mycircle"

    def test_04_create_create_rectangle(self):
        n2 = self.aedtapp.modeler.create_rectangle("Top", [0, 0], [6, 8], 3, 2, "myrectangle")
        assert n2.name == "myrectangle"

    def test_05_subtract(self):
        assert self.aedtapp.modeler.subtract("mycircle", "myrectangle")

    def test_06_unite(self):
        n1 = self.aedtapp.modeler.create_circle("Top", 0, 5, 8, "mycircle2")
        n2 = self.aedtapp.modeler.create_rectangle("Top", [0, 0], [6, 8], 3, 2, "myrectangle2")
        assert self.aedtapp.modeler.unite([n1, n2])

    def test_07_intersect(self):
        n1 = self.aedtapp.modeler.create_circle("Top", 0, 5, 8, "mycircle3")
        n2 = self.aedtapp.modeler.create_rectangle("Top", [0, 0], [6, 8], 3, 2, "myrectangle3")
        assert self.aedtapp.modeler.intersect([n1, n2])

    def test_08_objectlist(self):
        a = self.aedtapp.modeler.geometries
        assert len(a) > 0

    def test_09_modify_padstack(self):
        pad_0 = self.aedtapp.modeler.padstacks["PlanarEMVia"]
        assert self.aedtapp.modeler.padstacks["PlanarEMVia"].plating != 55
        pad_0.plating = "55"
        pad_0.update()
        assert self.aedtapp.modeler.padstacks["PlanarEMVia"].plating == "55"

    def test_10_create_padstack(self):
        pad1 = self.aedtapp.modeler.new_padstack("My_padstack2")
        hole1 = pad1.add_hole()
        pad1.add_layer("Start", pad_hole=hole1, thermal_hole=hole1)
        hole2 = pad1.add_hole(holetype="Rct", sizes=[0.5, 0.8])
        pad1.add_layer("Default", pad_hole=hole2, thermal_hole=hole2)
        pad1.add_layer("Stop", pad_hole=hole1, thermal_hole=hole1)
        pad1.hole.sizes = ["0.8mm"]
        pad1.plating = 70
        assert pad1.create()

    def test_11_create_via(self):
        tmp = self.aedtapp.modeler.vias
        cvia = self.aedtapp.modeler.create_via("PlanarEMVia", x=1.1, y=0, name="port_via")
        via = cvia.name
        assert isinstance(via, str)
        assert self.aedtapp.modeler.vias[via].name == via == "port_via"
        assert self.aedtapp.modeler.vias[via].prim_type == "via"
        assert self.aedtapp.modeler.vias[via].location[0] == float(1.1)
        assert self.aedtapp.modeler.vias[via].location[1] == float(0)
        assert self.aedtapp.modeler.vias[via].angle == "0deg"

        via = self.aedtapp.modeler.create_via(x=1, y=1)
        via_1 = via.name
        assert isinstance(via_1, str)
        assert self.aedtapp.modeler.vias[via_1].name == via_1
        assert self.aedtapp.modeler.vias[via_1].prim_type == "via"
        assert self.aedtapp.modeler.vias[via_1].location[0] == float(1)
        assert self.aedtapp.modeler.vias[via_1].location[1] == float(1)
        assert self.aedtapp.modeler.vias[via_1].angle == "0deg"
        assert self.aedtapp.modeler.vias[via_1].holediam == "1mm"
        via2 = self.aedtapp.modeler.create_via("PlanarEMVia", x=10, y=10, name="Via123", netname="VCC")
        via_2 = via2.name
        assert isinstance(via_2, str)
        assert self.aedtapp.modeler.vias[via_2].name == via_2
        assert self.aedtapp.modeler.vias[via_2].prim_type == "via"
        assert self.aedtapp.modeler.vias[via_2].location[0] == float(10)
        assert self.aedtapp.modeler.vias[via_2].location[1] == float(10)
        assert self.aedtapp.modeler.vias[via_2].angle == "0deg"
        assert "VCC" in self.aedtapp.oeditor.GetNets()
        via_3 = self.aedtapp.modeler.create_via(
            "PlanarEMVia", x=5, y=5, name="Via1234", netname="VCC", hole_diam="22mm"
        )
        assert via_3.location[0] == float(5)
        assert via_3.location[1] == float(5)
        assert via_3.angle == "0deg"
        assert via_3.holediam == "22mm"
        assert "VCC" in self.aedtapp.oeditor.GetNets()

    def test_12_create_line(self):
        line = self.aedtapp.modeler.create_line(
            "Bottom", [[0, 0], [10, 30], [20, 30]], lw=1, name="line2", net_name="VCC"
        )
        assert line.name == "line2"
        line.name = "line1"
        assert isinstance(line.center_line, dict)
        line.center_line = {"Pt0": [1, "0mm"]}
        assert line.center_line["Pt0"] == ["1", "0"]
        line.center_line = {"Pt0": ["0mm", "0mm"]}
        assert line.remove("Pt1")
        assert line.add([1, 2], 1)

    def test_13a_create_edge_port(self):
        port_wave = self.aedtapp.create_edge_port("line1", 3, False, True, 6, 4, "2mm")
        assert port_wave
        assert self.aedtapp.delete_port(port_wave.name)
        port_wave = self.aedtapp.create_wave_port("line1", 3, 6, 4, "2mm")
        assert port_wave
        assert self.aedtapp.delete_port(port_wave.name)
        assert self.aedtapp.create_edge_port("line1", 3, False)
        assert len(self.aedtapp.excitations) > 0
        time_domain = os.path.join(local_path, "../_unittest/example_models", test_subfolder, "Sinusoidal.csv")
        assert self.aedtapp.edit_source_from_file(
            port_wave.name,
            time_domain,
            is_time_domain=True,
            data_format="Voltage",
            x_scale=1e-6,
            y_scale=1e-3,
        )

    def test_14a_create_coaxial_port(self):
        port = self.aedtapp.create_coax_port("port_via", 0.5, "Top", "Lower")
        assert port.name == "Port2"
        assert port.props["Radial Extent Factor"] == "0.5"

    def test_14_create_setup(self):
        setup_name = "RFBoardSetup"
        setup = self.aedtapp.create_setup(setupname=setup_name)
        assert setup.name == self.aedtapp.existing_analysis_setups[0]
        assert setup.solver_type == "HFSS"

    def test_15_edit_setup(self):
        setup_name = "RFBoardSetup2"
        setup2 = self.aedtapp.create_setup(setupname=setup_name)
        assert not setup2.get_sweep()

        sweep = setup2.add_sweep()
        sweep1 = setup2.get_sweep(sweep.name)
        assert sweep1 == sweep
        sweep2 = setup2.get_sweep()
        assert sweep2 == sweep1
        setup2.props["AdaptiveSettings"]["SingleFrequencyDataList"]["AdaptiveFrequencyData"][
            "AdaptiveFrequency"
        ] = "1GHz"
        setup2.props["AdaptiveSettings"]["SingleFrequencyDataList"]["AdaptiveFrequencyData"]["MaxPasses"] = 23
        setup2.props["AdvancedSettings"]["OrderBasis"] = 2
        setup2.props["PercentRefinementPerPass"] = 17
        assert setup2.update()

    def test_16_disable_enable_setup(self):
        setup_name = "RFBoardSetup3"
        setup3 = self.aedtapp.create_setup(setupname=setup_name)
        setup3.props["AdaptiveSettings"]["SingleFrequencyDataList"]["AdaptiveFrequencyData"]["MaxPasses"] = 1
        assert setup3.update()
        assert setup3.disable()
        assert setup3.enable()
        sweep = setup3.add_sweep()
        assert sweep
        assert sweep.change_range("LinearStep", 1.1, 2.1, 0.4, "GHz")
        assert sweep.add_subrange("LinearCount", 1, 1.5, 3, "MHz")
        assert sweep.change_type("Discrete")
        assert not sweep.add_subrange("SinglePoint", 10.1e-1, "GHz")
        assert not sweep.add_subrange("SinglePoint", 10.2e-1, "GHz")
        assert sweep.set_save_fields(True, True)
        assert sweep.set_save_fields(False, False)

    def test_17_get_setup(self):
        setup4 = self.aedtapp.get_setup(self.aedtapp.existing_analysis_setups[0])
        setup4.props["PercentRefinementPerPass"] = 37
        setup4.props["AdaptiveSettings"]["SingleFrequencyDataList"]["AdaptiveFrequencyData"]["MaxPasses"] = 44
        assert setup4.update()
        assert setup4.disable()
        assert setup4.enable()

    def test_18a_create_linear_count_sweep(self):
        setup_name = "RF_create_linear_count"
        self.aedtapp.create_setup(setupname=setup_name)
        sweep1 = self.aedtapp.create_linear_count_sweep(
            setupname=setup_name,
            unit="GHz",
            freqstart=1,
            freqstop=10,
            num_of_freq_points=1001,
            sweepname="RFBoardSweep1",
            sweep_type="Interpolating",
            interpolation_tol_percent=0.2,
            interpolation_max_solutions=111,
            save_fields=False,
            use_q3d_for_dc=False,
        )
        assert sweep1.props["Sweeps"]["Data"] == "LINC 1GHz 10GHz 1001"
        sweep2 = self.aedtapp.create_linear_count_sweep(
            setupname=setup_name,
            unit="GHz",
            freqstart=1,
            freqstop=10,
            num_of_freq_points=12,
            sweepname="RFBoardSweep2",
            sweep_type="Discrete",
            interpolation_tol_percent=0.4,
            interpolation_max_solutions=255,
            save_fields=True,
            save_rad_fields_only=True,
            use_q3d_for_dc=True,
        )
        assert sweep2.props["Sweeps"]["Data"] == "LINC 1GHz 10GHz 12"

    def test_18b_create_linear_step_sweep(self):
        setup_name = "RF_create_linear_step"
        self.aedtapp.create_setup(setupname=setup_name)
        sweep3 = self.aedtapp.create_linear_step_sweep(
            setupname=setup_name,
            unit="GHz",
            freqstart=1,
            freqstop=10,
            step_size=0.2,
            sweepname="RFBoardSweep3",
            sweep_type="Interpolating",
            interpolation_tol_percent=0.4,
            interpolation_max_solutions=255,
            save_fields=True,
            save_rad_fields_only=True,
            use_q3d_for_dc=True,
        )
        assert sweep3.props["Sweeps"]["Data"] == "LIN 1GHz 10GHz 0.2GHz"
        sweep4 = self.aedtapp.create_linear_step_sweep(
            setupname=setup_name,
            unit="GHz",
            freqstart=1,
            freqstop=10,
            step_size=0.12,
            sweepname="RFBoardSweep4",
            sweep_type="Discrete",
            save_fields=True,
        )
        assert sweep4.props["Sweeps"]["Data"] == "LIN 1GHz 10GHz 0.12GHz"

        # Create a linear step sweep with the incorrect sweep type.
        with pytest.raises(AttributeError) as execinfo:
            self.aedtapp.create_linear_step_sweep(
                setupname=setup_name,
                unit="GHz",
                freqstart=1,
                freqstop=10,
                step_size=0.12,
                sweepname="RFBoardSweep4",
                sweep_type="Incorrect",
                save_fields=True,
            )
            assert (
                execinfo.args[0] == "Invalid value for 'sweep_type'. The value must be 'Discrete', "
                "'Interpolating', or 'Fast'."
            )

    def test_18c_create_single_point_sweep(self):
        setup_name = "RF_create_single_point"
        self.aedtapp.create_setup(setupname=setup_name)
        sweep5 = self.aedtapp.create_single_point_sweep(
            setupname=setup_name,
            unit="MHz",
            freq=1.23,
            sweepname="RFBoardSingle",
            save_fields=True,
        )
        assert sweep5.props["Sweeps"]["Data"] == "1.23MHz"
        sweep6 = self.aedtapp.create_single_point_sweep(
            setupname=setup_name,
            unit="GHz",
            freq=[1, 2, 3, 4],
            sweepname="RFBoardSingle",
            save_fields=False,
        )
        assert sweep6.props["Sweeps"]["Data"] == "1GHz 2GHz 3GHz 4GHz"

        with pytest.raises(AttributeError) as execinfo:
            self.aedtapp.create_single_point_sweep(
                setupname=setup_name,
                unit="GHz",
                freq=[],
                sweepname="RFBoardSingle",
                save_fields=False,
            )
            assert execinfo.args[0] == "Frequency list is empty. Specify at least one frequency point."

    def test_18d_delete_setup(self):
        setup_name = "SetupToDelete"
        setuptd = self.aedtapp.create_setup(setupname=setup_name)
        assert setuptd.name in self.aedtapp.existing_analysis_setups
        self.aedtapp.delete_setup(setup_name)
        assert setuptd.name not in self.aedtapp.existing_analysis_setups

    def test_19A_validate(self):
        assert self.aedtapp.validate_full_design()

    def test_19D_export_to_hfss(self):
        self.aedtapp.save_project()
        filename = "export_to_hfss_test"
        filename2 = "export_to_hfss_test2"
        file_fullname = os.path.join(self.local_scratch.path, filename)
        file_fullname2 = os.path.join(self.local_scratch.path, filename2)
        setup = self.aedtapp.get_setup(self.aedtapp.existing_analysis_setups[0])
        assert setup.export_to_hfss(file_fullname=file_fullname)
        assert setup.export_to_hfss(file_fullname=file_fullname2, keep_net_name=True)

    def test_19E_export_to_q3d(self):
        filename = "export_to_q3d_test"
        file_fullname = os.path.join(self.local_scratch.path, filename)
        setup = self.aedtapp.get_setup(self.aedtapp.existing_analysis_setups[0])
        assert setup.export_to_q3d(file_fullname)

    def test_21_variables(self):
        assert isinstance(self.aedtapp.available_variations.nominal_w_values_dict, dict)
        assert isinstance(self.aedtapp.available_variations.nominal_w_values, list)

    def test_26_duplicate(self):
        assert self.aedtapp.modeler.duplicate("myrectangle", 2, [1, 1])
        assert self.aedtapp.modeler.duplicate_across_layers("mycircle2", "Bottom")

    def test_27_create_pin_port(self):
        port = self.aedtapp.create_pin_port("PinPort1")
        assert port.name == "PinPort1"
        port.props["Magnitude"] = "2V"
        assert port.props["Magnitude"] == "2V"
        assert port.object_properties.props["Magnitude"] == "2V"
        port.object_properties.props["Magnitude"] = "5V"
        assert port.object_properties.props["Magnitude"] == "5V"

    def test_28_create_scattering(self):
        assert self.aedtapp.create_scattering()

    def test_29_duplicate_material(self):
        material = self.aedtapp.materials.add_material("FirstMaterial")
        new_material = self.aedtapp.materials.duplicate_material("FirstMaterial", "SecondMaterial")
        assert new_material.name == "SecondMaterial"

    def test_30_expand(self):
        self.aedtapp.modeler.create_rectangle("Bottom", [20, 20], [50, 50], name="rect_1")
        self.aedtapp.modeler.create_line("Bottom", [[25, 25], [40, 40]], name="line_3")
        out1 = self.aedtapp.modeler.expand("line_3", size=1, expand_type="ROUND", replace_original=False)
        assert isinstance(out1, str)

    def test_31_heal(self):
        l1 = self.aedtapp.modeler.create_line("Bottom", [[0, 0], [100, 0]], 0.5, name="poly_1111")
        l2 = self.aedtapp.modeler.create_line("Bottom", [[100, 0], [120, -35]], 0.5, name="poly_2222")
        self.aedtapp.modeler.unite([l1, l2])
        assert self.aedtapp.modeler.colinear_heal("poly_2222", tolerance=0.25)

    def test_32_cosim_simulation(self):
        assert self.aedtapp.edit_cosim_options()
        assert not self.aedtapp.edit_cosim_options(interpolation_algorithm="auto1")

    def test_33_set_temperature_dependence(self):
        assert self.aedtapp.modeler.set_temperature_dependence(
            include_temperature_dependence=True,
            enable_feedback=True,
            ambient_temp=23,
            create_project_var=False,
        )
        assert self.aedtapp.modeler.set_temperature_dependence(
            include_temperature_dependence=False,
        )
        assert self.aedtapp.modeler.set_temperature_dependence(
            include_temperature_dependence=True,
            enable_feedback=True,
            ambient_temp=27,
            create_project_var=True,
        )
        pass

    def test_34_create_additional_setup(self):
        setup_name = "SiwaveDC"
        setup = self.aedtapp.create_setup(setupname=setup_name, setuptype="SiwaveDC3DLayout")
        assert setup_name == setup.name
        setup_name = "SiwaveAC"
        setup = self.aedtapp.create_setup(setupname=setup_name, setuptype="SiwaveAC3DLayout")
        assert setup_name == setup.name
        setup_name = "LNA"
        setup = self.aedtapp.create_setup(setupname=setup_name, setuptype="LNA3DLayout")
        assert setup_name == setup.name

    def test_35a_export_layout(self):
        self.aedtapp.insert_design("export_layout")
        s1 = self.aedtapp.modeler.layers.add_layer(
            layername="Top", layertype="signal", thickness="0.035mm", elevation="0mm", material="iron"
        )
        n2 = self.aedtapp.modeler.create_rectangle("Top", [0, 0], [6, 8], 3, 2, "myrectangle")
        output = self.aedtapp.export_3d_model()
        time_out = 0
        while time_out < 10:
            if not os.path.exists(output):
                time_out += 1
                time.sleep(1)
            else:
                break
        if time_out == 10:
            assert False

    @pytest.mark.skipif(is_linux, reason="Failing on linux")
    def test_36_import_gerber(self):
        self.aedtapp.insert_design("gerber")
        gerber_file = self.local_scratch.copyfile(
            os.path.join(local_path, "../_unittest/example_models", "cad", "Gerber", "gerber1.zip")
        )
        control_file = self.local_scratch.copyfile(
            os.path.join(local_path, "../_unittest/example_models", "cad", "Gerber", "gerber1.xml")
        )

        aedb_file = os.path.join(self.local_scratch.path, generate_unique_name("gerber_out") + ".aedb")
        assert self.aedtapp.import_gerber(gerber_file, aedb_path=aedb_file, control_file=control_file)

    @pytest.mark.skipif(is_linux, reason="Fails in linux")
    def test_37_import_gds(self):
        self.aedtapp.insert_design("gds")
        gds_file = os.path.join(local_path, "../_unittest/example_models", "cad", "GDS", "gds1.gds")
        control_file = self.local_scratch.copyfile(
            os.path.join(local_path, "../_unittest/example_models", "cad", "GDS", "gds1.tech")
        )
        aedb_file = os.path.join(self.local_scratch.path, generate_unique_name("gds_out") + ".aedb")
        assert self.aedtapp.import_gds(gds_file, aedb_path=aedb_file, control_file=control_file)

    @pytest.mark.skipif(is_linux, reason="Fails in linux")
    def test_38_import_dxf(self):
        self.aedtapp.insert_design("dxf")
        dxf_file = os.path.join(local_path, "../_unittest/example_models", "cad", "DXF", "dxf1.dxf")
        control_file = os.path.join(local_path, "../_unittest/example_models", "cad", "DXF", "dxf1.xml")
        aedb_file = os.path.join(self.local_scratch.path, "dxf_out.aedb")
        assert self.aedtapp.import_gerber(dxf_file, aedb_path=aedb_file, control_file=control_file)

    def test_39_import_ipc(self):
        self.aedtapp.insert_design("ipc")
        dxf_file = os.path.join(local_path, "../_unittest/example_models", "cad", "ipc", "galileo.xml")
        aedb_file = os.path.join(self.local_scratch.path, "ipc_out.aedb")
        assert self.aedtapp.import_ipc2581(dxf_file, aedb_path=aedb_file, control_file="")

    @pytest.mark.skipif(config["desktopVersion"] < "2022.2", reason="Not working on AEDT 22R1")
    def test_40_test_flex(self, add_app):
        flex = add_app(project_name=test_rigid_flex, application=Hfss3dLayout, subfolder=test_subfolder)
        assert flex.enable_rigid_flex()
        pass

    def test_41_test_create_polygon(self):
        points = [[100, 100], [100, 200], [200, 200]]
        p1 = self.aedtapp.modeler.create_polygon("Top", points, name="poly_41")
        assert p1.name == "poly_41"
        points2 = [[120, 120], [120, 170], [170, 140]]

        p2 = self.aedtapp.modeler.create_polygon_void("Top", points2, p1.name, name="poly_test_41_void")

        assert p2.name == "poly_test_41_void"
        assert not self.aedtapp.modeler.create_polygon_void("Top", points2, "another_object", name="poly_43_void")

    @pytest.mark.skipif(not config["use_grpc"], reason="Not running in COM mode")
    @pytest.mark.skipif(config["desktopVersion"] < "2023.2", reason="Working only from 2023 R2")
    def test_42_post_processing(self, add_app):
        test_post1 = add_app(project_name=test_post, application=Maxwell3d, subfolder=test_subfolder)
        assert test_post1.post.create_fieldplot_layers_nets(
            [["TOP", "GND", "V3P3_S5"], ["PWR", "V3P3_S5"]],
            "Mag_Volume_Force_Density",
            intrinsics={"Time": "1ms"},
            plot_name="Test_Layers",
        )
        test_post2 = add_app(project_name=test_post1.project_name, just_open=True)
        assert test_post2.post.create_fieldplot_layers_nets(
            [["TOP", "GND", "V3P3_S5"], ["PWR", "V3P3_S5"]],
            "Mag_E",
            intrinsics={"Freq": "1GHz", "Phase": "0deg"},
            plot_name="Test_Layers",
        )
        self.aedtapp.close_project(test_post2.project_name)

    @pytest.mark.skipif(config["desktopVersion"] < "2023.2", reason="Working only from 2023 R2")
    def test_42_post_processing_3d_layout(self, add_app):
        test = add_app(
            project_name="test_post_3d_layout_solved_23R2", application=Hfss3dLayout, subfolder=test_subfolder
        )
        pl1 = test.post.create_fieldplot_layers_nets(
            [["TOP", "GND", "V3P3_S5"], ["PWR", "V3P3_S5"]],
            "Mag_E",
            intrinsics={"Freq": "1GHz"},
            plot_name="Test_Layers",
        )
        assert pl1
        assert pl1.export_image_from_aedtplt(tempfile.gettempdir())
        self.aedtapp.close_project(test.project_name)

    @pytest.mark.skipif(is_linux, reason="Bug on linux")
    def test_90_set_differential_pairs(self, hfss3dl):
        assert not self.aedtapp.get_differential_pairs()
        assert hfss3dl.set_differential_pair(
            positive_terminal="Port3",
            negative_terminal="Port4",
            common_name=None,
            diff_name=None,
            common_ref_z=34,
            diff_ref_z=123,
            active=True,
            matched=False,
        )
        assert hfss3dl.set_differential_pair(positive_terminal="Port3", negative_terminal="Port5")
        assert hfss3dl.get_differential_pairs()
        assert hfss3dl.get_traces_for_plot(differential_pairs=["Diff1"], category="dB(S")

    @pytest.mark.skipif(is_linux, reason="Bug on linux")
    def test_91_load_and_save_diff_pair_file(self, hfss3dl):
        diff_def_file = os.path.join(
            local_path, "../_unittest/example_models", test_subfolder, "differential_pairs_definition.txt"
        )
        diff_file = self.local_scratch.copyfile(diff_def_file)
        assert hfss3dl.load_diff_pairs_from_file(diff_file)

        diff_file2 = os.path.join(self.local_scratch.path, "diff_file2.txt")
        assert hfss3dl.save_diff_pairs_to_file(diff_file2)
        with open(diff_file2, "r") as fh:
            lines = fh.read().splitlines()
        assert len(lines) == 3

    def test_92_import_edb(self):
        assert self.aedtapp.import_edb(self.target_path)

    @pytest.mark.skipif(
        config["desktopVersion"] < "2022.2", reason="This test does not work on versions earlier than 2022 R2."
    )
    def test_93_clip_plane(self):
        cp_name = self.aedtapp.modeler.clip_plane()
        assert cp_name in self.aedtapp.modeler.clip_planes

    def test_94_edit_3dlayout_extents(self):
        assert self.aedtapp.edit_hfss_extents(
            diel_extent_type="ConformalExtent",
            diel_extent_horizontal_padding="1mm",
            air_extent_type="ConformalExtent",
            air_vertical_positive_padding="10mm",
            air_vertical_negative_padding="10mm",
            air_horizontal_padding="1mm",
        )

    def test_95_create_text(self):
        assert self.aedtapp.modeler.create_text("test", [0, 0], "SIwave Regions")

    def test_96_change_nets_visibility(self, add_app):
        project_name = "ipc_out"
        design_name = "Galileo_um"
        hfss3d = add_app(application=Hfss3dLayout, project_name=project_name, design_name=design_name, just_open=True)
        # hide all
        assert hfss3d.modeler.change_net_visibility(visible=False)
        # hide all
        assert hfss3d.modeler.change_net_visibility(visible="false")
        # visualize all
        assert hfss3d.modeler.change_net_visibility(visible=True)
        # visualize all
        assert hfss3d.modeler.change_net_visibility(visible="true")
        # visualize selected nets only
        assert hfss3d.modeler.change_net_visibility(["V3P3_S0", "V3P3_S3", "V3P3_S5"], visible=True)
        # hide selected nets and show others
        assert hfss3d.modeler.change_net_visibility(["V3P3_S0", "V3P3_S3", "V3P3_S5"], visible=False)
        assert not hfss3d.modeler.change_net_visibility(["test1, test2"])
        assert not hfss3d.modeler.change_net_visibility(visible="")
        assert not hfss3d.modeler.change_net_visibility(visible=0)

    def test_97_mesh_settings(self):
        assert self.aedtapp.set_meshing_settings(mesh_method="PhiPlus", enable_intersections_check=False)
        assert self.aedtapp.set_meshing_settings(mesh_method="Classic", enable_intersections_check=True)

    def test_98_geom_check(self):
        assert self.aedtapp.modeler.geometry_check_and_fix_all()
