import os

from _unittest.conftest import desktop_version
import pytest

from pyaedt import Circuit

test_subfolder = "T11"
if desktop_version > "2022.2":
    test_project_name = "coax_setup_231"
else:
    test_project_name = "coax_setup"


@pytest.fixture(scope="class")
def aedtapp(add_app):
    app = add_app(project_name=test_project_name, subfolder=test_subfolder)
    return app


class TestClass:
    @pytest.fixture(autouse=True)
    def init(self, aedtapp, local_scratch):
        self.aedtapp = aedtapp
        self.local_scratch = local_scratch

    def test_01_create_hfss_setup(self):
        setup1 = self.aedtapp.create_setup("My_HFSS_Setup", self.aedtapp.SETUPS.HFSSDrivenDefault)
        assert setup1.name == "My_HFSS_Setup"
        assert "SaveRadFieldsOnly" in setup1.props
        assert "SaveRadFieldsOnly" in setup1.available_properties
        setup1["SaveRadFieldsonly"] = True
        assert setup1.props["SaveRadFieldsOnly"] == setup1["SaveRadFieldsonly"]
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
        self.aedtapp.save_project()
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
        sweep2 = setup1.add_sweep(sweepname="test_sweeptype", sweeptype="invalid")
        assert sweep2.props["Type"] == "Interpolating"
        sweep3 = setup1.create_frequency_sweep(freqstart=1, freqstop="500MHz")
        assert sweep3.props["Type"] == "Discrete"
        sweep4 = setup1.create_frequency_sweep("GHz", 23, 25, 401, sweep_type="Fast")
        assert sweep4.props["Type"] == "Fast"

    def test_01c_create_hfss_setup_auto_open(self):
        self.aedtapp.duplicate_design("auto_open")
        for setup in self.aedtapp.get_setups():
            self.aedtapp.delete_setup(setup)
        self.aedtapp.set_auto_open()
        setup1 = self.aedtapp.get_setup("Auto1")
        setup1.enable_adaptive_setup_multifrequency([1.9, 2.4], 0.02)
        assert setup1.update({"MaximumPasses": 20})
        assert setup1.props["SolveType"] == "MultiFrequency"

    def test_02_create_circuit_setup(self):
        circuit = Circuit(specified_version=desktop_version)
        setup1 = circuit.create_setup("circuit", self.aedtapp.SETUPS.NexximLNA)
        assert setup1.name == "circuit"
        setup1.props["SweepDefinition"]["Data"] = "LINC 0GHz 4GHz 501"
        setup1["SaveRadFieldsonly"] = True
        setup1["SweepDefinition/Data"] = "LINC 0GHz 4GHz 301"
        assert setup1.props["SweepDefinition"]["Data"] == "LINC 0GHz 4GHz 301"
        assert "SweepDefinition" in setup1.available_properties
        setup1.update()
        setup1.disable()
        setup1.enable()

    def test_03_non_valid_setup(self):
        self.aedtapp.set_active_design("HFSSDesign")
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

    def test_05_sweep_auto(self):
        self.aedtapp.insert_design("sweep")
        setup1 = self.aedtapp.create_setup("My_HFSS_Setup4", self.aedtapp.SETUPS.HFSSDrivenAuto)
        assert setup1.add_subrange("LinearStep", 1, 10, 0.1, clear=False)
        assert setup1.add_subrange("LinearCount", 10, 20, 10, clear=True)

    def test_06_sweep_sbr(self):
        self.aedtapp.insert_design("sweepsbr")
        self.aedtapp.solution_type = "SBR+"
        self.aedtapp.insert_infinite_sphere()
        setup1 = self.aedtapp.create_setup("My_HFSS_Setup4", self.aedtapp.SETUPS.HFSSSBR)
        assert setup1.add_subrange("LinearStep", 1, 10, 0.1, clear=False)
        assert setup1.add_subrange("LinearCount", 10, 20, 10, clear=True)

    def test_25a_create_parametrics(self):
        self.aedtapp.set_active_design("HFSSDesign")
        self.aedtapp["w1"] = "10mm"
        self.aedtapp["w2"] = "2mm"
        setup1 = self.aedtapp.parametrics.add("w1", 0.1, 20, 0.2, "LinearStep")
        assert setup1
        assert setup1.add_variation("w2", "0.1mm", 10, 11)
        assert setup1.add_variation("w2", start_point="0.2mm", variation_type="SingleValue")
        assert setup1.add_variation("w1", start_point="0.3mm", end_point=5, step=0.2, variation_type="LinearStep")
        assert setup1.add_variation("w1", start_point="0.3mm", end_point=5, step=1, variation_type="DecadeCount")
        assert setup1.add_variation("w1", start_point="0.3mm", end_point=5, step=1, variation_type="OctaveCount")
        assert setup1.add_variation("w1", start_point="0.3mm", end_point=5, step=1, variation_type="ExponentialCount")
        assert setup1.add_calculation(
            calculation="dB(S(1,1))", ranges={"Freq": "3.5GHz"}, solution="My_HFSS_Setup : LastAdaptive"
        )
        assert setup1.name in self.aedtapp.get_oo_name(
            self.aedtapp.odesign, r"Optimetrics".format(self.aedtapp.design_name)
        )
        oo = self.aedtapp.get_oo_object(self.aedtapp.odesign, r"Optimetrics\{}".format(setup1.name))
        oo_calculation = oo.GetCalculationInfo()[0]
        assert "Modal Solution Data" in oo_calculation
        assert setup1.export_to_csv(os.path.join(self.local_scratch.path, "test.csv"))
        assert os.path.exists(os.path.join(self.local_scratch.path, "test.csv"))
        assert self.aedtapp.parametrics.add_from_file(
            os.path.join(self.local_scratch.path, "test.csv"), "ParametricsfromFile"
        )
        oo = self.aedtapp.get_oo_object(self.aedtapp.odesign, r"Optimetrics\ParametricsfromFile")
        assert oo
        assert self.aedtapp.parametrics.delete("ParametricsfromFile")

    def test_25b_create_parametrics_sync(self):
        self.aedtapp["a1"] = "10mm"
        self.aedtapp["a2"] = "2mm"
        setup1 = self.aedtapp.parametrics.add(
            "a1", start_point=0.1, end_point=20, step=10, variation_type="LinearCount"
        )
        assert setup1
        assert setup1.add_variation("a2", start_point="0.3mm", end_point=5, step=10, variation_type="LinearCount")
        assert setup1.sync_variables(["a1", "a2"], sync_n=1)
        assert setup1.sync_variables(["a1", "a2"], sync_n=0)
        setup1.add_variation("a1", start_point="13mm", variation_type="SingleValue")

    def test_26_create_optimization(self):
        calculation = "db(S(1,1))"
        new_setup = self.aedtapp.create_setup("MyOptimSetup")
        new_setup.props["Frequency"] = "2.5GHz"
        sweep = new_setup.create_linear_step_sweep(freqstart=2, freqstop=10, step_size=0.1)
        setup2 = self.aedtapp.optimizations.add(
            calculation, ranges={"Freq": "2.5GHz"}, solution="{} : {}".format(new_setup.name, sweep.name)
        )
        assert setup2
        assert setup2.name in self.aedtapp.get_oo_name(
            self.aedtapp.odesign, r"Optimetrics".format(self.aedtapp.design_name)
        )
        oo = self.aedtapp.get_oo_object(self.aedtapp.odesign, r"Optimetrics\{}".format(setup2.name))
        oo_calculation = oo.GetCalculationInfo()[0]
        assert calculation in oo_calculation
        assert "{} : {}".format(new_setup.name, sweep.name) in oo_calculation
        for el in oo_calculation:
            if "NAME:Ranges" in el:
                break
        assert len(el) == 3
        assert setup2.add_variation("w1", 0.1, 10, 5)
        assert setup2.add_goal(
            calculation=calculation, ranges={"Freq": "2.6GHz"}, solution="{} : {}".format(new_setup.name, sweep.name)
        )
        oo_calculation = oo.GetCalculationInfo()[0]
        for el in reversed(oo_calculation):
            if "NAME:Ranges" in el:
                break
        assert "2.6GHz" in el[2]
        assert setup2.add_goal(
            calculation=calculation,
            ranges={"Freq": ("2.6GHz", "5GHZ")},
            solution="{} : {}".format(new_setup.name, sweep.name),
        )
        oo = self.aedtapp.get_oo_object(self.aedtapp.odesign, r"Optimetrics\{}".format(setup2.name))
        oo_calculation = oo.GetCalculationInfo()[0]
        for el in reversed(oo_calculation):
            if "NAME:Ranges" in el:
                break
        assert "rd" in el[2]
        assert self.aedtapp.optimizations.delete(setup2.name)

    def test_27_create_doe(self):
        calculation = "db(S(1,1))"
        new_setup = self.aedtapp.create_setup("MyDOESetup")
        new_setup.props["Frequency"] = "2.5GHz"
        sweep = new_setup.create_linear_step_sweep(freqstart=2, freqstop=10, step_size=0.1)
        setup2 = self.aedtapp.optimizations.add(
            calculation,
            ranges={"Freq": "2.5GHz"},
            optim_type="DXDOE",
            solution="{} : {}".format(new_setup.name, sweep.name),
        )
        assert setup2.add_variation("w1", 0.1, 10)
        assert setup2.add_variation("w2", 0.1, 10)
        assert setup2
        if desktop_version < "2024.1":
            assert setup2.add_goal(
                calculation="dB(S(1,1))",
                ranges={"Freq": "2.5GHz"},
                solution="{} : {}".format(new_setup.name, sweep.name),
            )
            assert setup2.add_calculation(
                calculation="dB(S(1,1))",
                ranges={"Freq": "2.5GHz"},
                solution="{} : {}".format(new_setup.name, sweep.name),
            )
        assert setup2.delete()

    def test_28A_create_optislang(self):
        new_setup = self.aedtapp.create_setup("MyOptisSetup")
        new_setup.props["Frequency"] = "2.5GHz"
        sweep = new_setup.create_linear_step_sweep(freqstart=2, freqstop=10, step_size=0.1)
        setup1 = self.aedtapp.optimizations.add(
            calculation=None,
            ranges=None,
            variables=None,
            optim_type="optiSLang",
            solution="{} : {}".format(new_setup.name, sweep.name),
        )
        assert setup1.add_variation("w1", 1, 10, 51)
        setup2 = self.aedtapp.optimizations.add(
            calculation=None,
            ranges=None,
            variables={"w1": "1mm", "w2": "2mm"},
            optim_type="optiSLang",
            solution="{} : {}".format(new_setup.name, sweep.name),
        )
        assert setup2.add_variation("a1", 1, 10, 51)
        assert not setup2.add_variation("w3", 0.1, 10, 5)
        assert setup2
        assert setup2.add_goal(
            calculation="dB(S(1,1))", ranges={"Freq": "2.5GHz"}, solution="{} : {}".format(new_setup.name, sweep.name)
        )

    def test_28B_create_dx(self):
        new_setup = self.aedtapp.create_setup("MyDXSetup")
        new_setup.props["Frequency"] = "2.5GHz"
        sweep = new_setup.create_linear_step_sweep(freqstart=2, freqstop=10, step_size=0.1)
        setup1 = self.aedtapp.optimizations.add(
            None,
            ranges=None,
            variables=None,
            optim_type="DesignExplorer",
            solution="{} : {}".format(new_setup.name, sweep.name),
        )
        assert setup1.add_variation("w1", 5, 10, 51)
        setup2 = self.aedtapp.optimizations.add(
            None,
            ranges=None,
            variables={"w1": "1mm", "w2": "2mm"},
            optim_type="DesignExplorer",
            solution="{} : {}".format(new_setup.name, sweep.name),
        )
        assert setup2.add_variation("a1", 1, 10, 51)
        assert setup2
        assert setup2.add_goal(
            calculation="dB(S(1,1))", ranges={"Freq": "2.5GHz"}, solution="{} : {}".format(new_setup.name, sweep.name)
        )

    def test_29_create_sensitivity(self):
        calculation = "db(S(1,1))"
        new_setup = self.aedtapp.create_setup("MySensiSetup")
        new_setup.props["Frequency"] = "2.5GHz"
        sweep = new_setup.create_linear_step_sweep(freqstart=2, freqstop=10, step_size=0.1)
        setup2 = self.aedtapp.optimizations.add(
            calculation,
            ranges={"Freq": "2.5GHz"},
            optim_type="Sensitivity",
            solution="{} : {}".format(new_setup.name, sweep.name),
        )
        assert setup2.add_variation("w1", 0.1, 10, 3.2)
        assert setup2
        assert setup2.add_calculation(
            calculation="dB(S(1,1))", ranges={"Freq": "2.5GHz"}, solution="{} : {}".format(new_setup.name, sweep.name)
        )

    def test_29_create_statistical(self):
        calculation = "db(S(1,1))"
        new_setup = self.aedtapp.create_setup("MyStatisticsetup")
        new_setup.props["Frequency"] = "2.5GHz"
        sweep = new_setup.create_linear_step_sweep(freqstart=2, freqstop=10, step_size=0.1)
        setup2 = self.aedtapp.optimizations.add(
            calculation,
            ranges={"Freq": "2.5GHz"},
            optim_type="Statistical",
            solution="{} : {}".format(new_setup.name, sweep.name),
        )
        assert setup2.add_variation("w1", 0.1, 10, 0.3)
        assert setup2
        assert setup2.add_calculation(
            calculation="dB(S(1,1))", ranges={"Freq": "2.5GHz"}, solution="{} : {}".format(new_setup.name, sweep.name)
        )
