import os

from _unittest.conftest import config
from _unittest.conftest import local_path
import pytest

from pyaedt import Circuit
from pyaedt import Q2d
from pyaedt import Q3d
from pyaedt import is_ironpython
from pyaedt.generic.general_methods import is_linux

test_subfloder = "T22"
test_project_name = "Dynamic_Link"
src_design_name = "uUSB"
if config["desktopVersion"] > "2022.2":
    src_project_name = "USB_Connector_231"
    linked_project_name = "Filter_Board_231"
else:
    src_project_name = "USB_Connector"
    linked_project_name = "Filter_Board"


@pytest.fixture(scope="class")
def aedtapp(add_app, local_scratch):
    example_project = os.path.join(local_path, "example_models", test_subfloder, test_project_name + ".aedt")
    test_project = local_scratch.copyfile(example_project)
    local_scratch.copyfolder(
        os.path.join(local_path, "example_models", test_subfloder, test_project_name + ".aedb"),
        os.path.join(local_scratch.path, test_project_name + ".aedb"),
    )

    linked_project = os.path.join(local_path, "example_models", test_subfloder, linked_project_name + ".aedt")
    test_lkd_project = local_scratch.copyfile(linked_project)
    local_scratch.copyfolder(
        os.path.join(local_path, "example_models", test_subfloder, linked_project_name + ".aedb"),
        os.path.join(local_scratch.path, linked_project_name + ".aedb"),
    )

    with open(example_project, "rb") as fh:
        temp = fh.read().splitlines()

    with open(test_project, "wb") as outf:
        found = False
        for line in temp:
            if not found:
                if "Filter_Board.aedt" in line.decode("utf-8"):
                    line = "\t\t\t\tfilename='{}'\n".format(test_lkd_project.replace("\\", "/")).encode()
                    found = True
            outf.write(line + b"\n")

    app = add_app(application=Circuit, project_name=test_project, just_open=True)
    return app


@pytest.fixture(scope="class", autouse=True)
def examples(local_scratch):
    source_project = os.path.join(local_path, "example_models", test_subfloder, src_project_name + ".aedt")
    src_project_file = local_scratch.copyfile(source_project)
    q3d = local_scratch.copyfile(os.path.join(local_path, "example_models", test_subfloder, "q2d_q3d.aedt"))
    return src_project_file, q3d


class TestClass:
    @pytest.fixture(autouse=True)
    def init(self, aedtapp, local_scratch, examples):
        self.aedtapp = aedtapp
        self.local_scratch = local_scratch
        self.src_project_file = examples[0]
        self.q3d = examples[1]

    def test_01_save(self):
        assert os.path.exists(self.aedtapp.project_path)

    @pytest.mark.skipif(
        is_ironpython or config.get("skip_circuits", False), reason="Skipped because Desktop is crashing"
    )
    def test_02_add_subcircuits_3dlayout(self):
        layout_design = "Galileo_G87173_205_cutout3"
        hfss3Dlayout_comp = self.aedtapp.modeler.schematic.add_subcircuit_3dlayout(layout_design)
        assert hfss3Dlayout_comp.id == 86
        assert hfss3Dlayout_comp

    @pytest.mark.skipif(is_ironpython or is_linux, reason="Skipped because Desktop is crashing")
    def test_03_add_subcircuits_hfss_link(self, add_app):
        pin_names = self.aedtapp.get_source_pin_names(src_design_name, src_project_name, self.src_project_file, 2)

        assert len(pin_names) == 4
        assert "usb_P_pcb" in pin_names
        hfss = add_app(project_name=self.src_project_file, design_name="uUSB", just_open=True)
        hfss_comp = self.aedtapp.modeler.schematic.add_subcircuit_dynamic_link(hfss, comp_name="uUSB")
        assert hfss_comp.id == 87
        assert hfss_comp.composed_name == "CompInst@uUSB;87;3"

    @pytest.mark.skipif(is_ironpython or is_linux, reason="Skipped because Desktop is crashing")
    def test_04_refresh_dynamic_link(self):
        assert self.aedtapp.modeler.schematic.refresh_dynamic_link("uUSB")

    @pytest.mark.skipif(is_ironpython or is_linux, reason="Skipped because Desktop is crashing")
    def test_05_set_sim_option_on_hfss_subcircuit(self):
        hfss_comp = "CompInst@uUSB;87;3"
        assert self.aedtapp.modeler.schematic.set_sim_option_on_hfss_subcircuit(hfss_comp)
        assert self.aedtapp.modeler.schematic.set_sim_option_on_hfss_subcircuit(hfss_comp, option="interpolate")
        assert not self.aedtapp.modeler.schematic.set_sim_option_on_hfss_subcircuit(hfss_comp, option="not_good")

    @pytest.mark.skipif(is_linux or is_ironpython, reason="Skipped because Desktop is crashing")
    def test_06_set_sim_solution_on_hfss_subcircuit(self):
        hfss_comp = "CompInst@uUSB;87;3"
        assert self.aedtapp.modeler.schematic.set_sim_solution_on_hfss_subcircuit(hfss_comp)

    @pytest.mark.skipif(is_ironpython or is_linux, reason="Skipped because Desktop is crashing")
    def test_07_create_page_port_and_interface_port(self):
        hfss_comp_id = 87
        hfss3Dlayout_comp_id = 86
        hfssComp_pins = self.aedtapp.modeler.schematic.get_pins(hfss_comp_id)
        assert type(hfssComp_pins) is list
        assert len(hfssComp_pins) == 4
        hfss_pin2location = {}
        for pin in hfssComp_pins:
            hfss_pin2location[pin] = self.aedtapp.modeler.schematic.get_pin_location(hfss_comp_id, pin)
            assert len(hfss_pin2location[pin]) == 2

        hfss3DlayoutComp_pins = self.aedtapp.modeler.schematic.get_pins(hfss3Dlayout_comp_id)
        assert type(hfssComp_pins) is list
        assert len(hfssComp_pins) == 4
        hfss3Dlayout_pin2location = {}
        for pin in hfss3DlayoutComp_pins:
            hfss3Dlayout_pin2location[pin] = self.aedtapp.modeler.schematic.get_pin_location(hfss3Dlayout_comp_id, pin)
            assert len(hfss3Dlayout_pin2location[pin]) == 2

        # Link 1 Creation
        portname = self.aedtapp.modeler.schematic.create_page_port(
            "Link1", [hfss_pin2location["usb_N_conn"][0], hfss_pin2location["usb_N_conn"][1]], 180
        )
        assert "Link1" in portname.composed_name
        portname = self.aedtapp.modeler.schematic.create_page_port(
            "Link1",
            [hfss3Dlayout_pin2location["J3B2.3.USBH2_DP_CH"][0], hfss3Dlayout_pin2location["J3B2.3.USBH2_DP_CH"][1]],
            180,
        )
        assert "Link1" in portname.composed_name

        # Link 2 Creation
        portname = self.aedtapp.modeler.schematic.create_page_port(
            "Link2", [hfss_pin2location["usb_N_pcb"][0], hfss_pin2location["usb_N_pcb"][1]], 180
        )
        assert "Link2" in portname.composed_name
        portname = self.aedtapp.modeler.schematic.create_page_port(
            "Link2",
            [hfss3Dlayout_pin2location["L3M1.3.USBH2_DN_CH"][0], hfss3Dlayout_pin2location["L3M1.3.USBH2_DN_CH"][1]],
            180,
        )
        assert "Link2" in portname.composed_name

        # Ports Creation
        portname = self.aedtapp.modeler.schematic.create_interface_port(
            "Excitation_1", [hfss_pin2location["USB_VCC_T1"][0], hfss_pin2location["USB_VCC_T1"][1]]
        )
        assert "Excitation_1" in portname.name
        portname = self.aedtapp.modeler.schematic.create_interface_port(
            "Excitation_2", [hfss_pin2location["usb_P_pcb"][0], hfss_pin2location["usb_P_pcb"][1]]
        )
        assert "Excitation_2" in portname.name
        portname = self.aedtapp.modeler.schematic.create_interface_port(
            "Port_1",
            [hfss3Dlayout_pin2location["L3M1.2.USBH2_DP_CH"][0], hfss3Dlayout_pin2location["L3M1.2.USBH2_DP_CH"][1]],
        )
        assert "Port_1" in portname.name
        portname = self.aedtapp.modeler.schematic.create_interface_port(
            "Port_2",
            [hfss3Dlayout_pin2location["J3B2.2.USBH2_DN_CH"][0], hfss3Dlayout_pin2location["J3B2.2.USBH2_DN_CH"][1]],
        )
        assert "Port_2" in portname.name

        portname = self.aedtapp.modeler.schematic.create_interface_port(
            "Port_remove",
            [hfss3Dlayout_pin2location["J3B2.2.USBH2_DN_CH"][0], hfss3Dlayout_pin2location["J3B2.2.USBH2_DN_CH"][1]],
        )
        self.aedtapp.excitations[portname.name].delete()

        assert "Port_remove" not in self.aedtapp.excitation_names

    @pytest.mark.skipif(is_ironpython or is_linux, reason="Skipped because Desktop is crashing")
    def test_08_assign_excitations(self):
        filepath = os.path.join(local_path, "example_models", test_subfloder, "frequency_dependent_source.fds")
        ports_list = ["Excitation_1", "Excitation_2"]
        assert self.aedtapp.assign_voltage_frequency_dependent_excitation_to_ports(ports_list, filepath)

        filepath = os.path.join(local_path, "example_models", test_subfloder, "frequency_dependent_source1.fds")
        ports_list = ["Excitation_1", "Excitation_2"]
        assert not self.aedtapp.assign_voltage_frequency_dependent_excitation_to_ports(ports_list, filepath)

        filepath = os.path.join(local_path, "example_models", test_subfloder, "frequency_dependent_source.fds")
        ports_list = ["Excitation_1", "Excitation_3"]
        assert not self.aedtapp.assign_voltage_frequency_dependent_excitation_to_ports(ports_list, filepath)

        ports_list = ["Excitation_1"]
        assert self.aedtapp.assign_voltage_sinusoidal_excitation_to_ports(ports_list)

    @pytest.mark.skipif(config.get("skip_circuits", False), reason="Skipped because Desktop is crashing")
    def test_09_setup(self):
        setup_name = "Dom_LNA"
        LNA_setup = self.aedtapp.create_setup(setup_name)
        sweep_list = ["LINC", "1GHz", "2GHz", "1001"]
        LNA_setup.props["SweepDefinition"]["Data"] = " ".join(sweep_list)
        assert LNA_setup.update()

    @pytest.mark.skipif(is_ironpython or is_linux, reason="Skipped because Desktop is crashing")
    def test_10_q2d_link(self, add_app):
        self.aedtapp.insert_design("test_link")
        q2d = add_app(application=Q2d, project_name=self.q3d, just_open=True)
        c1 = self.aedtapp.modeler.schematic.add_subcircuit_dynamic_link(q2d, extrusion_length=25)
        assert c1
        assert len(c1.pins) == 6
        assert c1.parameters["Length"] == "25mm"
        assert c1.parameters["r1"] == "0.3mm"

    @pytest.mark.skipif(is_ironpython or is_linux, reason="Skipped because Desktop is crashing")
    def test_10_q3d_link(self, add_app):
        q3d = add_app(application=Q3d, project_name=self.q3d, just_open=True)

        q3d_comp = self.aedtapp.modeler.schematic.add_subcircuit_dynamic_link(
            q3d, solution_name="Setup1 : LastAdaptive"
        )
        assert q3d_comp
        assert len(q3d_comp.pins) == 4

    @pytest.mark.skipif(is_ironpython or is_linux, reason="Skipped because Desktop is crashing")
    def test_10_hfss_link(self, add_app):
        hfss = add_app(project_name=self.q3d, just_open=True)

        hfss_comp = self.aedtapp.modeler.schematic.add_subcircuit_dynamic_link(hfss, solution_name="Setup1 : Sweep")
        assert hfss_comp
        assert len(hfss_comp.pins) == 2
        hfss2 = add_app(project_name=self.q3d, just_open=True)
        assert self.aedtapp.modeler.schematic.add_subcircuit_dynamic_link(
            hfss2, solution_name="Setup2 : Sweep", tline_port="1"
        )

    @pytest.mark.skipif(is_ironpython or is_linux, reason="Skipped because Desktop is crashing")
    def test_11_siwave_link(self):
        model = os.path.join(local_path, "example_models", test_subfloder, "Galileo_um.siw")
        model_out = self.local_scratch.copyfile(model)
        self.local_scratch.copyfolder(
            model + "averesults", os.path.join(self.local_scratch.path, "Galileo_um.siwaveresults")
        )
        siw_comp = self.aedtapp.modeler.schematic.add_siwave_dynamic_link(model_out)
        assert siw_comp
        assert len(siw_comp.pins) == 2

    @pytest.mark.skipif(config.get("skip_circuits", False) or is_linux, reason="Skipped because Desktop is crashing")
    def test_12_create_interface_port(self):
        page_port = self.aedtapp.modeler.components.create_page_port(name="Port12", location=[0, -0.50])
        interface_port = self.aedtapp.modeler.components.create_interface_port(name="Port12", location=[0.3, -0.50])
        second_page_port = self.aedtapp.modeler.components.create_page_port(name="Port12", location=[0.45, -0.5])
        second_interface_port = self.aedtapp.modeler.components.create_interface_port(
            name="Port122", location=[0.6, -0.50]
        )
        assert not self.aedtapp.modeler.components.create_interface_port(name="Port122", location=[0.6, -0.50])
        assert page_port.composed_name != second_page_port.composed_name
        assert page_port.composed_name != interface_port.name
        assert page_port.composed_name != second_interface_port.name
        assert interface_port.name != second_interface_port.name
