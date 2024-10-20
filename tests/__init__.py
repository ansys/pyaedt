from pathlib import Path


TESTS_PATH = Path(__file__).resolve().parent
TESTS_SYSTEM_PATH = TESTS_PATH / "system"
TESTS_UNIT_PATH = TESTS_PATH / "unit"
TESTS_GENERAL_PATH = TESTS_SYSTEM_PATH / "general"
TESTS_SOLVERS_PATH = TESTS_SYSTEM_PATH / "solvers"
