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

from __future__ import annotations

from io import BytesIO
import struct

import pytest

from ansys.aedt.core.modeler.circuits.state_space import SUPPORTED_VERSION
from ansys.aedt.core.modeler.circuits.state_space import SssHeader
from ansys.aedt.core.modeler.circuits.state_space import UnsupportedVersionError
from ansys.aedt.core.modeler.circuits.state_space import _Cursor
from ansys.aedt.core.modeler.circuits.state_space import _parse_header
from ansys.aedt.core.modeler.circuits.state_space import _skip_matrix
from ansys.aedt.core.modeler.circuits.state_space import _skip_vector
from ansys.aedt.core.modeler.circuits.state_space import read_header
from ansys.aedt.core.modeler.circuits.state_space import read_pin_names


@pytest.fixture(scope="module", autouse=True)
def desktop() -> None:
    """Override the desktop fixture to DO NOT open the Desktop when running this test class."""
    return


def _pack_u32(value: int) -> bytes:
    return struct.pack("<I", value)


def _pack_i32(value: int) -> bytes:
    return struct.pack("<i", value)


def _pack_f64(value: float) -> bytes:
    return struct.pack("<d", value)


def _pack_u8(value: int) -> bytes:
    return struct.pack("<B", value)


def _pack_string(value: str) -> bytes:
    raw = value.encode("latin-1")
    return _pack_u32(len(raw)) + raw


def _pack_vector(values: list[float] | None = None) -> bytes:
    values = values or []
    return _pack_u32(len(values)) + b"".join(_pack_f64(v) for v in values)


def build_sss(
    *,
    n_states: int = 0,
    nnz: int = 0,
    version: int = SUPPORTED_VERSION,
    premature: bool = False,
    flags: tuple[int, int, int, int] = (0, 0, 0, 0),
    param_code: int = 1,
    port_names: list[str] | None = None,
    include_trailing: bool = True,
    dense_rows: int = 0,
    dense_cols: int = 0,
    matrix_one: int = 1,
    matrix_total: int | None = None,
    include_matrix_payload: bool = True,
) -> bytes:
    """Build a minimal SSS binary payload matching the version-70 layout."""
    parts: list[bytes] = []
    n_row_starts = n_states + 1
    parts.append(_pack_u32(n_row_starts))
    parts.append(b"\x00" * (4 * n_row_starts))
    parts.append(_pack_u32(nnz))
    parts.append(b"\x00" * (4 * nnz))
    parts.append(_pack_u32(nnz))
    parts.append(b"\x00" * (8 * nnz))

    total = dense_rows * dense_cols if matrix_total is None else matrix_total
    for _ in range(4):
        parts.append(_pack_u32(dense_rows) + _pack_u32(dense_cols) + _pack_u32(matrix_one) + _pack_u32(total))
        if include_matrix_payload:
            parts.append(b"\x00" * (8 * total))

    parts.extend(
        [
            _pack_f64(0.0),  # epsilon_final
            _pack_f64(0.0),  # noncausality
            _pack_u8(0),  # input_oca_print
            _pack_f64(0.0),  # epsilon
            _pack_u8(0),  # is_do_rational_fitting
            _pack_i32(0),  # do_column_fit
            _pack_i32(0),  # do_mor
            _pack_i32(0),  # do_enforce_passivity
            _pack_u8(0),  # consider_dcfit
            _pack_u8(0),  # is_symmetric
            _pack_i32(0),  # max_states
            _pack_u8(0),  # by_entry
            _pack_f64(0.0),  # qlimit
            _pack_i32(0),  # rational_fitting_iteration_limit
        ]
    )

    if premature:
        parts.append(_pack_i32(version))
    else:
        parts.extend(_pack_u8(flag) for flag in flags)
        parts.append(_pack_i32(version))

    if include_trailing:
        for _ in range(7):
            parts.append(_pack_vector())
        parts.append(_pack_u8(param_code))
        names = port_names if port_names is not None else []
        parts.append(_pack_u32(len(names)))
        parts.extend(_pack_string(name) for name in names)

    return b"".join(parts)


def _write_sss(tmp_path, payload: bytes, name: str = "part.sss"):
    path = tmp_path / name
    path.write_bytes(payload)
    return str(path)


def test_sss_header_n_ports() -> None:
    header = SssHeader(n_states=2, version=70, param_code=1, port_names=["P1", "P2", "P3"])
    assert header.n_ports == 3


def test_unsupported_version_error_is_value_error() -> None:
    assert issubclass(UnsupportedVersionError, ValueError)
    with pytest.raises(ValueError, match="not supported"):
        raise UnsupportedVersionError("not supported")


def test_read_header_and_pin_names(tmp_path) -> None:
    payload = build_sss(n_states=2, nnz=1, port_names=["Port1", "Port2"], param_code=3)
    path = _write_sss(tmp_path, payload)

    header = read_header(path)
    assert header.n_states == 2
    assert header.version == SUPPORTED_VERSION
    assert header.param_code == 3
    assert header.port_names == ["Port1", "Port2"]
    assert header.n_ports == 2
    assert read_pin_names(path) == ["Port1", "Port2"]


def test_read_header_without_trailing_pin_section(tmp_path) -> None:
    payload = build_sss(include_trailing=False)
    header = read_header(_write_sss(tmp_path, payload))

    assert header.n_states == 0
    assert header.version == SUPPORTED_VERSION
    assert header.param_code == 0
    assert header.port_names == []
    assert header.n_ports == 0


def test_read_header_empty_pin_list(tmp_path) -> None:
    payload = build_sss(port_names=[], param_code=9)
    header = read_header(_write_sss(tmp_path, payload))
    assert header.param_code == 9
    assert header.port_names == []


def test_pin_names_trim_nul_and_spaces(tmp_path) -> None:
    payload = build_sss(port_names=["P1\x00  ", "", "café"])
    header = read_header(_write_sss(tmp_path, payload))
    assert header.port_names == ["P1", "", "café"]


def test_unsupported_version_raises(tmp_path) -> None:
    payload = build_sss(version=69, port_names=["P1"])
    with pytest.raises(UnsupportedVersionError, match="version 69 is not supported"):
        read_header(_write_sss(tmp_path, payload))


def test_legacy_premature_version_layout(tmp_path) -> None:
    payload = build_sss(premature=True, port_names=["LegacyPort"])
    header = read_header(_write_sss(tmp_path, payload))
    assert header.version == SUPPORTED_VERSION
    assert header.port_names == ["LegacyPort"]


def test_matrix_header_invalid_leading_dim() -> None:
    payload = build_sss(matrix_one=2, include_matrix_payload=False, include_trailing=False)
    with pytest.raises(ValueError, match="expected leading dim 1"):
        _parse_header(_Cursor(BytesIO(payload)))


def test_matrix_header_size_mismatch() -> None:
    payload = build_sss(
        dense_rows=2,
        dense_cols=2,
        matrix_total=3,
        include_matrix_payload=False,
        include_trailing=False,
    )
    with pytest.raises(ValueError, match="size mismatch"):
        _parse_header(_Cursor(BytesIO(payload)))


def test_truncated_file_raises_eof(tmp_path) -> None:
    path = _write_sss(tmp_path, b"\x01\x00")
    with pytest.raises(EOFError, match="Unexpected end of .sss data"):
        read_header(path)


def test_skip_past_end_raises_eof() -> None:
    payload = _pack_u32(50)
    with pytest.raises(EOFError, match="tried to skip"):
        _parse_header(_Cursor(BytesIO(payload)))


def test_missing_file(tmp_path) -> None:
    missing = tmp_path / "does_not_exist.sss"
    with pytest.raises(FileNotFoundError):
        read_header(str(missing))


def test_cursor_typed_reads_and_eof() -> None:
    payload = _pack_u32(7) + _pack_i32(-3) + _pack_f64(1.5) + _pack_u8(9) + _pack_string("") + _pack_string("ab\x00 ")
    cur = _Cursor(BytesIO(payload))
    assert cur.eof() is False
    assert cur.u32() == 7
    assert cur.i32() == -3
    assert cur.f64() == 1.5
    assert cur.u8() == 9
    assert cur.string() == ""
    assert cur.string() == "ab"
    assert cur.eof() is True


def test_cursor_take_past_end_raises_eof() -> None:
    cur = _Cursor(BytesIO(b"\x00\x00"))
    with pytest.raises(EOFError, match="requested 4 bytes"):
        cur.u32()


def test_skip_vector_and_matrix() -> None:
    matrix = _pack_u32(1) + _pack_u32(2) + _pack_u32(1) + _pack_u32(2) + _pack_f64(1.0) + _pack_f64(2.0)
    vector = _pack_vector([3.0, 4.0, 5.0])
    cur = _Cursor(BytesIO(matrix + vector))
    _skip_matrix(cur)
    _skip_vector(cur)
    assert cur.eof() is True


def test_dense_matrices_are_skipped(tmp_path) -> None:
    payload = build_sss(dense_rows=2, dense_cols=1, n_states=1, nnz=0, port_names=["Out"])
    header = read_header(_write_sss(tmp_path, payload))
    assert header.n_states == 1
    assert header.port_names == ["Out"]
