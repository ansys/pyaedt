import pytest
import os
import time
import shutil
import sys
from pyaedt import Desktop
import pathlib
local_path = os.path.dirname(os.path.realpath(__file__))
module_path = pathlib.Path(local_path)
scratch_path = "C:\\temp"
sys.path.append(module_path)

desktopVersion = "2021.1"
NonGraphical = False
NewThread = False

@pytest.fixture(scope='session', autouse=True)
def desktop_init():
    desktop = Desktop(desktopVersion, NonGraphical, NewThread)

    yield desktop

    desktop.force_close_desktop()
    p = pathlib.Path(scratch_path).glob('**/scratch*')
    for folder in p:
        shutil.rmtree(folder, ignore_errors=True)


