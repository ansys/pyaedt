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

from __future__ import annotations

import os
from pathlib import Path
import sys

import pytest


@pytest.fixture(autouse=True, scope="session")
def pin_tcl_library():
    """Ensure TCL_LIBRARY is explicitly set for the entire test session.

    Extension tests create and destroy tkinter.Tk() instances repeatedly.
    After the Tcl interpreter is torn down, Tcl's auto-detection of its own
    library path can fail and produce `_tkinter.TclError` with the following
    message: Can't find a usable init.tcl in the following directories

    Pinning TCL_LIBRARY (and TK_LIBRARY) in os.environ before the first
    Tk() is created ensures that every subsequent Tcl re-initialization
    can still find init.tcl, regardless of test ordering.
    """
    if "TCL_LIBRARY" in os.environ:
        return

    # Strategy 1: use tkinter.Tcl() to ask Tcl itself. Since it might fail,
    # we wrap it in a try/except to avoid masking other errors.
    try:
        import tkinter

        tcl = tkinter.Tcl()
        tcl_lib = tcl.eval("info library")
        if tcl_lib:
            os.environ["TCL_LIBRARY"] = tcl_lib
            # Derive TK_LIBRARY from the sibling tk* directory.
            tcl_parent = Path(tcl_lib).parent
            for candidate in tcl_parent.glob("tk*"):
                if (candidate / "tk.tcl").exists():
                    os.environ.setdefault("TK_LIBRARY", str(candidate))
                    return
    except Exception:
        pass

    # Strategy 2: probe the Python prefix for a bundled tcl/tk tree.
    for prefix in (sys.prefix, sys.base_prefix):
        for subdir in ("tcl", "lib", os.path.join("lib", "tcl")):
            root = Path(prefix) / subdir
            if not root.is_dir():
                continue
            for candidate in sorted(root.glob("tcl*"), reverse=True):
                if (candidate / "init.tcl").exists():
                    os.environ["TCL_LIBRARY"] = str(candidate)
                    # Look for a sibling tk directory.
                    for tk_candidate in sorted(root.glob("tk*"), reverse=True):
                        if (tk_candidate / "tk.tcl").exists():
                            os.environ.setdefault("TK_LIBRARY", str(tk_candidate))
                            return
