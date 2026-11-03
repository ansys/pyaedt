# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 - 2026 Synopsys, Inc. and ANSYS, Inc. All rights reserved.
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

"""Unit tests for MCAD assembly configuration and management."""

from __future__ import annotations

from pathlib import Path

from ansys.aedt.core.modeler.advanced_cad.mcad_assembly import Arrange
from ansys.aedt.core.modeler.advanced_cad.mcad_assembly import CoordinateSystem
from ansys.aedt.core.modeler.advanced_cad.mcad_assembly import ECADComponent
from ansys.aedt.core.modeler.advanced_cad.mcad_assembly import MCADAssembly
from ansys.aedt.core.modeler.advanced_cad.mcad_assembly import MCADComponent


class TestMCADAssembly:
    """Test suite for MCADAssembly class."""

    def setup_method(self):
        """Set up test fixtures."""
        self.assembly = MCADAssembly()

    def test_mcad_assembly_initialization(self):
        """Test MCADAssembly initialization creates empty collections."""
        assert isinstance(self.assembly.coordinate_system, dict)
        assert isinstance(self.assembly.mcad_component_models, dict)
        assert isinstance(self.assembly.ecad_component_models, dict)
        assert isinstance(self.assembly.model_libraries, list)
        assert isinstance(self.assembly.mcad_sub_components, dict)
        assert isinstance(self.assembly.ecad_sub_components, dict)

    def test_add_mcad_component_model(self):
        """Test registering MCAD component models."""
        model_name = "USB_Connector"
        model_path = "models/connectors/usb_type_a.a3dcomp"

        self.assembly.add_mcad_component_model(name=model_name, path=model_path)

        assert model_name in self.assembly.mcad_component_models
        assert self.assembly.mcad_component_models[model_name] == model_path

    def test_add_multiple_mcad_component_models(self):
        """Test registering multiple MCAD models."""
        models = {
            "Connector": "models/connectors/usb.a3dcomp",
            "Shield": "models/shields/rf_cage.step",
            "Antenna": "models/antennas/dipole.step",
        }

        for name, path in models.items():
            self.assembly.add_mcad_component_model(name=name, path=path)

        assert len(self.assembly.mcad_component_models) == 3
        for name, path in models.items():
            assert self.assembly.mcad_component_models[name] == path

    def test_add_ecad_component_model(self):
        """Test registering ECAD component models."""
        model_name = "MainBoard"
        model_path = "pcb/main_assembly.aedb"

        self.assembly.add_ecad_component_model(name=model_name, path=model_path)

        assert model_name in self.assembly.ecad_component_models
        assert self.assembly.ecad_component_models[model_name] == model_path

    def test_add_multiple_ecad_component_models(self):
        """Test registering multiple ECAD models."""
        models = {
            "MainBoard": "pcb/main.aedb",
            "DaughterCard": "pcb/daughter.aedb",
        }

        for name, path in models.items():
            self.assembly.add_ecad_component_model(name=name, path=path)

        assert len(self.assembly.ecad_component_models) == 2
        for name, path in models.items():
            assert self.assembly.ecad_component_models[name] == path

    def test_add_coordinate_system(self):
        """Test creating and registering coordinate systems."""
        cs_name = "MainCS"
        cs = self.assembly.add_coordinate_system(name=cs_name)

        assert isinstance(cs, CoordinateSystem)
        assert cs.name == cs_name
        assert cs.reference_coordinate_system == "Global"
        assert cs_name in self.assembly.coordinate_system

    def test_add_multiple_coordinate_systems(self):
        """Test creating multiple coordinate systems."""
        cs_names = ["MainCS", "Connector_Mount", "Antenna_Position"]

        for cs_name in cs_names:
            self.assembly.add_coordinate_system(name=cs_name)

        assert len(self.assembly.coordinate_system) == 3
        for cs_name in cs_names:
            assert cs_name in self.assembly.coordinate_system

    def test_add_sub_mcad_component(self):
        """Test adding top-level MCAD subcomponent."""
        self.assembly.add_mcad_component_model(name="Chassis", path="models/chassis.a3dcomp")

        comp = self.assembly.add_sub_mcad_component(name="Case", model="Chassis")

        assert isinstance(comp, MCADComponent)
        assert comp.name == "Case"
        assert comp.model == "Chassis"
        assert comp.component_type == "mcad"
        assert "Case" in self.assembly.mcad_sub_components

    def test_add_sub_ecad_component(self):
        """Test adding top-level ECAD subcomponent."""
        self.assembly.add_ecad_component_model(name="MainBoard", path="pcb/main.aedb")

        comp = self.assembly.add_sub_ecad_component(name="PCB_1", model="MainBoard")

        assert isinstance(comp, ECADComponent)
        assert comp.name == "PCB_1"
        assert comp.model == "MainBoard"
        assert comp.component_type == "ecad"
        assert "PCB_1" in self.assembly.ecad_sub_components

    def test_add_model_library(self):
        """Test registering model libraries."""
        lib_path = "/project/component_libraries/standard"

        self.assembly.add_model_library(library_path=lib_path)

        assert lib_path in self.assembly.model_libraries

    def test_add_multiple_model_libraries(self):
        """Test registering multiple model libraries."""
        libs = [
            "/project/libraries/standard",
            "/project/libraries/custom",
            "/project/libraries/connectors",
        ]

        for lib in libs:
            self.assembly.add_model_library(library_path=lib)

        assert len(self.assembly.model_libraries) == 3
        for lib in libs:
            assert lib in self.assembly.model_libraries

    def test_add_model_library_with_path_object(self):
        """Test registering model library using Path object."""
        lib_path = Path("/project/component_libraries/standard")

        self.assembly.add_model_library(library_path=lib_path)

        assert str(lib_path) in self.assembly.model_libraries

    def test_sub_components_property(self):
        """Test sub_components property returns combined dict."""
        self.assembly.add_mcad_component_model(name="Connector", path="models/connector.a3dcomp")
        self.assembly.add_ecad_component_model(name="MainBoard", path="pcb/main.aedb")

        mcad_comp = self.assembly.add_sub_mcad_component(name="J1", model="Connector")
        ecad_comp = self.assembly.add_sub_ecad_component(name="PCB_1", model="MainBoard")

        sub_comps = self.assembly.sub_components

        assert len(sub_comps) == 2
        assert "J1" in sub_comps
        assert "PCB_1" in sub_comps
        assert sub_comps["J1"] == mcad_comp
        assert sub_comps["PCB_1"] == ecad_comp

    def test_preprocess_backward_compatibility(self):
        """Test backward compatibility with legacy assembly format."""
        legacy_data = {
            "assembly": {
                "legacy_comp": {
                    "component_type": "mcad",
                    "name": "legacy_comp",
                    "model": "LegacyModel",
                    "layout_coordinate_systems": ["CS1"],  # Should be removed
                }
            }
        }

        # Preprocess should handle legacy format
        assembly = MCADAssembly.model_validate(legacy_data)

        assert "legacy_comp" in assembly.mcad_sub_components
        assert len(assembly.ecad_sub_components) == 0

    def test_preprocess_legacy_ecad_components(self):
        """Test backward compatibility with legacy ECAD components."""
        legacy_data = {
            "sub_components": {
                "legacy_ecad": {
                    "component_type": "ecad",
                    "name": "legacy_ecad",
                    "model": "LegacyECAD",
                }
            }
        }

        assembly = MCADAssembly.model_validate(legacy_data)

        assert "legacy_ecad" in assembly.ecad_sub_components
        assert len(assembly.mcad_sub_components) == 0

    def test_preprocess_merges_legacy_formats(self):
        """Test that both legacy assembly and sub_components keys are merged."""
        legacy_data = {
            "assembly": {"comp1": {"component_type": "mcad", "name": "comp1", "model": "Model1"}},
            "sub_components": {"comp2": {"component_type": "ecad", "name": "comp2", "model": "Model2"}},
        }

        assembly = MCADAssembly.model_validate(legacy_data)

        assert "comp1" in assembly.mcad_sub_components
        assert "comp2" in assembly.ecad_sub_components

    def test_full_workflow(self):
        """Test a complete assembly workflow."""
        # Register models
        self.assembly.add_mcad_component_model(name="Connector", path="models/usb_connector.a3dcomp")
        self.assembly.add_ecad_component_model(name="MainBoard", path="pcb/main.aedb")

        # Create coordinate systems
        cs_main = self.assembly.add_coordinate_system(name="MainCS")
        cs_connector = self.assembly.add_coordinate_system(name="Connector_CS")

        assert cs_main.name == "MainCS"
        assert cs_connector.name == "Connector_CS"

        # Add components
        pcb = self.assembly.add_sub_ecad_component(name="PCB_1", model="MainBoard")
        pcb.target_coordinate_system = "MainCS"
        pcb.layout_coordinate_systems = ["USB_Port"]

        connector = pcb.add_sub_mcad_component(name="J1", model="Connector")
        connector.target_coordinate_system = "Connector_CS"
        connector.add_arrange_rotate(axis="Z", angle="90deg")

        # Verify the assembly structure
        assert len(self.assembly.coordinate_system) == 2
        assert len(self.assembly.ecad_sub_components) == 1
        assert pcb.target_coordinate_system == "MainCS"
        assert len(pcb.mcad_sub_components) == 1
        assert connector.arranges[0].operation == "rotate"

    def test_coordinate_system_defaults(self):
        """Test that coordinate systems default to global reference."""
        cs = self.assembly.add_coordinate_system(name="TestCS")

        assert cs.reference_coordinate_system == "Global"
        assert cs.origin == ["0mm", "0mm", "0mm"]


class TestMCADComponent:
    """Test suite for MCADComponent class."""

    def setup_method(self):
        """Set up test fixtures."""
        self.component = MCADComponent(name="TestComp", model="TestModel")

    def test_add_sub_mcad_component(self):
        """Test adding child MCAD component."""
        child = self.component.add_sub_mcad_component(name="Child", model="ChildModel")

        assert isinstance(child, MCADComponent)
        assert child.name == "Child"
        assert "Child" in self.component.mcad_sub_components

    def test_add_sub_ecad_component(self):
        """Test adding child ECAD component."""
        child = self.component.add_sub_ecad_component(name="Child", model="ChildModel")

        assert isinstance(child, ECADComponent)
        assert child.name == "Child"
        assert "Child" in self.component.ecad_sub_components

    def test_add_arrange_rotate(self):
        """Test adding rotation transformation."""
        arrange = self.component.add_arrange_rotate(axis="Z", angle="90deg")

        assert isinstance(arrange, Arrange)
        assert arrange.operation == "rotate"
        assert arrange.axis == "Z"
        assert arrange.angle == "90deg"
        assert len(self.component.arranges) == 1

    def test_add_arrange_move(self):
        """Test adding translation transformation."""
        arrange = self.component.add_arrange_move(vector=("5mm", "0mm", "0mm"))

        assert isinstance(arrange, Arrange)
        assert arrange.operation == "move"
        assert arrange.vector == ["5mm", "0mm", "0mm"]
        assert len(self.component.arranges) == 1

    def test_multiple_transformations_order(self):
        """Test that transformations are applied in order."""
        self.component.add_arrange_rotate(axis="Z", angle="45deg")
        self.component.add_arrange_move(vector=("10mm", "0mm", "0mm"))
        self.component.add_arrange_rotate(axis="X", angle="90deg")

        assert len(self.component.arranges) == 3
        assert self.component.arranges[0].operation == "rotate"
        assert self.component.arranges[1].operation == "move"
        assert self.component.arranges[2].operation == "rotate"

    def test_sub_components_property(self):
        """Test sub_components property."""
        mcad_child = self.component.add_sub_mcad_component(name="MCAD_Child", model="M")
        ecad_child = self.component.add_sub_ecad_component(name="ECAD_Child", model="E")

        assert mcad_child.name == "MCAD_Child"
        assert ecad_child.name == "ECAD_Child"

        sub_comps = self.component.sub_components

        assert len(sub_comps) == 2
        assert "MCAD_Child" in sub_comps
        assert "ECAD_Child" in sub_comps


class TestECADComponent:
    """Test suite for ECADComponent class."""

    def setup_method(self):
        """Set up test fixtures."""
        self.component = ECADComponent(name="TestPCB", model="TestModel")

    def test_ecad_component_initialization(self):
        """Test ECADComponent initialization."""
        assert self.component.name == "TestPCB"
        assert self.component.model == "TestModel"
        assert self.component.component_type == "ecad"
        assert isinstance(self.component.layout_coordinate_systems, list)

    def test_add_sub_mcad_component_from_library(self):
        """Test adding MCAD components from library."""
        lib_path = "/project/libraries/standard"
        refdes = ["U1", "U2", "J1"]

        self.component.add_sub_mcad_component_from_library(library_path=lib_path, reference_designators=refdes)

        assert lib_path in self.component.model_libraries
        assert set(refdes).issubset(set(self.component._mcad_component_from_library))

    def test_add_sub_mcad_component_from_library_only_library(self):
        """Test adding library without specific designators."""
        lib_path = "/project/libraries/standard"

        self.component.add_sub_mcad_component_from_library(library_path=lib_path)

        assert lib_path in self.component.model_libraries

    def test_add_sub_mcad_component_from_library_only_designators(self):
        """Test specifying designators without library path."""
        refdes = ["R1", "C1"]

        self.component.add_sub_mcad_component_from_library(reference_designators=refdes)

        assert set(refdes).issubset(set(self.component._mcad_component_from_library))

    def test_add_sub_mcad_component_from_library_single_designator(self):
        """Test specifying single designator as string."""
        self.component.add_sub_mcad_component_from_library(reference_designators="U1")

        assert "U1" in self.component._mcad_component_from_library
