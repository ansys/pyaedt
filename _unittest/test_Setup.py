# standard imports
import os
# Setup paths for module imports
from _unittest.conftest import local_path, scratch_path

# Import required modules
from pyaedt import Hfss, Circuit
from pyaedt.generic.filesystem import Scratch
import gc
test_project_name = "coax_setup"


class TestClass:
    def setup_class(self):
        with Scratch(scratch_path) as self.local_scratch:
            try:
                example_project = os.path.join(
                    local_path, 'example_models', test_project_name + '.aedt')
                self.test_project = self.local_scratch.copyfile(example_project)
                self.local_scratch.copyfolder(os.path.join(local_path, 'example_models', test_project_name + '.aedb'),
                                              os.path.join(self.local_scratch.path, test_project_name + '.aedb'))
                self.aedtapp = Hfss(os.path.join(
                    self.local_scratch.path, test_project_name + '.aedt'))
            except:
                pass

    def teardown_class(self):
        assert self.aedtapp.close_project(self.aedtapp.project_name)
        self.local_scratch.remove()
        gc.collect()

    def test_01_create_hfss_setup(self):
        setup1 = self.aedtapp.create_setup(
            "My_HFSS_Setup", self.aedtapp.SimulationSetupTypes.HFSSDrivenDefault)
        assert setup1.name == "My_HFSS_Setup"
        assert "SaveRadFieldsOnly" in setup1.props
        setup1.props["SaveRadFieldsOnly"] = True
        setup1.props["AdaptMultipleFreqs"] = True
        setup1.props["MultipleAdaptiveFreqsSetup"]["1GHz"] = [0.01]
        del setup1.props["MultipleAdaptiveFreqsSetup"]["5GHz"]
        setup1.update()
        setup1.disable()
        setup1.enable()

    def test_01b_create_hfss_sweep(self):
        setup1 = self.aedtapp.get_setup("My_HFSS_Setup")
        assert self.aedtapp.get_setups()
        sweep1 = setup1.add_sweep("MyFrequencySweep")
        sweep1.props["RangeStart"] = "1Hz"
        sweep1.props["RangeEnd"] = "2GHz"
        assert sweep1.update()
        sweep1.props["Type"]="Fast"
        sweep1.props["SaveFields"]=True
        assert sweep1.update()
        assert self.aedtapp.get_sweeps("My_HFSS_Setup")

    def test_02_create_circuit_setup(self):
        circuit = Circuit()
        setup1 = circuit.create_setup("circuit", self.aedtapp.SimulationSetupTypes.NexximLNA)
        assert setup1.name == "circuit"
        setup1.props["SweepDefinition"]['Data'] = 'LINC 0GHz 4GHz 501'
        setup1.update()
        setup1.disable()
        setup1.enable()
