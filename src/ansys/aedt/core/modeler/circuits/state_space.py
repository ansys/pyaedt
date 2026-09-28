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

"""Standalone reader for pin (port) names in a binary SSS file.

This is a minimal, dependency-free extraction of the SSS header logic
from the XViewer package. It parses only what is needed
to reach and read the trailing pin-name section, *seeking* past the large
matrix and vector data blocks instead of reading them off disk -- so only a
few KB are read regardless of the file's total size. The byte layout
mirrors the authoritative C++ reader

All integers are little-endian.

Source of truth / versioning
----------------------------
This reader is a faithful mirror of the authoritative C++ SSS
writer/reader and MUST be kept in lockstep with it: the pin names live at the
very end of the file and there is no offset table to jump to them, so any
change to a field *before* the pin section shifts every offset and breaks
parsing.

This reader targets SSS format version ``70`` only (see
``SUPPORTED_VERSION``). A file reporting any other version is rejected with
:class:`UnsupportedVersionError` rather than returning garbage. When the
format changes, update the walk in :func:`read_header` and bump
``SUPPORTED_VERSION`` accordingly.

Layout (only the parts relevant to pin names are decoded; the rest is skipped)
------------------------------------------------------------------------------
1.  A matrix (sparse CSR):
        u32   n_row_starts   (= n_states + 1)
        u32[] row_starts
        u32   n_col_indices  (= nnz)
        u32[] col_indices
        u32   n_data         (= nnz)
        f64[] data
2.  B, C, D, delay -- each a dense matrix block:
        u32 rows, u32 cols, u32 one(=1), u32 total(=rows*cols)
        f64[] values
3.  Scalar metadata (14 fields).
4.  Four flag bytes + i32 version (with a legacy "premature" fallback).
5.  If bytes remain: vectors zo, freq, noise_freq, gamma_mag, gamma_ang,
    fmin, rn (each: u32 count + f64[count]); then u8 parameter code,
    u32 port count, and that many length-prefixed pin-name strings.

Usage
-----
    from sss_header_reader import read_pin_names, read_header

    names = read_pin_names("part.sss")

    hdr = read_header("part.sss")
    print(hdr.n_states, hdr.version, hdr.n_ports, hdr.port_names)

Command line
------------
    python sss_header_reader.py part.sss [more.sss ...]
"""

from __future__ import annotations

from dataclasses import dataclass
from dataclasses import field
import struct

#: The only SSS format version this reader understands. Bump this (and
#: update the byte walk in :func:`read_header`) when the SSS layout changes.
SUPPORTED_VERSION = 70


class UnsupportedVersionError(ValueError):
    """Raised when a SSS file's version differs from ``SUPPORTED_VERSION``.

    Subclasses ``ValueError`` so existing ``except ValueError`` handlers still
    catch it.
    """


class _Cursor:
    """Forward-only cursor over an open SSS file.

    Small typed fields are read directly; large data regions are *seeked* past
    with :meth:`skip`, so their bytes are never read off disk -- only the
    header scalars and the trailing pin-name strings (a few KB total) are ever
    read, regardless of the file's size. This makes reading the pin names
    effectively independent of the size of the matrices in the file.
    """

    __slots__ = ("_fh", "_len")

    def __init__(self, fh) -> None:
        self._fh = fh
        fh.seek(0, 2)  # end
        self._len = fh.tell()
        fh.seek(0, 0)  # back to start

    def eof(self) -> bool:
        return self._fh.tell() >= self._len

    def _take(self, n: int) -> bytes:
        pos = self._fh.tell()
        if pos + n > self._len:
            raise EOFError(
                f"Unexpected end of .sss data: requested {n} bytes at offset {pos}, but only {self._len - pos} remain."
            )
        return self._fh.read(n)

    def skip(self, n: int) -> None:
        pos = self._fh.tell()
        if pos + n > self._len:
            raise EOFError(
                f"Unexpected end of .sss data: tried to skip {n} bytes at "
                f"offset {pos}, but only {self._len - pos} remain."
            )
        self._fh.seek(n, 1)  # relative seek -- does not read the skipped bytes

    def u32(self) -> int:
        return struct.unpack_from("<I", self._take(4))[0]

    def i32(self) -> int:
        return struct.unpack_from("<i", self._take(4))[0]

    def f64(self) -> float:
        return struct.unpack_from("<d", self._take(8))[0]

    def u8(self) -> int:
        return self._take(1)[0]

    def string(self) -> str:
        """Read a u32 length-prefixed string (latin-1, trailing NUL/space trimmed)."""
        n = self.u32()
        if n == 0:
            return ""
        return self._take(n).decode("latin-1").rstrip("\x00 ")


@dataclass
class SssHeader:
    """Lightweight header info extracted from a SSS file."""

    n_states: int
    version: int
    param_code: int
    port_names: list[str] = field(default_factory=list)

    @property
    def n_ports(self) -> int:
        return len(self.port_names)


def _skip_matrix(cur: _Cursor) -> None:
    """Advance past one dense matrix block (u32 rows,cols,one,total + f64[total])."""
    _rows = cur.u32()
    _cols = cur.u32()
    one = cur.u32()
    total = cur.u32()
    if one != 1:
        raise ValueError(f".sss matrix header expected leading dim 1, got {one}.")
    if total != _rows * _cols:
        raise ValueError(f".sss matrix header size mismatch: total={total}, rows*cols={_rows * _cols}.")
    cur.skip(8 * total)


def _skip_vector(cur: _Cursor) -> None:
    """Advance past one length-prefixed f64 vector (u32 count + f64[count])."""
    n = cur.u32()
    cur.skip(8 * n)


def read_header(path: str) -> SssHeader:
    """Parse just the header/pin-name info from a SSS file.

    Returns an :class:`SssHeader`. If the file has no pin-name section (an
    older SSS layout that still reports version ``70``), ``port_names``
    is empty.

    Raises
    ------
    UnsupportedVersionError
        If the file's format version differs from ``SUPPORTED_VERSION`` (70).
    EOFError, ValueError
        If the file is truncated or structurally invalid.
    """
    with open(path, "rb") as fh:
        return _parse_header(_Cursor(fh))


def _parse_header(cur: _Cursor) -> SssHeader:
    """Walk an open SSS cursor and return its :class:`SssHeader`."""
    # --- A matrix (sparse CSR): skip row_starts, col_indices, data ------
    n_row_starts = cur.u32()
    cur.skip(4 * n_row_starts)
    n_col_indices = cur.u32()
    cur.skip(4 * n_col_indices)
    n_data = cur.u32()
    cur.skip(8 * n_data)
    n_states = max(n_row_starts - 1, 0)

    # --- B, C, D, delay -------------------------------------------------
    for _ in range(4):
        _skip_matrix(cur)

    # --- scalar metadata (14 fields, exact order/sizes) -----------------
    cur.f64()  # epsilon_final
    cur.f64()  # noncausality
    cur.u8()  # input_oca_print
    cur.f64()  # epsilon
    cur.u8()  # is_do_rational_fitting
    cur.i32()  # do_column_fit
    cur.i32()  # do_mor
    cur.i32()  # do_enforce_passivity
    cur.u8()  # consider_dcfit
    cur.u8()  # is_symmetric
    cur.i32()  # max_states
    cur.u8()  # by_entry
    cur.f64()  # qlimit
    cur.i32()  # rational_fitting_iteration_limit

    # --- four flag bytes + version (with legacy "premature" handling) ---
    version = 0
    premature = False
    for _ in range(4):  # twa, morsp, wide_dynamic_range, twa_conserve_memory
        if premature:
            continue
        b_flag = cur.u8()
        if b_flag not in (0, 1):
            # Legacy file: this byte is actually the first byte of the
            # version int; the flags were never written.
            version = b_flag
            premature = True

    if premature:
        # Old layout: consume the remaining 3 bytes of the version int.
        cur.u8()
        cur.u8()
        cur.u8()
    else:
        version = cur.i32()

    # --- version guard: only version 70 is supported --------------------
    # If the version does not match, the byte layout has (almost certainly)
    # changed, so anything we read past here would be garbage. Fail loudly.
    if version != SUPPORTED_VERSION:
        raise UnsupportedVersionError(
            f".sss format version {version} is not supported; this reader "
            f"targets version {SUPPORTED_VERSION}. The byte layout has likely "
            f"changed -- update read_header() and SUPPORTED_VERSION to match "
            f"the current .sss writer."
        )

    # --- trailing vectors + pin names (present in modern files) ---------
    param_code = 0
    port_names: list[str] = []
    if not cur.eof():
        for _ in range(7):  # zo, freq, noise_freq, gamma_mag, gamma_ang, fmin, rn
            _skip_vector(cur)
        param_code = cur.u8()
        port_count = cur.u32()
        for _ in range(port_count):
            port_names.append(cur.string())

    return SssHeader(
        n_states=n_states,
        version=version,
        param_code=param_code,
        port_names=port_names,
    )


def read_pin_names(path: str) -> list[str]:
    """Return the list of pin (port) names stored in a SSS file.

    Empty if the file has no pin-name section (older SSS layout).
    """
    return read_header(path).port_names
