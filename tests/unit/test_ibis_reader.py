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

import pytest

from ansys.aedt.core.generic.ibis_reader import ibis_parsing


@pytest.fixture(scope="module", autouse=True)
def desktop() -> None:
    """Override the desktop fixture to DO NOT open the Desktop when running this test class"""
    return


MINIMAL_IBIS = """\
IBIS Ver : 7.0
File Name : c_comp_model.ibs
Component : Driver

[Model]
Comp Pin : PIN_1
Pin Model : typ
[Model Spec]
| dummy
[End Model Spec]

[C Comp Model]
C_comp_model_mode All
File_TS ./dummy_typ.s2p ./dummy_fast.s2p
Number_of_terminals = 1
1 Buffer_I/O
[End C Comp Model]

[C Comp Corner]
C_comp_pullup 0.1982pF 0.1860pF 0.2132pF
[End C Comp Corner]

[End Component]
"""


def test_ibis_parsing_c_comp_model(tmp_path):
    """``[C Comp Model]`` is a valid IBIS 7.1+ child of ``[Model]`` and must not abort parsing."""
    ibs = tmp_path / "c_comp_model.ibs"
    ibs.write_text(MINIMAL_IBIS, encoding="utf-8")

    parsed = ibis_parsing(str(ibs))

    assert parsed is not False
    models = [k for k, v in parsed.items() if isinstance(v, dict) and "model" in v]
    assert models, "no [Model] section was parsed"
    c_comp_model = parsed[models[0]]["c comp model"]
    assert "C_comp_model_mode All" in c_comp_model["c comp model"]
    # a sibling keyword of [C Comp Model] must still be collected under the same model
    assert "c comp corner" in parsed[models[0]]
