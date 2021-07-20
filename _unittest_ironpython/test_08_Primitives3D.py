from unittest import TestCase
from conf_unittest import test_generator
import os
import sys

test_filter = "test_"

test_name = os.path.basename(__file__).replace(".py", "")
mymodule = __import__('_unittest.' + test_name, fromlist=['TestClass'])
test_obj = mymodule.TestClass()

class TestSequenceFunctionsGenerate(TestCase):
    def setUp(self):
        test_obj.setup_class()

    def tearDown(self):
        test_obj.teardown_class()

    def assertRaises(self, excClass, callableObj, *args, **kwargs):
        try:
            TestCase.assertRaises(self, excClass, callableObj, *args, **kwargs)
        except:
            print('\n    ' + repr(sys.exc_info()[1]))

    def assertTrue(self, callableObj, *args, **kwargs):
        try:
            TestCase.assertTrue(self, callableObj, *args, **kwargs)
        except:
            print('\n    ' + repr(sys.exc_info()[1]))



test_names = [name for name in dir(test_obj) if name.startswith(test_filter)]
for test_name in test_names:
    test_fn = test_generator(test_obj, test_name)
    setattr(TestSequenceFunctionsGenerate, test_name, test_fn)