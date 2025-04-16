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

import tempfile

import ansys.aedt.core

from emit_core.emit_constants import EmiCategoryFilter

AEDT_VERSION = "2025.1"
NG_MODE = False

temp_folder = tempfile.TemporaryDirectory(suffix=".ansys")

project_name = ansys.aedt.core.generate_unique_project_name(root_name=temp_folder.name, project_name="antenna_cosite")
d = ansys.aedt.core.launch_desktop(AEDT_VERSION, NG_MODE, new_desktop=True)

emit = ansys.aedt.core.Emit(project_name, version=AEDT_VERSION)

# add a couple quick radios
radio = emit.modeler.components.create_component("New Radio")
radio = emit.modeler.components.create_component("New Radio")

rev = emit.results.analyze()
cats = rev.get_emi_category_filter_enabled(EmiCategoryFilter.IN_CHANNEL_TX_INTERMOD)
# n1limit = rev.n_to_1_limit
# receivers = rev.get_receiver_names()
pass

emit.save_project()
emit.release_desktop()
