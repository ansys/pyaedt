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

from ansys.aedt.core.emit_core.nodes.emit_node import EmitNode
from ansys.aedt.core.internal.checks import min_aedt_version


class BandFolder(EmitNode):
    """Provide band folder."""

    def __init__(self, emit_obj, result_id, node_id) -> None:
        EmitNode.__init__(self, emit_obj, result_id, node_id)
        self._is_component = False

    @property
    @min_aedt_version("2025.2")
    def parent(self) -> EmitNode:
        """The parent of this emit node.

        Examples
        --------
        >>> from ansys.aedt.core import Emit
        >>> app = Emit()
        >>> radio = app.schematic.create_component("New Radio", name="Radio1")
        >>> folder = radio.add_folder()
        >>> folder.parent
        """
        return self._parent

    @property
    @min_aedt_version("2025.2")
    def node_type(self) -> str:
        """The type of this emit node.

        Examples
        --------
        >>> from ansys.aedt.core import Emit
        >>> app = Emit()
        >>> radio = app.schematic.create_component("New Radio", name="Radio1")
        >>> folder = radio.add_folder()
        >>> folder.node_type
        """
        return self._node_type

    @min_aedt_version("2025.2")
    def add_band(self) -> EmitNode:
        """Create a New Band

        Examples
        --------
        >>> from ansys.aedt.core import Emit
        >>> app = Emit()
        >>> radio = app.schematic.create_component("New Radio", name="Radio1")
        >>> folder = radio.add_folder()
        >>> band = folder.add_band()
        """
        return self._add_child_node("Band")

    @min_aedt_version("2025.2")
    def duplicate(self, new_name: str = "") -> EmitNode:
        """Duplicate this node

        Examples
        --------
        >>> from ansys.aedt.core import Emit
        >>> app = Emit()
        >>> radio = app.schematic.create_component("New Radio", name="Radio1")
        >>> folder = radio.add_folder()
        >>> folder_copy = folder.duplicate("BandFolder1")
        """
        return self._duplicate(new_name)

    @min_aedt_version("2025.2")
    def delete(self) -> None:
        """Delete this node

        Examples
        --------
        >>> from ansys.aedt.core import Emit
        >>> app = Emit()
        >>> radio = app.schematic.create_component("New Radio", name="Radio1")
        >>> folder = radio.add_folder()
        >>> folder.delete()
        """
        self._delete()
