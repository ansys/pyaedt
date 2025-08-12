from textwrap import dedent
from tkinter import TclError
from unittest.mock import patch

import pytest

from ansys.aedt.core.extensions.icepak.icepak_model_reviewer import EXTENSION_TITLE
from ansys.aedt.core.extensions.icepak.icepak_model_reviewer import IcepakModelReviewer


import pytest
from unittest.mock import patch
import json
from tests import TESTS_UNIT_PATH
import os

def load_json():

    json_file = os.path.join(TESTS_UNIT_PATH, 'extensions','graphics_card.json')
    with open(json_file, 'r') as file:
        data = json.load(file)
    return data

@pytest.fixture
def patched_loader():
    with patch.object(IcepakModelReviewer, "get_project_data", side_effect=load_json) as mock_loader:
        yield mock_loader

def test_icepak_model_reviewer(mock_icepak_app):
    """Test instantiation of the IcepakModelReviewer."""
    extension = IcepakModelReviewer(withdraw=True)

    assert EXTENSION_TITLE == extension.root.title()
    assert "light" == extension.root.theme

    extension.root.destroy()

def test_icepak_model_reviewer_load_project(mock_icepak_app, patched_loader):
    extension = IcepakModelReviewer(withdraw=True)
    extension.load_button.invoke()
    boundary_table = extension.root.boundary_tab.winfo_children()[0]
    assert boundary_table.tree is not None
    assert len(boundary_table.tree.get_children()) == 3

def test_icepak_model_reviewer_table_values(mock_icepak_app, patched_loader):
    extension = IcepakModelReviewer(withdraw=True)
    extension.load_button.invoke()
    boundary_table = extension.root.boundary_tab.winfo_children()[0]
    row1 = boundary_table.tree.get_children()[0]
    row2 = boundary_table.tree.get_children()[1]
    row3 = boundary_table.tree.get_children()[2]
    assert boundary_table.tree.item(row1)['values'][5] == '4W'
    assert boundary_table.tree.item(row2)['values'][5] == '5w_per_m3'
    assert boundary_table.tree.item(row3)['values'][5] == '1W'

def test_icepak_model_reviewer_table_modification(mock_icepak_app, patched_loader):
    extension = IcepakModelReviewer(withdraw=True)
    extension.load_button.invoke()
    boundary_table = extension.root.boundary_tab.winfo_children()[0]
    row1 = boundary_table.tree.get_children()[0]
    row2 = boundary_table.tree.get_children()[1]
    row3 = boundary_table.tree.get_children()[2]
    boundary_table.tree.set(row1)['values'][5] ='2W'
    boundary_table.tree.set(row2)['values'][5] ='2w_per_m3'
    boundary_table.tree.set(row3)['values'][5] ='1.5W'
    extension.update_button.invoke()

