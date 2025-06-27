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


from pathlib import Path
from ansys.aedt.core.generic.settings import settings
import re


class JobSettings(dict):

    _JOB_TEMPLATE = Path(__file__).resolve().parent.parent / 'misc' / 'Job_Settings_Template.txt'

    _job_defaults = \
        {
            "monitor": True,
            "wait_for_license": True,
            "use_ppe": False,
            "ng_solve": False,
            "product_full_path": None,
            "num_tasks": 0,
            "cores_per_task": 0,
            "max_tasks_per_node": 0,
            "ram_limit": 90,
            "num_gpu": 0,
            "num_nodes": 1,
            "num_cores": 32,
            "job_name": "AEDT Simulation",
            "ram_per_core": 2.0,  # RAM per core in GB
            "exclusive": False,  # Reserve the entire node.
            "custom_submission_string": "",  # Allow custom submission string.
        }

    _job_defaults_read_only = \
        {
            "use_custom_submission_string": False,
            "fix_job_name": False,
        }

    def __init__(self):
        super().__init__()
        self._template_path = self._JOB_TEMPLATE
        self.template_text = self._load_template()
        self.update(self._job_defaults)
        self.update(self._job_defaults_read_only)
        self.data = self._render_template()

    def _load_template(self) -> str:
        with self._template_path.open('r', encoding='utf-8') as f:
            return f.read()

    def _render_template(self) -> str:
        pattern = re.compile(r"\{\{(\w+)\}\}")

        def replacer(match):
            key = match.group(1)
            value = self.get(key, match.group(0))
            if isinstance(value, bool):  # Boolean need to be lower case.
                return str(value).lower()
            elif value is None:  # Return an empty string if None
                return ''
            return str(value)  # Keep {{key}} if not found

        return pattern.sub(replacer, self.template_text)

    def __setitem__(self, key, value):
        if key in self._job_defaults_read_only.keys():
            settings.logger.warning(f"Key {key} is read-only and will not be changed.")
            return
        super().__setitem__(key, value)
        self.data = self._render_template()

    def __getitem__(self, key):
        if key == "use_custom_submission_string":  # True if the string has been changed.
            return bool(self.get("custom_submission_string", ""))
        elif key == "fix_job_name":
            return default_keys["job_name"] == self["job_name"]
        return super().__getitem__(key)

    def save(self, filename: str = "Job_Settings.areg"):
        path = Path(filename)
        if not path.suffix:
            path = path.with_suffix(".areg")
        with path.open("w", encoding="utf-8") as f:
            f.write(self.data)
