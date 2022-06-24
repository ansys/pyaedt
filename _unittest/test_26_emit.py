# Import required modules
from _unittest.conftest import BasisTest
from _unittest.conftest import config
from _unittest.conftest import is_ironpython
from pyaedt import Emit
from pyaedt.modeler.PrimitivesEmit import EmitComponent
from pyaedt.modeler.PrimitivesEmit import EmitComponents

try:
    import pytest
except ImportError:
    import _unittest_ironpython.conf_unittest as pytest


class TestClass(BasisTest, object):
    def setup_class(self):
        BasisTest.my_setup(self)
        self.aedtapp = BasisTest.add_app(self, application=Emit)

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
        assert isinstance(antenna, EmitComponent)

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
        # Verify None,None is returned for an unconnected port
        radio2 = self.aedtapp.modeler.components.create_component("New Radio")
        radio2_port = radio2.port_names()[0]
        connected_comp, connected_port = radio2.port_connection(radio2_port)
        assert connected_comp is None
        assert connected_port is None

    @pytest.mark.skipif(
        config["desktopVersion"] <= "2022.1" or is_ironpython, reason="Skipped on versions lower than 2021.2"
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
        config["desktopVersion"] <= "2022.1" or is_ironpython, reason="Skipped on versions lower than 2021.2"
    )
    def test_couplings(self):
        self.aedtapp = BasisTest.add_app(self, project_name="Cell Phone RFI Desense", application=Emit)
        links = self.aedtapp.couplings.linkable_design_names
        assert len(links) == 0
        for link in self.aedtapp.couplings.coupling_names:
            assert link == "ATA_Analysis"
            self.aedtapp.couplings.update_link(link)
