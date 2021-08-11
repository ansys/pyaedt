# Setup paths for module imports
import gc
from pyaedt.modeler.PrimitivesEmit import EmitComponent, EmitComponents

# Import required modules
from pyaedt import Emit
from pyaedt.generic.filesystem import Scratch

from _unittest.conftest import scratch_path

class TestEmit:
    def setup_class(self):
        project_name = "EmitProject"
        design_name = "EmitDesign1"
        # set a scratch directory and the environment / test data
        with Scratch(scratch_path) as self.local_scratch:
            self.aedtapp = Emit()

    def teardown_class(self):
        assert self.aedtapp.close_project()
        self.local_scratch.remove()
        gc.collect()

    def test_objects(self):
        assert self.aedtapp.solution_type
        assert isinstance(self.aedtapp.existing_analysis_setups, list)
        assert isinstance(self.aedtapp.setup_names, list)
        assert isinstance(self.aedtapp.modeler.components, EmitComponents)
        assert self.aedtapp.modeler
        assert self.aedtapp.oanalysis is None

    def test_create_components(self):
        radio = self.aedtapp.modeler.components.create_component("New Radio", "TestRadio")
        assert radio.name == "TestRadio"
        assert isinstance(radio, EmitComponent)
        antenna = self.aedtapp.modeler.components.create_component("Antenna", "TestAntenna")
        assert antenna.name == "TestAntenna"
        assert isinstance(antenna, EmitComponent)

    def test_connect_components(self):
        radio = self.aedtapp.modeler.components.create_component("New Radio")
        antenna = self.aedtapp.modeler.components.create_component("Antenna")
        antenna.move_and_connect_to(radio)
        antenna_port = antenna.port_names()[0] # antennas have 1 port
        radio_port = radio.port_names()[0] # radios have 1 port
        connected_comp, connected_port = antenna.port_connection(antenna_port)
        assert connected_comp == radio.name
        assert connected_port == radio_port
        # Verify None,None is returned for an unconnected port
        radio2 = self.aedtapp.modeler.components.create_component("New Radio")
        radio2_port = radio2.port_names()[0]
        connected_comp, connected_port = radio2.port_connection(radio2_port)
        assert connected_comp == None
        assert connected_port == None
