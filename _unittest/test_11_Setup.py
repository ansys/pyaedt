# standard imports
# Setup paths for module imports
from _unittest.conftest import BasisTest
from pyaedt import Circuit

# Import required modules

test_project_name = "coax_setup"


class TestClass(BasisTest, object):
    def setup_class(self):
        BasisTest.my_setup(self)
        self.aedtapp = BasisTest.add_app(self, project_name=test_project_name)

    def teardown_class(self):
        BasisTest.my_teardown(self)

    def test_01_create_hfss_setup(self):
        setup1 = self.aedtapp.create_setup("My_HFSS_Setup", self.aedtapp.SETUPS.HFSSDrivenDefault)
        assert setup1.name == "My_HFSS_Setup"
        assert "SaveRadFieldsOnly" in setup1.props
        setup1.props["SaveRadFieldsOnly"] = True
        assert setup1.enable_adaptive_setup_multifrequency([1, 2, 3])
        assert setup1.props["MultipleAdaptiveFreqsSetup"]["1GHz"][0] == 0.02
        assert setup1.enable_adaptive_setup_broadband(1, 2.5, 10, 0.01)
        assert setup1.props["MultipleAdaptiveFreqsSetup"]["Low"] == "1GHz"
        assert setup1.props["MaximumPasses"] == 10
        assert setup1.props["MaxDeltaS"] == 0.01
        assert setup1.enable_adaptive_setup_single(3.5)
        assert setup1.props["Frequency"] == "3.5GHz"
        assert setup1.props["MaximumPasses"] == 10
        assert setup1.props["MaxDeltaS"] == 0.01
        setup1.disable()
        setup1.enable()

    def test_01b_create_hfss_sweep(self):
        setup1 = self.aedtapp.get_setup("My_HFSS_Setup")
        assert self.aedtapp.get_setups()
        sweep1 = setup1.add_sweep("MyFrequencySweep")
        sweep1.props["RangeStart"] = "1Hz"
        sweep1.props["RangeEnd"] = "2GHz"
        assert sweep1.update()
        sweep1.props["Type"] = "Fast"
        sweep1.props["SaveFields"] = True
        assert sweep1.update()
        assert self.aedtapp.get_sweeps("My_HFSS_Setup")

    def test_02_create_circuit_setup(self):
        circuit = Circuit()
        setup1 = circuit.create_setup("circuit", self.aedtapp.SETUPS.NexximLNA)
        assert setup1.name == "circuit"
        setup1.props["SweepDefinition"]["Data"] = "LINC 0GHz 4GHz 501"
        setup1.update()
        setup1.disable()
        setup1.enable()

    def test_03_non_valid_setup(self):
        self.aedtapp.duplicate_design("non_valid")
        setup1 = self.aedtapp.create_setup("My_HFSS_Setup2", self.aedtapp.SETUPS.HFSSDrivenAuto)
        assert not setup1.enable_adaptive_setup_multifrequency([1, 2, 3])
        assert not setup1.enable_adaptive_setup_broadband(1, 2.5, 10, 0.01)
        assert not setup1.enable_adaptive_setup_single(3.5)
        sol = self.aedtapp.solution_type
        self.aedtapp.solution_type = "Transient"
        assert not setup1.enable_adaptive_setup_multifrequency([1, 2, 3])
        assert not setup1.enable_adaptive_setup_broadband(1, 2.5, 10, 0.01)
        assert not setup1.enable_adaptive_setup_single(3.5)
        self.aedtapp.solution_type = sol

    def test_04_delete_setup(self):
        self.aedtapp.insert_design("delete_setups")
        setup1 = self.aedtapp.create_setup("My_HFSS_Setup2", self.aedtapp.SETUPS.HFSSDrivenAuto)
        assert len(self.aedtapp.setups) == 1
        assert setup1.delete()
        assert len(self.aedtapp.setups) == 0
        assert not self.aedtapp.get_setups()
