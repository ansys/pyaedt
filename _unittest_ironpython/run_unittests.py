import unittest
import os
import sys
from datetime import datetime
import time

sys.path.append(os.path.join(os.environ["ANSYSEM_ROOT211"],"PythonFiles","DesktopPlugin"))
path_dir = os.path.join(os.path.abspath(os.path.dirname(__file__)), "..")
sys.path.append(path_dir)

os.environ["UNITTEST_CURRENT_TEST"] = "1"
run_dir = os.path.abspath(os.path.dirname(__file__))
print(run_dir)

def discover_and_run(start_dir, pattern=None):
    """Discover and run tests cases, returning the result."""
    # use the default shared TestLoader instance
    test_loader = unittest.defaultTestLoader

    # automatically discover all tests
    test_suite = test_loader.discover(start_dir, pattern=pattern)

    # run the test suite
    log_file = os.path.join(start_dir, 'runner_unittest.log')
    with open(log_file, "w") as f:
        f.write("Test started {}\n".format(datetime.now()))
        runner = unittest.TextTestRunner(f, verbosity=2)
        result = runner.run(test_suite)


discover_and_run(run_dir, pattern='test_*.py')

success_file = os.path.join(run_dir, 'tests_succeeded.log')
with open(success_file, "w") as f:
    f.write("ok")
