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

from pydantic import BaseModel


class AedtInfo(BaseModel):
    """Provide AEDT info."""

    version: str = ""
    """Value for version."""
    port: int
    """Value for port."""
    aedt_process_id: int | None
    """Value for AEDT process id."""
    student_version: bool | None = False
    """Value for student version."""


class ExportOptions(BaseModel):
    """Provide export options."""

    general: bool = False
    """Value for general."""
    variables: bool = True
    """Value for variables."""
    stackup: bool = True
    """Value for stackup."""
    package_definitions: bool = False
    """Value for package definitions."""
    setups: bool = True
    """Value for setups."""
    sources: bool = True
    """Value for sources."""
    ports: bool = True
    """Value for ports."""
    nets: bool = False
    """Value for nets."""
    pin_groups: bool = True
    """Value for pin groups."""
    operations: bool = True
    """Value for operations."""
    components: bool = False
    """Value for components."""
    boundaries: bool = False
    """Value for boundaries."""
    s_parameters: bool = False
    """Value for s parameters."""
    padstacks: bool = False
    """Value for padstacks."""
    terminals: bool = False
    """Value for terminals."""
