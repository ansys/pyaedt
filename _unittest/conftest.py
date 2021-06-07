import tempfile
import pathlib
import pytest
import os
import shutil
import sys

import pytest
from pyaedt import Desktop

local_path = os.path.dirname(os.path.realpath(__file__))

scratch_path = tempfile.TemporaryDirectory().name
os.mkdir(scratch_path)
module_path = pathlib.Path(local_path)

# set scratch path and create it if necessary
scratch_path = tempfile.TemporaryDirectory().name
if not os.path.isdir(scratch_path):
    os.mkdir(scratch_path)
# sys.path.append(module_path)


desktopVersion = "2021.1"
NonGraphical = False
NewThread = True

@pytest.fixture(scope='session', autouse=True)
def desktop_init():
    desktop = Desktop(desktopVersion, NonGraphical, NewThread)

    yield desktop

    desktop.force_close_desktop()
    p = pathlib.Path(scratch_path).glob('**/scratch*')
    for folder in p:
        shutil.rmtree(folder, ignore_errors=True)
