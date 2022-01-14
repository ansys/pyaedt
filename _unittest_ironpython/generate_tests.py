""" Generate automatically launch files for all pytest test modules with filenames starting with "_test".
This overwrites any existing file that may have been modified.
"""
import os

standard_contents = """
from conf_unittest import test_generator, PytestMockup
import os

test_filter = "test_"

test_name = os.path.basename(__file__).replace(".py", "")
mymodule = __import__('_unittest.' + test_name, fromlist=['TestClass'])
test_obj = mymodule.TestClass()

class TestSequenceFunctionsGenerate(PytestMockup):
    @classmethod
    def setUpClass(cls):
        test_obj.setup_class()

    @classmethod
    def tearDownClass(cls):
        test_obj.teardown_class()

test_names = [name for name in dir(test_obj) if name.startswith(test_filter)]
for test_name in test_names:
    test_fn = test_generator(test_obj, test_name)
    setattr(TestSequenceFunctionsGenerate, test_name, test_fn)
"""

my_dir = os.path.dirname(__file__)
pytest_source_dir = os.path.join(my_dir, "..", "_unittest")
test_files = [f for f in os.listdir(pytest_source_dir) if f.startswith("test_")]
for pytest_filename in test_files:
    ut_filename = os.path.join(my_dir, pytest_filename)
    with open(ut_filename, "w") as f:
        f.write(standard_contents)
