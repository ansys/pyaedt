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

import json
from pathlib import Path

from ansys.aedt.core import Hfss


def test_import_from_open_street_map(add_app, test_tmp_dir):
    """Test OSM import with HFSS using mocked data."""
    hfss = add_app(application=Hfss, solution_type="SBR+")

    result = hfss.modeler.import_from_openstreet_map(
        latitude_longitude=[40.273726, -80.168269],
        env_name="test_hfss_environment",
        terrain_radius=50,
        road_step=3,
        plot_before_importing=False,
        import_in_aedt=True,
    )

    # Verify the result structure
    assert result is not None
    assert result["name"] == "test_hfss_environment"
    assert result["type"] == "environment"
    assert "parts" in result
    assert "terrain" in result["parts"]
    assert "buildings" in result["parts"]
    assert "roads" in result["parts"]

    # Verify objects were imported to HFSS
    assert len(hfss.modeler.object_names) > 0

    # Verify JSON file was created
    json_file = Path(hfss.working_directory) / "test_hfss_environment.json"
    assert json_file.exists()

    # Verify JSON content
    with open(json_file, "r", encoding="utf-8") as f:
        json_data = json.load(f)
        assert json_data["name"] == "test_hfss_environment"
        assert json_data["radius"] == 50

    # Verify model units are set to meters
    assert hfss.modeler.model_units == "meter"

    hfss.close_project(save=False)
