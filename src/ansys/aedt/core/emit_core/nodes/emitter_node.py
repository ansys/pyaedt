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

from typing import cast

from ansys.aedt.core.emit_core.nodes.emit_node import EmitNode
from ansys.aedt.core.emit_core.nodes.generated import AntennaNode
from ansys.aedt.core.emit_core.nodes.generated import BandFolder
from ansys.aedt.core.emit_core.nodes.generated import RadioNode
from ansys.aedt.core.emit_core.nodes.generated import Waveform


class EmitterNode(EmitNode):
    """
    Provides the EmitterNode object.

    Parameters
    ----------
    emit_obj : emit_obj object
        EMIT design object representing the project.
    result_id : int
        Unique ID associated with the Revision. For the Current Revision
        the ID = 0
    node_id : int
        Unique ID associated with the node.

    >>> aedtapp.results = Results()
    >>> revision = aedtapp.results.analyze()
    >>> receivers = revision.get_receiver_names()
    """

    def __init__(self, emit_obj, result_id, node_id):
        self._is_component = True
        EmitNode.__init__(self, emit_obj, result_id, node_id)
        self._radio_node = RadioNode(emit_obj, result_id, node_id)

        # create_component code provides the radio_id, but we also
        # need to get the antenna ID. We can get this by traversing
        # the SceneNode children and finding the antenna with the
        # same name as the Radio
        scene_node_id = self._oRevisionData.GetTopLevelNodeID(result_id, "Scene")
        antennas = self._oRevisionData.GetChildNodeNames(result_id, scene_node_id, "AntennaNode", True)
        for ant in antennas:
            if ant == self._radio_node.name:
                ant_id = self._oRevisionData.GetChildNodeID(result_id, scene_node_id, ant)
                self._antenna_node = AntennaNode(emit_obj, result_id, ant_id)

    def node_type(self) -> str:
        """The type of this emit node"""
        return "EmitterNode"

    def duplicate(self, new_name: str):
        """Duplicate this node"""
        return self._duplicate(new_name)

    def delete(self):
        """Delete this node"""
        self._delete()

    def get_radio(self) -> RadioNode:
        """Get the radio associated with this Emitter.

        Returns
        -------
        radio_node: RadioNode
            Node representing the radio of this Emitter

        Examples
        --------
        >>> node = emitter.get_radio()
        """
        return self._radio_node

    def get_antenna(self) -> AntennaNode:
        """Get the antenna associated with this Emitter.

        Returns
        -------
        antenna_node: AntennaNode
            Node representing the antenna of this Emitter

        Examples
        --------
        >>> node = emitter.get_antenna()
        """
        return self._antenna_node

    def children(self):
        """Overridden to return the Waveforms

        Returns
        -------
        waveforms: list[Waveform]
            list of waveform nodes defined for the Emitter.

        Examples
        --------
        >>> waveforms = emitter.get_waveforms()
        """
        return self.get_waveforms()

    def get_waveforms(self) -> list[Waveform]:
        """Get the waveform nodes for the Emitter.

        Returns
        -------
        waveforms: list[Waveform]
            list of waveform nodes defined for the Emitter.

        Examples
        --------
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
