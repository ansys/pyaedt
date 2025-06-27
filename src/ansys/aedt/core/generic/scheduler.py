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
import re

JOB_TEMPLATE = 'Job_Settings_Template.txt'

job_defaults = \
    {
    "monitor": True,
    "wait_for_license": True,
    "use_ppe": False,
    "ng_solve": False,
    "product_full_path": None,
    "num_tasks": 0,
    "cores_per_task": 1,
    "max_tasks_per_node": 0,
    "ram_limit": 90,
    "num_gpu": 0,
    "num_nodes": 1,
    "num_cores": 32,
    "job_name": "AEDT Job",
    "custom_options": "",  # String with custom job options
    }


class JobSettings(dict):
    def __init__(self):
        super().__init__()
        self._template_path = Path(__file__).resolve().parent.parent / 'misc' / JOB_TEMPLATE
        self.template_text = self._load_template()
        self.update(job_defaults)
        self.data = self._render_template()

        output_lines = []
        with template_path.open('r', encoding='utf-8') as f:
            for line in f:
                # Update default values in Job_Settings
                def replacer(match):
                    key = match.group(1)
                    return str(replacements.get(key, match.group(0)))  # Default to original if not found

                new_line = pattern.sub(replacer, line)
                output_lines.append(new_line)

        self.data = ''.join(output_lines)

    def _load_template(self) -> str:
        with self._template_path.open('r', encoding='utf-8') as f:
            return f.read()

    def _render_template(self) -> str:
        pattern = re.compile(r"\{\{(\w+)\}\}")

        def replacer(match):
            key = match.group(1)
            return str(self.get(key, match.group(0)))  # Keep {{key}} if not found

        return pattern.sub(replacer, self.template_text)

    def __setitem__(self, key, value):
        super().__setitem__(key, value)
        self.data = self._render_template()

    def save_to_file(self, filename: str = "Job_Settings.areg"):
        path = Path(filename)
        if not path.suffix:
            path = path.with_suffix(".areg")
        with path.open("w", encoding="utf-8") as f:
            f.write(self.data)
