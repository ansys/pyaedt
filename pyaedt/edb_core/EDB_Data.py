import math
import os
import time
import warnings
from collections import OrderedDict

from pyaedt.edb_core.general import convert_py_list_to_net_list
from pyaedt.generic.constants import BasisOrder
from pyaedt.generic.constants import CutoutSubdesignType
from pyaedt.generic.constants import RadiationBoxType
from pyaedt.generic.constants import SolverType
from pyaedt.generic.constants import SweepType
from pyaedt.generic.general_methods import is_ironpython
from pyaedt.generic.general_methods import pyaedt_function_handler
from pyaedt.modeler.GeometryOperators import GeometryOperators

try:
    from System import Array
    from System.Collections.Generic import List
except ImportError:
    if os.name != "posix":
        warnings.warn(
            "The clr is missing. Install Python.NET or use an IronPython version if you want to use the EDB module."
        )


class EDBNetsData(object):
    """Manages EDB functionalities for a primitives.
    It Inherits EDB Object properties.

    Examples
    --------
    >>> from pyaedt import Edb
    >>> edb = Edb(myedb, edbversion="2021.2")
    >>> edb_net = edb.core_nets.nets["GND"]
    >>> edb_net.name # Class Property
    >>> edb_net.GetName() # EDB Object Property
    """

    def __getattr__(self, key):
        try:
            return self[key]
        except:
            try:
                return getattr(self.net_object, key)
            except AttributeError:
                raise AttributeError("Attribute not present")

    def __init__(self, raw_net, core_app):
        self._app = core_app
        self._core_components = core_app.core_components
        self._core_primitive = core_app.core_primitives
        self.net_object = raw_net

    @property
    def name(self):
        """Return the Net Name.

        Returns
        -------
        str
        """
        return self.net_object.GetName()

    @name.setter
    def name(self, val):
        self.net_object.SetName(val)

    @property
    def primitives(self):
        """Return the list of primitives that belongs to the net.

        Returns
        -------
        list of :class:`pyaedt.edb_core.EDB_Data.EDBPrimitives`
        """
        prims = []
        for el in self._core_primitive.primitives:
            if self.name == el.net_name:
                prims.append(el)
        return prims

    @property
    def is_power_ground(self):
        """Either to get/set boolean for power/ground net.

        Returns
        -------
        bool
        """
        return self.net_object.IsPowerGround()

    @is_power_ground.setter
    def is_power_ground(self, val):
        if isinstance(val, bool):
            self.net_object.SetIsPowerGround(val)
        else:
            raise AttributeError("Value has to be a boolean.")

    @property
    def components(self):
        """Return the list of components that touch the net.

        Returns
        -------
        dict[str, :class:`pyaedt.edb_core.EDB_Data.EDBComponent`]
        """
        comps = {}
        for el, val in self._core_components.components.items():
            if self.name in val.nets:
                comps[el] = val
        return comps

    @pyaedt_function_handler()
    def plot(
        self,
        layers=None,
        show_legend=True,
        save_plot=None,
        outline=None,
        size=(2000, 1000),
    ):
        """Plot a Net to Matplotlib 2D Chart.

        Parameters
        ----------
        layers : str, list, optional
            Name of the layers to include in the plot. If `None` all the signal layers will be considered.
        show_legend : bool, optional
            If `True` the legend is shown in the plot. (default)
            If `False` the legend is not shown.
        save_plot : str, optional
            If `None` the plot will be shown.
            If a file path is specified the plot will be saved to such file.
        outline : list, optional
            List of points of the outline to plot.
        size : tuple, optional
            Image size in pixel (width, height).
        """

        self._app.core_nets.plot(
            self.name,
            layers=layers,
            show_legend=show_legend,
            save_plot=save_plot,
            outline=outline,
            size=size,
        )


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
        self._core_stackup = core_app.core_stackup
        self._core_net = core_app.core_nets
        self.primitive_object = raw_primitive

    @pyaedt_function_handler()
    def area(self, include_voids=True):
        """Return the total area.

        Parameters
        ----------
        include_voids : bool, optional
            Either if the voids have to be included in computation.
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
        xa = (x2-x1) / 2
        ya = (y2-y1) / 2
        xo = x1 + xa
        yo = y1 + ya
        a = math.sqrt(xa**2 + ya**2)
        if a < tol:
            return [], []
        r = (a**2)/(2*h) + h/2
        if abs(r-a) < tol:
            b = 0
            th = 2 * math.asin(1)  # chord angle
        else:
            b = math.sqrt(r**2 - a**2)
            th = 2 * math.asin(a/r)  # chord angle

        # center of the circle
        xc = xo + b*ya/a
        yc = yo - b*xa/a

        alpha = math.atan2((y1-yc), (x1-xc))
        xr = []
        yr = []
        for i in range(n):
            i += 1
            dth = (float(i)/(n+1)) * th
            xi = xc + r * math.cos(alpha-dth)
            yi = yc + r * math.sin(alpha-dth)
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
                p1 = [my_net_points[i-1].X.ToDouble(), my_net_points[i-1].Y.ToDouble()]
                if i+1 < len(my_net_points):
                    p2 = [my_net_points[i+1].X.ToDouble(), my_net_points[i+1].Y.ToDouble()]
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
            x, y = GeometryOperators.orient_polygon(xt, yt, clockwise=True)
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
        list of :class:`pyaedt.edb_core.EDB_Data.EDBPrimitives`
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
        if val in self._core_net.nets:
            net = self._core_net.nets[val].net_object
            self.primitive_object.SetNet(net)
        elif not isinstance(val, str):
            try:
                self.primitive_object.SetNet(val)
            except:
                raise AttributeError("Value inserted not found. Input has to be layer name or net object.")
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
            lay = self._core_stackup.stackup_layers.layers[val]._layer
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
        self.primitive_object.Delete()


class EDBLayer(object):
    """Manages EDB functionalities for a layer.

    Examples
    --------
    >>> from pyaedt import Edb
    >>> edb = Edb(myedb, edbversion="2021.2")
    >>> edb_layer = edb.core_stackup.stackup_layers.layers["TOP"]
    """

    def __init__(self, edblayer, app):
        self._layer = edblayer
        self._name = None
        self._layer_type = None
        self._thickness = None
        self._etch_factor = None
        self._material_name = None
        self._filling_material_name = None
        self._lower_elevation = None
        self._upper_elevation = None
        self._top_bottom_association = None
        self._id = None
        self._edb = app._edb
        self._active_layout = app._active_layout
        self._pedblayers = app
        self.init_vals()

    @property
    def _stackup_methods(self):
        return self._pedblayers._stackup_methods

    @property
    def _builder(self):
        return self._pedblayers._builder

    @property
    def _logger(self):
        """Logger."""
        return self._pedblayers.logger

    def _get_edb_value(self, value):
        """Get Edb Value."""
        return self._pedblayers._get_edb_value(value)

    @property
    def name(self):
        """Layer name.

        Returns
        -------
        str
            Name of the layer.
        """
        if not self._name:
            self._name = self._layer.GetName()
        return self._name

    @property
    def id(self):
        """Layer ID.

        Returns
        -------
        int
            ID of the layer.
        """
        if not self._id:
            self._id = self._layer.GetLayerId()
        return self._id

    @property
    def layer_type(self):
        """Layer type.

        Returns
        -------
        int
            Type of the layer.
        """
        if not self._layer_type:
            self._layer_type = self._layer.GetLayerType()
        return self._layer_type

    @layer_type.setter
    def layer_type(self, value):

        self._layer_type = value
        self.update_layers()

    @property
    def material_name(self):
        """Retrieve or update the material name.

        Returns
        -------
        str
            Name of the material.
        """
        try:
            self._material_name = self._layer.GetMaterial()
        except:
            pass
        return self._material_name

    @material_name.setter
    def material_name(self, value):

        self._material_name = value
        self.update_layers()

    @property
    def thickness_value(self):
        """Thickness value.

        Returns
        -------
        float
            Thickness value.
        """
        try:
            self._thickness = self._layer.GetThicknessValue().ToDouble()
        except:
            pass
        return self._thickness

    @thickness_value.setter
    def thickness_value(self, value):
        self._thickness = value
        self.update_layers()

    @property
    def filling_material_name(self):
        """Filling material.

        Returns
        -------
        str
            Name of the filling material if it exists.
        """
        if self._layer_type == 0 or self._layer_type == 2:
            try:
                self._filling_material_name = self._layer.GetFillMaterial()
            except:
                pass
            return self._filling_material_name
        return ""

    @filling_material_name.setter
    def filling_material_name(self, value):

        if self._layer_type == 0 or self._layer_type == 2:
            self._filling_material_name = value
            self.update_layers()

    @property
    def top_bottom_association(self):
        """Top/bottom association layer.

        Returns
        -------
        int
            Top/bottom association layer, where:

            * 0 - Top associated
            * 1 - No association
            * 2 - Bottom associated
            * 4 - Number of top/bottom associations
            * -1 -  Undefined.
        """
        try:
            self._top_bottom_association = int(self._layer.GetTopBottomAssociation())
        except:
            pass
        return self._top_bottom_association

    @property
    def lower_elevation(self):
        """Lower elevation.

        Returns
        -------
        float
            Lower elevation.
        """
        try:
            self._lower_elevation = self._layer.GetLowerElevation()
        except:
            pass
        return self._lower_elevation

    @lower_elevation.setter
    def lower_elevation(self, value):

        self._lower_elevation = value
        self.update_layers()

    @property
    def upper_elevation(self):
        """Upper elevation.

        Returns
        -------
        float
            Upper elevation.
        """
        try:
            self._upper_elevation = self._layer.GetUpperElevation()
        except:
            pass
        return self._upper_elevation

    @property
    def etch_factor(self):
        """Etch factor.

        Returns
        -------
        float
            Etch factor if it exists, 0 otherwise.
        """
        if self._layer_type == 0 or self._layer_type == 2:
            try:
                self._etch_factor = self._layer.GetEtchFactor().ToString()
            except:
                pass
            return self._etch_factor
        return 0

    @etch_factor.setter
    def etch_factor(self, value):

        if self._layer_type == 0 or self._layer_type == 2:
            self._etch_factor = value
            self.update_layers()

    @pyaedt_function_handler()
    def plot(
        self,
        nets=None,
        show_legend=True,
        save_plot=None,
        outline=None,
        size=(2000, 1000),
    ):
        """Plot a Layer to Matplotlib 2D Chart.

        Parameters
        ----------
        nets : str, list, optional
            Name of the nets to include in the plot. If `None` all the nets will be considered.
        show_legend : bool, optional
            If `True` the legend is shown in the plot. (default)
            If `False` the legend is not shown.
        save_plot : str, optional
            If `None` the plot will be shown.
            If a file path is specified the plot will be saved to such file.
        outline : list, optional
            List of points of the outline to plot.
        size : tuple, optional
            Image size in pixel (width, height).
        """

        self._pedblayers._pedbstackup._pedb.core_nets.plot(
            nets=nets,
            layers=self.name,
            color_by_net=True,
            show_legend=show_legend,
            save_plot=save_plot,
            outline=outline,
            size=size,
        )

    @pyaedt_function_handler()
    def init_vals(self):
        """Initialize values."""
        try:
            self._name = self._layer.GetName()
            self._layer_type = self._layer.GetLayerType()
            self._thickness = self._layer.GetThicknessValue().ToString()
            if self._layer_type == 0 or self._layer_type == 2:
                self._etch_factor = self._layer.GetEtchFactor().ToString()
                self._filling_material_name = self._layer.GetFillMaterial()
            self._material_name = self._layer.GetMaterial()
            self._lower_elevation = self._layer.GetLowerElevation()
            self._upper_elevation = self._layer.GetUpperElevation()
            self._top_bottom_association = self._layer.GetTopBottomAssociation()
        except:
            pass

    @pyaedt_function_handler()
    def update_layer_vals(
        self,
        layerName,
        newLayer,
        etchMap,
        materialMap,
        fillMaterialMap,
        thicknessMap,
        layerTypeMap,
    ):
        """Update layer properties.

        Parameters
        ----------
        layerName :

        newLayer :

        materialMap :

        fillMaterialMap :

        thicknessMap :

        layerTypeMap :

        Returns
        -------
        type
            Layer object.

        """
        newLayer.SetName(layerName)

        try:
            newLayer.SetLayerType(layerTypeMap)
        except:
            self._logger.error("Layer %s has unknown type %s.", layerName, layerTypeMap)
            return False
        if thicknessMap:
            newLayer.SetThickness(self._get_edb_value(thicknessMap))
        if materialMap:
            newLayer.SetMaterial(materialMap)
        if fillMaterialMap:
            newLayer.SetFillMaterial(fillMaterialMap)
        if etchMap and layerTypeMap == 0 or layerTypeMap == 2:
            etchVal = float(etchMap)
        else:
            etchVal = 0.0
        if etchVal != 0.0:
            newLayer.SetEtchFactorEnabled(True)
            newLayer.SetEtchFactor(self._get_edb_value(etchVal))
        return newLayer

    @pyaedt_function_handler()
    def set_elevation(self, layer, elev):
        """Update the layer elevation.

        Parameters
        ----------
        layer :
            Layer object.
        elev : float
            Layer elevation.

        Returns
        -------
        type
            Layer

        """

        layer.SetLowerElevation(self._get_edb_value(elev))
        return layer

    @pyaedt_function_handler()
    def update_layers(self):
        """Update all layers.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.
        """
        thisLC = self._edb.Cell.LayerCollection(self._active_layout.GetLayerCollection())
        layers = list(list(thisLC.Layers(self._edb.Cell.LayerTypeSet.AllLayerSet)))
        layers.reverse()
        newLayers = List[self._edb.Cell.Layer]()
        el = 0.0
        for lyr in layers:
            if not lyr.IsStackupLayer():
                newLayers.Add(lyr.Clone())
                continue
            layerName = lyr.GetName()

            if layerName == self.name:
                newLayer = lyr.Clone()
                newLayer = self.update_layer_vals(
                    self._name,
                    newLayer,
                    self._etch_factor,
                    self._material_name,
                    self._filling_material_name,
                    self._thickness,
                    self._layer_type,
                )
                newLayer = self.set_elevation(newLayer, el)
                el += newLayer.GetThickness()
            else:
                newLayer = lyr.Clone()
                newLayer = self.set_elevation(newLayer, el)
                el += newLayer.GetThickness()
            newLayers.Add(newLayer)

        lcNew = self._edb.Cell.LayerCollection()
        newLayers.Reverse()
        if not lcNew.AddLayers(newLayers) or not self._active_layout.SetLayerCollection(lcNew):
            self._logger.error("Failed to set new layers when updating the stackup information.")
            return False
        self._pedblayers._update_edb_objects()
        time.sleep(1)
        return True


class EDBLayers(object):
    """Manages EDB functionalities for all primitive layers.

    Parameters
    ----------
    edb_stackup : :class:`pyaedt.edb_core.stackup.EdbStackup`
        Inherited AEDT object.

    Examples
    --------
    >>> from pyaedt import Edb
    >>> edb = Edb(myedb, edbversion="2021.2")
    >>> edb_layers = edb.core_stackup.stackup_layers
    """

    def __init__(self, edb_stackup):
        self._stackup_mode = None
        self._pedbstackup = edb_stackup
        self._edb_object = {}
        self._update_edb_objects()

    def __getitem__(self, layername):
        """Retrieve a layer.

        Parameters
        ----------
        layername : str
            Name of the layer.

        Returns
        -------
        type
            EDB Layer
        """

        return self.layers[layername]

    @property
    def _logger(self):
        """Logger."""
        return self._pedbstackup.logger

    @property
    def _stackup_methods(self):
        return self._pedbstackup._stackup_methods

    @property
    def _edb(self):
        return self._pedbstackup._edb

    def _get_edb_value(self, value):
        return self._pedbstackup._get_edb_value(value)

    @property
    def _builder(self):
        return self._pedbstackup._builder

    @property
    def _active_layout(self):
        return self._pedbstackup._active_layout

    @property
    def layers(self):
        """Dictionary of layers.

        Returns
        -------
        dict[str, :class:`pyaedt.edb_core.EDB_Data.EDBLayer`]
            Dictionary of layers.
        """
        if not self._edb_object:
            self._update_edb_objects()
        return self._edb_object

    @property
    def edb_layers(self):
        """EDB layers.

        Returns
        -------
        list
            List of EDB layers.
        """
        allLayers = list(list(self.layer_collection.Layers(self._edb.Cell.LayerTypeSet.AllLayerSet)))
        allStackuplayers = filter(
            lambda lyr: (lyr.GetLayerType() == self._edb.Cell.LayerType.DielectricLayer)
            or (
                lyr.GetLayerType() == self._edb.Cell.LayerType.SignalLayer
                or lyr.GetLayerType() == self._edb.Cell.LayerType.ConductingLayer
            ),
            allLayers,
        )
        return sorted(
            allStackuplayers,
            key=lambda lyr=self._edb.Cell.StackupLayer: lyr.GetLowerElevation(),
        )

    @property
    def signal_layers(self):
        """Signal layers.

        Returns
        -------
        dict[str, :class:`pyaedt.edb_core.EDB_Data.EDBLayer`]
            Dictionary of signal layers.
        """
        self._signal_layers = OrderedDict({})
        for layer, edblayer in self.layers.items():
            if (
                edblayer._layer_type == self._edb.Cell.LayerType.SignalLayer
                or edblayer._layer_type == self._edb.Cell.LayerType.ConductingLayer
            ):
                self._signal_layers[layer] = edblayer
        return self._signal_layers

    @property
    def layer_collection(self):
        """Layer collection.

        Returns
        -------
        type
            Collection of layers.
        """
        return self._active_layout.GetLayerCollection()

    @property
    def layer_collection_mode(self):
        """Layer collection mode."""
        return self._edb.Cell.LayerCollectionMode

    @property
    def layer_types(self):
        """Layer types.

        Returns
        -------
        type
            Types of layers.
        """
        return self._edb.Cell.LayerType

    @property
    def stackup_mode(self):
        """Stackup mode.

        Returns
        -------
        int
            Type of the stackup mode, where:

            * 0 - Laminate
            * 1 - Overlapping
            * 2 - Multizone
        """
        self._stackup_mode = self.layer_collection.GetMode()
        return self._stackup_mode

    @property
    def _logger(self):
        """Logger."""
        return self._pedbstackup.logger

    @pyaedt_function_handler()
    def _int_to_layer_types(self, val):
        if int(val) == 0:
            return self.layer_types.SignalLayer
        elif int(val) == 1:
            return self.layer_types.DielectricLayer
        elif int(val) == 2:
            return self.layer_types.ConductingLayer
        elif int(val) == 3:
            return self.layer_types.AirlinesLayer
        elif int(val) == 4:
            return self.layer_types.ErrorsLayer
        elif int(val) == 5:
            return self.layer_types.SymbolLayer
        elif int(val) == 6:
            return self.layer_types.MeasureLayer
        elif int(val) == 8:
            return self.layer_types.AssemblyLayer
        elif int(val) == 9:
            return self.layer_types.SilkscreenLayer
        elif int(val) == 10:
            return self.layer_types.SolderMaskLayer
        elif int(val) == 11:
            return self.layer_types.SolderPasteLayer
        elif int(val) == 12:
            return self.layer_types.GlueLayer
        elif int(val) == 13:
            return self.layer_types.WirebondLayer
        elif int(val) == 14:
            return self.layer_types.UserLayer
        elif int(val) == 16:
            return self.layer_types.SIwaveHFSSSolverRegions
        elif int(val) == 18:
            return self.layer_types.OutlineLayer

    @stackup_mode.setter
    def stackup_mode(self, value):

        if value == 0 or value == self.layer_collection_mode.Laminate:
            self.layer_collection.SetMode(self.layer_collection_mode.Laminate)
        elif value == 1 or value == self.layer_collection_mode.Overlapping:
            self.layer_collection.SetMode(self.layer_collection_mode.Overlapping)
        elif value == 2 or value == self.layer_collection_mode.MultiZone:
            self.layer_collection.SetMode(self.layer_collection_mode.MultiZone)

    @pyaedt_function_handler()
    def _update_edb_objects(self):
        self._edb_object = OrderedDict({})
        layers = self.edb_layers
        for i in range(len(layers)):
            self._edb_object[layers[i].GetName()] = EDBLayer(layers[i], self)
        return True

    @pyaedt_function_handler()
    def add_layer(
        self,
        layerName,
        start_layer=None,
        material="copper",
        fillMaterial="",
        thickness="35um",
        layerType=0,
        etchMap=None,
    ):
        """Add a layer after a specific layer.

        Parameters
        ----------
        layerName : str
            Name of the layer to add.
        start_layer : str, optional
            Name of the layer after which to add the new layer.
            The default is ``None``.
        material : str, optional
            Name of the material. The default is ``"copper"``.
        fillMaterial : str, optional
            Name of the fill material. The default is ``""``.)
        thickness : str, optional
            Thickness value, including units. The default is ``"35um"``.
        layerType :
            Type of the layer. The default is ``0``, which is a signal layer.
        etchMap : optional
            Etch value if any. The default is ``None``.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.
        """
        thisLC = self._pedbstackup._active_layout.GetLayerCollection()
        layers = list(list(thisLC.Layers(self._edb.Cell.LayerTypeSet.AllLayerSet)))
        layers.reverse()
        # newLayers = List[self._edb.Cell.Layer]()
        el = 0.0
        lcNew = self._edb.Cell.LayerCollection()

        if not layers or not start_layer:
            if int(layerType) > 2:
                newLayer = self._edb.Cell.Layer(layerName, self._int_to_layer_types(layerType))
                # newLayers.Add(newLayer)
                lcNew.AddLayerTop(newLayer)
            else:
                for lyr in layers:
                    if not lyr.IsStackupLayer():
                        # newLayers.Add(lyr.Clone())
                        lcNew.AddLayerTop(lyr.Clone())
                        continue
                newLayer = self._edb.Cell.StackupLayer(
                    layerName,
                    self._int_to_layer_types(layerType),
                    self._get_edb_value(0),
                    self._get_edb_value(0),
                    "",
                )
                self._edb_object[layerName] = EDBLayer(newLayer, self._pedbstackup)
                newLayer = self._edb_object[layerName].update_layer_vals(
                    layerName,
                    newLayer,
                    etchMap,
                    material,
                    fillMaterial,
                    thickness,
                    self._int_to_layer_types(layerType),
                )
                newLayer.SetLowerElevation(self._get_edb_value(el))

                # newLayers.Add(newLayer)
                lcNew.AddLayerTop(newLayer)
                el += newLayer.GetThickness()
            for lyr in layers:
                if not lyr.IsStackupLayer():
                    continue
                newLayer = lyr.Clone()
                newLayer.SetLowerElevation(self._get_edb_value(el))
                el += newLayer.GetThickness()
                # newLayers.Add(newLayer)
                lcNew.AddLayerTop(newLayer)
        else:
            for lyr in layers:
                if not lyr.IsStackupLayer():
                    # newLayers.Add(lyr.Clone())
                    lcNew.AddLayerTop(lyr.Clone())
                    continue
                if lyr.GetName() == start_layer:
                    original_layer = lyr.Clone()
                    original_layer.SetLowerElevation(self._get_edb_value(el))
                    lcNew.AddLayerTop(original_layer)
                    el += original_layer.GetThickness()
                    newLayer = self._edb.Cell.StackupLayer(
                        layerName,
                        self._int_to_layer_types(layerType),
                        self._get_edb_value(0),
                        self._get_edb_value(0),
                        "",
                    )
                    self._edb_object[layerName] = EDBLayer(newLayer, self._pedbstackup)
                    newLayer = self._edb_object[layerName].update_layer_vals(
                        layerName,
                        newLayer,
                        etchMap,
                        material,
                        fillMaterial,
                        thickness,
                        self._int_to_layer_types(layerType),
                    )
                    newLayer.SetLowerElevation(self._get_edb_value(el))
                    lcNew.AddLayerTop(newLayer)
                    el += newLayer.GetThickness()
                    # newLayers.Add(original_layer)

                else:
                    newLayer = lyr.Clone()
                    newLayer.SetLowerElevation(self._get_edb_value(el))
                    el += newLayer.GetThickness()
                    lcNew.AddLayerTop(newLayer)
        # lcNew = self._edb.Cell.LayerCollection()
        # newLayers.Reverse()
        if not self._active_layout.SetLayerCollection(lcNew):
            self._logger.error("Failed to set new layers when updating the stackup information.")
            return False
        self._update_edb_objects()
        return True

    def add_outline_layer(self, outline_name="Outline"):
        """
        Add an outline layer named ``"Outline"`` if it is not present.

        Returns
        -------
        bool
            "True" if succeeded
        """
        outlineLayer = self._edb.Cell.Layer.FindByName(self._active_layout.GetLayerCollection(), outline_name)
        if outlineLayer.IsNull():
            return self.add_layer(
                outline_name,
                layerType=self.layer_types.OutlineLayer,
                material="",
                thickness="",
            )
        else:
            return False

    @pyaedt_function_handler()
    def remove_layer(self, layername):
        """Remove a layer.

        Parameters
        ----------
        layername : str
            Name of the layer.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.
        """
        thisLC = self._edb.Cell.LayerCollection(self._pedbstackup._active_layout.GetLayerCollection())
        layers = list(list(thisLC.Layers(self._edb.Cell.LayerTypeSet.AllLayerSet)))
        layers.reverse()
        newLayers = List[self._edb.Cell.Layer]()
        el = 0.0
        for lyr in layers:
            if not lyr.IsStackupLayer():
                newLayers.Add(lyr.Clone())
                continue
            if not (layername == lyr.GetName()):
                newLayer = lyr.Clone()
                newLayer = self._edb_object[lyr.GetName()].set_elevation(newLayer, el)
                el += newLayer.GetThickness()
                newLayers.Add(newLayer)
        lcNew = self._edb.Cell.LayerCollection()
        newLayers.Reverse()
        if not lcNew.AddLayers(newLayers) or not self._pedbstackup._active_layout.SetLayerCollection(lcNew):
            self._logger.error("Failed to set new layers when updating the stackup information.")
            return False
        self._update_edb_objects()
        return True


class EDBPadProperties(object):
    """Manages EDB functionalities for pad properties.

    Parameters
    ----------
    edb_padstack :

    layer_name : str
        Name of the layer.
    pad_type :
        Type of the pad.
    pedbpadstack : str
        Inherited AEDT object.

    Examples
    --------
    >>> from pyaedt import Edb
    >>> edb = Edb(myedb, edbversion="2021.2")
    >>> edb_pad_properties = edb.core_padstack.padstacks["MyPad"].pad_by_layer["TOP"]
    """

    def __init__(self, edb_padstack, layer_name, pad_type, p_edb_padstack):
        self._edb_padstack = edb_padstack
        self._pedbpadstack = p_edb_padstack
        self.layer_name = layer_name
        self.pad_type = pad_type
        pass

    @property
    def _padstack_methods(self):
        return self._pedbpadstack._padstack_methods

    @property
    def _stackup_layers(self):
        return self._pedbpadstack._stackup_layers

    @property
    def _builder(self):
        return self._pedbpadstack._builder

    @property
    def _edb(self):
        return self._pedbpadstack._edb

    def _get_edb_value(self, value):
        return self._pedbpadstack._get_edb_value(value)

    @property
    def geometry_type(self):
        """Geometry type.

        Returns
        -------
        int
            Type of the geometry.
        """
        padparams = self._padstack_methods.GetPadParametersValue(self._edb_padstack, self.layer_name, self.pad_type)
        return int(padparams.Item1)

    @geometry_type.setter
    def geometry_type(self, geom_type):
        """0, NoGeometry. 1, Circle. 2 Square. 3, Rectangle. 4, Oval. 5, Bullet. 6, N-sided polygon. 7, Polygonal
        shape.8, Round gap with 45 degree thermal ties. 9, Round gap with 90 degree thermal ties.10, Square gap
        with 45 degree thermal ties. 11, Square gap with 90 degree thermal ties.
        """
        val = self._get_edb_value(0)
        params = []
        if geom_type == 0:
            pass
        elif geom_type == 1:
            params = [val]
        elif geom_type == 2:
            params = [val]
        elif geom_type == 3:
            params = [val, val]
        elif geom_type == 4:
            params = [val, val, val]
        elif geom_type == 5:
            params = [val, val, val]
        self._update_pad_parameters_parameters(geom_type=geom_type, params=params)

    @property
    def parameters_values(self):
        """Parameters.

        Returns
        -------
        list
            List of parameters.
        """
        pad_values = self._padstack_methods.GetPadParametersValue(self._edb_padstack, self.layer_name, self.pad_type)
        return [i.ToDouble() for i in pad_values.Item2]

    @property
    def polygon_data(self):
        """Parameters.

        Returns
        -------
        list
            List of parameters.
        """
        try:
            pad_values = self._padstack_methods.GetPolygonalPadParameters(
                self._edb_padstack, self.layer_name, self.pad_type
            )
            return pad_values.Item1
        except:
            return

    @property
    def parameters(self):
        """Parameters.

        Returns
        -------
        list
            List of parameters.
        """
        pad_values = self._padstack_methods.GetPadParametersValue(self._edb_padstack, self.layer_name, self.pad_type)
        return [i.ToString() for i in pad_values.Item2]

    @parameters.setter
    def parameters(self, propertylist):

        if not isinstance(propertylist, list):
            propertylist = [self._get_edb_value(propertylist)]
        else:
            propertylist = [self._get_edb_value(i) for i in propertylist]
        self._update_pad_parameters_parameters(params=propertylist)

    @property
    def offset_x(self):
        """Offset for the X axis.

        Returns
        -------
        str
            Offset for the X axis.
        """
        pad_values = self._padstack_methods.GetPadParametersValue(self._edb_padstack, self.layer_name, self.pad_type)
        return pad_values.Item3.ToString()

    @offset_x.setter
    def offset_x(self, offset_value):

        self._update_pad_parameters_parameters(offsetx=offset_value)

    @property
    def offset_y(self):
        """Offset for the Y axis.

        Returns
        -------
        str
            Offset for the Y axis.
        """
        pad_values = self._padstack_methods.GetPadParametersValue(self._edb_padstack, self.layer_name, self.pad_type)
        return pad_values.Item4.ToString()

    @offset_y.setter
    def offset_y(self, offset_value):

        self._update_pad_parameters_parameters(offsety=offset_value)

    @property
    def rotation(self):
        """Rotation.

        Returns
        -------
        str
            Value for the rotation.
        """
        pad_values = self._padstack_methods.GetPadParametersValue(self._edb_padstack, self.layer_name, self.pad_type)
        return pad_values.Item5.ToString()

    @rotation.setter
    def rotation(self, rotation_value):

        self._update_pad_parameters_parameters(rotation=rotation_value)

    @pyaedt_function_handler()
    def int_to_geometry_type(self, val=0):
        """Convert an integer to an EDB.PadGeometryType.

        Parameters
        ----------
        val : int

        Returns
        -------
        object
            EDB.PadGeometryType enumerator value.
        """
        if val == 0:
            return self._edb.Definition.PadGeometryType.NoGeometry
        elif val == 1:
            return self._edb.Definition.PadGeometryType.Circle
        elif val == 2:
            return self._edb.Definition.PadGeometryType.Square
        elif val == 3:
            return self._edb.Definition.PadGeometryType.Rectangle
        elif val == 4:
            return self._edb.Definition.PadGeometryType.Oval
        elif val == 5:
            return self._edb.Definition.PadGeometryType.Bullet
        elif val == 6:
            return self._edb.Definition.PadGeometryType.NSidedPolygon
        elif val == 7:
            return self._edb.Definition.PadGeometryType.Polygon
        elif val == 8:
            return self._edb.Definition.PadGeometryType.Round45
        elif val == 9:
            return self._edb.Definition.PadGeometryType.Round90
        elif val == 10:
            return self._edb.Definition.PadGeometryType.Square45
        elif val == 11:
            return self._edb.Definition.PadGeometryType.Square90
        elif val == 12:
            return self._edb.Definition.PadGeometryType.InvalidGeometry

    @pyaedt_function_handler()
    def _update_pad_parameters_parameters(
        self,
        layer_name=None,
        pad_type=None,
        geom_type=None,
        params=None,
        offsetx=None,
        offsety=None,
        rotation=None,
    ):
        """Update padstack parameters.

        Parameters
        ----------
        layer_name : str, optional
            Name of the layer. The default is ``None``.
        pad_type : int, optional
            Type of the pad. The default is ``None``.
        geom_type : int, optional
            Type of the geometry. The default is ``None``.
        params : list, optional
            The default is ``None``.
        offsetx : float, optional
            Offset value for the X axis. The default is ``None``.
        offsety :  float, optional
            Offset value for the Y axis. The default is ``None``.
        rotation : float, optional
            Rotation value. The default is ``None``.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.
        """
        originalPadstackDefinitionData = self._edb_padstack.GetData()
        newPadstackDefinitionData = self._edb.Definition.PadstackDefData(originalPadstackDefinitionData)
        if not pad_type:
            pad_type = self.pad_type
        if not geom_type:
            geom_type = self.geometry_type
        if not params:
            params = [self._get_edb_value(i) for i in self.parameters]
        if not offsetx:
            offsetx = self.offset_x
        if not offsety:
            offsety = self.offset_y
        if not rotation:
            rotation = self.rotation
        if not layer_name:
            layer_name = self.layer_name
        if is_ironpython:
            if isinstance(geom_type, int):
                geom_type = self.int_to_geometry_type(geom_type)
        newPadstackDefinitionData.SetPadParameters(
            layer_name,
            pad_type,
            geom_type,
            convert_py_list_to_net_list(params),
            self._get_edb_value(offsetx),
            self._get_edb_value(offsety),
            self._get_edb_value(rotation),
        )
        self._edb_padstack.SetData(newPadstackDefinitionData)


class EDBPadstack(object):
    """Manages EDB functionalities for a padstack.

    Parameters
    ----------
    edb_padstack :

    ppadstack : str
        Inherited AEDT object.

    Examples
    --------
    >>> from pyaedt import Edb
    >>> edb = Edb(myedb, edbversion="2021.2")
    >>> edb_padstack = edb.core_padstack.padstacks["MyPad"]
    """

    def __init__(self, edb_padstack, ppadstack):
        self.edb_padstack = edb_padstack
        self._ppadstack = ppadstack
        self.pad_by_layer = {}
        self.antipad_by_layer = {}
        self.thermalpad_by_layer = {}
        for layer in self.via_layers:
            self.pad_by_layer[layer] = EDBPadProperties(edb_padstack, layer, 0, self)
            self.antipad_by_layer[layer] = EDBPadProperties(edb_padstack, layer, 1, self)
            self.thermalpad_by_layer[layer] = EDBPadProperties(edb_padstack, layer, 2, self)
        pass

    @property
    def _padstack_methods(self):
        return self._ppadstack._padstack_methods

    @property
    def _stackup_layers(self):
        return self._ppadstack._stackup_layers

    @property
    def _builder(self):
        return self._ppadstack._builder

    @property
    def _edb(self):
        return self._ppadstack._edb

    def _get_edb_value(self, value):
        return self._ppadstack._get_edb_value(value)

    @property
    def via_layers(self):
        """Layers.

        Returns
        -------
        list
            List of layers.
        """
        return self.edb_padstack.GetData().GetLayerNames()

    @property
    def via_start_layer(self):
        """Starting layer.

        Returns
        -------
        str
            Name of the starting layer.
        """
        return list(self.via_layers)[0]

    @property
    def via_stop_layer(self):
        """Stopping layer.

        Returns
        -------
        str
            Name of the stopping layer.
        """
        return list(self.via_layers)[-1]

    @property
    def _hole_params(self):
        viaData = self.edb_padstack.GetData()
        if is_ironpython:
            out = viaData.GetHoleParametersValue()
        else:
            value0 = self._get_edb_value("0.0")
            ptype = self._edb.Definition.PadGeometryType.Circle
            HoleParam = Array[type(value0)]([])
            out = viaData.GetHoleParametersValue(ptype, HoleParam, value0, value0, value0)
        return out

    @property
    def hole_parameters(self):
        """Hole parameters.

        Returns
        -------
        list
            List of the hole parameters.
        """
        self._hole_parameters = self._hole_params[2]
        return self._hole_parameters

    @pyaedt_function_handler()
    def _update_hole_parameters(self, hole_type=None, params=None, offsetx=None, offsety=None, rotation=None):
        """Update hole parameters.

        Parameters
        ----------
        hole_type : optional
            Type of the hole. The default is ``None``.
        params : optional
            The default is ``None``.
        offsetx : float, optional
            Offset value for the X axis. The default is ``None``.
        offsety :  float, optional
            Offset value for the Y axis. The default is ``None``.
        rotation : float, optional
            Rotation value in degrees. The default is ``None``.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.
        """
        originalPadstackDefinitionData = self.edb_padstack.GetData()
        newPadstackDefinitionData = self._edb.Definition.PadstackDefData(originalPadstackDefinitionData)
        if not hole_type:
            hole_type = self.hole_type
        if not params:
            params = self.hole_parameters
        if not offsetx:
            offsetx = self.hole_offset_x
        if not offsety:
            offsety = self.hole_offset_y
        if not rotation:
            rotation = self.hole_rotation
        if is_ironpython:
            newPadstackDefinitionData.SetHoleParameters(
                hole_type,
                params,
                self._get_edb_value(offsetx),
                self._get_edb_value(offsety),
                self._get_edb_value(rotation),
            )
        else:
            newPadstackDefinitionData.SetHoleParameters(
                hole_type,
                convert_py_list_to_net_list(params),
                self._get_edb_value(offsetx),
                self._get_edb_value(offsety),
                self._get_edb_value(rotation),
            )
        self.edb_padstack.SetData(newPadstackDefinitionData)

    @property
    def hole_properties(self):
        """Hole properties.

        Returns
        -------
        list
            List of float values for hole properties.
        """
        self._hole_properties = [i.ToDouble() for i in self._hole_params[2]]
        return self._hole_properties

    @hole_properties.setter
    def hole_properties(self, propertylist):

        if not isinstance(propertylist, list):
            propertylist = [self._get_edb_value(propertylist)]
        else:
            propertylist = [self._get_edb_value(i) for i in propertylist]
        self._update_hole_parameters(params=propertylist)

    @property
    def hole_type(self):
        """Hole type.

        Returns
        -------
        int
            Type of the hole.
        """
        self._hole_type = self._hole_params[1]
        return self._hole_type

    @property
    def hole_offset_x(self):
        """Hole offset for the X axis.

        Returns
        -------
        str
            Hole offset value for the X axis.
        """
        self._hole_offset_x = self._hole_params[3].ToString()
        return self._hole_offset_x

    @hole_offset_x.setter
    def hole_offset_x(self, offset):

        self._hole_offset_x = offset
        self._update_hole_parameters(offsetx=offset)

    @property
    def hole_offset_y(self):
        """Hole offset for the Y axis.

        Returns
        -------
        str
            Hole offset value for the Y axis.
        """
        self._hole_offset_y = self._hole_params[4].ToString()
        return self._hole_offset_y

    @hole_offset_y.setter
    def hole_offset_y(self, offset):

        self._hole_offset_y = offset
        self._update_hole_parameters(offsety=offset)

    @property
    def hole_rotation(self):
        """Hole rotation.

        Returns
        -------
        str
            Value for the hole rotation.
        """
        self._hole_rotation = self._hole_params[5].ToString()
        return self._hole_rotation

    @hole_rotation.setter
    def hole_rotation(self, rotation):

        self._hole_rotation = rotation
        self._update_hole_parameters(rotation=rotation)

    @property
    def hole_plating_ratio(self):
        """Hole plating ratio.

        Returns
        -------
        float
            Percentage for the hole plating.
        """
        return self.edb_padstack.GetData().GetHolePlatingPercentage()

    @hole_plating_ratio.setter
    def hole_plating_ratio(self, ratio):

        originalPadstackDefinitionData = self.edb_padstack.GetData()
        newPadstackDefinitionData = self._edb.Definition.PadstackDefData(originalPadstackDefinitionData)
        newPadstackDefinitionData.SetHolePlatingPercentage(self._get_edb_value(ratio))
        self.edb_padstack.SetData(newPadstackDefinitionData)

    @property
    def hole_plating_thickness(self):
        """Hole plating thickness.

        Returns
        -------
        float
            Thickness of the hole plating if present.
        """
        if len(self.hole_properties) > 0:
            return (float(self.hole_properties[0]) * self.hole_plating_ratio / 100) / 2
        else:
            return 0

    @property
    def hole_finished_size(self):
        """Finished hole size.

        Returns
        -------
        float
            Finished size of the hole (Total Size + PlatingThickess*2).
        """
        if len(self.hole_properties) > 0:
            return float(self.hole_properties[0]) - (self.hole_plating_thickness * 2)
        else:
            return 0

    @property
    def material(self):
        """Hole material.

        Returns
        -------
        str
            Material of the hole.
        """
        return self.edb_padstack.GetData().GetMaterial()

    @material.setter
    def material(self, materialname):

        originalPadstackDefinitionData = self.edb_padstack.GetData()
        newPadstackDefinitionData = self._edb.Definition.PadstackDefData(originalPadstackDefinitionData)
        newPadstackDefinitionData.SetMaterial(materialname)
        self.edb_padstack.SetData(newPadstackDefinitionData)


class EDBPadstackInstance(object):
    """Manages EDB functionalities for a padstack.

    Parameters
    ----------
    edb_padstackinstance :

    _pedb :
        Inherited AEDT object.

    Examples
    --------
    >>> from pyaedt import Edb
    >>> edb = Edb(myedb, edbversion="2021.2")
    >>> edb_padstack_instance = edb.core_padstack.padstack_instances[0]
    """

    def __init__(self, edb_padstackinstance, _pedb):
        self._edb_padstackinstance = edb_padstackinstance
        self._pedb = _pedb

    @property
    def pin(self):
        """Return Edb padstack object."""
        return self._edb_padstackinstance

    @property
    def padstack_definition(self):
        """Padstack definition.

        Returns
        -------
        str
            Name of the padstack definition.
        """
        return self._edb_padstackinstance.GetPadstackDef().GetName()

    @property
    def backdrill_top(self):
        """Backdrill layer from top.

        Returns
        -------
        tuple
            Tuple of the layer name and drill diameter.
        """
        layer = self._pedb.edb.Cell.Layer("", 1)
        val = self._pedb.edb_value(0)
        (
            _,
            depth,
            diameter,
        ) = self._edb_padstackinstance.GetBackDrillParametersLayerValue(layer, val, False)
        return depth.GetName(), diameter.ToString()

    @property
    def backdrill_bottom(self):
        """Backdrill layer from bottom.

        Returns
        -------
        tuple
            Tuple of the layer name and drill diameter.
        """
        layer = self._pedb.edb.Cell.Layer("", 1)
        val = self._pedb.edb_value(0)
        (
            _,
            depth,
            diameter,
        ) = self._edb_padstackinstance.GetBackDrillParametersLayerValue(layer, val, True)
        return depth.GetName(), diameter.ToString()

    @property
    def start_layer(self):
        """Starting layer.

        Returns
        -------
        str
            Name of the starting layer.
        """
        layer = self._pedb.edb.Cell.Layer("", 1)
        _, start_layer, stop_layer = self._edb_padstackinstance.GetLayerRange(layer, layer)
        return start_layer.GetName()

    @start_layer.setter
    def start_layer(self, layer_name):
        stop_layer = self._pedb.core_stackup.signal_layers[self.stop_layer]._layer
        layer = self._pedb.core_stackup.signal_layers[layer_name]._layer
        self._edb_padstackinstance.SetLayerRange(layer, stop_layer)

    @property
    def stop_layer(self):
        """Stopping layer.

        Returns
        -------
        str
            Name of the stopping layer.
        """
        layer = self._pedb.edb.Cell.Layer("", 1)
        _, start_layer, stop_layer = self._edb_padstackinstance.GetLayerRange(layer, layer)
        return stop_layer.GetName()

    @stop_layer.setter
    def stop_layer(self, layer_name):
        start_layer = self._pedb.core_stackup.signal_layers[self.start_layer]._layer
        layer = self._pedb.core_stackup.signal_layers[layer_name]._layer
        self._edb_padstackinstance.SetLayerRange(start_layer, layer)

    @property
    def net_name(self):
        """Net name.

        Returns
        -------
        str
            Name of the net.
        """
        return self._edb_padstackinstance.GetNet().GetName()

    @property
    def is_pin(self):
        """Determines whether this padstack instance is a layout pin.

        Returns
        -------
        bool
            True if this padstack type is a layout pin, False otherwise.
        """
        return self._edb_padstackinstance.IsLayoutPin()

    @is_pin.setter
    def is_pin(self, pin):
        """Set padstack type

        Parameters
        ----------
        pin : bool
            True if set this padstack instance as pin, False otherwise
        """
        self._edb_padstackinstance.SetIsLayoutPin(pin)

    @property
    def position(self):
        """Padstack instance position.

        Returns
        -------
        list
            List of ``[x, y]``` coordinates for the padstack instance position.
        """
        point_data = self._pedb.edb.Geometry.PointData(self._pedb.edb_value(0.0), self._pedb.edb_value(0.0))
        if is_ironpython:
            out = self._edb_padstackinstance.GetPositionAndRotationValue()
        else:
            out = self._edb_padstackinstance.GetPositionAndRotationValue(
                point_data,
                self._pedb.edb_value(0.0),
            )
        if out[0]:
            return [out[1].X.ToDouble(), out[1].Y.ToDouble()]

    @property
    def rotation(self):
        """Padstack instance rotation.

        Returns
        -------
        float
            Rotatation value for the padstack instance.
        """
        point_data = self._pedb.edb.Geometry.PointData(self._pedb.edb_value(0.0), self._pedb.edb_value(0.0))
        if is_ironpython:
            out = self._edb_padstackinstance.GetPositionAndRotationValue()
        else:
            out = self._edb_padstackinstance.GetPositionAndRotationValue(
                point_data,
                self._pedb.edb_value(0.0),
            )
        if out[0]:
            return out[2].ToDouble()

    @property
    def id(self):
        """Id of this padstack instance.

        Returns
        -------
        str
            Padstack instance id.
        """
        return self._edb_padstackinstance.GetId()

    @property
    def name(self):
        """Padstack Instance Name. If it is a pin, the syntax will be like in AEDT ComponentName-PinName."""
        if self.is_pin:
            comp_name = self._edb_padstackinstance.GetComponent().GetName()
            pin_name = self._edb_padstackinstance.GetName()
            return "-".join([comp_name, pin_name])
        else:
            return self._edb_padstackinstance.GetName()

    @pyaedt_function_handler()
    def delete_padstack_instance(self):
        """Delete this padstack instance."""
        self._edb_padstackinstance.Delete()

    @pyaedt_function_handler()
    def in_voids(self, net_name=None, layer_name=None):
        """Check if this padstack instance is in any void.

        Parameters
        ----------
        net_name : str
            Net name of the voids to be checked.
        layer_name : str
            Layer name of the voids to be checked.
        Returns
        -------
        list
            List of the voids includes this padstack instance.
        """
        x_pos = self._pedb.edb_value(self.position[0])
        y_pos = self._pedb.edb_value(self.position[1])
        point_data = self._pedb.core_primitives._edb.Geometry.PointData(x_pos, y_pos)

        voids = []
        for prim in self._pedb.core_primitives.get_primitives(net_name, layer_name, is_void=True):
            if prim.primitive_object.GetPolygonData().PointInPolygon(point_data):
                voids.append(prim)
        return voids

    @property
    def pingroups(self):
        """Pin groups that the pin belongs to.

        Returns
        -------
        list
            List of pin groups that the pin belongs to.
        """
        return self._edb_padstackinstance.GetPinGroups()

    @property
    def placement_layer(self):
        """Placement layer.

        Returns
        -------
        str
            Name of the placement layer.
        """
        return self._edb_padstackinstance.GetGroup().GetPlacementLayer().GetName()

    @property
    def lower_elevation(self):
        """Lower elevation of the placement layer.

        Returns
        -------
        float
            Lower elavation of the placement layer.
        """
        return self._edb_padstackinstance.GetGroup().GetPlacementLayer().GetLowerElevation()

    @property
    def upper_elevation(self):
        """Upper elevation of the placement layer.

        Returns
        -------
        float
           Upper elevation of the placement layer.
        """
        return self._edb_padstackinstance.GetGroup().GetPlacementLayer().GetUpperElevation()

    @property
    def top_bottom_association(self):
        """Top/bottom association of the placement layer.

        Returns
        -------
        int
            Top/bottom association of the placement layer.

            * 0 Top associated.
            * 1 No association.
            * 2 Bottom associated.
            * 4 Number of top/bottom association type.
            * -1 Undefined.
        """
        return int(self._edb_padstackinstance.GetGroup().GetPlacementLayer().GetTopBottomAssociation())

    @pyaedt_function_handler()
    def create_rectangle_in_pad(self, layer_name, return_points=False):
        """Create a rectangle inscribed inside a padstack instance pad. The rectangle is fully inscribed in the
        pad and has the maximum area. It is necessary to specify the layer on which the rectangle will be created.

        Parameters
        ----------
        layer_name : str
            Name of the layer on which to create the polygon.

        return_points : bool, optional
            If `True` does not create the rectangle and just returns a list containing the rectangle vertices.
            Default is `False`.

        Returns
        -------
        bool, List,  :class:`pyaedt.edb_core.EDB_Data.EDBPrimitives`
            Polygon when successful, ``False`` when failed, list of list if `return_points=True`.

        Examples
        --------
        >>> from pyaedt import Edb
        >>> edbapp = Edb("myaedbfolder", edbversion="2021.2")
        >>> edb_layout = edbapp.core_primitives
        >>> list_of_padstack_instances = list(edbapp.core_padstack.padstack_instances.values())
        >>> padstack_inst = list_of_padstack_instances[0]
        >>> padstack_inst.create_rectangle_in_pad("TOP")
        """

        padstack_center = self.position
        rotation = self.rotation  # in radians
        padstack_name = self.padstack_definition
        try:
            padstack = self._pedb.core_padstack.padstacks[padstack_name]
        except KeyError:  # pragma: no cover
            return False
        try:
            padstack_pad = padstack.pad_by_layer[layer_name]
        except KeyError:  # pragma: no cover
            try:
                padstack_pad = padstack.pad_by_layer[padstack.via_start_layer]
            except KeyError:  # pragma: no cover
                return False

        pad_shape = padstack_pad.geometry_type
        params = padstack_pad.parameters_values
        polygon_data = padstack_pad.polygon_data

        def _rotate(p):
            x = p[0] * math.cos(rotation) - p[1] * math.sin(rotation)
            y = p[0] * math.sin(rotation) + p[1] * math.cos(rotation)
            return [x, y]

        def _translate(p):
            x = p[0] + padstack_center[0]
            y = p[1] + padstack_center[1]
            return [x, y]

        rect = None

        if pad_shape == 1:
            # Circle
            diameter = params[0]
            r = diameter * 0.5
            p1 = [r, 0.0]
            p2 = [0.0, r]
            p3 = [-r, 0.0]
            p4 = [0.0, -r]
            rect = [_translate(p1), _translate(p2), _translate(p3), _translate(p4)]
        elif pad_shape == 2:
            # Square
            square_size = params[0]
            s2 = square_size * 0.5
            p1 = [s2, s2]
            p2 = [-s2, s2]
            p3 = [-s2, -s2]
            p4 = [s2, -s2]
            rect = [
                _translate(_rotate(p1)),
                _translate(_rotate(p2)),
                _translate(_rotate(p3)),
                _translate(_rotate(p4)),
            ]
        elif pad_shape == 3:
            # Rectangle
            x_size = float(params[0])
            y_size = float(params[1])
            sx2 = x_size * 0.5
            sy2 = y_size * 0.5
            p1 = [sx2, sy2]
            p2 = [-sx2, sy2]
            p3 = [-sx2, -sy2]
            p4 = [sx2, -sy2]
            rect = [
                _translate(_rotate(p1)),
                _translate(_rotate(p2)),
                _translate(_rotate(p3)),
                _translate(_rotate(p4)),
            ]
        elif pad_shape == 4:
            # Oval
            x_size = params[0]
            y_size = params[1]
            corner_radius = float(params[2])
            if corner_radius >= min(x_size, y_size):
                r = min(x_size, y_size)
            else:
                r = corner_radius
            sx = x_size * 0.5 - r
            sy = y_size * 0.5 - r
            k = r / math.sqrt(2)
            p1 = [sx + k, sy + k]
            p2 = [-sx - k, sy + k]
            p3 = [-sx - k, -sy - k]
            p4 = [sx + k, -sy - k]
            rect = [
                _translate(_rotate(p1)),
                _translate(_rotate(p2)),
                _translate(_rotate(p3)),
                _translate(_rotate(p4)),
            ]
        elif pad_shape == 5:
            # Bullet
            x_size = params[0]
            y_size = params[1]
            corner_radius = params[2]
            if corner_radius >= min(x_size, y_size):
                r = min(x_size, y_size)
            else:
                r = corner_radius
            sx = x_size * 0.5 - r
            sy = y_size * 0.5 - r
            k = r / math.sqrt(2)
            p1 = [sx + k, sy + k]
            p2 = [-x_size * 0.5, sy + k]
            p3 = [-x_size * 0.5, -sy - k]
            p4 = [sx + k, -sy - k]
            rect = [
                _translate(_rotate(p1)),
                _translate(_rotate(p2)),
                _translate(_rotate(p3)),
                _translate(_rotate(p4)),
            ]
        elif pad_shape == 6:
            # N-Sided Polygon
            size = params[0]
            num_sides = params[1]
            ext_radius = size * 0.5
            apothem = ext_radius * math.cos(math.pi / num_sides)
            p1 = [apothem, 0.0]
            p2 = [0.0, apothem]
            p3 = [-apothem, 0.0]
            p4 = [0.0, -apothem]
            rect = [
                _translate(_rotate(p1)),
                _translate(_rotate(p2)),
                _translate(_rotate(p3)),
                _translate(_rotate(p4)),
            ]
        elif pad_shape == 0 and polygon_data is not None:
            # Polygon
            points = []
            i = 0
            while i < polygon_data.Count:
                point = polygon_data.GetPoint(i)
                if point.IsArc():
                    continue
                else:
                    points.append([point.X.ToDouble(), point.Y.ToDouble()])
                i += 1
            xpoly, ypoly = zip(*points)
            polygon = [list(xpoly), list(ypoly)]
            rectangles = GeometryOperators.find_largest_rectangle_inside_polygon(polygon)
            rect = rectangles[0]
            for i in range(4):
                rect[i] = _translate(_rotate(rect[i]))

        if rect is None or len(rect) != 4:
            return False
        path = self._pedb.core_primitives.Shape("polygon", points=rect)
        pdata = self._pedb.core_primitives.shape_to_polygon_data(path)
        new_rect = []
        for point in pdata.Points:
            p_transf = self._edb_padstackinstance.GetComponent().GetTransform().TransformPoint(point)
            new_rect.append([p_transf.X.ToDouble(), p_transf.Y.ToDouble()])
        if return_points:
            return new_rect
        else:
            path = self._pedb.core_primitives.Shape("polygon", points=new_rect)
            created_polygon = self._pedb.core_primitives.create_polygon(path, layer_name)
            return created_polygon


class EDBComponent(object):
    """Manages EDB functionalities for components.

    Parameters
    ----------
    parent : :class:`pyaedt.edb_core.components.Components`
        Inherited AEDT object.
    component : object
        Edb Component Object

    """

    def __init__(self, components, cmp):
        self._pcomponents = components
        self.edbcomponent = cmp

    @property
    def component_property(self):
        """Component Property Object."""
        return self.edbcomponent.GetComponentProperty().Clone()

    @property
    def solder_ball_height(self):
        """Solder ball height if available.."""
        if "GetSolderBallProperty" in dir(self.component_property):
            return self.component_property.GetSolderBallProperty().GetHeight()
        return None

    @property
    def solder_ball_placement(self):
        """Solder ball placement if available.."""
        if "GetSolderBallProperty" in dir(self.component_property):
            return int(self.component_property.GetSolderBallProperty().GetPlacement())
        return 2

    @property
    def refdes(self):
        """Reference Designator Name.

        Returns
        -------
        str
            Reference Designator Name.
        """
        return self.edbcomponent.GetName()

    @property
    def res_value(self):
        """Resitance Value.

        Returns
        -------
        str
            Resitance Value. ``None`` if not an RLC Type.
        """
        cmp_type = int(self.edbcomponent.GetComponentType())
        if 0 < cmp_type < 4:
            componentProperty = self.edbcomponent.GetComponentProperty()
            model = componentProperty.GetModel()
            pinpairs = model.PinPairs
            for pinpair in pinpairs:
                pair = model.GetPinPairRlc(pinpair)
                return pair.R.ToString()
        return None

    @property
    def cap_value(self):
        """Capacitance Value.

        Returns
        -------
        str
            Capacitance Value. ``None`` if not an RLC Type.
        """
        cmp_type = int(self.edbcomponent.GetComponentType())
        if 0 < cmp_type < 4:
            componentProperty = self.edbcomponent.GetComponentProperty()
            model = componentProperty.GetModel()
            pinpairs = model.PinPairs
            for pinpair in pinpairs:
                pair = model.GetPinPairRlc(pinpair)
                return pair.C.ToString()
        return None

    @property
    def ind_value(self):
        """Inductance Value.

        Returns
        -------
        str
            Inductance Value. ``None`` if not an RLC Type.
        """
        cmp_type = int(self.edbcomponent.GetComponentType())
        if 0 < cmp_type < 4:
            componentProperty = self.edbcomponent.GetComponentProperty()
            model = componentProperty.GetModel()
            pinpairs = model.PinPairs
            for pinpair in pinpairs:
                pair = model.GetPinPairRlc(pinpair)
                return pair.L.ToString()
        return None

    @property
    def is_parallel_rlc(self):
        """Define if model is Parallel or Series.

        Returns
        -------
        bool
            ``True`` if it is a parallel rlc model. ``False`` for series RLC. ``None`` if not an RLC Type.
        """
        cmp_type = int(self.edbcomponent.GetComponentType())
        if 0 < cmp_type < 4:
            componentProperty = self.edbcomponent.GetComponentProperty()
            model = componentProperty.GetModel()
            pinpairs = model.PinPairs
            for pinpair in pinpairs:
                pair = model.GetPinPairRlc(pinpair)
                return pair.IsParallel
        return None

    @property
    def center(self):
        """Compute the component center.

        Returns
        -------
        list
        """
        layinst = self.edbcomponent.GetLayout().GetLayoutInstance()
        cmpinst = layinst.GetLayoutObjInstance(self.edbcomponent, None)
        center = cmpinst.GetCenter()
        return [center.X.ToDouble(), center.Y.ToDouble()]

    @property
    def pinlist(self):
        """Pins of Component.

        Returns
        -------
        list
            List of Pins of Component.
        """
        pins = [
            p
            for p in self.edbcomponent.LayoutObjs
            if p.GetObjType() == self._edb.Cell.LayoutObjType.PadstackInstance and p.IsLayoutPin()
        ]
        return pins

    @property
    def nets(self):
        """Nets of Component.

        Returns
        -------
        list
            List of Nets of Component.
        """
        netlist = []
        for pin in self.pinlist:
            netlist.append(pin.GetNet().GetName())
        return list(set(netlist))

    @property
    def pins(self):
        """EDBPadstackInstance of Component.

        Returns
        -------
        dic[str, :class:`pyaedt.edb_core.EDB_Data.EDBPadstackInstance`]
            Dictionary of EDBPadstackInstance Components.
        """
        pins = {}
        for el in self.pinlist:
            pins[el.GetName()] = EDBPadstackInstance(el, self._pcomponents._pedb)
        return pins

    @property
    def type(self):
        """Component type.

        Returns
        -------
        str
            Component type.
        """
        cmp_type = int(self.edbcomponent.GetComponentType())
        if cmp_type == 1:
            return "Resistor"
        elif cmp_type == 2:
            return "Inductor"
        elif cmp_type == 3:
            return "Capacitor"
        elif cmp_type == 4:
            return "IC"
        elif cmp_type == 5:
            return "IO"
        elif cmp_type == 0:
            return "Other"

    @type.setter
    def type(self, new_type):
        """Set component type

        Parameters
        ----------
        new_type : str
            Type of the component. Options are ``"Resistor"``,  ``"Inductor"``, ``"Capacitor"``,
            ``"IC"``, ``"IO"`` and ``"Other"``.
        """
        if new_type == "Resistor":
            type_id = self._edb.Definition.ComponentType.Resistor
        elif new_type == "Inductor":
            type_id = self._edb.Definition.ComponentType.Inductor
        elif new_type == "Capacitor":
            type_id = self._edb.Definition.ComponentType.Capacitor
        elif new_type == "IC":
            type_id = self._edb.Definition.ComponentType.IC
        elif new_type == "IO":
            type_id = self._edb.Definition.ComponentType.IO
        elif new_type == "Other":
            type_id = self._edb.Definition.ComponentType.Other
        else:
            return
        self.edbcomponent.SetComponentType(type_id)

    @property
    def numpins(self):
        """Number of Pins of Component.

        Returns
        -------
        int
            Number of Pins of Component.
        """
        return self.edbcomponent.GetNumberOfPins()

    @property
    def partname(self):
        """Component Part Name.

        Returns
        -------
        str
            Component Part Name.
        """
        return self.edbcomponent.GetComponentDef().GetName()

    def _get_edb_value(self, value):
        return self._pcomponents._get_edb_value(value)

    @property
    def _edb(self):
        return self._pcomponents._edb

    @property
    def placement_layer(self):
        """Placement layer.

        Returns
        -------
        str
           Name of the placement layer.
        """
        return self.edbcomponent.GetPlacementLayer().GetName()

    @property
    def lower_elevation(self):
        """Lower elevation of the placement layer.

        Returns
        -------
        float
            Lower elevation of the placement layer.
        """
        return self.edbcomponent.GetPlacementLayer().GetLowerElevation()

    @property
    def upper_elevation(self):
        """Upper elevation of the placement layer.

        Returns
        -------
        float
            Upper elevation of the placement layer.

        """
        return self.edbcomponent.GetPlacementLayer().GetUpperElevation()

    @property
    def top_bottom_association(self):
        """Top/bottom association of the placement layer.

        Returns
        -------
        int
            Top/bottom association of the placement layer, where:

            * 0 - Top associated
            * 1 - No association
            * 2 - Bottom associated
            * 4 - Number of top/bottom associations.
            * -1 - Undefined
        """
        return int(self.edbcomponent.GetPlacementLayer().GetTopBottomAssociation())


class EdbBuilder(object):
    """Data Class to Overcome EdbLib in Linux."""

    def __init__(self, edbutils, db, cell):
        self.EdbHandler = edbutils.EdbHandler()
        self.EdbHandler.dB = db
        self.EdbHandler.cell = cell
        self.EdbHandler.layout = cell.GetLayout()


class SimulationConfiguration(object):
    """Data class used to parse s simulation configuration file. The configuration file is ASCII and supports all type
    of inputs to setup and automated any kind of SI or PI simulation both with HFSS 3D layout and Siwave. If field are
    omitted the default values will be applied. This class can be instantiated directly from
    Configuration file example:
    SolverType = 'Hfss3DLayout'
    GenerateSolerdBalls = 'True'
    SignalNets = ['net1', 'net2']
    PowerNets = ['gnd']
    Components = []
    SolderBallsDiams = ['0.077mm', '0.077mm']
    UseDefaultCoaxPortRadialExtentFactor='True'
    TrimRefSize='False'
    CutoutSubdesignType='Conformal'
    CutoutSubdesignExpansion='0.1'
    CutoutSubdesignRoundCorners='True'
    SweepInterpolating='True'
    UseQ3DForDC='True'
    RelatirelativeveErrorS='0.5'
    UseErrorZ0='False'
    PercentErrorZ0='1'
    EnforceCausality='True'
    EnforcePassivity='True'
    PassivityTolerance='0.0001'
    SweepName='Sweep1'
    RadiationBox='ConvexHull'
    StartFreq = '0.0GHz'
    StopFreq = '10.001GHz'
    SweepType='LinearStep'
    StepFreq = '0.040004GHz'
    Mesh_Freq = '3GHz'
    MaxNumPasses='30'
    MaxMagDeltaS='0.03'
    MinNumPasses='1'
    BasisOrder='Mixed'
    DoLambdaRefinement='True'
    ArcAngle='30deg'
    StartAzimuth='0'
    MaxArcPoints='8'
    UseArcToChordError='True'
    ArcToChordError='1um'
    DefeatureAbsLength='1um'
    DefeatureLayout='True'
    MinimumVoidSuface = '0'
    MaxSufDev = '0.001'
    ProcessPadstackDefinitions = 'False'
    ReturnCurrentDistribution = 'True'
    IgnoreNonFunctionalPads =  'True'
    IncludeInterPlaneCoupling = 'True'
    XtalkThreshold = '-50'
    MinVoidArea = '0.01mm2'
    MinPadAreaToMesh = '0.01mm2'
    SnapLengthThreshold = '2.5um'
    DcMinPlaneAreaToMesh = '8mil2'
    MaxInitMeshEdgeLength = '14.5mil'
    SignalLayersProperties = []
    """

    def __init__(self, filename):
        self._filename = filename
        self._setup_name = "Pyaedt_setup"
        self._generate_solder_balls = True
        self._signal_nets = []
        self._power_nets = []
        self._components = []
        self._coax_solder_ball_diameter = []
        self._use_default_coax_port_radial_extension = True
        self._trim_reference_size = False
        self._cutout_subdesign_type = CutoutSubdesignType.Conformal  # Conformal
        self._cutout_subdesign_expansion = 0.1
        self._cutout_subdesign_round_corner = True
        self._sweep_interpolating = True
        self._use_q3d_for_dc = False
        self._relative_error = 0.5
        self._use_error_z0 = False
        self._percentage_error_z0 = 1
        self._enforce_causality = True
        self._enforce_passivity = True
        self._passivity_tolerance = 0.0001
        self._sweep_name = "Sweep1"
        self._radiation_box = RadiationBoxType.ConvexHull  # 'ConvexHull'
        self._start_frequency = "0.0GHz"  # 0.0
        self._stop_freq = "10.0GHz"  # 10e9
        self._sweep_type = SweepType.Linear  # 'Linear'
        self._step_freq = "0.025GHz"  # 10e6
        self._decade_count = 100  # Newly Added
        self._mesh_freq = "3GHz"  # 5e9
        self._max_num_passes = 30
        self._max_mag_delta_s = 0.03
        self._min_num_passes = 1
        self._basis_order = BasisOrder.Mixed  # 'Mixed'
        self._do_lambda_refinement = True
        self._arc_angle = "30deg"  # 30
        self._start_azimuth = 0
        self._max_arc_points = 8
        self._use_arc_to_chord_error = True
        self._arc_to_chord_error = "1um"  # 1e-6
        self._defeature_abs_length = "1um"  # 1e-6
        self._defeature_layout = True
        self._minimum_void_surface = 0
        self._max_suf_dev = 1e-3
        self._process_padstack_definitions = False
        self._return_current_distribution = True
        self._ignore_non_functional_pads = True
        self._include_inter_plane_coupling = True
        self._xtalk_threshold = -50
        self._min_void_area = "0.01mm2"
        self._min_pad_area_to_mesh = "0.01mm2"
        self._snap_length_threshold = "2.5um"
        self._min_plane_area_to_mesh = "4mil2"  # Newly Added
        self._dc_min_plane_area_to_mesh = "8mil2"
        self._max_init_mesh_edge_length = "14.5mil"
        self._signal_layers_properties = {}
        self._coplanar_instances = []
        self._signal_layer_etching_instances = []
        self._etching_factor_instances = []
        self._dielectric_extent = 0.01
        self._airbox_horizontal_extent = 0.04
        self._airbox_negative_vertical_extent = 0.1
        self._airbox_positive_vertical_extent = 0.1
        self._honor_user_dielectric = False
        self._truncate_airbox_at_ground = False
        self._use_radiation_boundary = True
        self._do_cutout_subdesign = True
        self._solver_type = SolverType.Hfss3dLayout
        self._read_cfg()

    @property
    def generate_solder_balls(self):
        return self._generate_solder_balls

    @generate_solder_balls.setter
    def generate_solder_balls(self, value):
        if isinstance(value, bool):
            self._generate_solder_balls = value

    @property
    def signal_nets(self):
        return self._signal_nets

    @signal_nets.setter
    def signal_nets(self, value):
        if isinstance(value, list):
            self._signal_nets = value

    @property
    def setup_name(self):
        return self._setup_name

    @setup_name.setter
    def setup_name(self, value):
        if isinstance(value, str):
            self._setup_name = value

    @property
    def power_nets(self):
        return self._power_nets

    @power_nets.setter
    def power_nets(self, value):
        if isinstance(value, list):
            self._power_nets = value

    @property
    def components(self):
        return self._components

    @components.setter
    def components(self, value):
        if isinstance(value, list):
            self._components = value

    @property
    def coax_solder_ball_diameter(self):
        return self._coax_solder_ball_diameter

    @coax_solder_ball_diameter.setter
    def coax_solder_ball_diameter(self, value):
        if isinstance(value, list):
            self._coax_solder_ball_diameter = value

    @property
    def use_default_coax_port_radial_extension(self):
        return self._use_default_coax_port_radial_extension

    @use_default_coax_port_radial_extension.setter
    def use_default_coax_port_radial_extension(self, value):
        if isinstance(value, bool):
            self._use_default_coax_port_radial_extension = value

    @property
    def trim_reference_size(self):
        return self._trim_reference_size

    @trim_reference_size.setter
    def trim_reference_size(self, value):
        if isinstance(value, bool):
            self._trim_reference_size = value

    @property
    def do_cutout_subdesign(self):
        return self._do_cutout_subdesign

    @do_cutout_subdesign.setter
    def do_cutout_subdesign(self, value):
        if isinstance(value, bool):
            self._do_cutout_subdesign = value

    @property
    def cutout_subdesign_type(self):
        return self._cutout_subdesign_type

    @cutout_subdesign_type.setter
    def cutout_subdesign_type(self, value):
        if isinstance(value, CutoutSubdesignType):
            self._cutout_subdesign_type = value

    @property
    def cutout_subdesign_expansion(self):
        return self._cutout_subdesign_expansion

    @cutout_subdesign_expansion.setter
    def cutout_subdesign_expansion(self, value):
        if isinstance(value, float):
            self._cutout_subdesign_expansion = value

    @property
    def cutout_subdesign_round_corner(self):
        return self._cutout_subdesign_round_corner

    @cutout_subdesign_round_corner.setter
    def cutout_subdesign_round_corner(self, value):
        if isinstance(value, bool):
            self._cutout_subdesign_round_corner = value

    @property
    def sweep_interpolating(self):
        return self._sweep_interpolating

    @sweep_interpolating.setter
    def sweep_interpolating(self, value):
        if isinstance(value, bool):
            self._sweep_interpolating = value

    @property
    def use_q3d_for_dc(self):
        return self._use_q3d_for_dc

    @use_q3d_for_dc.setter
    def use_q3d_for_dc(self, value):
        if isinstance(value, bool):
            self._use_q3d_for_dc = value

    @property
    def relative_error(self):
        return self._relative_error

    @relative_error.setter
    def relative_error(self, value):
        if isinstance(value, float):
            self._relative_error = value

    @property
    def use_error_z0(self):
        return self._use_error_z0

    @use_error_z0.setter
    def use_error_z0(self, value):
        if isinstance(value, bool):
            self._use_error_z0 = value

    @property
    def percentage_error_z0(self):
        return self._percentage_error_z0

    @percentage_error_z0.setter
    def percentage_error_z0(self, value):
        if isinstance(value, float):
            self._percentage_error_z0 = value

    @property
    def enforce_causality(self):
        return self._enforce_causality

    @enforce_causality.setter
    def enforce_causality(self, value):
        if isinstance(value, bool):
            self._enforce_causality = value

    @property
    def enforce_passivity(self):
        return self._enforce_passivity

    @enforce_passivity.setter
    def enforce_passivity(self, value):
        if isinstance(value, bool):
            self._enforce_passivity = value

    @property
    def passivity_tolerance(self):
        return self._passivity_tolerance

    @passivity_tolerance.setter
    def passivity_tolerance(self, value):
        if isinstance(value, float):
            self._passivity_tolerance = value

    @property
    def sweep_name(self):
        return self._sweep_name

    @sweep_name.setter
    def sweep_name(self, value):
        if isinstance(value, str):
            self._sweep_name = value

    @property
    def radiation_box(self):
        return self._radiation_box

    @radiation_box.setter
    def radiation_box(self, value):
        if isinstance(value, RadiationBoxType):
            self._radiation_box = value

    @property
    def start_frequency(self):
        return self._start_frequency

    @start_frequency.setter
    def start_frequency(self, value):
        if isinstance(value, str):
            self._start_frequency = value

    @property
    def stop_freq(self):
        return self._stop_freq

    @stop_freq.setter
    def stop_freq(self, value):
        if isinstance(value, str):
            self._stop_freq = value

    @property
    def sweep_type(self):
        return self._sweep_type

    @sweep_type.setter
    def sweep_type(self, value):
        if isinstance(value, SweepType):
            self._sweep_type = value
        # if isinstance(value, str):
        #     self._sweep_type = value

    @property
    def step_freq(self):
        return self._step_freq

    @step_freq.setter
    def step_freq(self, value):
        if isinstance(value, str):
            self._step_freq = value

    @property
    def decade_count(self):
        return self._decade_count

    @decade_count.setter
    def decade_count(self, value):
        if isinstance(value, int):
            self._decade_count = value

    @property
    def mesh_freq(self):
        return self._mesh_freq

    @mesh_freq.setter
    def mesh_freq(self, value):
        if isinstance(value, str):
            self._mesh_freq = value

    @property
    def max_num_passes(self):
        return self._max_num_passes

    @max_num_passes.setter
    def max_num_passes(self, value):
        if isinstance(value, int):
            self._max_num_passes = value

    @property
    def max_mag_delta_s(self):
        return self._max_mag_delta_s

    @max_mag_delta_s.setter
    def max_mag_delta_s(self, value):
        if isinstance(value, float):
            self._max_mag_delta_s = value

    @property
    def min_num_passes(self):
        return self._min_num_passes

    @min_num_passes.setter
    def min_num_passes(self, value):
        if isinstance(value, int):
            self._min_num_passes = value

    @property
    def basis_order(self):
        return self._basis_order

    @basis_order.setter
    def basis_order(self, value):
        if isinstance(value, BasisOrder):
            self._basis_order = value

    @property
    def do_lambda_refinement(self):
        return self._do_lambda_refinement

    @do_lambda_refinement.setter
    def do_lambda_refinement(self, value):
        if isinstance(value, bool):
            self._do_lambda_refinement = value

    @property
    def arc_angle(self):
        return self._arc_angle

    @arc_angle.setter
    def arc_angle(self, value):
        if isinstance(value, str):
            self._arc_angle = value

    @property
    def start_azimuth(self):
        return self._start_azimuth

    @start_azimuth.setter
    def start_azimuth(self, value):
        if isinstance(value, float):
            self._start_azimuth = value

    @property
    def max_arc_points(self):
        return self._max_arc_points

    @max_arc_points.setter
    def max_arc_points(self, value):
        if isinstance(value, int):
            self._max_arc_points = value

    @property
    def use_arc_to_chord_error(self):
        return self._use_arc_to_chord_error

    @use_arc_to_chord_error.setter
    def use_arc_to_chord_error(self, value):
        if isinstance(value, bool):
            self._use_arc_to_chord_error = value

    @property
    def arc_to_chord_error(self):
        return self._arc_to_chord_error

    @arc_to_chord_error.setter
    def arc_to_chord_error(self, value):
        if isinstance(value, str):
            self._arc_to_chord_error = value

    @property
    def defeature_abs_length(self):
        return self._defeature_abs_length

    @defeature_abs_length.setter
    def defeature_abs_length(self, value):
        if isinstance(value, str):
            self._defeature_abs_length = value

    @property
    def defeature_layout(self):
        return self._defeature_layout

    @defeature_layout.setter
    def defeature_layout(self, value):
        if isinstance(value, bool):
            self._defeature_layout = value

    @property
    def minimum_void_surface(self):
        return self._minimum_void_surface

    @minimum_void_surface.setter
    def minimum_void_surface(self, value):
        if isinstance(value, float):
            self._minimum_void_surface = value

    @property
    def max_suf_dev(self):
        return self._max_suf_dev

    @max_suf_dev.setter
    def max_suf_dev(self, value):
        if isinstance(value, float):
            self._max_suf_dev = value

    @property
    def process_padstack_definitions(self):
        return self._process_padstack_definitions

    @process_padstack_definitions.setter
    def process_padstack_definitions(self, value):
        if isinstance(value, bool):
            self._process_padstack_definitions = value

    @property
    def return_current_distribution(self):
        return self._return_current_distribution

    @return_current_distribution.setter
    def return_current_distribution(self, value):
        if isinstance(value, bool):
            self._return_current_distribution = value

    @property
    def ignore_non_functional_pads(self):
        return self._ignore_non_functional_pads

    @ignore_non_functional_pads.setter
    def ignore_non_functional_pads(self, value):
        if isinstance(value, bool):
            self._ignore_non_functional_pads = value

    @property
    def include_inter_plane_coupling(self):
        return self._include_inter_plane_coupling

    @include_inter_plane_coupling.setter
    def include_inter_plane_coupling(self, value):
        if isinstance(value, bool):
            self._include_inter_plane_coupling = value

    @property
    def xtalk_threshold(self):
        return self._xtalk_threshold

    @xtalk_threshold.setter
    def xtalk_threshold(self, value):
        if isinstance(value, float):
            self._xtalk_threshold = value

    @property
    def min_void_area(self):
        return self._min_void_area

    @min_void_area.setter
    def min_void_area(self, value):
        if isinstance(value, str):
            self._min_void_area = value

    @property
    def min_pad_area_to_mesh(self):
        return self._min_pad_area_to_mesh

    @min_pad_area_to_mesh.setter
    def min_pad_area_to_mesh(self, value):
        if isinstance(value, str):
            self._min_pad_area_to_mesh = value

    @property
    def snap_length_threshold(self):
        return self._snap_length_threshold

    @snap_length_threshold.setter
    def snap_length_threshold(self, value):
        if isinstance(value, str):
            self._snap_length_threshold = value

    @property
    def min_plane_area_to_mesh(self):
        return self._min_plane_area_to_mesh

    @min_plane_area_to_mesh.setter
    def min_plane_area_to_mesh(self, value):
        if isinstance(value, str):
            self._min_plane_area_to_mesh = value

    @property
    def dc_min_plane_area_to_mesh(self):
        return self._dc_min_plane_area_to_mesh

    @dc_min_plane_area_to_mesh.setter
    def dc_min_plane_area_to_mesh(self, value):
        if isinstance(value, str):
            self._dc_min_plane_area_to_mesh = value

    @property
    def max_init_mesh_edge_length(self):
        return self._max_init_mesh_edge_length

    @max_init_mesh_edge_length.setter
    def max_init_mesh_edge_length(self, value):
        if isinstance(value, str):
            self._max_init_mesh_edge_length = value

    @property
    def signal_layers_properties(self):
        return self._signal_layers_properties

    @signal_layers_properties.setter
    def signal_layers_properties(self, value):
        if isinstance(value, dict):
            self._signal_layers_properties = value

    @property
    def coplanar_instances(self):
        return self._coplanar_instances

    @coplanar_instances.setter
    def coplanar_instances(self, value):
        if isinstance(value, list):
            self._coplanar_instances = value

    @property
    def signal_layer_etching_instances(self):
        return self._signal_layer_etching_instances

    @signal_layer_etching_instances.setter
    def signal_layer_etching_instances(self, value):
        if isinstance(value, list):
            self._signal_layer_etching_instances = value

    @property
    def etching_factor_instances(self):
        return self._etching_factor_instances

    @etching_factor_instances.setter
    def etching_factor_instances(self, value):
        if isinstance(value, list):
            self._etching_factor_instances = value

    @property
    def dielectric_extent(self):
        return self._dielectric_extent

    @dielectric_extent.setter
    def dielectric_extent(self, value):
        if isinstance(value, float):
            self._dielectric_extent = value

    @property
    def airbox_horizontal_extent(self):
        return self._airbox_horizontal_extent

    @airbox_horizontal_extent.setter
    def airbox_horizontal_extent(self, value):
        if isinstance(value, float):
            self._airbox_horizontal_extent = value

    @property
    def airbox_negative_vertical_extent(self):
        return self._airbox_negative_vertical_extent

    @airbox_negative_vertical_extent.setter
    def airbox_negative_vertical_extent(self, value):
        if isinstance(value, float):
            self._airbox_negative_vertical_extent = value

    @property
    def airbox_positive_vertical_extent(self):
        return self._airbox_positive_vertical_extent

    @airbox_positive_vertical_extent.setter
    def airbox_positive_vertical_extent(self, value):
        if isinstance(value, float):
            self._airbox_positive_vertical_extent = value

    @property
    def honor_user_dielectric(self):
        return self._honor_user_dielectric

    @honor_user_dielectric.setter
    def honor_user_dielectric(self, value):
        if isinstance(value, bool):
            self._honor_user_dielectric = value

    @property
    def truncate_airbox_at_ground(self):
        return self._truncate_airbox_at_ground

    @truncate_airbox_at_ground.setter
    def truncate_airbox_at_ground(self, value):
        if isinstance(value, bool):
            self._truncate_airbox_at_ground = value

    @property
    def solver_type(self):
        return self._solver_type

    @solver_type.setter
    def solver_type(self, value):
        if isinstance(value, int):
            self._solver_type = value

    @property
    def use_radiation_boundary(self):
        return self._use_radiation_boundary

    @use_radiation_boundary.setter
    def use_radiation_boundary(self, value):
        if isinstance(value, bool):
            self._use_radiation_boundary = value

    def _get_bool_value(self, value):
        val = value.lower()
        if val in ("y", "yes", "t", "true", "on", "1"):
            return True
        elif val in ("n", "no", "f", "false", "off", "0"):
            return False
        else:
            raise ValueError("invalid truth value %r" % (val,))

    def _get_list_value(self, value):
        value = value.strip("[]")
        if len(value) == 0:
            return []
        else:
            value = value.split(",")
            if isinstance(value, list):
                prop_values = [i.strip() for i in value]
            else:
                prop_values = [value.strip()]
            return prop_values

    def _parse_signal_layer_properties(self, signal_properties):
        for lay in signal_properties:
            lp = lay.split(":")
            try:
                self.signal_layers_properties.update({lp[0]: [lp[1], lp[2], lp[3], lp[4], lp[5]]})
            except:
                print("Missing parameter for layer {0}".format(lp[0]))

    def _read_cfg(self):
        """Configuration file reader.

        Examples
        --------

        >>> from pyaedt import Edb
        >>> from pyaedt.edb_core.EDB_Data import SimulationConfiguration
        >>> config_file = path_configuration_file
        >>> source_file = path_to_edb_folder
        >>> edb = Edb(source_file)
        >>> sim_setup = SimulationConfiguration(config_file)
        >>> edb.build_simulation_project(sim_setup)
        >>> edb.save_edb()
        >>> edb.close_edb()
        """

        if not os.path.exists(self._filename):
            # raise Exception("{} does not exist.".format(self._filename))
            pass

        try:
            with open(self._filename) as cfg_file:
                cfg_lines = cfg_file.read().split("\n")
                for line in cfg_lines:
                    if line.strip() != "":
                        if line.find("="):
                            i, prop_value = line.strip().split("=")
                            value = prop_value.replace("'", "").strip()
                            if i.startswith("GenerateSolderBalls"):
                                self.generate_solder_balls = self._get_bool_value(value)
                            elif i.startswith("SignalNets"):
                                self.signal_nets = self._get_list_value(value)
                            elif i.startswith("PowerNets"):
                                self.power_nets = self._get_list_value(value)
                            elif i.startswith("Components"):
                                self.components = self._get_list_value(value)
                            elif i.startswith("coaxSolderBallsDiams"):
                                self.coax_solder_ball_diameter = self._get_list_value(value)
                            elif i.startswith("UseDefaultCoaxPortRadialExtentFactor"):
                                self.signal_nets = self._get_bool_value(value)
                            elif i.startswith("TrimRefSize"):
                                self.trim_reference_size = self._get_bool_value(value)
                            elif i.startswith("CutoutSubdesignType"):
                                if value.lower().startswith("conformal"):
                                    self.cutout_subdesign_type = CutoutSubdesignType.Conformal
                                elif value.lower().startswith("boundingbox"):
                                    self.cutout_subdesign_type = CutoutSubdesignType.BoundingBox
                                else:
                                    print("Unprocessed value for CutoutSubdesignType '{0}'".format(value))
                            elif i.startswith("CutoutSubdesignExpansion"):
                                self.cutout_subdesign_expansion = float(value)
                            elif i.startswith("CutoutSubdesignRoundCorners"):
                                self.cutout_subdesign_round_corner = self._get_bool_value(value)
                            elif i.startswith("SweepInterpolating"):
                                self.sweep_interpolating = self._get_bool_value(value)
                            elif i.startswith("UseQ3DForDC"):
                                self.use_q3d_for_dc = self._get_bool_value(value)
                            elif i.startswith("RelativeErrorS"):
                                self.relative_error = float(value)
                            elif i.startswith("UseErrorZ0"):
                                self.use_error_z0 = self._get_bool_value(value)
                            elif i.startswith("PercentErrorZ0"):
                                self.percentage_error_z0 = float(value)
                            elif i.startswith("EnforceCausality"):
                                self.enforce_causality = self._get_bool_value(value)
                            elif i.startswith("EnforcePassivity"):
                                self.enforce_passivity = self._get_bool_value(value)
                            elif i.startswith("PassivityTolerance"):
                                self.passivity_tolerance = float(value)
                            elif i.startswith("SweepName"):
                                self.sweep_name = value
                            elif i.startswith("RadiationBox"):
                                if value.lower().startswith("conformal"):
                                    self.radiation_box = RadiationBoxType.Conformal
                                elif value.lower().startswith("boundingbox"):
                                    self.radiation_box = RadiationBoxType.BoundingBox
                                elif value.lower().startswith("convexhull"):
                                    self.radiation_box = RadiationBoxType.ConvexHull
                                else:
                                    print("Unprocessed value for RadiationBox '{0}'".format(value))
                            elif i.startswith("StartFreq"):
                                self.start_frequency = value
                            elif i.startswith("StopFreq"):
                                self.stop_freq = value
                            elif i.startswith("SweepType"):
                                if value.lower().startswith("linear"):
                                    self.sweep_type = SweepType.Linear
                                elif value.lower().startswith("logcount"):
                                    self.sweep_type = SweepType.LogCount
                                else:
                                    print("Unprocessed value for SweepType '{0}'".format(value))
                            elif i.startswith("StepFreq"):
                                self.step_freq = value
                            elif i.startswith("DecadeCount"):
                                self.decade_count = int(value)
                            elif i.startswith("Mesh_Freq"):
                                self.mesh_freq = value
                            elif i.startswith("MaxNumPasses"):
                                self.max_num_passes = int(value)
                            elif i.startswith("MaxMagDeltaS"):
                                self.max_mag_delta_s = float(value)
                            elif i.startswith("MinNumPasses"):
                                self.min_num_passes = int(value)
                            elif i.startswith("BasisOrder"):
                                if value.lower().startswith("mixed"):
                                    self.basis_order = BasisOrder.Mixed
                                elif value.lower().startswith("zero"):
                                    self.basis_order = BasisOrder.Zero
                                elif value.lower().startswith("first"):  # single
                                    self.basis_order = BasisOrder.single
                                elif value.lower().startswith("second"):  # double
                                    self.basis_order = BasisOrder.Double
                                else:
                                    print("Unprocessed value for BasisOrder '{0}'".format(value))
                            elif i.startswith("DoLambdaRefinement"):
                                self.do_lambda_refinement = self._get_bool_value(value)
                            elif i.startswith("ArcAngle"):
                                self.arc_angle = value
                            elif i.startswith("StartAzimuth"):
                                self.start_azimuth = float(value)
                            elif i.startswith("MaxArcPoints"):
                                self.max_arc_points = int(value)
                            elif i.startswith("UseArcToChordError"):
                                self.use_arc_to_chord_error = self._get_bool_value(value)
                            elif i.startswith("ArcToChordError"):
                                self.arc_to_chord_error = value
                            elif i.startswith("DefeatureAbsLength"):
                                self.defeature_abs_length = value
                            elif i.startswith("DefeatureLayout"):
                                self.defeature_layout = self._get_bool_value(value)
                            elif i.startswith("MinimumVoidSuface"):
                                self.minimum_void_surface = float(value)
                            elif i.startswith("MaxSufDev"):
                                self.max_suf_dev = float(value)
                            elif i.startswith("ProcessPadstackDefinitions"):
                                self.process_padstack_definitions = self._get_bool_value(value)
                            elif i.startswith("ReturnCurrentDistribution"):
                                self.return_current_distribution = self._get_bool_value(value)
                            elif i.startswith("IgnoreNonFunctionalPads"):
                                self.ignore_non_functional_pads = self._get_bool_value(value)
                            elif i.startswith("IncludeInterPlaneCoupling"):
                                self.include_inter_plane_coupling = self._get_bool_value(value)
                            elif i.startswith("XtalkThreshold"):
                                self.xtalk_threshold = float(value)
                            elif i.startswith("MinVoidArea"):
                                self.min_void_area = value
                            elif i.startswith("MinPadAreaToMesh"):
                                self.min_pad_area_to_mesh = value
                            elif i.startswith("SnapLengthThreshold"):
                                self.snap_length_threshold = value
                            elif i.startswith("MinPlaneAreaToMesh"):
                                self.min_plane_area_to_mesh = value
                            elif i.startswith("DcMinPlaneAreaToMesh"):
                                self.dc_min_plane_area_to_mesh = value
                            elif i.startswith("MaxInitMeshEdgeLength"):
                                self.max_init_mesh_edge_length = value
                            elif i.startswith("SignalLayersProperties"):
                                self._parse_signal_layer_properties(self._get_list_value(value))
                            elif i.startswith("coplanar_instances"):
                                self.coplanar_instances = self._get_list_value(value)
                            elif i.startswith("SignalLayersEtching"):
                                self.signal_layer_etching_instances = self._get_list_value(value)
                            elif i.startswith("EtchingFactor"):
                                self.etching_factor_instances = self._get_list_value(value)
                            elif i.startswith("DoCutoutSubdesign"):
                                self.do_cutout_subdesign = self._get_list_value(value)
                            elif i.startswith("SolverType"):
                                if value.lower() == "hfss":
                                    self.solver_type = 0
                                if value.lower() == "hfss3dlayout":
                                    self.solver_type = 6
                                elif value.lower().startswith("siwave"):
                                    self.solver_type = 1
                                elif value.lower().startswith("q3d"):
                                    self.solver_type = 2
                                elif value.lower().startswith("nexxim"):
                                    self.solver_type = 4
                                elif value.lower().startswith("maxwell"):
                                    self.solver_type = 3
                                elif value.lower().startswith("twinbuilder"):
                                    self.solver_type = 5
                                else:
                                    self.solver_type = SolverType.Hfss3dLayout
                        else:
                            print("Unprocessed line in cfg file: {0}".format(line))
                    else:
                        continue
        except EnvironmentError as e:
            print("Error reading cfg file: {}".format(e.message))
            raise
