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

from ansys.aedt.core.generic.constants import LineStyle
from ansys.aedt.core.generic.general_methods import pyaedt_function_handler
from ansys.aedt.core.modeler.cad.elements_3d import BinaryTreeNode


class LimitLine(BinaryTreeNode):
    """Line Limit Management Class."""

    def __init__(self, post, trace_name, oo=None):
        self._oo = oo
        self._app = post._app
        self._oreport_setup = post.oreportsetup
        self.line_name = trace_name
        self.LINESTYLE = LineStyle()
        self._initialize_tree_node()

    @pyaedt_function_handler()
    def _initialize_tree_node(self):
        BinaryTreeNode.__init__(self, self.line_name, self._oo, False, app=self._app)
        return True

    @pyaedt_function_handler()
    def _change_property(self, props_value):
        self._oreport_setup.ChangeProperty(
            ["NAME:AllTabs", ["NAME:Limit Line", ["NAME:PropServers", self.line_name], props_value]]
        )
        return True

    @pyaedt_function_handler()
    def set_line_properties(
        self, style=None, width=None, hatch_above=None, violation_emphasis=None, hatch_pixels=None, color=None
    ):
        """Set trace properties.

        Parameters
        ----------
        style : str, optional
            Style for the limit line. The default is ``None``. You can also use
            the ``LIFESTYLE`` property.
        width : int, optional
            Width of the limit line. The default is ``None``.
        hatch_above : bool
           Whether the hatch is above the limit line. The default is ``None``.
        violation_emphasis : bool
            Whether to add violation emphasis. The default is ``None``.
        hatch_pixels : int
            Number of pixels for the hatch. The default is ``None``.
        color : tuple, list
            Trace color as a tuple (R,G,B) or a list of integers [0,255].
            The default is ``None``.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.
        """
        props = ["NAME:ChangedProps"]
        if style:
            props.append(["NAME:Line Style", "Value:=", style])
        if width and isinstance(width, (int, float, str)):
            props.append(["NAME:Line Width", "Value:=", str(width)])
        if hatch_above is not None and isinstance(hatch_pixels, (int, str)):
            props.append(["NAME:Hatch Above", "Value:=", hatch_above])
        if hatch_pixels and isinstance(hatch_pixels, (int, str)):
            props.append(["NAME:Hatch Pixels", "Value:=", str(hatch_pixels)])
        if violation_emphasis:
            props.append(["NAME:Violation Emphasis", "Value:=", violation_emphasis])
        if color and isinstance(color, (list, tuple)) and len(color) == 3:
            props.append(["NAME:Color", "R:=", color[0], "G:=", color[1], "B:=", color[2]])
        return self._change_property(props)
