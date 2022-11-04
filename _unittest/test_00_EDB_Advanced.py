import json
import math
import os
import time

from pyaedt import Edb
from pyaedt.edb_core.edb_data.simulation_configuration import SimulationConfiguration
from pyaedt.edb_core.edb_data.sources import Source
from pyaedt.generic.constants import RadiationBoxType

# Setup paths for module imports
# Import required modules

test_project_name = "Galileo_edb"
bom_example = "bom_example.csv"
from _unittest.conftest import BasisTest
from _unittest.conftest import config
from _unittest.conftest import desktop_version
from _unittest.conftest import is_ironpython
from _unittest.conftest import local_path
from pyaedt.generic.constants import SolverType
from pyaedt.generic.constants import SourceType

try:
    import pytest
except ImportError:  # pragma: no cover
    import _unittest_ironpython.conf_unittest as pytest

test_subfolder = "TEDB"


if not config["skip_edb"]:

    class TestClass(BasisTest, object):
        def setup_class(self):
            BasisTest.my_setup(self)
            self.edbapp = BasisTest.add_edb(self, test_project_name, subfolder=test_subfolder)
            example_project = os.path.join(local_path, "example_models", test_subfolder, "Package.aedb")
            self.target_path = os.path.join(self.local_scratch.path, "Package_test_00.aedb")
            self.local_scratch.copyfolder(example_project, self.target_path)
            example_project2 = os.path.join(local_path, "example_models", test_subfolder, "simple.aedb")
            self.target_path2 = os.path.join(self.local_scratch.path, "simple_00.aedb")
            self.local_scratch.copyfolder(example_project2, self.target_path2)

        def teardown_class(self):
            self.edbapp.close_edb()
            self.local_scratch.remove()
            del self.edbapp

        def test_01_flip_layer_stackup(self):
            edb1 = Edb(self.target_path2, edbversion=desktop_version)

            edb2 = Edb(self.target_path, edbversion=desktop_version)
            assert edb2.core_stackup.place_in_layout_3d_placement(
                edb1,
                angle=0.0,
                offset_x="41.783mm",
                offset_y="35.179mm",
                flipped_stackup=False,
                place_on_top=False,
                solder_height=0.0,
            )
            edb2.close_edb()
            edb2 = Edb(self.target_path, edbversion=desktop_version)
            assert edb2.core_stackup.place_in_layout_3d_placement(
                edb1,
                angle=0.0,
                offset_x="41.783mm",
                offset_y="35.179mm",
                flipped_stackup=True,
                place_on_top=False,
                solder_height=0.0,
            )
            edb2.close_edb()
            edb2 = Edb(self.target_path, edbversion=desktop_version)
            assert edb2.core_stackup.place_in_layout_3d_placement(
                edb1,
                angle=0.0,
                offset_x="41.783mm",
                offset_y="35.179mm",
                flipped_stackup=False,
                place_on_top=True,
                solder_height=0.0,
            )
            edb2.close_edb()
            edb2 = Edb(self.target_path, edbversion=desktop_version)
            assert edb2.core_stackup.place_in_layout_3d_placement(
                edb1,
                angle=0.0,
                offset_x="41.783mm",
                offset_y="35.179mm",
                flipped_stackup=True,
                place_on_top=True,
                solder_height=0.0,
            )
            edb2.close_edb()
            edb1.close_edb()

        def test_02_flip_layer_stackup_2(self):
            edb2 = Edb(self.target_path, edbversion=desktop_version)
            assert edb2.core_stackup.place_in_layout(
                self.edbapp,
                angle=0.0,
                offset_x="41.783mm",
                offset_y="35.179mm",
                flipped_stackup=True,
                place_on_top=True,
            )
            edb2.close_edb()

        def test_03_get_placement_vector(self):
            edb2 = Edb(self.target_path, edbversion=desktop_version)
            for cmpname, cmp in edb2.core_components.components.items():
                assert isinstance(cmp.solder_ball_placement, int)
            mounted_cmp = edb2.core_components.get_component_by_name("BGA")
            hosting_cmp = self.edbapp.core_components.get_component_by_name("U2A5")
            (
                result,
                vector,
                rotation,
                solder_ball_height,
            ) = self.edbapp.core_components.get_component_placement_vector(
                mounted_component=mounted_cmp,
                hosting_component=hosting_cmp,
                mounted_component_pin1="A10",
                mounted_component_pin2="A12",
                hosting_component_pin1="A2",
                hosting_component_pin2="A4",
            )
            assert result
            assert abs(abs(rotation) - math.pi / 2) < 1e-9
            assert solder_ball_height == 0.00033
            assert len(vector) == 2
            (
                result,
                vector,
                rotation,
                solder_ball_height,
            ) = self.edbapp.core_components.get_component_placement_vector(
                mounted_component=mounted_cmp,
                hosting_component=hosting_cmp,
                mounted_component_pin1="A10",
                mounted_component_pin2="A12",
                hosting_component_pin1="A2",
                hosting_component_pin2="A4",
                flipped=True,
            )
            assert result
            assert abs(rotation + math.pi / 2) < 1e-9
            assert solder_ball_height == 0.00033
            assert len(vector) == 2
            edb2.close_edb()
            del edb2

        def test_04_edb_without_path(self):
            edbapp_without_path = Edb(edbversion=desktop_version, isreadonly=False)
            time.sleep(2)
            edbapp_without_path.close_edb()
            edbapp_without_path = None
            del edbapp_without_path

        def test_05_create_rectangle_in_pad(self):
            example_model = os.path.join(local_path, "example_models", test_subfolder, "padstacks.aedb")
            self.local_scratch.copyfolder(
                example_model,
                os.path.join(self.local_scratch.path, "padstacks2.aedb"),
            )
            edb_padstacks = Edb(
                edbpath=os.path.join(self.local_scratch.path, "padstacks2.aedb"),
                edbversion=desktop_version,
                isreadonly=True,
            )
            padstack_instances = list(edb_padstacks.core_padstack.padstack_instances.values())
            for padstack_instance in padstack_instances:
                result = padstack_instance.create_rectangle_in_pad("s")
                if padstack_instance.padstack_definition != "Padstack_None":
                    assert result
                else:
                    assert result is False
            edb_padstacks.close_edb()

        def test_06_edb_with_dxf(self):
            src = os.path.join(local_path, "example_models", test_subfolder, "edb_test_82.dxf")
            dxf_path = self.local_scratch.copyfile(src)
            edb3 = Edb(dxf_path, edbversion=desktop_version)
            edb3.close_edb()
            del edb3

        def test_07_place_on_lam_with_mold(self):
            laminateEdb = Edb(
                os.path.join(local_path, "example_models", test_subfolder, "lam_with_mold.aedb"),
                edbversion=desktop_version,
            )
            chipEdb = Edb(
                os.path.join(local_path, "example_models", test_subfolder, "chip.aedb"),
                edbversion=desktop_version,
            )
            try:
                layout = laminateEdb.active_layout
                cellInstances = list(layout.CellInstances)
                assert len(cellInstances) == 0
                assert chipEdb.core_stackup.place_in_layout_3d_placement(
                    laminateEdb,
                    angle=0.0,
                    offset_x=0.0,
                    offset_y=0.0,
                    flipped_stackup=False,
                    place_on_top=True,
                )
                merged_cell = chipEdb.edb.Cell.Cell.FindByName(
                    chipEdb.db, chipEdb.edb.Cell.CellType.CircuitCell, "lam_with_mold"
                )
                assert not merged_cell.IsNull()
                layout = merged_cell.GetLayout()
                cellInstances = list(layout.CellInstances)
                assert len(cellInstances) == 1
                cellInstance = cellInstances[0]
                assert cellInstance.Is3DPlacement()
                if is_ironpython:
                    (
                        res,
                        localOrigin,
                        rotAxisFrom,
                        rotAxisTo,
                        angle,
                        loc,
                    ) = cellInstance.Get3DTransformation()
                else:
                    (
                        res,
                        localOrigin,
                        rotAxisFrom,
                        rotAxisTo,
                        angle,
                        loc,
                    ) = cellInstance.Get3DTransformation(None, None, None, None, None)
                assert res
                zeroValue = chipEdb.edb_value(0)
                oneValue = chipEdb.edb_value(1)
                originPoint = chipEdb.edb.Geometry.Point3DData(zeroValue, zeroValue, zeroValue)
                xAxisPoint = chipEdb.edb.Geometry.Point3DData(oneValue, zeroValue, zeroValue)
                assert localOrigin.IsEqual(originPoint)
                assert rotAxisFrom.IsEqual(xAxisPoint)
                assert rotAxisTo.IsEqual(xAxisPoint)
                assert angle.IsEqual(zeroValue)
                assert loc.IsEqual(chipEdb.edb.Geometry.Point3DData(zeroValue, zeroValue, chipEdb.edb_value(170e-6)))
            finally:
                chipEdb.close_edb()
                laminateEdb.close_edb()

        def test_08_place_on_bottom_of_lam_with_mold(self):
            laminateEdb = Edb(
                os.path.join(local_path, "example_models", test_subfolder, "lam_with_mold.aedb"),
                edbversion=desktop_version,
            )
            chipEdb = Edb(
                os.path.join(local_path, "example_models", test_subfolder, "chip_flipped_stackup.aedb"),
                edbversion=desktop_version,
            )
            try:
                layout = laminateEdb.active_layout
                cellInstances = list(layout.CellInstances)
                assert len(cellInstances) == 0
                assert chipEdb.core_stackup.place_in_layout_3d_placement(
                    laminateEdb,
                    angle=0.0,
                    offset_x=0.0,
                    offset_y=0.0,
                    flipped_stackup=False,
                    place_on_top=False,
                )
                merged_cell = chipEdb.edb.Cell.Cell.FindByName(
                    chipEdb.db, chipEdb.edb.Cell.CellType.CircuitCell, "lam_with_mold"
                )
                assert not merged_cell.IsNull()
                layout = merged_cell.GetLayout()
                cellInstances = list(layout.CellInstances)
                assert len(cellInstances) == 1
                cellInstance = cellInstances[0]
                assert cellInstance.Is3DPlacement()
                if is_ironpython:
                    (
                        res,
                        localOrigin,
                        rotAxisFrom,
                        rotAxisTo,
                        angle,
                        loc,
                    ) = cellInstance.Get3DTransformation()
                else:
                    (
                        res,
                        localOrigin,
                        rotAxisFrom,
                        rotAxisTo,
                        angle,
                        loc,
                    ) = cellInstance.Get3DTransformation(None, None, None, None, None)
                assert res
                zeroValue = chipEdb.edb_value(0)
                oneValue = chipEdb.edb_value(1)
                originPoint = chipEdb.edb.Geometry.Point3DData(zeroValue, zeroValue, zeroValue)
                xAxisPoint = chipEdb.edb.Geometry.Point3DData(oneValue, zeroValue, zeroValue)
                assert localOrigin.IsEqual(originPoint)
                assert rotAxisFrom.IsEqual(xAxisPoint)
                assert rotAxisTo.IsEqual(xAxisPoint)
                assert angle.IsEqual(zeroValue)
                assert loc.IsEqual(chipEdb.edb.Geometry.Point3DData(zeroValue, zeroValue, chipEdb.edb_value(-90e-6)))
            finally:
                chipEdb.close_edb()
                laminateEdb.close_edb()

        def test_09_place_on_lam_with_mold_solder(self):
            laminateEdb = Edb(
                os.path.join(local_path, "example_models", test_subfolder, "lam_with_mold.aedb"),
                edbversion=desktop_version,
            )
            chipEdb = Edb(
                os.path.join(local_path, "example_models", test_subfolder, "chip_solder.aedb"),
                edbversion=desktop_version,
            )
            try:
                layout = laminateEdb.active_layout
                cellInstances = list(layout.CellInstances)
                assert len(cellInstances) == 0
                assert chipEdb.core_stackup.place_in_layout_3d_placement(
                    laminateEdb,
                    angle=0.0,
                    offset_x=0.0,
                    offset_y=0.0,
                    flipped_stackup=False,
                    place_on_top=True,
                )
                merged_cell = chipEdb.edb.Cell.Cell.FindByName(
                    chipEdb.db, chipEdb.edb.Cell.CellType.CircuitCell, "lam_with_mold"
                )
                assert not merged_cell.IsNull()
                layout = merged_cell.GetLayout()
                cellInstances = list(layout.CellInstances)
                assert len(cellInstances) == 1
                cellInstance = cellInstances[0]
                assert cellInstance.Is3DPlacement()
                if is_ironpython:
                    (
                        res,
                        localOrigin,
                        rotAxisFrom,
                        rotAxisTo,
                        angle,
                        loc,
                    ) = cellInstance.Get3DTransformation()
                else:
                    (
                        res,
                        localOrigin,
                        rotAxisFrom,
                        rotAxisTo,
                        angle,
                        loc,
                    ) = cellInstance.Get3DTransformation(None, None, None, None, None)
                assert res
                zeroValue = chipEdb.edb_value(0)
                oneValue = chipEdb.edb_value(1)
                originPoint = chipEdb.edb.Geometry.Point3DData(zeroValue, zeroValue, zeroValue)
                xAxisPoint = chipEdb.edb.Geometry.Point3DData(oneValue, zeroValue, zeroValue)
                assert localOrigin.IsEqual(originPoint)
                assert rotAxisFrom.IsEqual(xAxisPoint)
                assert rotAxisTo.IsEqual(xAxisPoint)
                assert angle.IsEqual(zeroValue)
                assert loc.IsEqual(chipEdb.edb.Geometry.Point3DData(zeroValue, zeroValue, chipEdb.edb_value(190e-6)))
            finally:
                chipEdb.close_edb()
                laminateEdb.close_edb()

        def test_10_place_on_bottom_of_lam_with_mold_solder(self):
            laminateEdb = Edb(
                os.path.join(local_path, "example_models", test_subfolder, "lam_with_mold.aedb"),
                edbversion=desktop_version,
            )
            chipEdb = Edb(
                os.path.join(local_path, "example_models", test_subfolder, "chip_solder.aedb"),
                edbversion=desktop_version,
            )
            try:
                layout = laminateEdb.active_layout
                cellInstances = list(layout.CellInstances)
                assert len(cellInstances) == 0
                assert chipEdb.core_stackup.place_in_layout_3d_placement(
                    laminateEdb,
                    angle=0.0,
                    offset_x=0.0,
                    offset_y=0.0,
                    flipped_stackup=True,
                    place_on_top=False,
                )
                merged_cell = chipEdb.edb.Cell.Cell.FindByName(
                    chipEdb.db, chipEdb.edb.Cell.CellType.CircuitCell, "lam_with_mold"
                )
                assert not merged_cell.IsNull()
                layout = merged_cell.GetLayout()
                cellInstances = list(layout.CellInstances)
                assert len(cellInstances) == 1
                cellInstance = cellInstances[0]
                assert cellInstance.Is3DPlacement()
                if is_ironpython:
                    (
                        res,
                        localOrigin,
                        rotAxisFrom,
                        rotAxisTo,
                        angle,
                        loc,
                    ) = cellInstance.Get3DTransformation()
                else:
                    (
                        res,
                        localOrigin,
                        rotAxisFrom,
                        rotAxisTo,
                        angle,
                        loc,
                    ) = cellInstance.Get3DTransformation(None, None, None, None, None)
                assert res
                zeroValue = chipEdb.edb_value(0)
                oneValue = chipEdb.edb_value(1)
                originPoint = chipEdb.edb.Geometry.Point3DData(zeroValue, zeroValue, zeroValue)
                xAxisPoint = chipEdb.edb.Geometry.Point3DData(oneValue, zeroValue, zeroValue)
                assert localOrigin.IsEqual(originPoint)
                assert rotAxisFrom.IsEqual(xAxisPoint)
                assert rotAxisTo.IsEqual(xAxisPoint)
                assert angle.IsEqual(chipEdb.edb_value(math.pi))
                assert loc.IsEqual(chipEdb.edb.Geometry.Point3DData(zeroValue, zeroValue, chipEdb.edb_value(-20e-6)))
            finally:
                chipEdb.close_edb()
                laminateEdb.close_edb()

        def test_11_place_zoffset_chip(self):
            laminateEdb = Edb(
                os.path.join(local_path, "example_models", test_subfolder, "lam_with_mold.aedb"),
                edbversion=desktop_version,
            )
            chipEdb = Edb(
                os.path.join(local_path, "example_models", test_subfolder, "chip_zoffset.aedb"),
                edbversion=desktop_version,
            )
            try:
                layout = laminateEdb.active_layout
                cellInstances = list(layout.CellInstances)
                assert len(cellInstances) == 0
                assert chipEdb.core_stackup.place_in_layout_3d_placement(
                    laminateEdb,
                    angle=0.0,
                    offset_x=0.0,
                    offset_y=0.0,
                    flipped_stackup=False,
                    place_on_top=True,
                )
                merged_cell = chipEdb.edb.Cell.Cell.FindByName(
                    chipEdb.db, chipEdb.edb.Cell.CellType.CircuitCell, "lam_with_mold"
                )
                assert not merged_cell.IsNull()
                layout = merged_cell.GetLayout()
                cellInstances = list(layout.CellInstances)
                assert len(cellInstances) == 1
                cellInstance = cellInstances[0]
                assert cellInstance.Is3DPlacement()
                if is_ironpython:
                    (
                        res,
                        localOrigin,
                        rotAxisFrom,
                        rotAxisTo,
                        angle,
                        loc,
                    ) = cellInstance.Get3DTransformation()
                else:
                    (
                        res,
                        localOrigin,
                        rotAxisFrom,
                        rotAxisTo,
                        angle,
                        loc,
                    ) = cellInstance.Get3DTransformation(None, None, None, None, None)
                assert res
                zeroValue = chipEdb.edb_value(0)
                oneValue = chipEdb.edb_value(1)
                originPoint = chipEdb.edb.Geometry.Point3DData(zeroValue, zeroValue, zeroValue)
                xAxisPoint = chipEdb.edb.Geometry.Point3DData(oneValue, zeroValue, zeroValue)
                assert localOrigin.IsEqual(originPoint)
                assert rotAxisFrom.IsEqual(xAxisPoint)
                assert rotAxisTo.IsEqual(xAxisPoint)
                assert angle.IsEqual(zeroValue)
                assert loc.IsEqual(chipEdb.edb.Geometry.Point3DData(zeroValue, zeroValue, chipEdb.edb_value(160e-6)))
            finally:
                chipEdb.close_edb()
                laminateEdb.close_edb()

        def test_12_place_on_bottom_zoffset_chip(self):
            laminateEdb = Edb(
                os.path.join(local_path, "example_models", test_subfolder, "lam_with_mold.aedb"),
                edbversion=desktop_version,
            )
            chipEdb = Edb(
                os.path.join(local_path, "example_models", test_subfolder, "chip_zoffset.aedb"),
                edbversion=desktop_version,
            )
            try:
                layout = laminateEdb.active_layout
                cellInstances = list(layout.CellInstances)
                assert len(cellInstances) == 0
                assert chipEdb.core_stackup.place_in_layout_3d_placement(
                    laminateEdb,
                    angle=0.0,
                    offset_x=0.0,
                    offset_y=0.0,
                    flipped_stackup=True,
                    place_on_top=False,
                )
                merged_cell = chipEdb.edb.Cell.Cell.FindByName(
                    chipEdb.db, chipEdb.edb.Cell.CellType.CircuitCell, "lam_with_mold"
                )
                assert not merged_cell.IsNull()
                layout = merged_cell.GetLayout()
                cellInstances = list(layout.CellInstances)
                assert len(cellInstances) == 1
                cellInstance = cellInstances[0]
                assert cellInstance.Is3DPlacement()
                if is_ironpython:
                    (
                        res,
                        localOrigin,
                        rotAxisFrom,
                        rotAxisTo,
                        angle,
                        loc,
                    ) = cellInstance.Get3DTransformation()
                else:
                    (
                        res,
                        localOrigin,
                        rotAxisFrom,
                        rotAxisTo,
                        angle,
                        loc,
                    ) = cellInstance.Get3DTransformation(None, None, None, None, None)
                assert res
                zeroValue = chipEdb.edb_value(0)
                oneValue = chipEdb.edb_value(1)
                originPoint = chipEdb.edb.Geometry.Point3DData(zeroValue, zeroValue, zeroValue)
                xAxisPoint = chipEdb.edb.Geometry.Point3DData(oneValue, zeroValue, zeroValue)
                assert localOrigin.IsEqual(originPoint)
                assert rotAxisFrom.IsEqual(xAxisPoint)
                assert rotAxisTo.IsEqual(xAxisPoint)
                assert angle.IsEqual(chipEdb.edb_value(math.pi))
                assert loc.IsEqual(chipEdb.edb.Geometry.Point3DData(zeroValue, zeroValue, chipEdb.edb_value(10e-6)))
            finally:
                chipEdb.close_edb()
                laminateEdb.close_edb()

        def test_13_place_zoffset_solder_chip(self):
            laminateEdb = Edb(
                os.path.join(local_path, "example_models", test_subfolder, "lam_with_mold.aedb"),
                edbversion=desktop_version,
            )
            chipEdb = Edb(
                os.path.join(local_path, "example_models", test_subfolder, "chip_zoffset_solder.aedb"),
                edbversion=desktop_version,
            )
            try:
                layout = laminateEdb.active_layout
                cellInstances = list(layout.CellInstances)
                assert len(cellInstances) == 0
                assert chipEdb.core_stackup.place_in_layout_3d_placement(
                    laminateEdb,
                    angle=0.0,
                    offset_x=0.0,
                    offset_y=0.0,
                    flipped_stackup=False,
                    place_on_top=True,
                )
                merged_cell = chipEdb.edb.Cell.Cell.FindByName(
                    chipEdb.db, chipEdb.edb.Cell.CellType.CircuitCell, "lam_with_mold"
                )
                assert not merged_cell.IsNull()
                layout = merged_cell.GetLayout()
                cellInstances = list(layout.CellInstances)
                assert len(cellInstances) == 1
                cellInstance = cellInstances[0]
                assert cellInstance.Is3DPlacement()
                if is_ironpython:
                    (
                        res,
                        localOrigin,
                        rotAxisFrom,
                        rotAxisTo,
                        angle,
                        loc,
                    ) = cellInstance.Get3DTransformation()
                else:
                    (
                        res,
                        localOrigin,
                        rotAxisFrom,
                        rotAxisTo,
                        angle,
                        loc,
                    ) = cellInstance.Get3DTransformation(None, None, None, None, None)
                assert res
                zeroValue = chipEdb.edb_value(0)
                oneValue = chipEdb.edb_value(1)
                originPoint = chipEdb.edb.Geometry.Point3DData(zeroValue, zeroValue, zeroValue)
                xAxisPoint = chipEdb.edb.Geometry.Point3DData(oneValue, zeroValue, zeroValue)
                assert localOrigin.IsEqual(originPoint)
                assert rotAxisFrom.IsEqual(xAxisPoint)
                assert rotAxisTo.IsEqual(xAxisPoint)
                assert angle.IsEqual(zeroValue)
                assert loc.IsEqual(chipEdb.edb.Geometry.Point3DData(zeroValue, zeroValue, chipEdb.edb_value(150e-6)))
            finally:
                chipEdb.close_edb()
                laminateEdb.close_edb()

        def test_14_place_on_bottom_zoffset_solder_chip(self):
            laminateEdb = Edb(
                os.path.join(local_path, "example_models", test_subfolder, "lam_with_mold.aedb"),
                edbversion=desktop_version,
            )
            chipEdb = Edb(
                os.path.join(local_path, "example_models", test_subfolder, "chip_zoffset_solder.aedb"),
                edbversion=desktop_version,
            )
            try:
                layout = laminateEdb.active_layout
                cellInstances = list(layout.CellInstances)
                assert len(cellInstances) == 0
                assert chipEdb.core_stackup.place_in_layout_3d_placement(
                    laminateEdb,
                    angle=0.0,
                    offset_x=0.0,
                    offset_y=0.0,
                    flipped_stackup=True,
                    place_on_top=False,
                )
                merged_cell = chipEdb.edb.Cell.Cell.FindByName(
                    chipEdb.db, chipEdb.edb.Cell.CellType.CircuitCell, "lam_with_mold"
                )
                assert not merged_cell.IsNull()
                layout = merged_cell.GetLayout()
                cellInstances = list(layout.CellInstances)
                assert len(cellInstances) == 1
                cellInstance = cellInstances[0]
                assert cellInstance.Is3DPlacement()
                if is_ironpython:
                    (
                        res,
                        localOrigin,
                        rotAxisFrom,
                        rotAxisTo,
                        angle,
                        loc,
                    ) = cellInstance.Get3DTransformation()
                else:
                    (
                        res,
                        localOrigin,
                        rotAxisFrom,
                        rotAxisTo,
                        angle,
                        loc,
                    ) = cellInstance.Get3DTransformation(None, None, None, None, None)
                assert res
                zeroValue = chipEdb.edb_value(0)
                oneValue = chipEdb.edb_value(1)
                originPoint = chipEdb.edb.Geometry.Point3DData(zeroValue, zeroValue, zeroValue)
                xAxisPoint = chipEdb.edb.Geometry.Point3DData(oneValue, zeroValue, zeroValue)
                assert localOrigin.IsEqual(originPoint)
                assert rotAxisFrom.IsEqual(xAxisPoint)
                assert rotAxisTo.IsEqual(xAxisPoint)
                assert angle.IsEqual(chipEdb.edb_value(math.pi))
                assert loc.IsEqual(chipEdb.edb.Geometry.Point3DData(zeroValue, zeroValue, chipEdb.edb_value(20e-6)))
            finally:
                chipEdb.close_edb()
                laminateEdb.close_edb()

        def test_15_build_siwave_project_from_config_file(self):
            example_project = os.path.join(local_path, "example_models", test_subfolder, "Galileo.aedb")
            self.target_path = os.path.join(self.local_scratch.path, "Galileo.aedb")
            self.local_scratch.copyfolder(example_project, self.target_path)
            cfg_file = os.path.join(self.target_path, "test.cfg")
            with open(cfg_file, "w") as f:
                f.writelines("SolverType = 'SiwaveSYZ'\n")
                f.writelines("PowerNets = ['GND']\n")
                f.writelines("Components = ['U2A5', 'U1B5']")
            sim_config = SimulationConfiguration(cfg_file)
            edb = Edb(self.target_path)
            assert edb.build_simulation_project(sim_config)
            edb.close_edb()

        def test_16_create_symmetric_stackup(self):
            app_edb = Edb(edbversion=desktop_version)
            assert not app_edb.core_stackup.create_symmetric_stackup(9)
            assert app_edb.core_stackup.create_symmetric_stackup(8)
            app_edb.close_edb()

            app_edb = Edb(edbversion=desktop_version)
            assert app_edb.core_stackup.create_symmetric_stackup(8, soldermask=False)
            app_edb.close_edb()
            app_edb = Edb(edbversion=desktop_version)
            assert not app_edb.stackup.create_symmetric_stackup(9)
            assert app_edb.stackup.create_symmetric_stackup(8)
            app_edb.close_edb()

            app_edb = Edb(edbversion=desktop_version)
            assert app_edb.stackup.create_symmetric_stackup(8, soldermask=False)
            app_edb.close_edb()

        def test_17_export_import_json_for_config(self):
            sim_config = SimulationConfiguration()
            assert sim_config.output_aedb is None
            sim_config.output_aedb = os.path.join(self.local_scratch.path, "test.aedb")
            assert sim_config.output_aedb == os.path.join(self.local_scratch.path, "test.aedb")
            json_file = os.path.join(self.local_scratch.path, "test.json")
            sim_config._filename = json_file
            sim_config.arc_angle = "90deg"
            assert sim_config.export_json(json_file)
            test_import = SimulationConfiguration()
            assert test_import.import_json(json_file)
            assert test_import.arc_angle == "90deg"
            assert test_import._filename == json_file

        def test_18_duplicate_material(self):
            stack_up = self.edbapp.core_stackup
            duplicated_copper = stack_up.duplicate_material("copper", "my_new_copper")
            assert duplicated_copper
            duplicated_fr4_epoxy = stack_up.duplicate_material("FR4_epoxy", "my_new_FR4")
            assert duplicated_fr4_epoxy
            duplicated_pec = stack_up.duplicate_material("pec", "my_new_pec")
            assert duplicated_pec
            cloned_permittivity = stack_up.get_property_by_material_name("permittivity", "my_new_pec")
            permittivity = stack_up.get_property_by_material_name("permittivity", "pec")
            cloned_permeability = stack_up.get_property_by_material_name("permeability", "my_new_pec")
            permeability = stack_up.get_property_by_material_name("permeability", "pec")
            cloned_conductivity = stack_up.get_property_by_material_name("conductivity", "my_new_pec")
            conductivity = stack_up.get_property_by_material_name("conductivity", "pec")
            cloned_dielectric_loss = stack_up.get_property_by_material_name("dielectric_loss_tangent", "my_new_pec")
            dielectric_loss = stack_up.get_property_by_material_name("dielectric_loss_tangent", "pec")
            cloned_magnetic_loss = stack_up.get_property_by_material_name("magnetic_loss_tangent", "my_new_pec")
            magnetic_loss = stack_up.get_property_by_material_name("magnetic_loss_tangent", "pec")
            assert cloned_permittivity == permittivity
            assert cloned_permeability == permeability
            assert cloned_conductivity == conductivity
            assert cloned_dielectric_loss == dielectric_loss
            assert cloned_magnetic_loss == magnetic_loss
            non_duplicated = stack_up.duplicate_material("my_nonexistent_mat", "nothing")
            assert not non_duplicated

        def test_19_get_property_by_material_name(self):
            stack_up = self.edbapp.core_stackup
            permittivity = stack_up.get_property_by_material_name("permittivity", "FR4_epoxy")
            permeability = stack_up.get_property_by_material_name("permeability", "FR4_epoxy")
            conductivity = stack_up.get_property_by_material_name("conductivity", "copper")
            dielectric_loss = stack_up.get_property_by_material_name("dielectric_loss_tangent", "FR4_epoxy")
            magnetic_loss = stack_up.get_property_by_material_name("magnetic_loss_tangent", "FR4_epoxy")
            assert permittivity == 4.4
            assert permeability == 0
            assert conductivity == 59590000
            assert dielectric_loss == 0.02
            assert magnetic_loss == 0
            failing_test_1 = stack_up.get_property_by_material_name("magnetic_loss_tangent", "inexistent_material")
            assert not failing_test_1
            failing_test_2 = stack_up.get_property_by_material_name("none_property", "copper")
            assert not failing_test_2

        def test_20_classify_nets(self):
            sim_setup = SimulationConfiguration()
            sim_setup.power_nets = ["RSVD_0", "RSVD_1"]
            sim_setup.signal_nets = ["V3P3_S0"]
            self.edbapp.core_nets.classify_nets(sim_setup)

        def test_21_place_a3dcomp_3d_placement(self):
            source_path = os.path.join(local_path, "example_models", test_subfolder, "lam_for_bottom_place.aedb")
            target_path = os.path.join(self.local_scratch.path, "output.aedb")
            self.local_scratch.copyfolder(source_path, target_path)
            laminate_edb = Edb(target_path, edbversion=desktop_version)
            chip_a3dcomp = os.path.join(local_path, "example_models", test_subfolder, "chip.a3dcomp")
            try:
                layout = laminate_edb.active_layout
                cell_instances = list(layout.CellInstances)
                assert len(cell_instances) == 0
                assert laminate_edb.core_stackup.place_a3dcomp_3d_placement(
                    chip_a3dcomp,
                    angle=0.0,
                    offset_x=0.0,
                    offset_y=0.0,
                    place_on_top=True,
                )
                cell_instances = list(layout.CellInstances)
                assert len(cell_instances) == 1
                cell_instance = cell_instances[0]
                assert cell_instance.Is3DPlacement()
                if is_ironpython:
                    (
                        res,
                        local_origin,
                        rotation_axis_from,
                        rotation_axis_to,
                        angle,
                        loc,
                    ) = cell_instance.Get3DTransformation()
                else:
                    (
                        res,
                        local_origin,
                        rotation_axis_from,
                        rotation_axis_to,
                        angle,
                        loc,
                    ) = cell_instance.Get3DTransformation(None, None, None, None, None)
                assert res
                zero_value = laminate_edb.edb_value(0)
                one_value = laminate_edb.edb_value(1)
                origin_point = laminate_edb.edb.Geometry.Point3DData(zero_value, zero_value, zero_value)
                x_axis_point = laminate_edb.edb.Geometry.Point3DData(one_value, zero_value, zero_value)
                assert local_origin.IsEqual(origin_point)
                assert rotation_axis_from.IsEqual(x_axis_point)
                assert rotation_axis_to.IsEqual(x_axis_point)
                assert angle.IsEqual(zero_value)
                assert loc.IsEqual(
                    laminate_edb.edb.Geometry.Point3DData(zero_value, zero_value, laminate_edb.edb_value(170e-6))
                )
                assert laminate_edb.save_edb()
            finally:
                laminate_edb.close_edb()

        def test_22_place_a3dcomp_3d_placement_on_bottom(self):
            source_path = os.path.join(local_path, "example_models", test_subfolder, "lam_for_bottom_place.aedb")
            target_path = os.path.join(self.local_scratch.path, "output.aedb")
            self.local_scratch.copyfolder(source_path, target_path)
            laminate_edb = Edb(target_path, edbversion=desktop_version)
            chip_a3dcomp = os.path.join(local_path, "example_models", test_subfolder, "chip.a3dcomp")
            try:
                layout = laminate_edb.active_layout
                cell_instances = list(layout.CellInstances)
                assert len(cell_instances) == 0
                assert laminate_edb.core_stackup.place_a3dcomp_3d_placement(
                    chip_a3dcomp,
                    angle=90.0,
                    offset_x=0.5e-3,
                    offset_y=-0.5e-3,
                    place_on_top=False,
                )
                cell_instances = list(layout.CellInstances)
                assert len(cell_instances) == 1
                cell_instance = cell_instances[0]
                assert cell_instance.Is3DPlacement()
                if is_ironpython:
                    (
                        res,
                        local_origin,
                        rotation_axis_from,
                        rotation_axis_to,
                        angle,
                        loc,
                    ) = cell_instance.Get3DTransformation()
                else:
                    (
                        res,
                        local_origin,
                        rotation_axis_from,
                        rotation_axis_to,
                        angle,
                        loc,
                    ) = cell_instance.Get3DTransformation(None, None, None, None, None)
                assert res
                zero_value = laminate_edb.edb_value(0)
                one_value = laminate_edb.edb_value(1)
                flip_angle_value = laminate_edb.edb_value("180deg")
                origin_point = laminate_edb.edb.Geometry.Point3DData(zero_value, zero_value, zero_value)
                x_axis_point = laminate_edb.edb.Geometry.Point3DData(one_value, zero_value, zero_value)
                assert local_origin.IsEqual(origin_point)
                assert rotation_axis_from.IsEqual(x_axis_point)
                assert rotation_axis_to.IsEqual(
                    laminate_edb.edb.Geometry.Point3DData(zero_value, laminate_edb.edb_value(-1.0), zero_value)
                )
                assert angle.IsEqual(flip_angle_value)
                assert loc.IsEqual(
                    laminate_edb.edb.Geometry.Point3DData(
                        laminate_edb.edb_value(0.5e-3),
                        laminate_edb.edb_value(-0.5e-3),
                        zero_value,
                    )
                )
                assert laminate_edb.save_edb()
            finally:
                laminate_edb.close_edb()

        def test_23_create_edge_ports(self):
            edb = Edb(
                edbpath=os.path.join(local_path, "example_models", test_subfolder, "edge_ports.aedb"),
                edbversion=desktop_version,
            )
            poly_list = [poly for poly in list(edb.active_layout.Primitives) if int(poly.GetPrimitiveType()) == 2]
            port_poly = [poly for poly in poly_list if poly.GetId() == 17][0]
            ref_poly = [poly for poly in poly_list if poly.GetId() == 19][0]
            port_location = [-65e-3, -13e-3]
            ref_location = [-63e-3, -13e-3]
            assert edb.core_hfss.create_edge_port_on_polygon(
                polygon=port_poly,
                reference_polygon=ref_poly,
                terminal_point=port_location,
                reference_point=ref_location,
            )
            port_poly = [poly for poly in poly_list if poly.GetId() == 23][0]
            ref_poly = [poly for poly in poly_list if poly.GetId() == 22][0]
            port_location = [-65e-3, -10e-3]
            ref_location = [-65e-3, -10e-3]
            assert edb.core_hfss.create_edge_port_on_polygon(
                polygon=port_poly,
                reference_polygon=ref_poly,
                terminal_point=port_location,
                reference_point=ref_location,
            )
            port_poly = [poly for poly in poly_list if poly.GetId() == 25][0]
            port_location = [-65e-3, -7e-3]
            assert edb.core_hfss.create_edge_port_on_polygon(
                polygon=port_poly, terminal_point=port_location, reference_layer="gnd"
            )
            edb.close_edb()

        def test_24_create_dc_simulation(self):
            edb = Edb(
                edbpath=os.path.join(local_path, "example_models", test_subfolder, "dc_flow.aedb"),
                edbversion=desktop_version,
            )
            sim_setup = SimulationConfiguration()
            sim_setup.do_cutout_subdesign = False
            sim_setup.solver_type = SolverType.SiwaveDC
            sim_setup.add_voltage_source(
                positive_node_component="Q3",
                positive_node_net="SOURCE_HBA_PHASEA",
                negative_node_component="Q3",
                negative_node_net="HV_DC+",
            )
            sim_setup.add_current_source(
                name="I25",
                positive_node_component="Q5",
                positive_node_net="SOURCE_HBB_PHASEB",
                negative_node_component="Q5",
                negative_node_net="HV_DC+",
            )
            assert len(sim_setup.sources) == 2
            assert edb.build_simulation_project(sim_setup)
            edb.close_edb()

        def test_25_add_soure(self):
            example_project = os.path.join(local_path, "example_models", test_subfolder, "Galileo.aedb")
            self.target_path = os.path.join(self.local_scratch.path, "test_create_source", "Galileo.aedb")
            self.local_scratch.copyfolder(example_project, self.target_path)
            sim_config = SimulationConfiguration()
            sim_config.add_voltage_source(
                name="test_v_source",
                positive_node_component="U2A5",
                positive_node_net="V3P3_S0",
                negative_node_component="U2A5",
                negative_node_net="GND",
            )
            sim_config.add_current_source(
                positive_node_component="U2A5",
                positive_node_net="V1P5_S0",
                negative_node_component="U2A5",
                negative_node_net="GND",
            )
            sim_config.add_dc_ground_source_term("test_v_source", 1)
            assert sim_config.dc_source_terms_to_ground["test_v_source"] == 1
            assert len(sim_config.sources) == 2

        def test_26_layout_tchickness(self):
            assert self.edbapp.core_stackup.get_layout_thickness()

        def test_27_get_layout_stats(self):
            assert self.edbapp.get_statistics()

        def test_28_edb_stats(self):
            example_project = os.path.join(local_path, "example_models", test_subfolder, "Galileo.aedb")
            target_path = os.path.join(self.local_scratch.path, "Galileo_110.aedb")
            self.local_scratch.copyfolder(example_project, target_path)
            edb = Edb(target_path, edbversion=desktop_version)
            edb_stats = edb.get_statistics(compute_area=True)
            assert edb_stats
            assert edb_stats.num_layers
            assert edb_stats.stackup_thickness
            assert edb_stats.num_vias
            assert edb_stats.occupying_ratio
            assert edb_stats.occupying_surface
            assert edb_stats.layout_size
            assert edb_stats.num_polygons
            assert edb_stats.num_traces
            assert edb_stats.num_nets
            assert edb_stats.num_discrete_components
            assert edb_stats.num_inductors
            assert edb_stats.num_capacitors
            assert edb_stats.num_resistors

        def test_29_set_bounding_box_extent(self):
            source_path = os.path.join(local_path, "example_models", test_subfolder, "test_107.aedb")
            target_path = os.path.join(self.local_scratch.path, "test_111.aedb")
            self.local_scratch.copyfolder(source_path, target_path)
            edb = Edb(target_path)
            initial_extent_info = edb.active_cell.GetHFSSExtentInfo()
            assert initial_extent_info.ExtentType == edb.edb.Utility.HFSSExtentInfoType.Conforming
            config = SimulationConfiguration()
            config.radiation_box = RadiationBoxType.BoundingBox
            assert edb.core_hfss.configure_hfss_extents(config)
            final_extent_info = edb.active_cell.GetHFSSExtentInfo()
            assert final_extent_info.ExtentType == edb.edb.Utility.HFSSExtentInfoType.BoundingBox

        def test_30_create_source(self):
            source = Source()
            source.l_value = 1e-9
            assert source.l_value == 1e-9
            source.r_value = 1.3
            assert source.r_value == 1.3
            source.c_value = 1e-13
            assert source.c_value == 1e-13
            source.create_physical_resistor = True
            assert source.create_physical_resistor

        def test_31_create_rlc(self):
            sim_config = SimulationConfiguration()
            sim_config.add_rlc(
                "test",
                r_value=1.5,
                c_value=1e-13,
                l_value=1e-10,
                positive_node_net="test_net",
                positive_node_component="U2",
                negative_node_net="neg_net",
                negative_node_component="U2",
            )
            assert sim_config.sources
            assert sim_config.sources[0].source_type == SourceType.Rlc
            assert sim_config.sources[0].r_value == 1.5
            assert sim_config.sources[0].l_value == 1e-10
            assert sim_config.sources[0].c_value == 1e-13

        def test_32_create_rlc_component(self):
            example_project = os.path.join(local_path, "example_models", test_subfolder, "Galileo.aedb")
            target_path = os.path.join(self.local_scratch.path, "Galileo_114.aedb")
            self.local_scratch.copyfolder(example_project, target_path)
            edb = Edb(target_path, edbversion=desktop_version)
            pins = edb.core_components.get_pin_from_component("U2A5", "V1P5_S0")
            ref_pins = edb.core_components.get_pin_from_component("U2A5", "GND")
            assert edb.core_components.create_rlc_component(
                [pins[0], ref_pins[0]], "test_rlc", r_value=1.67, l_value=1e-13, c_value=1e-11
            )
            edb.close_edb()

        def test_33_create_rlc_boundary(self):
            example_project = os.path.join(local_path, "example_models", test_subfolder, "Galileo.aedb")
            target_path = os.path.join(self.local_scratch.path, "Galileo_115.aedb")
            if not os.path.exists(self.local_scratch.path):
                os.mkdir(self.local_scratch.path)
            self.local_scratch.copyfolder(example_project, target_path)
            edb = Edb(target_path, edbversion=desktop_version)
            pins = edb.core_components.get_pin_from_component("U2A5", "V1P5_S0")
            ref_pins = edb.core_components.get_pin_from_component("U2A5", "GND")
            assert edb.core_hfss.create_rlc_boundary_on_pins(
                pins[0], ref_pins[0], rvalue=1.05, lvalue=1.05e-12, cvalue=1.78e-13
            )
            edb.close_edb()

        def test_34_configure_hfss_analysis_setup_enforce_causality(self):
            source_path = os.path.join(local_path, "example_models", test_subfolder, "lam_for_top_place_no_setups.aedb")
            target_path = os.path.join(self.local_scratch.path, "lam_for_top_place_no_setups_t116.aedb")
            if not os.path.exists(self.local_scratch.path):
                os.mkdir(self.local_scratch.path)
            self.local_scratch.copyfolder(source_path, target_path)
            edb = Edb(target_path)
            assert len(list(edb.active_cell.SimulationSetups)) == 0
            sim_config = SimulationConfiguration()
            sim_config.enforce_causality = False
            assert sim_config.do_lambda_refinement
            sim_config.mesh_sizefactor = 0.1
            assert sim_config.mesh_sizefactor == 0.1
            assert not sim_config.do_lambda_refinement
            edb.core_hfss.configure_hfss_analysis_setup(sim_config)
            assert len(list(edb.active_cell.SimulationSetups)) == 1
            setup = list(edb.active_cell.SimulationSetups)[0]
            ssi = setup.GetSimSetupInfo()
            assert len(list(ssi.SweepDataList)) == 1
            sweep = list(ssi.SweepDataList)[0]
            assert not sweep.EnforceCausality

        def test_35_add_hfss_config(self):
            source_path = os.path.join(local_path, "example_models", test_subfolder, "Galileo.aedb")
            target_path = os.path.join(self.local_scratch.path, "test_117.aedb")
            self.local_scratch.copyfolder(source_path, target_path)
            edb = Edb(target_path)
            sim_setup = SimulationConfiguration()
            sim_setup.mesh_sizefactor = 1.9
            assert not sim_setup.do_lambda_refinement
            edb.core_hfss.configure_hfss_analysis_setup(sim_setup)
            if is_ironpython:
                mesh_size_factor = (
                    list(edb.active_cell.SimulationSetups)[0]
                    .GetSimSetupInfo()
                    .SimulationSettings.InitialMeshSettings.MeshSizefactor
                )
            else:
                mesh_size_factor = (
                    list(edb.active_cell.SimulationSetups)[0]
                    .GetSimSetupInfo()
                    .get_SimulationSettings()
                    .get_InitialMeshSettings()
                    .get_MeshSizefactor()
                )
            assert mesh_size_factor == 1.9

        def test_36_edb_create_port(self):
            edb = Edb(
                edbpath=os.path.join(local_path, "example_models", "edb_edge_ports.aedb"),
                edbversion=desktop_version,
            )
            prim_1_id = [i.id for i in edb.core_primitives.primitives if i.net_name == "trace_2"][0]
            assert edb.core_hfss.create_edge_port_vertical(prim_1_id, ["-66mm", "-4mm"], "port_ver")

            prim_2_id = [i.id for i in edb.core_primitives.primitives if i.net_name == "trace_3"][0]
            assert edb.core_hfss.create_edge_port_horizontal(
                prim_1_id, ["-60mm", "-4mm"], prim_2_id, ["-59mm", "-4mm"], "port_hori", 30, "Lower"
            )
            assert edb.core_hfss.get_ports_number() == 2
            port_ver = edb.core_hfss.excitations["port_ver"]
            assert port_ver.hfss_type == "Gap"
            assert isinstance(port_ver.horizontal_extent_factor, float)
            assert isinstance(port_ver.vertical_extent_factor, float)
            assert isinstance(port_ver.radial_extent_factor, float)
            assert port_ver.pec_launch_width
            edb.close_edb()

        def test_37_insert_layer(self):
            layers = self.edbapp.core_stackup.stackup_layers
            layer = layers.insert_layer_above("NewLayer", "TOP", "copper", "air", "10um", 0, roughness_enabled=True)
            assert layer.name in layers.layers

        def test_38_build_hfss_project_from_config_file(self):
            cfg_file = os.path.join(os.path.dirname(self.edbapp.edbpath), "test.cfg")
            with open(cfg_file, "w") as f:
                f.writelines("SolverType = 'Hfss3dLayout'\n")
                f.writelines("PowerNets = ['GND']\n")
                f.writelines("Components = ['U2A5', 'U1B5']")

            sim_config = SimulationConfiguration(cfg_file)
            assert self.edbapp.build_simulation_project(sim_config)

        def test_39_set_all_antipad_values(self):
            source_path = os.path.join(local_path, "example_models", test_subfolder, "Galileo.aedb")
            target_path = os.path.join(self.local_scratch.path, "test_120.aedb")
            self.local_scratch.copyfolder(source_path, target_path)
            assert self.edbapp.core_padstack.set_all_antipad_value(0.0)

        def test_40_stackup(self):
            target_path = os.path.join(local_path, "example_models", test_subfolder, "Galileo.aedb")
            edbapp = Edb(target_path, edbversion=desktop_version)
            assert isinstance(edbapp.stackup.layers, dict)
            assert isinstance(edbapp.stackup.signal_layers, dict)
            assert isinstance(edbapp.stackup.stackup_layers, dict)
            assert isinstance(edbapp.stackup.non_stackup_layers, dict)
            assert not edbapp.stackup["Outline"].is_stackup_layer
            assert edbapp.stackup["TOP"].conductivity
            assert edbapp.stackup["UNNAMED_002"].permittivity
            assert edbapp.stackup.add_layer("new_layer")
            new_layer = edbapp.stackup["new_layer"]
            assert new_layer.is_stackup_layer
            new_layer.name = "renamed_layer"
            assert new_layer.name == "renamed_layer"
            rename_layer = edbapp.stackup["renamed_layer"]
            rename_layer.thickness = 50e-6
            assert rename_layer.thickness == 50e-6
            rename_layer.etch_factor = 0
            rename_layer.etch_factor = 2
            assert rename_layer.etch_factor == 2
            assert rename_layer.material
            assert rename_layer.type
            assert rename_layer.dielectric_fill

            rename_layer.roughness_enabled = True
            assert rename_layer.roughness_enabled
            rename_layer.roughness_enabled = False
            assert not rename_layer.roughness_enabled
            assert rename_layer.assign_roughness_model("groisse", groisse_roughness="2um")
            assert rename_layer.assign_roughness_model(apply_on_surface="top")
            assert rename_layer.assign_roughness_model(apply_on_surface="bottom")
            assert rename_layer.assign_roughness_model(apply_on_surface="side")
            assert edbapp.stackup.add_layer("new_above", "TOP", "insert_above")
            assert edbapp.stackup.add_layer("new_below", "TOP", "insert_below")
            assert edbapp.stackup.add_layer("new_bottom", "TOP", "add_on_bottom", "dielectric")
            assert edbapp.stackup.remove_layer("new_bottom")
            assert "new_bottom" not in edbapp.stackup.layers

            assert edbapp.stackup["TOP"].color
            edbapp.stackup["TOP"].color = [0, 120, 0]
            assert edbapp.stackup["TOP"].color == (0, 120, 0)
            edbapp.close_edb()

        @pytest.mark.skipif(is_ironpython, reason="Requires Pandas")
        def test_41_stackup(self):
            edbapp = Edb(edbversion=desktop_version)
            assert edbapp.stackup.add_layer("TOP", None, "add_on_top", material="iron")
            assert edbapp.stackup.import_stackup(
                os.path.join(local_path, "example_models", test_subfolder, "galileo_stackup.csv")
            )
            assert "TOP" in edbapp.stackup.layers.keys()
            assert edbapp.stackup.layers["TOP"].material == "COPPER"
            assert edbapp.stackup.layers["TOP"].thickness == 6e-5
            export_stackup_path = os.path.join(self.local_scratch.path, "export_galileo_stackup.csv")
            assert edbapp.stackup.export_stackup(export_stackup_path)
            assert os.path.exists(export_stackup_path)
            edbapp.close_edb()

        @pytest.mark.skipif(is_ironpython, reason="Requires Numpy")
        def test_42_comp_def(self):
            assert self.edbapp.core_components.components
            assert self.edbapp.core_components.definitions
            comp_def = self.edbapp.core_components.definitions["G83568-001"]
            assert comp_def
            comp_def.part_name = "G83568-001x"
            assert comp_def.part_name == "G83568-001x"
            assert len(comp_def.components) > 0
            cap = self.edbapp.core_components.definitions["602431-005"]
            assert cap.type == "Capacitor"
            cap.type = "Resistor"
            assert cap.type == "Resistor"

            export_path = os.path.join(self.local_scratch.path, "comp_definition.csv")
            assert self.edbapp.core_components.export_definition(export_path)
            assert self.edbapp.core_components.import_definition(export_path)

            assert self.edbapp.core_components.definitions["602431-005"].assign_rlc_model(1, 2, 3)
            sparam_path = os.path.join(local_path, "example_models", test_subfolder, "GRM32_DC0V_25degC_series.s2p")
            assert self.edbapp.core_components.definitions["602433-026"].assign_s_param_model(sparam_path)
            spice_path = os.path.join(local_path, "example_models", test_subfolder, "GRM32_DC0V_25degC.mod")
            assert self.edbapp.core_components.definitions["602433-038"].assign_spice_model(spice_path)

        def test_43_material(self):
            target_path = os.path.join(local_path, "example_models", test_subfolder, "Galileo.aedb")
            edbapp = Edb(target_path, edbversion=desktop_version)
            assert isinstance(edbapp.materials.materials, dict)
            edbapp.materials["FR4_epoxy"].conductivity = 1
            assert edbapp.materials["FR4_epoxy"].conductivity == 1
            edbapp.materials["FR4_epoxy"].permittivity = 1
            assert edbapp.materials["FR4_epoxy"].permittivity == 1
            edbapp.materials["FR4_epoxy"].loss_tangent = 1
            assert edbapp.materials["FR4_epoxy"].loss_tangent == 1
            edbapp.materials.add_conductor_material("new_conductor", 1)
            assert not edbapp.materials.add_conductor_material("new_conductor", 1)
            edbapp.materials.add_dielectric_material("new_dielectric", 1, 2)
            assert not edbapp.materials.add_dielectric_material("new_dielectric", 1, 2)
            edbapp.materials["FR4_epoxy"].magnetic_loss_tangent = 0.01
            assert edbapp.materials["FR4_epoxy"].magnetic_loss_tangent == 0.01
            edbapp.materials["FR4_epoxy"].youngs_modulus = 5000
            assert edbapp.materials["FR4_epoxy"].youngs_modulus == 5000
            edbapp.materials["FR4_epoxy"].mass_density = 50

            assert edbapp.materials["FR4_epoxy"].mass_density == 50
            edbapp.materials["FR4_epoxy"].thermal_conductivity = 1e-5

            assert edbapp.materials["FR4_epoxy"].thermal_conductivity == 1e-5
            edbapp.materials["FR4_epoxy"].thermal_expansion_coefficient = 1e-7

            assert edbapp.materials["FR4_epoxy"].thermal_expansion_coefficient == 1e-7
            edbapp.materials["FR4_epoxy"].poisson_ratio = 1e-3
            assert edbapp.materials["FR4_epoxy"].poisson_ratio == 1e-3
            assert edbapp.materials["new_conductor"]
            assert edbapp.materials.duplicate("FR4_epoxy", "FR41")
            assert edbapp.materials["FR41"]
            assert edbapp.materials["FR4_epoxy"].conductivity == edbapp.materials["FR41"].conductivity
            assert edbapp.materials["FR4_epoxy"].permittivity == edbapp.materials["FR41"].permittivity
            assert edbapp.materials["FR4_epoxy"].loss_tangent == edbapp.materials["FR41"].loss_tangent
            assert edbapp.materials["FR4_epoxy"].magnetic_loss_tangent == edbapp.materials["FR41"].magnetic_loss_tangent
            assert edbapp.materials["FR4_epoxy"].youngs_modulus == edbapp.materials["FR41"].youngs_modulus
            assert edbapp.materials["FR4_epoxy"].mass_density == edbapp.materials["FR41"].mass_density
            assert edbapp.materials["FR4_epoxy"].thermal_conductivity == edbapp.materials["FR41"].thermal_conductivity
            assert (
                edbapp.materials["FR4_epoxy"].thermal_expansion_coefficient
                == edbapp.materials["FR41"].thermal_expansion_coefficient
            )
            assert edbapp.materials["FR4_epoxy"].poisson_ratio == edbapp.materials["FR41"].poisson_ratio
            assert edbapp.materials.add_debye_material("My_Debye2", 5, 3, 0.02, 0.05, 1e5, 1e9)
            assert edbapp.materials.add_djordjevicsarkar_material("MyDjord2", 3.3, 0.02, 3.3)
            freq = [0, 2, 3, 4, 5, 6]
            rel_perm = [1e9, 1.1e9, 1.2e9, 1.3e9, 1.5e9, 1.6e9]
            loss_tan = [0.025, 0.026, 0.027, 0.028, 0.029, 0.030]
            assert edbapp.materials.add_multipole_debye_material("My_MP_Debye2", freq, rel_perm, loss_tan)
            edbapp.close_edb()

        @pytest.mark.skipif(is_ironpython, reason="Not supported in IPY")
        def test_44_solve(self):
            target_path = os.path.join(local_path, "example_models", test_subfolder, "Galileo_to_be_solved.aedb")
            out_edb = os.path.join(self.local_scratch.path, "Galileo_to_be_solved.aedb")
            self.local_scratch.copyfolder(target_path, out_edb)
            edbapp = Edb(out_edb, edbversion=desktop_version)
            edbapp.core_siwave.create_exec_file(add_dc=True)
            out = edbapp.solve_siwave()
            assert os.path.exists(out)
            res = edbapp.export_siwave_dc_results(out, "myDCIR_4")
            for i in res:
                assert os.path.exists(i)

        @pytest.mark.skipif(is_ironpython, reason="Not supported in Ironpython because of numpy.")
        def test_45_component(self):
            edb_path = os.path.join(local_path, "example_models", test_subfolder, "Galileo.aedb")
            sparam_path = os.path.join(local_path, "example_models", test_subfolder, "GRM32_DC0V_25degC_series.s2p")
            spice_path = os.path.join(local_path, "example_models", test_subfolder, "GRM32_DC0V_25degC.mod")

            edbapp = Edb(edb_path, edbversion=desktop_version)
            comp = edbapp.core_components.components["R6"]
            comp.assign_rlc_model(1, 2, 3, False)
            assert (
                not comp.is_parallel_rlc
                and float(comp.res_value) == 1
                and float(comp.ind_value) == 2
                and float(comp.cap_value) == 3
            )
            comp.assign_rlc_model(1, 2, 3, True)
            assert comp.is_parallel_rlc
            assert (
                comp.is_parallel_rlc
                and float(comp.res_value) == 1
                and float(comp.ind_value) == 2
                and float(comp.cap_value) == 3
            )
            assert comp.value
            assert not comp.spice_model and not comp.s_param_model and not comp.netlist_model
            assert comp.assign_s_param_model(sparam_path) and comp.value
            assert comp.s_param_model
            assert comp.assign_spice_model(spice_path) and comp.value
            assert comp.spice_model
            assert edbapp.core_components.nport_comp_definition
            comp.type = "Inductor"
            comp.value = 10  # This command set the model back to ideal RLC
            assert comp.type == "Inductor" and comp.value == 10 and float(comp.ind_value) == 10

        def test_46_stackup(self):
            def validate_material(pedb_materials, material, delta):
                pedb_mat = pedb_materials[material["name"]]
                if not material["dielectric_model_frequency"]:
                    assert (pedb_mat.conductivity - material["conductivity"]) < delta
                    assert (pedb_mat.permittivity - material["permittivity"]) < delta
                    assert (pedb_mat.loss_tangent - material["loss_tangent"]) < delta
                    assert (pedb_mat.permeability - material["permeability"]) < delta
                    assert (pedb_mat.magnetic_loss_tangent - material["magnetic_loss_tangent"]) < delta
                assert (pedb_mat.mass_density - material["mass_density"]) < delta
                assert (pedb_mat.poisson_ratio - material["poisson_ratio"]) < delta
                assert (pedb_mat.specific_heat - material["specific_heat"]) < delta
                assert (pedb_mat.thermal_conductivity - material["thermal_conductivity"]) < delta
                assert (pedb_mat.youngs_modulus - material["youngs_modulus"]) < delta
                assert (pedb_mat.thermal_expansion_coefficient - material["thermal_expansion_coefficient"]) < delta
                if material["dc_conductivity"] is not None:
                    assert (pedb_mat.dc_conductivity - material["dc_conductivity"]) < delta
                else:
                    assert pedb_mat.dc_conductivity == material["dc_conductivity"]
                if material["dc_permittivity"] is not None:
                    assert (pedb_mat.dc_permittivity - material["dc_permittivity"]) < delta
                else:
                    assert pedb_mat.dc_permittivity == material["dc_permittivity"]
                if material["dielectric_model_frequency"] is not None:
                    assert (pedb_mat.dielectric_model_frequency - material["dielectric_model_frequency"]) < delta
                else:
                    assert pedb_mat.dielectric_model_frequency == material["dielectric_model_frequency"]
                if material["loss_tangent_at_frequency"] is not None:
                    assert (pedb_mat.loss_tangent_at_frequency - material["loss_tangent_at_frequency"]) < delta
                else:
                    assert pedb_mat.loss_tangent_at_frequency == material["loss_tangent_at_frequency"]
                if material["permittivity_at_frequency"] is not None:
                    assert (pedb_mat.permittivity_at_frequency - material["permittivity_at_frequency"]) < delta
                else:
                    assert pedb_mat.permittivity_at_frequency == material["permittivity_at_frequency"]
                return 0

            target_path = os.path.join(local_path, "example_models", test_subfolder, "Galileo.aedb")
            out_edb = os.path.join(self.local_scratch.path, "Galileo_test.aedb")
            self.local_scratch.copyfolder(target_path, out_edb)
            json_path = os.path.join(local_path, "example_models", test_subfolder, "test_mat.json")
            edbapp = Edb(out_edb, edbversion=desktop_version)
            edbapp.stackup._import_layer_stackup(json_path)
            edbapp.save_edb()
            delta = 1e-6
            f = open(json_path)
            json_dict = json.load(f)
            for k, v in json_dict.items():
                if k == "materials":
                    for material in v.values():
                        assert 0 == validate_material(edbapp.materials, material, delta)
            for k, v in json_dict.items():
                if k == "layers":
                    for layer_name, layer in v.items():
                        pedb_lay = edbapp.stackup.layers[layer_name]
                        assert list(pedb_lay.color) == layer["color"]
                        assert pedb_lay.type == layer["type"]
                        if isinstance(layer["material"], str):
                            assert pedb_lay.material == layer["material"]
                        else:
                            assert 0 == validate_material(edbapp.materials, layer["material"], delta)
                        if isinstance(layer["dielectric_fill"], str) or layer["dielectric_fill"] is None:
                            assert pedb_lay.dielectric_fill == layer["dielectric_fill"]
                        else:
                            assert 0 == validate_material(edbapp.materials, layer["dielectric_fill"], delta)
                        assert (pedb_lay.thickness - layer["thickness"]) < delta
                        assert (pedb_lay.etch_factor - layer["etch_factor"]) < delta
                        assert pedb_lay.roughness_enabled == layer["roughness_enabled"]
                        if layer["roughness_enabled"]:
                            assert (pedb_lay.top_hallhuray_nodule_radius - layer["top_hallhuray_nodule_radius"]) < delta
                            assert (pedb_lay.top_hallhuray_surface_ratio - layer["top_hallhuray_surface_ratio"]) < delta
                            assert (
                                pedb_lay.bottom_hallhuray_nodule_radius - layer["bottom_hallhuray_nodule_radius"]
                            ) < delta
                            assert (
                                pedb_lay.bottom_hallhuray_surface_ratio - layer["bottom_hallhuray_surface_ratio"]
                            ) < delta
                            assert (
                                pedb_lay.side_hallhuray_nodule_radius - layer["side_hallhuray_nodule_radius"]
                            ) < delta
                            assert (
                                pedb_lay.side_hallhuray_surface_ratio - layer["side_hallhuray_surface_ratio"]
                            ) < delta
            edbapp.close_edb()

        def test_47_build_project(self):
            target_path = os.path.join(local_path, "example_models", test_subfolder, "Galileo.aedb")
            out_edb = os.path.join(self.local_scratch.path, "Galileo_build_project.aedb")
            self.local_scratch.copyfolder(target_path, out_edb)
            edbapp = Edb(out_edb, edbversion=desktop_version)
            sim_setup = SimulationConfiguration()
            sim_setup.signal_nets = [
                "M_DQ<0>",
                "M_DQ<1>",
                "M_DQ<2>",
                "M_DQ<3>",
                "M_DQ<4>",
                "M_DQ<5>",
                "M_DQ<6>",
                "M_DQ<7>",
            ]
            sim_setup.power_nets = ["GND"]
            sim_setup.do_cutout_subdesign = True
            sim_setup.components = ["U2A5", "U1B5"]
            sim_setup.use_default_coax_port_radial_extension = False
            sim_setup.cutout_subdesign_expansion = 0.001
            sim_setup.start_frequency = 0
            sim_setup.stop_freq = 20e9
            sim_setup.step_freq = 10e6
            assert edbapp.build_simulation_project(sim_setup)
