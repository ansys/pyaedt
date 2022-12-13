import math

from pyaedt.generic.general_methods import pyaedt_function_handler
from pyaedt.modeler import GeometryOperators


class EDBPrimitives(object):
    """Manages EDB functionalities for a primitives.
    It Inherits EDB Object properties.

    Examples
    --------
    >>> from pyaedt import Edb
    >>> edb = Edb(myedb, edbversion="2021.2")
    >>> edb_prim = edb.core_primitives.primitives[0]
    >>> edb_prim.is_void # Class Property
    >>> edb_prim.IsVoid() # EDB Object Property
    """

    def __getattr__(self, key):
        try:
            return self[key]
        except:
            try:
                return getattr(self.primitive_object, key)
            except AttributeError:
                raise AttributeError("Attribute not present")

    def __init__(self, raw_primitive, core_app):
        self._app = core_app
        self._core_stackup = core_app.stackup
        self._core_net = core_app.core_nets
        self.primitive_object = raw_primitive

    @pyaedt_function_handler()
    def area(self, include_voids=True):
        """Return the total area.

        Parameters
        ----------
        include_voids : bool, optional
            Either if the voids have to be included in computation.
            The default value is ``True``.
        Returns
        -------
        float
        """
        area = self.primitive_object.GetPolygonData().Area()
        if include_voids:
            for el in self.primitive_object.Voids:
                area -= el.GetPolygonData().Area()
        return area

    @property
    def is_void(self):
        """Either if the primitive is a void or not.

        Returns
        -------
        bool
        """
        if not hasattr(self.primitive_object, "IsVoid"):
            return False
        return self.primitive_object.IsVoid()

    @property
    def id(self):
        """Primitive ID.

        Returns
        -------
        int
        """
        return self.GetId()

    @staticmethod
    def _eval_arc_points(p1, p2, h, n=6, tol=1e-12):
        """Get the points of the arc

        Parameters
        ----------
        p1 : list
            Arc starting point.
        p2 : list
            Arc ending point.
        h : float
            Arc height.
        n : int
            Number of points to generate along the arc.
        tol : float
            Geometric tolerance.

        Returns
        -------
        list, list
            Points generated along the arc.
        """
        # fmt: off
        if abs(h) < tol:
            return [], []
        elif h > 0:
            reverse = False
            x1 = p1[0]
            y1 = p1[1]
            x2 = p2[0]
            y2 = p2[1]
        else:
            reverse = True
            x1 = p2[0]
            y1 = p2[1]
            x2 = p1[0]
            y2 = p1[1]
            h *= -1
        xa = (x2 - x1) / 2
        ya = (y2 - y1) / 2
        xo = x1 + xa
        yo = y1 + ya
        a = math.sqrt(xa ** 2 + ya ** 2)
        if a < tol:
            return [], []
        r = (a ** 2) / (2 * h) + h / 2
        if abs(r - a) < tol:
            b = 0
            th = 2 * math.asin(1)  # chord angle
        else:
            b = math.sqrt(r ** 2 - a ** 2)
            th = 2 * math.asin(a / r)  # chord angle

        # center of the circle
        xc = xo + b * ya / a
        yc = yo - b * xa / a

        alpha = math.atan2((y1 - yc), (x1 - xc))
        xr = []
        yr = []
        for i in range(n):
            i += 1
            dth = (float(i) / (n + 1)) * th
            xi = xc + r * math.cos(alpha - dth)
            yi = yc + r * math.sin(alpha - dth)
            xr.append(xi)
            yr.append(yi)

        if reverse:
            xr.reverse()
            yr.reverse()
        # fmt: on
        return xr, yr

    def _get_points_for_plot(self, my_net_points, num):
        """
        Get the points to be plotted.
        """
        # fmt: off
        x = []
        y = []
        for i, point in enumerate(my_net_points):
            if not self.is_arc(point):
                x.append(point.X.ToDouble())
                y.append(point.Y.ToDouble())
                # i += 1
            else:
                arc_h = point.GetArcHeight().ToDouble()
                p1 = [my_net_points[i - 1].X.ToDouble(), my_net_points[i - 1].Y.ToDouble()]
                if i + 1 < len(my_net_points):
                    p2 = [my_net_points[i + 1].X.ToDouble(), my_net_points[i + 1].Y.ToDouble()]
                else:
                    p2 = [my_net_points[0].X.ToDouble(), my_net_points[0].Y.ToDouble()]
                x_arc, y_arc = self._eval_arc_points(p1, p2, arc_h, num)
                x.extend(x_arc)
                y.extend(y_arc)
                # i += 1
        # fmt: on
        return x, y

    @pyaedt_function_handler()
    def points(self, arc_segments=6):
        """Return the list of points with arcs converted to segments.

        Parameters
        ----------
        arc_segments : int
            Number of facets to convert an arc. Default is `6`.

        Returns
        -------
        list, list
            x and y list of points.
        """
        try:
            my_net_points = list(self.primitive_object.GetPolygonData().Points)
            xt, yt = self._get_points_for_plot(my_net_points, arc_segments)
            if not xt:
                return []
            x, y = GeometryOperators.GeometryOperators.orient_polygon(xt, yt, clockwise=True)
            return x, y
        except:
            x = []
            y = []
        return x, y

    @property
    def voids(self):
        """Return a list of voids of the given primitive if any.

        Returns
        -------
        list of :class:`pyaedt.edb_core.edb_data.primitives_data.EDBPrimitives`
        """
        voids = []
        for void in self.primitive_object.Voids:
            voids.append(EDBPrimitives(void, self._app))
        return voids

    @pyaedt_function_handler()
    def points_raw(self):
        """Return a list of Edb points.

        Returns
        -------
        list
            Edb Points.
        """
        points = []
        try:
            my_net_points = list(self.primitive_object.GetPolygonData().Points)
            for point in my_net_points:
                points.append(point)
            return points
        except:
            return points

    @pyaedt_function_handler()
    def is_arc(self, point):
        """Either if a point is an arc or not.

        Returns
        -------
        bool
        """
        return point.IsArc()

    @property
    def type(self):
        """Return the type of the primitive.
        Allowed outputs are `"Circle"`, `"Rectangle"`,`"Polygon"`,`"Path"`,`"Bondwire"`.

        Returns
        -------
        str
        """
        types = ["Circle", "Path", "Polygon", "Rectangle", "Bondwire"]
        str_type = self.primitive_object.ToString().split(".")
        if str_type[-1] in types:
            return str_type[-1]
        return None

    @property
    def net(self):
        """Return EDB Net Object."""
        return self.primitive_object.GetNet()

    @property
    def net_name(self):
        """Get or Set the primitive net name.

        Returns
        -------
        str
        """
        return self.net.GetName()

    @net_name.setter
    def net_name(self, val):
        if not isinstance(val, str):
            try:
                self.primitive_object.SetNet(val)
            except:
                raise AttributeError("Value inserted not found. Input has to be layer name or net object.")
        elif val in self._core_net.nets:
            net = self._core_net.nets[val].net_object
            self.primitive_object.SetNet(net)
        else:
            raise AttributeError("Value inserted not found. Input has to be layer name or net object.")

    @property
    def layer(self):
        """Get the primitive edb layer object."""
        return self.primitive_object.GetLayer()

    @property
    def layer_name(self):
        """Get or Set the primitive layer name.

        Returns
        -------
        str
        """
        return self.layer.GetName()

    @layer_name.setter
    def layer_name(self, val):
        if val in self._core_stackup.stackup_layers.layers:
            lay = self._core_stackup.stackup_layers.layers[val]._edb_layer
            self.primitive_object.SetLayer(lay)
        elif not isinstance(val, str):
            try:
                self.primitive_object.SetLayer(val)
            except:
                raise AttributeError("Value inserted not found. Input has to be layer name or layer object.")
        else:
            raise AttributeError("Value inserted not found. Input has to be layer name or layer object.")

    @pyaedt_function_handler()
    def delete(self):
        """Delete this primtive."""
        return self.primitive_object.Delete()

    @pyaedt_function_handler()
    def get_connected_object_id_set(self):
        """Produce a list of all geometries physically connected to a given layout object.

        Returns
        -------
        list
            Found connected objects IDs with Layout object.
        """
        layoutInst = self.primitive_object.GetLayout().GetLayoutInstance()
        layoutObjInst = layoutInst.GetLayoutObjInstance(self.primitive_object, None)  # 2nd arg was []
        return [loi.GetLayoutObj().GetId() for loi in layoutInst.GetConnectedObjects(layoutObjInst).Items]

    @pyaedt_function_handler()
    def convert_to_polygon(self):
        """Convert path to polygon.

        Returns
        -------
        Converted polygon.

        """
        if self.type == "Path":
            polygon_data = self.primitive_object.GetPolygonData()
            polygon = self._app.core_primitives.create_polygon(polygon_data, self.layer_name, [], self.net_name)
            self.primitive_object.Delete()
            return polygon
