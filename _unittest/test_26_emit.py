# Import required modules
from _unittest.conftest import BasisTest
from _unittest.conftest import config
from _unittest.conftest import is_ironpython
from pyaedt import Emit
from pyaedt.emit import Result
from pyaedt.modeler.PrimitivesEmit import EmitAntennaComponent
from pyaedt.modeler.PrimitivesEmit import EmitComponent
from pyaedt.modeler.PrimitivesEmit import EmitComponents
import os
try:
    import pytest
except ImportError:
    import _unittest_ironpython.conf_unittest as pytest

test_subfolder = "T26"


class TestClass(BasisTest, object):
    def setup_class(self):
        BasisTest.my_setup(self)
        self.aedtapp = BasisTest.add_app(self, application=Emit)
        self.aedtapp2 = BasisTest.add_app(self, application=Emit)

    def teardown_class(self):
        BasisTest.my_teardown(self)

    def test_objects(self):
        assert self.aedtapp.solution_type
        assert isinstance(self.aedtapp.existing_analysis_setups, list)
        assert isinstance(self.aedtapp.setup_names, list)
        assert isinstance(self.aedtapp.modeler.components, EmitComponents)
        assert self.aedtapp.modeler
        assert self.aedtapp.oanalysis is None

    @pytest.mark.skipif(
        config["desktopVersion"] <= "2022.1" or is_ironpython, reason="Skipped on versions lower than 2021.2"
    )
    def test_create_components(self):
        radio = self.aedtapp.modeler.components.create_component("New Radio", "TestRadio")
        assert radio.name == "TestRadio"
        assert isinstance(radio, EmitComponent)
        antenna = self.aedtapp.modeler.components.create_component("Antenna", "TestAntenna")
        assert antenna.name == "TestAntenna"
        assert isinstance(antenna, EmitAntennaComponent)

    @pytest.mark.skipif(
        config["desktopVersion"] <= "2022.1" or is_ironpython, reason="Skipped on versions lower than 2021.2"
    )
    def test_connect_components(self):
        radio = self.aedtapp.modeler.components.create_component("New Radio")
        antenna = self.aedtapp.modeler.components.create_component("Antenna")
        antenna.move_and_connect_to(radio)
        antenna_port = antenna.port_names()[0]  # antennas have 1 port
        radio_port = radio.port_names()[0]  # radios have 1 port
        connected_comp, connected_port = antenna.port_connection(antenna_port)
        assert connected_comp == radio.name
        assert connected_port == radio_port
        # Test get_connected_components()
        connected_components_list = radio.get_connected_components()
        assert antenna in connected_components_list
        # Verify None,None is returned for an unconnected port
        radio2 = self.aedtapp.modeler.components.create_component("New Radio")
        radio2_port = radio2.port_names()[0]
        connected_comp, connected_port = radio2.port_connection(radio2_port)
        assert connected_comp is None
        assert connected_port is None

    @pytest.mark.skipif(
        config["desktopVersion"] <= "2022.1" or is_ironpython, reason="Skipped on versions earlier than 2022 R2."
    )
    def test_radio_component(self):
        radio = self.aedtapp.modeler.components.create_component("New Radio")
        # default radio has 1 Tx channel and 1 Rx channel
        assert radio.has_rx_channels()
        assert radio.has_tx_channels()
        # test band.enabled to confirm component properties can be get/set
        assert len(radio.bands()) > 0
        band = radio.bands()[0]
        assert band.enabled
        band.enabled = False
        assert not band.enabled

    @pytest.mark.skipif(
        config["desktopVersion"] <= "2022.1" or is_ironpython, reason="Skipped on versions earlier than 2021 R2."
    )
    def test_antenna_component(self):
        antenna = self.aedtapp.modeler.components.create_component("Antenna")
        # Default pattern filename is empty string
        pattern_filename = antenna.get_pattern_filename()
        assert pattern_filename == ""
        # Default orientation is 0 0 0
        orientation = antenna.get_orientation_rpy()
        assert orientation == (0.0, 0.0, 0.0)
        # Default position is 0 0 0
        position = antenna.get_position()
        assert position == (0.0, 0.0, 0.0)
  
    @pytest.mark.skipif(
        config["desktopVersion"] <= "2023.1" or is_ironpython, reason="Skipped on versions lower than 2023.2"
    )
    def test_revision_generation(self):
        assert len(self.aedtapp2.results.revisions_list) == 0
        # place components and generate the appropriate number of revisions
        rad1 = self.aedtapp2.modeler.components.create_component("UE - Handheld")
        ant1 = self.aedtapp2.modeler.components.create_component("Antenna")
        if rad1 and ant1:
            ant1.move_and_connect_to(rad1)
        rad2 = self.aedtapp2.modeler.components.create_component("Bluetooth")
        ant2 = self.aedtapp2.modeler.components.create_component("Antenna")
        if rad2 and ant2:
            ant2.move_and_connect_to(rad2)
        rad3 = self.aedtapp2.modeler.components.create_component("Bluetooth")
        ant3 = self.aedtapp2.modeler.components.create_component("Antenna")
        if rad3 and ant3:
            ant3.move_and_connect_to(rad3)
        self.aedtapp2.analyze()
        assert len(self.aedtapp2.results.revisions_list) == 1
        self.aedtapp2.analyze()
        assert len(self.aedtapp2.results.revisions_list) == 1
        rad4 = self.aedtapp2.modeler.components.create_component("Bluetooth")
        ant4 = self.aedtapp2.modeler.components.create_component("Antenna")
        if rad4 and ant4:
            ant4.move_and_connect_to(rad4)
        self.aedtapp2.analyze()
        assert len(self.aedtapp2.results.revisions_list) == 2
   
    @pytest.mark.skipif(
        config["desktopVersion"] <= "2023.1" or is_ironpython, reason="Skipped on versions lower than 2023.2"
    )
    def test_manual_revision_access_test_getters(self):
        rad1 = self.aedtapp2.modeler.components.create_component("UE - Handheld")
        ant1 = self.aedtapp2.modeler.components.create_component("Antenna")        
        rad2 = self.aedtapp2.modeler.components.create_component("Bluetooth")
        if rad1 and ant1:
            ant1.move_and_connect_to(rad1)
        ant2 = self.aedtapp2.modeler.components.create_component("Antenna")
        if rad2 and ant2:
            ant2.move_and_connect_to(rad2)
        rad3 = self.aedtapp2.modeler.components.create_component("Bluetooth")
        ant3 = self.aedtapp2.modeler.components.create_component("Antenna")
        if rad3 and ant3:
            ant3.move_and_connect_to(rad3)
        self.aedtapp2.analyze()
        domain = Result.interaction_domain()
        self.aedtapp2.results.revisions_list[-1].run(domain)
        radiosRX = self.aedtapp2.results.get_radio_names(Emit.tx_rx_mode().rx)
        assert radiosRX[0] == 'Bluetooth'
        assert radiosRX[1] == 'Bluetooth 2'
        bandsRX = self.aedtapp2.results.get_band_names(radiosRX[0], Emit.tx_rx_mode().rx)
        assert bandsRX[0] =='Rx - Base Data Rate'
        assert bandsRX[1] == 'Rx - Enhanced Data Rate'
        rx_frequencies = self.aedtapp2.results.get_active_frequencies(radiosRX[0], bandsRX[0],  Emit.tx_rx_mode().rx)
        assert rx_frequencies[0] == 2402000000.0
        assert rx_frequencies[1] == 2403000000.0
        radiosTX = self.aedtapp2.results.get_radio_names(Emit.tx_rx_mode().tx)
        assert len(radiosTX) == 0
    
    @pytest.mark.skipif(
        config["desktopVersion"] <= "2023.1" or is_ironpython, reason="Skipped on versions lower than 2023.2"
    )
    def test_static_type_generation(self):
        domain = Result.interaction_domain()
        assert str(type(domain)) == "<class 'EmitApiPython.InteractionDomain'>"
        mode = Emit.tx_rx_mode()
        mode_rx = Emit.tx_rx_mode().rx
        assert str(type(mode)) == "<class 'EmitApiPython.tx_rx_mode'>"
        assert str(type(mode_rx)) == "<class 'EmitApiPython.tx_rx_mode'>"
        result_type = Emit.result_type()
        result_type_sensitivity =  Emit.result_type().sensitivity
        assert str(type(result_type)) == "<class 'EmitApiPython.result_type'>"
        assert str(type(result_type_sensitivity)) == "<class 'EmitApiPython.result_type'>"
    
    """
    Please note: The test below should be maintained as the last test within this file to ensure,
    aedtapp functions as intended.

    """
    @pytest.mark.skipif(
        config["desktopVersion"] <= "2022.1" or is_ironpython, reason="Skipped on versions lower than 2021.2"
    )
    def test_couplings(self):
        self.aedtapp = BasisTest.add_app(
            self, project_name="Cell Phone RFI Desense", application=Emit, subfolder=test_subfolder
        )
        links = self.aedtapp.couplings.linkable_design_names
        assert len(links) == 0
        for link in self.aedtapp.couplings.coupling_names:
            assert link == "ATA_Analysis"
            self.aedtapp.couplings.update_link(link)