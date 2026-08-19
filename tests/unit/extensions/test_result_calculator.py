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

"""Unit tests for the Result Calculator extension business-logic layer.

Only pure-Python classes are exercised here (ResultStore, FormulaCalculator,
FileFormats, ResultDataService).  All AEDT communication is mocked; no real
AEDT session is opened.
"""

from __future__ import annotations

from pathlib import Path
from types import SimpleNamespace
from unittest.mock import MagicMock
from unittest.mock import patch

import numpy as np
import pytest

from ansys.aedt.core.extensions.common.result_calculator import FileFormats
from ansys.aedt.core.extensions.common.result_calculator import FormulaCalculator
from ansys.aedt.core.extensions.common.result_calculator import ResultCalculatorExtension
from ansys.aedt.core.extensions.common.result_calculator import ResultDataService
from ansys.aedt.core.extensions.common.result_calculator import ResultStore
from ansys.aedt.core.internal.errors import AEDTRuntimeError


@pytest.fixture(scope="module", autouse=True)
def desktop() -> None:
    """Override the desktop fixture to not open the Desktop when running this test module."""
    return


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

_MODULE = "ansys.aedt.core.extensions.common.result_calculator"


def _make_service(active_sessions_return=None) -> ResultDataService:
    """Create a ResultDataService with mocked session discovery."""
    if active_sessions_return is None:
        active_sessions_return = {}
    with (
        patch(f"{_MODULE}.active_sessions", return_value=active_sessions_return),
        patch(f"{_MODULE}._check_psutil_connections", return_value={}),
    ):
        return ResultDataService()


def _add_trace(store: ResultStore, name: str | None = None, n: int = 5) -> str:
    """Helper to add a simple trace to a ResultStore."""
    x = np.linspace(0.0, 1.0, n)
    y = np.linspace(1.0, 2.0, n)
    return store.add(x, y, source="test", metadata={}, name=name)


def _make_sol_data(
    x: list | np.ndarray,
    y_real: list | np.ndarray,
    y_imag: list | np.ndarray | None = None,
    expression: str = "S11",
    primary_sweep: str = "Freq",
    sweep_unit: str = "GHz",
) -> MagicMock:
    """Build a mock solution-data object returned by report.get_solution_data()."""
    if y_imag is None:
        y_imag = [0.0] * len(y_real)
    sol = MagicMock()
    sol.active_expression = expression
    sol.primary_sweep = primary_sweep
    sol.units_sweeps = {primary_sweep: sweep_unit}

    def _get_expression_data(expression, formula):  # noqa: ARG001
        if formula == "real":
            return (x, y_real)
        return (x, y_imag)

    sol.get_expression_data.side_effect = _get_expression_data
    return sol


# ===========================================================================
# ResultStore tests
# ===========================================================================


class TestResultStore:
    def test_sanitize_name_valid(self) -> None:
        assert ResultStore._sanitize_name("my_trace_1") == "my_trace_1"

    def test_sanitize_name_replaces_invalid_chars(self) -> None:
        # Spaces, dots and dashes should become underscores.
        assert ResultStore._sanitize_name("my trace-1.5") == "my_trace_1_5"

    def test_sanitize_name_strips_surrounding_whitespace(self) -> None:
        assert ResultStore._sanitize_name("  hello  ") == "hello"

    def test_sanitize_name_empty_raises(self) -> None:
        with pytest.raises(ValueError, match="at least one valid character"):
            ResultStore._sanitize_name("   ")

    def test_sanitize_name_only_invalid_chars_does_not_raise(self) -> None:
        # "!!!" sanitizes to "___" (underscores are allowed), so no error is raised.
        assert ResultStore._sanitize_name("!!!") == "___"

    def test_add_auto_name_first_trace(self) -> None:
        store = ResultStore()
        name = _add_trace(store)
        assert name == "result_1"
        assert "result_1" in store.data

    def test_add_auto_name_counter_increments(self) -> None:
        store = ResultStore()
        n1 = _add_trace(store)
        n2 = _add_trace(store)
        assert n1 == "result_1"
        assert n2 == "result_2"

    def test_add_custom_name(self) -> None:
        store = ResultStore()
        name = _add_trace(store, name="my_trace")
        assert name == "my_trace"

    def test_add_custom_name_sanitized(self) -> None:
        store = ResultStore()
        # "my trace" has a space - it should be sanitized to "my_trace".
        name = _add_trace(store, name="my trace")
        assert name == "my_trace"

    def test_add_duplicate_name_raises(self) -> None:
        store = ResultStore()
        _add_trace(store, name="dup")
        with pytest.raises(ValueError, match="already exists"):
            _add_trace(store, name="dup")

    def test_add_stores_x_y_as_ndarray(self) -> None:
        store = ResultStore()
        x = [1.0, 2.0, 3.0]
        y = [4.0, 5.0, 6.0]
        name = store.add(np.array(x), np.array(y), source="test", metadata={})
        assert isinstance(store.data[name]["x"], np.ndarray)
        assert isinstance(store.data[name]["y"], np.ndarray)
        np.testing.assert_array_equal(store.data[name]["x"], x)
        np.testing.assert_array_equal(store.data[name]["y"], y)

    def test_add_stores_source_and_metadata(self) -> None:
        store = ResultStore()
        meta = {"project": "proj", "design": "des"}
        name = store.add(np.array([0.0]), np.array([1.0]), source="file_import", metadata=meta)
        assert store.data[name]["source"] == "file_import"
        assert store.data[name]["metadata"] == meta

    def test_remove_existing_trace(self) -> None:
        store = ResultStore()
        name = _add_trace(store)
        store.remove(name)
        assert name not in store.data

    def test_remove_nonexistent_trace_is_silent(self) -> None:
        store = ResultStore()
        # Should not raise.
        store.remove("does_not_exist")

    def test_rename_valid(self) -> None:
        store = ResultStore()
        _add_trace(store, name="old_name")
        store.rename("old_name", "new_name")
        assert "new_name" in store.data
        assert "old_name" not in store.data

    def test_rename_preserves_insertion_order(self) -> None:
        store = ResultStore()
        _add_trace(store, name="a")
        _add_trace(store, name="b")
        _add_trace(store, name="c")
        store.rename("b", "B")
        assert list(store.data.keys()) == ["a", "B", "c"]

    def test_rename_same_name_is_noop(self) -> None:
        store = ResultStore()
        _add_trace(store, name="trace")
        store.rename("trace", "trace")
        assert "trace" in store.data

    def test_rename_missing_key_raises(self) -> None:
        store = ResultStore()
        with pytest.raises(KeyError):
            store.rename("missing", "new")

    def test_rename_duplicate_target_raises(self) -> None:
        store = ResultStore()
        _add_trace(store, name="a")
        _add_trace(store, name="b")
        with pytest.raises(ValueError, match="already exists"):
            store.rename("a", "b")

    def test_rename_invalid_chars_raises(self) -> None:
        store = ResultStore()
        _add_trace(store, name="trace")
        with pytest.raises(ValueError, match="only contain letters"):
            store.rename("trace", "bad name")

    def test_keys_returns_list(self) -> None:
        store = ResultStore()
        _add_trace(store, name="a")
        _add_trace(store, name="b")
        assert store.keys() == ["a", "b"]

    def test_keys_empty_store(self) -> None:
        store = ResultStore()
        assert store.keys() == []


# ===========================================================================
# FormulaCalculator tests
# ===========================================================================


class TestFormulaCalculator:
    # ---- referenced_names --------------------------------------------------

    def test_referenced_names_empty_formula(self) -> None:
        assert FormulaCalculator.referenced_names("", {"result_1"}) == []

    def test_referenced_names_match_available(self) -> None:
        names = FormulaCalculator.referenced_names("result_1 + result_2", {"result_1", "result_2", "result_3"})
        assert sorted(names) == ["result_1", "result_2"]

    def test_referenced_names_no_match(self) -> None:
        names = FormulaCalculator.referenced_names("x + y", {"result_1"})
        assert names == []

    def test_referenced_names_ignores_numpy_builtins(self) -> None:
        # "log10" is in _ALLOWED_GLOBALS but not in the available set.
        names = FormulaCalculator.referenced_names("20*log10(abs(r1))", {"r1"})
        assert "log10" not in names
        assert "r1" in names

    # ---- evaluate ----------------------------------------------------------

    def test_evaluate_empty_formula_raises(self) -> None:
        calc = FormulaCalculator()
        with pytest.raises(ValueError, match="Empty formula"):
            calc.evaluate("", {})

    def test_evaluate_no_referenced_traces_raises(self) -> None:
        calc = FormulaCalculator()
        store_data = {"r1": {"x": np.array([0.0, 1.0]), "y": np.array([1.0, 2.0])}}
        with pytest.raises(ValueError, match="does not reference any stored trace"):
            calc.evaluate("x + y", store_data)

    def test_evaluate_identity(self) -> None:
        """Formula 'r1' should return the y values of r1."""
        calc = FormulaCalculator(num_points=5)
        x = np.linspace(0.0, 1.0, 5)
        y = np.array([1.0, 2.0, 3.0, 4.0, 5.0])
        store_data = {"r1": {"x": x, "y": y}}
        x_out, y_out, used = calc.evaluate("r1", store_data)
        assert "r1" in used
        np.testing.assert_allclose(y_out, y, atol=1e-10)

    def test_evaluate_addition_of_two_traces(self) -> None:
        calc = FormulaCalculator(num_points=5)
        x = np.linspace(0.0, 1.0, 5)
        y1 = np.ones(5)
        y2 = np.ones(5) * 2.0
        store_data = {
            "r1": {"x": x, "y": y1},
            "r2": {"x": x, "y": y2},
        }
        _, y_out, used = calc.evaluate("r1 + r2", store_data)
        np.testing.assert_allclose(y_out, np.full(5, 3.0), atol=1e-10)
        assert sorted(used) == ["r1", "r2"]

    def test_evaluate_scalar_broadcasts_to_x(self) -> None:
        """Scalar formula result should be broadcast to x shape."""
        calc = FormulaCalculator(num_points=5)
        x = np.linspace(0.0, 1.0, 5)
        store_data = {"r1": {"x": x, "y": np.ones(5)}}
        # np.sum(r1) returns a scalar: 5.0.
        _, y_out, _ = calc.evaluate("np.sum(r1)", store_data)
        assert y_out.shape == x.shape
        np.testing.assert_allclose(y_out, np.full(5, 5.0), atol=1e-10)

    def test_evaluate_numpy_math_functions(self) -> None:
        """Bare-name numpy aliases (log10, abs, ...) must be accessible."""
        calc = FormulaCalculator(num_points=5)
        x = np.linspace(1.0, 10.0, 5)
        y = np.ones(5) * 10.0
        store_data = {"r1": {"x": x, "y": y}}
        _, y_out, _ = calc.evaluate("20*log10(abs(r1))", store_data)
        np.testing.assert_allclose(y_out, np.full(5, 20.0), atol=1e-10)

    def test_evaluate_uses_pi_constant(self) -> None:
        calc = FormulaCalculator(num_points=5)
        x = np.linspace(0.0, 1.0, 5)
        store_data = {"r1": {"x": x, "y": np.ones(5)}}
        _, y_out, _ = calc.evaluate("r1 * pi", store_data)
        np.testing.assert_allclose(y_out, np.full(5, np.pi), atol=1e-10)

    def test_evaluate_subtraction(self) -> None:
        calc = FormulaCalculator(num_points=5)
        x = np.linspace(0.0, 1.0, 5)
        store_data = {
            "r1": {"x": x, "y": np.ones(5) * 5.0},
            "r2": {"x": x, "y": np.ones(5) * 3.0},
        }
        _, y_out, _ = calc.evaluate("r1 - r2", store_data)
        np.testing.assert_allclose(y_out, np.full(5, 2.0), atol=1e-10)

    def test_evaluate_returns_used_names(self) -> None:
        calc = FormulaCalculator(num_points=5)
        x = np.linspace(0.0, 1.0, 5)
        store_data = {
            "r1": {"x": x, "y": np.ones(5)},
            "r2": {"x": x, "y": np.ones(5)},
            "r3": {"x": x, "y": np.ones(5)},
        }
        _, _, used = calc.evaluate("r1 + r2", store_data)
        assert "r3" not in used
        assert set(used) == {"r1", "r2"}

    # ---- alignment strategies ----------------------------------------------

    def test_align_common_interval(self) -> None:
        calc = FormulaCalculator(num_points=11, interval_strategy="common")
        # r1 spans [0, 2], r2 spans [1, 3] -> common interval is [1, 2].
        store_data = {
            "r1": {"x": np.array([0.0, 1.0, 2.0]), "y": np.array([0.0, 1.0, 2.0])},
            "r2": {"x": np.array([1.0, 2.0, 3.0]), "y": np.array([1.0, 2.0, 3.0])},
        }
        x_out, _, _ = calc.evaluate("r1 + r2", store_data)
        assert x_out[0] == pytest.approx(1.0, abs=1e-9)
        assert x_out[-1] == pytest.approx(2.0, abs=1e-9)

    def test_align_extended_interval(self) -> None:
        calc = FormulaCalculator(num_points=11, interval_strategy="extended")
        store_data = {
            "r1": {"x": np.array([0.0, 1.0]), "y": np.array([0.0, 1.0])},
            "r2": {"x": np.array([0.5, 1.5]), "y": np.array([0.5, 1.5])},
        }
        x_out, _, _ = calc.evaluate("r1 + r2", store_data)
        # Extended interval spans [0.0, 1.5].
        assert x_out[0] == pytest.approx(0.0, abs=1e-9)
        assert x_out[-1] == pytest.approx(1.5, abs=1e-9)

    def test_align_common_interval_empty_raises(self) -> None:
        calc = FormulaCalculator(num_points=5, interval_strategy="common")
        # Disjoint x-ranges -> empty common interval.
        store_data = {
            "r1": {"x": np.array([0.0, 1.0]), "y": np.array([0.0, 1.0])},
            "r2": {"x": np.array([2.0, 3.0]), "y": np.array([2.0, 3.0])},
        }
        with pytest.raises(ValueError, match="Common x interval is empty"):
            calc.evaluate("r1 + r2", store_data)

    def test_align_unknown_strategy_raises(self) -> None:
        calc = FormulaCalculator(num_points=5, interval_strategy="unknown_strategy")
        store_data = {
            "r1": {"x": np.array([0.0, 1.0]), "y": np.array([0.0, 1.0])},
            "r2": {"x": np.array([0.0, 1.0]), "y": np.array([1.0, 2.0])},
        }
        with pytest.raises(ValueError, match="Unknown interval strategy"):
            calc.evaluate("r1 + r2", store_data)

    def test_align_no_interpolation_same_axes_passes(self) -> None:
        calc = FormulaCalculator(interpolate=False)
        x = np.linspace(0.0, 1.0, 5)
        store_data = {
            "r1": {"x": x.copy(), "y": np.ones(5)},
            "r2": {"x": x.copy(), "y": np.ones(5) * 2.0},
        }
        _, y_out, _ = calc.evaluate("r1 + r2", store_data)
        np.testing.assert_allclose(y_out, np.full(5, 3.0), atol=1e-10)

    def test_align_no_interpolation_different_axes_raises(self) -> None:
        calc = FormulaCalculator(interpolate=False)
        store_data = {
            "r1": {"x": np.array([0.0, 1.0, 2.0]), "y": np.ones(3)},
            "r2": {"x": np.array([0.0, 1.5, 3.0]), "y": np.ones(3)},
        }
        with pytest.raises(ValueError, match="different x axis"):
            calc.evaluate("r1 + r2", store_data)

    # ---- _interp_one -------------------------------------------------------

    def test_interp_one_linear_on_known_points(self) -> None:
        calc = FormulaCalculator(interval_strategy="common")
        x_old = np.array([0.0, 1.0, 2.0])
        y_old = np.array([0.0, 1.0, 2.0])
        x_new = np.array([0.0, 0.5, 1.0, 1.5, 2.0])
        y_new = calc._interp_one(x_old, y_old, x_new)
        np.testing.assert_allclose(y_new, x_new, atol=1e-10)

    def test_interp_one_sorts_unsorted_x(self) -> None:
        calc = FormulaCalculator(interval_strategy="common")
        x_old = np.array([2.0, 0.0, 1.0])
        y_old = np.array([2.0, 0.0, 1.0])
        x_new = np.array([0.0, 0.5, 1.0, 2.0])
        y_new = calc._interp_one(x_old, y_old, x_new)
        np.testing.assert_allclose(y_new, x_new, atol=1e-10)

    def test_interp_one_extended_linear_extrapolation(self) -> None:
        """Linear extrapolation outside the original range in 'extended' mode."""
        calc = FormulaCalculator(interval_strategy="extended")
        x_old = np.array([1.0, 2.0])
        y_old = np.array([1.0, 2.0])  # slope = 1
        x_new = np.array([0.0, 1.0, 2.0, 3.0])
        y_new = calc._interp_one(x_old, y_old, x_new)
        # Expected: linear extrapolation -> y = x.
        np.testing.assert_allclose(y_new, x_new, atol=1e-10)

    # ---- INTERP_KINDS constant ---------------------------------------------

    def test_interp_kinds_contains_expected_options(self) -> None:
        expected = {"linear", "quadratic", "cubic", "nearest"}
        assert set(FormulaCalculator.INTERP_KINDS) == expected

    def test_interval_strategies_contains_expected_options(self) -> None:
        expected = {"common", "extended"}
        assert set(FormulaCalculator.INTERVAL_STRATEGIES) == expected


# ===========================================================================
# FileFormats tests
# ===========================================================================


class TestFileFormats:
    # ---- parse_delimited ---------------------------------------------------

    def test_parse_delimited_csv(self, tmp_path: Path) -> None:
        f = tmp_path / "data.csv"
        f.write_text("1.0,10.0\n2.0,20.0\n3.0,30.0\n")
        x, y = FileFormats.parse_delimited(str(f), separator=",")
        np.testing.assert_array_equal(x, [1.0, 2.0, 3.0])
        np.testing.assert_array_equal(y, [10.0, 20.0, 30.0])

    def test_parse_delimited_tsv(self, tmp_path: Path) -> None:
        f = tmp_path / "data.tsv"
        f.write_text("1.0\t10.0\n2.0\t20.0\n")
        x, y = FileFormats.parse_delimited(str(f), separator="\t")
        np.testing.assert_array_equal(x, [1.0, 2.0])
        np.testing.assert_array_equal(y, [10.0, 20.0])

    def test_parse_delimited_tab_escape_sequence(self, tmp_path: Path) -> None:
        """The UI passes the separator as the string r'\t'; the parser must treat it as a tab."""
        f = tmp_path / "data.tsv"
        f.write_text("1.0\t10.0\n2.0\t20.0\n")
        x, y = FileFormats.parse_delimited(str(f), separator=r"\t")
        np.testing.assert_array_equal(x, [1.0, 2.0])
        np.testing.assert_array_equal(y, [10.0, 20.0])

    def test_parse_delimited_skip_comment_lines(self, tmp_path: Path) -> None:
        f = tmp_path / "data.csv"
        f.write_text("# This is a comment\n1.0,2.0\n# Another comment\n3.0,4.0\n")
        x, y = FileFormats.parse_delimited(str(f), separator=",")
        np.testing.assert_array_equal(x, [1.0, 3.0])
        np.testing.assert_array_equal(y, [2.0, 4.0])

    def test_parse_delimited_skip_blank_lines(self, tmp_path: Path) -> None:
        f = tmp_path / "data.csv"
        f.write_text("1.0,2.0\n\n3.0,4.0\n")
        x, y = FileFormats.parse_delimited(str(f), separator=",")
        np.testing.assert_array_equal(x, [1.0, 3.0])
        np.testing.assert_array_equal(y, [2.0, 4.0])

    def test_parse_delimited_header_lines_skipped(self, tmp_path: Path) -> None:
        f = tmp_path / "data.csv"
        f.write_text("x,y\n1.0,2.0\n3.0,4.0\n")
        x, y = FileFormats.parse_delimited(str(f), separator=",", header_lines=1)
        np.testing.assert_array_equal(x, [1.0, 3.0])
        np.testing.assert_array_equal(y, [2.0, 4.0])

    def test_parse_delimited_custom_column_indices(self, tmp_path: Path) -> None:
        f = tmp_path / "data.csv"
        f.write_text("a,b,c\n1.0,2.0,3.0\n4.0,5.0,6.0\n")
        x, y = FileFormats.parse_delimited(str(f), separator=",", header_lines=1, x_col=1, y_col=2)
        np.testing.assert_array_equal(x, [2.0, 5.0])
        np.testing.assert_array_equal(y, [3.0, 6.0])

    def test_parse_delimited_no_data_raises(self, tmp_path: Path) -> None:
        f = tmp_path / "data.csv"
        f.write_text("# Only comments\n# No data\n")
        with pytest.raises(ValueError, match="No data rows found"):
            FileFormats.parse_delimited(str(f), separator=",")

    def test_parse_delimited_bad_line_raises(self, tmp_path: Path) -> None:
        f = tmp_path / "data.csv"
        f.write_text("1.0,2.0\nnot_a_number,3.0\n")
        with pytest.raises(ValueError, match="Cannot parse line"):
            FileFormats.parse_delimited(str(f), separator=",")

    def test_parse_delimited_space_separator(self, tmp_path: Path) -> None:
        f = tmp_path / "data.txt"
        f.write_text("1.0 10.0\n2.0 20.0\n")
        x, y = FileFormats.parse_delimited(str(f), separator=" ")
        np.testing.assert_array_equal(x, [1.0, 2.0])
        np.testing.assert_array_equal(y, [10.0, 20.0])

    def test_parse_delimited_returns_float_arrays(self, tmp_path: Path) -> None:
        f = tmp_path / "data.csv"
        f.write_text("1,2\n3,4\n")
        x, y = FileFormats.parse_delimited(str(f), separator=",")
        assert x.dtype == float
        assert y.dtype == float

    def test_parse_delimited_multiple_header_lines(self, tmp_path: Path) -> None:
        f = tmp_path / "data.csv"
        f.write_text("Line 1\nLine 2\n1.0,10.0\n2.0,20.0\n")
        x, y = FileFormats.parse_delimited(str(f), separator=",", header_lines=2)
        np.testing.assert_array_equal(x, [1.0, 2.0])
        np.testing.assert_array_equal(y, [10.0, 20.0])

    # ---- touchstone_port_count ---------------------------------------------

    def test_touchstone_port_count_1port(self) -> None:
        assert FileFormats.touchstone_port_count("network.s1p") == 1

    def test_touchstone_port_count_2port(self) -> None:
        assert FileFormats.touchstone_port_count("path/to/net.S2P") == 2

    def test_touchstone_port_count_multiport(self) -> None:
        assert FileFormats.touchstone_port_count("device.s17p") == 17

    def test_touchstone_port_count_snp_returns_none(self) -> None:
        assert FileFormats.touchstone_port_count("device.snp") is None

    def test_touchstone_port_count_csv_returns_none(self) -> None:
        assert FileFormats.touchstone_port_count("file.csv") is None

    def test_touchstone_port_count_no_extension_returns_none(self) -> None:
        assert FileFormats.touchstone_port_count("no_extension") is None

    def test_touchstone_port_count_case_insensitive(self) -> None:
        assert FileFormats.touchstone_port_count("NET.S4P") == 4

    # ---- FORMATS list ------------------------------------------------------

    def test_formats_list_is_populated(self) -> None:
        assert len(FileFormats.FORMATS) > 0

    def test_formats_csv_entry_present(self) -> None:
        names = [fmt.name for fmt in FileFormats.FORMATS]
        assert any("CSV" in n for n in names)

    def test_formats_touchstone_entry_present(self) -> None:
        names = [fmt.name for fmt in FileFormats.FORMATS]
        assert any("Touchstone" in n for n in names)

    def test_formats_each_has_parser_callable(self) -> None:
        for fmt in FileFormats.FORMATS:
            assert callable(fmt.parser)

    def test_formats_tsv_uses_tab_separator(self) -> None:
        tsv_fmt = next(f for f in FileFormats.FORMATS if "TSV" in f.name)
        assert tsv_fmt.default_separator in (r"\t", "\t")

    def test_formats_touchstone_separator_not_editable(self) -> None:
        ts_fmt = next(f for f in FileFormats.FORMATS if "Touchstone" in f.name)
        assert ts_fmt.separator_editable is False

    def test_formats_csv_separator_editable(self) -> None:
        csv_fmt = next(f for f in FileFormats.FORMATS if "CSV" in f.name)
        assert csv_fmt.separator_editable is True


# ===========================================================================
# ResultDataService tests
# ===========================================================================


class TestResultDataService:
    # ---- _empty_session_cache ----------------------------------------------

    def test_empty_session_cache_has_expected_keys(self) -> None:
        cache = ResultDataService._empty_session_cache()
        assert "projects_designs" in cache
        assert "existing_reports" in cache
        assert "solution_info" in cache
        assert "aedtapp_cache" in cache

    def test_empty_session_cache_values_are_empty_dicts(self) -> None:
        cache = ResultDataService._empty_session_cache()
        for v in cache.values():
            assert isinstance(v, dict)
            assert len(v) == 0

    def test_empty_session_cache_returns_independent_instances(self) -> None:
        cache_a = ResultDataService._empty_session_cache()
        cache_b = ResultDataService._empty_session_cache()
        cache_a["projects_designs"]["x"] = 1
        assert "x" not in cache_b["projects_designs"]

    # ---- _extract_session_metadata ----------------------------------------

    def test_extract_session_metadata_with_version(self) -> None:
        service = _make_service()
        cmdline = r"C:\Program Files\ANSYS Inc\v261\common\mono\mono.exe"
        meta = service._extract_session_metadata(cmdline)
        assert meta["version"] is not None
        assert "2026" in str(meta["version"])

    def test_extract_session_metadata_non_graphical_flag(self) -> None:
        service = _make_service()
        cmdline = r"C:\AnsysEM\v261\Win64\ansysedt.exe -ng"
        meta = service._extract_session_metadata(cmdline)
        assert meta["non_graphical"] is True

    def test_extract_session_metadata_graphical_mode(self) -> None:
        service = _make_service()
        cmdline = r"C:\AnsysEM\v261\Win64\ansysedt.exe"
        meta = service._extract_session_metadata(cmdline)
        assert meta["non_graphical"] is False

    def test_extract_session_metadata_no_cmdline(self) -> None:
        service = _make_service()
        meta = service._extract_session_metadata(None)
        assert meta["version"] == "unknown"
        assert meta["non_graphical"] is None

    def test_extract_session_metadata_empty_cmdline(self) -> None:
        service = _make_service()
        meta = service._extract_session_metadata("")
        assert meta["version"] == "unknown"

    def test_extract_session_metadata_linux_style_path(self) -> None:
        service = _make_service()
        cmdline = "/opt/ansys_inc/v261/Linux64/ansysedt -ng"
        meta = service._extract_session_metadata(cmdline)
        assert "2026" in str(meta["version"])
        assert meta["non_graphical"] is True

    # ---- format_session_label ----------------------------------------------

    def test_format_session_label_basic(self) -> None:
        session = {"pid": 1234, "version": "2026.1", "port": 50051, "student_version": False, "non_graphical": False}
        with patch(f"{_MODULE}.AEDT_PROCESS_ID", 9999):
            label = ResultDataService.format_session_label(session)
        assert "1234" in label
        assert "2026.1" in label
        assert "50051" in label

    def test_format_session_label_student_version(self) -> None:
        session = {"pid": 1234, "version": "2026.1", "port": 50051, "student_version": True, "non_graphical": False}
        with patch(f"{_MODULE}.AEDT_PROCESS_ID", 9999):
            label = ResultDataService.format_session_label(session)
        assert "student" in label

    def test_format_session_label_non_graphical(self) -> None:
        session = {"pid": 1234, "version": "2026.1", "port": 50051, "student_version": False, "non_graphical": True}
        with patch(f"{_MODULE}.AEDT_PROCESS_ID", 9999):
            label = ResultDataService.format_session_label(session)
        assert "non-graphical" in label

    def test_format_session_label_current_session(self) -> None:
        session = {"pid": 1234, "version": "2026.1", "port": 50051, "student_version": False, "non_graphical": False}
        with patch(f"{_MODULE}.AEDT_PROCESS_ID", 1234):
            label = ResultDataService.format_session_label(session)
        assert "current" in label

    def test_format_session_label_com_port(self) -> None:
        session = {
            "pid": 1234,
            "version": "2026.1",
            "port": "n/a (com)",
            "student_version": False,
            "non_graphical": False,
        }
        with patch(f"{_MODULE}.AEDT_PROCESS_ID", 9999):
            label = ResultDataService.format_session_label(session)
        assert "n/a (com)" in label

    def test_format_session_label_no_student_no_ng_no_current(self) -> None:
        session = {"pid": 5555, "version": "2025.2", "port": 50099, "student_version": False, "non_graphical": False}
        with patch(f"{_MODULE}.AEDT_PROCESS_ID", 9999):
            label = ResultDataService.format_session_label(session)
        assert "student" not in label
        assert "non-graphical" not in label
        assert "current" not in label

    # ---- _ensure_connected / _current_cache --------------------------------

    def test_ensure_connected_raises_when_no_session(self) -> None:
        service = _make_service()
        with pytest.raises(AEDTRuntimeError, match="No AEDT session selected"):
            service._ensure_connected()

    def test_ensure_connected_raises_when_desktop_is_none(self) -> None:
        service = _make_service()
        service.current_session_pid = 1
        service.desktop = None
        with pytest.raises(AEDTRuntimeError):
            service._ensure_connected()

    def test_current_cache_raises_when_not_connected(self) -> None:
        service = _make_service()
        with pytest.raises(AEDTRuntimeError):
            _ = service._current_cache

    def test_current_cache_returns_correct_session_cache(self) -> None:
        service = _make_service()
        service.desktop = MagicMock()
        service.current_session_pid = 42
        service._cache_by_session[42] = ResultDataService._empty_session_cache()
        service._cache_by_session[42]["projects_designs"]["x"] = "sentinel"
        cache = service._current_cache
        assert cache["projects_designs"]["x"] == "sentinel"

    # ---- property accessors ------------------------------------------------

    def test_projects_designs_property(self) -> None:
        service = _make_service()
        service.desktop = MagicMock()
        service.current_session_pid = 1
        service._cache_by_session[1] = ResultDataService._empty_session_cache()
        service._cache_by_session[1]["projects_designs"]["P"] = ["D1"]
        assert service.projects_designs == {"P": ["D1"]}

    def test_existing_reports_property(self) -> None:
        service = _make_service()
        service.desktop = MagicMock()
        service.current_session_pid = 1
        service._cache_by_session[1] = ResultDataService._empty_session_cache()
        service._cache_by_session[1]["existing_reports"]["Proj"] = {}
        assert "Proj" in service.existing_reports

    def test_solution_info_property(self) -> None:
        service = _make_service()
        service.desktop = MagicMock()
        service.current_session_pid = 1
        service._cache_by_session[1] = ResultDataService._empty_session_cache()
        service._cache_by_session[1]["solution_info"]["Proj"] = {"Des": {}}
        assert service.solution_info["Proj"]["Des"] == {}

    # ---- get_projects_list -------------------------------------------------

    def test_get_projects_list_no_desktop(self) -> None:
        service = _make_service()
        projects, msg = service.get_projects_list()
        assert projects == []
        assert msg is not None

    def test_get_projects_list_with_projects(self) -> None:
        service = _make_service()
        service.desktop = MagicMock()
        service.desktop.project_list = ["ProjectB", "ProjectA"]
        service.current_session_pid = 1234
        service._cache_by_session[1234] = ResultDataService._empty_session_cache()
        projects, msg = service.get_projects_list()
        assert sorted(projects) == ["ProjectA", "ProjectB"]
        assert msg is None

    def test_get_projects_list_empty_returns_message(self) -> None:
        service = _make_service()
        service.desktop = MagicMock()
        service.desktop.project_list = []
        service.current_session_pid = 1234
        service._cache_by_session[1234] = ResultDataService._empty_session_cache()
        projects, msg = service.get_projects_list()
        assert projects == []
        assert msg is not None

    def test_get_projects_list_exception_returns_error(self) -> None:
        service = _make_service()
        service.desktop = MagicMock()
        service.desktop.project_list = property(lambda self: (_ for _ in ()).throw(RuntimeError("boom")))
        service.current_session_pid = 1234
        service._cache_by_session[1234] = ResultDataService._empty_session_cache()
        # Accessing project_list raises; get_projects_list should catch it.
        service.desktop.project_list = MagicMock(side_effect=RuntimeError("boom"))
        projects, msg = service.get_projects_list()
        # Either no projects returned, or msg is not None.
        assert projects == [] or msg is not None

    # ---- clear_all_caches --------------------------------------------------

    def test_clear_all_caches_removes_cached_data(self) -> None:
        service = _make_service()
        service._cache_by_session[1234] = ResultDataService._empty_session_cache()
        service.current_session_pid = 1234
        service.clear_all_caches()
        assert service._cache_by_session == {}
        assert service.current_session_pid is None

    def test_clear_all_caches_re_discovers_sessions(self) -> None:
        service = _make_service()
        new_map = {7777: 50070}
        with (
            patch(f"{_MODULE}.active_sessions", return_value=new_map),
            patch(f"{_MODULE}._check_psutil_connections", return_value={}),
        ):
            service.clear_all_caches()
        assert any(s["pid"] == 7777 for s in service.active_sessions)

    # ---- set_session -------------------------------------------------------

    def test_set_session_pid_not_found_raises(self) -> None:
        service = _make_service()
        service.active_sessions = [{"pid": 111, "port": 50051}]
        with pytest.raises(AEDTRuntimeError, match="not found"):
            with patch(f"{_MODULE}.Desktop"):
                service.set_session(999)

    def test_set_session_already_connected_returns_early(self) -> None:
        service = _make_service()
        service.active_sessions = [{"pid": 111, "port": 50051}]
        service.current_session_pid = 111
        service.desktop = MagicMock()
        with patch.object(service, "_connect_to_session") as mock_connect:
            service.set_session(111)
            mock_connect.assert_not_called()

    def test_set_session_creates_empty_cache_for_new_pid(self) -> None:
        service = _make_service()
        service.active_sessions = [{"pid": 222, "port": 50052}]
        with patch.object(service, "_connect_to_session"):
            service.set_session(222)
        assert 222 in service._cache_by_session

    def test_set_session_resets_aedtapp_cache_on_reconnect(self) -> None:
        service = _make_service()
        service.active_sessions = [{"pid": 333, "port": 50053}]
        # Pre-populate with stale aedtapp handles.
        service._cache_by_session[333] = ResultDataService._empty_session_cache()
        service._cache_by_session[333]["aedtapp_cache"][("proj", "des")] = MagicMock()
        with patch.object(service, "_connect_to_session"):
            service.set_session(333)
        assert service._cache_by_session[333]["aedtapp_cache"] == {}

    def test_set_session_sets_current_pid(self) -> None:
        service = _make_service()
        service.active_sessions = [{"pid": 444, "port": 50054}]
        with patch.object(service, "_connect_to_session"):
            service.set_session(444)
        assert service.current_session_pid == 444

    # ---- load_designs ------------------------------------------------------

    def test_load_designs_populates_cache(self) -> None:
        service = _make_service()
        service.desktop = MagicMock()
        service.desktop.design_list.return_value = ["DesignA", "DesignB"]
        service.current_session_pid = 1
        service._cache_by_session[1] = ResultDataService._empty_session_cache()

        designs, msg = service.load_designs("MyProject")
        assert sorted(designs) == ["DesignA", "DesignB"]
        assert msg is None

    def test_load_designs_uses_cache_on_second_call(self) -> None:
        service = _make_service()
        service.desktop = MagicMock()
        service.desktop.design_list.return_value = ["DesignA"]
        service.current_session_pid = 1
        service._cache_by_session[1] = ResultDataService._empty_session_cache()

        service.load_designs("MyProject")
        # Second call should NOT hit desktop again.
        service.desktop.design_list.return_value = ["Different"]
        designs, _ = service.load_designs("MyProject")
        assert designs == ["DesignA"]

    def test_load_designs_empty_returns_message(self) -> None:
        service = _make_service()
        service.desktop = MagicMock()
        service.desktop.design_list.return_value = []
        service.current_session_pid = 1
        service._cache_by_session[1] = ResultDataService._empty_session_cache()

        designs, msg = service.load_designs("EmptyProject")
        assert designs == []
        assert msg is not None

    def test_load_designs_mirrors_to_existing_reports_and_solution_info(self) -> None:
        service = _make_service()
        service.desktop = MagicMock()
        service.desktop.design_list.return_value = ["D1", "D2"]
        service.current_session_pid = 1
        service._cache_by_session[1] = ResultDataService._empty_session_cache()

        service.load_designs("Proj")
        er = service.existing_reports
        si = service.solution_info
        assert "D1" in er.get("Proj", {})
        assert "D2" in er.get("Proj", {})
        assert "D1" in si.get("Proj", {})
        assert "D2" in si.get("Proj", {})

    def test_load_designs_exception_returns_empty_list(self) -> None:
        service = _make_service()
        service.desktop = MagicMock()
        service.desktop.design_list.side_effect = RuntimeError("AEDT error")
        service.current_session_pid = 1
        service._cache_by_session[1] = ResultDataService._empty_session_cache()

        designs, msg = service.load_designs("Proj")
        assert designs == []
        assert msg is not None

    # ---- load_reports_for_design -------------------------------------------

    def test_load_reports_for_design_lazy_fetch(self) -> None:
        service = _make_service()
        service.desktop = MagicMock()
        service.current_session_pid = 1
        service._cache_by_session[1] = ResultDataService._empty_session_cache()

        report1 = MagicMock()
        report1.plot_name = "SParams"
        report2 = MagicMock()
        report2.plot_name = "Gain"

        aedtapp = MagicMock()
        aedtapp.post.plots = [report1, report2]
        with patch.object(service, "_get_aedtapp", return_value=aedtapp):
            reports, msg = service.load_reports_for_design("Proj", "Des")
        assert sorted(reports) == ["Gain", "SParams"]
        assert msg is None

    def test_load_reports_for_design_uses_cache(self) -> None:
        service = _make_service()
        service.desktop = MagicMock()
        service.current_session_pid = 1
        service._cache_by_session[1] = ResultDataService._empty_session_cache()
        # Pre-populate the cache.
        service.existing_reports.setdefault("Proj", {})["Des"] = {"CachedReport": {}}

        with patch.object(service, "_get_aedtapp") as mock_app:
            reports, _ = service.load_reports_for_design("Proj", "Des")
            mock_app.assert_not_called()
        assert reports == ["CachedReport"]

    def test_load_reports_for_design_empty_returns_message(self) -> None:
        service = _make_service()
        service.desktop = MagicMock()
        service.current_session_pid = 1
        service._cache_by_session[1] = ResultDataService._empty_session_cache()

        aedtapp = MagicMock()
        aedtapp.post.plots = []
        with patch.object(service, "_get_aedtapp", return_value=aedtapp):
            reports, msg = service.load_reports_for_design("Proj", "Des")
        assert reports == []
        assert msg is not None

    def test_load_reports_for_design_exception_returns_error(self) -> None:
        service = _make_service()
        service.desktop = MagicMock()
        service.current_session_pid = 1
        service._cache_by_session[1] = ResultDataService._empty_session_cache()

        with patch.object(service, "_get_aedtapp", side_effect=RuntimeError("AEDT crashed")):
            reports, msg = service.load_reports_for_design("Proj", "Des")
        assert reports == []
        assert msg is not None

    # ---- load_traces_for_report --------------------------------------------

    def test_load_traces_for_report_lazy_fetch(self) -> None:
        service = _make_service()
        service.desktop = MagicMock()
        service.current_session_pid = 1
        service._cache_by_session[1] = ResultDataService._empty_session_cache()
        service.existing_reports.setdefault("Proj", {}).setdefault("Des", {})["Report1"] = {}

        report = MagicMock()
        report.plot_name = "Report1"
        report.expressions = ["S11", "S21"]
        aedtapp = MagicMock()
        aedtapp.post.plots = [report]
        with patch.object(service, "_get_aedtapp", return_value=aedtapp):
            traces, msg = service.load_traces_for_report("Proj", "Des", "Report1")
        assert sorted(traces) == ["S11", "S21"]
        assert msg is None

    def test_load_traces_for_report_uses_cache(self) -> None:
        service = _make_service()
        service.desktop = MagicMock()
        service.current_session_pid = 1
        service._cache_by_session[1] = ResultDataService._empty_session_cache()
        service.existing_reports.setdefault("Proj", {}).setdefault("Des", {})["Report1"] = {"S11": None}

        with patch.object(service, "_get_aedtapp") as mock_app:
            traces, _ = service.load_traces_for_report("Proj", "Des", "Report1")
            mock_app.assert_not_called()
        assert traces == ["S11"]

    def test_load_traces_for_report_empty_raises_message(self) -> None:
        service = _make_service()
        service.desktop = MagicMock()
        service.current_session_pid = 1
        service._cache_by_session[1] = ResultDataService._empty_session_cache()
        service.existing_reports.setdefault("Proj", {}).setdefault("Des", {})["Report1"] = {}

        report = MagicMock()
        report.plot_name = "Report1"
        report.expressions = []
        aedtapp = MagicMock()
        aedtapp.post.plots = [report]
        with patch.object(service, "_get_aedtapp", return_value=aedtapp):
            traces, msg = service.load_traces_for_report("Proj", "Des", "Report1")
        assert traces == []
        assert msg is not None

    def test_load_traces_for_report_exception_returns_error(self) -> None:
        service = _make_service()
        service.desktop = MagicMock()
        service.current_session_pid = 1
        service._cache_by_session[1] = ResultDataService._empty_session_cache()
        service.existing_reports.setdefault("Proj", {}).setdefault("Des", {})["Report1"] = {}

        with patch.object(service, "_get_aedtapp", side_effect=RuntimeError("boom")):
            traces, msg = service.load_traces_for_report("Proj", "Des", "Report1")
        assert traces == []
        assert msg is not None

    # ---- get_trace_data ----------------------------------------------------

    def test_get_trace_data_fetches_and_caches(self) -> None:
        service = _make_service()
        service.desktop = MagicMock()
        service.current_session_pid = 1
        service._cache_by_session[1] = ResultDataService._empty_session_cache()
        service.existing_reports.setdefault("Proj", {}).setdefault("Des", {})["Rep"] = {"S11": None}

        x = np.array([1.0, 2.0, 3.0])
        y_real = np.array([-10.0, -20.0, -30.0])
        sol = _make_sol_data(x, y_real)

        report = MagicMock()
        report.plot_name = "Rep"
        report.get_solution_data.return_value = sol
        aedtapp = MagicMock()
        aedtapp.post.plots = [report]
        with patch.object(service, "_get_aedtapp", return_value=aedtapp):
            data = service.get_trace_data("Proj", "Des", "Rep", "S11")

        np.testing.assert_array_equal(data["x"], x)
        np.testing.assert_array_equal(data["y"], y_real)
        assert data["is_complex"] is False

    def test_get_trace_data_uses_cache(self) -> None:
        service = _make_service()
        service.desktop = MagicMock()
        service.current_session_pid = 1
        service._cache_by_session[1] = ResultDataService._empty_session_cache()
        cached = {"x": np.array([1.0]), "y": np.array([2.0])}
        service.existing_reports.setdefault("Proj", {}).setdefault("Des", {})["Rep"] = {"S11": cached}

        with patch.object(service, "_get_aedtapp") as mock_app:
            data = service.get_trace_data("Proj", "Des", "Rep", "S11")
            mock_app.assert_not_called()
        assert data is cached

    def test_get_trace_data_report_not_found_raises(self) -> None:
        service = _make_service()
        service.desktop = MagicMock()
        service.current_session_pid = 1
        service._cache_by_session[1] = ResultDataService._empty_session_cache()
        service.existing_reports.setdefault("Proj", {}).setdefault("Des", {})["Rep"] = {"S11": None}

        aedtapp = MagicMock()
        aedtapp.post.plots = []  # Report not present.
        with patch.object(service, "_get_aedtapp", return_value=aedtapp):
            with pytest.raises(AEDTRuntimeError, match="not found"):
                service.get_trace_data("Proj", "Des", "Rep", "S11")

    def test_get_trace_data_stores_result_as_ndarray(self) -> None:
        service = _make_service()
        service.desktop = MagicMock()
        service.current_session_pid = 1
        service._cache_by_session[1] = ResultDataService._empty_session_cache()
        service.existing_reports.setdefault("Proj", {}).setdefault("Des", {})["Rep"] = {"S11": None}

        sol = _make_sol_data([1.0, 2.0], [-10.0, -20.0])  # plain lists, not ndarray
        report = MagicMock()
        report.plot_name = "Rep"
        report.get_solution_data.return_value = sol
        aedtapp = MagicMock()
        aedtapp.post.plots = [report]
        with patch.object(service, "_get_aedtapp", return_value=aedtapp):
            data = service.get_trace_data("Proj", "Des", "Rep", "S11")
        assert isinstance(data["x"], np.ndarray)
        assert isinstance(data["y"], np.ndarray)

    def test_get_trace_data_complex_trace_returns_complex_y(self) -> None:
        """When the imaginary part is non-zero, y must be a complex ndarray."""
        service = _make_service()
        service.desktop = MagicMock()
        service.current_session_pid = 1
        service._cache_by_session[1] = ResultDataService._empty_session_cache()
        service.existing_reports.setdefault("Proj", {}).setdefault("Des", {})["Rep"] = {"S11": None}

        x = np.array([1e9, 2e9, 3e9])
        y_real = np.array([0.5, 0.3, 0.1])
        y_imag = np.array([-0.2, -0.4, -0.6])
        sol = _make_sol_data(x, y_real, y_imag)

        report = MagicMock()
        report.plot_name = "Rep"
        report.get_solution_data.return_value = sol
        aedtapp = MagicMock()
        aedtapp.post.plots = [report]
        with patch.object(service, "_get_aedtapp", return_value=aedtapp):
            data = service.get_trace_data("Proj", "Des", "Rep", "S11")

        assert data["is_complex"] is True
        assert np.iscomplexobj(data["y"])
        np.testing.assert_allclose(data["y"].real, y_real, atol=1e-12)
        np.testing.assert_allclose(data["y"].imag, y_imag, atol=1e-12)

    def test_get_trace_data_real_only_trace_is_not_complex(self) -> None:
        """A trace with all-zero imaginary part must be marked as not complex."""
        service = _make_service()
        service.desktop = MagicMock()
        service.current_session_pid = 1
        service._cache_by_session[1] = ResultDataService._empty_session_cache()
        service.existing_reports.setdefault("Proj", {}).setdefault("Des", {})["Rep"] = {"Mag": None}

        x = np.array([0.0, 1.0])
        y_real = np.array([1.0, 2.0])
        y_imag = np.array([0.0, 0.0])
        sol = _make_sol_data(x, y_real, y_imag, expression="Mag")

        report = MagicMock()
        report.plot_name = "Rep"
        report.get_solution_data.return_value = sol
        aedtapp = MagicMock()
        aedtapp.post.plots = [report]
        with patch.object(service, "_get_aedtapp", return_value=aedtapp):
            data = service.get_trace_data("Proj", "Des", "Rep", "Mag")

        assert data["is_complex"] is False
        assert not np.iscomplexobj(data["y"])

    # ---- load_datasets_for_design ------------------------------------------

    def test_load_datasets_for_design_returns_2d_datasets_only(self) -> None:
        service = _make_service()
        service.desktop = MagicMock()
        service.current_session_pid = 1
        service._cache_by_session[1] = ResultDataService._empty_session_cache()

        ds_2d = SimpleNamespace(x=[1.0, 2.0], y=[3.0, 4.0], z=[])
        ds_3d = SimpleNamespace(x=[1.0], y=[2.0], z=[3.0])
        aedtapp = MagicMock()
        aedtapp.project_datasets = {"ds_2d": ds_2d}
        aedtapp.design_datasets = {"ds_3d": ds_3d}
        with patch.object(service, "_get_aedtapp", return_value=aedtapp):
            names, msg = service.load_datasets_for_design("Proj", "Des")
        assert "ds_2d" in names
        assert "ds_3d" not in names
        assert msg is None

    def test_load_datasets_for_design_empty_returns_message(self) -> None:
        service = _make_service()
        service.desktop = MagicMock()
        service.current_session_pid = 1
        service._cache_by_session[1] = ResultDataService._empty_session_cache()

        aedtapp = MagicMock()
        aedtapp.project_datasets = {}
        aedtapp.design_datasets = {}
        with patch.object(service, "_get_aedtapp", return_value=aedtapp):
            names, msg = service.load_datasets_for_design("Proj", "Des")
        assert names == []
        assert msg is not None

    def test_load_datasets_for_design_uses_cache(self) -> None:
        service = _make_service()
        service.desktop = MagicMock()
        service.current_session_pid = 1
        service._cache_by_session[1] = ResultDataService._empty_session_cache()
        ds = SimpleNamespace(x=[0.0], y=[1.0], z=[])
        service.solution_info.setdefault("Proj", {})["Des"] = {"datasets": {"cached_ds": ds}}

        with patch.object(service, "_get_aedtapp") as mock_app:
            names, _ = service.load_datasets_for_design("Proj", "Des")
            mock_app.assert_not_called()
        assert "cached_ds" in names

    def test_load_datasets_for_design_merges_project_and_design_datasets(self) -> None:
        service = _make_service()
        service.desktop = MagicMock()
        service.current_session_pid = 1
        service._cache_by_session[1] = ResultDataService._empty_session_cache()

        proj_ds = SimpleNamespace(x=[1.0], y=[2.0], z=[])
        des_ds = SimpleNamespace(x=[3.0], y=[4.0], z=[])
        aedtapp = MagicMock()
        aedtapp.project_datasets = {"proj_dataset": proj_ds}
        aedtapp.design_datasets = {"des_dataset": des_ds}
        with patch.object(service, "_get_aedtapp", return_value=aedtapp):
            names, _ = service.load_datasets_for_design("Proj", "Des")
        assert "proj_dataset" in names
        assert "des_dataset" in names

    # ---- get_dataset_xy ----------------------------------------------------

    def test_get_dataset_xy_returns_float_arrays(self) -> None:
        service = _make_service()
        service.desktop = MagicMock()
        service.current_session_pid = 1
        service._cache_by_session[1] = ResultDataService._empty_session_cache()
        ds = SimpleNamespace(x=[1.0, 2.0, 3.0], y=[4.0, 5.0, 6.0])
        service.solution_info.setdefault("Proj", {})["Des"] = {"datasets": {"myds": ds}}

        data = service.get_dataset_xy("Proj", "Des", "myds")
        np.testing.assert_array_equal(data["x"], [1.0, 2.0, 3.0])
        np.testing.assert_array_equal(data["y"], [4.0, 5.0, 6.0])
        assert data["x"].dtype == float
        assert data["y"].dtype == float

    def test_get_dataset_xy_returns_ndarray_from_list_input(self) -> None:
        service = _make_service()
        service.desktop = MagicMock()
        service.current_session_pid = 1
        service._cache_by_session[1] = ResultDataService._empty_session_cache()
        ds = SimpleNamespace(x=[0.0, 1.0], y=[2.0, 3.0])
        service.solution_info.setdefault("Proj", {})["Des"] = {"datasets": {"ds": ds}}

        data = service.get_dataset_xy("Proj", "Des", "ds")
        assert isinstance(data["x"], np.ndarray)
        assert isinstance(data["y"], np.ndarray)

    # ---- create_dataset ----------------------------------------------------

    def test_create_dataset_not_connected_raises(self) -> None:
        service = _make_service()
        with pytest.raises(AEDTRuntimeError, match="No AEDT session selected"):
            service.create_dataset("Proj", "Des", "NewDS", [1.0], [2.0])

    def test_create_dataset_delegates_to_aedtapp(self) -> None:
        service = _make_service()
        service.current_session_pid = 1
        service._cache_by_session[1] = ResultDataService._empty_session_cache()
        service.desktop = MagicMock()

        aedtapp = MagicMock()
        aedtapp.create_dataset.return_value = MagicMock()
        with patch.object(service, "_get_aedtapp", return_value=aedtapp):
            service.create_dataset("Proj", "Des", "NewDS", [1.0, 2.0], [3.0, 4.0], is_project_dataset=True)

        aedtapp.create_dataset.assert_called_once_with("NewDS", x=[1.0, 2.0], y=[3.0, 4.0], is_project_dataset=True)

    def test_create_dataset_design_scope(self) -> None:
        service = _make_service()
        service.current_session_pid = 1
        service._cache_by_session[1] = ResultDataService._empty_session_cache()
        service.desktop = MagicMock()

        aedtapp = MagicMock()
        with patch.object(service, "_get_aedtapp", return_value=aedtapp):
            service.create_dataset("Proj", "Des", "DDS", [0.0], [1.0], is_project_dataset=False)

        aedtapp.create_dataset.assert_called_once_with("DDS", x=[0.0], y=[1.0], is_project_dataset=False)

    # ---- _discover_aedt_sessions -------------------------------------------

    def test_discover_aedt_sessions_empty_when_no_sessions(self) -> None:
        service = _make_service(active_sessions_return={})
        assert service.active_sessions == []

    def test_discover_aedt_sessions_populates_from_active_sessions(self) -> None:
        sessions_map = {1234: 50051}
        with (
            patch(f"{_MODULE}.active_sessions", return_value=sessions_map),
            patch(f"{_MODULE}._check_psutil_connections", return_value={}),
        ):
            service = ResultDataService()
        assert len(service.active_sessions) == 1
        assert service.active_sessions[0]["pid"] == 1234
        assert service.active_sessions[0]["port"] == 50051

    def test_discover_aedt_sessions_com_port_on_windows(self) -> None:
        sessions_map = {5678: -1}
        with (
            patch(f"{_MODULE}.active_sessions", return_value=sessions_map),
            patch(f"{_MODULE}._check_psutil_connections", return_value={}),
            patch(f"{_MODULE}.is_linux", False),
        ):
            service = ResultDataService()
        assert any(s["pid"] == 5678 for s in service.active_sessions)
        assert service.active_sessions[0]["port"] == "n/a (com)"

    def test_discover_aedt_sessions_enriches_from_cmdline(self) -> None:
        sessions_map = {9999: 50060}
        cmdline = r"C:\ANSYS\v261\Win64\ansysedt.exe -ng"
        connections = {9999: [{"cmdline": cmdline}]}
        with (
            patch(f"{_MODULE}.active_sessions", return_value=sessions_map),
            patch(f"{_MODULE}._check_psutil_connections", return_value=connections),
        ):
            service = ResultDataService()
        sess = service.active_sessions[0]
        assert "2026" in str(sess["version"])
        assert sess["non_graphical"] is True

    def test_discover_aedt_sessions_sorted_by_pid(self) -> None:
        sessions_map = {300: 50053, 100: 50051, 200: 50052}
        with (
            patch(f"{_MODULE}.active_sessions", return_value=sessions_map),
            patch(f"{_MODULE}._check_psutil_connections", return_value={}),
        ):
            service = ResultDataService()
        pids = [s["pid"] for s in service.active_sessions]
        assert pids == sorted(pids)

    # ---- refresh_sessions --------------------------------------------------

    def test_refresh_sessions_re_discovers_sessions(self) -> None:
        service = _make_service()
        new_map = {1111: 50061}
        with (
            patch(f"{_MODULE}.active_sessions", return_value=new_map),
            patch(f"{_MODULE}._check_psutil_connections", return_value={}),
        ):
            sessions = service.refresh_sessions()
        assert len(sessions) == 1
        assert sessions[0]["pid"] == 1111

    def test_refresh_sessions_updates_active_sessions_attribute(self) -> None:
        service = _make_service()
        assert service.active_sessions == []
        new_map = {2222: 50062}
        with (
            patch(f"{_MODULE}.active_sessions", return_value=new_map),
            patch(f"{_MODULE}._check_psutil_connections", return_value={}),
        ):
            service.refresh_sessions()
        assert any(s["pid"] == 2222 for s in service.active_sessions)


# ===========================================================================
# ResultCalculatorExtension static/pure helpers (no Tk needed)
# ===========================================================================


class TestResultCalculatorExtensionHelpers:
    """Tests for static helpers that can be called without instantiating the extension."""

    def test_trace_info_label_generated_report(self) -> None:
        payload = {"source": "generated_report", "metadata": {"expression": "S11"}}
        label = ResultCalculatorExtension._trace_info_label(payload)
        assert label == "S11"

    def test_trace_info_label_existing_report(self) -> None:
        payload = {"source": "existing_report", "metadata": {"report": "SParams"}}
        label = ResultCalculatorExtension._trace_info_label(payload)
        assert label == "SParams"

    def test_trace_info_label_manual_dataset_short(self) -> None:
        payload = {"source": "manual_dataset", "metadata": {"description": "My short desc"}}
        label = ResultCalculatorExtension._trace_info_label(payload)
        assert label == "My short desc"

    def test_trace_info_label_manual_dataset_long_truncated(self) -> None:
        long_desc = "A" * 50
        payload = {"source": "manual_dataset", "metadata": {"description": long_desc}}
        label = ResultCalculatorExtension._trace_info_label(payload)
        # Truncated to 37 chars + ellipsis marker.
        assert len(label) <= 42

    def test_trace_info_label_aedt_dataset_short(self) -> None:
        payload = {"source": "aedt_dataset", "metadata": {"description": "Short"}}
        label = ResultCalculatorExtension._trace_info_label(payload)
        assert label == "Short"

    def test_trace_info_label_formula_short(self) -> None:
        payload = {"source": "formula", "metadata": {"expression": "r1 + r2"}}
        label = ResultCalculatorExtension._trace_info_label(payload)
        assert label == "r1 + r2"

    def test_trace_info_label_formula_long_truncated(self) -> None:
        long_expr = "r1 + " * 20
        payload = {"source": "formula", "metadata": {"expression": long_expr}}
        label = ResultCalculatorExtension._trace_info_label(payload)
        assert len(label) <= 42

    def test_trace_info_label_file_import_short(self) -> None:
        payload = {"source": "file_import", "metadata": {"expression": "my_file.csv"}}
        label = ResultCalculatorExtension._trace_info_label(payload)
        assert label == "my_file.csv"

    def test_trace_info_label_file_import_long_truncated(self) -> None:
        long_expr = "x" * 70
        payload = {"source": "file_import", "metadata": {"expression": long_expr}}
        label = ResultCalculatorExtension._trace_info_label(payload)
        assert len(label) <= 63  # 57 chars + "..."

    def test_trace_info_label_unknown_source(self) -> None:
        payload = {"source": "unknown_source", "metadata": {}}
        label = ResultCalculatorExtension._trace_info_label(payload)
        assert label == ""

    def test_trace_info_label_no_metadata(self) -> None:
        payload = {"source": "generated_report", "metadata": None}
        label = ResultCalculatorExtension._trace_info_label(payload)
        assert label == ""

    def test_trace_info_label_missing_expression_key(self) -> None:
        payload = {"source": "generated_report", "metadata": {}}
        label = ResultCalculatorExtension._trace_info_label(payload)
        assert label == ""

    def test_trace_info_label_existing_report_missing_report_key(self) -> None:
        payload = {"source": "existing_report", "metadata": {}}
        label = ResultCalculatorExtension._trace_info_label(payload)
        assert label == ""
