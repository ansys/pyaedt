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

import webbrowser

import tkinter as tk

INTRO_LINK = "https://aedt.docs.pyansys.com/version/dev/User_guide/pyaedt_extensions_doc/project/configure_layout.html"
GUIDE_LINK = "https://examples.aedt.docs.pyansys.com/version/dev/examples/00_edb/use_configuration/index.html"


def create_help_manu(menu_bar, master):
    # === File Menu ===
    help_menu = tk.Menu(menu_bar, tearoff=0)
    help_menu.add_command(
        label="Introduction",
        command=lambda: webbrowser.open(INTRO_LINK),
    )
    help_menu.add_command(
        label="User Guide",
        command=lambda: webbrowser.open(GUIDE_LINK),
    )

    # Add File menu to menubar
    menu_bar.add_cascade(label="Help", menu=help_menu)