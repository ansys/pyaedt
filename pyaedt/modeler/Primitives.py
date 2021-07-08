"""
This module contains these Primitives classes: `Polyline` and `Primitives`.
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
from collections import OrderedDict
if "IronPython" in sys.version or ".NETFramework" in sys.version:
    _ironpython = True
else:
    _ironpython = False


default_materials = {"Icepak": "air", "HFSS": "vacuum", "Maxwell 3D": "vacuum", "Maxwell 2D": "vacuum",
                     "2D Extractor": "copper", "Q3D Extractor": "copper", "HFSS 3D Layout": "copper", "Mechanical" : "copper"}


class PolylineSegment():
    """PolylineSegment class.
    
    A polyline segment is an object describing a segment of a polyline within the 3D modeler.

    Parameters
    ----------
    type : str
        Type of the object. Options are ``Line``, ``Arc``, ``Spline``, and ``AngularArc``.
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
    arc_plane : str, optional
        Plane in which the arc sweep is performed in the active coordinate system ``XY``, ``YZ`` 
        or ``ZX``. The default is ``None``. If ``None``, the plane is determined automatically 
        by the first coordinate for which start-point and center-point have the same value.

    Examples
    ----------
    See Polyline().
    """
    @aedt_exception_handler
    def __init__(self, type, num_seg=0, num_points=0, arc_angle=0, arc_center=None, arc_plane=None):
   
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
    """Polyline class.

    This class provides methods for creating and manipulating polyline objects within 
    the AEDT Modeler. Intended usage is for the constructor of this class to be called
    by the `Primitives.draw_polyline` method. The documentation is provided there.

    The returned polyline object exposes the methods for manipulation of the polyline:

    Parameters
    ----------
    parent : 
    position_list : list, optional
        The default is ''None``. 
    object_id : optional
        The default is ''None``.
    segment_type : optional
        The default is ''None``.
    cover_surface : bool, optional
        The default is ''False``.
    close_surface : bool, optional
        The default is ''False``.
    name : optional
        The default is ''None``.
    matname : str, optional
        Name of the material. The default is ''None``.
    xsection_type : str, optional
        Type of the cross-section. Options are ``"Line"``, ``"Circle"``, ``"Rectangle"`` 
        and ``"Isosceles Trapezoid"``. The default is ``None``.
    xsection_orient : str, optional
        Direction of the normal vector to the width of the cross-section. 
        Options are ``"X"``, ``"Y"``, ``"Z"``, and ``"Auto"``. The 
        default is ``None``.
    xsection_width : float or str, optional
        Width or diameter of the cross-section for all types. The default is
        ``0``.
    xsection_topwidth : float or str, ooptional
        Top width of the cross-section for the type ``"Isosceles Trapezoid"`` only.
        The default is ``0``.
    xsection_height : float or str, optional
        Height of the cross-section for the type ``"Rectangle"`` or ``"Isosceles 
        Trapezoid"`` only. The default is ``0``.
    xsection_num_seg : int, optional
        Number of segments in the cross-section surface for the type ``"Circle"``, 
        ``"Rectangle"`` or ``"Isosceles Trapezoid"``. The default is ``0``. 
        The value must be ``0`` or greater than ``2``.
    xsection_bend_type : str, optional
        Type of the bend. The default is ``None``, in which case the bend type
        is set to ``"Corner"``. For the type ``"Circle"``, the bend type 
        should be set to ``"Curved"``.
        
    Methods
    -------
    set_crosssection_properties
    insert_segment
    remove_vertex
    remove_edges
    clone
        
    See Also
    --------
    The constructor is intended to be called from the `Primitives.draw_polyline` method.
    """
    @aedt_exception_handler
    def __init__(self, parent, position_list=None, object_id=None, segment_type=None, cover_surface=False,
                 close_surface=False, name=None, matname=None, xsection_type=None, xsection_orient=None,
                 xsection_width=0, xsection_topwidth=0, xsection_height=0,
                 xsection_num_seg=0, xsection_bend_type=None):
     
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

            if name:
                obj_name = name
            else:
                obj_name = self._o.name

            varg2 = self._o.export_attributes(obj_name)

            self._o._m_name = parent.oeditor.CreatePolyline(varg1, varg2)

            self._parent._refresh_object_types()
            self._parent._update_object(self._o)

        else:
            # Instantiate a new Polyline object for an existing object id in the modeler
            self._o = self._parent.objects[object_id]
            self._positions = []
            for vertex in self._o.vertices:
                position = vertex.position
                self._positions.append(position)

    @property
    def id(self):
        """Object ID of the polyline in the AEDT modeler.

        Returns
        -------
        int
        """
        return self._o.id

    @property
    def name(self):
        """Name of the polyline in the AEDT modeler. 
        
        The name can differ from the specified name if an
        object of this name already exists.

        Returns
        -------
        int
        """
        return self._o.name

    @property
    def start_point(self):
        """Position of the first point in the polyline object in ``[x, y, z]`` in the object coordinate system.

        Returns
        -------
        list
        """
        vertex_id = self._parent.get_object_vertices(partID=self.id)[0]
        return self._parent.get_vertex_position(vertex_id)

    @property
    def end_point(self):
        """Position of the end point in the polyline object in ``[x, y, z]`` in the object coordinate system.

        Returns
        -------
        list      
        """
        end_vertex_id = self._parent.get_object_vertices(partID=self.id)[-1]
        return self._parent.get_vertex_position(end_vertex_id)

    @property
    def vertex_positions(self):
        """A list of all vertex positions in the polyline object in ``[x, y, z]`` in the object coordinate system.

        Returns
        -------
        list
        """
        id_list = self._parent.get_object_vertices(partID=self.id)
        position_list = [ self._parent.get_vertex_position(id) for id in id_list]
        return position_list

    @aedt_exception_handler
    def _crosssection(self, type=None, orient=None, width=0, topwidth=0, height=0, num_seg=0, bend_type=None):
        """Generate an array of properties for the polyline cross-section.
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
        """Retrieve an array of property data for a polyline point.

        Generate the property array for the XYZ point data. The X, Y, and Z coordinates are taken
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
        """Retrieve an array of parameter data for points and segments.

        Returns the array of parameters required to specify the points and segments of a polyline
        for use in the AEDT API method `CreatePolyline`.

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
                raise ("Number of segments is inconsistent with the number of points.")

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
                                err_str = "There are insufficient points in the position list to complete the specified segment list."
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
        """Retrieve an array of properties for a polyline segment.

        Returns an array of parameters for an individual segment of a polyline
        to use in the AEDT API method `CreatePolyline`.

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
        type
            Polyline object created.

        Examples
        --------
        >>> primitives = self.aedtapp.modeler.primitives
        >>> P1 = primitives.create_polyline([[0, 1, 2], [0, 2, 3], [2, 1, 4]])
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
        """Remove a vertex from an existing polyline by position.

        You must enter the exact position of the vertex as a list
        of [x, y, z] coordinates in the object coordinate system.

        Parameters
        ----------
        position : list
            List of x, y, z coordinates specifying the vertex to be removed.
        abstol : float, optional
            Absolute tolerance of the comparison of a specified position to the 
            vertex positions. The default is ``1e-9``.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.

        Examples
        --------
        Use floating point values for the vertex positions.
        
        >>> P = primitives.create_polyline([[0, 1, 2], [0, 2, 3], [2, 1, 4]])
        >>> P.remove_vertex([0, 1, 2])

        Use string expressions for the vertex position.
        
        >>> P = primitives.create_polyline([[0, 1, 2], [0, 2, 3], [2, 1, 4]])
        >>> P.remove_vertex(["0mm", "1mm", "2mm"])

        Use string expressions for the vertex position and include an absolute
        tolerance when searching for the vertex to be removed.
        
        >>> P = primitives.create_polyline([[0, 1, 2], [0, 2, 3], [2, 1, 4]])
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
        """Remove a vertex from an existing polyline by position.

        You must enter the exact position of the vertex as a list 
        of ``[x, y, z]`` coordinates in the object coordinate system.

        Parameters
        ----------
        edge_id : int or list of int
            One or more edge IDs within the total number of edges in the polyline.            
        
        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed. 

        Examples
        --------
        >>> P = primitives.create_polyline([[0, 1, 2], [0, 2, 3], [2, 1, 4]])
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
            Types of the cross-sections. Options are ``"Line"``, ``"Circle"``, ``"Rectangle"`` 
            and ``"Isosceles Trapezoid"``. The default is ``None``.
        orient : str, optional
            Direction of the normal vector to the width of the cross-section. 
            Options are ``"X"``, ``"Y"``, ``"Z"``, and ``"Auto"``. The default 
            is ``None``, which sents the orientation to ``"Auto"``.
        width : float or str, optional
           Width or diameter of the cross-section for all types. The default is
           ``0``.
        topwidth : float or str
           Top width of the cross-section for the type ``"Isosceles Trapezoid"`` 
           only. The default is ``0``.
        height : float or str
            Height of the cross-section for the type ``"Rectangle"`` or ``"Isosceles 
            Trapezoid"`` only. The default is ``0``.
        num_seg : int, optional
            Number of segments in the cross-section surface for the type ``"Circle"``, 
            ``"Rectangle"`` or ``"Isosceles Trapezoid"``. The default is ``0``. 
            The value must be ``0`` or greater than ``2``.
        bend_type : str, optional
            Type of the bend. The default is ``None``, in which case the bend type
            is set to ``"Corner"``. For the type ``"Circle"``, the bend type should be 
            set to ``"Curved"``.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.

        Examples
        --------
        >>> P = primitives.create_polyline([[0, 1, 2], [0, 2, 3], [2, 1, 4]])
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

        self._parent._refresh_object_types()
        self._parent._update_object(self._o)
        #self._parent._update_object(self._o)
        return True

    @aedt_exception_handler
    def insert_segment(self, position_list, segment=None):
        """Add a segment to an existing polyline.

        Parameters
        ----------
        position_list : list
            List of positions of the points that define the segment to insert. 
            Either the starting point or ending point of the segment list must 
            match one of the vertices of the existing polyline.
        segment: str or PolylineSegment
            Definition of the segment to insert. Valid string values are 
            ``"Line"`` or ``"Arc"``. Otherwise use ``"PolylineSegment"`` 
            to define the segment precicesly for the type ``"AngularArc"`` 
            or ``"Spline"``.

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
    """Common primitives class."""
    def __init__(self, parent, modeler):
        self._modeler = modeler
        self._parent = parent
        self.objects = defaultdict(Object3d)
        self.objects_names = defaultdict()
        self._currentId = 0
        self.refresh()

    @property
    def non_models(self):
        """List of all objects of type ``"Solid"``.`"""
        return self._nonmodels

    @property
    def solids(self):
        """List of all objects of type ``"Solid"``."""
        return self._solids

    @property
    def sheets(self):
        """List of all objects of type ``"Sheet"``."""
        return self._sheets

    @property
    def lines(self):
        """List of all objects of type ``"Line"``."""
        return self._lines

    @property
    def object_names(self):
        """List of all objects of type ``"Line"``."""
        return self._all_object_names

    @aedt_exception_handler
    def __getitem__(self, partId):
        """Return the object `Object3D` for a given object ID or object name.

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
        bool
            ``True`` when successful, ``False`` when failed
        """
        self.objects[partId].name = partName
        return True

    @property
    def oproject(self):
        """Project object."""
        return self._parent.oproject

    @property
    def odesign(self):
        """Design object."""
        return self._parent.odesign

    @property
    def materials(self):
        """Materials."""
        return self._parent.materials

    @property
    def defaultmaterial(self):
        """Default material."""
        return default_materials[self._parent._design_type]

    @property
    def variable_manager(self):
        """Variable manager."""
        return self._parent.variable_manager

    @property
    def messenger(self):
        """Messenger."""
        return self._parent._messenger

    @property
    def version(self):
        """AEDT version."""
        return self._parent._aedt_version

    @property
    def modeler(self):
        """Modeler."""
        return self._modeler

    @property
    def design_types(self):
        """Design types."""
        return self._parent._modeler

    @property
    def oeditor(self):
        """Editor object."""
        return self.modeler.oeditor

    @property
    def model_units(self):
        """Model units."""
        return self.modeler.model_units

    @aedt_exception_handler
    def _delete_object_from_dict(self, objname):
        """Delete an object from the dictionaries.

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
    def _update_object(self, o):


        # Store the new object infos
        self.objects[o.id] = o
        self.objects_names[o.name] = o.id

        o.update_object_type()
        o.update_properties()

        # Cleanup
        if 0 in self.objects:
            del self.objects[0]

        return o.id

    @aedt_exception_handler
    def _check_material(self, matname, defaultmatname):
        """Check for a material name.
        
        If a material name exists, it is assigned. Otherwise, the default material
        specified is assigned.

        Parameters
        ----------
        matname : str
            Name of the material.
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
        """Convert a numerical length string, such as ``"10mm"`` to a floating point value.

        Converts a numerical length string, such as ``"10mm"``, to a floating point value 
        in the defined object units ``self.object_units``. If a list of such objects is 
        given, the entire list is converted.

        Parameters
        ----------
        value : string or list of strings
            One or more numerical length strings to convert.
        
        Returns
        -------
            float or list of floats
        """
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
        """"Check to see if an object exits.
        
        Parameters
        ----------
        object : 
            Object name or object ID.
        
        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed
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
        """Create an air region.

        Parameters
        ----------
        pad_percent : list
            Percent to pad.

        Returns
        -------
        type
            Object ID.
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
        obj._m_name = "Region"
        obj._solve_inside = True
        obj._transparency = 0
        obj._wireframe = True
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
        int
            ID of the object.
        """
        o = self._new_object()

        obj = self._find_object_from_edge_id(edgeID)

        if obj is not None:

            varg1 = ['NAME:Selections']
            varg1.append('Selections:='), varg1.append(obj)
            varg1.append('NewPartsModelFlag:='), varg1.append('Model')

            varg2 = ['NAME:BodyFromEdgeToParameters']
            varg2.append('Edges:='), varg2.append([edgeID])
            o._m_name =self.oeditor.CreateObjectFromEdges(varg1, ['NAME:Parameters', varg2])[0]

            self._refresh_object_types()
            id = self._update_object(o)
            self.objects[id] = o
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
        int
            ID of the object.
        """
        o = self._new_object()

        obj = self._find_object_from_face_id(faceId)

        if obj is not None:

            varg1 = ['NAME:Selections']
            varg1.append('Selections:='), varg1.append(obj)
            varg1.append('NewPartsModelFlag:='), varg1.append('Model')

            varg2 = ['NAME:BodyFromFaceToParameters']
            varg2.append('FacesToDetach:='), varg2.append([faceId])
            o._m_name =self.oeditor.CreateObjectFromFaces(varg1, ['NAME:Parameters', varg2])[0]

            self._refresh_object_types()
            id = self._update_object(o)
            self.objects[id] = o
        return id

    @aedt_exception_handler
    def create_polyline(self, position_list, segment_type=None,
                        cover_surface=False, close_surface=False, name=None,
                        matname=None, xsection_type=None, xsection_orient=None,
                        xsection_width=1, xsection_topwidth=1, xsection_height=1,
                        xsection_num_seg=0, xsection_bend_type=None):
        """Draw a polyline object in the 3D modeler.

        Retrieves an object of the type ``Polyline``, allowing for manipulation
        of the polyline.

        Parameters
        ----------
        position_list : list
            Array of positions of each point of the polyline.
            A position is a list of 2D or 3D coordinates. Position coordinate values
            can be numbers or valid AEDT string expressions. For example, ``[0, 1, 2]``, 
            ``["0mm", "5mm", "1mm"]``, or ``["x1", "y1"]``.
        segment_type : str or PolylineSegment or list, optional
            The default behavior is to connect all points as ``"Line"`` segments. The
            default is ``None``. For a string, ``"Line"`` or ``"Arc"`` is valid. For a
            ``"PolylineSegment"``, for ``"Line",`` ``"Arc"``, ``"Spline"``, or 
            ``"AngularArc"``, a list of segment types (str or PolylineSegment) is 
            valid for a compound polyline.
        cover_surface : bool, optional
            The default is ``False``.
        close_surface : bool, optional
            The default is ``False``, which automatically joins the starting and 
            ending points.
        name: str, optional
            Name of the polyline. The default is ``None``.
        matname: str, optional
            Name of the material. The default is ``None``, in which case a name
            is automatically assigned. 
        xsection_type : str, optional
            Type of the cross-section. Options are ``"Line"``, ``"Circle"``, 
            ``"Rectangle"``, and ``"Isosceles Trapezoid"``. The default is ``None``.
        xsection_orient : str, optional
            Direction of the normal vector to the width of the cross-section.
            Options are ``"X"``, ``"Y"``, ``"Z"``, and ``"Auto"``. The default is 
            ``None``, which sets the direction to ``"Auto"``.
        xsection_width : float or str, optional
            Width or diameter of the cross-section for all  types. The 
            default is ``1``.
        xsection_topwidth : float or str, optional
            Top width of the cross-section for type ``"Isosceles Trapezoid"`` only.
            The default is ``1``.
        xsection_height : float or str
            Height of the cross-section for type ``"Rectangle"`` or ``"Isosceles 
            Trapezoid"`` only. The default is ``1``.
        xsection_num_seg : int, optional
            Number of segments in the cross-section surface for type ``"Circle"``, 
            ``"Rectangle"``, or ``"Isosceles Trapezoid"``. The default is ``0``. The
            value must be ``0`` or greater than ``2``.
        xsection_bend_type : str, optional
            Type of the bend for the cross-section. The default is ``None``, in which 
            case the bend type is set to ``"Corner"``. For the type ``"Circle"``, the bend type 
            should be set to ``"Curved"``.
        
        Returns
        -------
        Polyline
            Object with additional methods for manipulating the polyline.  
            
            For example, `insert_segment`. The object ID of the created polyline can be accessed
            via `Polyline.id`.

        Examples
        -------
        Set up the desktop environment.
        
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

        The default behavior assumes that all points are to be connected by line segments. 
        Optionally specify the name.
        
        >>> P1 = primitives.create_polyline(test_points, name="PL_line_segments")

        Specify that the first segment is a line and the last three points define a three-point arc.
        
        >>> P2 = primitives.create_polyline(test_points, segment_type=["Line", "Arc"], name="PL_line_plus_arc")

        Redraw the 3-point arc alone from the last three points and additionally specify five segments 
        using ``PolylineSegment``.
        
        >>> P3 = primitives.create_polyline(test_points[1:],
        ...                               segment_type=PolylineSegment(type="Arc", num_seg=7),
        ...                               name="PL_segmented_arc")

        Specify that the four points form a spline and add a circular cross-section with a 
        diameter of 1 mm.
        
        >>> P4 = primitives.create_polyline(test_points, segment_type="Spline", name="PL_spline",
        ...                               xsection_type="Circle", xsection_width="1mm")

        Use the `PolylineSegment` object to specify more detail about the individual segments.
        Create a center point arc starting from the position ``test_points[1]``, rotating 
        about the center point position ``test_points[0]`` in the XY plane.
        
        >>> start_point = test_points[1]
        >>> center_point = test_points[0]
        >>> segment_def = PolylineSegment(type="AngularArc", arc_center=center_point, arc_angle="90deg", arc_plane="XY")
        >>> primitives.create_polyline(start_point, segment_type=segment_def, name="PL_center_point_arc")
        
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
            ID of the polyline object in the 3D modeler.

        Returns
        -------
        type
            Polyline
        """
        return Polyline(self, object_id=object_id)

    @aedt_exception_handler
    def create_udp(self, udp_dll_name, udp_parameters_list, upd_library='syslib', name=None, udptye="Solid"):
        """Create a user-defined primitive.

        Parameters
        ----------
        udp_dll_name : str
            Name of the UPD DLL.
        udp_parameters_list :
            List of the UDP paraemters.
        upd_library : str, optional
            Name of the UPP library. The default is ``"syslib"``.
        name : str, coptional
            Name of the component. The default is ``None``.
        udptye : str, optional
            Type of the UDP. The default is ``"Solid"``.

        Returns
        -------
        type
            ID of the object.
        """
        o = self._new_object()

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
        o._m_name =name
        vArg2 = o.export_attributes(namergs[-1])
        self.oeditor.CreateUserDefinedPart(vArg1, vArg2)

        self._refresh_object_types()
        id = self._update_object(o)

        return id

    @aedt_exception_handler
    def get_obj_name(self, partId):
        """Return an object name from an ID.

        Parameters
        ----------
        partId :
            ID of the object.

        Returns
        -------
        type
            Object ID.

        """
        return self.objects[partId].name

    @aedt_exception_handler
    def convert_to_selections(self, objtosplit, return_list=False):
        """Convert a list of objects to a selection.

        Parameters
        ----------
        objtosplit : str, int, or list of mixed types
            Objects to convert to a selection. 
        return_list : bool, optional
            How to return the objects in the selection. The default is ''False``.
            When ``False``, the objects in the selection are returned as a string.
            When ``True``, the objects in the selection are returned as a list.
        
        Returns
        -------
        type
            Object name in the form of a list of string.

        """
        if type(objtosplit) is not list:
            objtosplit = [objtosplit]
        objnames = []
        for el in objtosplit:
            if type(el) is int:
                objnames.append(self.get_obj_name(el))
            else:
                objnames.append(el)
        if return_list:
            return objnames
        else:
            return ",".join(objnames)

    @aedt_exception_handler
    def delete(self, objects):
        """Delete objects or groups.

        Parameters
        ----------
        objects : list
            List of objects or group names.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed
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
        """Delete all objects with a given prefix.

        Parameters
        ----------
        contained_string : str
            Prefix in names of objects to delete.
        case_sensitive : bool, optional
            Whether the prefix is case-senstive. The default is ``True``.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed

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
        """Retrieve the model's bounding box."""
        bound = []
        if self.oeditor is not None:
            bound = self.oeditor.GetModelBoundingBox()
        return bound

    @aedt_exception_handler
    def get_obj_id(self, objname):
        """Return the object ID from an object name.

        Parameters
        ----------
        objname : str
            Name of the object.

        Returns
        -------
        type
            Object ID.
        """
        if objname in self.objects_names:
            if self.objects_names[objname] in self.objects:
                return self.objects_names[objname]
        return None

    @aedt_exception_handler
    def get_objects_w_string(self, stringname, case_sensitive=True):
        """Retrieve all objects with a given string in their names.

        Parameters
        ----------
        stringname : str
            String for which to search object names
        case_sensitive : bool, optional
            Whether the string is case-sensitive. The default is ``True``.

        Returns
        -------
        type
            Objects in a list of strings.

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
        """Retrieve all model objects.

        Parameters
        ----------
        model : bool, optional
            Whether to retrieve all model objects. The default is ''True``. When ``False``, 
            all non-model objects are retrieved.

        Returns
        -------
        list
            List of model objects.

        """
        list_objs = []
        for el in self.objects:
            if self.objects[el].model==model:
                list_objs.append(self.objects[el].name)
        return list_objs

    @aedt_exception_handler
    def refresh(self):
        self._refresh_all_ids_from_aedt_file()
        #TODO: Why do we need this ?
        if not self.objects:
            self.refresh_all_ids()

    @aedt_exception_handler
    def _refresh_object_types(self):
        self._nonmodels = list(self.oeditor.GetObjectsInGroup("Non Model"))
        self._solids = list(self.oeditor.GetObjectsInGroup("Solids"))
        self._sheets = list(self.oeditor.GetObjectsInGroup("Sheets"))
        self._lines = list(self.oeditor.GetObjectsInGroup("Lines"))
        self._all_object_names = self._solids + self._sheets + self._lines

    @aedt_exception_handler
    def refresh_all_ids(self):

        self._refresh_object_types()
        all_object_names = self.get_all_objects_names()

        for el in self._solids:
            if el not in all_object_names:
                o = Object3d(self, name=el)
                self._update_object(o)

        for el in self._sheets:
            if el not in all_object_names:
                o = Object3d(self, name=el)
                self._update_object(o)

        for el in self._lines:
            if el not in all_object_names:
                o = Object3d(self, name=el)
                self._update_object(o)

        for el in all_object_names:
            if el not in self._all_object_names:
                self._delete_object_from_dict(el)

        return len(self.objects)

    @aedt_exception_handler
    def _refresh_all_ids_from_aedt_file(self):
        if not self._parent.design_properties or "ModelSetup" not in self._parent.design_properties:
            return 0

        self._refresh_object_types()

        try:
            groups = self._parent.design_properties['ModelSetup']['GeometryCore']['GeometryOperations']['Groups'][
                'Group']
        except KeyError:
            groups = []
        if type(groups) is not list:
            groups = [groups]
        try:
            self._parent.design_properties['ModelSetup']['GeometryCore']['GeometryOperations']['ToplevelParts'][
                'GeometryPart']
        except KeyError:
            return 0
        for el in self._parent.design_properties['ModelSetup']['GeometryCore']['GeometryOperations']['ToplevelParts']['GeometryPart']:
            if isinstance(el, OrderedDict):
                attribs = el['Attributes']
            else:
                attribs = \
                self._parent.design_properties['ModelSetup']['GeometryCore']['GeometryOperations']['ToplevelParts'][
                    'GeometryPart']['Attributes']

            o = Object3d(self, name=attribs['Name'])

            o.update_object_type()

            if o.analysis_type:
                o._solve_inside = attribs['SolveInside']
                o._material_name = attribs['MaterialValue'][1:-1]

            o.part_coordinate_system = attribs['PartCoordinateSystem']
            if "NonModel" in attribs['Flags']:
                o._model = False
            else:
                o._model = True
            if "Wireframe" in attribs['Flags']:
                o._wireframe = True
            else:
                o._wireframe = False
            groupname = ""
            for group in groups:
                if attribs['GroupId'] == group['GroupID']:
                    groupname = group['Attributes']['Name']

            o._m_groupName = groupname
            o._color = attribs['Color']
            o._surface_material = attribs['SurfaceMaterialValue']

            # Store the new object infos
            self.objects[o.id] = o
            self.objects_names[o.name] = o.id

        return len(self.objects)

    #TODO Deprecate this to Object3D
    @aedt_exception_handler
    def update_object_properties(self, o):
        """Update properties for an object.

        Parameters
        ----------
        o : str
            Name of the object.

        Returns
        -------

        """
        n = 10
        name = o.name
        all_prop = retry_ntimes(n, self.oeditor.GetProperties, "Geometry3DAttributeTab", name)
        if 'Solve Inside' in all_prop:
            solveinside = retry_ntimes(n, self.oeditor.GetPropertyValue, "Geometry3DAttributeTab", name, 'Solve Inside')
            if solveinside == 'false' or solveinside == 'False':
                o._solve_inside = False
        if 'Material' in all_prop:
            mat = retry_ntimes(n, self.oeditor.GetPropertyValue, "Geometry3DAttributeTab", name, 'Material')
            if mat:
                o._material_name = mat[1:-1].lower()
            else:
                o._material_name = ''
        if 'Orientation' in all_prop:
            o._part_coordinate_system = retry_ntimes(n, self.oeditor.GetPropertyValue,
                                                    "Geometry3DAttributeTab", name, 'Orientation')
        if 'Model' in all_prop:
            mod = retry_ntimes(n, self.oeditor.GetPropertyValue, "Geometry3DAttributeTab", name, 'Model')
            if mod == 'false' or mod == 'False':
                o._model = False
            else:
                o._model = True
        if 'Group' in all_prop:
            o._m_groupName = retry_ntimes(n, self.oeditor.GetPropertyValue, "Geometry3DAttributeTab", name, 'Group')
        if 'Display Wireframe' in all_prop:
            wireframe = retry_ntimes(n, self.oeditor.GetPropertyValue,
                                     "Geometry3DAttributeTab", name, 'Display Wireframe')
            if wireframe == 'true' or wireframe == 'True':
                o._wireframe = True
        if 'Transparent' in all_prop:
            transp = retry_ntimes(n, self.oeditor.GetPropertyValue, "Geometry3DAttributeTab", name, 'Transparent')
            try:
                o._transparency = float(transp)
            except:
                o._transparency = 0.3
        if 'Color' in all_prop:
            color = int(retry_ntimes(n, self.oeditor.GetPropertyValue, "Geometry3DAttributeTab", name, 'Color'))
            if color:
                r = (color >> 16) & 255
                g = (color >> 8) & 255
                b = color & 255
                o._color = (r, g, b)
            else:
                o._color = (0, 195, 255)
        if 'Surface Material' in all_prop:
            o._surface_material = retry_ntimes(n, self.oeditor.GetPropertyValue,
                                               "Geometry3DAttributeTab", name, 'Surface Material')
        return o

    @aedt_exception_handler
    def get_all_objects_names(self, refresh_list=False, get_solids=True, get_sheets=True, get_lines=True):
        """Retrieve the names of all objects in the design.

        Parameters
        ----------
        refresh_list : bool, optional
            Whether to forcibly refresh the list of objects. 
            The default is ``False``.
        get_solids : bool, optional
            Whether to include the solids in the list. The default is ``True``.
        get_sheets : bool, optional
            Whether to include the sheets in the list. The default is ``True``.
        get_lines : bool, optional
            Whether to include the lines in the list. The default is ``True``.

        Returns
        -------
        list
            List of the object names.

        """
        if refresh_list:
            l = self.refresh_all_ids()
            self.messenger.add_info_message("Found " + str(l) + " Objects")
        obj_names = []
        if get_lines and get_sheets and get_solids:
            return [i for i in list(self.objects_names.keys())]

        for id, el in self.objects.items():
            if (el.object_type == "Solid" and get_solids) \
                    or (el.object_type == "Sheet" and get_sheets) \
                    or (el.object_type == "Line" and get_lines):
                obj_names.append(el.name)
        return obj_names

    @aedt_exception_handler
    def get_all_sheets_names(self, refresh_list=False):
        """Retrieve the names of all sheets in the design.

        Parameters
        ----------
        refresh_list : bool, optional
            Whether to forcibly refresh the list of objects.
            The default is ``False``.

        Returns
        -------
        list
            List of the sheet names.
        """
        return self.get_all_objects_names(refresh_list=refresh_list, get_solids=False, get_sheets=True, get_lines=False)

    @aedt_exception_handler
    def get_all_lines_names(self, refresh_list=False):
        """Retrieve the names of all lines in the design.

        Parameters
        ----------
        refresh_list : bool, optional
            Whether to forcibly refresh the list objects. 
            The default is ``False``.
            
        Returns
        -------
        list
            List of the line names.

        """
        return self.get_all_objects_names(refresh_list=refresh_list, get_solids=False, get_sheets=False, get_lines=True)

    @aedt_exception_handler
    def get_objects_by_material(self, materialname):
        """Retrieve a list of the IDs for objects of a specified material.

        Parameters
        ----------
        materialname : str
            Name of the material.

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
        """Retrieve the IDs of all objects.

        Returns
        -------
        type
            List of object IDs.
        """
        objs = []
        for el in self.objects:
            objs.append(el)
        return objs

    @aedt_exception_handler
    def request_new_object(self, matname=None):
        """Retrieve the new object.

        Parameters
        ----------
        matname : str, optional
        Name of the material of the new component.

        Returns
        -------
        Object3d
        """
        return self._new_object(matname=matname)

    @aedt_exception_handler
    def _new_object(self, matname=None):
        """Deprecate this to _new_object """
        o = Object3d(self)
        self.objects[0] = o
        o._material_name, o._solve_inside = self._check_material(matname, self.defaultmaterial)
        return o

    @aedt_exception_handler
    def _new_id(self):
        """Deprecate this to _new_object """
        o = Object3d(self)
        self._currentId = 0
        self.objects[self._currentId] = o
        return self._currentId

    @aedt_exception_handler
    def find_closest_edges(self, start_obj, end_obj, port_direction=0):
        """Retrieve the two closet edges that are not perpendicular for two objects.
        
        PortDirection is used in case more than 2 couple are on the same distance (eg. coax or microstrip). in that case
        it will give the precedence to the edges that are on that axis direction (eg XNeg)

        Parameters
        ----------
        start_obj : str
            Name of the starting object.
        end_obj : str
            Name of the ending object.
        port_direction : str, optional 
            Direction of the port to which to give edges precedence when more than two couples 
            are at the same distance. Options are ``"XNeg"``, ``"XPos"``, ``"YNeg"``, 
            ``"YPos`"``, ``"ZNeg"``, and ``"ZPos"``. The default is ``0``.

        Returns
        -------
        list
            List with two edges if present.
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
        """Create two new edges that are parallel and equal to the smallest edge given a parallel couple of edges. 

        Parameters
        ----------
        edgelist : list
            List of two parallel edges.
        portonplane : bool, optional
            Whether edges are to be on the plane orthogonal to the axis direction.
            The default is ''True``.
        axisdir : int, optional
            Axis direction. Options are ``0`` through ``5``. The default is ``0``.
        startobj : str, optional
             Name of the starting object. The default is ``""``.
        endobject : str, optional
             Name of the ending object. The default is ``""``.

        Returns
        -------
        list
            List of the two newly created edges.
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
        """Retrieve the face IDs of a given object ID or object name.

        Parameters
        ----------
        partId : int or str
            Object ID or object name.

        Returns
        -------
        list
            List of faces IDs.
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
        """Retrieve the edge IDs of a given object ID or object name.

        Parameters
        ----------
        partId : int or str
            Object ID or object name.

        Returns
        -------
        list
            List of edge IDs.

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
        """Retrieve the edge IDs of a given face name or face ID.

        Parameters
        ----------
        partId : int or str
            Object ID or object name.

        Returns
        -------
        list
            List of edge IDs.
        """
        oEdgeIDs = self.oeditor.GetEdgeIDsFromFace(partId)
        oEdgeIDs = [int(i) for i in oEdgeIDs]
        return oEdgeIDs

    @aedt_exception_handler
    def get_object_vertices(self, partID):
        """Retrieve the vertex IDs of a given object name or object ID.

        Parameters
        ----------
        partID : int or str
            Object ID or object name.

        Returns
        -------
        list
            List of vertex IDs.

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
        """Retrieve the vertex IDs of a given face ID or face name.

        Parameters
        ----------
        face_id : int or str
            Object ID or object name, which is available 
            using the method `get_object_vertices`.

        Returns
        -------
        list
            List of vertex IDs.
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
        """Get the length of an edge.

        Parameters
        ----------
        edgeID : int
            ID of the edge.

        Returns
        -------
        type
            Edge length.
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
        """Retrieve the vertex IDs of a given edge ID or edge name.

        Parameters
        ----------
        edgeID : int, str
            Object ID or object name, which is available using 
            `get_object_vertices`.

        Returns
        -------
        list
            List of vertex IDs.
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
        """Retrieve a vector of vertex coordinates.

        Parameters
        ----------
        vertex_id : int or str
            ID or name of the vertex.

        Returns
        -------
        list
            List of float values indicating the position. 
            For example, ``[x, y, z]``.
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
        """Retrieve the area of a given face ID.

        Parameters
        ----------
        face_id : int
            ID of the face.

        Returns
        -------
        type
            Float value for the face area.
        """

        area = self.oeditor.GetFaceArea(face_id)
        return area

    @aedt_exception_handler
    def get_face_center(self, face_id):
        """Retrieve the center position for a given planar face ID.

        Parameters
        ----------
        face_id : int
            ID of the face.

        Returns
        -------
        list
            An array as a list of float values containing the
            planar face center position. For example,
            ``[x, y, z]``.

        """
        try:
            c = self.oeditor.GetFaceCenter(face_id)
        except:
            self.messenger.add_warning_message("Non Planar Faces doesn't provide any Face Center")
            return False
        center = [float(i) for i in c]
        return center

    @aedt_exception_handler
    def get_mid_points_on_dir(self, sheet, axisdir):
        """Retrieve midpoints on a given axis direction.

        Parameters
        ----------
        sheet :

        axisdir : int
            Axis direction. Options are ``0`` through ``5``.

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
        """Retrieve the midpoint coordinates of a given edge ID or edge name.

        Parameters
        ----------
        partID : int or str
            Object ID  or object name.

        Returns
        -------
        list
            List of midpoint coordinates. If the edge is not a segment with
            two vertices, an empty list is returned.
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
        """Retrieve the names of the objects that are in contact with the given point.

        Parameters
        ----------
        position :
            ApplicationName.modeler.Position(x,y,z) object
        units : str, optional
            Units, such as ``"m''``. The default is ``None``, in which case the
            model units are used.

        Returns
        -------
        list
            List of object names.
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
        obj_name : str, optional
            Name of the object. The default is ``None``, in which case all 
            objects are searched. 
        units : str, optional
            Units for the position, such as ``"m"``. The default is ``None``, 
            in which case the model units are used.

        Returns
        -------
        type
            Edge ID of the first object touching this position.
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
        """Retrieve edge IDs for a vertex ID.

        Parameters
        ----------
        vertexid : int
            Vertex ID.
        obj_name :
            Name of the object.

        Returns
        -------
        type
            Array of edge IDs.
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
        """Retrieve a face ID from a position.

        Parameters
        ----------
        position :
            ApplicationName.modeler.Position(x,y,z) object
        obj_name : str, optional
            Name of the object. The default is ``None``, in which case all 
            objects are searched. 
        units : str, optional
            Units, such as ``"m"``. The default is ``None``, in which case the
            model units are used. 
        
        Returns
        -------
        type
            Face ID of the first object touching this position.
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
        units : str, optional
           Units, such as ``"m"``. The default is ``None``, in which case the
           model units are used.
        
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

        units : str, optional
            Units, such as ``"m"``. The default is ``None``, in which case the
            model units are used.
        
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
        """Retrieve an object using an edge ID.

        Parameters
        ----------
        lval :  str
            ID of the edge.
        
        """

        objList = []
        objListSheets = self.sheets
        if len(objListSheets) > 0:
            objList.extend(objListSheets)
        objListSolids = self.solids
        if len(objListSolids) > 0:
            objList.extend(objListSolids)
        for obj in objList:
            edgeIDs = list(self.oeditor.GetEdgeIDsFromObject(obj))
            if str(lval) in edgeIDs:
                return obj

        return None

    @aedt_exception_handler
    def _find_object_from_face_id(self, lval):
        """Retrieve an object using a face ID.

        Parameters
        ----------
        lval : str
            ID of the face.
        """
        if self.oeditor is not None:
            objList = []
            objListSheets = self.sheets
            if len(objListSheets) > 0:
                objList.extend(objListSheets)
            objListSolids = self.solids
            if len(objListSolids) > 0:
                objList.extend(objListSolids)
            for obj in objList:
                face_ids = list(self.oeditor.GetFaceIDs(obj))
                if str(lval) in face_ids:
                    return obj

        return None

    @aedt_exception_handler
    def get_edges_on_bunding_box(self, sheets, return_colinear=True, tol=1e-6):
        """Retrieve the edges of the sheets passed in the input that are laying on the bounding box.
        
        This method creates new lines for the detected edges and returns the IDs of these lines.
        If required, only colinear edges are returned.

        Parameters
        ----------
        sheets : int, str, or list
            ID or name for one or more sheets.
        return_colinear : bool, optional
            Whether to return only colinear edges. The default is ''True``. 
            If ``False``, all edges on the bounding box are returned.
        tol : float, optional
            Geometric tolerance. The default is ``1e-6``.

        Returns
        -------
        list
            List of edge IDs.
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
        """Retrieve two edge IDs suitable for the circuit port from a sheet.
                    
        One edge belongs to the sheet passed in the input, and the second edge 
        is the closest edge's coplanar to the first edge (aligned to the XY, YZ, 
        or XZ plane). This method creates new lines for the detected edges and returns
        the IDs of these lines.
        
        This method accepts a one or more sheet objects as input, while 
        the method `get_edges_for_circuit_port` accepts a face ID.
        
        Parameters
        ----------
        sheet : int, str, or list
            ID or name for one or more sheets.
        XY_plane : bool, optional
            Whether the edge's pair are to be on the XY plane.
            The default is ``True``.
        YZ_plane : bool, optional
            Whether the edge's pair are to be on the YZ plane.
            The default is ``True``.
        XZ_plane : bool, optional
            Whether the edge's pair are to be on the XZ plane.
            The default is ``True``.
        allow_perpendicular : bool, optional
            Whether the edge's pair are to be perpendicular.
            The default is ``False``.
        tol : float, optional
            Geometric tolerance. The default is ``1e-6``.

        Returns
        -------
        list
            List of edge IDs.
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
        """Retrieve the names of all solids. """
        return []

    @aedt_exception_handler
    def get_edges_for_circuit_port(self, face_id, XY_plane=True, YZ_plane=True, XZ_plane=True,
                                   allow_perpendicular=False, tol=1e-6):
        """Retrieve two edge IDs suitable for the circuit port.
        
        One edge belongs to the face ID passed in the input, and the second edge 
        is the closest edge's coplanar to the first edge (aligned to the XY, YZ, 
        or XZ plane). This method creates new lines for the detected edges and returns 
        the IDs of these lines.
        
        This method accepts a face ID in the input, while the `get_edges_for_circuit_port_from_port` 
        method accepts one or more sheet objects.
                
        Parameters
        ----------
        face_id :
            ID of the face.
         XY_plane : bool, optional
            Whether the edge's pair are to be on the XY plane.
            The default is ``True``.
        YZ_plane : bool, optional
            Whether the edge's pair are to be on the YZ plane.
            The default is ``True``.
        XZ_plane : bool, optional
            Whether the edge's pair are to be on the XZ plane.
            The default is ``True``.
        allow_perpendicular : bool, optional
            Whether the edge's pair are to be perpendicular.
            The default is ``False``.
        tol : float, optional
            Geometric tolerance. The default is ``1e-6``.
        
        Returns
        -------
        list
            List of edge IDs.

        """
        tol2 = tol**2

        port_edges = self.get_face_edges(face_id)

        # find the bodies to exclude
        port_sheet_midpoint = self.get_face_center(face_id)
        point = self._modeler.Position(port_sheet_midpoint)
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
        """Get the edge ID closest to a given position.

        Parameters
        ----------
        position : list
            List of float values, such as ``[x,y,z]`` or the `ApplicationName.modeler.Position(x,y,z)` object.
        units :
            Units for the position, such as ``"m"``. The default is ``None``, in which case the model units are used.

        Returns
        -------
        type
            Edge ID of the edge closest to this position.

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
