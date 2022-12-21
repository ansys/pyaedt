import json
import math
import os
import time

from pyaedt import Edb
from pyaedt.edb_core.edb_data.simulation_configuration import SimulationConfiguration

# Setup paths for module imports
# Import required modules

test_project_name = "Galileo_edb"
bom_example = "bom_example.csv"
from _unittest.conftest import BasisTest
from _unittest.conftest import config
from _unittest.conftest import desktop_version
from _unittest.conftest import is_ironpython
from _unittest.conftest import local_path

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
            example_project = os.path.join(local_path, "example_models", test_subfolder, "example_package.aedb")
            self.target_path = os.path.join(self.local_scratch.path, "example_package.aedb")
            self.local_scratch.copyfolder(example_project, self.target_path)
            example_project2 = os.path.join(local_path, "example_models", test_subfolder, "simple.aedb")
            self.target_path2 = os.path.join(self.local_scratch.path, "simple_00.aedb")
            self.local_scratch.copyfolder(example_project2, self.target_path2)
            example_project3 = os.path.join(local_path, "example_models", test_subfolder, "Galileo_edb_plot.aedb")
            self.target_path3 = os.path.join(self.local_scratch.path, "Galileo_edb_plot_00.aedb")
            self.local_scratch.copyfolder(example_project3, self.target_path3)
            example_project4 = os.path.join(local_path, "example_models", test_subfolder, "Package.aedb")
            self.target_path4 = os.path.join(self.local_scratch.path, "Package_00.aedb")
            self.local_scratch.copyfolder(example_project4, self.target_path4)

        def teardown_class(self):
            self.edbapp.close_edb()
            self.local_scratch.remove()
            del self.edbapp

        def test_01_flip_layer_stackup(self):
            edb_path = os.path.join(self.target_path2, "edb.def")
            edb1 = Edb(edb_path, edbversion=desktop_version)

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
            edb2 = Edb(self.target_path4, edbversion=desktop_version)
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
            target_path = os.path.join(self.local_scratch.path, "Galileo.aedb")
            self.local_scratch.copyfolder(example_project, target_path)
            cfg_file = os.path.join(target_path, "test.cfg")
            with open(cfg_file, "w") as f:
                f.writelines("SolverType = 'SiwaveSYZ'\n")
                f.writelines("PowerNets = ['GND']\n")
                f.writelines("Components = ['U2A5', 'U1B5']")
            sim_config = SimulationConfiguration(cfg_file)
            assert Edb(target_path).build_simulation_project(sim_config)

        @pytest.mark.skipif(is_ironpython, reason="Not supported in IPY")
        def test_16_solve(self):
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
        def test_17_component(self):
            source_path = os.path.join(local_path, "example_models", test_subfolder, "Galileo.aedb")
            target_path = os.path.join(self.local_scratch.path, "test_122.aedb")
            self.local_scratch.copyfolder(source_path, target_path)
            sparam_path = os.path.join(local_path, "example_models", test_subfolder, "GRM32_DC0V_25degC_series.s2p")
            spice_path = os.path.join(local_path, "example_models", test_subfolder, "GRM32_DC0V_25degC.mod")

            edbapp = Edb(target_path, edbversion=desktop_version)
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

        def test_18_stackup(self):
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
            edbapp.stackup.import_stackup(json_path)
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
            edbapp = Edb()
            json_path = os.path.join(local_path, "example_models", test_subfolder, "test_mat2.json")
            assert edbapp.stackup.import_stackup(json_path)
            assert "SOLDER" in edbapp.stackup.stackup_layers
            edbapp.close_edb()

        def test_19_build_project(self):
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
            sim_setup.start_freq = 0
            sim_setup.stop_freq = 20e9
            sim_setup.step_freq = 10e6
            assert edbapp.build_simulation_project(sim_setup)

        def test_20_build_project(self):
            target_path = os.path.join(local_path, "example_models", test_subfolder, "Galileo.aedb")
            out_edb = os.path.join(self.local_scratch.path, "Galileo_build_project2.aedb")
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
            sim_setup.start_freq = 0
            sim_setup.stop_freq = 20e9
            sim_setup.step_freq = 10e6
            sim_setup.use_default_cutout = False
            assert edbapp.build_simulation_project(sim_setup)
            assert edbapp.are_port_reference_terminals_connected()
            port1 = list(edbapp.excitations.values())[0]
            assert port1.magnitude == 0.0
            assert port1.phase == 0
            assert port1.reference_net_name == "GND"
            assert not port1.deembed
            assert port1.impedance == 50.0
            assert port1.deembed_length == 0
            assert not port1.is_circuit
            assert not port1.renormalize
            assert port1.renormalize_z0 == (50.0, 0.0)
            assert not port1.get_pin_group_terminal_reference_pin()
            assert not port1.get_pad_edge_terminal_reference_pin()

        def test_21_get_component_bounding_box(self):
            target_path = os.path.join(local_path, "example_models", test_subfolder, "Galileo.aedb")
            out_edb = os.path.join(self.local_scratch.path, "Galileo_get_comp_bbox.aedb")
            self.local_scratch.copyfolder(target_path, out_edb)
            edbapp = Edb(out_edb, edbversion=desktop_version)
            component = edbapp.core_components.components["U2A5"]
            assert component.bounding_box
            assert isinstance(component.rotation, float)

        def test_22_eligible_power_nets(self):
            assert "GND" in [i.name for i in self.edbapp.core_nets.eligible_power_nets]

        @pytest.mark.skipif(is_ironpython, reason="This test uses Matplotlib, which is not supported by IronPython.")
        def test_023_plot_on_matplotlib(self):
            edb_plot = Edb(self.target_path3, edbversion=desktop_version)
            local_png1 = os.path.join(self.local_scratch.path, "test1.png")
            edb_plot.core_nets.plot(
                nets=None,
                layers=None,
                save_plot=local_png1,
                plot_components_on_top=True,
                plot_components_on_bottom=True,
                outline=[[-10e-3, -10e-3], [110e-3, -10e-3], [110e-3, 70e-3], [-10e-3, 70e-3]],
            )
            assert os.path.exists(local_png1)

            local_png2 = os.path.join(self.local_scratch.path, "test2.png")
            edb_plot.core_nets.plot(
                nets="V3P3_S5",
                layers=None,
                save_plot=local_png2,
                plot_components_on_top=True,
                plot_components_on_bottom=True,
            )
            assert os.path.exists(local_png2)
            local_png3 = os.path.join(self.local_scratch.path, "test3.png")
            edb_plot.core_nets.plot(
                nets=["LVL_I2C_SCL", "V3P3_S5", "GATE_V5_USB"],
                layers="TOP",
                color_by_net=True,
                save_plot=local_png3,
                plot_components_on_top=True,
                plot_components_on_bottom=True,
            )
            assert os.path.exists(local_png3)

        def test_24_convert_net_to_polygon(self):
            target_path = os.path.join(local_path, "example_models", "convert_and_merge_path.aedb")
            edb = Edb(target_path, edbversion=desktop_version)
            for path in edb.core_primitives.paths:
                assert path.convert_to_polygon()
            assert edb.core_nets.merge_nets_polygons("test")
