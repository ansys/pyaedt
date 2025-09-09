# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 - 2025 ANSYS, Inc. and/or its affiliates.
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

from datetime import timedelta

import ansys.aedt.core.modules.profile as profiles


def test_string_to_time_and_format_timedelta():
    td = profiles.string_to_time("01:02:03")
    assert isinstance(td, timedelta)
    assert profiles.format_timedelta(td) == "01:02:03"

    td2 = timedelta(days=2, hours=3, minutes=4, seconds=5)
    assert profiles.format_timedelta(td2) == "2 days 03:04:05"

    assert profiles.format_timedelta("na") == "na"


def test_merge_dict_all_paths_and_ordering():
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


def test_merge_profiles_calls_add():
    class Sim:
        def __init__(self, v):
            self.v = v

        def __add__(self, other):
            return Sim(self.v + other.v)

    sims = [Sim(1), Sim(2), Sim(3)]
    out = profiles._merge_profiles(sims)
    assert out.v == 6
