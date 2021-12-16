# standard imports
import os
from _unittest.conftest import local_path, scratch_path, config

from pyaedt import Circuit
from pyaedt.generic.filesystem import Scratch
import gc

try:
    import pytest
except ImportError:
    import _unittest_ironpython.conf_unittest as pytest
import time

# Access the desktop
test_project_name = "Dynamic_Link"
src_design_name = "uUSB"
src_project_name = "USB_Connector"
source_project = os.path.join(local_path, "example_models", src_project_name + ".aedt")
linked_project_name = "Filter_Board"


class TestClass:
    def setup_class(self):
        # set a scratch directory and the environment / test data
        with Scratch(scratch_path) as self.local_scratch:
            try:
                time.sleep(2)
                example_project = os.path.join(local_path, "example_models", test_project_name + ".aedt")
                source_project = os.path.join(local_path, "example_models", src_project_name + ".aedt")
                linked_project = os.path.join(local_path, "example_models", linked_project_name + ".aedt")

                self.test_project = self.local_scratch.copyfile(example_project)
                self.test_src_project = self.local_scratch.copyfile(source_project)
                self.test_lkd_project = self.local_scratch.copyfile(linked_project)
                self.local_scratch.copyfolder(
                    os.path.join(local_path, "example_models", test_project_name + ".aedb"),
                    os.path.join(self.local_scratch.path, test_project_name + ".aedb"),
                )
                self.local_scratch.copyfolder(
                    os.path.join(local_path, "example_models", linked_project_name + ".aedb"),
                    os.path.join(self.local_scratch.path, linked_project_name + ".aedb"),
                )
                temp = open(example_project, "rb").read().splitlines()

                outf = open(os.path.join(self.local_scratch.path, test_project_name + ".aedt"), "wb")
                found = False
                for line in temp:
                    if not found:
                        if "Filter_Board.aedt" in line.decode("utf-8"):
                            line = "\t\t\t\tfilename='{}/Filter_Board.aedt'\n".format(
                                self.local_scratch.path.replace("\\", "/")
                            ).encode()
                            found = True
                    outf.write(line + b"\n")
                outf.close()
                self.aedtapp = Circuit(self.test_project)
            except:
                pass

    def teardown_class(self):
        self.aedtapp._desktop.ClearMessages("", "", 3)
        for proj in self.aedtapp.project_list:
            try:
                self.aedtapp.close_project(proj, False)
            except:
                pass
        self.local_scratch.remove()
        gc.collect()

    def test_01_save(self):
        assert os.path.exists(self.aedtapp.project_path)

    @pytest.mark.skipif(config.get("skip_circuits", False), reason="Skipped because Desktop is crashing")
    def test_02_add_subcircuits_3dlayout(self):
        layout_design = "Galileo_G87173_205_cutout3"
        hfss3Dlayout_comp = self.aedtapp.modeler.schematic.add_subcircuit_3dlayout(layout_design)
        assert hfss3Dlayout_comp.id == 86
        assert hfss3Dlayout_comp

    @pytest.mark.skipif(config.get("skip_circuits", False), reason="Skipped because Desktop is crashing")
    def test_03_add_subcircuits_hfss_link(self):
        source_project_path = os.path.join(self.local_scratch.path, src_project_name + ".aedt")
        pin_names = self.aedtapp.get_source_pin_names(src_design_name, src_project_name, source_project_path, 2)

        assert len(pin_names) == 4
        assert "usb_P_pcb" in pin_names

        hfss_comp = self.aedtapp.modeler.schematic.add_subcircuit_hfss_link(
            "uUSB", pin_names, source_project_path, src_design_name
        )
        assert hfss_comp.id == 87
        assert hfss_comp.composed_name == "CompInst@uUSB;87;3"

    @pytest.mark.skipif(config.get("skip_circuits", False), reason="Skipped because Desktop is crashing")
    def test_04_refresh_dynamic_link(self):
        assert self.aedtapp.modeler.schematic.refresh_dynamic_link("uUSB")

    @pytest.mark.skipif(config.get("skip_circuits", False), reason="Skipped because Desktop is crashing")
    def test_05_set_sim_option_on_hfss_subcircuit(self):
        hfss_comp = "CompInst@uUSB;87;3"
        assert self.aedtapp.modeler.schematic.set_sim_option_on_hfss_subcircuit(hfss_comp)
        assert self.aedtapp.modeler.schematic.set_sim_option_on_hfss_subcircuit(hfss_comp, option="interpolate")
        assert not self.aedtapp.modeler.schematic.set_sim_option_on_hfss_subcircuit(hfss_comp, option="not_good")

    @pytest.mark.skipif(config.get("skip_circuits", False), reason="Skipped because Desktop is crashing")
    def test_06_set_sim_solution_on_hfss_subcircuit(self):
        hfss_comp = "CompInst@uUSB;87;3"
        assert self.aedtapp.modeler.schematic.set_sim_solution_on_hfss_subcircuit(hfss_comp)

    @pytest.mark.skipif(config.get("skip_circuits", False), reason="Skipped because Desktop is crashing")
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
        assert "Excitation_1" in portname.composed_name
        portname = self.aedtapp.modeler.schematic.create_interface_port(
            "Excitation_2", [hfss_pin2location["usb_P_pcb"][0], hfss_pin2location["usb_P_pcb"][1]]
        )
        assert "Excitation_2" in portname.composed_name
        portname = self.aedtapp.modeler.schematic.create_interface_port(
            "Port_1",
            [hfss3Dlayout_pin2location["L3M1.2.USBH2_DP_CH"][0], hfss3Dlayout_pin2location["L3M1.2.USBH2_DP_CH"][1]],
        )
        assert "Port_1" in portname.composed_name
        portname = self.aedtapp.modeler.schematic.create_interface_port(
            "Port_2",
            [hfss3Dlayout_pin2location["J3B2.2.USBH2_DN_CH"][0], hfss3Dlayout_pin2location["J3B2.2.USBH2_DN_CH"][1]],
        )
        assert "Port_2" in portname.composed_name

    @pytest.mark.skipif(config.get("skip_circuits", False), reason="Skipped because Desktop is crashing")
    def test_08_assign_excitations(self):
        excitation_settings = ["1 V", "0deg", "0V", "25V", "1V", "2.5GHz", "0s", "0", "0deg", "0Hz"]
        ports_list = ["Excitation_1", "Excitation_2"]
        assert self.aedtapp.assign_voltage_sinusoidal_excitation_to_ports(ports_list, excitation_settings)

    @pytest.mark.skipif(config.get("skip_circuits", False), reason="Skipped because Desktop is crashing")
    def test_09_setup(self):
        setup_name = "Dom_LNA"
        LNA_setup = self.aedtapp.create_setup(setup_name)
        sweep_list = ["LINC", "1GHz", "2GHz", "1001"]
        LNA_setup.props["SweepDefinition"]["Data"] = " ".join(sweep_list)
        assert LNA_setup.update()
