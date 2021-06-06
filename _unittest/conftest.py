import tempfile
import pytest
import os
import time
import shutil
import sys
import pathlib

from pyaedt import Desktop

local_path = os.path.dirname(os.path.realpath(__file__))
module_path = pathlib.Path(local_path)

# set scratch path and create it if necessary
scratch_path = tempfile.TemporaryDirectory().name
if not os.path.isdir(scratch_path):
    os.mkdir(scratch_path)

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

