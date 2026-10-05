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

from pathlib import Path

import pytest

from ansys.aedt.core.examples import downloads
from ansys.aedt.core.generic.file_utils import generate_unique_name
from ansys.aedt.core.generic.settings import is_linux


@pytest.fixture(scope="module", autouse=True)
def desktop():
    """Override the desktop fixture to DO NOT open the Desktop when running this test class"""
    return


def test_download_edb(test_tmp_dir):
    assert downloads.download_aedb(test_tmp_dir)
    assert (test_tmp_dir / "ANSYS-HSD_V1.aedb" / "GRM32ER72A225KA35_25C_0V.sp").is_file()
    assert (test_tmp_dir / "ANSYS-HSD_V1.aedb" / "edb.def").is_file()


def test_download_touchstone(test_tmp_dir):
    assert downloads.download_touchstone(test_tmp_dir)
    assert (test_tmp_dir / "SSN_ssn.s6p").is_file()


def test_download_netlist(test_tmp_dir):
    assert downloads.download_netlist(test_tmp_dir)
    assert (test_tmp_dir / "netlist_small.cir").is_file()


def test_download_sbr(test_tmp_dir):
    assert downloads.download_sbr(test_tmp_dir)
    assert (test_tmp_dir / "sbr" / "Cassegrain.aedt").is_file()


def test_download_antenna_array(test_tmp_dir):
    assert downloads.download_antenna_array(test_tmp_dir)
    assert (test_tmp_dir / "FiniteArray_Radome_77GHz_3D_CADDM.aedt").is_file()


def test_download_antenna_sherlock(test_tmp_dir):
    assert downloads.download_sherlock(test_tmp_dir / "sherlock")
    example_folder = test_tmp_dir / "sherlock" / "sherlock"
    for name in (
        "MaterialExport.csv",
        "TutorialBoard.stp",
        "TutorialBoardPartsList.csv",
    ):
        assert (example_folder / name).is_file()
    assert not (example_folder / "SherlockTutorial.aedb").exists()
    assert not (example_folder / "SherlockTutorial.aedt").exists()


@pytest.mark.skipif(is_linux, reason="Crashes on Linux")
def test_download_multiparts(test_tmp_dir):
    assert downloads.download_multiparts(local_path=test_tmp_dir / "multi")
    example_folder = test_tmp_dir / "multi" / "multiparts"
    assert (example_folder / "library.zip").is_file()
    assert (example_folder / "library" / "actor_library" / "bike1" / "bike1.json").is_file()
    assert (example_folder / "library" / "actor_library" / "bike1" / "body.a3dcomp").is_file()
    assert (example_folder / "library" / "environment_library" / "road1" / "road1.a3dcomp").is_file()
    assert (example_folder / "library" / "radar_modules" / "Example_1Tx_1Rx.json").is_file()


def test_download_leaf(test_tmp_dir):
    out = downloads.download_leaf(test_tmp_dir)

    assert Path(out[0]).exists()
    assert Path(out[1]).exists()
    assert (test_tmp_dir / "30DH_20C_smooth.tab").is_file()
    assert (test_tmp_dir / "BH_Arnold_Magnetics_N30UH_80C.tab").is_file()

    new_name = generate_unique_name("test")

    orig_path = Path(out[0])
    orig_dir = orig_path.parent

    new_path = orig_dir.with_name(new_name)

    orig_dir.rename(new_path)

    assert new_path.exists()
    assert (new_path / "30DH_20C_smooth.tab").is_file()
    assert (new_path / "BH_Arnold_Magnetics_N30UH_80C.tab").is_file()


def test_download_custom_report(test_tmp_dir):
    out = downloads.download_custom_reports(local_path=test_tmp_dir)
    assert Path(out).exists()
    example_folder = test_tmp_dir / "custom_reports"
    for name in (
        "CISPR25_Radiated_Emissions_Example22R1.aedtz",
        "CISPR25_Radiated_Emissions_Example23R1.aedtz",
        "EyeDiagram_CISPR_Basic.json",
        "EyeDiagram_CISPR_Custom.json",
        "Spectrum_CISPR_Basic.json",
        "Spectrum_CISPR_Custom.json",
        "Transient_CISPR_Basic.json",
        "Transient_CISPR_Custom.json",
    ):
        assert (example_folder / name).is_file()


def test_download_3dcomp(test_tmp_dir):
    out = downloads.download_3dcomponent(local_path=test_tmp_dir)
    assert Path(out).exists()
    example_folder = test_tmp_dir / "array_3d_component"
    for name in (
        "Circ_Patch_5GHz.a3dcomp",
        "Circ_Patch_5GHz_hex.a3dcomp",
        "array_simple.json",
        "array_simple_2by6.json",
    ):
        assert (example_folder / name).is_file()


def test_download_twin_builder_data(test_tmp_dir):
    example_folder = downloads.download_twin_builder_data(
        "Ex1_Mechanical_DynamicRom.zip", True, local_path=test_tmp_dir
    )
    assert Path(example_folder).exists()
    assert (test_tmp_dir / "twin_builder" / "Ex1_Mechanical_DynamicRom.zip").is_file()


def test_download_specific_file(test_tmp_dir):
    example_folder = downloads.download_file("motorcad", "IPM_Vweb_Hairpin.mot", test_tmp_dir)
    assert Path(example_folder).exists()
    assert (test_tmp_dir / "pyaedt" / "motorcad" / "IPM_Vweb_Hairpin.mot").is_file()


def test_download_specific_folder(test_tmp_dir):
    example_folder = downloads.download_file(source="nissan", local_path=test_tmp_dir)
    assert Path(example_folder).exists()
    assert (test_tmp_dir / "pyaedt" / "nissan" / "30DH_20C_smooth.tab").is_file()
    assert (test_tmp_dir / "pyaedt" / "nissan" / "BH_Arnold_Magnetics_N30UH_80C.tab").is_file()
    example_folder = downloads.download_file(source="wpf_edb_merge", local_path=test_tmp_dir)
    assert Path(example_folder).exists()
    example_path = test_tmp_dir / "pyaedt" / "wpf_edb_merge"
    for name in (
        "board.aedb/edb.def",
        "merge_wizard.py",
        "merge_wizard_settings.json",
        "package.aedb/edb.def",
    ):
        assert (example_path / name).is_file()
    assert not (example_path / ".gitignore").exists()


def test_download_icepak_3d_component(test_tmp_dir):
    assert downloads.download_icepak_3d_component(test_tmp_dir)
    assert (test_tmp_dir / "PCBAssembly.aedt").is_file()
    assert (test_tmp_dir / "PCBAssembly.aedb" / "edb.def").is_file()
    assert (test_tmp_dir / "QFP2.aedt").is_file()


def test_download_fss_file(test_tmp_dir):
    example_folder = downloads.download_fss_3dcomponent(local_path=test_tmp_dir)
    assert Path(example_folder).exists()
    assert (test_tmp_dir / "fss_3d_component" / "FSS_unitcell_23R2.a3dcomp").is_file()


def test_download_file(test_tmp_dir):
    relative_path = "pyaedt/netlist/netlist_small.cir"
    expected_path = test_tmp_dir / "netlist" / "netlist_small.cir"

    assert downloads._download_file(relative_path, test_tmp_dir, strip_prefix="pyaedt") == expected_path.resolve()
    assert expected_path.is_file()
    downloaded_content = expected_path.read_bytes()
    assert downloaded_content

    cached_content = downloaded_content + b"\nCached content\n"
    expected_path.write_bytes(cached_content)
    assert downloads._download_file(relative_path, test_tmp_dir, strip_prefix="pyaedt") == expected_path.resolve()
    assert expected_path.read_bytes() == cached_content

    assert (
        downloads._download_file(relative_path, test_tmp_dir, strip_prefix="pyaedt", force=True)
        == expected_path.resolve()
    )
    assert expected_path.is_file()
    assert expected_path.read_bytes() == downloaded_content


def test_delete_downloads(test_tmp_dir, monkeypatch):
    examples_path = test_tmp_dir / "examples"
    monkeypatch.setattr(downloads, "EXAMPLES_PATH", examples_path)
    example_file = examples_path / "netlist" / "netlist_small.cir"
    example_file.parent.mkdir(parents=True)
    example_file.write_text("cached content")
    assert example_file.is_file()

    assert downloads.delete_downloads()
    assert not examples_path.exists()
    assert test_tmp_dir.is_dir()
