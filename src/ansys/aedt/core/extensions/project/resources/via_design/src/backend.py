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

import json
from pathlib import Path
import tempfile

from pyedb import Edb
from pyedb.extensions.via_design_backend import Board


class ViaDesignBackend:
    _OUTPUT_DIR = None

    @property
    def output_dir(self):
        if self._OUTPUT_DIR is None:
            output_dir = self.cfg["general"]["output_dir"]
            if output_dir == "":
                self._OUTPUT_DIR = Path(tempfile.TemporaryDirectory(suffix=".ansys").name)
            else:
                self._OUTPUT_DIR = Path(output_dir)
        return self._OUTPUT_DIR

    def __init__(self, cfg):
        cfg_json = {
            "stackup": {"layers": [], "materials": []},
            "variables": [],
            "ports": [],
            "modeler": {"traces": [], "planes": [], "padstack_definitions": [], "padstack_instances": []},
        }

        self.cfg = cfg
        self.version = self.cfg["general"]["version"]
        outline_extent = self.cfg["placement"]["outline_extent"]
        pitch = self.cfg["placement"]["pitch"]

        board = Board(
            stackup=self.cfg["stackup"] if isinstance(self.cfg["stackup"], list) else self.cfg["stackup"]["layers"],
            padstack_defs=self.cfg["padstack_defs"],
            outline_extent=outline_extent,
            pitch=pitch,
            pin_map=self.cfg["placement"]["pin_map"],
            signals=self.cfg["signals"],
            differential_signals=self.cfg["differential_signals"],
        )
        board.populate_config(cfg_json)

        self.cfg_json = cfg_json

    def create_edb(self):
        self.output_dir.mkdir(parents=True, exist_ok=True)
        with open(self.output_dir / "config.json", "w") as f:
            json.dump(self.cfg_json, f, indent=4)
        app = Edb(edbpath=str((Path(self.output_dir) / self.cfg["title"]).with_suffix(".aedb")), version=self.version)
        app.configuration.load(self.cfg_json, apply_file=True)
        app.save()
        app.close()
        return app.edbpath
