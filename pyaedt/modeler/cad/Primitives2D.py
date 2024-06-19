# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 - 2024 ANSYS, Inc. and/or its affiliates.
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

from pyaedt.generic.general_methods import pyaedt_function_handler
from pyaedt.modeler.cad.Primitives import GeometryModeler


class Primitives2D(GeometryModeler, object):
    """Manages primitives in 2D tools.

    This class is inherited in the caller application and is accessible through the primitives variable part
    of the modeler object (for example, ``hfss.modeler`` or ``icepak.modeler``).


    Examples
    --------
    Basic usage demonstrated with a Q2D or Maxwell 2D design:

    >>> from pyaedt import Q2d
    >>> aedtapp = Q2d()
    >>> prim = aedtapp.modeler
    """

    @property
    def plane2d(self):
        """Create a 2D plane."""
        plane = "Z"
        if self._app.design_type == "Maxwell 2D":  # Cylindrical symmetry about the z-axis.
            if self._app._odesign.GetGeometryMode() == "about Z":
                plane = "Y"
        return plane

    def __init__(self, application):
        GeometryModeler.__init__(self, application, is3d=False)

    @pyaedt_function_handler(position="origin", matname="material")
    def create_circle(
        self, origin, radius, num_sides=0, is_covered=True, name=None, material=None, non_model=False, **kwargs
    ):
        """Create a circle.

        Parameters
        ----------
        origin : list
            ApplicationName.modeler.Position(x,y,z) object
        radius : float
            Radius of the object.
        num_sides : int, optional
            Number of sides. The default is ``0``, which is correct for a circle.
        is_covered : bool
            Specify whether the ellipse is a sheet (covered) or a line object
        name : str, optional
            Name of the object. The default is ``None``. If ``None`` ,
            a unique name ``"NewObject_xxxxxx"`` will be assigned)
        material : str, optional
            Name of the material. The default is ``None``. If ``None``,
            the default material is assigned.
        non_model : bool, optional
             Either to create the new object as model or non-model. The default is ``False``.
         **kwargs : optional
            Additional keyword arguments may be passed when creating the primitive to set properties. See
            ``pyaedt.modeler.cad.object3d.Object3d`` for more details.


        Returns
        -------
        :class:`pyaedt.modeler.cad.object3d.Object3d`
            3D object.

        References
        ----------

        >>> oEditor.CreateCircle

        Examples
        --------
        >>> circle1 = aedtapp.modeler.create_circle([0, -2, -2],3)
        >>> circle2 = aedtapp.modeler.create_circle(origin=[0, -2, -2],radius=3,
        ...                                         num_sides=6,name="MyCircle",material="Copper")


        """
        # TODO: kwargs such as 'matname' and 'nonmodel' should be deprecated.
        szAxis = self.plane2d
        XCenter, YCenter, ZCenter = self._pos_with_arg(origin)
        Radius = self._arg_with_dim(radius)

        vArg1 = ["NAME:CircleParameters"]
        vArg1.append("IsCovered:="), vArg1.append(is_covered)
        vArg1.append("XCenter:="), vArg1.append(XCenter)
        vArg1.append("YCenter:="), vArg1.append(YCenter)
        vArg1.append("ZCenter:="), vArg1.append(ZCenter)
        vArg1.append("Radius:="), vArg1.append(Radius)
        vArg1.append("WhichAxis:="), vArg1.append(szAxis)
        vArg1.append("NumSegments:="), vArg1.append("{}".format(num_sides))

        vArg2 = self._default_object_attributes(name=name, matname=material, flags="NonModel#" if non_model else "")
        new_object_name = self.oeditor.CreateCircle(vArg1, vArg2)
        return self._create_object(new_object_name, **kwargs)

    # fmt: off
    @pyaedt_function_handler(position="origin", matname="material")
    def create_ellipse(
        self,
        origin,
        major_radius,
        ratio,
        is_covered=True,
        name=None,
        material=None,
        non_model=False,
        segments=0,
        **kwargs
    ):  # fmt: on
        """Create an ellipse.

        Parameters
        ----------
        origin : list of float
            Center Position of the ellipse
        major_radius : flost
            Length of the major axis of the ellipse
        ratio : float
            Ratio of the major axis to the minor axis of the ellipse
        is_covered : bool
            Specify whether the ellipse is a sheet (covered) or a line object
        name : str, default=None
            Name of the object. The default is ``None``. If ``None`` ,
            a unique name NewObject_xxxxxx will be assigned)
        material : str, default=None
             Name of the material. The default is ``None``. If ``None``,
             the default material is assigned.
        non_model : bool, optional
             Whether to create the object as a non-model. The default is ``False``, in which
             case the object is created as a model.
        segments : int, optional
            Number of segments to apply to create the segmented geometry.
            The default is ``0``.
        **kwargs : optional
            Additional keyword arguments to pass to set properties when creating the primitive.
           For more information, see ``pyaedt.modeler.cad.object3d.Object3d``.


        Returns
        -------
        pyaedt.modeler.cad.object3d.Object3d
            Object 3d.

        References
        ----------

        >>> oEditor.CreateEllipse

        Examples
        --------
        >>> ellipse1 = aedtapp.modeler.create_ellipse([0, -2, -2], 4.0, 0.2)
        >>> ellipse2 = aedtapp.modeler.create_ellipse(origin=[0, -2, -2], major_radius=4.0, ratio=0.2,
        ...                                           name="MyEllipse", material="Copper")
        """
        szAxis = self.plane2d
        XStart, YStart, ZStart = self._pos_with_arg(origin)

        vArg1 = ["NAME:EllipseParameters"]
        vArg1.append("IsCovered:="), vArg1.append(is_covered)
        vArg1.append("XCenter:="), vArg1.append(XStart)
        vArg1.append("YCenter:="), vArg1.append(YStart)
        vArg1.append("ZCenter:="), vArg1.append(ZStart)
        vArg1.append("MajRadius:="), vArg1.append(self._arg_with_dim(major_radius))
        vArg1.append("Ratio:="), vArg1.append(ratio)
        vArg1.append("WhichAxis:="), vArg1.append(szAxis)
        vArg1.append("NumSegments:="), vArg1.append(segments)

        vArg2 = self._default_object_attributes(name=name, matname=material, flags="NonModel#" if non_model else "")
        new_object_name = self.oeditor.CreateEllipse(vArg1, vArg2)
        return self._create_object(new_object_name, **kwargs)

    @pyaedt_function_handler(position="origin", dimension_list="sizes", matname="material")
    def create_rectangle(self, origin, sizes, is_covered=True, name=None, material=None, non_model=False, **kwargs):
        """Create a rectangle.

        Parameters
        ----------
        origin : list
            Position of the lower-left corner of the rectangle
        sizes : list
            List of rectangle sizes: [X size, Y size] for XY planes or [Z size, R size] for RZ planes
        is_covered : bool
            Specify whether the ellipse is a sheet (covered) or a line object
        name : str, default=None
            Name of the object. The default is ``None``. If ``None`` ,
            a unique name NewObject_xxxxxx will be assigned)
        material : str, default=None
             Name of the material. The default is ``None``. If ``None``,
             the default material is assigned.
        non_model : bool, optional
             Either if create the new object as model or non-model. The default is ``False``.

        Returns
        -------
        :class:`pyaedt.modeler.cad.object3d.Object3d`

        References
        ----------

        >>> oEditor.CreateRectangle

        Examples
        --------

        >>> rect1 = aedtapp.modeler.create_rectangle([0, -2, -2],[3, 4])
        >>> rect2 = aedtapp.modeler.create_rectangle(origin=[0, -2, -2],sizes=[3, 4],name="MyCircle",material="Copper")

        """
        # TODO: Primitives in Maxwell 2D must have Z=0, otherwise the transparency cannot be changed. (issue 4071)
        axis = self.plane2d
        x_start, y_start, z_start = self._pos_with_arg(origin)
        width = self._arg_with_dim(sizes[0])
        height = self._arg_with_dim(sizes[1])

        vArg1 = ["NAME:RectangleParameters"]
        vArg1.append("IsCovered:="), vArg1.append(is_covered)
        vArg1.append("XStart:="), vArg1.append(x_start)
        vArg1.append("YStart:="), vArg1.append(y_start)
        vArg1.append("ZStart:="), vArg1.append(z_start)
        vArg1.append("Width:="), vArg1.append(width)
        vArg1.append("Height:="), vArg1.append(height)
        vArg1.append("WhichAxis:="), vArg1.append(axis)

        vArg2 = self._default_object_attributes(name=name, matname=material, flags="NonModel#" if non_model else "")
        new_object_name = self.oeditor.CreateRectangle(vArg1, vArg2)
        return self._create_object(new_object_name, **kwargs)

    @pyaedt_function_handler(position="origin", matname="material")
    def create_regular_polygon(
        self, origin, start_point, num_sides=6, name=None, material=None, non_model=False, **kwargs
    ):
        """Create a rectangle.

        Parameters
        ----------
        origin : list of float
            Position of the center of the polygon in ``[x, y, z]``.
        start_point : list of float
            Start point for the outer path of the polygon in ``[x, y, z]``.
        num_sides : int
            Number of sides of the polygon. Must be an integer >= 3.
        name : str, default=None
            Name of the object. The default is ``None``. If ``None`` ,
            a unique name NewObject_xxxxxx will be assigned)
        material : str, default=None
             Name of the material. The default is ``None``. If ``None``,
             the default material is assigned.
        non_model : bool, optional
             Either if create the new object as model or non-model. The default is ``False``.
         **kwargs : optional
            Additional keyword arguments may be passed when creating the primitive to set properties. See
            ``pyaedt.modeler.cad.object3d.Object3d`` for more details.


        Returns
        -------
        pyaedt.modeler.cad.object3d.Object3d

        References
        ----------

        >>> oEditor.CreateRegularPolygon

        Examples
        --------

        >>> pg1 = aedtapp.modeler.create_regular_polygon([0, 0, 0], [0, 2, 0])
        >>> pg2 = aedtapp.modeler.create_regular_polygon(origin=[0, 0, 0], start_point=[0, 2, 0],
        ...                                              name="MyPolygon", material="Copper")

        """
        x_center, y_center, z_center = self._pos_with_arg(origin)
        x_start, y_start, z_start = self._pos_with_arg(start_point)

        n_sides = int(num_sides)
        assert n_sides > 2  # TODO: Replace assert with an exception.

        vArg1 = ["NAME:RegularPolygonParameters"]
        vArg1.append("XCenter:="), vArg1.append(x_center)
        vArg1.append("YCenter:="), vArg1.append(y_center)
        vArg1.append("ZCenter:="), vArg1.append(z_center)
        vArg1.append("XStart:="), vArg1.append(x_start)
        vArg1.append("YStart:="), vArg1.append(y_start)
        vArg1.append("ZStart:="), vArg1.append(z_start)

        vArg1.append("NumSides:="), vArg1.append(n_sides)
        vArg1.append("WhichAxis:="), vArg1.append(self.plane2d)

        vArg2 = self._default_object_attributes(name=name, matname=material, flags="NonModel#" if non_model else "")
        new_object_name = self.oeditor.CreateRegularPolygon(vArg1, vArg2)
        return self._create_object(new_object_name, **kwargs)

    @pyaedt_function_handler(region_name="name")
    def create_region(self, pad_value=300, pad_type="Percentage Offset", name="Region", **kwarg):
        """Create an air region.

        Parameters
        ----------
        pad_value : float, str, list of floats or list of str, optional
            Padding values to apply. If a list is not provided, the same
            value is applied to all padding directions. If a list of floats
            or strings is provided, the values are
            interpreted as padding for ``["+X", "-X", "+Y", "-Y"]`` for XY geometry mode,
            and ``["+R", "+Z", "-Z"]`` for RZ geometry mode.
        pad_type : str, optional
            Padding definition. The default is ``"Percentage Offset"``.
            Options are ``"Absolute Offset"``,
            ``"Absolute Position"``, ``"Percentage Offset"``, and
            ``"Transverse Percentage Offset"``. When using a list,
            different padding types can be provided for different
           directions.
        name : str, optional
            Region name. The default is ``None``, in which case the name
            is generated automatically.

        Returns
        -------
        :class:`pyaedt.modeler.cad.object3d.Object3d`
            Region object.

        References
        ----------

        >>> oEditor.CreateRegion
        """
        # backward compatibility
        if kwarg:
            if "is_percentage" in kwarg.keys():
                is_percentage = kwarg["is_percentage"]
            else:
                is_percentage = True
            if kwarg.get("pad_percent", False):
                pad_percent = kwarg["pad_percent"]
                pad_value = pad_percent
            if isinstance(pad_value, list) and len(pad_value) == 4:
                pad_value = [pad_value[i // 2 + 2 * (i % 2)] for i in range(4)]
            pad_type = ["Absolute Offset", "Percentage Offset"][int(is_percentage)]

        if isinstance(pad_type, bool):
            pad_type = ["Absolute Offset", "Percentage Offset"][int(pad_type)]

        if self._app.design_type == "2D Extractor" or (
            self._app.design_type == "Maxwell 2D" and self._app.odesign.GetGeometryMode() == "XY"
        ):
            if not isinstance(pad_value, list):
                pad_value = [pad_value] * 4
            if len(pad_value) != 4:
                self.logger.error("Wrong padding list provided. Four values have to be provided.")
                return False
            pad_value = [pad_value[0], pad_value[2], pad_value[1], pad_value[3], 0, 0]
        else:
            if not isinstance(pad_value, list):
                pad_value = [pad_value] * 3
            if len(pad_value) != 3:
                self.logger.error("Wrong padding list provided. Three values have to be provided for RZ geometry.")
                return False
            pad_value = [pad_value[0], 0, 0, 0, pad_value[1], pad_value[2]]

        return self._create_region(pad_value, pad_type, name, region_type="Region")
