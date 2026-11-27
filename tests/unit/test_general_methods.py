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

from types import SimpleNamespace
from unittest.mock import patch

import pytest

from ansys.aedt.core.generic.general_methods import _get_pids_by_name_windows
from ansys.aedt.core.generic.general_methods import _get_pids_by_name_windows_tasklist
from ansys.aedt.core.generic.general_methods import _is_version_format_valid
from ansys.aedt.core.generic.general_methods import _normalize_version_to_string
from ansys.aedt.core.generic.general_methods import _run_ss
from ansys.aedt.core.generic.general_methods import number_aware_string_key
from ansys.aedt.core.generic.settings import is_linux


@pytest.fixture(scope="module", autouse=True)
def desktop() -> None:
    """Override the desktop fixture to DO NOT open the Desktop when running this test class"""
    return


class TestGeneralMethods:
    def test_number_aware_string_key(self) -> None:
        assert number_aware_string_key("C1") == ("C", 1)
        assert number_aware_string_key("1234asdf") == (1234, "asdf")
        assert number_aware_string_key("U100") == ("U", 100)
        assert number_aware_string_key("U100X0") == ("U", 100, "X", 0)
        component_names = ["U10", "U2", "C1", "Y1000", "Y200"]
        expected_sort_order = ["C1", "U2", "U10", "Y200", "Y1000"]
        assert sorted(component_names, key=number_aware_string_key) == expected_sort_order
        assert sorted(component_names + [""], key=number_aware_string_key) == [""] + expected_sort_order

    def test_valid_full_year_float(self) -> None:
        assert _normalize_version_to_string(2023.2) == "2023.2"
        assert _normalize_version_to_string("2024.5") == "2024.5"

    def test_valid_short_year_float(self) -> None:
        assert _normalize_version_to_string(23.4) == "2023.4"
        assert _normalize_version_to_string("25.9") == "2025.9"

    def test_valid_int_formats(self) -> None:
        assert _normalize_version_to_string(232) == "2023.2"
        assert _normalize_version_to_string("245") == "2024.5"

    def test_valid_string_R_formats(self) -> None:
        assert _normalize_version_to_string("2026R1") == "2026.1"
        assert _normalize_version_to_string("2026 R1") == "2026.1"
        assert _normalize_version_to_string("26R1") == "2026.1"
        assert _normalize_version_to_string("26 R1") == "2026.1"

    def test_none_value_as_version(self) -> None:
        assert _normalize_version_to_string(None) is None

    def test_invalid_types(self) -> None:
        with pytest.raises(ValueError):
            _normalize_version_to_string([2023.2])  # list not allowed
        with pytest.raises(ValueError):
            _normalize_version_to_string({"year": 2023.2})  # dict not allowed

    def test_invalid_formats(self) -> None:
        with pytest.raises(ValueError):
            _normalize_version_to_string("20232")  # too many digits
        with pytest.raises(ValueError):
            _normalize_version_to_string("2023.23")  # too many decimals
        with pytest.raises(ValueError):
            _normalize_version_to_string("23")  # too short
        with pytest.raises(ValueError):
            _normalize_version_to_string("1999.2")  # not 20XX
        with pytest.raises(ValueError):
            _normalize_version_to_string("20A3.2")  # invalid chars
        with pytest.raises(ValueError):
            _normalize_version_to_string("2025 R")  # missing digit after R

    def test_edge_cases(self) -> None:
        assert _normalize_version_to_string("2000.0") == "2000.0"  # earliest year
        assert _normalize_version_to_string("2099.9") == "2099.9"  # latest year
        assert _normalize_version_to_string("00.1") == "2000.1"  # short float lowest
        assert _normalize_version_to_string("99.9") == "2099.9"  # short float highest
        assert _normalize_version_to_string("000") == "2000.0"  # int lowest
        assert _normalize_version_to_string("999") == "2099.9"  # int highest
        assert _normalize_version_to_string("00R1") == "2000.1"  # short R format
        assert _normalize_version_to_string("99R9") == "2099.9"  # short R format max
        assert _normalize_version_to_string("2000R1") == "2000.1"  # long R format
        assert _normalize_version_to_string("2099R9") == "2099.9"  # long R format max

    @pytest.mark.parametrize(
        "version",
        [
            "2023.2",
            "2023.12",
            "1999.1",
            "2023.2SV",
            "2023.12SV",
        ],
    )
    def test_valid_versions(self, version):
        assert _is_version_format_valid(version)

    @pytest.mark.parametrize(
        "version",
        [
            "23.2",  # too short year
            "202.2",  # too short year
            "20234.2",  # too long year
            "2023.02",  # leading zero
            "2023",  # missing minor version
            "2023.",  # dangling dot
            "2023.2Extra",  # extra text
            "2023.2 SV",  # space before SV
            "",  # empty
            None,  # None value
            2023.2,  # float type
        ],
    )
    def test_invalid_versions(self, version):
        assert not _is_version_format_valid(version)

    @pytest.mark.skipif(not is_linux, reason="Linux-only tests")
    def test_run_ss_returns_dict(self):
        result = _run_ss()
        assert isinstance(result, dict)
        for pid, port in result.items():
            assert isinstance(pid, int)
            assert isinstance(port, int)

    @pytest.mark.skipif(not is_linux, reason="Linux-only tests")
    @patch("ansys.aedt.core.generic.general_methods.shutil.which", return_value=None)
    def test_run_ss_returns_empty_when_ss_missing(self, _mock_which):
        assert _run_ss() == {}

    @pytest.mark.skipif(not is_linux, reason="Linux-only tests")
    @patch("ansys.aedt.core.generic.general_methods.subprocess.run")
    def test_run_ss_returns_empty_when_ss_fails(self, mock_run):
        """A non-zero ``ss`` exit code must produce an empty mapping."""
        mock_run.return_value = SimpleNamespace(returncode=1, stdout="", stderr="boom")
        assert _run_ss() == {}

    def test_run_ss_returns_empty_on_non_linux(self):
        """``_run_ss`` must short-circuit to ``{}`` outside Linux."""
        if is_linux:
            pytest.skip("Behaviour only applies to non-Linux platforms.")
        assert _run_ss() == {}

    @patch("ansys.aedt.core.generic.general_methods.psutil.version_info", (6, 1, 0))
    @patch("ansys.aedt.core.generic.general_methods.subprocess.run")
    @patch("ansys.aedt.core.generic.general_methods.psutil.process_iter")
    def test_get_pids_by_name_windows_matches_name_only(self, mock_process_iter, mock_run):
        """With psutil >= 6.1.0, only matching process names are returned and tasklist is not used."""
        mock_process_iter.return_value = [
            SimpleNamespace(pid=10, info={"name": "ansysedt.exe"}),
            SimpleNamespace(pid=11, info={"name": "AnsysEDT.EXE"}),
            SimpleNamespace(pid=12, info={"name": "ansysedtsv.exe"}),
            SimpleNamespace(pid=13, info={"name": None}),
            SimpleNamespace(pid=14, info={}),
        ]
        assert _get_pids_by_name_windows("ansysedt.exe") == [10, 11]
        mock_process_iter.assert_called_with(["name"])
        mock_run.assert_not_called()

    @patch("ansys.aedt.core.generic.general_methods.psutil.version_info", (6, 0, 0))
    @patch("ansys.aedt.core.generic.general_methods.subprocess.run")
    @patch("ansys.aedt.core.generic.general_methods.psutil.process_iter")
    def test_get_pids_by_name_windows_uses_tasklist_on_old_psutil(self, mock_process_iter, mock_run):
        """With psutil < 6.1.0, the tasklist fallback is used and its CSV output is parsed."""
        mock_run.return_value = SimpleNamespace(
            stdout=(
                '"ansysedt.exe","1234","Console","1","245,678 K"\n'
                "\n"
                "INFO: No tasks are running which match the specified criteria.\n"
                '"ansysedt.exe","5678","Console","1","1,024 K"\n'
            )
        )
        assert _get_pids_by_name_windows("ansysedt.exe") == [1234, 5678]
        assert mock_run.call_args.args[0][0] == "tasklist"
        mock_process_iter.assert_not_called()

    def test_get_pids_by_name_windows_tasklist_rejects_unknown_name(self):
        with pytest.raises(ValueError):
            _get_pids_by_name_windows_tasklist("python.exe")
