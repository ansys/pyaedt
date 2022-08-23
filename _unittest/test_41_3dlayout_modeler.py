import os
import time

from _unittest.conftest import BasisTest
from _unittest.conftest import config
from _unittest.conftest import is_ironpython
from _unittest.conftest import local_path
from _unittest.conftest import scratch_path
from pyaedt import Hfss3dLayout
from pyaedt.generic.filesystem import Scratch

try:
    import pytest  # noqa: F401
except ImportError:
    import _unittest_ironpython.conf_unittest as pytest  # noqa: F401

# Input Data and version for the test
test_project_name = "Test_RadioBoard"
test_rigid_flex = "demo_flex"


class TestClass(BasisTest, object):
    def setup_class(self):
        BasisTest.my_setup(self)
        self.aedtapp = BasisTest.add_app(self, project_name=test_project_name, application=Hfss3dLayout)
        self.hfss3dl = BasisTest.add_app(self, project_name="differential_pairs", application=Hfss3dLayout)
        self.flex = BasisTest.add_app(self, project_name=test_rigid_flex, application=Hfss3dLayout)
        example_project = os.path.join(local_path, "example_models", "Package.aedb")
        self.target_path = os.path.join(self.local_scratch.path, "Package_test_41.aedb")
        self.local_scratch.copyfolder(example_project, self.target_path)

    def teardown_class(self):
        BasisTest.my_teardown(self)

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
        assert s1.thickness == "0.035mm"
        assert s1.material == "iron"
        assert s1.useetch is False
        assert s1.user is False
        assert s1.usp is False
        s1.material = "copper"
        s1.fillmaterial = "glass"
        s1.update_stackup_layer()
        assert s1.material == "copper"
        assert s1.fillmaterial == "glass"
        s1.useetch = True
        s1.etch = 1.2
        s1.user = True
        s1.usp = True
        s1.hfssSp["dt"] = 1
        s1.planaremSp["ifg"] = True
        s1.update_stackup_layer()
        assert s1.useetch is True
        assert s1.etch == 1.2
        assert s1.user is True
        assert s1.usp is True
        assert s1.hfssSp["dt"] == 1
        assert s1.planaremSp["ifg"] is True
        d1 = self.aedtapp.modeler.layers.add_layer(
            layername="Diel3", layertype="dielectric", thickness="1.0mm", elevation="0.035mm", material="plexiglass"
        )
        assert d1.material == "plexiglass"
        assert d1.thickness == "1.0mm"
        assert d1.transparency == 60
        d1.material = "fr4_epoxy"
        d1.transparency = 23
        d1.update_stackup_layer()
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
        assert s2.thickness == 3.5e-5
        assert s2.IsNegative is True
        s2.IsNegative = False
        s2.update_stackup_layer()
        assert s2.IsNegative is False

        self.aedtapp.modeler.layers.refresh_all_layers()
        s1 = self.aedtapp.modeler.layers.layers[self.aedtapp.modeler.layers.layer_id("Bottom")]
        assert s1.thickness == "0.035mm" or s1.thickness == 3.5e-5
        assert s1.material == "copper"
        assert s1.fillmaterial == "glass"
        assert s1.useetch is True
        assert s1.etch == 1.2
        assert s1.user is True
        assert s1.usp is True
        assert s1.hfssSp["dt"] == 1
        assert s1.planaremSp["ifg"] is True
        d1 = self.aedtapp.modeler.layers.layers[self.aedtapp.modeler.layers.layer_id("Diel3")]
        assert d1.material == "fr4_epoxy"
        assert d1.thickness == "1.0mm" or d1.thickness == 1e-3
        assert d1.transparency == 23
        s2 = self.aedtapp.modeler.layers.layers[self.aedtapp.modeler.layers.layer_id("Top")]
        assert s2.name == "Top"
        assert s2.type == "signal"
        assert s2.material == "copper"
        assert s2.thickness == 3.5e-5
        assert s2.IsNegative is False

        s1.useetch = False
        s1.user = False
        s1.usp = False
        s1.update_stackup_layer()

    def test_03_create_circle(self):
        n1 = self.aedtapp.modeler.create_circle("Top", 0, 5, 40, "mycircle")
        assert n1 == "mycircle"

    def test_04_create_create_rectangle(self):
        n2 = self.aedtapp.modeler.create_rectangle("Top", [0, 0], [6, 8], 3, 2, "myrectangle")
        assert n2 == "myrectangle"

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
        via = self.aedtapp.modeler.create_via("My_padstack2", x=0, y=0)
        assert type(via) is str
        via = self.aedtapp.modeler.create_via("My_padstack2", x=10, y=10, name="Via123", netname="VCC")
        assert via == "Via123"

    def test_12_create_line(self):
        line = self.aedtapp.modeler.create_line(
            "Bottom", [[0, 0], [10, 30], [20, 30]], lw=1, name="line1", netname="VCC"
        )
        assert line == "line1"

    def test_13a_create_edge_port(self):
        port_wave = self.aedtapp.create_edge_port("line1", 3, False, True, 6, 4, "2mm")
        assert port_wave
        assert self.aedtapp.delete_port(port_wave)
        assert self.aedtapp.create_edge_port("line1", 3, False)
        assert self.aedtapp.create_edge_port("line1", 0, True)
        assert len(self.aedtapp.excitations) > 0

    def test_14a_create_coaxial_port(self):
        assert self.aedtapp.create_coax_port("Via123", "Bottom", "Top", 10, 10, 10, 10)

    def test_14_create_setup(self):
        setup_name = "RFBoardSetup"
        setup = self.aedtapp.create_setup(setupname=setup_name)
        assert setup.name == self.aedtapp.existing_analysis_setups[0]
        assert setup.solver_type == "HFSS"

    def test_15_edit_setup(self):
        setup_name = "RFBoardSetup2"
        setup2 = self.aedtapp.create_setup(setupname=setup_name)
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
        assert sweep.add_subrange("SinglePoint", 10.1e-1, "GHz")
        assert sweep.add_subrange("SinglePoint", 10.2e-1, "GHz")
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
        exception_raised = False
        try:
            sweep_raising_error = self.aedtapp.create_linear_step_sweep(
                setupname=setup_name,
                unit="GHz",
                freqstart=1,
                freqstop=10,
                step_size=0.12,
                sweepname="RFBoardSweep4",
                sweep_type="Incorrect",
                save_fields=True,
            )
        except AttributeError as e:
            exception_raised = True
            assert (
                e.args[0] == "Invalid value for `sweep_type`. The value must be 'Discrete', 'Interpolating', or 'Fast'."
            )
        assert exception_raised

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

        try:
            sweep7 = self.aedtapp.create_single_point_sweep(
                setupname=setup_name,
                unit="GHz",
                freq=[],
                sweepname="RFBoardSingle",
                save_fields=False,
            )
        except AttributeError as e:
            exception_raised = True
            assert e.args[0] == "Frequency list is empty. Specify at least one frequency point."
        assert exception_raised

    def test_18d_delete_setup(self):
        setup_name = "SetupToDelete"
        setuptd = self.aedtapp.create_setup(setupname=setup_name)
        assert setuptd.name in self.aedtapp.existing_analysis_setups
        self.aedtapp.delete_setup(setup_name)
        assert setuptd.name not in self.aedtapp.existing_analysis_setups

    def test_19A_validate(self):
        assert self.aedtapp.validate_full_design()
        self.aedtapp.delete_port("Port3")
        assert self.aedtapp.validate_full_design(ports=3)

    def test_19B_analyze_setup(self):
        self.aedtapp.save_project()
        assert self.aedtapp.analyze_setup("RFBoardSetup3")
        self.aedtapp.save_project()
        assert os.path.exists(self.aedtapp.export_profile("RFBoardSetup3"))
        assert os.path.exists(self.aedtapp.export_mesh_stats("RFBoardSetup3"))

    @pytest.mark.skipif(os.name == "posix", reason="To be investigated on linux.")
    def test_19C_export_touchsthone(self):
        filename = os.path.join(scratch_path, "touchstone.s2p")
        solution_name = "RFBoardSetup3"
        sweep_name = "Last Adaptive"
        assert self.aedtapp.export_touchstone(solution_name, sweep_name, filename)
        assert os.path.exists(filename)
        assert self.aedtapp.export_touchstone(solution_name)
        sweep_name = None
        assert self.aedtapp.export_touchstone(solution_name, sweep_name)

    def test_19D_export_to_hfss(self):
        with Scratch(scratch_path) as local_scratch:
            filename = "export_to_hfss_test"
            file_fullname = os.path.join(local_scratch.path, filename)
            setup = self.aedtapp.get_setup(self.aedtapp.existing_analysis_setups[0])
            assert setup.export_to_hfss(file_fullname=file_fullname)
            time.sleep(2)  # wait for the export operation to finish

    def test_19_E_export_results(self):
        files = self.aedtapp.export_results()
        assert len(files) > 0

    def test_20_set_export_touchstone(self):
        assert self.aedtapp.set_export_touchstone(True)
        assert self.aedtapp.set_export_touchstone(False)

    def test_21_variables(self):
        assert isinstance(self.aedtapp.available_variations.nominal_w_values_dict, dict)
        assert isinstance(self.aedtapp.available_variations.nominal_w_values, list)

    def test_21_get_all_sparameter_list(self):
        assert self.aedtapp.get_all_sparameter_list == ["S(Port1,Port1)", "S(Port1,Port2)", "S(Port2,Port2)"]

    def test_22_get_all_return_loss_list(self):
        assert self.aedtapp.get_all_return_loss_list() == ["S(Port1,Port1)", "S(Port2,Port2)"]

    def test_23_get_all_insertion_loss_list(self):
        assert self.aedtapp.get_all_insertion_loss_list() == ["S(Port1,Port1)", "S(Port2,Port2)"]

    def test_24_get_next_xtalk_list(self):
        assert self.aedtapp.get_next_xtalk_list() == ["S(Port1,Port2)"]

    def test_25_get_fext_xtalk_list(self):
        assert self.aedtapp.get_fext_xtalk_list() == ["S(Port1,Port2)", "S(Port2,Port1)"]

    def test_26_duplicate(self):
        assert self.aedtapp.modeler.duplicate("myrectangle", 2, [1, 1])

    def test_27_create_pin_port(self):
        assert self.aedtapp.create_pin_port("PinPort1")

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
        output = self.aedtapp.export_3d_model()
        assert os.path.exists(output)

    def test_36_import_gds(self):
        gds_file = os.path.join(local_path, "example_models", "cad", "GDS", "gds1.gds")
        control_file = ""
        aedb_file = os.path.join(self.local_scratch.path, "gds_out.aedb")
        assert self.aedtapp.import_gds(gds_file, aedb_path=aedb_file, control_file=control_file)
        assert self.aedtapp.import_gds(gds_file, aedb_path=aedb_file, control_file=control_file)

    @pytest.mark.skipif(os.name == "posix", reason="Failing on linux")
    def test_37_import_gerber(self):
        gerber_file = os.path.join(local_path, "example_models", "cad", "Gerber", "gerber1.zip")
        control_file = os.path.join(local_path, "example_models", "cad", "Gerber", "gerber1.xml")
        aedb_file = os.path.join(self.local_scratch.path, "gerber_out.aedb")
        assert self.aedtapp.import_gerber(gerber_file, aedb_path=aedb_file, control_file=control_file)

    def test_38_import_dxf(self):
        dxf_file = os.path.join(local_path, "example_models", "cad", "DXF", "dxf1.dxf")
        control_file = os.path.join(local_path, "example_models", "cad", "DXF", "dxf1.xml")
        aedb_file = os.path.join(self.local_scratch.path, "dxf_out.aedb")
        assert self.aedtapp.import_gerber(dxf_file, aedb_path=aedb_file, control_file=control_file)

    def test_39_import_ipc(self):
        dxf_file = os.path.join(local_path, "example_models", "cad", "ipc", "galileo.xml")
        aedb_file = os.path.join(self.local_scratch.path, "dxf_out.aedb")
        assert self.aedtapp.import_ipc2581(dxf_file, aedb_path=aedb_file, control_file="")

    @pytest.mark.skipif(config["desktopVersion"] < "2022.2", reason="Not working on AEDT 22R1")
    def test_40_test_flex(self):
        assert self.flex.enable_rigid_flex()
        pass

    @pytest.mark.skipif(os.name == "posix", reason="Bug on linux")
    def test_90_set_differential_pairs(self):
        assert self.hfss3dl.set_differential_pair(
            positive_terminal="Port3",
            negative_terminal="Port4",
            common_name=None,
            diff_name=None,
            common_ref_z=34,
            diff_ref_z=123,
            active=True,
            matched=False,
        )
        assert self.hfss3dl.set_differential_pair(positive_terminal="Port3", negative_terminal="Port5")

    @pytest.mark.skipif(os.name == "posix", reason="Bug on linux")
    def test_91_load_and_save_diff_pair_file(self):
        diff_def_file = os.path.join(local_path, "example_models", "differential_pairs_definition.txt")
        diff_file = self.local_scratch.copyfile(diff_def_file)
        assert self.hfss3dl.load_diff_pairs_from_file(diff_file)

        diff_file2 = os.path.join(self.local_scratch.path, "diff_file2.txt")
        assert self.hfss3dl.save_diff_pairs_to_file(diff_file2)
        with open(diff_file2, "r") as fh:
            lines = fh.read().splitlines()
        assert len(lines) == 3

    @pytest.mark.skipif(is_ironpython, reason="Crash on Ironpython")
    def test_92_import_edb(self):
        assert self.aedtapp.import_edb(self.target_path)

    @pytest.mark.skipif(config["desktopVersion"] < "2022.2", reason="Not Working on Version earlier than 2022R2.")
    def test_93_clip_plane(self):
        assert self.aedtapp.modeler.clip_plane("CS1")

    def test_94_edit_3dlayout_extents(self):
        assert self.aedtapp.edit_hfss_extents(
            diel_extent_type="ConformalExtent",
            diel_extent_horizontal_padding="1mm",
            air_extent_type="ConformalExtent",
            air_vertical_positive_padding="10mm",
            air_vertical_negative_padding="10mm",
        )
