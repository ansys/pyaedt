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

def config_file_load():
    config_file = os.path.join(TESTS_UNIT_PATH, 'extensions','graphics_card.json')
    with open(config_file, 'r') as file:
        data = json.load(file)
    return data

def mapping_load():
    mapping_file = os.path.join(TESTS_UNIT_PATH, 'extensions','mapping.json')
    with open(mapping_file, 'r') as file:
        data = json.load(file)
    return data

@pytest.fixture
def patched_loader():
    with patch.object(IcepakModelReviewer, "get_project_data", side_effect=config_file_load) as mock_loader:
        yield mock_loader

@pytest.fixture
def patched_object_id():
    with patch.object(IcepakModelReviewer, "object_id_mapping", side_effect=mapping_load) as mock_loader:
        yield mock_loader

@pytest.fixture
def patched_import_data_to_project():
    with patch.object(IcepakModelReviewer, "import_data_to_project", return_value = None) as mock_loader:
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
    assert boundary_table.tree.column(5)['id'] == 'Value 1'
    assert boundary_table.tree.item(row1)['values'][5] == '4W'
    assert boundary_table.tree.item(row2)['values'][5] == '5w_per_m3'
    assert boundary_table.tree.item(row3)['values'][5] == '1W'
    materials_table = extension.root.materials_tab.winfo_children()[0]
    assert len(materials_table.tree.get_children()) == 4
    row1 = materials_table.tree.get_children()[0]
    row2 = materials_table.tree.get_children()[1]
    row3 = materials_table.tree.get_children()[2]
    row4 = materials_table.tree.get_children()[3]
    assert materials_table.tree.item(row1)['values'][3] == 152
    assert materials_table.tree.item(row2)['values'][4] == '1.1614'
    assert materials_table.tree.item(row3)['values'][5] == 2
    assert materials_table.tree.item(row4)['values'][6] == 0
    model_table = extension.root.models_tab.winfo_children()[0]
    assert len(model_table.tree.get_children()) == 11
    assert model_table.tree.item(row1)['values'][2] == 'air'
    assert model_table.tree.item(row2)['values'][3] == 'Soft Rubber-Gray-surface'
    assert model_table.tree.item(row3)['values'][4] == 'True'
    assert model_table.tree.item(row3)['values'][5] == 'Model'

def test_icepak_model_reviewer_table_modification(mock_icepak_app, patched_loader,
                                                  patched_import_data_to_project, patched_object_id):
    extension = IcepakModelReviewer(withdraw=True)
    extension.load_button.invoke()
    boundary_table = extension.root.boundary_tab.winfo_children()[0]
    row1 = boundary_table.tree.get_children()[0]
    row2 = boundary_table.tree.get_children()[1]
    row3 = boundary_table.tree.get_children()[2]
    boundary_table.tree.set(row1, column='Value 1', value='2W')
    boundary_table.tree.set(row2, column='Value 1', value='2w_per_m3')
    boundary_table.tree.set(row3, column='Value 1', value='1.5W')
    extension.update_button.invoke()
    data = extension.root.bc_table.get_modified_data()
    assert extension.combined_data['boundaries']['CPU']['Total Power'] == '2W'
    assert extension.combined_data['boundaries']['Memory']['Power Density'] == '2w_per_m3'
    assert extension.combined_data['boundaries']['Source1']['Total Power'] == '1.5W'


