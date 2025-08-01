# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 - 2025 ANSYS, Inc. and/or its affiliates.
# SPDX-License-Identifier: MIT
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


from pathlib import Path

from pydantic import BaseModel
from ansys.aedt.core.generic.file_utils import read_toml


class LayoutValidation(BaseModel):
    illegal_rlc_values: bool = False


class Operations(BaseModel):
    rlc_to_ports: list = []


class CfgConfigureLayout(BaseModel):
    operations: Operations = Operations()
    layout_validation: LayoutValidation = LayoutValidation()

    layout_file: str
    edb_config: dict = {}
    supplementary_json: str = ""

    @classmethod
    def from_file(cls, file_path: str):
        _file_path = Path(file_path)
        data = read_toml(_file_path)

        supplementary_json = data.get("supplementary_json", "")
        if supplementary_json != "":
            supplementary_json = str(_file_path.with_name(Path(supplementary_json).name))
        else:  # pragma: no cover
            supplementary_json = ""
        data["supplementary_json"] = supplementary_json

        layout_file = Path(data["layout_file"])
        if layout_file.suffix == ".aedt":  # pragma: no cover
            layout_file = layout_file.with_suffix(".aedb")
        if not bool(layout_file.drive):
            layout_file = _file_path.parent / layout_file
        data["layout_file"] = str(layout_file)
        return cls(**data)

    def get_edb_config_dict(self, edb):
        edb_config = dict(self.edb_config)

        # RLC
        cfg_components = []
        cfg_ports = []
        for i in self.rlc_to_ports:
            comp = edb.components[i]
            layer = comp.placement_layer
            p1, p2 = list(comp.pins.values())
            cfg_port = {
                "name": f"port_{comp.name}",
                "type": "circuit",
                "positive_terminal": {"coordinates": {"layer": layer, "point": p1.position, "net": p1.net_name}},
                "negative_terminal": {"coordinates": {"layer": layer, "point": p2.position, "net": p2.net_name}},
            }
            cfg_ports.append(cfg_port)

            cfg_comp = {
                "enabled": False,
                "reference_designator": comp.name,
            }
            cfg_components.append(cfg_comp)
        if "ports" in edb_config:
            edb_config["ports"].extend(cfg_ports)
        else:  # pragma: no cover
            edb_config["ports"] = cfg_ports

        if "components" in edb_config:
            edb_config["components"].extend(cfg_components)
        else:  # pragma: no cover
            edb_config["components"] = cfg_components

        return edb_config