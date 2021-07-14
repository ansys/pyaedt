# -*- coding: utf-8 -*-
from ..generic.general_methods import aedt_exception_handler
from .modeler_constants import CoordinateSystemPlane, CoordinateSystemAxis, SweepDraftType
import math
import re


class GeometryOperators(object):
    """GeometryOperators class."""

    @staticmethod
    @aedt_exception_handler
    def List2list(input_list):
        """Convert a C# list object to a Python list.
        
        This function performs a deep conversion.

        Parameters
        ----------
        input_list : list
            C# list to convert to a Python list.

        Returns
        -------
        list
            Converted Python list.
        
        """
        output_list = []
        for i in input_list:
            if 'List' in str(type(i)):
                output_list.append(GeometryOperators.List2list(list(i)))
            else:
                output_list.append(i)
        return output_list
    
    @staticmethod
    @aedt_exception_handler
    def parse_dim_arg(string, scale_to_unit=None):
        """Convert a number and unit to a float.

        Angles are converted in radians.

        Parameters
        ----------
        string : str
            String to convert. For example, ``"2mm"``.
        scale_to_unit : str
            Units for the value to convert. For example, ``"mm"``.

        Returns
        -------
        float
            Float value for the converted value and units. For example, ``0.002`.

        Examples
        --------
        Parse `'"2mm"'`.

        >>> from pyaedt.modeler.GeometryOperators import GeometryOperators as go
        >>> go.parse_dim_arg('2mm')
        0.002

        Use the optional argument ``scale_to_unit`` to specify the destination unit.

        >>> go.parse_dim_arg('2mm', scale_to_unit='mm')
        2.0
        
        """
        scaling = {
            "m": 1.0,
            "meter": 1.0,
            "meters": 1.0,
            "dm": 0.1,
            "cm": 1e-2,
            "mm": 1e-3,
            "um": 1e-6,
            "nm": 1e-9,
            "in": 2.54e-2,
            "mil": 2.54e-5,
            "uin": 2.54e-8,
            "ft": 3.048e-1,
            "s": 1.0,
            "sec": 1.0,
            "ms": 1e-3,
            "us": 1e-6,
            "ns": 1e-9,
            "Hz": 1.0,
            "kHz": 1e3,
            "MHz": 1e6,
            "GHz": 1e9,
            "THz": 1e12
        }

        if type(string) is not str:
            try:
                return float(string)
            except ValueError:
                raise TypeError("Input argument is not string nor number")

        if scale_to_unit:
            try:
                sunit = scaling[scale_to_unit]
            except KeyError as e:
                raise e
        else:
            sunit = 1.

        pattern = r"(?P<number>[-+]?(\d+(\.\d*)?|\.\d+)([eE][-+]?\d+)?)\s*(?P<unit>[a-zA-Z]*)"
        m = re.search(pattern, string)

        if m:
            if not m.group("unit"):
                return float(m.group("number"))
            elif m.group("unit") == 'deg':
                return GeometryOperators.deg2rad(float(m.group("number")))
            elif m.group("unit") == 'rad':
                return float(m.group("number"))
            else:
                try:
                    scaling_factor = scaling[m.group("unit")]
                except KeyError as e:
                    raise e
                else:
                    return float(m.group("number")) * scaling_factor / sunit
        else:
            raise TypeError("String is no number")

    @staticmethod
    @aedt_exception_handler
    def cs_plane_str(val):
        """Retrieve a string for a coordinate system plane.

        Parameters
        ----------
        val :
            

        Returns
        -------
        str
           String for the coordinate system plane.

        """
        if val == CoordinateSystemPlane.XYPlane:
            return 'Z'
        elif val == CoordinateSystemPlane.YZPlane:
            return 'X'
        else:
            return 'Y'
    
    @staticmethod
    @aedt_exception_handler
    def cs_axis_str(val):
        """Retrieve a string for a coordinate system axis.

        Parameters
        ----------
        val :
            

        Returns
        -------
        str
            String for the coordinate system axis.

        """
        if val == CoordinateSystemAxis.XAxis or val == 'X':
            return 'X'
        elif val == CoordinateSystemAxis.YAxis  or val == 'Y':
            return 'Y'
        else:
            return 'Z'
    
    @staticmethod
    @aedt_exception_handler
    def draft_type_str(val):
        """Retrieve the draft type.

        Parameters
        ----------
        val :
            

        Returns
        -------
        str
           Type of the draft.

        """
        if val == SweepDraftType.ExtendedDraft:
            return 'Extended'
        elif val == SweepDraftType.RoundDraft:
            return 'Round'
        else:
            return 'Natural'
    
    @staticmethod
    @aedt_exception_handler
    def get_mid_point(v1, v2):
        """Evaluate the midpoint between two points.

        Parameters
        ----------
        v1 : list
            List of ``[x, y, z]`` coordinates for the first point.         
        v2 : list
            List of ``[x, y, z]`` coordinates for the second point. 

        Returns
        -------
        list
            List of ``[x, y, z]`` coordinates for the midpoint. 
        
        """
        x = (v1[0] + v2[0]) / 2.
        y = (v1[1] + v2[1]) / 2.
        z = (v1[2] + v2[2]) / 2.
        return [x, y, z]
    
    @staticmethod
    @aedt_exception_handler
    def get_triangle_area(v1, v2, v3):
        """Evaluate the area of a triangle defined by its three vertices.

        Parameters
        ----------
        v1 : list
            List of ``[x, y, z]`` coordinates for the first vertex.         
        v2 : list
            List of ``[x, y, z]`` coordinates for the second vertex.         
        v3 : list
            List of ``[x, y, z]`` coordinates for the third vertex.         

        Returns
        -------
        float
            Area of the triangle.
        
        """
        a = ((v1[0] - v2[0]) ** 2 + (v1[1] - v2[1]) ** 2 + (v1[2] - v2[2]) ** 2) ** 0.5
        b = ((v2[0] - v3[0]) ** 2 + (v2[1] - v3[1]) ** 2 + (v2[2] - v3[2]) ** 2) ** 0.5
        c = ((v3[0] - v1[0]) ** 2 + (v3[1] - v1[1]) ** 2 + (v3[2] - v1[2]) ** 2) ** 0.5
        s = 0.5 * (a + b + c)
        area = (s * (s - a) * (s - b) * (s - c)) ** 0.5
        return area
    
    @staticmethod
    @aedt_exception_handler
    def v_cross(a, b):
        """Evaluate the cross product of two geometry vectors.

        Parameters
        ----------
        a : list
            List of ``[x, y, z]`` coordinates for the first vector. 
        b : list
            List of ``[x, y, z]`` coordinates for the second vector. 

        Returns
        -------
        list
            List of ``[x, y, z]`` coordinates for the result vector. 
        """
        
        c = [a[1] * b[2] - a[2] * b[1],
             a[2] * b[0] - a[0] * b[2],
             a[0] * b[1] - a[1] * b[0]]
        return c
    
    @staticmethod
    @aedt_exception_handler
    def _v_dot(a, b):
        """Evaluate the dot product between two geometry vectors.

        Parameters
        ----------
        a : list
            List of ``[x, y, z]`` coordinates for the first vector. 
        b : list
            List of ``[x, y, z]`` coordinates for the second vector. 

        Returns
        -------
        float
            Result of the dot product.
        
        """
        c = a[0] * b[0] + a[1] * b[1] + a[2] * b[2]
        return c

    @staticmethod
    @aedt_exception_handler
    def v_dot(a, b):
        """Evaluate the dot product between two geometry vectors.

        Parameters
        ----------
        a : list
            List of ``[x, y, z]`` coordinates for the first vector. 
        b : list
            List of ``[x, y, z]`` coordinates for the second vector. 

        Returns
        -------
        float
            Result of the dot product.
        
        """
        return GeometryOperators._v_dot(a, b)

    @staticmethod
    @aedt_exception_handler
    def v_prod(s, v):
        """Evaluate the product between a scalar value and a vector.
                
        Parameters
        ----------
        s : float
            Scalar value.
        v : list
            List of values for the vector in the format ``[v1, v2,..., vn]``.
            The vector can be any length.

        Returns
        -------
        list
            List of values for the result vector. This list is the 
            same length as the list for the input vector.
        
        """
        r = [s * i for i in v]
        return r

    @staticmethod
    @aedt_exception_handler
    def v_sub(a, b):
        """Evaluate two geometry vectors by subtracting them (a-b).

        Parameters
        ----------
        a : list
            List of ``[x, y, z]`` coordinates for the first vector. 
        b : list
            List of ``[x, y, z]`` coordinates for the second vector. 

        Returns
        -------
        list
            List of ``[x, y, z]`` coordinates for the result vector.
        
        """
        c = [a[0] - b[0],
             a[1] - b[1],
             a[2] - b[2]]
        return c
    
    @staticmethod
    @aedt_exception_handler
    def v_sum(a, b):
        """Evaluate two geometry vectors by adding them (a+b).

        Parameters
        ----------
        a : list
            List of ``[x, y, z]`` coordinates for the first vector. 
        b : list
            List of ``[x, y, z]`` coordinates for the second vector. 

        Returns
        -------
        list
            List of ``[x, y, z]`` coordinates for the result vector.
        
        """
        c = [a[0] + b[0],
             a[1] + b[1],
             a[2] + b[2]]
        return c
    
    @staticmethod
    @aedt_exception_handler
    def v_norm(a):
        """ Evaluate the Euclidean norm of a geometry vector.

        Parameters
        ----------
         a : list
            List of ``[x, y, z]`` coordinates for the vector. 
        
        Returns
        -------
        float
            Evaluated norm in the same unit as the coordinates for the input vector.
        
        """
        m = (a[0]**2 + a[1]**2 + a[2]**2) ** 0.5
        return m
    
    @staticmethod
    @aedt_exception_handler
    def normalize_vector(v):
        """Normalize a geometry vector.

        Parameters
        ----------
        v : list
            List of ``[x, y, z]`` coordinates for vector.

        Returns
        -------
        list
            List of ``[x, y, z]`` coordinates for the normalized vector.
        
        """
        # normalize a vector to its norm
        norm = GeometryOperators.v_norm(v)
        vn = [i/norm for i in v]
        return vn
    
    @staticmethod
    @aedt_exception_handler
    def v_points(p1, p2):
        """Return the vector from one point to another point.

        Parameters
        ----------
        p1 : list
            List of ``[x1,y1,z1]`` coordinates for the first point.
        p2 : list
            List of ``[x2,y2,z2]`` coordinates for second point.

        Returns
        -------
        list
            List of ``[vx, vy, vz]``coordinates for the vector from the first point to the second point.
        """
        return GeometryOperators.v_sub(p2, p1)
    
    @staticmethod
    @aedt_exception_handler
    def points_distance(p1, p2):
        """Evaluate the distance between two points expressed as their Cartesian coordinates.

        Parameters
        ----------
        p1 : list
            List of ``[x1,y1,z1]"`` coordinates for the first point.
        p2 : list
            List of ``[x2,y2,z2] coordinates for the second ppint.

        Returns
        -------
        float
            Distance between the two points in the same unit as the coordinates for the points.
        
        """
        v = GeometryOperators.v_points(p1, p2)
        d = GeometryOperators.v_norm(v)
        return d

    @staticmethod
    @aedt_exception_handler
    def find_point_on_plane(pointlists, direction=0):
        """Find a point on a plane.

        Parameters
        ----------
        pointlists : list
            List of points.          
        direction : int, optional
             The default is ``0``.

        Returns
        -------
        list 
           
        """
    
        if direction <= 2:
            point = 1e6
            for p in pointlists:
                if p[direction] < point:
                    point = p[direction]
        else:
            point = -1e6
            for p in pointlists:
                if p[direction-3] > point:
                    point = p[direction-3]
        return point
    
    @staticmethod
    @aedt_exception_handler
    def distance_vector(p, a, b):
        """Evaluate the vector distance between point ``p`` and a line defined by two points, ``a`` and ``b``.
        
        .. note::
        The formula is  ``d = (a-p)-((a-p)dot p)n``, where ``a`` is a point of the line (either ``a`` or ``b``) 
        and ``n`` is the unit vector in the direction of the line.

        Parameters
        ----------
        p : list
            List of ``[x, y, z]`` coordinates for the reference point.
        a : list
            List of ``[x, y, z]`` coordinates for the first point of the segment.
        b : list
            List of ``[x, y, z]`` coordinates for the second point of the segment.

        Returns
        -------
        list
            List of ``[x, y, z]`` coordinates for the distance vector.
        
        """
        v1 = GeometryOperators.v_points(a, b)
        n = [i / GeometryOperators.v_norm(v1) for i in v1]
        v2 = GeometryOperators.v_sub(a, p)
        s1 = GeometryOperators._v_dot(v2, n)
        v3 = [i * s1 for i in n]
        vd = GeometryOperators.v_sub(v2, v3)
        return vd
    
    @staticmethod
    @aedt_exception_handler
    def is_between_points(p, a, b, tol=1e-6):
        """Check if a point lies on the segment defined by two points.

        Parameters
        ----------
        p : list
            List of ``[x, y, z]`` coordinates for the reference point ``p``.
        a : list
            List of ``[x, y, z]`` coordinates for the first point of the segment.
        b : list
            List of ``[x, y, z]`` coordinates for the second point of the segment.   
        tol : float
            Linear tolerance. The default value is ``1e-6``.

        Returns
        -------
        bool
            ``True`` when the point lies on the segment defined by the two points, ``False`` otherwise.
	
        """
        v1 = GeometryOperators.v_points(a, b)
        v2 = GeometryOperators.v_points(a, p)
        if abs(GeometryOperators.v_norm(GeometryOperators.v_cross(v1, v2))) > tol:
            return False   # not colinear
        t1 = GeometryOperators._v_dot(v1, v2)
        t2 = GeometryOperators._v_dot(v1, v1)
        if t1 < 0 or t1 > t2:
            return False
        else:
            return True
    
    @staticmethod
    @aedt_exception_handler
    def is_parallel(a1, a2, b1, b2, tol=1e-6):
        """Check if a segment defined by two points is parallel to a segment defined by two other points.

        Parameters
        ----------
        a1 : list
            List of ``[x, y, z]`` coordinates for the first point of the fiirst segment.
        a2 : list
            List of ``[x, y, z]`` coordinates for the second point of the first segment.
        b1 : list
            List of ``[x, y, z]`` coordinates for the first point of the second segment.
        b2 : list
            List of ``[x, y, z]`` coordinates for the second point of the second segment.
        tol : float
            Linear tolerance. The default value is ``1e-6``.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.
        
        """
        if 1. - GeometryOperators.parallel_coeff(a1, a2, b1, b2) < tol*tol:
            return True
        else:
            return False

    @staticmethod
    @aedt_exception_handler
    def parallel_coeff(a1, a2, b1, b2):
        """ADD DESCRIPTION.

        Parameters
        ----------
        a1 : list
            List of ``[x, y, z]`` coordinates for the first point of the first segment.
        a2 : list
            List of ``[x, y, z]`` coordinates for the second point of the first segment.
        b1 : list
            List of ``[x, y, z]`` coordinates for the first point of the second segment.
        b2 : list
            List of ``[x, y, z]`` coordinates for the second point of the second segment.

        Returns
        -------
        float
            _vdot of 4 vertex of 2 segments
        """
        va = GeometryOperators.v_points(a1, a2)
        vb = GeometryOperators.v_points(b1, b2)
        an = GeometryOperators.v_norm(va)
        bn = GeometryOperators.v_norm(vb)
        var = GeometryOperators._v_dot(va, vb) / (an * bn)
        return abs(var)

    @staticmethod
    @aedt_exception_handler
    def is_projection_inside(a1, a2, b1, b2):
        """Project a segment onto another segment and check if the projected segment is inside it.
        
        Parameters
        ----------
        a1 : list
            List of ``[x, y, z]`` coordinates for the first point of the projected segment.
        a2 : list
            List of ``[x, y, z]`` coordinates for the second point of the projected segment.
        b1 : list
            List of ``[x, y, z]`` coordinates for the first point of the other segment.
        b2 : list
            List of ``[x, y, z]`` coordinates for the second point of the other segment.

        Returns
        -------
        bool
            ``True`` when the projected segment is inside the other segmennt, ``False`` otherwise.
        
        """
        if not GeometryOperators.is_parallel(a1, a2, b1, b2):
            return False
        d = GeometryOperators.distance_vector(a1, b1, b2)
        a1n = GeometryOperators.v_sum(a1, d)
        a2n = GeometryOperators.v_sum(a2, d)
        if not GeometryOperators.is_between_points(a1n, b1, b2):
            return False
        if not GeometryOperators.is_between_points(a2n, b1, b2):
            return False
        return True
    
    @staticmethod
    @aedt_exception_handler
    def arrays_positions_sum(vertlist1, vertlist2):
        """ADD DESCRIPTION.

        Parameters
        ----------
        vertlist1 : list
            
        vertlist2 : list

        Returns
        -------
        float
        
        """
        s = 0
        for el in vertlist1:
            for el1 in vertlist2:
                s += GeometryOperators.points_distance(el, el1)
        return s/(len(vertlist1)+len(vertlist2))

    @staticmethod
    @aedt_exception_handler
    def v_angle(a, b):
        """Evaluate the angle between two geometry vectors.

        Parameters
        ----------
        a : list
            List of ``[x, y, z]`` coordinates for the first vector.
        b : list
            List of ``[x, y, z]`` coordinates for the second vector.

        Returns
        -------
        float
            Angle in radians.
        
        """
        d = GeometryOperators.v_dot(a, b)
        an = GeometryOperators.v_norm(a)
        bn = GeometryOperators.v_norm(b)
        theta = math.acos(d / (an*bn))
        return theta

    @staticmethod
    @aedt_exception_handler
    def pointing_to_axis(x_pointing, y_pointing):
        """Retrieve the axes from the HFSS X axis and Y pointing axis as per the definition of the AEDT interface coordinate system.

        Parameters
        ----------
        x_pointing : list
            List of ``[x, y, z]`` coordinates for the X axis.

        y_pointing : list
            List of ``[x, y, z]`` coordinates for the Y pointing axis.

        Returns
        -------
        tuple
            ``[Xx, Xy, Xz], [Yx, Yy, Yz], [Zx, Zy, Zz]`` of the three axes (normalized).
        """
        
        xp = GeometryOperators.normalize_vector(x_pointing)

        tp = GeometryOperators.v_dot(y_pointing, xp)
        ypt = GeometryOperators.v_sub(y_pointing, GeometryOperators.v_prod(tp, xp))
        yp = GeometryOperators.normalize_vector(ypt)

        zpt = GeometryOperators.v_cross(xp, yp)
        zp = GeometryOperators.normalize_vector(zpt)

        return xp, yp, zp

    @staticmethod
    @aedt_exception_handler
    def axis_to_euler_zxz(x, y, z):
        """Finds the Euler angles of a frame defined by X, Y, and Z axes, following the rotation sequence ZXZ.
        
        Provides assumption for the gimbal lock problem.

        Parameters
        ----------
        x : list
            List of ``[Xx, Xy, Xz]`` coordinates for the X axis.
        y : list
            List of ``[Yx, Yy, Yz]`` coordinates for the Y axis. 
        z : list
            List of ``[Zx, Zy, Zz]`` coordinates for the Z axis.

        Returns
        -------
        tuple
            (phi, theta, psi) containing the Euler angles in radians.
        
        """
        x1 = x[0]
        x2 = x[1]
        x3 = x[2]
        y3 = y[2]
        z1 = z[0]
        z2 = z[1]
        z3 = z[2]
        if z == [0, 0, 1]:
            phi = GeometryOperators.atan2(x2, x1)
            theta = 0.
            psi = 0.
        elif z == [0, 0, -1]:
            phi = GeometryOperators.atan2(x2, x1)
            theta = math.pi
            psi = 0.
        else:
            phi = GeometryOperators.atan2(z1, -z2)
            theta = math.acos(z3)
            psi = GeometryOperators.atan2(x3, y3)
        return phi, theta, psi

    @staticmethod
    @aedt_exception_handler
    def axis_to_euler_zyz(x, y, z):
        """Finds the Euler angles of a frame defined by X, Y, and Z axes, following rotation sequence ZYZ.
        
        Provides assumption for the gimbal lock problem.

        Parameters
        ----------
        x : list
            List of ``[Xx, Xy, Xz]`` coordinates for the X axis.
        y : list
            List of ``[Yx, Yy, Yz]`` coordinates for the Y axis. 
        z : list
            List of ``[Zx, Zy, Zz]`` coordinates for the Z axis.
        
        Returns
        -------
        tuple
            (phi, theta, psi) containing the Euler angles in radians.
        
        """
        x1 = x[0]
        x2 = x[1]
        x3 = x[2]
        y3 = y[2]
        z1 = z[0]
        z2 = z[1]
        z3 = z[2]
        if z == [0, 0, 1]:
            phi = GeometryOperators.atan2(x2, x1)
            theta = 0.
            psi = 0.
        elif z == [0, 0, -1]:
            phi = GeometryOperators.atan2(x2, x1)
            theta = math.pi
            psi = 0.
        else:
            phi = GeometryOperators.atan2(z2, z1)
            theta = math.acos(z3)
            psi = GeometryOperators.atan2(y3, -x3)
        return phi, theta, psi

    @staticmethod
    @aedt_exception_handler
    def quaternion_to_axis(q):
        """Convert a quaternion to a rotated frame defined by X, Y, and Z axes.

        Parameters
        ----------
        q : list
            List of ``[q1, q2, q3, q4]`` coordinates for the quaternion.

        Returns
        -------
        tuple
            [Xx, Xy, Xz], [Yx, Yy, Yz], [Zx, Zy, Zz] of the three axes (normalized).
        
        """
        q1 = q[0]
        q2 = q[1]
        q3 = q[2]
        q4 = q[3]

        m11 = q1*q1 + q2*q2 - q3*q3 - q4*q4
        m12 = 2. * (q2*q3 - q1*q4)
        m13 = 2. * (q2*q4 + q1*q3)

        m21 = 2. * (q2*q3 + q1*q4)
        m22 = q1*q1 - q2*q2 + q3*q3 - q4*q4
        m23 = 2. * (q3*q4 - q1*q2)

        m31 = 2. * (q2*q4 - q1*q3)
        m32 = 2. * (q3*q4 + q1*q2)
        m33 = q1*q1 - q2*q2 - q3*q3 + q4*q4

        x = GeometryOperators.normalize_vector([m11, m21, m31])
        y = GeometryOperators.normalize_vector([m12, m22, m32])
        z = GeometryOperators.normalize_vector([m13, m23, m33])

        return x, y, z

    @staticmethod
    @aedt_exception_handler
    def quaternion_to_axis_angle(q):
        """Convert a quaternion to the axis angle rotation formulation.

        Parameters
        ----------
        q : list
            List of ``[q1, q2, q3, q4]`` coordinates for the quaternion.

        Returns
        -------
        tuple
            ([ux, uy, uz], theta) containing the rotation axes expressed as X, Y, Z components of the unit vector ``u``
            and the rotation angle theta expressed in radians.
        
        """
        q1 = q[0]
        q2 = q[1]
        q3 = q[2]
        q4 = q[3]
        n = (q2*q2 + q3*q3 + q4*q4) ** 0.5
        u = [q2/n, q3/n, q4/n]
        theta = 2.0 * GeometryOperators.atan2(n, q1)
        return u, theta

    @staticmethod
    @aedt_exception_handler
    def axis_angle_to_quaternion(u, theta):
        """Convert the axis angle rotation formulation to a quaternion.

        Parameters
        ----------
        u : list
            List of ``[ux, uy, uz]`` coordinates for the rotation axis.

        theta : float
            Angle of rotation in radians.

        Returns
        -------
        list
            List of ``[q1, q2, q3, q4]`` coordinates for the quaternion.
        
        """
        un = GeometryOperators.normalize_vector(u)
        s = math.sin(theta * 0.5)
        q1 = math.cos(theta * 0.5)
        q2 = un[0] * s
        q3 = un[1] * s
        q4 = un[2] * s
        return [q1, q2, q3, q4]

    @staticmethod
    @aedt_exception_handler
    def quaternion_to_euler_zxz(q):
        """Convert a quaternion to Euler angles following rotation sequence ZXZ.

        Parameters
        ----------
        q : list
            List of ``[q1, q2, q3, q4]`` coordinates for the quaternion.

        Returns
        -------
        tuple
            (phi, theta, psi) containing the Euler angles in radians.
        
        """
        q1 = q[0]
        q2 = q[1]
        q3 = q[2]
        q4 = q[3]
        m13 = 2. * (q2*q4 + q1*q3)
        m23 = 2. * (q3*q4 - q1*q2)
        m33 = q1*q1 - q2*q2 - q3*q3 + q4*q4
        m31 = 2. * (q2*q4 - q1*q3)
        m32 = 2. * (q3*q4 + q1*q2)
        phi = GeometryOperators.atan2(m13, -m23)
        theta = GeometryOperators.atan2((1.-m33*m33)**0.5, m33)
        psi = GeometryOperators.atan2(m31, m32)
        return phi, theta, psi

    @staticmethod
    @aedt_exception_handler
    def euler_zxz_to_quaternion(phi, theta, psi):
        """Convert the Euler angles following rotation sequence ZXZ to a quaternion.

        Parameters
        ----------
        phi : float
            Euler angle psi in radians.
        theta : float
            Euler angle theta in radians.
        psi : float
            Euler angle phi in radians.

        Returns
        -------
        list
            List of ``[q1, q2, q3, q4]`` coordinates for the quaternion.
        
        """
        t1 = phi
        t2 = theta
        t3 = psi
        c = math.cos(t2 * 0.5)
        s = math.sin(t2 * 0.5)
        q1 = c * math.cos((t1+t3) * 0.5)
        q2 = s * math.cos((t1-t3) * 0.5)
        q3 = s * math.sin((t1-t3) * 0.5)
        q4 = c * math.sin((t1+t3) * 0.5)
        return [q1, q2, q3, q4]

    @staticmethod
    @aedt_exception_handler
    def quaternion_to_euler_zyz(q):
        """Convert a quaternion to Euler angles following rotation sequence ZYZ.

        Parameters
        ----------
        q : list
            List of ``[q1, q2, q3, q4]`` coordinates for the quaternion.
            
        Returns
        -------
        tuple
            (phi, theta, psi) containing the Euler angles in radians.
        
        """
        q1 = q[0]
        q2 = q[1]
        q3 = q[2]
        q4 = q[3]
        m13 = 2. * (q2*q4 + q1*q3)
        m23 = 2. * (q3*q4 - q1*q2)
        m33 = q1*q1 - q2*q2 - q3*q3 + q4*q4
        m31 = 2. * (q2*q4 - q1*q3)
        m32 = 2. * (q3*q4 + q1*q2)
        phi = GeometryOperators.atan2(m23, m13)
        theta = GeometryOperators.atan2((1.-m33*m33)**0.5, m33)
        psi = GeometryOperators.atan2(m32, -m31)
        return phi, theta, psi

    @staticmethod
    @aedt_exception_handler
    def euler_zyz_to_quaternion(phi, theta, psi):
        """Convert the Euler angles following rotation sequence ZYZ to a quaternion.

        Parameters
        ----------
        phi : float
            Euler angle psi in radians.
        theta : float
            Euler angle theta in radians.
        psi : float
            Euler angle phi in radians.

        Returns
        -------
        list
            List of ``[q1, q2, q3, q4]`` coordinates for the quaternion.
        
        """
        t1 = phi
        t2 = theta
        t3 = psi
        c = math.cos(t2 * 0.5)
        s = math.sin(t2 * 0.5)
        q1 = c * math.cos((t1+t3) * 0.5)
        q2 = -s * math.sin((t1-t3) * 0.5)
        q3 = s * math.cos((t1-t3) * 0.5)
        q4 = c * math.sin((t1+t3) * 0.5)
        return [q1, q2, q3, q4]

    @staticmethod
    @aedt_exception_handler
    def deg2rad(angle):
        """Convert the angle from degrees to radians.

        Parameters
        ----------
        angle : float
            Angle in degrees.

        Returns
        -------
        float
            Angle in radians.
        
        """
        pi = math.pi
        return angle / 180. * pi

    @staticmethod
    @aedt_exception_handler
    def rad2deg(angle):
        """Convert the angle from radians to degrees.

        Parameters
        ----------
        angle : float
            Angle in radians.

        Returns
        -------
        float
            Angle in degrees.
        
        """
        pi = math.pi
        return angle * 180. / pi

    @staticmethod
    @aedt_exception_handler
    def atan2(y, x):
        """Implementation of atan2 that does not suffer from the following issues:
        math.atan2(0.0, 0.0) = 0.0
        math.atan2(-0.0, 0.0) = -0.0
        math.atan2(0.0, -0.0) = 3.141592653589793
        math.atan2(-0.0, -0.0) = -3.141592653589793
        and returns always 0.0

        Parameters
        ----------
        y : float
            Y-axis value for atan2.

        x : float
            X-axis value for atan2.

        Returns
        -------
        float
            atan2(y, x)
        
        """
        eps = 7./3. - 4./3. - 1.
        if abs(y) < eps:
            y = 0.0
        if abs(x) < eps:
            x = 0.0
        return math.atan2(y, x)

    @staticmethod
    @aedt_exception_handler
    def q_prod(p, q):
        """Evaluate the product of two quaternions, ``p`` and ``q``, defined as:
            
            * p = p0 + p' = p0 + ip1 + jp2 + kp3
            
            * q = q0 + q' = q0 + iq1 + jq2 + kq3

            r = pq = p0q0 - p' • q' + p0q' + q0p' + p' x q'

        Parameters
        ----------
        p : list
            List of ``[p1, p2, p3, p4]`` coordinates for quaternion ``p``.

        q : list
            List of ``[p1, p2, p3, p4]`` coordinates for quaternion ``q``.

        Returns
        -------
        list
            List of [r1, r2, r3, r4] coordinates for the result quaternion.
        
        """
        p0 = p[0]
        pv = p[1:4]
        q0 = q[0]
        qv = q[1:4]

        r0 = p0 * q0 - GeometryOperators.v_dot(pv, qv)

        t1 = GeometryOperators.v_prod(p0, qv)
        t2 = GeometryOperators.v_prod(q0, pv)
        t3 = GeometryOperators.v_cross(pv, qv)
        rv = GeometryOperators.v_sum(t1, GeometryOperators.v_sum(t2, t3))

        return [r0, rv[0], rv[1], rv[2]]

    @staticmethod
    @aedt_exception_handler
    def q_rotation(v, q):
        """Evaluate the rotation of a vector defined by a quaternion.

        Evaluated as:
        
        ``q = q0 + q' = q0 + iq1 + jq2 + kq3``
        
        ``w = qvq* = (q0^2 - |q'|^2)v + 2(q' • v)q' + 2q0(q' x v)``

        Parameters
        ----------
        v : list
            List of ``[v1, v2, v3]`` coordinates for the vector. 

        q : list
            List of ``[q1, q2, q3, q4]``coordinates for the quaternion. 

        Returns
        -------
        list
            List of ``[w1, w2, w3]`` coordinates for the result vector ``w``.
        
        """
        q0 = q[0]
        qv = q[1:4]

        c1 = q0*q0 - (qv[0]*qv[0] + qv[1]*qv[1] + qv[2]*qv[2])
        t1 = GeometryOperators.v_prod(c1, v)

        c2 = 2. * GeometryOperators.v_dot(qv, v)
        t2 = GeometryOperators.v_prod(c2, qv)

        t3 = GeometryOperators.v_cross(qv, v)
        t4 = GeometryOperators.v_prod(2. * q0, t3)

        w = GeometryOperators.v_sum(t1, GeometryOperators.v_sum(t2, t4))

        return w

    @staticmethod
    @aedt_exception_handler
    def q_rotation_inv(v, q):
        """Evaluate the inverse rotation of a vector that is defined by a quaternion.
        
        It can also be the rotation of the coordinate frame with respect to the vector.

            q = q0 + q' = q0 + iq1 + jq2 + kq3
            q* = q0 - q' = q0 - iq1 - jq2 - kq3
            w = q*vq

        Parameters
        ----------
        v : list
            List of ``[v1, v2, v3]`` coordinates for the vector.

        q : list
            List of ``[q1, q2, q3, q4]`` coordinates for the quaternion.

        Returns
        -------
        list
            List of ``[w1, w2, w3]`` coordinates for the vector.
        
        """
        q1 = [q[0], -q[1], -q[2], -q[3]]
        return GeometryOperators.q_rotation(v, q1)

    @staticmethod
    @aedt_exception_handler
    def get_polygon_centroid(pts):
        """Evaluate the centroid of a polygon defined by its points.

        Parameters
        ----------
        pts : list
            List of points, with each point defined by its ``[x,y,z]`` coordinates.

        Returns
        -------
        list
            List of [x,y,z] coordinates for the centroid of the polygon.
        
        """
        sx = sy = sz = sl = sl2 = 0
        for i in range(len(pts)):  # counts from 0 to len(points)-1
            x0, y0, z0 = pts[i - 1]  # in Python points[-1] is last element of points
            x1, y1, z1 = pts[i]
            L = ((x1 - x0) ** 2 + (y1 - y0) ** 2) ** 0.5
            sx += (x0 + x1) / 2 * L
            sy += (y0 + y1) / 2 * L
            L2 = ((z1 - z0) ** 2 + (x1 - x0) ** 2) ** 0.5
            sz += (z0 + z1) / 2 * L2
            sl += L
            sl2 += L2
        xc = sx / sl
        yc = sy / sl
        zc = sz / sl2

        return [xc, yc, zc]
