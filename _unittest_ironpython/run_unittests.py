import unittest
import os
import sys
sys.path.append(r"C:\Program Files\AnsysEM\AnsysEM21.1\Win64\PythonFiles\DesktopPlugin")
sys.path.append(r"C:\data\pyaedt")

#import ScriptEnv
#ScriptEnv.Initialize("Ansoft.ElectronicsDesktop")

os.environ["UNITTEST_CURRENT_TEST"] = "1"


run_dir = r"C:\data\pyaedt\_unittest_ironpython"

def discover_and_run(start_dir, pattern=None):
    """Discover and run tests cases, returning the result."""
    if not pattern:
        pattern = 'test*.py'

    # use the default shared TestLoader instance
    test_loader = unittest.defaultTestLoader

    # automatically discover all tests
    test_suite = test_loader.discover(start_dir, pattern=pattern)

    # run the test suite
    log_file = os.path.join(start_dir, 'log_file.txt')
    with open(log_file, "w") as f:
        runner = unittest.TextTestRunner(f, verbosity=2)
        result = runner.run(test_suite)

discover_and_run(run_dir, pattern='test*.py')