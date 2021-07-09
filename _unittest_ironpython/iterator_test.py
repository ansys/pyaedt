from pyaedt import Hfss
from _unittest.test_07_Object3D import TestObject3D
from unittest import TestCase

def test_generator(test_obj, test_function):
    def test(self):
        method_to_call = getattr(test_obj, test_function)
        try:
            method_to_call()
        except AssertionError:
            self.assertTrue(False)
    return test

class TestSequenceFunctionsGenerate(TestCase):
    pass

test_obj = TestObject3D()
test_names = [name for name in dir(test_obj) if name.startswith("test_")]
test_obj.aedtapp = Hfss()
for test_name in test_names:
    test_fn = test_generator(test_obj, test_name)
    setattr(TestSequenceFunctionsGenerate, test_name, test_fn)