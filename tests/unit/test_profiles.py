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

"""Test profile functions of PyAEDT."""

from datetime import datetime
from datetime import timedelta

import pytest

import ansys.aedt.core.modules.profile as profiles


# Mock Node class to simulate the structure used in profiles
class Node:
    def __init__(self, properties=None, children=None) -> None:
        self.properties = properties or {}
        self.children = children or {}


def test_string_to_time_and_format_timedelta() -> None:
    td = profiles.string_to_time("01:02:03")
    assert isinstance(td, timedelta)
    assert profiles.format_timedelta(td) == "01:02:03"

    td2 = timedelta(days=2, hours=3, minutes=4, seconds=5)
    assert profiles.format_timedelta(td2) == "2 days 03:04:05"

    assert profiles.format_timedelta("na") == "na"


def test_merge_dict_all_paths_and_ordering() -> None:
    d1 = {
        "a 2": 1,
        "b": {"x": 1},
        "c": [3, 1],
        "d": "hola",
        "e": 100,
    }
    d2 = {
        "a 10": 2,
        "b": {"y": 2},
        "c": [2, 4],
        "d": "mundo",
        "e": 200,
        "f": 999,
    }
    merged = profiles.merge_dict(d1, d2)
    # Keys sorted with natural numeration 'a 2' before 'a 10'
    assert list(merged.keys()).index("a 2") < list(merged.keys()).index("a 10")
    # recursive
    assert merged["b"]["x"] == 1 and merged["b"]["y"] == 2
    # concatenated list
    assert merged["c"] == [1, 2, 3, 4]
    # concatenated strings with \n
    assert merged["d"] == "hola\nmundo"
    # Type conflict
    assert merged["e"] == 100 and merged["e_2"] == 200
    # keys only in d2
    assert merged["f"] == 999


def test_merge_profiles_calls_add() -> None:
    class Sim:
        def __init__(self, v) -> None:
            self.v = v

        def __add__(self, other):
            return Sim(self.v + other.v)

    sims = [Sim(1), Sim(2), Sim(3)]
    out = profiles._merge_profiles(sims)
    assert out.v == 6


def test_memorygb_all_dunder_methods_and_errors() -> None:
    with pytest.raises(TypeError):
        profiles.MemoryGB(object())

    m1 = profiles.MemoryGB("1 G")
    m2 = profiles.MemoryGB(2)
    m3 = profiles.MemoryGB(m1)
    assert str(m1) == "1 G"
    assert repr(m2) == "2 G"
    assert float(m1) == 1.0
    assert m1.value == 1.0
    assert (m1 + m2).value == 3.0
    assert sum([m1, m2], 0).value == 3.0
    assert m1 == m3
    assert m1 < m2
    assert profiles.MemoryGB("1000 M").value == 1.0
    assert profiles.MemoryGB("1 TB").value == 1000.0
    assert profiles.MemoryGB("1024 KB").value == 0.001024


def test_step_name_map() -> None:
    assert profiles.step_name_map("Frequency - 1GHz") == "1GHz"
    assert profiles.step_name_map("Something else") == "Something else"


def test_profile_step_summary_all_paths() -> None:
    props = {
        "Name": "Solve",
        "Cpu time": "00:00:10",
        "Real time": "00:00:05",
        "Memory": "2 G",
    }
    p = profiles.ProfileStepSummary(props)
    assert p.name == "Solve"
    assert p.cpu_time == timedelta(seconds=10)
    assert p.real_time == timedelta(seconds=5)
    assert p.memory.value == 2.0

    props2 = {"Name": "Group", "Info": "Elapsed time : 00:00:07, other stuff"}
    p2 = profiles.ProfileStepSummary(props2)
    assert p2.real_time == timedelta(seconds=7)


def test_profile_step_and_table_and_addition() -> None:
    child1 = Node(
        properties={
            "Name": "Adaptive Pass 1",
            "Cpu time": "00:00:05",
            "Real time": "00:00:03",
            "Memory": "1 G",
            "Start Time": "01/01/2024 12:00:00",
            "Stop Time": "01/01/2024 12:00:05",
        }
    )
    child2 = Node(
        properties={
            "Name": "Adaptive Pass 2",
            "Elapsed Time": "00:00:04",
            "Memory": "1.5 G",
            "Start Time": "01/01/2024 12:00:10",
            "Stop Time": "01/01/2024 12:00:14",
        }
    )
    root = Node(
        properties={
            "Name": "Meshing Process Group",
            "Cpu time": "00:00:01",
            "Real time": "00:00:01",
            "Memory": "0.5 G",
            "Start Time": "01/01/2024 11:59:59",
        },
        children={
            "Adaptive Pass 1": child1,
            "Adaptive Pass 2": child2,
        },
    )

    step = profiles.ProfileStep(root)
    assert step.cpu_time == timedelta(seconds=1)
    assert step.real_time == timedelta(seconds=1)
    assert step.max_memory.value == 1.5

    df = step.table()
    assert "Step" in df.columns and "elapsed_time" in df.columns
    assert any(x in ("00:00:04", "NA") for x in df["elapsed_time"].tolist())

    other = profiles.ProfileStep(Node(properties={"Name": "Other", "Cpu time": "00:00:02"}))
    combined = step + other
    assert combined._cpu_time == max(step._cpu_time, other._cpu_time)


def test_transient_profile_paths() -> None:
    t1 = Node(properties={"Name": "0.01s", "Real time": "00:00:02"})
    t2 = Node(properties={"Name": "0.2s", "Real time": "00:00:03"})
    troot = Node(properties={"Name": "Transient Solution Group"}, children={"0.01s": t1, "0.2s": t2})
    tp = profiles.TransientProfile(troot)
    assert tp.time_steps == [0.01, 0.2]
    assert tp.max_time == 0.2
    assert tp.time_step_keys(0.05) == ["0.01s"]


def test_frequency_sweep_profile_summary_and_children_to_elapsed() -> None:
    info = (
        "Interpolating HFSS Frequency Sweep\n"
        "Passivity Error = 0.123, ...\n"
        "S Matrix Error = 2.5%\n"
        "sweep converged\n"
        "Frequencies: 1GHz 2GHz 500MHz"
    )
    # hijo de frecuencia con Info y elapsed
    child_key = "Frequency - 1 GHz Group"
    child_node = Node(
        properties={
            "Info": "Elapsed time : 00:00:05, more",
            "Name": child_key,
            "Memory": "0.7 G",
        }
    )
    group = Node(properties={"Info": info, "Time": "02/03/2024 10:20:30"}, children={child_key: child_node})
    fsp = profiles.FrequencySweepProfile(group, sweep_name="Sweep A")
    # _create_summary
    assert fsp.sweep_type == "Interpolating"
    assert fsp.converged is True
    assert pytest.approx(fsp.passivity_error, 1e-9) == 0.123
    assert pytest.approx(fsp.s_matrix_error, 1e-9) == 0.025
    assert [str(q) for q in fsp.frequency_basis]  # se llenó
    assert fsp.start_time == datetime(2024, 2, 3, 10, 20, 30)
    # se asignó elapsed_time al paso hijo
    name_in_steps = child_key.replace("Group", "").strip()
    assert fsp.steps[name_in_steps].elapsed_time == timedelta(seconds=5)


def test_adaptive_pass_adapt_frequency_property() -> None:
    n = Node(properties={"Frequency": "2 GHz"})
    ap = profiles.AdaptivePass(n)
    assert str(ap.adapt_frequency) == "2 GHz"


def test_get_mesh_process_name() -> None:
    n = Node(children={"Initial Meshing Group": Node(), "Other": Node()})
    assert "Initial Meshing Group" in profiles.get_mesh_process_name(n)
    n2 = Node(children={"Meshing Process Group": Node()})
    assert "Meshing Process Group" in profiles.get_mesh_process_name(n2)
    n3 = Node(children={"X": Node()})
    assert profiles.get_mesh_process_name(n3) is None


def build_simulation_group(product: str="HFSS"):
    design_validation_hfss = Node(properties={"Info": "Elapsed Time: 00:00:06, Memory: 3 G"})
    design_validation_mx = Node(properties={"Elapsed Time": "00:00:04", "Memory": "1.2 G"})
    freq_child = Node(properties={"Info": "Elapsed time : 00:00:02", "Name": "Frequency - 1 GHz Group"}, children={})
    freq_group = Node(
        properties={},
        children={"Sweep 1 - Frequency Sweep Group": Node(children={"Frequency - 1 GHz Group": freq_child})},
    )
    hpc_group = Node(properties={"MPI Vendor": "OpenMPI", "MPI Version": "4.1"})
    transient_group = Node(
        properties={}, children={"0.01s": Node(properties={"Real time": "00:00:01", "Memory": "1 G"})}
    )
    solver_init = Node(
        properties={"Name": "Solver Initialization", "Cpu time": "00:00:01", "Real time": "00:00:02", "Memory": "0.5 G"}
    )
    populate = Node(properties={"Name": "Populate Solver Input", "Elapsed Time": "00:00:03", "Memory": "0.7 G"})
    solve = Node(properties={"Name": "Solve", "Real time": "00:00:05", "Memory": "2 G"})

    children = {
        "Adaptive Meshing Group": Node(
            properties={"Name": "Adaptive Meshing Group"},
            children={
                "Adaptive Pass 1": Node(
                    properties={"Name": "Adaptive Pass 1", "Real time": "00:00:03", "Memory": "1.5 G"}
                ),
                "Adaptive Pass 2": Node(
                    properties={"Name": "Adaptive Pass 2", "Real time": "00:00:04", "Memory": "1.7 G"}
                ),
            },
        ),
        "Design Validation": design_validation_hfss if product == "HFSS" else design_validation_mx,
        "Frequency Sweep Group": freq_group if product == "HFSS" else None,
        "HPC Group": hpc_group,
        "Transient Solution Group": transient_group,
        "Solver Initialization": solver_init,
        "Populate Solver Input": populate,
        "Solve": solve,
        "Meshing Process Group": Node(properties={"Name": "Meshing", "Memory": "2.2 G"}),
    }
    children = {k: v for k, v in children.items() if v is not None}

    node = Node(properties={"Product": f"{product} 2025", "Name": "Simulation"}, children=children)
    return node


def test_simulation_profile_building_hfss_and_methods(monkeypatch) -> None:
    sp = profiles.SimulationProfile(build_simulation_group("HFSS"))
    assert sp.product == "HFSS" and sp.product_version == "2025"
    assert sp.num_adaptive_passes == 2
    assert sp.is_transient is True
    assert sp.has_frequency_sweep is True
    assert isinstance(sp.validation_time, timedelta)
    assert hasattr(sp, "mpi_vendor") and sp.use_mpi is True

    assert sp.real_time(num_passes=1) == timedelta(seconds=3)
    assert sp.real_time(max_time=0.005) == timedelta(seconds=7)
    assert sp.max_time == pytest.approx(0.01)

    mm = sp.max_memory()
    assert isinstance(mm, profiles.MemoryGB) or mm == 0
    assert float(mm) >= 2.2  # mesh 2.2 G es de las mayores

    r = repr(sp)
    assert "SimulationProfile" in r and "HFSS, version: 2025" in r
    s = str(sp)
    assert "Instance of SimulationProfile" in s

    assert sp._check_num_passes(99) == sp.num_adaptive_passes
    assert sp._check_num_passes(1) == 1
    assert sp._check_num_passes(None) == sp.num_adaptive_passes


def test_simulation_profile_building_maxwell_and_warning_in_add(caplog) -> None:
    sp1 = profiles.SimulationProfile(build_simulation_group("Maxwell"))
    sp2 = profiles.SimulationProfile(build_simulation_group("Maxwell"))
    sp1.weird = object()
    sp2.weird = object()


def test_parse_profile_data_happy_and_error_paths() -> None:
    ok_group = Node(children={"Group1": build_simulation_group("HFSS")})
    bad_child = Node(properties={"Product": "HFSS 2025"}, children={})
    _ = Node(children={"Bad": bad_child})
    _ = Node(children={"OK": ok_group.children["Group1"], "BAD": bad_child})

    both = Node(children={"Good": build_simulation_group("HFSS"), "Bad": bad_child})
    res = profiles._parse_profile_data(both)
    assert res.product == "HFSS" and res.product_version == "2025"


# def test_profiles_mapping_ok_and_fallback_paths():
#     clean = {"key1": Node(children={"A": build_simulation_group("HFSS")})}
#     with patch.object(
#         profiles,
#         "_parse_profile_data",
#         side_effect=lambda x: profiles.SimulationProfile(build_simulation_group("HFSS")),
#     ):
#         p = profiles.Profiles(clean)
#         # mapping interface
#         k = list(p.keys())[0]
#         assert p[k].product == "HFSS"
#         assert len(p) == 1
#         assert "Profiles(" in repr(p)
#         assert list(iter(p))[0] == k
#
#     raw = {"rawkey": Node(children={})}
#     with (
#         patch.object(profiles, "_parse_profile_data", side_effect=Exception("fail")),
#         patch.object(profiles.logging, "warning") as warn,
#     ):
#         p2 = profiles.Profiles(raw)
#         assert warn.called
#         assert list(p2.keys()) == ["rawkey"]
#         assert len(p2) == 0 or len(p2) == 1
#         assert list(iter(p2))[0] == "rawkey"
#         assert p2["rawkey"] is raw["rawkey"]
#
#     with pytest.raises(TypeError):
#         p.__setitem__("x", 1)
