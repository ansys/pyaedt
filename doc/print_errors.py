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

"""Read errors output from a sphinx build and remove duplicate groups"""

import os
import pathlib
import sys

sys.tracebacklimit = 0
my_path = pathlib.Path(__file__).parent.resolve()

errors = set()
error_file = os.path.join(my_path, "build_errors.txt")
if os.path.isfile(error_file):
    with open(error_file) as fid:
        group = []
        for line in fid.readlines():
            line = line.strip()
            if line:
                group.append(line)
            else:
                errors.add("\n".join(group))
                group = []

    for error in list(errors):
        print(error)
        print()

    # There should be no errors here since sphinx will have exited
    print()
    if errors:
        raise Exception(f"Sphinx reported unique {len(errors)} warnings\n\n")

print("Sphinx Reported no warnings\n\n")
