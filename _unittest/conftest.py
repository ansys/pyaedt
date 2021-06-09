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


desktop_version = "2021.1"
non_graphical = False
new_thread = True


@pytest.fixture(scope='session', autouse=True)
def desktop_init():
    desktop = Desktop(desktop_version, non_graphical, new_thread)

    yield desktop

    desktop.force_close_desktop()
    p = pathlib.Path(scratch_path).glob('**/scratch*')
    for folder in p:
        shutil.rmtree(folder, ignore_errors=True)

