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
from ansys.aedt.core.generic.constants import SymbolStyle
from ansys.aedt.core.generic.constants import TraceType
from ansys.aedt.core.generic.general_methods import pyaedt_function_handler
from ansys.aedt.core.modeler.cad.elements_3d import BinaryTreeNode


class Trace(BinaryTreeNode):
    """Provides trace management."""

    def __init__(
        self,
        post,
        aedt_name,
        trace_name,
        oo=None,
    ):
        self._oo = oo
        self._app = post._app
        self._oreport_setup = post.oreportsetup
        self.aedt_name = aedt_name
        self._name = trace_name
        self.LINESTYLE = LineStyle()
        self.TRACETYPE = TraceType()
        self.SYMBOLSTYLE = SymbolStyle()
        self._trace_style = None
        self._trace_width = None
        self._trace_color = None
        self._symbol_style = None
        self._show_arrows = None
        self._fill_symbol = None
        self._symbol_color = None
        self._show_symbol = False
        self._available_props = []
        self._initialize_tree_node()

    @pyaedt_function_handler()
    def _initialize_tree_node(self):
        BinaryTreeNode.__init__(self, self.aedt_name, self._oo, False, app=self._app)
        return True

    @property
    def curve_properties(self):
        """All curve graphical properties. It includes colors, trace and symbol settings.

        Returns
        -------
            :class:`ansys.aedt.core.modeler.cad.elements_3d.BinaryTree` when successful,
            ``False`` when failed.

        """
        if self.aedt_name.split(":")[-1] in self.children:
            return self.children[self.aedt_name.split(":")[-1]].properties
        return {}

    @property
    def name(self):
        """Trace name.

        Returns
        -------
        str
            Trace name.
        """
        return self._name

    @name.setter
    def name(self, value):
        report_name = self.aedt_name.split(":")[0]
        prop_name = report_name + ":" + self.name

        self._oreport_setup.ChangeProperty(
            [
                "NAME:AllTabs",
                [
                    "NAME:Trace",
                    ["NAME:PropServers", prop_name],
                    ["NAME:ChangedProps", ["NAME:Specify Name", "Value:=", True]],
                ],
            ]
        )
        self._oreport_setup.ChangeProperty(
            [
                "NAME:AllTabs",
                ["NAME:Trace", ["NAME:PropServers", prop_name], ["NAME:ChangedProps", ["NAME:Name", "Value:=", value]]],
            ]
        )
        self.aedt_name = self.aedt_name.replace(self.name, value)
        self.trace_name = value

    @pyaedt_function_handler()
    def _change_property(self, props_value):
        self._oreport_setup.ChangeProperty(
            ["NAME:AllTabs", ["NAME:Attributes", ["NAME:PropServers", self.aedt_name], props_value]]
        )
        return True

    @pyaedt_function_handler(trace_style="style")
    def set_trace_properties(self, style=None, width=None, trace_type=None, color=None):
        """Set trace properties.

        Parameters
        ----------
        style : str, optional
            Style for the trace line. The default is ``None``. You can also use
            the ``LINESTYLE`` property.
        width : int, optional
            Width of the trace line. The default is ``None``.
        trace_type : str
            Type of the trace line. The default is ``None``. You can also use the ``TRACETYPE``
            property.
        color : tuple, list
            Trace line color specified as a tuple (R,G,B) or a list of integers [0,255].
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
        if trace_type:
            props.append(["NAME:Trace Type", "Value:=", trace_type])
        if color and isinstance(color, (list, tuple)) and len(color) == 3:
            props.append(["NAME:Color", "R:=", color[0], "G:=", color[1], "B:=", color[2]])
        return self._change_property(props)

    @pyaedt_function_handler()
    def set_symbol_properties(self, show=True, style=None, show_arrows=None, fill=None, color=None):
        """Set symbol properties.

        Parameters
        ----------
        show : bool, optional
            Whether to show the symbol. The default is ``True``.
        style : str, optional
           Style of the style. The default is ``None``. You can also use the ``SYMBOLSTYLE``
           property.
        show_arrows : bool, optional
            Whether to show arrows. The default is ``None``.
        fill : bool, optional
            Whether to fill the symbol with a color. The default is ``None``.
        color : tuple, list
            Symbol fill color specified as a tuple (R,G,B) or a list of integers [0,255].
            The default is ``None``.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.
        """
        props = ["NAME:ChangedProps", ["NAME:Show Symbol", "Value:=", show]]
        if style:
            props.append(["NAME:Symbol Style", "Value:=", style])
        if show_arrows:
            props.append(["NAME:Show Arrows", "Value:=", show_arrows])
        if fill:
            props.append(["NAME:Fill Symbol", "Value:=", fill])
        if color and isinstance(color, (list, tuple)) and len(color) == 3:
            props.append(["NAME:Symbol Color", "R:=", color[0], "G:=", color[1], "B:=", color[2]])
        return self._change_property(props)
