import unittest
from datetime import datetime
import os


from pyaedt import Circuit
from pyaedt import Hfss
from pyaedt import Hfss3dLayout
from pyaedt import Icepak
from pyaedt import Maxwell2d
from pyaedt import Maxwell3d
from pyaedt import Mechanical
from pyaedt import Q2d
from pyaedt import Q3d
from pyaedt import TwinBuilder


run_dir = os.path.abspath(os.path.dirname(__file__))
log_filename = os.path.join(run_dir, "pyaedt_unit_test_ironpython.log")


def run_tests(filename):
    suite = unittest.makeSuite(TestIronPython)

    with open(filename, "w") as f:
        f.write("Ironpython Unit Tests Started\n\n")
        f.write("Start time: {}\n\n".format(datetime.now()))

        runner = unittest.TextTestRunner(stream=f, verbosity=2)
        result = runner.run(suite)

        num_runs = result.testsRun
        num_errors = len(result.errors)
        num_failures = len(result.failures)

        f.write("\n<unittest.runner.TextTestResult Total Test run={}>\n".format(num_runs))
        if not result.wasSuccessful():
            f.write("\n<unittest.runner.TextTestResult errors={}>\n".format(num_errors+num_failures))


class TestIronPython(unittest.TestCase):

    def test_run_desktop_mechanical(self):
        aedtapp = Mechanical()
        self.assertTrue(aedtapp.design_type == "Mechanical")
        self.assertTrue(aedtapp.solution_type == "Steady-State Thermal")
        aedtapp.solution_type = "Modal"
        self.assertTrue(aedtapp.solution_type == "Modal")
        self.assertTrue(aedtapp.modeler)
        self.assertTrue(aedtapp.post)
        self.assertTrue(aedtapp.materials)
        self.assertTrue(aedtapp.mesh)
        self.assertTrue(aedtapp.variable_manager)

    def test_run_desktop_circuit(self):
        aedtapp = Circuit()
        self.assertTrue(aedtapp.design_type == "Circuit Design")
        self.assertTrue(aedtapp.solution_type == "NexximLNA")
        self.assertTrue(aedtapp.modeler)
        self.assertTrue(aedtapp.post)
        self.assertTrue(aedtapp.variable_manager)

    def test_run_desktop_icepak(self):
        aedtapp = Icepak()
        self.assertTrue(aedtapp.design_type == "Icepak")
        self.assertTrue(aedtapp.solution_type == "SteadyState")
        self.assertTrue(aedtapp.modeler)
        self.assertTrue(aedtapp.post)
        self.assertTrue(aedtapp.materials)
        self.assertTrue(aedtapp.mesh)
        self.assertTrue(aedtapp.variable_manager)

    def test_run_desktop_hfss3dlayout(self):
        aedtapp = Hfss3dLayout()
        self.assertTrue(aedtapp.design_type == "HFSS 3D Layout Design")
        self.assertTrue(aedtapp.solution_type == "HFSS3DLayout")
        self.assertTrue(aedtapp.modeler)
        self.assertTrue(aedtapp.post)
        self.assertTrue(aedtapp.materials)
        self.assertTrue(aedtapp.mesh)
        self.assertTrue(aedtapp.variable_manager)

    def test_run_desktop_twinbuilder(self):
        aedtapp = TwinBuilder()
        self.assertTrue(aedtapp.design_type == "Twin Builder")
        self.assertTrue(aedtapp.solution_type == "TR")
        self.assertTrue(aedtapp.modeler)
        self.assertTrue(aedtapp.post)
        self.assertTrue(aedtapp.materials)
        self.assertTrue(aedtapp.variable_manager)

    def test_run_desktop_q2d(self):
        aedtapp = Q2d()
        self.assertTrue(aedtapp.design_type == "2D Extractor")
        self.assertTrue(aedtapp.solution_type == "Open")
        self.assertTrue(aedtapp.modeler)
        self.assertTrue(aedtapp.post)
        self.assertTrue(aedtapp.materials)
        self.assertTrue(aedtapp.mesh)
        self.assertTrue(aedtapp.variable_manager)

    def test_run_desktop_q3d(self):
        aedtapp = Q3d()
        self.assertTrue(aedtapp.design_type == "Q3D Extractor")
        self.assertTrue(aedtapp.modeler)
        self.assertTrue(aedtapp.post)
        self.assertTrue(aedtapp.materials)
        self.assertTrue(aedtapp.mesh)
        self.assertTrue(aedtapp.variable_manager)

    def test_run_desktop_maxwell2d(self):
        aedtapp = Maxwell2d()
        self.assertTrue(aedtapp.design_type == "Maxwell 2D")
        self.assertTrue(aedtapp.solution_type == "Magnetostatic")
        self.assertTrue(aedtapp.modeler)
        self.assertTrue(aedtapp.post)
        self.assertTrue(aedtapp.materials)
        self.assertTrue(aedtapp.mesh)
        self.assertTrue(aedtapp.variable_manager)

    def test_run_desktop_hfss(self):
        aedtapp = Hfss()
        self.assertTrue(aedtapp.design_type == "HFSS")
        self.assertTrue("Modal" in aedtapp.solution_type)
        self.assertTrue(aedtapp.modeler)
        self.assertTrue(aedtapp.post)
        self.assertTrue(aedtapp.materials)
        self.assertTrue(aedtapp.mesh)
        self.assertTrue(aedtapp.variable_manager)

    def test_run_desktop_maxwell3d(self):
        aedtapp = Maxwell3d()
        self.assertTrue(aedtapp.design_type == "Maxwell 3D")
        self.assertTrue(aedtapp.solution_type == "Magnetostatic")
        self.assertTrue(aedtapp.modeler)
        self.assertTrue(aedtapp.post)
        self.assertTrue(aedtapp.materials)
        self.assertTrue(aedtapp.mesh)
        self.assertTrue(aedtapp.variable_manager)


if __name__ == '__main__':
    run_tests(log_filename)
