from _unittest.test_07_Object3D import TestObject3D as TestClass
#from _unittest.test_08_Primitives import TestPrimitives as TestClass
from pyaedt import Hfss as application

#-------------------------------------------------------------------------------------
from unittest import TestCase
from conf_unittest import test_generator

class TestSequenceFunctionsGenerate(TestCase):
    pass

test_str = "test_"

test_obj = TestClass()
test_obj.setup_class()
test_obj.aedtapp = application()
test_names = [name for name in dir(test_obj) if name.startswith(test_str)]
for test_name in test_names:
    test_fn = test_generator(test_obj, test_name)
    setattr(TestSequenceFunctionsGenerate, test_name, test_fn)