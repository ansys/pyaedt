import pytest
# Setup paths for module imports
import gc
# Import required modules
from pyaedt import Hfss
from pyaedt.generic.filesystem import Scratch

class TestVariable:
    def setup_class(self):
        self.aedtapp = Hfss()

    def teardown_class(self):
        assert self.aedtapp.close_project(self.aedtapp.project_name)
        #self.desktop.force_close_desktop()
        #self.local_scratch.remove()
        gc.collect()

    def test_01_set_globals(self):
        var = self.aedtapp.variable_manager
        self.aedtapp['$Test_Global1'] = "5rad"
        self.aedtapp['$Test_Global2'] = -1.0
        self.aedtapp['$Test_Global3'] = "0"
        self.aedtapp['$Test_Global4'] = "$Test_Global2*$Test_Global1"
        independent = self.aedtapp._variable_manager.independent_variable_names
        dependent = self.aedtapp._variable_manager.dependent_variable_names
        val = var['$Test_Global4']
        assert val.numeric_value == -5.0
        assert '$Test_Global1' in independent
        assert '$Test_Global2' in independent
        assert '$Test_Global3' in independent
        assert '$Test_Global4' in dependent
        pass

    def test_01_set_var_simple(self):
        var = self.aedtapp.variable_manager
        self.aedtapp['Var1'] = '1rpm'
        var_1 = self.aedtapp['Var1']
        var_2 = var['Var1'].string_value
        assert var_1 == var_2
        assert var['Var1'].numeric_value == 1.0
        pass

