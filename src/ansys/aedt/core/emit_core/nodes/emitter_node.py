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

from typing import cast

from ansys.aedt.core.emit_core.nodes.emit_node import EmitNode
from ansys.aedt.core.emit_core.nodes.generated import AntennaNode
from ansys.aedt.core.emit_core.nodes.generated import BandFolder
from ansys.aedt.core.emit_core.nodes.generated import RadioNode
from ansys.aedt.core.emit_core.nodes.generated import Waveform
from ansys.aedt.core.internal.checks import min_aedt_version


class EmitterNode(EmitNode):
    """Provides the EmitterNode object.

    Parameters
    ----------
    emit_obj : emit_obj object
        EMIT design object representing the project.
    result_id : int
        Unique ID associated with the Revision. For the Current Revision
        the ID = 0
    node_id : int
        Unique ID associated with the node.

    Examples
    --------
    >>> from ansys.aedt.core import Emit
    >>> app = Emit()
    >>> emitter, antenna = app.schematic.create_radio_antenna("Bluetooth")

    """

    def __init__(self, emit_obj, result_id, node_id) -> None:
        o_revision_data = emit_obj.odesign.GetModule("EmitCom")
        props = EmitNode.props_to_dict(o_revision_data.GetEmitNodeProperties(result_id, node_id, True))
        node_type = props.get("Type", "")

        radio_node_id = node_id
        antenna_node_id = None

        if node_type == "AntennaNode" and props.get("SubType") == "Emitter":
            antenna_node_id = node_id
            emitter_name = props.get("Name", "")
            if emitter_name:
                radio_node_id = o_revision_data.GetComponentNodeID(result_id, emitter_name)
        elif node_type == "RadioNode" and props.get("IsEmitter") == "true":
            radio_node_id = node_id

        EmitNode.__init__(self, emit_obj, result_id, radio_node_id)
        self._is_component = True
        self._radio_node = RadioNode(emit_obj, result_id, radio_node_id)

        if antenna_node_id is not None:
            self._antenna_node = AntennaNode(emit_obj, result_id, antenna_node_id)
        else:
            scene_node_id = o_revision_data.GetTopLevelNodeID(result_id, "Scene")
            antennas = o_revision_data.GetChildNodeNames(result_id, scene_node_id, "AntennaNode", True)
            for ant in antennas:
                if ant == self._radio_node.name:
                    ant_id = o_revision_data.GetChildNodeID(result_id, scene_node_id, ant, True)
                    self._antenna_node = AntennaNode(emit_obj, result_id, ant_id)
                    break

    @property
    @min_aedt_version("2025.2")
    def node_type(self) -> str:
        """The type of this emit node.

        Examples
        --------
        >>> from ansys.aedt.core import Emit
        >>> app = Emit()
        >>> emitter, antenna = app.schematic.create_radio_antenna("Bluetooth")
        >>> emitter.node_type

        """
        return "EmitterNode"

    @min_aedt_version("2025.2")
    def duplicate(self, new_name: str) -> EmitNode:
        """Duplicate this node.

        Examples
        --------
        >>> from ansys.aedt.core import Emit
        >>> app = Emit()
        >>> emitter, antenna = app.schematic.create_radio_antenna("Bluetooth")
        >>> emitter_copy = emitter.duplicate("Bluetooth_Copy")

        """
        return self._duplicate(new_name)

    @min_aedt_version("2025.2")
    def delete(self) -> None:
        """Delete this node.

        Examples
        --------
        >>> from ansys.aedt.core import Emit
        >>> app = Emit()
        >>> emitter, antenna = app.schematic.create_radio_antenna("Bluetooth")
        >>> emitter.delete()

        """
        self._delete()

    @min_aedt_version("2025.2")
    def get_radio(self) -> RadioNode:
        """Get the radio associated with this Emitter.

        Returns
        -------
        radio_node: RadioNode
            Node representing the radio of this Emitter

        Examples
        --------
        >>> from ansys.aedt.core import Emit
        >>> app = Emit()
        >>> emitter, antenna = app.schematic.create_radio_antenna("Bluetooth")
        >>> node = emitter.get_radio()

        """
        return self._radio_node

    @min_aedt_version("2025.2")
    def get_antenna(self) -> AntennaNode:
        """Get the antenna associated with this Emitter.

        Returns
        -------
        antenna_node: AntennaNode
            Node representing the antenna of this Emitter

        Examples
        --------
        >>> from ansys.aedt.core import Emit
        >>> app = Emit()
        >>> emitter, antenna = app.schematic.create_radio_antenna("Bluetooth")
        >>> node = emitter.get_antenna()

        """
        return self._antenna_node

    @property
    @min_aedt_version("2025.2")
    def children(self) -> list[EmitNode]:
        """Overridden to return the Waveforms.

        Returns
        -------
        waveforms: list[Waveform]
            list of waveform nodes defined for the Emitter.

        Examples
        --------
        >>> from ansys.aedt.core import Emit
        >>> app = Emit()
        >>> emitter, antenna = app.schematic.create_radio_antenna("Bluetooth")
        >>> waveforms = emitter.get_waveforms()

        """
        return self.get_waveforms()

    @min_aedt_version("2025.2")
    def get_waveforms(self) -> list[Waveform]:
        """Get the waveform nodes for the Emitter.

        Returns
        -------
        waveforms: list[Waveform]
            list of waveform nodes defined for the Emitter.

        Examples
        --------
        >>> from ansys.aedt.core import Emit
        >>> app = Emit()
        >>> emitter, antenna = app.schematic.create_radio_antenna("Bluetooth")
        >>> waveforms = emitter.get_waveforms()

        """
        radio = self.get_radio()
        radio_children = radio.children
        waveforms = []
        # check for folders and recurse them if needed
        for child in radio_children:
            if isinstance(child, BandFolder):
                grandchildren = child.children
                for grandchild in grandchildren:
                    # we don't allow nested folders, so can add these
                    # directly to the waveform list
                    waveforms.append(cast(Waveform, grandchild))
            elif isinstance(child, Waveform):
                waveforms.append(cast(Waveform, child))
        return waveforms
