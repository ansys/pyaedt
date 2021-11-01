from conf_unittest import test_generator, PytestMockup
import os

test_filter = "test_"

test_name = os.path.basename(__file__).replace(".py", "")
fromlist = ["TestHFSSProjectFile", "TestProjectFileWithBinaryContent", "TestProjectFileWithMultipleDesigns"]
mymodule = __import__("_unittest." + test_name, fromlist=fromlist)


def make_test_sequence_functions_generate_class(test_obj):
    class TestSequenceFunctionsGenerate(PytestMockup):
        @classmethod
        def setUpClass(cls):
            test_obj.setup_class()

        @classmethod
        def tearDownClass(cls):
            test_obj.teardown_class()

    return TestSequenceFunctionsGenerate


test_obj = mymodule.TestHFSSProjectFile()
test_names = [name for name in dir(test_obj) if name.startswith(test_filter)]
for test_name in test_names:
    test_fn = test_generator(test_obj, test_name)
    setattr(make_test_sequence_functions_generate_class(test_obj), test_name, test_fn)


test_obj = mymodule.TestProjectFileWithBinaryContent()
test_names = [name for name in dir(test_obj) if name.startswith(test_filter)]
for test_name in test_names:
    test_fn = test_generator(test_obj, test_name)
    setattr(make_test_sequence_functions_generate_class(test_obj), test_name, test_fn)


test_obj = mymodule.TestProjectFileWithMultipleDesigns()
test_names = [name for name in dir(test_obj) if name.startswith(test_filter)]
for test_name in test_names:
    test_fn = test_generator(test_obj, test_name)
    setattr(make_test_sequence_functions_generate_class(test_obj), test_name, test_fn)
