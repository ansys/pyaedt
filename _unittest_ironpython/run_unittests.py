import argparse
import os
import sys
import unittest
import tempfile
from datetime import datetime
from pyaedt import settings

log_path = os.path.join(tempfile.gettempdir(), "test.log")
if os.path.exists(os.path.join(tempfile.gettempdir(), "test.log")):
    os.remove(log_path)
settings.logger_file_path = log_path

from pyaedt.generic.general_methods import is_ironpython

if os.name != "posix":
    ansysem_install_dir = os.environ.get("ANSYSEM_INSTALL_DIR", "")
    if not ansysem_install_dir:
        ansysem_install_dir = os.environ["ANSYSEM_ROOT212"]
    sys.path.append(os.path.join(ansysem_install_dir, "PythonFiles", "DesktopPlugin"))
path_dir = os.path.join(os.path.abspath(os.path.dirname(__file__)), "..")
sys.path.append(path_dir)

os.environ["UNITTEST_CURRENT_TEST"] = "1"
run_dir = os.path.abspath(os.path.dirname(__file__))

args_env = os.environ.get("RUN_UNITTESTS_ARGS", "")
parser = argparse.ArgumentParser()
parser.add_argument("--test-filter", "-t", default="test_*.py", help="test filter")
args = parser.parse_args(args_env.split())
test_filter = args.test_filter

max_attempts = 2


def discover_and_run(start_dir, pattern=None):
    """Discover and run tests cases. Return the tests result."""
    # use the default shared TestLoader instance
    test_loader = unittest.defaultTestLoader

    # automatically discover all tests
    test_suite = test_loader.discover(start_dir, pattern=pattern)

    # run the test suite
    log_file = os.path.join(start_dir, "runner_unittest.log")
    with open(log_file, "w+") as f:
        f.write("Test filter: {}\n".format(test_filter))
        f.write("Test started {}\n\n".format(datetime.now()))
        runner = unittest.TextTestRunner(f, verbosity=2)
        total_runs = 0
        total_errors = 0
        total_failures = 0
        for sub_suite in test_suite:
            attempts = 0
            while True:
                attempts += 1
                f.write("\n")
                result = runner.run(sub_suite)
                if attempts == max_attempts:
                    total_runs += result.testsRun
                    total_errors += len(result.errors)
                    total_failures += len(result.failures)
                    break
                if result.wasSuccessful():
                    total_runs += result.testsRun
                    break
                # try again
                f.write("\nAttempt n.{} FAILED. Re-running test suite.\n".format(attempts))
        f.write(
            "\n<unittest.runner.TextTestResult run={} errors={} failures={}>\n".format(
                total_runs, total_errors, total_failures
            )
        )
    return result


tests_result = discover_and_run(run_dir, pattern=test_filter)

if is_ironpython and "oDesktop" in dir(sys.modules["__main__"]):
    pid = sys.modules["__main__"].oDesktop.GetProcessID()
    if pid > 0:
        try:
            os.kill(pid, 9)
        except:
            successfully_closed = False
