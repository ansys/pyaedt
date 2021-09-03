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
source_project = os.path.join(local_path, 'example_models', src_project_name + '.aedt')
linked_project_name = "Filter_Board"

class TestClass:

    def setup_class(self):
        # set a scratch directory and the environment / test data
        with Scratch(scratch_path) as self.local_scratch:
            try:
                time.sleep(2)
                example_project = os.path.join(
                    local_path, 'example_models', test_project_name + '.aedt')
                source_project = os.path.join(
                    local_path, 'example_models', src_project_name + '.aedt')
                linked_project = os.path.join(
                    local_path, 'example_models', linked_project_name + '.aedt')

                self.test_project = self.local_scratch.copyfile(example_project)
                self.test_src_project = self.local_scratch.copyfile(source_project)
                self.test_lkd_project = self.local_scratch.copyfile(linked_project)
                self.local_scratch.copyfolder(os.path.join(local_path, 'example_models', test_project_name + '.aedb'),
                                              os.path.join(self.local_scratch.path, test_project_name + '.aedb'))
                self.local_scratch.copyfolder(os.path.join(local_path, 'example_models', linked_project_name + '.aedb'),
                                              os.path.join(self.local_scratch.path, linked_project_name + '.aedb'))
                temp = open(example_project, 'rb').read().splitlines()

                outf = open(os.path.join(self.local_scratch.path, test_project_name+".aedt"), 'wb')
                found = False
                for line in temp:
                    if not found:
                        if 'Filter_Board.aedt' in line.decode('utf-8'):
                            line = '\t\t\t\tfilename=\'{}/Filter_Board.aedt\'\n'.format(
                                self.local_scratch.path.replace("\\","/")).encode()
                            found = True
                    outf.write(line+b"\n")
                outf.close()
                self.aedtapp = Circuit(self.test_project)
            except:
                pass

    def teardown_class(self):
        for proj in self.aedtapp.project_list:
            try:
                self.aedtapp.close_project(proj, saveproject=False)
            except:
                pass
        self.local_scratch.remove()
        gc.collect()

    def test_01_save(self):
        assert os.path.exists(self.aedtapp.project_path)

    @pytest.mark.skipif(config.get("skip_circuits", False),
                        reason="Skipped because Desktop is crashing")
    def test_02_add_subcircuits(self):
        source_project_path = os.path.join(self.local_scratch.path, src_project_name + '.aedt')
        layout_design = "Galileo_G87173_205_cutout3"
        pin_names = self.aedtapp.get_source_pin_names(
            src_design_name,src_project_name, source_project_path,  3)
        hfss3Dlayout_comp_id, hfss3Dlayout_comp = self.aedtapp.modeler.components.create_3dlayout_subcircuit(
            layout_design)
        hfss_comp_id, hfss_comp = self.aedtapp.modeler.components.add_subcircuit_hfss_link(
            "uUSB", pin_names, source_project_path, src_project_name, src_design_name)

        self.aedtapp.modeler.components.refresh_dynamic_link("uUSB")
        self.aedtapp.modeler.components.set_sim_option_on_hfss_subcircuit(hfss_comp)
        self.aedtapp.modeler.components.set_sim_solution_on_hfss_subcircuit(hfss_comp)
        #self.aedtapp.modeler.components.refresh_dynamic_link("Galileo_G87173_205_cutout3")

        #hfssComp = self.aedtapp.modeler.components.components[hfss_comp_id]
        #hfssComp.set_location("-3000mil","0mil")

        hfssComp_pins = self.aedtapp.modeler.components.get_pins(hfss_comp_id)
        hfss_pin2location = { }
        for pin in hfssComp_pins:
            hfss_pin2location[pin] = self.aedtapp.modeler.components.get_pin_location(
                hfss_comp_id, pin)

        hfss3DlayoutComp_pins = self.aedtapp.modeler.components.get_pins(hfss3Dlayout_comp_id)
        hfss3Dlayout_pin2location = { }
        for pin in hfss3DlayoutComp_pins:
            hfss3Dlayout_pin2location[pin] = self.aedtapp.modeler.components.get_pin_location(
                hfss3Dlayout_comp_id, pin)

        # Link 1 Creation
        self.aedtapp.modeler.components.create_page_port(
            "Link1", hfss_pin2location["usb_N_conn"][0], hfss_pin2location["usb_N_conn"][1], 180)
        self.aedtapp.modeler.components.create_page_port("Link1", hfss3Dlayout_pin2location["J3B2.3.USBH2_DP_CH"][0],
                                                         hfss3Dlayout_pin2location["J3B2.3.USBH2_DP_CH"][1], 180)

        # Link 2 Creation
        self.aedtapp.modeler.components.create_page_port("Link2", hfss_pin2location["usb_N_pcb"][0],
                                                         hfss_pin2location["usb_N_pcb"][1], 180)
        self.aedtapp.modeler.components.create_page_port("Link2", hfss3Dlayout_pin2location["L3M1.3.USBH2_DN_CH"][0],
                                                         hfss3Dlayout_pin2location["L3M1.3.USBH2_DN_CH"][1], 180)

        # Ports Creation
        self.aedtapp.modeler.components.create_iport(
            "Excitation_1", hfss_pin2location["USB_VCC_T1"][0], hfss_pin2location["USB_VCC_T1"][1])
        self.aedtapp.modeler.components.create_iport("Excitation_2", hfss_pin2location["usb_P_pcb"][0],
                                                     hfss_pin2location["usb_P_pcb"][1])
        self.aedtapp.modeler.components.create_iport("Port_1", hfss3Dlayout_pin2location["L3M1.2.USBH2_DP_CH"][0],
                                                         hfss3Dlayout_pin2location["L3M1.2.USBH2_DP_CH"][1])
        self.aedtapp.modeler.components.create_iport("Port_2", hfss3Dlayout_pin2location["J3B2.2.USBH2_DN_CH"][0],
                                                         hfss3Dlayout_pin2location["J3B2.2.USBH2_DN_CH"][1])

        pass

    @pytest.mark.skipif(config.get("skip_circuits", False),
                        reason="Skipped because Desktop is crashing")
    def test_03_assign_excitations(self):
        excitation_settings = ["1 V", "0deg", "0V", "25V", "1V", "2.5GHz", "0s", "0", "0deg", "0Hz"]
        ports_list = ["Excitation_1", "Excitation_2"]
        self.aedtapp.modeler.components.assign_sin_excitation2ports(ports_list, excitation_settings)

        pass

    @pytest.mark.skipif(config.get("skip_circuits", False),
                        reason="Skipped because Desktop is crashing")
    def test_04_setup(self):
        setup_name = "Dom_LNA"
        LNA_setup = self.aedtapp.create_setup(setup_name)
        sweep_list = ["LINC", "1GHz", "2GHz", "1001"]
        LNA_setup.props["SweepDefinition"]["Data"] = " ".join(sweep_list)
        assert LNA_setup.update()
