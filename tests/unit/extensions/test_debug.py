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


def test_export_template():
    import tkinter as tk
    from tkinter import ttk

    root = tk.Tk()
    root.title("RadioButton Example")

    # Tkinter variable for selection (0 = Active, 1 = Specify)
    var_active_design = tk.IntVar(master=root, value=0, name="var1")  # default to Active Design

    row = 0
    # First radio button
    ttk.Radiobutton(
        root,
        text="Active Design",
        value=0,
        variable=var_active_design,
        style="PyAEDT.TRadiobutton",
        name="active_design",
    ).grid(row=row, column=0, padx=5, pady=5, sticky="w")

    row += 1
    # Second radio button
    b1 = ttk.Radiobutton(
        root,
        text="Specify Design",
        value=1,
        variable=var_active_design,
        style="PyAEDT.TRadiobutton",
        name="specified_design",
    )
    b1.grid(row=row, column=0, padx=5, pady=5, sticky="w")
    assert var_active_design.get() == 0
    b1.invoke()
    assert root.getvar("var1") == 1
