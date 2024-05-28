# Copyright (C) 2023 - 2024 ANSYS, Inc. and/or its affiliates.
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

"""Miscellaneous Methods for PyAEDT workflows."""

import os

from pyaedt.misc import current_version


def get_process_id():
    """Get process ID from environment variable."""
    aedt_process_id = None
    if os.getenv("PYAEDT_SCRIPT_PROCESS_ID", None):
        aedt_process_id = int(os.getenv("PYAEDT_SCRIPT_PROCESS_ID"))
    return aedt_process_id


def get_port():
    """Get GRPC port from environment variable."""
    port = 0
    if "PYAEDT_SCRIPT_PORT" in os.environ:
        port = int(os.environ["PYAEDT_SCRIPT_PORT"])
    return port


def get_aedt_version():
    """Get AEDT release from environment variable."""
    version = current_version()
    if "PYAEDT_SCRIPT_VERSION" in os.environ:
        version = os.environ["PYAEDT_SCRIPT_VERSION"]
    return version


def is_student():
    """Get if AEDT student is opened from environment variable."""
    student_version = False
    if "PYAEDT_STUDENT_VERSION" in os.environ:
        student_version = False if os.environ["PYAEDT_STUDENT_VERSION"] == "False" else True
    return student_version
