# ruff: noqa: E402

# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 - 2025 ANSYS, Inc. and/or its affiliates.
# SPDX-License-Identifier: MIT
#
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import pytest

from ansys.aedt.core.generic.file_utils import read_json
from ansys.aedt.core.perceive_em import MISC_PATH
from ansys.aedt.core.perceive_em.core.api_interface import PerceiveEM
from ansys.aedt.core.perceive_em.modules.material import MaterialManager
from ansys.aedt.core.perceive_em.modules.material import calculate_itu_properties
from ansys.aedt.core.perceive_em.modules.material_properties import MaterialProperties

default_material = MaterialProperties(
    thickness=1.0,
    rel_eps_real=2.5,
    rel_eps_imag=0.1,
    rel_mu_real=1.2,
    rel_mu_imag=0.05,
    conductivity=1500,
    height_standard_dev=0.003,
    roughness=0.002,
    backing="foam",
    coating_idx=4,
)


def test_init_material_manager():
    em = PerceiveEM()

    manager1 = MaterialManager(em)
    assert len(manager1.available_materials) == 31
    assert len(manager1.available_material_names) == len(manager1.available_materials)
    assert len(manager1.available_material_names_by_coating_index) == len(manager1.available_materials)

    assert len(manager1.materials) == 0
    assert len(manager1.material_names) == len(manager1.materials)
    assert len(manager1.material_names_by_coating_index) == len(manager1.materials)

    material_library = {"mat1": default_material}
    manager2 = MaterialManager(em, material_library)
    assert len(manager2.available_materials) == 1
    assert len(manager2.available_material_names) == len(manager2.available_materials)
    assert len(manager2.available_material_names_by_coating_index) == len(manager2.available_materials)

    assert len(manager2.materials) == 0
    assert len(manager2.material_names) == len(manager2.materials)
    assert len(manager2.material_names_by_coating_index) == len(manager2.materials)

    material_file = MISC_PATH / "default_material_library.json"
    manager3 = MaterialManager(em, material_file)
    assert len(manager3.available_materials) == 31
    assert len(manager3.available_material_names) == len(manager3.available_materials)
    assert len(manager3.available_material_names_by_coating_index) == len(manager3.available_materials)

    assert len(manager3.materials) == 0
    assert len(manager3.material_names) == len(manager3.materials)
    assert len(manager3.material_names_by_coating_index) == len(manager3.materials)

    with pytest.raises(FileNotFoundError):
        material_file = MISC_PATH / "invented.json"
        _ = MaterialManager(em, material_file)


def test_load_material():
    em = PerceiveEM()

    manager = MaterialManager(em)

    available_materials = len(manager.available_materials)
    materials = len(manager.materials)

    assert manager.load_material("pec")

    assert manager.load_material("absorber")
    assert len(manager.available_materials) == available_materials
    assert len(manager.materials) == materials + 1
    materials += 1

    assert manager.load_material("wall_interior")
    assert len(manager.available_materials) == available_materials
    assert len(manager.materials) == materials + 1
    materials += 1

    with pytest.raises(ValueError):
        manager.load_material("invented")


def test_add_material():
    em = PerceiveEM()

    manager = MaterialManager(em)

    available_materials = len(manager.available_materials)
    materials = len(manager.materials)

    with pytest.raises(ValueError):
        manager.add_material(name="absorber", overwrite=False, properties=default_material)

    with pytest.raises(TypeError):
        manager.add_material("new", overwrite=False, properties={})

    assert manager.add_material("absorber", overwrite=True, properties=default_material, load=True)

    assert len(manager.available_materials) == available_materials
    assert len(manager.materials) == materials + 1
    materials += 1

    assert manager.add_material("new", properties=default_material, load=False)

    assert len(manager.available_materials) == available_materials + 1
    assert len(manager.materials) == materials
    available_materials += 1


def test_calculate_itu_properties():
    new_material = calculate_itu_properties(frequency=1e9)
    assert isinstance(new_material, dict)

    em = PerceiveEM()
    material_manager_new = MaterialManager(em, new_material)
    assert len(material_manager_new.available_materials) == 15
