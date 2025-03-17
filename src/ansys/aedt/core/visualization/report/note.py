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

from ansys.aedt.core.generic.general_methods import pyaedt_function_handler
from ansys.aedt.core.modeler.cad.elements_3d import BinaryTreeNode


class Note(BinaryTreeNode):
    """Note Management Class."""

    def __init__(self, post, plot_note_name, oo=None):
        self._oo = oo
        self._app = post._app
        self._oreport_setup = post.oreportsetup
        self.plot_note_name = plot_note_name
        BinaryTreeNode.__init__(self, self.plot_note_name, self._oo, False, app=self._app)

    @pyaedt_function_handler()
    def _change_property(self, props_value):
        prop_server_name = self.plot_note_name
        self._oreport_setup.ChangeProperty(
            ["NAME:AllTabs", ["NAME:Note", ["NAME:PropServers", prop_server_name], props_value]]
        )
        return True

    @pyaedt_function_handler()
    def set_note_properties(
        self,
        text=None,
        back_color=None,
        background_visibility=None,
        border_color=None,
        border_visibility=None,
        border_width=None,
        font="Arial",
        font_size=12,
        italic=False,
        bold=False,
        color=(0, 0, 0),
    ):
        """Set note properties.

        Parameters
        ----------
        text : str, optional
            Style for the limit line. The default is ``None``. You can also use
            the ``LIFESTYLE`` property.
        back_color : int
            Background color specified as a tuple (R,G,B) or a list of integers [0,255].
            The default is ``None``.
        background_visibility : bool
            Whether to view background. The default is ``None``.
        border_color : int
            Trace color specified as a tuple (R,G,B) or a list of integers [0,255].
            The default is ``None``.
        border_visibility : bool
            Whether to view text border. The default is ``None``.
            The default is ``None``.
        border_width : int
            Text boarder width.
            The default is ``None``.
        font : str, optional
            The default is ``None``.
        font_size : int, optional
            The default is ``None``.
        italic : bool
            Whether the text is italic.
            The default is ``None``.
        bold : bool
            Whether the text is bold.
            The default is ``None``.
        color : int =(0, 0, 0)
            Trace color specified as a tuple (R,G,B) or a list of integers [0,255].
            The default is ``None``.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.
        """
        props = ["NAME:ChangedProps"]
        if text:
            props.append(["NAME:Note Text", "Value:=", text])
        if back_color and isinstance(back_color, (list, tuple)) and len(back_color) == 3:
            props.append(["NAME:Back Color", "R:=", back_color[0], "G:=", back_color[1], "B:=", back_color[2]])
        if background_visibility is not None:
            props.append(["NAME:Background Visibility", "Value:=", background_visibility])
        if border_color and isinstance(border_color, (list, tuple)) and len(border_color) == 3:
            props.append(["NAME:Border Color", "R:=", border_color[0], "G:=", border_color[1], "B:=", border_color[2]])
        if border_visibility is not None:
            props.append(["NAME:Border Visibility", "Value:=", border_visibility])
        if border_width and isinstance(border_width, (int, float)):
            props.append(["NAME:Border Width", "Value:=", str(border_width)])

        font_props = [
            "NAME:Note Font",
            "Height:=",
            -1 * font_size - 2,
            "Width:=",
            0,
            "Escapement:=",
            0,
            "Orientation:=",
            0,
            "Weight:=",
            700 if bold else 400,
            "Italic:=",
            255 if italic else 0,
            "Underline:=",
            0,
            "StrikeOut:=",
            0,
            "CharSet:=",
            0,
            "OutPrecision:=",
            3,
            "ClipPrecision:=",
            2,
            "Quality:=",
            1,
            "PitchAndFamily:=",
            34,
            "FaceName:=",
            font,
            "R:=",
            color[0],
            "G:=",
            color[1],
            "B:=",
            color[2],
        ]
        props.append(font_props)
        return self._change_property(props)
