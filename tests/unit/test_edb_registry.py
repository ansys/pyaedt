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

import os
from unittest import mock

import pytest

from ansys.aedt.core.internal.edb_registry import EdbOpenError
from ansys.aedt.core.internal.edb_registry import EdbSessionRegistry


@pytest.fixture(scope="module", autouse=True)
def desktop() -> None:
    """Override the desktop fixture to DO NOT open the Desktop when running this test module."""
    return


class FakeEdb:
    opened = []

    def __init__(self, path, cell, readonly, version, isaedtowned=False, oproject=None):
        self.path, self.cell, self.readonly = path, cell, readonly
        self._db = object()
        self._active_cell = object()
        self.close_args = []
        FakeEdb.opened.append(self)

    def close(self, terminate_rpc_session=None):
        self.close_args.append(terminate_rpc_session)
        self._db = None
        self._active_cell = None
        return True


class FakeDotnetEdb(FakeEdb):
    """Like PyEDB's .NET backend: close() takes only keywords and leaves ``_db`` set."""

    def close(self, **kwargs):
        self.close_args.append(kwargs.get("terminate_rpc_session"))
        self._active_cell = None
        return True


@pytest.fixture
def aedb(tmp_path):
    folder = tmp_path / "proj.aedb"
    folder.mkdir()
    (folder / "edb.def").write_bytes(b"v1")
    return folder


@pytest.fixture
def registry():
    FakeEdb.opened = []
    with mock.patch("ansys.aedt.core.Edb", FakeEdb):
        yield EdbSessionRegistry()


def test_same_path_and_design_share_one_open(registry, aedb):
    first = registry.get(aedb, "D1", "2026.1")
    second = registry.get(aedb, "D1", "2026.1")
    assert first is second
    assert len(FakeEdb.opened) == 1
    assert first.readonly is True


def test_path_key_is_normalized(registry, aedb):
    registry.get(aedb, "D1", "2026.1")
    registry.get(str(aedb).upper() if os.name == "nt" else str(aedb), "D1", "2026.1")
    assert len(FakeEdb.opened) == 1


def test_reopens_when_edb_def_changes(registry, aedb):
    first = registry.get(aedb, "D1", "2026.1")
    st = (aedb / "edb.def").stat()
    (aedb / "edb.def").write_bytes(b"v2 saved by AEDT")
    os.utime(aedb / "edb.def", ns=(st.st_atime_ns, st.st_mtime_ns + 10**9))
    second = registry.get(aedb, "D1", "2026.1")
    assert second is not first
    assert first.close_args == [False]


def test_reopens_for_another_design(registry, aedb):
    first = registry.get(aedb, "D1", "2026.1")
    second = registry.get(aedb, "D2", "2026.1")
    assert second is not first and second.cell == "D2"
    assert first.close_args == [False]


def test_user_close_is_pyedbs_own_and_next_get_reopens(registry, aedb):
    edb = registry.get(aedb, "D1", "2026.1")
    assert edb.close(terminate_rpc_session=True) is True
    assert edb.close_args == [True]
    assert not registry.is_open(aedb)
    again = registry.get(aedb, "D1", "2026.1")
    assert again is not edb
    assert edb.close_args == [True]


def test_dotnet_close_is_seen_and_not_repeated(aedb):
    FakeEdb.opened = []
    with mock.patch("ansys.aedt.core.Edb", FakeDotnetEdb):
        reg = EdbSessionRegistry()
        edb = reg.get(aedb, "D1", "2025.2")
        edb.close()
        assert edb._db is not None
        assert not reg.is_open(aedb)
        again = reg.get(aedb, "D1", "2025.2")
        assert again is not edb
        assert edb.close_args == [None]
        reg.get(aedb, "D2", "2025.2")
        assert again.close_args == [False]


def test_reopens_when_the_server_is_gone(registry, aedb):
    first = registry.get(aedb, "D1", "2026.1")
    with mock.patch("ansys.aedt.core.internal.edb_registry._server_alive", return_value=False):
        second = registry.get(aedb, "D1", "2026.1")
    assert second is not first
    assert first.close_args == [False]
    assert registry.get(aedb, "D1", "2026.1") is second


def test_unreadable_edb_def_reopens(registry, aedb):
    first = registry.get(aedb, "D1", "2026.1")
    with mock.patch("ansys.aedt.core.internal.edb_registry._stamp", return_value=None):
        second = registry.get(aedb, "D1", "2026.1")
        third = registry.get(aedb, "D1", "2026.1")
    assert second is not first and third is not second
    assert first.close_args == [False] and second.close_args == [False]
    fourth = registry.get(aedb, "D1", "2026.1")
    assert fourth is not third


def test_close_all_and_list(registry, aedb, tmp_path):
    other = tmp_path / "other.aedb"
    other.mkdir()
    (other / "edb.def").write_bytes(b"x")
    a = registry.get(aedb, "D1", "2026.1")
    b = registry.get(other, "D1", "2026.1")
    listed = registry.list()
    assert len(listed) == 2 and all(e["open"] for e in listed)
    assert listed[0]["aedt_saved_at"]
    registry.close_all()
    assert a.close_args == [False] and b.close_args == [False]
    assert registry.list() == []


def test_open_failure_is_explained(aedb):
    def failing(*args, **kwargs):
        raise ValueError("Failed during EDB loading.")

    with mock.patch("ansys.aedt.core.Edb", failing):
        reg = EdbSessionRegistry()
        with pytest.raises(EdbOpenError) as err:
            reg.get(aedb, "D1", "2026.1")
    assert isinstance(err.value, ValueError)
    assert "direct Edb(...)" in str(err.value) and "layout components" in str(err.value)
