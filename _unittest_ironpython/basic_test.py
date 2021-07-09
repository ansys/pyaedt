import unittest
from pyaedt import Hfss
from _unittest.test_07_Object3D import TestObject3D
class TestSequenceFunctions(unittest.TestCase):

    def setUp(self):
        self.aedtapp = Hfss()
        self.test_obj = TestObject3D

    def test_create_box(self):
        # make sure the shuffled sequence does not lose any elements
        o = self.aedtapp.modeler.primitives.create_box([0, 0, 0],[1, 2, 3], name="MyBox")
        self.assertTrue(o.name.startswith("MyBox"))

        # should raise an exception for invalid dimensions
        with self.assertRaises(AssertionError):
            self.aedtapp.modeler.primitives.create_box([0, 0, 0], "Invalid")

    def test_pyaedt_test(self):
        self.test_obj.test_01_bounding_box()

if __name__ == '__main__':
    unittest.main()