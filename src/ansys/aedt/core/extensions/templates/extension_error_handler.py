# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 - 2026 ANSYS, Inc. and/or its affiliates.
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

"""
* * * This script is meant to run in CPython. * * *

Wrapper that executes an extension script and displays a dialog with the
error traceback when the script exits with a non-zero return code.

Usage::

    python extension_error_handler.py --script <script_path> [script_args ...]

"""

import os
import subprocess  # nosec
import sys


def main():
    if len(sys.argv) < 2:
        sys.exit(1)

    script = None
    script_args = []

    if len(sys.argv) < 3:
        sys.exit(1)
    script = sys.argv[2]
    script_args = sys.argv[3:]

    result = subprocess.run(
        [sys.executable, script] + script_args,
        env=os.environ.copy(),
        stderr=subprocess.PIPE,
        text=True,
    )  # nosec

    if result.returncode != 0:
        error_msg = result.stderr or "Process exited with code {}".format(result.returncode)
        _show_error(error_msg)
        sys.exit(result.returncode)


def _show_error(error_msg):
    """Show error in a dialog box and print to stderr."""
    sys.stderr.write(error_msg + "\n")
    try:
        import tkinter as tk
        from tkinter import messagebox

        root = tk.Tk()
        root.withdraw()
        if len(error_msg) > 3000:
            error_msg = "...\n" + error_msg[-3000:]
        messagebox.showerror("PyAEDT Extension Error", error_msg)
        root.destroy()
    except Exception:
        print("Failed to show error dialog. Error message:\n" + error_msg)


if __name__ == "__main__":
    main()
