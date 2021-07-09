from pyaedt import Hfss
from _unittest.test_07_Object3D import TestObject3D
from unittest import TestCase
import sys

class TestSequenceFunctionsGenerate(TestCase):
    pass

def test_generator(test_obj, test_function):
    def test(self):
        try:
            getattr(test_obj, test_function)()
        except AssertionError:
            print(sys.exc_info())
            self.assertTrue(False)
    return test

test_obj = TestObject3D()
test_names = [name for name in dir(test_obj) if name.startswith("test_")]
test_obj.aedtapp = Hfss()
for test_name in test_names:
    test_fn = test_generator(test_obj, test_name)
    setattr(TestSequenceFunctionsGenerate, test_name, test_fn)