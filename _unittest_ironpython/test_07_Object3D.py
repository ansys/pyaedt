from pyaedt import Hfss as application
from unittest import TestCase
from .conf_unittest import test_generator
import os

class TestSequenceFunctionsGenerate(TestCase):
    pass

test_filter = "test_"

test_name = os.path.basename(__file__).replace(".py", "")
mymodule = __import__('_unittest.' + test_name, fromlist=['TestClass'])
test_obj = mymodule.TestClass()
test_obj.setup_class()
test_obj.aedtapp = application()
test_names = [name for name in dir(test_obj) if name.startswith(test_filter)]
for test_name in test_names:
    test_fn = test_generator(test_obj, test_name)
    setattr(TestSequenceFunctionsGenerate, test_name, test_fn)