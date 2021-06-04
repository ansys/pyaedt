from ..generic.general_methods import aedt_exception_handler
from .modeler_constants import CoordinateSystemPlane, CoordinateSystemAxis, SweepDraftType

class GeometryOperators(object):
    """ """

    @staticmethod
    @aedt_exception_handler
    def List2list(input_list):
        """

        Parameters
        ----------
        input_list :
            

        Returns
        -------

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
    def parse_dim_arg(string2parse):
        """

        Parameters
        ----------
        string2parse :
            

        Returns
        -------

        """
        return string2parse
    
    @staticmethod
    @aedt_exception_handler
    def cs_plane_str(val):
        """

        Parameters
        ----------
        val :
            

        Returns
        -------

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
        """

        Parameters
        ----------
        val :
            

        Returns
        -------

        """
        if val == CoordinateSystemAxis.XAxis:
            return 'X'
        elif val == CoordinateSystemAxis.YAxis:
            return 'Y'
        else:
            return 'Z'
    
    @staticmethod
    @aedt_exception_handler
    def draft_type_str(val):
        """

        Parameters
        ----------
        val :
            

        Returns
        -------

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
        """

        Parameters
        ----------
        v1 :
            
        v2 :
            

        Returns
        -------

        """
        x = (v1[0] + v2[0]) / 2.
        y = (v1[1] + v2[1]) / 2.
        z = (v1[2] + v2[2]) / 2.
        return [x, y, z]
    
    @staticmethod
    @aedt_exception_handler
    def get_triangle_area(v1, v2, v3):
        """

        Parameters
        ----------
        v1 :
            
        v2 :
            
        v3 :
            

        Returns
        -------

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
        """

        Parameters
        ----------
        a :
            
        b :
            

        Returns
        -------

        """
        c = [a[1] * b[2] - a[2] * b[1],
             a[2] * b[0] - a[0] * b[2],
             a[0] * b[1] - a[1] * b[0]]
        return c
    
    @staticmethod
    @aedt_exception_handler
    def _v_dot(a, b):
        """

        Parameters
        ----------
        a :
            
        b :
            

        Returns
        -------

        """
        c = a[0] * b[0] + a[1] * b[1] + a[2] * b[2]
        return c
    
    @staticmethod
    @aedt_exception_handler
    def v_sub(a, b):
        """

        Parameters
        ----------
        a :
            
        b :
            

        Returns
        -------

        """
        c = [a[0] - b[0],
             a[1] - b[1],
             a[2] - b[2]]
        return c
    
    @staticmethod
    @aedt_exception_handler
    def v_sum(a, b):
        """

        Parameters
        ----------
        a :
            
        b :
            

        Returns
        -------

        """
        c = [a[0] + b[0],
             a[1] + b[1],
             a[2] + b[2]]
        return c
    
    @staticmethod
    @aedt_exception_handler
    def v_norm(a):
        """

        Parameters
        ----------
        a :
            

        Returns
        -------

        """
        m = (a[0]**2 + a[1]**2 + a[2]**2) ** 0.5
        return m
    
    @staticmethod
    @aedt_exception_handler
    def normalize_vector(v):
        """

        Parameters
        ----------
        v :
            

        Returns
        -------

        """
        # normalize a vector to its norm
        norm = GeometryOperators.v_norm(v)
        vn = [i/norm for i in v]
        return vn
    
    @staticmethod
    @aedt_exception_handler
    def v_points(p1, p2):
        """returns the vector from p1 to p2

        Parameters
        ----------
        p1 :
            x1,y1,z1] of p1
        p2 :
            x2,y2,z2] of p2

        Returns
        -------
        type
            vx, vy, vz]

        """
        return GeometryOperators.v_sub(p2, p1)
    
    @staticmethod
    @aedt_exception_handler
    def points_distance(p1, p2):
        """

        Parameters
        ----------
        p1 :
            
        p2 :
            

        Returns
        -------

        """
        v = GeometryOperators.v_points(p1, p2)
        d = GeometryOperators.v_norm(v)
        return d

    @staticmethod
    @aedt_exception_handler
    def find_point_on_plane(pointlists, direction=0):
        """

        Parameters
        ----------
        pointlists :
            
        direction :
             (Default value = 0)

        Returns
        -------

        """
    
        if direction <= 2:
            point = 1e6
            for p in pointlists:
                if p[direction]<point:
                    point = p[direction]
        else:
            point = -1e6
            for p in pointlists:
                if p[direction-3]>point:
                    point = p[direction-3]
        return point
    
    @staticmethod
    @aedt_exception_handler
    def distance_vector(p, a, b):
        """return the vector distance between a point p and a line defined by two points a1 and a2
        The used formula is   d = (a-p)-((a-p)dot p)n
        where a is a point of the line (either a1 or a2) and n is the unit vector in the direction of the line.

        Parameters
        ----------
        p :
            reference point
        a :
            first point of the segment
        b :
            second point of the segment

        Returns
        -------

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
        """Return True if p lies on the segment defined by points a1 and a2,
        otherwise eturn False

        Parameters
        ----------
        p :
            reference point
        a :
            first point of the segment
        b :
            second point of the segment
        tol :
            set the linear tolerance (Default value = 1e-6)

        Returns
        -------

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
        """

        Parameters
        ----------
        a1 :
            first point of segment a
        a2 :
            second point of segment a
        b1 :
            first point of segment b
        b2 :
            second point of segment b
        tol :
            set the linear tolerance (Default value = 1e-6)

        Returns
        -------
        type
            True if it is parallel, False otherwise

        """
        if 1. - GeometryOperators.parallel_coeff(a1,a2,b1,b2) < tol*tol:
            return True
        else:
            return False

    @staticmethod
    @aedt_exception_handler
    def parallel_coeff(a1, a2, b1, b2):
        """

        Parameters
        ----------
        a1 :
            first point of segment a
        a2 :
            second point of segment a
        b1 :
            first point of segment b
        b2 :
            second point of segment b

        Returns
        -------
        type
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
        """Projects a onto b and check if is inside
        Return True if it is inside, False otherwise

        Parameters
        ----------
        a1 :
            first point of segment a
        a2 :
            second point of segment a
        b1 :
            first point of segment b
        b2 :
            second point of segment b

        Returns
        -------
        type
            True if it is inside, False otherwise

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
        """

        Parameters
        ----------
        vertlist1 :
            
        vertlist2 :
            

        Returns
        -------

        """
        sum = 0
        for el in vertlist1:
            for el1 in vertlist2:
                sum += GeometryOperators.points_distance(el, el1)
        return sum/(len(vertlist1)+len(vertlist2))