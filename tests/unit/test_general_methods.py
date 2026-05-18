# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 - 2026 ANSYS, Inc. and/or its affiliates.
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

from unittest.mock import patch

import pytest

from ansys.aedt.core.generic.general_methods import _is_version_format_valid
from ansys.aedt.core.generic.general_methods import _normalize_version_to_string
from ansys.aedt.core.generic.general_methods import _parse_proc_net_unix
from ansys.aedt.core.generic.general_methods import _run_ss_xlp
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

    @pytest.mark.skipif(is_linux, reason="Linux-only tests")
    def test_run_ss_xlp_returns_dict(self):
        result = _run_ss_xlp()
        assert isinstance(result, dict)
        for pid, port in result.items():
            assert isinstance(pid, int)
            assert isinstance(port, int)

    @pytest.mark.skipif(is_linux, reason="Linux-only tests")
    @patch("ansys.aedt.core.generic.general_methods._get_target_processes")
    def test_run_ss_xlp_with_real_unix_socket(self, mock_get_target_processes, tmp_path):
        """Create a real Unix socket whose name matches the AnsysEMUDS pattern,
        register it in /proc/net/unix (via the live kernel), and confirm that
        _run_ss_xlp discovers for the current process.

        The test creates a listening Unix socket at
        ``<tmp_path>/AnsysEMUDS-59999.sock`` bound inside the current process,
        then calls _run_ss_xlp with the current PID injected as an AEDT target.
        Both the ``ss`` path and the ``/proc/net/unix`` fallback are exercised
        because the kernel exposes the socket in both places.
        """
        import os
        import socket as _socket

        sock_path = str(tmp_path / "AnsysEMUDS-59999.sock")
        sock = _socket.socket(_socket.AF_UNIX, _socket.SOCK_STREAM)
        try:
            sock.bind(sock_path)
            sock.listen(1)

            current_pid = os.getpid()

            # Inject the current process as the only "AEDT" target so that
            # _run_ss_xlp inspects our own /proc/<pid>/fd entries.
            mock_get_target_processes.return_value = [(current_pid, ["/ansysedt"])]
            result = _run_ss_xlp()

            # The socket must be discovered via ss or /proc/net/unix fallback.
            assert current_pid in result
            assert result[current_pid] == 59999
        finally:
            sock.close()

    @pytest.mark.skipif(is_linux, reason="Linux-only tests")
    def test_parse_proc_net_unix_returns_dict(self):
        result = _parse_proc_net_unix(set())
        assert isinstance(result, dict)

    @pytest.mark.skipif(is_linux, reason="Linux-only tests")
    def test_parse_proc_net_unix_with_real_unix_socket(self, tmp_path):
        """Bind a real Unix socket whose name matches AnsysEMUDS-<port>.sock,
        then verify that _parse_proc_net_unix resolves the current pid→port
        by reading the live /proc/net/unix and /proc/<pid>/fd.
        """
        import os
        import socket as _socket

        sock_path = str(tmp_path / "AnsysEMUDS-58888.sock")
        sock = _socket.socket(_socket.AF_UNIX, _socket.SOCK_STREAM)
        try:
            sock.bind(sock_path)
            sock.listen(1)

            current_pid = os.getpid()
            result = _parse_proc_net_unix({current_pid})

            assert current_pid in result
            assert result[current_pid] == 58888
        finally:
            sock.close()
