"""
This module contains these Primitives classes: ``Polyline`` and ``Primitives``.


========================================================

"""
from __future__ import absolute_import
import sys
from collections import defaultdict
import math
import time
import numbers
from copy import copy
from .GeometryOperators import GeometryOperators
from .Object3d import Object3d, EdgePrimitive, FacePrimitive, VertexPrimitive, _dim_arg
from ..generic.general_methods import aedt_exception_handler, retry_ntimes
from ..application.Variables import Variable

if "IronPython" in sys.version or ".NETFramework" in sys.version:
    _ironpython = True
else:
    _ironpython = False


default_materials = {"Icepak": "air", "HFSS": "vacuum", "Maxwell 3D": "vacuum", "Maxwell 2D": "vacuum",
                     "2D Extractor": "copper", "Q3D Extractor": "copper", "HFSS 3D Layout": "copper", "Mechanical" : "copper"}


class PolylineSegment():

    @aedt_exception_handler
    def __init__(self, type, num_seg=0, num_points=0, arc_angle=0, arc_center=None, arc_plane=None):
        '''Object that describes a segment of a polyline within the 3D modeler.

        Parameters
        ----------
        type : str
            Type of object. Choices are ``Line``, ``Arc``, ``Spline``, and ``AngularArc``.
        num_seg: int, optional
            Number of segments for the type ``Arc``, ``Spline``, or ``AngularArc``.
            The default is ``0``. If the type is ``Line``, this parameter is ignored.
        num_points : int, optional
            Number of control points for the type ``Spline``. For other types, this parameter
            is defined automatically.
        arc_angle : float or str, optional
            Sweep angle in radians or a valid value string. For example, ``"35deg"`` or ``"Specific 
            to type AngularArc``.
        arc_center : list, optional
            List of values in model units or value string. For example, ``[x, y, z]`` or ``"Specific 
            to type AngularArc"``.
        arc_plane : str, optinal
            Plane in which the arc sweep is performed in the active coordinate system ``XY``, ``YZ`` 
            or ``ZX``. The default is ``None``. If ``None``, the plane is determined automatically 
            by the first coordinate for which start-point and center-point have the same value.

        Examples
        ----------

        See Polyline()
        '''

        valid_types = ["Line", "Arc", "Spline", "AngularArc"]
        assert type in valid_types, "Segment type must be in {}".format(valid_types)
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
        self.arc_plane = arc_plane


class Polyline(object):
    """ Polyline class.

    This class provides methods for creating and manipulating polyline objects within 
    the AEDT Modeler. Intended usage is for the constructor of this class to be called
    by the ``Primitives.draw_polyline`` method. The documentation is provided there.

    The returned Polyline object exposes the methods for manipulation of the polyline:

    Methods
    ------
    set_crosssection_properties
    insert_segment
    remove_vertex
    remove_edges
    clone

    """
    @aedt_exception_handler
    def __init__(self, parent, position_list=None, object_id=None, segment_type=None, cover_surface=False,
                 close_surface=False, name=None, matname=None, xsection_type=None, xsection_orient=None,
                 xsection_width=0, xsection_topwidth=0, xsection_height=0,
                 xsection_num_seg=0, xsection_bend_type=None):
        """
        See Also
        --------
        The constructor is intended to be called from the Primitives.draw_polyline method

        """
        self._parent = parent

        self._xsection = self._crosssection(type=xsection_type, orient=xsection_orient, width=xsection_width,
                                            topwidth=xsection_topwidth, height=xsection_height, num_seg=xsection_num_seg,
                                            bend_type=xsection_bend_type)
        if position_list:

            self._o = parent.request_new_object(matname=matname)

            self._positions = copy(position_list)

            # When close surface or cover_surface are set to True, ensure the start point and end point are coincident,
            # and insert a line segment to achieve this if necessary
            if cover_surface:
                close_surface = True

            self._is_closed = close_surface
            self._is_covered = cover_surface

            self._segment_types = None
            if segment_type:
                self._segment_types = copy(segment_type)

            varg1 = self._point_segment_string_array()

            varg2 = self._o.export_attributes(name)

            self._o.name = parent.oeditor.CreatePolyline(varg1, varg2)

            # Determine whether line or sheet based on the number of faces
            if len(self._o.faces):
                object_type = "Sheet"
            else:
                object_type = "Line"

            parent._update_object(self._o, object_type)

        else:
            # Instantiate a new Polyline object for an existing object id in the modeler
            self._o = self._parent.objects[object_id]
            self._positions = []
            for vertex in self._o.vertices:
                position = vertex.position
                self._positions.append(position)

        # If a cross-section type is defined, specify a solid 3D object
        if xsection_type:
            self._parent.objects[self.id].is3d = True
            self._parent.objects[self.id].object_type = "Solid"
        else:
            self._parent.objects[self.id].is3d = False
            if cover_surface:
                self._parent.objects[self.id].object_type = "Sheet"
            else:
                self._parent.objects[self.id].object_type = "Line"

    @property
    def id(self):
        """Object ID of the polyline in the AEDT modeler.

        Returns
        -------
        int
        """
        return self._o._id

    @property
    def name(self):
        """ Name of the polyline in the AEDT modeler. 
        
        .. note::
           The name can differ from the specified name if an
           object of this name already existed.

        Returns
        -------
        int
        
        """
        return self._o.name

    @property
    def start_point(self):
        """ Position of the first point in the polyline object in [x, y, z] in the object coordinate system.

        Returns
        -------
        list
        
        """
        vertex_id = self._parent.get_object_vertices(partID=self.id)[0]
        return self._parent.get_vertex_position(vertex_id)

    @property
    def end_point(self):
        """ Position of the end point in the polyline object in [x, y, z] in the object coordinate system.

        Returns
        -------
        list
        
        """
        end_vertex_id = self._parent.get_object_vertices(partID=self.id)[-1]
        return self._parent.get_vertex_position(end_vertex_id)

    @property
    def vertex_positions(self):
        """ List of all vertex positions in the polyline object in [x, y, z] in the object coordinate system.

        Returns
        -------
        list
        
        """
        id_list = self._parent.get_object_vertices(partID=self.id)
        position_list = [ self._parent.get_vertex_position(id) for id in id_list]
        return position_list

    @aedt_exception_handler
    def _crosssection(self, type=None, orient=None, width=0, topwidth=0, height=0, num_seg=0, bend_type=None):
        """ Generate the properties array for the polyline cross-section.
        """
        arg_str = ["NAME:PolylineXSection"]

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

        #Ensure number-of segments is valid
        if num_seg:
            assert num_seg > 2, "Number of segments for a cross-section must be 0 or greater than 2."

        model_units = self._parent.model_units
        arg_str += ["XSectionType:=", section_type]
        arg_str += ["XSectionOrient:=", section_orient]
        arg_str += ["XSectionWidth:=", _dim_arg(width, model_units)]
        arg_str += ["XSectionTopWidth:=", _dim_arg(topwidth, model_units)]
        arg_str += ["XSectionHeight:=", _dim_arg(height, model_units)]
        arg_str += ["XSectionNumSegments:=", "{}".format(num_seg)]
        arg_str += ["XSectionBendType:=", section_bend]

        return arg_str

    @aedt_exception_handler
    def _pl_point(self, pt):
        """ Property array data for a polyline point.

        Generate the XYZ point data property array for AEDT. The X, Y, and Z coordinates are taken
        from the first three elements of the point. Numeric values are converted to strings with model units.

        Parameters
        ------
        pt : list or indexable object
            Position in X, Y, and Z coordinates.

        Returns
        -------
        list

        """
        #
        pt_data= ["NAME:PLPoint"]
        pt_data.append('X:=')
        pt_data.append(_dim_arg(pt[0], self._parent.model_units))
        pt_data.append('Y:=')
        pt_data.append(_dim_arg(pt[1], self._parent.model_units))
        pt_data.append('Z:=')
        pt_data.append(_dim_arg(pt[2], self._parent.model_units))
        return pt_data

    @aedt_exception_handler
    def _point_segment_string_array(self):
        """ Retrieve a parameter array for points and segments.

        Returns the parameter array required to specify the points and segments of a polyline
        for use in the AEDT API command ``CreatePolyline``.

        Returns
        -------
        list

        """
        position_list = self._positions
        segment_types = self._segment_types

        assert len(position_list) > 0, "The ``position_list`` argument must be a list of positions with at least one point."
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
            raise("Invalid segment_types input of type {}".format(type(segment_types)))

        # Add a closing point if needed  #TODO check for all combinations
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
                seg_str = self._segment_array(current_segment, start_index=index_count, start_point=position_list[pos_count])
                segment_str.append(seg_str)

                pos_count_incr = 0
                for i in range(1, current_segment.num_points):

                    if current_segment.type == "AngularArc":
                        points_str.append(self._pl_point(current_segment.extra_points[i-1]))
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

    @aedt_exception_handler
    def _segment_array(self, segment_data, start_index=0, start_point=None):
        """Property array for a polyline segment.

        Returns a list containing parameters for an individual segment of a polyline
        to use in the command ``CreatePolyline`` in the AEDT API.

        Parameters
        ----------
        segment_data : PolylineSegment or str with segment type ``Line`` or ``Arc``.

        start_index : int, string
            Starting vertex index of the segment within a compound polyline. The
            default is ``0``.
        start_point : list, optional
            Position of the first point for type ``AngularArc``. The default is 
            ``None``. Float values are considered in model units.

        Returns
        ------
        list
        
        """

        if isinstance(segment_data, str):
            segment_data = PolylineSegment(segment_data)

        seg = [ "NAME:PLSegment",
                "SegmentType:="	, segment_data.type,
                "StartIndex:="		, start_index,
                "NoOfPoints:="		, segment_data.num_points ]
        if segment_data.type != "Line":
            seg += ["NoOfSegments:="	, '{}'.format(segment_data.num_seg)]

        if segment_data.type == "AngularArc":

            # from start-point and angle, calculate the mid- and end-points
            # Also identify the plane of the arc ("YZ", "ZX", "XY")
            plane_axes = {
                "YZ": [1, 2],
                "ZX": [2, 0],
                "XY": [0, 1]
            }
            assert start_point, "Start-point must be defined for an AngularArc Segment"
            c_xyz = self._parent.value_in_object_units(segment_data.arc_center)
            p0_xyz = self._parent.value_in_object_units(start_point)

            if segment_data.arc_plane:
                # Accept the user input for the plane of rotation - let the modeler fail if invalid
                plane_def = (segment_data.arc_plane, plane_axes[segment_data.arc_plane])
            else:
                # Compare the numeric values of start-point and center-point to determine the orientation plane
                if c_xyz[0] == p0_xyz[0]:
                    plane_def = ( "YZ", plane_axes["YZ"] )
                elif c_xyz[1] == p0_xyz[1]:
                    plane_def = ( "ZX", plane_axes["ZX"] )
                elif c_xyz[2] == p0_xyz[2]:
                    plane_def = ( "XY", plane_axes["XY"] )
                else:
                    raise("Start point and arc-center do not lie on a common base plane.")

            mod_units = self._parent.model_units
            seg += ["ArcAngle:=", segment_data.arc_angle,
                    "ArcCenterX:=", "{}".format(_dim_arg(segment_data.arc_center[0], mod_units)),
                    "ArcCenterY:=", "{}".format(_dim_arg(segment_data.arc_center[1], mod_units)),
                    "ArcCenterZ:=", "{}".format(_dim_arg(segment_data.arc_center[2], mod_units)),
                    "ArcPlane:=", plane_def[0]
                    ]

            # Calculate the extra two points of the angular arc in the alpha-beta plane
            alph_index = plane_def[1][0]
            beta_index = plane_def[1][1]
            c_alph = c_xyz[alph_index]
            c_beta = c_xyz[beta_index]
            p0_alph = p0_xyz[alph_index] - c_alph
            p0_beta = p0_xyz[beta_index] - c_beta

            #rotate to generate the new points
            arc_ang_rad = self._parent._parent.evaluate_expression(segment_data.arc_angle)
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

    @aedt_exception_handler
    def clone(self):
        """Clone the polyline object in the modeler.

        A new polyline object is instantiated and the copied object is returned.

        Returns
        -------
        Polyline

        Examples
        --------

        >>> primitives = self.aedtapp.modeler.primitives
        >>> P1 = primitives.draw_polyline([[0, 1, 2], [0, 2, 3], [2, 1, 4]])
        >>> P2 = P1.clone()

        """
        # Clone the polyline in the modeler
        ret, new_name = self._parent._modeler.clone(self.id)

        # Ensure that a single string name is returned
        assert isinstance(new_name, str), "Could not copy myself"

        # obtain the id of the polyine from the returned name
        new_id = self._parent.get_obj_id(new_name)

        # Instantiate the new Polyline object based on the new object id
        duplicate = Polyline(self._parent, object_id=new_id)

        # return the new Polyline object
        return duplicate

    @aedt_exception_handler
    def remove_vertex(self, position, abstol=1e-9):
        """ Remove a vertex from an existing polyline by position.

        Removes a vertex from a polyline object.You must enter the exact position of the vertex as a list
        of [x, y, z] coordinates in the object coordinate system

        Parameters
        ----------
        position : list
            List of x, y, z coordinates specifying the vertex to be removed

        abstol : float, default = 0.0
            Absolute tolerance of the comparison of specified position to the vertex positions

        Returns
        -------
        bool

        Examples
        ------
        Using floating-point values for the vertex positions
        >>> P = primitives.draw_polyline([[0, 1, 2], [0, 2, 3], [2, 1, 4]])
        >>> P.remove_vertex([0, 1, 2])

        or using string expressions for the position:
        >>> P = primitives.draw_polyline([[0, 1, 2], [0, 2, 3], [2, 1, 4]])
        >>> P.remove_vertex(["0mm", "1mm", "2mm"])

        and including an absolute tolerance when searching for the vertex to be removed:
        >>> P = primitives.draw_polyline([[0, 1, 2], [0, 2, 3], [2, 1, 4]])
        >>> P.remove_vertex(["0mm", "1mm", "2mm"], abstol=1e-6)

        """
        found_vertex = False

        # Search for position in the vertex data
        pos_xyz = self._parent.value_in_object_units(position)
        for ind, vertex_pos in enumerate(self.vertex_positions):
            # compare the specified point with the vertex data using an absolute tolerance
            # (default of math.isclose is 1e-9 which should be ok in almost all cases)
            found_vertex = GeometryOperators.points_distance(vertex_pos, pos_xyz) <= abstol
            if found_vertex:
                if ind == len(self.vertex_positions) - 1:
                    seg_id = ind-1
                    at_start = False
                else:
                    seg_id = ind
                    at_start = True
                break

        assert found_vertex, "Specified vertex {} not found in polyline {}.".format(position, self.name)
        self._parent.oeditor.DeletePolylinePoint(
            [
                "NAME:Delete Point",
                "Selections:=", self.name + ":CreatePolyline:1",
                "Segment Indices:=", [seg_id],
                "At Start:="	, at_start])

        return True

    @aedt_exception_handler
    def remove_edges(self, edge_id):
        """ Remove a vertex from an existing polyline by position

        Removes a vertex from a polyline object. You must enter the exact position of 
        the vertex as a list of [x, y, z] coordinates in the object coordinate system.

        Parameters
        ----------
        edge_id : int or list of int
            One or more edge IDs within the total number of edges within the polyline,
            
        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed. 

        Examples
        --------
        
        >>> P = primitives.draw_polyline([[0, 1, 2], [0, 2, 3], [2, 1, 4]])
        >>> P.remove_edges(edge_id=0)

        """
        if isinstance(edge_id, int):
            edge_id  = [edge_id]
        try:
            self._parent.oeditor.DeletePolylinePoint(
                [
                    "NAME:Delete Point",
                    "Selections:=", self.name + ":CreatePolyline:1",
                    "Segment Indices:=", edge_id,
                    "At Start:="	, True])
        except:
            raise ValueError("Invalid edge ID {} is specified on polyline {}.".format(edge_id, self.name))
        return True

    @aedt_exception_handler
    def set_crosssection_properties(self, type=None, orient=None, width=0, topwidth=0, height=0, num_seg=0, bend_type=None):
        """Set the properties of an existing polyline object.

        Parameters
        ----------
        type : str, optional
            Cross-section type. Choices are ``Line``, ``Circle``, ``Rectangle`` and 
            ``Isosceles Trapezoid``. The default is ``None``.
        orient : str, optional
            Direction of the normal vector to the width of the cross-section. 
            Choices are ``X``, ``Y``, ``Z``, and ``Auto``. The default is ``Auto``.
        width : float or str, optional
           Width or diameter of the cross-section for all types. The default is
           ``0``.
        topwidth : float or str, default=0
           Top width of the cross-section for type ``Isosceles Trapezoid`` only.
           The default is ``0``.
        height : float or str
            Height of the cross-section for type "Rectangle" or "Isosceles 
            Trapezoid" only. The default is ``0``.
        num_seg : int, optional
            Number of segments in the cross-section surface for types ``Circle``, 
            ``Rectangle`` or ``Isosceles Trapezoid``. The default is ``0``. The
            value ust be ``0`` or greater than ``2``.
        bend_type : str, optional
            Type of the bend. The defaut is ``None``, which sets the bend type
            to ``Corner.`` For the type ``Circle,`` the bend type should be 
            set to ``Curved``.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.

        Examples
        --------
        
        >>> P = primitives.draw_polyline([[0, 1, 2], [0, 2, 3], [2, 1, 4]])
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

        model_units = self._parent.model_units

        arg1 = ["NAME:AllTabs"]
        arg2 = ["NAME:Geometry3DCmdTab", ["NAME:PropServers", self.name + ":CreatePolyline:1"]]
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
        self._parent.oeditor.ChangeProperty(arg1)
        objid = self._parent.get_obj_id(self.name)

        # If a cross-section type is defined, specify a solid 3D object
        if type:
            if type == "Line":
                self._parent.objects[objid].object_type = "Sheet"
            else:
                self._parent.objects[objid].is3d = True
                self._parent.objects[objid].object_type = "Solid"

        return True

    @aedt_exception_handler
    def insert_segment(self, position_list, segment=None):
        """Add a segment to an existing polyline.

        Parameters
        ----------
        position_list : list
            List of positions of the points that define the segment to insert. 
            Either the start-point or end-point of the segment list must match 
            one of the vertices of the existing polyline.
        segment: str or PolylineSegment
            Definition of the segment to insert. Valid string values are ``Line`` 
            or ``Arc``. Otherwise use ``PolylineSegment`` to define the segment 
            precicesly for the types ``AngularArc`` or ``Spline``.

        Returns
        ------
        bool
            ``True`` when successful, ``False`` when failed.
        
        """
        name = self._o.name

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
        start_point = self._parent.value_in_object_units(position_list[0])

        # End point does not exist e.g. for an AngularArc
        try:
            end_point = self._parent.value_in_object_units(position_list[num_points-1])
        except:
            end_point = []

        segment_index = 0
        num_vertices = len(self._o.vertices)
        for vertex in self._o.vertices:
            if vertex.position == end_point:
                at_start = True
                break
            elif vertex.position == start_point:
                at_start = False
                if segment_index > 0:
                    segment_index -= 1
                break
            segment_index += 1

        assert segment_index < num_vertices, "Vertex for the insert is not found."
        type = segment.type

        varg1=["NAME:Insert Polyline Segment="]
        varg1.append("Selections:=")
        varg1.append(name +":CreatePolyline:1")
        varg1.append("Segment Indices:=")
        varg1.append([segment_index])
        varg1.append("At Start:=")
        varg1.append(at_start)
        varg1.append("SegmentType:=")
        varg1.append(type)

        # Points and segment data
        varg2 = ["NAME:PolylinePoints"]

        if segment.type == 'Line' or segment.type == 'Spline' or segment.type == 'Arc':
            for pt in position_list[0:num_points]:
                varg2.append(self._pl_point(pt))
            varg1.append(varg2)
        elif segment.type == 'AngularArc':
            seg_str = self._segment_array(segment, start_point=start_point)
            varg2.append(self._pl_point(start_point))
            varg2.append(self._pl_point(segment.extra_points[0]))
            varg2.append(self._pl_point(segment.extra_points[1]))
            varg1.append(varg2)
            varg1 += seg_str[9:]
        self._parent.oeditor.InsertPolylineSegment(varg1)
        #Todo: check this !
        self._parent._update_object(self._o, objtype="Solid")

        return True

class Primitives(object):
    """Primitives class.
    def __init__(self, parent, modeler):
        self._modeler = modeler
        self._parent = parent
        self.objects = defaultdict(Object3d)
        self.objects_names = defaultdict()
        self._currentId = 0
        self.refresh()

    @aedt_exception_handler
    def __getitem__(self, partId):
        """Return the object ``Object3D`` for a given object ID or object name.

        Parameters
        ----------
        partId : int or str
            Object ID or object name from the 3D modeler.

        Returns
        -------
        Object3d

        """
        if isinstance(partId, int) and partId in self.objects:
            return self.objects[partId]
        elif partId in self.objects_names:
            return self.objects[self.objects_names[partId]]
        return None

    @aedt_exception_handler
    def __setitem__(self, partId, partName):
        """Rename an existing part in the 3D modler.

        Parameters
        ----------
        partId : int
            Object ID of the part to rename.

        partName : str
            New name for the part.

        Returns
        -------

        """
        self.objects[partId].name = partName
        return True

    @property
    def oproject(self):
        """ """
        return self._parent.oproject

    @property
    def odesign(self):
        """ """
        return self._parent.odesign

    @property
    def materials(self):
        """ """
        return self._parent.materials

    @property
    def defaultmaterial(self):
        """ """
        return default_materials[self._parent._design_type]

    @property
    def variable_manager(self):
        return self._parent.variable_manager

    @property
    def messenger(self):
        """ """
        return self._parent._messenger

    @property
    def version(self):
        """ """
        return self._parent._aedt_version

    @property
    def modeler(self):
        """ """
        return self._modeler

    @property
    def design_types(self):
        """ """
        return self._parent._modeler

    @property
    def oeditor(self):
        """ """
        return self.modeler.oeditor

    @property
    def model_units(self):
        """ """
        return self.modeler.model_units

    @aedt_exception_handler
    def _delete_object_from_dict(self, objname):
        """Delete object from dictionaries.

        Parameters
        ----------
        objname : int or str
            Object ID or object name from the 3D modeler.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.

        """
        if type(objname) is str and objname in self.objects_names:
            id1 = self.objects_names[objname]
            self.objects_names.pop(objname)
            if id1 in self.objects:
                self.objects.pop(id1)
        elif objname in self.objects:
            name = self.objects[objname].name
            self.objects.pop(objname)
            if name in self.objects_names:
                self.objects_names.pop(name)
        return True

    @aedt_exception_handler
    def _update_object(self, o, objtype="Solid"):
        """

        Parameters
        ----------
        o :

        objtype : str, optional
            The type of object to update. The default is ``Solid``.

        Returns
        -------

        """
        o.object_type = objtype
        if objtype != "Solid":
            o.is3d = False

        # Store the new id in the Object3d object
        o._id = self.oeditor.GetObjectIDByName(o.name)

        # Store the new object infos
        self.objects[o._id] = o
        self.objects_names[o.name] = o._id

        # Cleanup
        if 0 in self.objects:
            del self.objects[0]

        return o._id

    @aedt_exception_handler
    def _check_material(self, matname, defaultmatname):
        """If matname exists it assigns it. Otherwise it assigns the default value.

        Parameters
        ----------
        matname : str
            Name of the material to assign.
        defaultmatname : str
            Name of the default material to assign if ``metname`` does not exist.

        Returns
        -------
        str or bool
            String if a material name, Boolean if the material is a dielectric.

        """

        if matname:
            matname = matname.lower()
            if self._parent.materials.checkifmaterialexists(matname):
                if self._parent._design_type == "HFSS":
                    return matname, self._parent.materials.material_keys[matname].is_dielectric()
                else:
                    return matname, True

            else:
                self.messenger.add_warning_message(
                    "Material {} doesn not exists. Assigning default material".format(matname))
        if self._parent._design_type == "HFSS":
            return defaultmatname, self._parent.materials.material_keys[defaultmatname].is_dielectric()
        else:
            return defaultmatname, True

    @aedt_exception_handler
    def value_in_object_units(self, value):
        '''
            Convert a numerical length string, such as ``10mm`` to a floating point value 
            in the defined object units ``self.object_units``. If a list of such objects is 
            given, convert the entire list.

        Parameters
        ----------
        value : string or list of strings
            Numerical length string to convert.
        
        Returns
        -------
        float or list of floats
        
        '''
        # Convert to a list if a scalar is presented

        scalar = False
        if not isinstance(value, list):
            value = [value]
            scalar = True

        numeric_list = []
        for element in value:
            if isinstance(element, numbers.Number):
                num_val = element
            elif isinstance(element, str):
                # element is an existing variable
                si_value = self._parent.evaluate_expression(element)
                v = Variable("{}meter".format(si_value))
                v.rescale_to(self.model_units)
                num_val = v.numeric_value
            else:
                raise("Inputs to value_in_object_units must be strings or numbers!")

            numeric_list.append(num_val)

        if scalar:
            return numeric_list[0]
        else:
            return numeric_list

    @aedt_exception_handler
    def does_object_exists(self, object):
        """"
        Return True if object exists


        :param object: OBject name or object id
        :return: True
        """
        if type(object) is int:
            if object in self.objects:
                return True
            else:
                return False
        else:
            for el in self.objects:
                if self.objects[el].name == object:
                    return True

        return False

    @aedt_exception_handler
    def create_region(self, pad_percent):
        """Create Air Region

        Parameters
        ----------
        pad_percent : list
            Percent to pad.

        Returns
        -------
        type
            object ID.

        """
        if "Region" in self.get_all_objects_names():
            return None
        id = self._new_id()
        obj = self.objects[id]
        arg = ["NAME:RegionParameters"]
        p = ["+X", "+Y", "+Z", "-X", "-Y", "-Z"]
        i = 0
        for pval in p:
            pvalstr = str(pval) + "PaddingType:="
            qvalstr = str(pval) + "Padding:="
            arg.append(pvalstr)
            arg.append("Percentage Offset")
            arg.append(qvalstr)
            arg.append(str(pad_percent[i]))
            i += 1
        arg2 = ["NAME:Attributes", "Name:=", "Region", "Flags:=", "Wireframe#", "Color:=", "(143 175 143)",
                "Transparency:=", 0, "PartCoordinateSystem:=", "Global", "UDMId:=", "", "Materiaobjidue:=",
                "\"air\"", "SurfaceMateriaobjidue:=", "\"\"", "SolveInside:=", True, "IsMaterialEditable:=", True,
                "UseMaterialAppearance:=", False, "IsLightweight:=", False]
        self.oeditor.CreateRegion(arg, arg2)
        obj.name = "Region"
        obj.solve_inside = True
        obj.transparency = 0
        obj.wireframe = True
        id = self._update_object(obj)
        self.objects[id] = obj
        return id


    @aedt_exception_handler
    def create_object_from_edge(self, edgeID):
        """Create an object from an edge.
        
        Parameters
        ----------
        edgeID: int
            ID of the edge.
            
        Returns
        -------
        
        """

        id = self._new_id()

        o = self.objects[id]

        obj = self._find_object_from_edge_id(edgeID)

        if obj is not None:

            varg1 = ['NAME:Selections']
            varg1.append('Selections:='), varg1.append(obj)
            varg1.append('NewPartsModelFlag:='), varg1.append('Model')

            varg2 = ['NAME:BodyFromEdgeToParameters']
            varg2.append('Edges:='), varg2.append([edgeID])
            o.name = self.oeditor.CreateObjectFromEdges(varg1, ['NAME:Parameters', varg2])[0]
            id = self._update_object(o, "Line")
        return id

    @aedt_exception_handler
    def create_object_from_face(self, faceId):
        """Create an object from a face.

        Parameters
        ----------
        faceId : int
            ID of the face.
        
        Returns
        -------
        
        """
        id = self._new_id()

        o = self.objects[id]

        obj = self._find_object_from_face_id(faceId)

        if obj is not None:

            varg1 = ['NAME:Selections']
            varg1.append('Selections:='), varg1.append(obj)
            varg1.append('NewPartsModelFlag:='), varg1.append('Model')

            varg2 = ['NAME:BodyFromFaceToParameters']
            varg2.append('FacesToDetach:='), varg2.append([faceId])
            o.name = self.oeditor.CreateObjectFromFaces(varg1, ['NAME:Parameters', varg2])[0]
            id = self._update_object(o, "Sheet")
        return id

    @aedt_exception_handler
    def draw_polyline(self, position_list, segment_type=None,
                      cover_surface=False, close_surface=False, name=None,
                      matname=None, xsection_type=None, xsection_orient=None,
                      xsection_width=1, xsection_topwidth=1, xsection_height=1,
                      xsection_num_seg=0, xsection_bend_type=None):
        """Draw a polyline object in the 3D modeler.

        Returns an object of the type ``Polyline``, allowing for manipulation
        of the polyline.

        Parameters
        -------
        position_list : list
            Array of positions of each point of the polyline.
            A position is a list of 2D or 3D coordinates. Position coordinate values
            can be numbers or valid AEDT string expressions. For example, ``[0, 1, 2]`` or 
            ``["0mm", "5mm", "1mm"]`` or ``["x1", "y1"]``.
        segment_type : str or PolylineSegment or list, optional
            The default behavior is to connect all points as ``Line`` segments. The
            default is ``None``. For a string, ``Line`` or ``Arc`` are valid. For a
            ``PolylineSegment``, for ``Line,`` ``Arc``, ``Spline``, or ``AngularArc``,
            a list of segment types (str or PolylineSegment) for a compound polyline.
        cover_surface : bool, optional
            The default is ``False``.
        close_surface : bool, optional
            The default is ``False``, which automatically joins the start and end
            points.
        name: str, optional
            Name of the polyline. The default is ``None``.
        matname: str, optional
            Name of the material. The default is ``None``, which automatically assigns
            a name.
        xsection_type : str, optional
            The cross-section type. Choices are ``"Line"``, ``"Circle"``, ``"Rectangle"``, 
            and ``"Isosceles Trapezoid"``. The default is ``None``.
        xsection_orient : str, optional
            Direction of the normal vector to the width of the cross-section.
            Choices are "X", "Y", "Z", or "Auto. The default is ``None``, which 
            sets the direction to ``Auto``.
        xsection_width : float or str, optional
            The width or diamater of the cross-section for all  types. The 
            default is ``1``.
        xsection_topwidth : float or str, optional
            Top width of the cross-section for type ``"Isosceles Trapezoid"`` only.
            The default is ``1``.
        xsection_height : float or str
            Height of the cross-section for type ``"Rectangle"`` or ``"Isosceles 
            Trapezoid"`` only. The default is ``1``.
        xsection_num_seg : int, optional
            Number of segments in the cross-section surface for types ``"Circle"``, 
            ``"Rectangle"``, or ``"Isosceles Trapezoid"``. The default is ``0``. The
            value must be ``0`` or greater than ``2``.
        xsection_bend_type : str, optional
            Type of the cross-section bend. The defaut is ``None``, which sets the bend type
            to ``Corner.`` For the type ``Circle,`` the bend type should be 
            set to ``Curved``.
        
        Returns
        -------
        Polyline
            Object with additional methods for manipulating the polyline e.g. insert_segment. The object-id of the
            created polyline can be accessed via ``Polyline.id``.

        Examples
        -------
        
        Set up the desktop environment
        
        >>> from pyaedt.desktop import Desktop
        >>> from pyaedt.Maxwell import Maxwell3d
        >>> from pyaedt.modeler.Primitives import PolylineSegment
        >>> desktop=Desktop(specified_version="2021.1", AlwaysNew=False)
        >>> aedtapp = Maxwell3D()
        >>> aedtapp.modeler.model_units = "mm"
        >>> primitives = aedtapp.modeler.primitives

        Define some test data points.
        
        >>> test_points = [["0mm", "0mm", "0mm"], ["100mm", "20mm", "0mm"],
        ...                ["71mm", "71mm", "0mm"], ["0mm", "100mm", "0mm"]]

        Default behaviour assumes that all points are to be connected by line segments. Optionally specify the name.
        
        >>> P1 = primitives.draw_polyline(test_points, name="PL_line_segments")

        Specify that the first segment is a line and the last three points define a 3-point arc.
        
        >>> P2 = primitives.draw_polyline(test_points, segment_type=["Line", "Arc"], name="PL_line_plus_arc")

        Redraw the 3-point arc alone from the last three points and additionally specify five segments 
        using ``PolylineSegment``.
        
        >>> P3 = primitives.draw_polyline(test_points[1:],
        ...                          segment_type=PolylineSegment(type="Arc", num_seg=7),
        ...                          name = "PL_segmented_arc")

        Specify that the four points form a spline and add a circular cross-section of diameter 1mm.
        
        >>> P4 = primitives.draw_polyline(test_points, segment_type="Spline", name="PL_spline",
        ...                          xsection_type="Circle", xsection_width="1mm")

        Now use the ``PolylineSegment`` object to specify more detail about the individual segments.
        Create a center-point arc starting from the position test_points[1], rotating about the
        center-point position test_points[0] in the XY plane.
        
        >>> start_point = test_points[1]
        >>> center_point = test_points[0]
        >>> segment_def = PolylineSegment(type="AngularArc", arc_center=center_point, arc_angle="90deg", arc_plane="XY")
        >>> primitives.draw_polyline(start_point, segment_type=segment_def, name="PL_center_point_arc")

        """
        new_polyline = Polyline(parent=self, position_list=position_list, segment_type=segment_type,
                                cover_surface=cover_surface, close_surface=close_surface, name=name,
                                matname=matname, xsection_type=xsection_type, xsection_orient=xsection_orient,
                                xsection_width=xsection_width, xsection_topwidth=xsection_topwidth, xsection_height=xsection_height,
                                xsection_num_seg=xsection_num_seg, xsection_bend_type=xsection_bend_type)
        return new_polyline

    @aedt_exception_handler
    def get_existing_polyline(self, object_id):
        """Retrieve a polyline object to manipulate it.

        Parameters
        ----------
        object_id : int
            Integer object id of an existing polyline object in the 3D modeler.

        Returns
        -------
        Polyline

        """
        return Polyline(self, object_id=object_id)

    @aedt_exception_handler
    def create_udp(self, udp_dll_name, udp_parameters_list, upd_library='syslib', name=None, udptye="Solid"):
        """Create user-defined primitive.

        Parameters
        ----------
        udp_dll_name :
            dll name
        udp_parameters_list :
            udp pairs object
        upd_library :
            udp library (Default value = 'syslib')
        name :
            component name (Default value = None)
        udptye :
            udpy type (Default value = "Solid")

        Returns
        -------
        type
            object ID

        """
        id = self._new_id()

        o = self.objects[id]
        if ".dll" not in udp_dll_name:
            vArg1 = ["NAME:UserDefinedPrimitiveParameters", "DllName:=", udp_dll_name + ".dll", "Library:=", upd_library]
        else:
            vArg1 = ["NAME:UserDefinedPrimitiveParameters", "DllName:=", udp_dll_name, "Library:=", upd_library]

        vArgParamVector = ["NAME:ParamVector"]

        for pair in udp_parameters_list:
            if type(pair) is list:
                vArgParamVector.append(["NAME:Pair", "Name:=", pair[0], "Value:=", pair[1]])

            else:
                vArgParamVector.append(["NAME:Pair", "Name:=", pair.Name, "Value:=", pair.Value])

        vArg1.append(vArgParamVector)
        namergs = name.replace(".dll", "").split("/")
        o.name = name
        vArg2 = o.export_attributes(namergs[-1])
        self.oeditor.CreateUserDefinedPart(vArg1, vArg2)
        id = self._update_object(o, udptye)
        return id


    @aedt_exception_handler
    def get_obj_name(self, partId):
        """Return object name from ID

        Parameters
        ----------
        partId :
            object id

        Returns
        -------

        """
        return self.objects[partId].name

    @aedt_exception_handler
    def convert_to_selections(self, objtosplit, return_list=False):
        """

        Parameters
        ----------
        objtosplit :
            list of objects to convert to selection. it can be a string, int or list of mixed.
        return_list :
            Bool. if False it returns a string of the selections. if True it return the list (Default value = False)

        Returns
        -------
        type
            objectname in a form of list of string

        """
        if type(objtosplit) is not list:
            objtosplit = [objtosplit]
        objnames = []
        for el in objtosplit:
            if type(el) is int and el in list(self.objects.keys()):
                objnames.append(self.get_obj_name(el))
            else:
                objnames.append(el)
        if return_list:
            return objnames
        else:
            return ",".join(objnames)

    @aedt_exception_handler
    def delete(self, objects):
        """deletes objects or groups

        Parameters
        ----------
        objects :
            list of objects or group names

        Returns
        -------
        type
            True if succeeded, False otherwise

        """
        if type(objects) is not list:
            objects = [objects]

        while len(objects) > 100:
            objs = objects[:100]
            objects_str = self.convert_to_selections(objs, return_list=False)
            arg = [
                "NAME:Selections",
                "Selections:="	, objects_str
                ]
            self.oeditor.Delete(arg)
            for el in objs:
                self._delete_object_from_dict(el)


            objects = objects[100:]

        objects_str = self.convert_to_selections(objects, return_list=False)
        arg = [
            "NAME:Selections",
            "Selections:="	, objects_str
            ]
        self.oeditor.Delete(arg)

        for el in objects:
            self._delete_object_from_dict(el)

        if len(objects) > 0:
            self.messenger.add_info_message("Deleted {} Objects".format(len(objects)))

        return True

    @aedt_exception_handler
    def delete_objects_containing(self, contained_string, case_sensitive=True):
        """Delete all objects with predefined prefix

        Parameters
        ----------
        contained_string :
            string
        case_sensitive :
            Boolean (Default value = True)

        Returns
        -------
        type
            Boolean

        """
        objnames = self.get_all_objects_names()
        num_del = 0
        for el in objnames:
            if case_sensitive:
                if contained_string in el:
                    self.delete(el)
                    num_del += 1
            else:
                if contained_string.lower() in el.lower():
                    self.delete(el)
                    num_del += 1
        self.messenger.add_info_message("Deleted {} objects".format(num_del))
        return True

    @aedt_exception_handler
    def get_model_bounding_box(self):
        """GetModelBoundingbox and return it"""
        bound = []
        if self.oeditor is not None:
            bound = self.oeditor.GetModelBoundingBox()
        return bound

    @aedt_exception_handler
    def get_obj_id(self, objname):
        """Return object ID from name

        Parameters
        ----------
        partId :
            object name
        objname :


        Returns
        -------
        type
            object id

        """
        if objname in self.objects_names:
            if self.objects_names[objname] in self.objects:
                return self.objects_names[objname]
        return None

    @aedt_exception_handler
    def get_objects_w_string(self, stringname, case_sensitive=True):
        """Return all objects name of objects containing stringname

        Parameters
        ----------
        stringname :
            object string to be searched in object names
        case_sensitive :
            Boolean (Default value = True)

        Returns
        -------
        type
            objects lists of strings

        """
        list_objs=[]
        for el in self.objects:
            if case_sensitive:
                if stringname in self.objects[el].name:
                    list_objs.append(self.objects[el].name)
            else:
                if stringname.lower() in self.objects[el].name.lower():
                    list_objs.append(self.objects[el].name)

        return list_objs

    @aedt_exception_handler
    def get_model_objects(self, model=True):
        """Return all objects name of Model objects

        Parameters
        ----------
        model :
            bool True to return model objects. False to return Non-Model objects (Default value = True)

        Returns
        -------
        type
            objects lists

        """
        list_objs = []
        for el in self.objects:
            if self.objects[el].model==model:
                list_objs.append(self.objects[el].name)
        return list_objs

    @aedt_exception_handler
    def refresh(self):
        """Refresh all ids"""
        self.refresh_all_ids_from_aedt_file()
        if not self.objects:
            self.refresh_all_ids()

    @aedt_exception_handler
    def refresh_all_ids(self):
        """Refresh all ids"""
        n = 10
        #self.objects = defaultdict(Object3d)
        all_object_names = self.get_all_objects_names()
        try:
            obj = list(self.oeditor.GetObjectsInGroup("Solids"))
        except:
            obj = []
        for el in obj:
            if el not in all_object_names:
                o = Object3d(self)
                o.name = el
                o.is3d = True
                o.object_type = "Solid"
                o_updated = self.update_object_properties(o)
                self._update_object(o_updated)
        try:
            sheets = list(self.oeditor.GetObjectsInGroup("Sheets"))
        except:
            sheets = []
        for el in sheets:
            if el not in all_object_names:
                o = Object3d(self)
                o.name = el
                o.is3d = False
                o.object_type = "Sheet"
                o_updated = self.update_object_properties(o)
                self._update_object(o_updated, "Sheet")

        try:
            lines = list(self.oeditor.GetObjectsInGroup("Lines"))
        except:
            lines = []
        for el in lines:
            if el not in all_object_names:
                o = Object3d(self)
                o.name = el
                o.is3d = False
                o.object_type = "Line"
                o_updated = self.update_object_properties(o)
                self._update_object(o_updated, "Line")
        all_objs = obj+sheets+lines
        for el in all_object_names:
            if el not in all_objs:
                self._delete_object_from_dict(el)
        return len(self.objects)

    @aedt_exception_handler
    def refresh_all_ids_from_aedt_file(self):
        """Refresh all ids from aedt_file properties. This method is much faster than the original refresh_all_ids method


        :return: length of imported objects

        Parameters
        ----------

        Returns
        -------

        """
        if not self._parent.design_properties or "ModelSetup" not in self._parent.design_properties:
            return 0
        solids = list(self.oeditor.GetObjectsInGroup("Solids"))
        sheets = list(self.oeditor.GetObjectsInGroup("Sheets"))
        try:
            groups = self._parent.design_properties['ModelSetup']['GeometryCore']['GeometryOperations']['Groups'][
                'Group']
        except:
            groups = []
        if type(groups) is not list:
            groups = [groups]
        try:
            self._parent.design_properties['ModelSetup']['GeometryCore']['GeometryOperations']['ToplevelParts'][
                'GeometryPart']
        except:
            return 0
        for el in self._parent.design_properties['ModelSetup']['GeometryCore']['GeometryOperations']['ToplevelParts']['GeometryPart']:
            try:
                attribs = el['Attributes']
                o = Object3d(self)
                try:
                    objID = el['Operations']['Operation']['ID']
                except:
                    objID = el['Operations']['Operation'][0]['ParentPartID']
                o.name = attribs['Name']
                if o.name in solids:
                    o.is3d = True
                    o.object_type = "Solid"
                elif o.name in sheets:
                    o.is3d = False
                    o.object_type = "Sheet"
                else:
                    o.is3d = False
                    o.object_type = "Line"
                o.solve_inside = attribs['SolveInside']
                o.material_name = attribs['MaterialValue'][1:-1]
                o.part_coordinate_system = attribs['PartCoordinateSystem']
                if "NonModel" in attribs['Flags']:
                    o.model = False
                else:
                    o.model = True
                if "Wireframe" in attribs['Flags']:
                    o.wireframe = True
                else:
                    o.wireframe = False
                groupname = ""
                for group in groups:
                    if attribs['GroupId'] == group['GroupID']:
                        groupname = group['Attributes']['Name']

                o._m_groupName = groupname
                o.color = attribs['Color']
                o.m_surfacematerial = attribs['SurfaceMaterialValue']
                self.objects[objID] = o
                self.objects_names[o.name] = objID
            except:
                pass
        return len(self.objects)

    @aedt_exception_handler
    def update_object_properties(self, o):
        """

        Parameters
        ----------
        o :
            return:

        Returns
        -------

        """
        n = 10
        name = o.name
        all_prop = retry_ntimes(n, self.oeditor.GetProperties, "Geometry3DAttributeTab", name)
        if 'Solve Inside' in all_prop:
            solveinside = retry_ntimes(n, self.oeditor.GetPropertyValue, "Geometry3DAttributeTab", name, 'Solve Inside')
            if solveinside == 'false' or solveinside == 'False':
                o.solve_inside = False
        if 'Material' in all_prop:
            mat = retry_ntimes(n, self.oeditor.GetPropertyValue, "Geometry3DAttributeTab", name, 'Material')
            if mat:
                o.material_name = mat[1:-1].lower()
            else:
                o.material_name = ''
        if 'Orientation' in all_prop:
            o.part_coordinate_system = retry_ntimes(n, self.oeditor.GetPropertyValue,
                                                    "Geometry3DAttributeTab", name, 'Orientation')
        if 'Model' in all_prop:
            mod = retry_ntimes(n, self.oeditor.GetPropertyValue, "Geometry3DAttributeTab", name, 'Model')
            if mod == 'false' or mod == 'False':
                o.model = False
            else:
                o.model = True
        if 'Group' in all_prop:
            o.m_groupName = retry_ntimes(n, self.oeditor.GetPropertyValue, "Geometry3DAttributeTab", name, 'Group')
        if 'Display Wireframe' in all_prop:
            wireframe = retry_ntimes(n, self.oeditor.GetPropertyValue,
                                     "Geometry3DAttributeTab", name, 'Display Wireframe')
            if wireframe == 'true' or wireframe == 'True':
                o.wireframe = True
        if 'Transparent' in all_prop:
            transp = retry_ntimes(n, self.oeditor.GetPropertyValue, "Geometry3DAttributeTab", name, 'Transparent')
            try:
                o.transparency = float(transp)
            except:
                o.transparency = 0.3
        if 'Color' in all_prop:
            color = int(retry_ntimes(n, self.oeditor.GetPropertyValue, "Geometry3DAttributeTab", name, 'Color'))
            if color:
                r = (color >> 16) & 255
                g = (color >> 8) & 255
                b = color & 255
                o.color = "(" + str(r) + " " + str(g) + " " + str(b) + ")"
            else:
                o.color = "(0 195 255)"
        if 'Surface Material' in all_prop:
            o.m_surfacematerial = retry_ntimes(n, self.oeditor.GetPropertyValue,
                                               "Geometry3DAttributeTab", name, 'Surface Material')
        return o

    @aedt_exception_handler
    def get_all_objects_names(self, refresh_list=False, get_solids=True, get_sheets=True, get_lines=True):
        """Get all objects names in the design

        Parameters
        ----------
        refresh_list :
            bool, force the refresh of objects (Default value = False)
        get_solids :
            bool, include the solids in the return list (Default value = True)
        get_sheets :
            bool, include the sheets in the return list (Default value = True)
        get_lines :
            bool, include the lines in the return list (Default value = True)

        Returns
        -------
        type
            list of the objects names

        """
        if refresh_list:
            l = self.refresh_all_ids()
            self.messenger.add_info_message("Found " + str(l) + " Objects")
        obj_names = []
        if get_lines and get_sheets and get_solids:
            return [i for i in list(self.objects_names.keys())]

        for el in self.objects:
            if (self.objects[el].object_type == "Solid" and get_solids) or (
                    self.objects[el].object_type == "Sheet" and get_sheets) or (
                    self.objects[el].object_type == "Line" and get_lines):
                obj_names.append(self.objects[el].name)
        return obj_names

    @aedt_exception_handler
    def get_all_sheets_names(self, refresh_list=False):
        """get all sheets names in the design

        Parameters
        ----------
        refresh_list :
            bool, force the refresh of objects (Default value = False)

        Returns
        -------
        type
            list of the sheets names

        """
        return self.get_all_objects_names(refresh_list=refresh_list, get_solids=False, get_sheets=True, get_lines=False)

    @aedt_exception_handler
    def get_all_lines_names(self, refresh_list=False):
        """get all lines names in the design

        Parameters
        ----------
        refresh_list :
            bool, force the refresh of objects (Default value = False)

        Returns
        -------
        type
            list of the lines names

        """
        return self.get_all_objects_names(refresh_list=refresh_list, get_solids=False, get_sheets=False, get_lines=True)

    @aedt_exception_handler
    def get_objects_by_material(self, materialname):
        """Get objects ID list of specified material

        Parameters
        ----------
        materialname :
            str material name

        Returns
        -------

        """
        obj_lst = []
        for el in self.objects:
            if self.objects[el].material_name == materialname or self.objects[el].material_name == '"'+ materialname +'"':
                obj_lst.append(el)
        return obj_lst

    @aedt_exception_handler
    def get_all_objects_ids(self):
        """Get all object ids


        :return: obj id list
        """
        objs = []
        for el in self.objects:
            objs.append(el)
        return objs

    @aedt_exception_handler
    def request_new_object(self, matname=None):
        """

        Parameters
        ----------
        matname : str
        Name of the material of the new component

        Returns
        -------
        Object3d
        """
        id = self._new_id()
        o = self.objects[id]
        o.material_name, o.solve_inside = self._check_material(matname, o.material_name)
        return o

    @aedt_exception_handler
    def _new_id(self):
        """ """
        # self._currentId = self._currentId + 1
        o = Object3d(self)
        o.material_name = self.defaultmaterial
        self._currentId = 0
        self.objects[self._currentId] = o
        return self._currentId

    @aedt_exception_handler
    def set_part_name(self, partName, partId):
        """Set Part name value

        Parameters
        ----------
        partName :
            part name
        partId :
            part id

        Returns
        -------

        """
        o = self.objects[partId]
        o.set_name(partName)
        o.name = partName

    @aedt_exception_handler
    def get_part_name(self, partId):
        """Get Part name


        :return: part name

        Parameters
        ----------
        partId :


        Returns
        -------

        """
        o = self.objects[partId]
        return o.name

    @aedt_exception_handler
    def set_material_name(self, matName, partId):
        """Set Material name

        Parameters
        ----------
        matName :
            material name
        partId :
            part id

        Returns
        -------

        """
        o = self.objects[partId]
        o.assign_material(matName)

    @aedt_exception_handler
    def set_part_color(self, partId, color):
        """Set Part Color

        Parameters
        ----------
        partId :
            part id
        color :
            part color as hex number

        Returns
        -------

        """
        # Convert long color to RGB
        rgb = (color // 256 // 256 % 256, color // 256 % 256, color % 256)
        self.set_color(rgb[0], rgb[1], rgb[2], partId)

    @aedt_exception_handler
    def set_color(self, r, g, b, partId):
        """Set Part Color from r g b

        Parameters
        ----------
        partId :
            part id
        r :
            part color red
        g :
            part color green
        b :
            part color blue

        Returns
        -------

        """
        o = self.objects[partId]
        o.set_color(r, g, b)

    @aedt_exception_handler
    def set_wireframe(self, partId, fWire):
        """Set Part wireframe

        Parameters
        ----------
        partId :
            part id
        fWire :
            boolean

        Returns
        -------

        """
        o = self.objects[partId]
        o.display_wireframe(fWire)

    @aedt_exception_handler
    def set_part_refid(self, partId, refId):
        """

        Parameters
        ----------
        partId :

        refId :


        Returns
        -------

        """
        o = self.objects[partId]
        o.m_refId = refId

    # @aedt_exception_handler
    # def get_objname_from_id(self, partId):
    #     """
    #
    #     :param partId: Object ID
    #     :return: Object name
    #     """
    #
    #     if type(partId) is str:
    #         if not self.objects:
    #             self.refresh()
    #         for el in self.objects:
    #             if self.objects[el].name == partId:
    #                 partId = el
    #     return partId

    @aedt_exception_handler
    def find_closest_edges(self, start_obj, end_obj, port_direction=0):
        """Given two objects the tool will check and provide the two closest edges that are not perpendicular.
        PortDirection is used in case more than 2 couple are on the same distance (eg. coax or microstrip). in that case
        it will give the precedence to the edges that are on that axis direction (eg XNeg)

        Parameters
        ----------
        start_obj :
            Start objectName
        end_obj :
            End Object Name
        port_direction :
            AxisDir.XNeg,AxisDir.XPos, AxisDir.YNeg,AxisDir.YPos, AxisDir.ZNeg,AxisDir.ZPos, (Default value = 0)

        Returns
        -------
        type
            list with 2 edges if present

        """
        if not self.does_object_exists(start_obj):
            self.messenger.add_error_message("Error. Object {} does not exists".format(str(start_obj)))
            return False
        if not self.does_object_exists(end_obj):
            self.messenger.add_error_message("Error. Object {} does not exists".format(str(end_obj)))
            return False
        edge_start_list = self.modeler.primitives.get_object_edges(start_obj)
        edge_stop_list = self.modeler.primitives.get_object_edges(end_obj)
        mindist = 1e6
        tol = 1e-12
        pos_tol = 1e-6
        edge_list = []
        actual_point = None
        is_parallel = False
        for el in edge_start_list:
            vertices_i = self.get_edge_vertices(el)
            vertex1_i = None
            vertex2_i = None
            if len(vertices_i) == 2:  # normal segment edge
                vertex1_i = self.get_vertex_position(vertices_i[0])
                vertex2_i = self.get_vertex_position(vertices_i[1])
                start_midpoint = GeometryOperators.get_mid_point(vertex1_i, vertex2_i)
            elif len(vertices_i) == 1:
                start_midpoint = self.get_vertex_position(vertices_i[0])
            else:
                continue
            for el1 in edge_stop_list:
                vertices_j = self.get_edge_vertices(el1)
                vertex1_j = None
                vertex2_j = None
                if len(vertices_j) == 2:  # normal segment edge
                    vertex1_j = self.get_vertex_position(vertices_j[0])
                    vertex2_j = self.get_vertex_position(vertices_j[1])
                    end_midpoint = GeometryOperators.get_mid_point(vertex1_j, vertex2_j)
                elif len(vertices_j) == 1:
                    end_midpoint = self.get_vertex_position(vertices_j[0])
                else:
                    continue

                parallel_edges = False
                vect = None
                if vertex1_i and vertex1_j:
                    if abs(GeometryOperators._v_dot(GeometryOperators.v_points(vertex1_i, vertex2_i), GeometryOperators.v_points(vertex1_j, vertex2_j))) < tol:
                        continue  #skip perperndicular edges
                    if GeometryOperators.is_parallel(vertex1_i, vertex2_i, vertex1_j, vertex2_j):
                        parallel_edges = True
                    vert_dist_sum = GeometryOperators.arrays_positions_sum([vertex1_i, vertex2_i], [vertex1_j, vertex2_j])
                    vect = GeometryOperators.distance_vector(start_midpoint, vertex1_j, vertex2_j)
                else:
                    vert_dist_sum = GeometryOperators.arrays_positions_sum([start_midpoint], [end_midpoint])

                # dist = abs(_v_norm(vect))

                if parallel_edges:
                    pd1=GeometryOperators.points_distance(vertex1_i, vertex2_i)
                    pd2=GeometryOperators.points_distance(vertex1_j, vertex2_j)

                    if pd1 < pd2 and not GeometryOperators.is_projection_inside(vertex1_i, vertex2_i, vertex1_j, vertex2_j):
                        continue
                    elif pd1 >= pd2 and not GeometryOperators.is_projection_inside(vertex1_j, vertex2_j, vertex1_i, vertex2_i):
                        continue
                # if GeometryOperators.is_between_points(end_midpoint, vertex1_i,
                #                                        vertex1_j) or GeometryOperators.is_between_points(start_midpoint,
                #                                                                                          vertex2_i,
                #                                                                                          vertex2_j):
                #     continue
                if actual_point is None:
                    edge_list = [el, el1]
                    is_parallel = parallel_edges
                    actual_point = GeometryOperators.find_point_on_plane([start_midpoint, end_midpoint], port_direction)
                    mindist = vert_dist_sum
                else:
                    new_point = GeometryOperators.find_point_on_plane([start_midpoint, end_midpoint], port_direction)
                    if (port_direction <= 2 and new_point - actual_point < 0) or (port_direction > 2 and actual_point - new_point < 0):
                        edge_list = [el, el1]
                        is_parallel = parallel_edges
                        actual_point = new_point
                        mindist = vert_dist_sum
                    elif port_direction <= 2 and new_point - actual_point < tol and vert_dist_sum - mindist < pos_tol:
                            edge_list = [el, el1]
                            is_parallel = parallel_edges
                            actual_point = new_point
                            mindist = vert_dist_sum
                    elif port_direction > 2 and actual_point - new_point < tol and vert_dist_sum - mindist < pos_tol:
                        edge_list = [el, el1]
                        is_parallel = parallel_edges
                        actual_point = new_point
                        mindist = vert_dist_sum
        return edge_list, is_parallel

    @aedt_exception_handler
    def get_equivalent_parallel_edges(self, edgelist, portonplane=True, axisdir=0, startobj="", endobject=""):
        """Given a parallel couple of edges it creates 2 new edges that are pallel and are equal to the smallest edge

        Parameters
        ----------
        edgelist :
            List with 2 parallel edge
        portonplane :
            Boolean, if True, Edges will be on plane ortogonal to axisdir (Default value = True)
        axisdir :
            Axis Direction (Default value = 0)
        startobj :
             (Default value = "")
        endobject :
             (Default value = "")

        Returns
        -------
        type
            list of the two new created edges

        """
        try:
            l1 = self.get_edge_length(edgelist[0])
            l2 = self.get_edge_length(edgelist[1])
        except:
            return None
        if l1 < l2:
            orig_edge = edgelist[0]
            dest_edge = edgelist[1]
        else:
            orig_edge = edgelist[1]
            dest_edge = edgelist[0]

        first_edge = self.create_object_from_edge(orig_edge)
        second_edge = self.create_object_from_edge(orig_edge)
        ver1 = self.get_edge_vertices(orig_edge)
        ver2 = self.get_edge_vertices(dest_edge)
        if len(ver2) < 2:
            self.delete(first_edge)
            self.delete(second_edge)
            return False
        p = self.get_vertex_position(ver1[0])
        a1 = self.get_vertex_position(ver2[0])
        a2 = self.get_vertex_position(ver2[1])

        vect = GeometryOperators.distance_vector(p, a1, a2)

        #vect = self.modeler.Position([i for i in d])
        if portonplane:
            vect[divmod(axisdir, 3)[1]] = 0
        self.modeler.translate(second_edge, vect)
        ver_check = self.get_object_vertices(second_edge)
        p_check = self.get_vertex_position(ver_check[0])
        obj_check =self.get_bodynames_from_position(p_check)
        p_check2 = self.get_vertex_position(ver_check[1])
        obj_check2 = self.get_bodynames_from_position(p_check2)
        if (startobj in obj_check or endobject in obj_check) and (startobj in obj_check2 or endobject in obj_check2):
            if l1<l2:
                return [first_edge, second_edge]
            else:
                return [second_edge,first_edge]
        else:
            self.delete(second_edge)
            self.delete(first_edge)
            return None

    @aedt_exception_handler
    def get_object_faces(self, partId):
        """Get the face IDs of given an object name

        Parameters
        ----------
        partId :
            part ID (integer) or objectName (string)

        Returns
        -------
        type
            Faces ID List

        """
        oFaceIDs = []
        if type(partId) is str and partId in self.objects_names:
            oFaceIDs = self.oeditor.GetFaceIDs(partId)
            oFaceIDs = [int(i) for i in oFaceIDs]
        elif partId in self.objects:
            o = self.objects[partId]
            name = o.name
            oFaceIDs = self.oeditor.GetFaceIDs(name)
            oFaceIDs = [int(i) for i in oFaceIDs]
        return oFaceIDs

    @aedt_exception_handler
    def get_object_edges(self, partId):
        """Get the edge IDs of given an object name or object ID

        Parameters
        ----------
        partId :
            part ID (integer) or objectName (string)

        Returns
        -------
        type
            Edge ID List

        """
        oEdgeIDs = []
        if type(partId) is str and partId in self.objects_names:
            oEdgeIDs = self.oeditor.GetEdgeIDsFromObject(partId)
            oEdgeIDs = [int(i) for i in oEdgeIDs]
        elif partId in self.objects:
            o = self.objects[partId]
            oEdgeIDs = self.oeditor.GetEdgeIDsFromObject(o.name)
            oEdgeIDs = [int(i) for i in oEdgeIDs]
        return oEdgeIDs

    @aedt_exception_handler
    def get_face_edges(self, partId):
        """Get the edge IDs of given an face name or object ID

        Parameters
        ----------
        partId :
            part ID (integer) or objectName (string)

        Returns
        -------
        type
            Edge ID List

        """
        oEdgeIDs = self.oeditor.GetEdgeIDsFromFace(partId)
        oEdgeIDs = [int(i) for i in oEdgeIDs]
        return oEdgeIDs

    @aedt_exception_handler
    def get_object_vertices(self, partID):
        """Get the vertex IDs of given an object name or object ID.

        Parameters
        ----------
        partID :
            part ID (integer) or objectName (string)

        Returns
        -------
        type
            Vertex ID List

        """
        oVertexIDs = []
        if type(partID) is str and partID in self.objects_names:
            oVertexIDs = self.oeditor.GetVertexIDsFromObject(partID)
            oVertexIDs = [int(i) for i in oVertexIDs]
        elif partID in self.objects:
            o = self.objects[partID]
            oVertexIDs = self.oeditor.GetVertexIDsFromObject(o.name)
            oVertexIDs = [int(i) for i in oVertexIDs]
        return oVertexIDs

    @aedt_exception_handler
    def get_face_vertices(self, face_id):
        """Get the vertex IDs of given a face ID.

        Parameters
        ----------
        face_id :
            part ID (integer). If objectName (string) is available then use get_object_vertices

        Returns
        -------
        type
            Vertex ID List

        """
        try:
            oVertexIDs = self.oeditor.GetVertexIDsFromFace(face_id)
        except:
            oVertexIDs = []
        else:
            oVertexIDs = [int(i) for i in oVertexIDs]
        return oVertexIDs

    @aedt_exception_handler
    def get_edge_length(self, edgeID):
        """

        Parameters
        ----------
        edgeID :
            Edge id

        Returns
        -------
        type
            Edge length

        """
        vertexID = self.get_edge_vertices(edgeID)
        pos1 = self.get_vertex_position(vertexID[0])
        if len(vertexID) < 2:
            return 0
        pos2 = self.get_vertex_position(vertexID[1])
        length = GeometryOperators.points_distance(pos1, pos2)
        return length

    @aedt_exception_handler
    def get_edge_vertices(self, edgeID):
        """Get the vertex IDs of given a edge ID.

        Parameters
        ----------
        edgeID :
            part ID (integer). If objectName (string) is available then use get_object_vertices

        Returns
        -------
        type
            Vertex ID List

        """
        try:
            oVertexIDs = self.oeditor.GetVertexIDsFromEdge(edgeID)
        except:
            oVertexIDs = []
        else:
            oVertexIDs = [int(i) for i in oVertexIDs]
        return oVertexIDs

    @aedt_exception_handler
    def get_vertex_position(self, vertex_id):
        """Returns a vector of vertex coordinates.

        Parameters
        ----------
        vertex_id :
            vertex ID (integer or str)

        Returns
        -------
        type
            position as list of float [x, y, z]

        """
        try:
            pos = self.oeditor.GetVertexPosition(vertex_id)
        except:
            position = []
        else:
            position = [float(i) for i in pos]
        return position

    @aedt_exception_handler
    def get_face_area(self, face_id):
        """Get area of given face ID.

        Parameters
        ----------
        face_id :
            Face ID

        Returns
        -------
        type
            float value for face area

        """

        area = self.oeditor.GetFaceArea(face_id)
        return area

    @aedt_exception_handler
    def get_face_center(self, face_id):
        """Given a planar face ID, return the center position.

        Parameters
        ----------
        face_id :
            Face ID

        Returns
        -------
        list
            An array as list of float [x, y, z] containing planar face center position

        """
        if not self.objects:
            self.refresh_all_ids()

        try:
            c = self.oeditor.GetFaceCenter(face_id)
        except:
            self.messenger.add_warning_message("Non Planar Faces doesn't provide any Face Center")
            return False
        center = [float(i) for i in c]
        return center

    @aedt_exception_handler
    def get_mid_points_on_dir(self, sheet, axisdir):
        """

        Parameters
        ----------
        sheet :

        axisdir :


        Returns
        -------

        """
        edgesid = self.get_object_edges(sheet)
        id =divmod(axisdir,3)[1]
        midpoint_array = []
        for ed in edgesid:
            midpoint_array.append(self.get_edge_midpoint(ed))
        point0=[]
        point1=[]
        for el in midpoint_array:
            if not point0:
                point0 = el
                point1 = el
            elif axisdir < 3 and el[id] < point0[id] or axisdir > 2 and el[id] > point0[id]:
                point0 = el
            elif axisdir < 3 and el[id] > point1[id] or axisdir > 2 and el[id] < point1[id]:
                point1 = el
        return point0, point1

    @aedt_exception_handler
    def get_edge_midpoint(self, partID):
        """Get the midpoint coordinates of given edge name or edge ID


        If the edge is not a segment with two vertices return an empty list.

        Parameters
        ----------
        partID :
            part ID (integer) or objectName (string)

        Returns
        -------
        type
            midpoint coordinates

        """

        if type(partID) is str and partID in self.objects_names:
            partID = self.objects_names[partID]

        if partID in self.objects and self.objects[partID].object_type == "Line":
            vertices = self.get_object_vertices(partID)
        else:
            try:
                vertices = self.get_edge_vertices(partID)
            except:
                vertices = []
        if len(vertices) == 2:
            vertex1 = self.get_vertex_position(vertices[0])
            vertex2 = self.get_vertex_position(vertices[1])
            midpoint = GeometryOperators.get_mid_point(vertex1, vertex2)
            return list(midpoint)
        elif len(vertices) == 1:
            return list(self.get_vertex_position(vertices[0]))
        else:
            return []

    @aedt_exception_handler
    def get_bodynames_from_position(self, position, units=None):
        """Gets the object names that contact the given point

        Parameters
        ----------
        position :
            ApplicationName.modeler.Position(x,y,z) object
        units :
            units (e.g. 'm'), if None model units is used (Default value = None)

        Returns
        -------
        type
            The list of object names

        """
        XCenter, YCenter, ZCenter = self.pos_with_arg(position, units)
        vArg1 = ['NAME:Parameters']
        vArg1.append('XPosition:='), vArg1.append(XCenter)
        vArg1.append('YPosition:='), vArg1.append(YCenter)
        vArg1.append('ZPosition:='), vArg1.append(ZCenter)

        list_of_bodies = list(self.oeditor.GetBodyNamesByPosition(vArg1))
        return list_of_bodies

    @aedt_exception_handler
    def get_edgeid_from_position(self, position, obj_name=None, units=None):
        """

        Parameters
        ----------
        position :
            ApplicationName.modeler.Position(x,y,z) object
        obj_name :
            optional object name. Otherwise it will search in all objects (Default value = None)
        units :
            units (e.g. 'm'), if None model units is used (Default value = None)

        Returns
        -------
        type
            Edge ID of first object touching that position

        """
        edgeID = -1
        XCenter, YCenter, ZCenter = self.pos_with_arg(position, units)

        vArg1 = ['NAME:EdgeParameters']
        vArg1.append('BodyName:='), vArg1.append('')
        vArg1.append('XPosition:='), vArg1.append(XCenter)
        vArg1.append('YPosition:='), vArg1.append(YCenter)
        vArg1.append('ZPosition:='), vArg1.append(ZCenter)
        if obj_name:
            vArg1[2] = obj_name
            try:
                edgeID = self.oeditor.GetEdgeByPosition(vArg1)
            except Exception:
                # Not Found, keep looking
                pass
        else:
            for obj in self.get_all_objects_names():
                vArg1[2] = obj
                try:
                    edgeID = self.oeditor.GetEdgeByPosition(vArg1)
                    break
                except Exception:
                    # Not Found, keep looking
                    pass

        return edgeID

    @aedt_exception_handler
    def get_edgeids_from_vertexid(self, vertexid, obj_name):
        """

        Parameters
        ----------
        vertexid :
            Vertex ID to search
        obj_name :
            object name.

        Returns
        -------
        type
            Edge ID array

        """
        edgeID = []
        edges = self.get_object_edges(obj_name)
        for edge in edges:
            vertx=self.get_edge_vertices(edge)
            if vertexid in vertx:
                edgeID.append(edge)

        return edgeID

    @aedt_exception_handler
    def get_faceid_from_position(self, position, obj_name=None, units=None):
        """

        Parameters
        ----------
        position :
            ApplicationName.modeler.Position(x,y,z) object
        obj_name :
            optional object name. Otherwise it will search in all objects (Default value = None)
        units :
            units (e.g. 'm'), if None model units is used (Default value = None)

        Returns
        -------
        type
            Face ID of first object touching that position

        """
        face_id = -1
        XCenter, YCenter, ZCenter = self.pos_with_arg(position, units)

        vArg1 = ['NAME:FaceParameters']
        vArg1.append('BodyName:='), vArg1.append('')
        vArg1.append('XPosition:='), vArg1.append(XCenter)
        vArg1.append('YPosition:='), vArg1.append(YCenter)
        vArg1.append('ZPosition:='), vArg1.append(ZCenter)
        if obj_name:
            vArg1[2] = obj_name
            try:
                face_id = self.oeditor.GetFaceByPosition(vArg1)
            except Exception:
                # Not Found, keep looking
                pass
        else:
            for obj in self.get_all_objects_names():
                vArg1[2] = obj
                try:
                    face_id = self.oeditor.GetFaceByPosition(vArg1)
                    break
                except Exception:
                    # Not Found, keep looking
                    pass

        return face_id

    @aedt_exception_handler
    def arg_with_dim(self, Value, units=None):
        """

        Parameters
        ----------
        Value :

        units :
             (Default value = None)

        Returns
        -------

        """
        if type(Value) is str:
            val = Value
        else:
            if units is None:
                units = self.model_units
            val = "{0}{1}".format(Value, units)

        return val

    @aedt_exception_handler
    def pos_with_arg(self, pos, units=None):
        """

        Parameters
        ----------
        pos :

        units :
             (Default value = None)

        Returns
        -------

        """
        try:
            posx = self.arg_with_dim(pos[0], units)
        except:
            posx = None
        try:
            posy = self.arg_with_dim(pos[1], units)
        except:
            posy = None
        try:
            posz = self.arg_with_dim(pos[2], units)
        except:
            posz = None
        return posx, posy, posz

    @aedt_exception_handler
    def _str_list(self, theList):
        """

        Parameters
        ----------
        theList :


        Returns
        -------

        """
        szList = ''
        for id in theList:
            o = self.objects[id]
            if len(szList):
                szList += ','
            szList += str(o.name)

        return szList

    @aedt_exception_handler
    def _find_object_from_edge_id(self, lval):
        """

        Parameters
        ----------
        lval :


        Returns
        -------

        """

        objList = []
        objListSheets = list(self.oeditor.GetObjectsInGroup("Sheets"))
        if len(objListSheets) > 0:
            objList.extend(objListSheets)
        objListSolids = list(self.oeditor.GetObjectsInGroup("Solids"))
        if len(objListSolids) > 0:
            objList.extend(objListSolids)
        for obj in objList:
            edgeIDs = list(self.oeditor.GetEdgeIDsFromObject(obj))
            if str(lval) in edgeIDs:
                return obj

        return None

    @aedt_exception_handler
    def _find_object_from_face_id(self, lval):
        """

        Parameters
        ----------
        lval :


        Returns
        -------

        """

        if self.oeditor is not None:
            objList = []
            objListSheets = list(self.oeditor.GetObjectsInGroup("Sheets"))
            if len(objListSheets) > 0:
                objList.extend(objListSheets)
            objListSolids = list(self.oeditor.GetObjectsInGroup("Solids"))
            if len(objListSolids) > 0:
                objList.extend(objListSolids)
            for obj in objList:
                face_ids = list(self.oeditor.GetFaceIDs(obj))
                if str(lval) in face_ids:
                    return obj

        return None

    @aedt_exception_handler
    def get_edges_on_bunding_box(self, sheets, return_colinear=True, tol=1e-6):
        """Get the edges of the sheets passed in input that are laying on the bounding box.
        Create new lines for the detected edges and returns the Id of those new lines.
        If required return only the colinear edges.

        Parameters
        ----------
        sheets :
            sheets as Id or name, list or single object.
        return_colinear :
            True to return only the colinear edges, False to return all edges on boundingbox. (Default value = True)
        tol :
            set the geometric tolerance (Default value = 1e-6)

        Returns
        -------
        type
            list of edges Id

        """

        port_sheets = self.convert_to_selections(sheets, return_list=True)
        bb = self._modeler.get_model_bounding_box()

        candidate_edges = []
        for p in port_sheets:
            edges = self.get_object_edges(p)
            for edge in edges:
                new_edge = self.create_object_from_edge(edge)
                time.sleep(1)
                vertices = self.get_object_vertices(new_edge)
                v_flag = False
                for vertex in vertices:
                    v = self.get_vertex_position(vertex)
                    if not v:
                        v_flag = False
                        break
                    xyz_flag = 0
                    if abs(v[0] - bb[0]) < tol or abs(v[0] - bb[3]) < tol:
                        xyz_flag += 1
                    if abs(v[1] - bb[1]) < tol or abs(v[1] - bb[4]) < tol:
                        xyz_flag += 1
                    if abs(v[2] - bb[2]) < tol or abs(v[2] - bb[5]) < tol:
                        xyz_flag += 1
                    if xyz_flag >= 2:
                        v_flag = True
                    else:
                        v_flag = False
                        break
                if v_flag:
                    candidate_edges.append(new_edge)
                else:
                    self.delete(new_edge)

        if return_colinear is False:
            return candidate_edges

        found_flag = False
        selected_edges = []
        for i in range(len(candidate_edges) - 1):
            if found_flag:
                break
            vertices_i = self.get_object_vertices(candidate_edges[i])
            vertex1_i = self.get_vertex_position(vertices_i[0])
            vertex2_i = self.get_vertex_position(vertices_i[1])
            midpoint_i = GeometryOperators.get_mid_point(vertex1_i, vertex2_i)
            for j in range(i + 1, len(candidate_edges)):
                vertices_j = self.get_object_vertices(candidate_edges[j])
                vertex1_j = self.get_vertex_position(vertices_j[0])
                vertex2_j = self.get_vertex_position(vertices_j[1])
                midpoint_j = GeometryOperators.get_mid_point(vertex1_j, vertex2_j)
                area = GeometryOperators.get_triangle_area(midpoint_i, midpoint_j, vertex1_i)
                if area < tol ** 2:
                    selected_edges.extend([candidate_edges[i], candidate_edges[j]])
                    found_flag = True
                    break
        selected_edges = list(set(selected_edges))

        for edge in candidate_edges:
            if edge not in selected_edges:
                self.delete(edge)

        return selected_edges

    @aedt_exception_handler
    def get_edges_for_circuit_port_from_sheet(self, sheet, XY_plane=True, YZ_plane=True, XZ_plane=True,
                                             allow_perpendicular=False, tol=1e-6):
        """Returns two edges ID suitable for the circuit port.
        One is belonging to the sheet passed in and the second one is the closest
        edges coplanar to first edge (aligned to XY, YZ, or XZ plane)
        Create new lines for the detected edges and returns the Id of those new lines.
        get_edges_for_circuit_port_fromsheet accepts a separated sheet object in input.
        get_edges_for_circuit_port accepts a faceId.

        Parameters
        ----------
        sheet :
            sheets as Id or name, list or single object.
        XY_plane :
            allows edges pair to be on XY plane (Default value = True)
        YZ_plane :
            allows edges pair to be on YZ plane (Default value = True)
        XZ_plane :
            allows edges pair to be on XZ plane (Default value = True)
        allow_perpendicular :
            allows edges pair to be perpendicular (Default value = False)
        tol :
            set the geometric tolerance (Default value = 1e-6)

        Returns
        -------
        type
            list of edges Id

        """
        tol2 = tol**2
        port_sheet = self.convert_to_selections(sheet, return_list=True)
        if len(port_sheet) > 1:
            return []
        else:
            port_sheet = port_sheet[0]
        port_edges = self.get_object_edges(port_sheet)

        # find the bodies to exclude
        port_sheet_midpoint = self.get_face_center(self.get_object_faces(port_sheet)[0])
        point = self._modeler.Position(*port_sheet_midpoint)
        list_of_bodies = self.get_bodynames_from_position(point)

        # select all edges
        all_edges = []
        solids = self.get_all_solids_names()
        solids = [s for s in solids if s not in list_of_bodies]
        for solid in solids:
            edges = self.get_object_edges(solid)
            all_edges.extend(edges)
        all_edges = list(set(all_edges))  # remove duplicates

        # select edges coplanar to port edges (aligned to XY, YZ, or XZ plane)
        ux = [1.0, 0.0, 0.0]
        uy = [0.0, 1.0, 0.0]
        uz = [0.0, 0.0, 1.0]
        midpoints = {}
        candidate_edges = []
        for ei in port_edges:
            vertices_i = self.get_edge_vertices(ei)
            if len(vertices_i) == 1:  # maybe a circle
                vertex1_i = self.get_vertex_position(vertices_i[0])
                area_i = self.get_face_area(self.get_object_faces(port_sheet)[0])
                if area_i is None or area_i < tol2:  # degenerated face
                    continue
                center_i = self.get_face_center(self.get_object_faces(port_sheet)[0])
                if not center_i:  # non planar face
                    continue
                radius_i = GeometryOperators.points_distance(vertex1_i, center_i)
                area_i_eval = 3.141592653589793*radius_i**2
                if abs(area_i-area_i_eval) < tol2:  # it is a circle
                    vertex2_i = center_i
                    midpoints[ei] = center_i
                else:  # not a circle
                    continue
            elif len(vertices_i) == 2:  # normal segment edge
                vertex1_i = self.get_vertex_position(vertices_i[0])
                vertex2_i = self.get_vertex_position(vertices_i[1])
                midpoints[ei] = self.get_edge_midpoint(ei)
            else:  # undetermined edge --> skip
                continue
            for ej in all_edges:
                vertices_j = self.get_edge_vertices(ej)
                if len(vertices_j) == 1:  # edge is an arc, not supported
                    continue
                elif len(vertices_j) == 2:  # normal segment edge
                    vertex1_j = self.get_vertex_position(vertices_j[0])
                    vertex2_j = self.get_vertex_position(vertices_j[1])
                else:  # undetermined edge --> skip
                    continue

                if not allow_perpendicular and \
                        abs(GeometryOperators._v_dot(GeometryOperators.v_points(vertex1_i, vertex2_i), GeometryOperators.v_points(vertex1_j, vertex2_j))) < tol:
                    continue

                normal1 = GeometryOperators.v_cross(GeometryOperators.v_points(vertex1_i, vertex2_i), GeometryOperators.v_points(vertex1_i, vertex1_j))
                normal1_norm = GeometryOperators.v_norm(normal1)
                if YZ_plane and abs(abs(GeometryOperators._v_dot(normal1, ux)) - normal1_norm) < tol:
                    pass
                elif XZ_plane and abs(abs(GeometryOperators._v_dot(normal1, uy)) - normal1_norm) < tol:
                    pass
                elif XY_plane and abs(abs(GeometryOperators._v_dot(normal1, uz)) - normal1_norm) < tol:
                    pass
                else:
                    continue

                vec1 = GeometryOperators.v_points(vertex1_i, vertex2_j)
                if abs(GeometryOperators._v_dot(normal1, vec1)) < tol2:  # the 4th point is coplanar
                    candidate_edges.append(ej)

        minimum_distance = tol**-1
        selected_edges = []
        for ei in midpoints:
            midpoint_i = midpoints[ei]
            for ej in candidate_edges:
                midpoint_j = self.get_edge_midpoint(ej)
                d = GeometryOperators.points_distance(midpoint_i, midpoint_j)
                if d < minimum_distance:
                    minimum_distance = d
                    selected_edges = [ei, ej]

        if selected_edges:
            new_edge1 = self.create_object_from_edge(selected_edges[0])
            time.sleep(1)
            new_edge2 = self.create_object_from_edge(selected_edges[1])
            return selected_edges
        else:
            return []
        pass

    @aedt_exception_handler
    def get_all_solids_names(self):
        """ """
        return []

    @aedt_exception_handler
    def get_edges_for_circuit_port(self, face_id, XY_plane=True, YZ_plane=True, XZ_plane=True,
                                   allow_perpendicular=False, tol=1e-6):
        """Returns two edges ID suitable for the circuit port.
        One is belonging to the faceId passed in input and the second one is the closest
        edges coplanar to first edge (aligned to XY, YZ, or XZ plane)
        Create new lines for the detected edges and returns the Id of those new lines.
        get_edges_for_circuit_port_fromsheet accepts a separated sheet object in input.
        get_edges_for_circuit_port accepts a faceId.

        Parameters
        ----------
        face_id :
            faceId of the input face.
        XY_plane :
            allows edges pair to be on XY plane (Default value = True)
        YZ_plane :
            allows edges pair to be on YZ plane (Default value = True)
        XZ_plane :
            allows edges pair to be on XZ plane (Default value = True)
        allow_perpendicular :
            allows edges pair to be perpendicular (Default value = False)
        tol :
            set the geometric tolerance (Default value = 1e-6)

        Returns
        -------
        type
            list of edges Id

        """
        tol2 = tol**2

        port_edges = self.get_face_edges(face_id)

        # find the bodies to exclude
        port_sheet_midpoint = self.get_face_center(face_id)
        list_of_bodies = self.get_bodynames_from_position(port_sheet_midpoint)

        # select all edges
        all_edges = []
        solids = self.get_all_solids_names()
        solids = [s for s in solids if s not in list_of_bodies]
        for solid in solids:
            edges = self.get_object_edges(solid)
            all_edges.extend(edges)
        all_edges = list(set(all_edges))  # remove duplicates

        # select edges coplanar to port edges (aligned to XY, YZ, or XZ plane)
        ux = [1.0, 0.0, 0.0]
        uy = [0.0, 1.0, 0.0]
        uz = [0.0, 0.0, 1.0]
        midpoints = {}
        candidate_edges = []
        for ei in port_edges:
            vertices_i = self.get_edge_vertices(ei)
            if len(vertices_i) == 1:  # maybe a circle
                vertex1_i = self.get_vertex_position(vertices_i[0])
                area_i = self.get_face_area(face_id)
                if area_i is None or area_i < tol2:  # degenerated face
                    continue
                center_i = self.get_face_center(face_id)
                if not center_i:  # non planar face
                    continue
                radius_i = GeometryOperators.points_distance(vertex1_i, center_i)
                area_i_eval = 3.141592653589793*radius_i**2
                if abs(area_i-area_i_eval) < tol2:  # it is a circle
                    vertex2_i = center_i
                    midpoints[ei] = center_i
                else:  # not a circle
                    continue
            elif len(vertices_i) == 2:  # normal segment edge
                vertex1_i = self.get_vertex_position(vertices_i[0])
                vertex2_i = self.get_vertex_position(vertices_i[1])
                midpoints[ei] = self.get_edge_midpoint(ei)
            else:  # undetermined edge --> skip
                continue
            for ej in all_edges:
                vertices_j = self.get_edge_vertices(ej)
                if len(vertices_j) == 1:  # edge is an arc, not supported
                    continue
                elif len(vertices_j) == 2:  # normal segment edge
                    vertex1_j = self.get_vertex_position(vertices_j[0])
                    vertex2_j = self.get_vertex_position(vertices_j[1])
                else:  # undetermined edge --> skip
                    continue

                if not allow_perpendicular and \
                        abs(GeometryOperators._v_dot(GeometryOperators.v_points(vertex1_i, vertex2_i), GeometryOperators.v_points(vertex1_j, vertex2_j))) < tol:
                    continue

                normal1 = GeometryOperators.v_cross(GeometryOperators.v_points(vertex1_i, vertex2_i), GeometryOperators.v_points(vertex1_i, vertex1_j))
                normal1_norm = GeometryOperators.v_norm(normal1)
                if YZ_plane and abs(abs(GeometryOperators._v_dot(normal1, ux)) - normal1_norm) < tol:
                    pass
                elif XZ_plane and abs(abs(GeometryOperators._v_dot(normal1, uy)) - normal1_norm) < tol:
                    pass
                elif XY_plane and abs(abs(GeometryOperators._v_dot(normal1, uz)) - normal1_norm) < tol:
                    pass
                else:
                    continue

                vec1 = GeometryOperators.v_points(vertex1_i, vertex2_j)
                if abs(GeometryOperators._v_dot(normal1, vec1)) < tol2:  # the 4th point is coplanar
                    candidate_edges.append(ej)

        minimum_distance = tol**-1
        selected_edges = []
        for ei in midpoints:
            midpoint_i = midpoints[ei]
            for ej in candidate_edges:
                midpoint_j = self.get_edge_midpoint(ej)
                d = GeometryOperators.points_distance(midpoint_i, midpoint_j)
                if d < minimum_distance:
                    minimum_distance = d
                    selected_edges = [ei, ej]

        if selected_edges:
            new_edge1 = self.create_object_from_edge(selected_edges[0])
            time.sleep(1)
            new_edge2 = self.create_object_from_edge(selected_edges[1])
            return selected_edges
        else:
            return []
        pass

    @aedt_exception_handler
    def get_closest_edgeid_to_position(self, position, units=None):
        """

        Parameters
        ----------
        position :
            x,y,z], list of float OR ApplicationName.modeler.Position(x,y,z) object
        units :
            units for position (e.g. 'm'), if None model unit is used (Default value = None)

        Returns
        -------
        type
            Edge ID of the closes edge to that position

        """
        if type(position) is list:
            position = self.modeler.Position(position)

        bodies = self.get_bodynames_from_position(position, units)
        # the function searches in all bodies, not efficient
        face_id = self.get_faceid_from_position(position, obj_name=bodies[0], units=units)
        edges = self.get_face_edges(face_id)
        distance = 1e6
        selected_edge = None
        for edge in edges:
            midpoint = self.get_edge_midpoint(edge)
            if self.model_units == 'mm' and units == 'meter':
                midpoint = [i/1000 for i in midpoint]
            elif self.model_units == 'meter' and units == 'mm':
                midpoint = [i*1000 for i in midpoint]
            d = GeometryOperators.points_distance(midpoint, [position.X, position.Y, position.Z])
            if d < distance:
                selected_edge = edge
                distance = d
        return selected_edge


