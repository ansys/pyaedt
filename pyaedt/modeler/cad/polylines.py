from __future__ import absolute_import

import math

from pyaedt import _retry_ntimes
from pyaedt import pyaedt_function_handler
from pyaedt.generic.general_methods import _dim_arg
from pyaedt.modeler.cad.object3d import Object3d
from pyaedt.modeler.geometry_operators import GeometryOperators


class PolylineSegment(object):
    """Creates and manipulates a segment of a polyline.

    Parameters
    ----------
    type : str
        Type of the object. Choices are ``"Line"``, ``"Arc"``, ``"Spline"``,
        and ``"AngularArc"``.
    num_seg : int, optional
        Number of segments for the types ``"Arc"``, ``"Spline"``, and
        ``"AngularArc"``.  The default is ``0``. For the type
        ``Line``, this parameter is ignored.
    num_points : int, optional
        Number of control points for the type ``Spline``. For other
        types, this parameter
        is defined automatically.
    arc_angle : float or str, optional
        Sweep angle in radians or a valid value string. For example,
        ``"35deg"`` or ``"Specific
        to type AngularArc"``.
    arc_center : list or str, optional
        List of values in model units or a valid value string. For
        example, a list of ``[x, y, z]`` coordinates or ``"Specific to
        type AngularArc"``.
    arc_plane : str, int optional
        Plane in which the arc sweep is performed in the active
        coordinate system ``"XY"``, ``"YZ"`` or ``"ZX"``. The default is
        ``None``, in which case the plane is determined automatically
        by the first coordinate for which the starting point and
        center point have the same value.

    Examples
    --------
    See :class:`pyaedt.Primitives.Polyline`.

    """

    def __init__(self, type, num_seg=0, num_points=0, arc_angle=0, arc_center=None, arc_plane=None):

        valid_types = ["Line", "Arc", "Spline", "AngularArc"]
        assert type in valid_types, "Segment type must be in {}.".format(valid_types)
        self.type = type
        if type != "Line":
            self.num_seg = num_seg
        if type == "Line":
            self.num_points = 2
        if type == "Spline":
            self.num_points = num_points
        if "Arc" in type:
            self.num_points = 3
        if type == "AngularArc":
            self.arc_angle = arc_angle
            if not arc_center:
                arc_center = [0, 0, 0]
            assert len(arc_center) == 3, "Arc center must be a list of length 3."
            self.arc_center = arc_center
        if isinstance(arc_plane, int):
            if arc_plane == PLANE.XY:
                self.arc_plane = "XY"
            elif arc_plane == PLANE.ZX:
                self.arc_plane = "ZX"
            else:
                self.arc_plane = "YZ"
        else:
            self.arc_plane = arc_plane


class Polyline(Object3d):
    """Creates and manipulates a polyline.

    The constructor for this class is intended to be called from the
    :func:`pyaedt.modeler.Primitives.Primitives.create_polyline` method.
    The documentation is provided there.

    The returned Polyline object exposes the methods for manipulating the polyline.

    Parameters
    ----------
    primitives : :class:`pyaedt.modeler.Primitives3D.Primitives3D`
        Pointer to the parent Primitives object.
    src_object : optional
        The default is ``None``.
    position_list : list, optional
        List of positions in the ``[x, y, z]`` format. The default is ``None``.
    segment_type : str or list, optional
        Define the list of segment types.
        Valid arguments are  ``"Line"``, ``"Arc"``, ``"Spline"``, ``"AngularArc"``.
        The default is ``None``.
    cover_surface : bool, optional
        The default is ``False``.
    close_surface : bool, optional
        The default is ``False``.
    name : str, optional
        The default is ``None``.
    matname : str, optional
        Name of the material. The default is ``None``.
    xsection_type : str, optional
        Type of the cross-section. Options are ``"Line"``, ``"Circle"``, ``"Rectangle"``,
        and ``"Isosceles Trapezoid"``. The default is ``None``.
    xsection_orient : str, optional
        Direction of the normal vector to the width of the cross-section.
        Options are ``"X"``, ``"Y"``, ``"Z"``, and ``"Auto"``. The
        default is ``None``.
    xsection_width : float or str, optional
        Width or diameter of the cross-section for all types. The default is
        ``1``.
    xsection_topwidth : float or str, optional
        Top width of the cross-section for the type ``"Isosceles Trapezoid"`` only.
        The default is ``1``.
    xsection_height : float or str, optional
        Height of the cross-section for the types ``"Rectangle"`` and ``"Isosceles
        Trapezoid"`` only. The default is ``1``.
    xsection_num_seg : int, optional
        Number of segments in the cross-section surface for the types ``"Circle"``,
        ``"Rectangle"`` and ``"Isosceles Trapezoid"``. The default is ``0``.
        The value must be ``0`` or greater than ``2``.
    xsection_bend_type : str, optional
        Type of the bend. The default is ``None``, in which case the bend type
        is set to ``"Corner"``. For the type ``"Circle"``, the bend type
        should be set to ``"Curved"``.

    """

    def __init__(
        self,
        primitives,
        src_object=None,
        position_list=None,
        segment_type=None,
        cover_surface=False,
        close_surface=False,
        name=None,
        matname=None,
        xsection_type=None,
        xsection_orient=None,
        xsection_width=1,
        xsection_topwidth=1,
        xsection_height=1,
        xsection_num_seg=0,
        xsection_bend_type=None,
        non_model=False,
    ):

        self._primitives = primitives

        if src_object:
            self.__dict__ = src_object.__dict__.copy()
            if name:
                self._m_name = name  # This is conimg from
            else:
                self._id = src_object.id
                self._m_name = src_object.name
        else:

            self._xsection = self._primitives._crosssection_arguments(
                type=xsection_type,
                orient=xsection_orient,
                width=xsection_width,
                topwidth=xsection_topwidth,
                height=xsection_height,
                num_seg=xsection_num_seg,
                bend_type=xsection_bend_type,
            )
            self._positions = [i for i in position_list]
            # When close surface or cover_surface are set to True, ensure the start point and end point are coincident,
            # and insert a line segment to achieve this if necessary
            if cover_surface:
                close_surface = True

            self._is_closed = close_surface
            self._is_covered = cover_surface

            self._segment_types = None
            if segment_type:
                if isinstance(segment_type, (list, tuple)):
                    # self._segment_types = copy(segment_type)
                    self._segment_types = [i for i in segment_type]
                else:
                    self._segment_types = segment_type

            varg1 = self._point_segment_string_array()
            if non_model:
                flag = "NonModel#"
            else:
                flag = ""
            varg2 = self._primitives._default_object_attributes(name=name, matname=matname, flags=flag)

            new_object_name = _retry_ntimes(10, self.m_Editor.CreatePolyline, varg1, varg2)

            Object3d.__init__(self, primitives, name=new_object_name)
            self._primitives.objects[self.id] = self
            self._primitives.object_id_dict[self.name] = self.id

    @property
    def start_point(self):
        """List of the ``[x, y, z]`` coordinates for the starting point in the polyline
        object in the object's coordinate system.

        Returns
        -------
        list
            List of the ``[x, y, z]`` coordinates for the starting point in the polyline
            object.

        """
        return self.vertices[0].position

    @property
    def end_point(self):
        """List of the ``[x, y, z]`` coordinates for the ending point in the polyline
        object in the object's coordinate system.

        Returns
        -------
        list
            List of the ``[x, y, z]`` coordinates for the ending point in the polyline
            object.

        References
        ----------

        >>> oEditor.GetVertexIDsFromObject
        >>> oEditor.GetVertexPosition

        """
        return self.vertices[-1].position

    @property
    def points(self):
        """Polyline Points."""
        return self._positions

    @property
    def vertex_positions(self):
        """List of the ``[x, y, z]`` coordinates for all vertex positions in the
        polyline object in the object's coordinate system.

        Returns
        -------
        list
            List of the ``[x, y, z]`` coordinates for all vertex positions in the
            polyline object.

        References
        ----------

        >>> oEditor.GetVertexIDsFromObject
        >>> oEditor.GetVertexPosition

        """
        id_list = self._primitives.get_object_vertices(partID=self.id)
        position_list = [self._primitives.get_vertex_position(id) for id in id_list]
        return position_list

    @pyaedt_function_handler()
    def _pl_point(self, pt):
        pt_data = ["NAME:PLPoint"]
        pt_data.append("X:=")
        pt_data.append(_dim_arg(pt[0], self._primitives.model_units))
        pt_data.append("Y:=")
        pt_data.append(_dim_arg(pt[1], self._primitives.model_units))
        pt_data.append("Z:=")
        pt_data.append(_dim_arg(pt[2], self._primitives.model_units))
        return pt_data

    @pyaedt_function_handler()
    def _point_segment_string_array(self):
        """Retrieve the parameter arrays for specifying the points and segments of a polyline
        used in the :class:`pyaedt.modeler.Primitives.Polyline` constructor.

        Returns
        -------
        list

        """
        position_list = self._positions
        segment_types = self._segment_types

        assert (
            len(position_list) > 0
        ), "The ``position_list`` argument must be a list of positions with at least one point."
        if not segment_types:
            segment_types = [PolylineSegment("Line")] * (len(position_list) - 1)
        elif isinstance(segment_types, str):
            segment_types = [PolylineSegment(segment_types, num_points=len(position_list))]
        elif isinstance(segment_types, PolylineSegment):
            segment_types = [segment_types]
        elif isinstance(segment_types, list):
            # Convert all string-type entries in the segment_types list to PolylineSegments
            for ind, seg in enumerate(segment_types):
                if isinstance(seg, str):
                    segment_types[ind] = PolylineSegment(seg)
        else:
            raise ("Invalid segment_types input of type {}".format(type(segment_types)))

        # Add a closing point if needed
        varg1 = ["NAME:PolylineParameters"]
        varg1.append("IsPolylineCovered:=")
        varg1.append(self._is_covered)
        varg1.append("IsPolylineClosed:=")
        varg1.append(self._is_closed)

        # PointsArray
        points_str = ["NAME:PolylinePoints"]
        points_str.append(self._pl_point(position_list[0]))

        # Segments Array
        segment_str = ["NAME:PolylineSegments"]

        pos_count = 0
        vertex_count = 0
        index_count = 0

        while vertex_count <= len(segment_types):
            try:
                current_segment = None
                if vertex_count == len(segment_types):
                    if self._is_closed:
                        # Check the special case of a closed polyline needing an additional Line segment
                        if position_list[0] != position_list[-1]:
                            position_list.append(position_list[0])
                            current_segment = PolylineSegment("Line")
                    else:
                        break
                else:
                    current_segment = segment_types[vertex_count]
            except IndexError:
                raise ("Number of segments inconsistent with the number of points!")

            if current_segment:
                seg_str = self._segment_array(
                    current_segment, start_index=index_count, start_point=position_list[pos_count]
                )
                segment_str.append(seg_str)

                pos_count_incr = 0
                for i in range(1, current_segment.num_points):

                    if current_segment.type == "AngularArc":
                        points_str.append(self._pl_point(current_segment.extra_points[i - 1]))
                        index_count += 1
                    else:
                        if (pos_count + i) == len(position_list):
                            if current_segment.type == "Arc" and self._is_closed:
                                position_list.append(position_list[0])
                            else:
                                err_str = "Insufficient points in position_list to complete the specified segment list"
                                raise IndexError(err_str)
                        points_str.append(self._pl_point(position_list[pos_count + i]))
                        pos_count_incr += 1
                        index_count += 1
                pos_count += pos_count_incr
                vertex_count += 1
            else:
                break

        varg1.append(points_str)
        varg1.append(segment_str)

        # Poly Line Cross Section
        varg1.append(self._xsection)

        return varg1

    @pyaedt_function_handler()
    def _segment_array(self, segment_data, start_index=0, start_point=None):
        """Retrieve a property array for a polyline segment for use in the
        :class:`pyaedt.modeler.Primitives.Polyline` constructor.

         Parameters
         ----------
         segment_data : :class:`pyaedt.modeler.Primitives.PolylineSegment` or str
             Pointer to the calling object that provides additional functionality
             or a string with the segment type ``Line`` or ``Arc``.
         start_index : int, string
             Starting vertex index of the segment within a compound polyline. The
             default is ``0``.
         start_point : list, optional
             Position of the first point for type ``AngularArc``. The default is
             ``None``. Float values are considered in model units.

         Returns
         ------
         list
             List of properties defining a polyline segment.

        """
        if isinstance(segment_data, str):
            segment_data = PolylineSegment(segment_data)

        seg = [
            "NAME:PLSegment",
            "SegmentType:=",
            segment_data.type,
            "StartIndex:=",
            start_index,
            "NoOfPoints:=",
            segment_data.num_points,
        ]
        if segment_data.type != "Line":
            seg += ["NoOfSegments:=", "{}".format(segment_data.num_seg)]

        if segment_data.type == "AngularArc":

            # from start-point and angle, calculate the mid- and end-points
            # Also identify the plane of the arc ("YZ", "ZX", "XY")
            plane_axes = {"YZ": [1, 2], "ZX": [2, 0], "XY": [0, 1]}
            assert start_point, "Start-point must be defined for an AngularArc Segment"
            c_xyz = self._primitives.value_in_object_units(segment_data.arc_center)
            p0_xyz = self._primitives.value_in_object_units(start_point)

            if segment_data.arc_plane:
                # Accept the user input for the plane of rotation - let the modeler fail if invalid
                plane_def = (segment_data.arc_plane, plane_axes[segment_data.arc_plane])
            else:
                # Compare the numeric values of start-point and center-point to determine the orientation plane
                if c_xyz[0] == p0_xyz[0]:
                    plane_def = ("YZ", plane_axes["YZ"])
                elif c_xyz[1] == p0_xyz[1]:
                    plane_def = ("ZX", plane_axes["ZX"])
                elif c_xyz[2] == p0_xyz[2]:
                    plane_def = ("XY", plane_axes["XY"])
                else:
                    raise ("Start point and arc-center do not lie on a common base plane.")

            mod_units = self._primitives.model_units
            seg += [
                "ArcAngle:=",
                segment_data.arc_angle,
                "ArcCenterX:=",
                "{}".format(_dim_arg(segment_data.arc_center[0], mod_units)),
                "ArcCenterY:=",
                "{}".format(_dim_arg(segment_data.arc_center[1], mod_units)),
                "ArcCenterZ:=",
                "{}".format(_dim_arg(segment_data.arc_center[2], mod_units)),
                "ArcPlane:=",
                plane_def[0],
            ]

            # Calculate the extra two points of the angular arc in the alpha-beta plane
            alph_index = plane_def[1][0]
            beta_index = plane_def[1][1]
            c_alph = c_xyz[alph_index]
            c_beta = c_xyz[beta_index]
            p0_alph = p0_xyz[alph_index] - c_alph
            p0_beta = p0_xyz[beta_index] - c_beta

            # rotate to generate the new points
            arc_ang_rad = self._primitives._app.evaluate_expression(segment_data.arc_angle)
            rot_angle = arc_ang_rad * 0.5
            p1_alph = p0_alph * math.cos(rot_angle) + p0_beta * math.sin(rot_angle)
            p1_beta = p0_beta * math.cos(rot_angle) - p0_alph * math.sin(rot_angle)
            p2_alph = p1_alph * math.cos(rot_angle) + p1_beta * math.sin(rot_angle)
            p2_beta = p1_beta * math.cos(rot_angle) - p1_alph * math.sin(rot_angle)

            # Generate the  2 new points in XYZ
            p1 = list(p0_xyz)
            p1[alph_index] = p1_alph + c_alph
            p1[beta_index] = p1_beta + c_alph
            p2 = list(p0_xyz)
            p2[alph_index] = p2_alph + c_alph
            p2[beta_index] = p2_beta + c_beta
            segment_data.extra_points = [p1, p2]

        return seg

    @pyaedt_function_handler()
    def clone(self):
        """Clone a polyline object.

        Returns
        -------
        pyaedt.modeler.polylines.Polyline
            Polyline object that was created.

        References
        ----------

        >>> oEditor.Copy
        >>> oEditor.Paste

        Examples
        --------
        >>> primitives = self.aedtapp.modeler
        >>> P1 = modeler.create_polyline([[0, 1, 2], [0, 2, 3], [2, 1, 4]])
        >>> P2 = P1.clone()

        """
        vArg1 = ["NAME:Selections", "Selections:=", self.name]
        self._primitives.oeditor.Copy(vArg1)
        self._primitives.oeditor.Paste()
        return self._add_new_polyline()

    @pyaedt_function_handler()
    def _add_new_polyline(self):
        new_objects = self._primitives.find_new_objects()
        assert len(new_objects) == 1
        new_name = new_objects[0]
        new_polyline = Polyline(self._primitives, src_object=self, name=new_name)
        new_polyline._id = None
        self._primitives.objects[new_polyline.id] = new_polyline
        self._primitives.object_id_dict[new_name] = new_polyline.id
        return new_polyline

    @pyaedt_function_handler()
    def remove_vertex(self, position, abstol=1e-9):
        """Remove a vertex from an existing polyline by position.

        You must enter the exact position of the vertex as a list
        of ``[x, y, z]`` coordinates in the object's coordinate system.

        Parameters
        ----------
        position : list
            List of ``[x, y, z]`` coordinates specifying the vertex to remove.
        abstol : float, optional
            Absolute tolerance of the comparison of a specified position to the
            vertex positions. The default is ``1e-9``.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.

        References
        ----------

        >>> oEditor.DeletePolylinePoint

        Examples
        --------
        Use floating point values for the vertex positions.

        >>> P = modeler.create_polyline([[0, 1, 2], [0, 2, 3], [2, 1, 4]])
        >>> P.remove_vertex([0, 1, 2])

        Use string expressions for the vertex position.

        >>> P = modeler.create_polyline([[0, 1, 2], [0, 2, 3], [2, 1, 4]])
        >>> P.remove_vertex(["0mm", "1mm", "2mm"])

        Use string expressions for the vertex position and include an absolute
        tolerance when searching for the vertex to be removed.

        >>> P = modeler.create_polyline([[0, 1, 2], [0, 2, 3], [2, 1, 4]])
        >>> P.remove_vertex(["0mm", "1mm", "2mm"], abstol=1e-6)
        """
        found_vertex = False
        if self._primitives._app._is_object_oriented_enabled():
            obj = self._primitives.oeditor.GetChildObject(self._m_name).GetChildObject("CreatePolyline:1")
            segments = obj.GetChildNames()
            seg_id = 0
            for seg in segments:
                point = obj.GetChildObject(seg).GetPropValue("Point1")
                p = self._primitives.value_in_object_units([point[1], point[3], point[5]])
                pos_xyz = self._primitives.value_in_object_units(position)
                found_vertex = GeometryOperators.points_distance(p, pos_xyz) <= abstol
                if found_vertex:
                    at_start = True
                    break
                point = obj.GetChildObject(seg).GetPropValue("Point2")
                p = self._primitives.value_in_object_units([point[1], point[3], point[5]])
                found_vertex = GeometryOperators.points_distance(p, pos_xyz) <= abstol
                if found_vertex:
                    at_start = False
                    break
                seg_id += 1
        else:  # pragma: no cover
            pos_xyz = self._primitives.value_in_object_units(position)
            for ind, vertex_pos in enumerate(self.vertex_positions):
                # compare the specified point with the vertex data using an absolute tolerance
                # (default of math.isclose is 1e-9 which should be ok in almost all cases)
                found_vertex = GeometryOperators.points_distance(vertex_pos, pos_xyz) <= abstol
                if found_vertex:
                    if ind == len(self.vertex_positions) - 1:
                        seg_id = ind - 1
                        at_start = True
                    else:
                        seg_id = ind
                        at_start = False
                    break

        assert found_vertex, "Specified vertex {} not found in polyline {}.".format(position, self._m_name)
        self._primitives.oeditor.DeletePolylinePoint(
            [
                "NAME:Delete Point",
                "Selections:=",
                self._m_name + ":CreatePolyline:1",
                "Segment Indices:=",
                [seg_id],
                "At Start:=",
                at_start,
            ]
        )

        return True

    @pyaedt_function_handler()
    def remove_edges(self, edge_id):
        """Remove a vertex from an existing polyline by position.

        You must enter the exact position of the vertex as a list
        of ``[x, y, z]`` coordinates in the object's coordinate system.

        Parameters
        ----------
        edge_id : int or list of int
            One or more edge IDs within the total number of edges within the polyline.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.

        References
        ----------

        >>> oEditor.DeletePolylinePoint

        Examples
        --------
        >>> P = modeler.create_polyline([[0, 1, 2], [0, 2, 3], [2, 1, 4]])
        >>> P.remove_edges(edge_id=0)
        """
        if isinstance(edge_id, int):
            edge_id = [edge_id]
        try:
            self._primitives.oeditor.DeletePolylinePoint(
                [
                    "NAME:Delete Point",
                    "Selections:=",
                    self.name + ":CreatePolyline:1",
                    "Segment Indices:=",
                    edge_id,
                    "At Start:=",
                    True,
                ]
            )
        except:
            raise ValueError("Invalid edge ID {} is specified on polyline {}.".format(edge_id, self.name))
        return True

    @pyaedt_function_handler()
    def set_crosssection_properties(
        self, type=None, orient=None, width=0, topwidth=0, height=0, num_seg=0, bend_type=None
    ):
        """Set the properties of an existing polyline object.

        Parameters
        ----------
        type : str, optional
            Types of the cross-sections. Options are ``"Line"``, ``"Circle"``, ``"Rectangle"``,
            and ``"Isosceles Trapezoid"``. The default is ``None``.
        orient : str, optional
            Direction of the normal vector to the width of the cross-section.
            Options are ``"X"``, ``"Y"``, ``"Z"``, and ``"Auto"``. The default
            is ``None``, which sets the orientation to ``"Auto"``.
        width : float or str, optional
           Width or diameter of the cross-section for all types. The default is
           ``0``.
        topwidth : float or str
           Top width of the cross-section for the type ``"Isosceles Trapezoid"``
           only. The default is ``0``.
        height : float or str
            Height of the cross-section for the types ``"Rectangle"`` and `"Isosceles
            Trapezoid"`` only. The default is ``0``.
        num_seg : int, optional
            Number of segments in the cross-section surface for the types ``"Circle"``,
            ``"Rectangle"``, and ``"Isosceles Trapezoid"``. The default is ``0``.
            The value must be ``0`` or greater than ``2``.
        bend_type : str, optional
            Type of the bend. The default is ``None``, in which case the bend type
            is set to ``"Corner"``. For the type ``"Circle"``, the bend type should be
            set to ``"Curved"``.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.

        References
        ----------

        >>> oEditor.ChangeProperty

        Examples
        --------
        >>> P = modeler.create_polyline([[0, 1, 2], [0, 2, 3], [2, 1, 4]])
        >>> P.set_crosssection_properties(type="Circle", width="1mm")

        """
        # Set the default section type to "None"
        section_type = type
        if not section_type:
            section_type = "None"

        # Set the default orientation to "Auto"
        section_orient = orient
        if not section_orient:
            section_orient = "Auto"

        # Set the default bend-type to "Corner"
        section_bend = bend_type
        if not section_bend:
            section_bend = "Corner"

        # Ensure number-of segments is valid
        if num_seg:
            assert num_seg > 2, "Number of segments for a cross-section must be 0 or greater than 2."

        model_units = self._primitives.model_units

        arg1 = ["NAME:AllTabs"]
        arg2 = ["NAME:Geometry3DCmdTab", ["NAME:PropServers", self._m_name + ":CreatePolyline:1"]]
        arg3 = ["NAME:ChangedProps"]
        arg3.append(["NAME:Type", "Value:=", section_type])
        arg3.append(["NAME:Orientation", "Value:=", section_orient])
        arg3.append(["NAME:Bend Type", "Value:=", section_bend])
        arg3.append(["NAME:Width/Diameter", "Value:=", _dim_arg(width, model_units)])
        if section_type == "Rectangle":
            arg3.append(["NAME:Height", "Value:=", _dim_arg(height, model_units)])
        elif section_type == "Circle":
            arg3.append(["NAME:Number of Segments", "Value:=", num_seg])
        elif section_type == "Isosceles Trapezoid":
            arg3.append(["NAME:Top Width", "Value:=", _dim_arg(topwidth, model_units)])
            arg3.append(["NAME:Height", "Value:=", _dim_arg(height, model_units)])
        arg2.append(arg3)
        arg1.append(arg2)
        self._primitives.oeditor.ChangeProperty(arg1)
        self._update()
        return True

    @pyaedt_function_handler()
    def insert_segment(self, position_list, segment=None, segment_number=0):
        """Add a segment to an existing polyline.

        Parameters
        ----------
        position_list : list
            List of positions of the points that define the segment to insert.
            Either the starting point or ending point of the segment list must
            match one of the vertices of the existing polyline.
        segment : str or :class:`pyaedt.modeler.Primitives.PolylineSegment`
            Definition of the segment to insert. For the types ``"Line"`` and ``"Arc"``,
            use their string values ``"Line"`` and ``"Arc"``. For the types ``"AngularArc"``
            and ``"Spline"``, use the :class:`pyaedt.modeler.Primitives.PolylineSegment`
            object to define the segment precisely.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.

        References
        ----------

        >>> oEditor.InsertPolylineSegment

        """

        # Check for a valid number of points
        num_points = len(position_list)

        # define the segment type from the number of points given
        if not segment:
            if num_points == 2:
                segment = PolylineSegment("Line")
            elif num_points == 3:
                segment = PolylineSegment("Arc")
            else:
                segment = PolylineSegment("Spline", num_points=num_points)
        else:
            if isinstance(segment, str):
                segment = PolylineSegment(segment)
            num_points = segment.num_points

        # Check whether start-point of the segment is in the existing vertices
        start_point = self._primitives.value_in_object_units(position_list[0])

        # End point does not exist e.g. for an AngularArc
        try:
            end_point = self._primitives.value_in_object_units(position_list[num_points - 1])
        except:
            end_point = []

        segment_id = 1
        segment_index = 0
        num_vertices = len(self.vertices)
        for vertex in self.vertices:
            if vertex.position == end_point:
                if vertex.id == self.vertices[0].id:
                    if segment_id > 0:
                        segment_id -= 1
                at_start = True
                break
            # If start_point=[0, 0, 0] (a list of integers provided by the user), it won't be equal to vertex.position
            # that returns a list of float: [0., 0., 0.]. Thus we cast start_point as a list of floats.
            elif vertex.position == [float(x) for x in start_point]:
                at_start = False
                if segment_index > 0:
                    segment_index -= 1
                break
            segment_index += 1
        id_v = 0

        if isinstance(self._segment_types, list):
            s_types = [i for i in self._segment_types]
        else:
            s_types = [self._segment_types]
        for el in s_types:
            if isinstance(el, PolylineSegment):
                id_v += el.num_seg - 1
                if id_v > segment_index:
                    id_v -= el.num_seg - 1
                    break
        segment_index -= id_v

        assert segment_index < num_vertices, "Vertex for the insert is not found."
        type = segment.type

        varg1 = ["NAME:Insert Polyline Segment"]
        varg1.append("Selections:=")
        varg1.append(self._m_name + ":CreatePolyline:1")
        varg1.append("Segment Indices:=")
        varg1.append([segment_index])
        varg1.append("At Start:=")
        varg1.append(at_start)
        varg1.append("SegmentType:=")
        varg1.append(type)

        # Points and segment data
        varg2 = ["NAME:PolylinePoints"]

        if segment.type == "Line" or segment.type == "Spline" or segment.type == "Arc":
            for pt in position_list[0:num_points]:
                varg2.append(self._pl_point(pt))
            varg1.append(varg2)
        elif segment.type == "AngularArc":
            seg_str = self._segment_array(segment, start_point=start_point)
            varg2.append(self._pl_point(start_point))
            varg2.append(self._pl_point(segment.extra_points[0]))
            varg2.append(self._pl_point(segment.extra_points[1]))
            varg1.append(varg2)
            varg1 += seg_str[9:]
        self._primitives.oeditor.InsertPolylineSegment(varg1)

        if segment.type == "Spline":
            varg1 = ["NAME:AllTabs"]
            varg2 = ["NAME:Geometry3DPolylineTab"]

            varg3 = ["NAME:PropServers"]
            varg3.append(self._m_name + ":CreatePolyline:1" + ":Segment" + str(segment_id))
            varg2.append(varg3)

            varg4 = ["NAME:ChangedProps"]
            varg5 = ["NAME:Number of Segments"]
            varg5.append("Value:=")
            varg5.append(str(segment_number))

            varg4.append(varg5)
            varg2.append(varg4)
            varg1.append(varg2)

            self._primitives.oeditor.ChangeProperty(varg1)

        return True
