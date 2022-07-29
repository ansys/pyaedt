import json
import math
import os
import time
import warnings
from collections import OrderedDict

from pyaedt import generate_unique_name
from pyaedt.edb_core.general import convert_py_list_to_net_list
from pyaedt.generic.constants import BasisOrder
from pyaedt.generic.constants import CutoutSubdesignType
from pyaedt.generic.constants import NodeType
from pyaedt.generic.constants import RadiationBoxType
from pyaedt.generic.constants import SolverType
from pyaedt.generic.constants import SourceType
from pyaedt.generic.constants import SweepType
from pyaedt.generic.constants import validate_enum_class_value
from pyaedt.generic.general_methods import pyaedt_function_handler
from pyaedt.modeler.GeometryOperators import GeometryOperators

try:
    from System.Collections.Generic import List
except ImportError:
    if os.name != "posix":
        warnings.warn(
            "The clr is missing. Install PythonNET or use an IronPython version if you want to use the EDB module."
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
        """Plot a net to Matplotlib 2D chart.

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
        self._negative_layer = False
        self._roughness_enabled = False
        self._lower_elevation = None
        self._upper_elevation = None
        self._top_bottom_association = None
        self._id = None
        self._edb = app._edb
        self._active_layout = app._active_layout
        self._pedblayers = app
        self.init_vals()

    @property
    def _cloned_layer(self):
        return self._layer.Clone()

    @property
    def _builder(self):
        return self._pedblayers._builder

    @property
    def _logger(self):
        """Logger."""
        return self._pedblayers._logger

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
        return self._pedblayers._layer_types_to_int(self._layer_type)

    @layer_type.setter
    def layer_type(self, value):
        if type(value) is not type(self._layer_type):
            self._layer_type = self._pedblayers._int_to_layer_types(value)
            self.update_layers()
        else:
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
            self._material_name = self._cloned_layer.GetMaterial()
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
            self._thickness = self._cloned_layer.GetThicknessValue().ToDouble()
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
        if (
            self._layer_type == self._edb.Cell.LayerType.SignalLayer
            or self._layer_type == self._edb.Cell.LayerType.ConductingLayer
        ):
            try:
                self._filling_material_name = self._cloned_layer.GetFillMaterial()
            except:
                pass
            return self._filling_material_name
        return ""

    @filling_material_name.setter
    def filling_material_name(self, value):

        if (
            self._layer_type == self._edb.Cell.LayerType.SignalLayer
            or self._layer_type == self._edb.Cell.LayerType.ConductingLayer
        ):
            self._filling_material_name = value
            self.update_layers()

    @property
    def negative_layer(self):
        """Negative layer.

        Returns
        -------
        bool
            ``True`` when negative, ``False`` otherwise..
        """
        if (
            self._layer_type == self._edb.Cell.LayerType.SignalLayer
            or self._layer_type == self._edb.Cell.LayerType.ConductingLayer
        ):
            try:
                self._negative_layer = self._layer.GetNegative()
            except:
                pass
        return self._negative_layer

    @negative_layer.setter
    def negative_layer(self, value):
        if (
            self._layer_type == self._edb.Cell.LayerType.SignalLayer
            or self._layer_type == self._edb.Cell.LayerType.ConductingLayer
        ):
            self._negative_layer = value
            self.update_layers()

    @property
    def roughness_enabled(self):
        """Roughness enabled.

        Returns
        -------
        bool
            ``True`` if the layer has roughness, ``False`` otherwise.
        """
        if (
            self._layer_type == self._edb.Cell.LayerType.SignalLayer
            or self._layer_type == self._edb.Cell.LayerType.ConductingLayer
        ):
            try:
                self._roughness_enabled = self._layer.IsRoughnessEnabled()
            except:
                pass
        return self._roughness_enabled

    @roughness_enabled.setter
    def roughness_enabled(self, value):
        if (
            self._layer_type == self._edb.Cell.LayerType.SignalLayer
            or self._layer_type == self._edb.Cell.LayerType.ConductingLayer
        ):
            self._roughness_enabled = value
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
            self._lower_elevation = self._cloned_layer.GetLowerElevation()
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
            self._upper_elevation = self._cloned_layer.GetUpperElevation()
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
        if (
            self._layer_type == self._edb.Cell.LayerType.SignalLayer
            or self._layer_type == self._edb.Cell.LayerType.ConductingLayer
        ):
            try:
                self._etch_factor = float(self._cloned_layer.GetEtchFactor().ToString())
                return self._etch_factor
            except:
                pass
        return 0

    @etch_factor.setter
    def etch_factor(self, value):
        if value is None:
            value = 0
        if (
            self._layer_type == self._edb.Cell.LayerType.SignalLayer
            or self._layer_type == self._edb.Cell.LayerType.ConductingLayer
        ):
            self._etch_factor = float(value)
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
        """Plot a layer to a Matplotlib 2D chart.

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
            if (
                self._layer_type == self._edb.Cell.LayerType.SignalLayer
                or self._layer_type == self._edb.Cell.LayerType.ConductingLayer
            ):
                self._etch_factor = float(self._layer.GetEtchFactor().ToString())
                self._filling_material_name = self._layer.GetFillMaterial()
                self._negative_layer = self._layer.GetNegative()
                self._roughness_enabled = self._layer.IsRoughnessEnabled()
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
        negativeMap,
        roughnessMap,
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

        negativeMap :

        roughnessMap :

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
        if negativeMap:
            newLayer.SetNegative(negativeMap)
        if roughnessMap:
            newLayer.SetRoughnessEnabled(roughnessMap)
        if isinstance(etchMap, float) and int(layerTypeMap) in [0, 2]:
            etchVal = float(etchMap)
        else:
            etchVal = 0.0
        if etchVal != 0.0:
            newLayer.SetEtchFactorEnabled(True)
            newLayer.SetEtchFactor(self._get_edb_value(etchVal))
        else:
            newLayer.SetEtchFactor(self._get_edb_value(etchVal))
            newLayer.SetEtchFactorEnabled(False)
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
        layer_collection_mode = thisLC.GetMode()
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
                    self._negative_layer,
                    self._roughness_enabled,
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
        if not lcNew.AddLayers(newLayers):
            self._logger.error("Failed to set new layers when updating the stackup information.")
            return False
        lcNew.SetMode(layer_collection_mode)
        if not self._active_layout.SetLayerCollection(lcNew):
            self._logger.error("Failed to set new layer stackup mode when updating the stackup information.")
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
        return self._pedbstackup._logger

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
            key=lambda lyr=self._edb.Cell.StackupLayer: lyr.Clone().GetLowerElevation(),
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

    @pyaedt_function_handler()
    def _layer_types_to_int(self, layer_type):
        if not isinstance(layer_type, int):
            if layer_type == self.layer_types.SignalLayer:
                return 0
            elif layer_type == self.layer_types.DielectricLayer:
                return 1
            elif layer_type == self.layer_types.ConductingLayer:
                return 2
            elif layer_type == self.layer_types.AirlinesLayer:
                return 3
            elif layer_type == self.layer_types.ErrorsLayer:
                return 4
            elif layer_type == self.layer_types.SymbolLayer:
                return 5
            elif layer_type == self.layer_types.MeasureLayer:
                return 6
            elif layer_type == self.layer_types.AssemblyLayer:
                return 8
            elif layer_type == self.layer_types.SilkscreenLayer:
                return 9
            elif layer_type == self.layer_types.SolderMaskLayer:
                return 10
            elif layer_type == self.layer_types.SolderPasteLayer:
                return 11
            elif layer_type == self.layer_types.GlueLayer:
                return 12
            elif layer_type == self.layer_types.WirebondLayer:
                return 13
            elif layer_type == self.layer_types.UserLayer:
                return 14
            elif layer_type == self.layer_types.SIwaveHFSSSolverRegions:
                return 16
            elif layer_type == self.layer_types.OutlineLayer:
                return 18
        elif isinstance(layer_type, int):
            return layer_type

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
        negative_layer=False,
        roughness_enabled=False,
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
            Type of the layer. The default is ``0``
            ``0``: Signal layer.
            ``1``: Dielectric layer.
            ``2``: Conducting plane layer.
            ``3``: Airline layer.
            ``4``: Error layer.
            ``5``: Symbol layer.
            ``6``: Measure layer.
            ``8``: Assembly layer.
            ``9``: Silkscreen layer.
            ``10``: Solder Mask layer.
            ``11``: Solder Paste layer.
        negative_layer : bool, optional
            ``True`` when negative, ``False`` otherwise.
        roughness_enabled : bool, optional
            ``True`` if the layer has roughness, ``False`` otherwise.
        etchMap : optional
            Etch value if any. The default is ``None``.

        Returns
        -------
        :class:`pyaedt.edb_core.EDB_Data.EDBLayer`
            Layer Object for stackup layers. Boolean otherwise (True in case of success).
        """
        thisLC = self._pedbstackup._active_layout.GetLayerCollection()
        layers = list(list(thisLC.Layers(self._edb.Cell.LayerTypeSet.AllLayerSet)))
        layers.reverse()
        el = 0.0
        lcNew = self._edb.Cell.LayerCollection()

        if not layers or not start_layer:
            if int(layerType) > 2:
                newLayer = self._edb.Cell.Layer(layerName, self._int_to_layer_types(layerType))
                lcNew.AddLayerTop(newLayer)
            else:
                newLayer = self._edb.Cell.StackupLayer(
                    layerName,
                    self._int_to_layer_types(layerType),
                    self._get_edb_value(0),
                    self._get_edb_value(0),
                    "",
                )
                self._edb_object[layerName] = EDBLayer(newLayer.Clone(), self._pedbstackup)
                newLayer = self._edb_object[layerName].update_layer_vals(
                    layerName,
                    newLayer,
                    etchMap,
                    material,
                    fillMaterial,
                    thickness,
                    negative_layer,
                    roughness_enabled,
                    self._int_to_layer_types(layerType),
                )
                newLayer.SetLowerElevation(self._get_edb_value(el))

                lcNew.AddLayerTop(newLayer)
                el += newLayer.GetThickness()
            for lyr in layers:
                if not lyr.IsStackupLayer():
                    continue
                newLayer = lyr.Clone()
                newLayer.SetLowerElevation(self._get_edb_value(el))
                el += newLayer.GetThickness()
                lcNew.AddLayerTop(newLayer)
            for lyr in layers:
                if not lyr.IsStackupLayer():
                    lcNew.AddLayerTop(lyr.Clone())
                    continue
        else:
            for lyr in layers:
                if not lyr.IsStackupLayer():
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
                    self._edb_object[layerName] = EDBLayer(newLayer.Clone(), self._pedbstackup)
                    newLayer = self._edb_object[layerName].update_layer_vals(
                        layerName,
                        newLayer,
                        etchMap,
                        material,
                        fillMaterial,
                        thickness,
                        negative_layer,
                        roughness_enabled,
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
            for lyr in layers:
                if not lyr.IsStackupLayer():
                    lcNew.AddLayerTop(lyr.Clone())
                    continue
        if not self._active_layout.SetLayerCollection(lcNew):
            self._logger.error("Failed to set new layers when updating the stackup information.")
            return False
        self._update_edb_objects()
        allLayers = [
            i.GetName() for i in list(list(self.layer_collection.Layers(self._edb.Cell.LayerTypeSet.AllLayerSet)))
        ]
        if layerName in self.layers:
            return self.layers[layerName]
        elif layerName in allLayers:
            return True
        return False

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

        padparams = self._edb_padstack.GetData().GetPadParametersValue(
            self.layer_name, self.int_to_pad_type(self.pad_type)
        )
        return int(padparams[1])

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

        pad_values = self._edb_padstack.GetData().GetPadParametersValue(
            self.layer_name, self.int_to_pad_type(self.pad_type)
        )
        return [i.ToDouble() for i in pad_values[2]]

    @property
    def polygon_data(self):
        """Parameters.

        Returns
        -------
        list
            List of parameters.
        """
        try:
            pad_values = self._edb_padstack.GetData().GetPolygonalPadParameters(
                self.layer_name, self.int_to_pad_type(self.pad_type)
            )
            return pad_values[1]
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
        pad_values = self._edb_padstack.GetData().GetPadParametersValue(
            self.layer_name, self.int_to_pad_type(self.pad_type)
        )

        # pad_values = self._padstack_methods.GetPadParametersValue(self._edb_padstack, self.layer_name, self)
        return [i.ToString() for i in pad_values[2]]

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

        pad_values = self._edb_padstack.GetData().GetPadParametersValue(
            self.layer_name, self.int_to_pad_type(self.pad_type)
        )
        return pad_values[3].ToString()

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

        pad_values = self._edb_padstack.GetData().GetPadParametersValue(
            self.layer_name, self.int_to_pad_type(self.pad_type)
        )
        return pad_values[4].ToString()

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

        pad_values = self._edb_padstack.GetData().GetPadParametersValue(
            self.layer_name, self.int_to_pad_type(self.pad_type)
        )
        return pad_values[5].ToString()

    @rotation.setter
    def rotation(self, rotation_value):

        self._update_pad_parameters_parameters(rotation=rotation_value)

    @pyaedt_function_handler()
    def int_to_pad_type(self, val=0):
        """Convert an integer to an EDB.PadGeometryType.

        Parameters
        ----------
        val : int

        Returns
        -------
        object
            EDB.PadType enumerator value.
        """
        return self._pedbpadstack._ppadstack.int_to_pad_type(val)

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
        return self._pedbpadstack._ppadstack.int_to_geometry_type(val)

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

        newPadstackDefinitionData.SetPadParameters(
            layer_name,
            self.int_to_pad_type(pad_type),
            self.int_to_geometry_type(geom_type),
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
        self._bounding_box = []
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
        out = viaData.GetHoleParametersValue()
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
        if isinstance(params, list):
            params = convert_py_list_to_net_list(params)
        if not offsetx:
            offsetx = self.hole_offset_x
        if not offsety:
            offsety = self.hole_offset_y
        if not rotation:
            rotation = self.hole_rotation
        newPadstackDefinitionData.SetHoleParameters(
            hole_type,
            params,
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
        return self._edb.Definition.PadstackDefData(self.edb_padstack.GetData()).GetHolePlatingPercentage()

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

    @hole_plating_thickness.setter
    def hole_plating_thickness(self, value):
        """Hole plating thickness.

        Returns
        -------
        float
            Thickness of the hole plating if present.
        """
        hr = 200 * float(value) / float(self.hole_properties[0])
        self.hole_plating_ratio = hr

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
        self._bounding_box = []

    @property
    def bounding_box(self):
        """Get bounding box of the padstack instance.
        Because this method is slow, the bounding box is stored in a variable and reused.

        Returns
        -------
        list of float
        """
        if self._bounding_box:
            return self._bounding_box
        bbox = (
            self._edb_padstackinstance.GetLayout()
            .GetLayoutInstance()
            .GetLayoutObjInstance(self._edb_padstackinstance, None)
            .GetBBox()
        )
        self._bounding_box = [
            [bbox.Item1.X.ToDouble(), bbox.Item1.Y.ToDouble()],
            [bbox.Item2.X.ToDouble(), bbox.Item2.Y.ToDouble()],
        ]
        return self._bounding_box

    @pyaedt_function_handler()
    def in_polygon(self, polygon_data, include_partial=True):
        """Check if padstack Instance is in given polygon data.

        Parameters
        ----------
        polygon_data : PolygonData Object
        include_partial : bool, optional
            Whether to include partial intersecting instances. The default is ``True``.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.
        """
        plane = self._pedb.core_primitives.Shape("rectangle", pointA=self.bounding_box[0], pointB=self.bounding_box[1])
        rectangle_data = self._pedb.core_primitives.shape_to_polygon_data(plane)
        int_val = polygon_data.GetIntersectionType(rectangle_data)
        # Intersection type:
        # 0 = objects do not intersect
        # 1 = this object fully inside other (no common contour points)
        # 2 = other object fully inside this
        # 3 = common contour points 4 = undefined intersection
        if int_val == 0:
            return False
        elif include_partial:
            return True
        elif int_val < 3:
            return True
        else:
            return False

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
        layer = self._pedb.edb.Cell.Layer("", self._pedb.edb.Cell.LayerType.SignalLayer)
        _, start_layer, stop_layer = self._edb_padstackinstance.GetLayerRange()

        if start_layer:
            return start_layer.GetName()
        return None

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
        layer = self._pedb.edb.Cell.Layer("", self._pedb.edb.Cell.LayerType.SignalLayer)
        _, start_layer, stop_layer = self._edb_padstackinstance.GetLayerRange()

        if stop_layer:
            return stop_layer.GetName()
        return None

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
        out = self._edb_padstackinstance.GetPositionAndRotationValue()

        if out[0]:
            return [out[1].X.ToDouble(), out[1].Y.ToDouble()]

    @position.setter
    def position(self, value):
        pos = []
        for v in value:
            if isinstance(v, (float, int, str)):
                pos.append(self._pedb.edb_value(v))
            else:
                pos.append(v)
        point_data = self._pedb.edb.Geometry.PointData(pos[0], pos[1])
        self._edb_padstackinstance.SetPositionAndRotation(point_data, self._pedb.edb_value(self.rotation))

    @property
    def rotation(self):
        """Padstack instance rotation.

        Returns
        -------
        float
            Rotatation value for the padstack instance.
        """
        point_data = self._pedb.edb.Geometry.PointData(self._pedb.edb_value(0.0), self._pedb.edb_value(0.0))
        out = self._edb_padstackinstance.GetPositionAndRotationValue()

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

    @name.setter
    def name(self, value):
        self._edb_padstackinstance.SetName(value)
        self._edb_padstackinstance.SetProductProperty(self._pedb.edb.ProductId.Designer, 11, value)

    @pyaedt_function_handler()
    def parametrize_position(self, prefix=None):
        """Parametrize the instance position.

        Parameters
        ----------
        prefix : str, optional
            Prefix for the variable name.
            Example `"MyVariableName"` will create 2 Project variables $MyVariableNamesX and $MyVariableNamesY.

        Returns
        -------
        List
            Variables created
        """
        p = self.position
        if not prefix:
            var_name = "${}_pos".format(self.name)
        else:
            var_name = "${}".format(prefix)
        self._pedb.add_design_variable(var_name + "X", p[0])
        self._pedb.add_design_variable(var_name + "Y", p[1])
        self.position = [var_name + "X", var_name + "Y"]
        return [var_name + "X", var_name + "Y"]

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
        return self._edb_padstackinstance.GetGroup().GetPlacementLayer().Clone().GetName()

    @property
    def lower_elevation(self):
        """Lower elevation of the placement layer.

        Returns
        -------
        float
            Lower elavation of the placement layer.
        """
        return self._edb_padstackinstance.GetGroup().GetPlacementLayer().Clone().GetLowerElevation()

    @property
    def upper_elevation(self):
        """Upper elevation of the placement layer.

        Returns
        -------
        float
           Upper elevation of the placement layer.
        """
        return self._edb_padstackinstance.GetGroup().GetPlacementLayer().Clone().GetUpperElevation()

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
        """Solder ball height if available."""
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
    def is_enabled(self):
        """Check if the current object is enabled.

        Returns
        -------
        bool
            ``True`` if current object is enabled, ``False`` otherwise.
        """
        if self.type in ["Resistor", "Capacitor", "Inductor"]:
            return self.component_property.IsEnabled()
        else:  # pragma: no cover
            return False

    @is_enabled.setter
    def is_enabled(self, enabled):
        """Enables the current object."""
        if self.type in ["Resistor", "Capacitor", "Inductor"]:
            component_property = self.component_property
            component_property.SetEnabled(enabled)
            self.edbcomponent.SetComponentProperty(component_property)

    @property
    def res_value(self):
        """Resitance value.

        Returns
        -------
        str
            Resitance Value. ``None`` if not an RLC Type.
        """
        cmp_type = int(self.edbcomponent.GetComponentType())
        if 0 < cmp_type < 4:
            componentProperty = self.edbcomponent.GetComponentProperty()
            model = componentProperty.GetModel().Clone()
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
            model = componentProperty.GetModel().Clone()
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
            model = componentProperty.GetModel().Clone()
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
            model = self.component_property.GetModel().Clone()
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
        return self.edbcomponent.GetPlacementLayer().Clone().GetName()

    @property
    def lower_elevation(self):
        """Lower elevation of the placement layer.

        Returns
        -------
        float
            Lower elevation of the placement layer.
        """
        return self.edbcomponent.GetPlacementLayer().Clone().GetLowerElevation()

    @property
    def upper_elevation(self):
        """Upper elevation of the placement layer.

        Returns
        -------
        float
            Upper elevation of the placement layer.

        """
        return self.edbcomponent.GetPlacementLayer().Clone().GetUpperElevation()

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


class Node(object):
    """Provides for handling nodes for Siwave sources."""

    def __init__(self):
        self._component = None
        self._net = None
        self._node_type = NodeType.Positive
        self._name = ""

    @property
    def component(self):  # pragma: no cover
        """Component name containing the node."""
        return self._component

    @component.setter
    def component(self, value):  # pragma: no cover
        if isinstance(value, str):
            self._component = value

    @property
    def net(self):  # pragma: no cover
        """Net of the node."""
        return self._net

    @net.setter
    def net(self, value):  # pragma: no cover
        if isinstance(value, str):
            self._net = value

    @property
    def node_type(self):  # pragma: no cover
        """Type of the node."""
        return self._node_type

    @node_type.setter
    def node_type(self, value):  # pragma: no cover
        if isinstance(value, int):
            self._node_type = value

    @property
    def name(self):  # pragma: no cover
        """Name of the node."""
        return self._name

    @name.setter
    def name(self, value):  # pragma: no cover
        if isinstance(value, str):
            self._name = value

    def _json_format(self):  # pragma: no cover
        dict_out = {}
        for k, v in self.__dict__.items():
            dict_out[k[1:]] = v
        return dict_out

    def _read_json(self, node_dict):  # pragma: no cover
        for k, v in node_dict.items():
            self.__setattr__(k, v)


class Source(object):
    """Provides for handling Siwave sources."""

    def __init__(self):
        self._name = ""
        self._source_type = SourceType.Vsource
        self._positive_node = Node()
        self._negative_node = Node()
        self._amplitude = 1.0
        self._phase = 0.0
        self._impedance = 1.0
        self._r = 1.0
        self._l = 0.0
        self._c = 0.0
        self._create_physical_resistor = True
        self._config_init()

    def _config_init(self):
        self._positive_node.node_type = int(NodeType.Positive)
        self._positive_node.name = "pos_term"
        self._negative_node.node_type = int(NodeType.Negative)
        self._negative_node.name = "neg_term"

    @property
    def name(self):  # pragma: no cover
        """Source name."""
        return self._name

    @name.setter
    def name(self, value):  # pragma: no cover
        if isinstance(value, str):
            self._name = value

    @property
    def source_type(self):  # pragma: no cover
        """Source type."""
        return self._source_type

    @source_type.setter
    def source_type(self, value):  # pragma: no cover
        if isinstance(value, int):
            self._source_type = value
            if value == 3:
                self._impedance = 1e-6
            if value == 4:
                self._impedance = 5e7
            if value == 5:
                self._r = 1.0
                self._l = 0.0
                self._c = 0.0

    @property
    def positive_node(self):  # pragma: no cover
        """Positive node of the source."""
        return self._positive_node

    @positive_node.setter
    def positive_node(self, value):  # pragma: no cover
        if isinstance(value, Node):
            self._positive_node = value

    @property
    def negative_node(self):  # pragma: no cover
        """Negative node of the source."""
        return self._negative_node

    @negative_node.setter
    def negative_node(self, value):  # pragma: no cover
        if isinstance(value, Node):
            self._negative_node = value
            #

    @property
    def amplitude(self):  # pragma: no cover
        """Amplitude value of the source. Either amperes for current source or volts for
        voltage source."""
        return self._amplitude

    @amplitude.setter
    def amplitude(self, value):  # pragma: no cover
        if isinstance(value, float):
            self._amplitude = value

    @property
    def phase(self):  # pragma: no cover
        """Phase of the source."""
        return self._phase

    @phase.setter
    def phase(self, value):  # pragma: no cover
        if isinstance(value, float):
            self._phase = value

    @property
    def impedance(self):  # pragma: no cover
        """Impedance values of the source."""
        return self._impedance

    @impedance.setter
    def impedance(self, value):  # pragma: no cover
        if isinstance(value, float):
            self._impedance = value

    @property
    def r_value(self):
        return self._r

    @r_value.setter
    def r_value(self, value):
        if isinstance(value, float) or isinstance(value, int):
            self._r = value

    @property
    def l_value(self):
        return self._l

    @l_value.setter
    def l_value(self, value):
        if isinstance(value, float) or isinstance(value, int):
            self._l = value

    @property
    def c_value(self):
        return self._c

    @c_value.setter
    def c_value(self, value):
        if isinstance(value, float) or isinstance(value, int):
            self._c = value

    @property
    def create_physical_resistor(self):
        return self._create_physical_resistor

    @create_physical_resistor.setter
    def create_physical_resistor(self, value):
        if isinstance(value, bool):
            self._create_physical_resistor = value

    def _json_format(self):  # pragma: no cover
        dict_out = {}
        for k, v in self.__dict__.items():
            if k == "_positive_node" or k == "_negative_node":
                nodes = v._json_format()
                dict_out[k[1:]] = nodes
            else:
                dict_out[k[1:]] = v
        return dict_out

    def _read_json(self, source_dict):  # pragma: no cover
        for k, v in source_dict.items():
            if k == "positive_node":
                self.positive_node._read_json(v)
            elif k == "negative_node":
                self.negative_node._read_json(v)
            else:
                self.__setattr__(k, v)


class SimulationConfiguration(object):
    """Parses an ASCII simulation configuration file, which supports all types of inputs
    for setting up and automating any kind of SI or PI simulation with HFSS 3D Layout
    or Siwave. If fields are omitted, default values are applied. This class can be instantiated directly from
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

    def __init__(self, filename=None):
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
        self._enforce_passivity = False
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
        self._output_aedb = None
        self._sources = []
        self._mesh_sizefactor = 0.0
        self._read_cfg()

    @property
    def filename(self):  # pragma: no cover
        """Retrieve the file name loaded for mapping properties value.

        Returns
        -------
        str
            the absolute path for the filename.
        """
        return self._filename

    @filename.setter
    def filename(self, value):
        if isinstance(value, str):  # pragma: no cover
            self._filename = value

    @property
    def generate_solder_balls(self):  # pragma: no cover
        """Retrieve the boolean for applying solder balls.

        Returns
        -------
        bool
            'True' when applied 'False' if not.
        """
        return self._generate_solder_balls

    @generate_solder_balls.setter
    def generate_solder_balls(self, value):
        if isinstance(value, bool):  # pragma: no cover
            self._generate_solder_balls = value

    @property
    def signal_nets(self):
        """Retrieve the list of signal net names.

        Returns
        -------
        list[str]
            List of signal net names.
        """

        return self._signal_nets

    @signal_nets.setter
    def signal_nets(self, value):
        if isinstance(value, list):  # pragma: no cover
            self._signal_nets = value

    @property
    def setup_name(self):
        """Retrieve setup name for the simulation.

        Returns
        -------
        str
            Setup name.
        """
        return self._setup_name

    @setup_name.setter
    def setup_name(self, value):
        if isinstance(value, str):  # pragma: no cover
            self._setup_name = value

    @property
    def power_nets(self):
        """Retrieve the list of power and reference net names.

        Returns
        -------
        list[str]
            List of the net name.
        """
        return self._power_nets

    @power_nets.setter
    def power_nets(self, value):
        if isinstance(value, list):
            self._power_nets = value

    @property
    def components(self):
        """Retrieve the list component name to be included in the simulation.

        Returns
        -------
        list[str]
            List of the component name.
        """
        return self._components

    @components.setter
    def components(self, value):
        if isinstance(value, list):
            self._components = value

    @property
    def coax_solder_ball_diameter(self):  # pragma: no cover
        """Retrieve the list of solder balls diameter values when the auto evaluated one is overwritten.

        Returns
        -------
        list[float]
            List of the solder balls diameter.
        """
        return self._coax_solder_ball_diameter

    @coax_solder_ball_diameter.setter
    def coax_solder_ball_diameter(self, value):  # pragma: no cover
        if isinstance(value, list):
            self._coax_solder_ball_diameter = value

    @property
    def use_default_coax_port_radial_extension(self):
        """Retrieve the boolean for using the default coaxial port extension value.

        Returns
        -------
        bool
            'True' when the default value is used 'False' if not.
        """
        return self._use_default_coax_port_radial_extension

    @use_default_coax_port_radial_extension.setter
    def use_default_coax_port_radial_extension(self, value):  # pragma: no cover
        if isinstance(value, bool):
            self._use_default_coax_port_radial_extension = value

    @property
    def trim_reference_size(self):
        """Retrieve the trim reference size when used.

        Returns
        -------
        float
            The size value.
        """
        return self._trim_reference_size

    @trim_reference_size.setter
    def trim_reference_size(self, value):  # pragma: no cover
        if isinstance(value, bool):
            self._trim_reference_size = value

    @property
    def do_cutout_subdesign(self):
        """Retrieve boolean to perform the cutout during the project build.

        Returns
        -------
            bool
            'True' when clipping the design is applied 'False' is not.
        """
        return self._do_cutout_subdesign

    @do_cutout_subdesign.setter
    def do_cutout_subdesign(self, value):  # pragma: no cover
        if isinstance(value, bool):
            self._do_cutout_subdesign = value

    @property
    def cutout_subdesign_type(self):
        """Retrieve the CutoutSubdesignType selection for clipping the design.

        Returns
        -------
        CutoutSubdesignType object
        """
        return self._cutout_subdesign_type

    @cutout_subdesign_type.setter
    def cutout_subdesign_type(self, value):  # pragma: no cover
        if validate_enum_class_value(CutoutSubdesignType, value):
            self._cutout_subdesign_type = value

    @property
    def cutout_subdesign_expansion(self):
        """Retrieve expansion factor used for clipping the design.

        Returns
        -------
            float
            The value used as a ratio.
        """

        return self._cutout_subdesign_expansion

    @cutout_subdesign_expansion.setter
    def cutout_subdesign_expansion(self, value):  # pragma: no cover
        if isinstance(value, float):
            self._cutout_subdesign_expansion = value

    @property
    def cutout_subdesign_round_corner(self):
        """Retrieve boolean to perform the design clipping using round corner for the extent generation.

        Returns
        -------
            bool
            'True' when using round corner, 'False' if not.
        """

        return self._cutout_subdesign_round_corner

    @cutout_subdesign_round_corner.setter
    def cutout_subdesign_round_corner(self, value):  # pragma: no cover
        if isinstance(value, bool):
            self._cutout_subdesign_round_corner = value

    @property
    def sweep_interpolating(self):  # pragma: no cover
        """Retrieve boolean to add a sweep interpolating sweep.

        Returns
        -------
            bool
            'True' when a sweep interpolating is defined, 'False' when a discrete one is defined instead.
        """

        return self._sweep_interpolating

    @sweep_interpolating.setter
    def sweep_interpolating(self, value):  # pragma: no cover
        if isinstance(value, bool):
            self._sweep_interpolating = value

    @property
    def use_q3d_for_dc(self):  # pragma: no cover
        """Retrieve boolean to Q3D solver for DC point value computation.

        Returns
        -------
            bool
            'True' when Q3D solver is used 'False' when interpolating value is used instead.
        """

        return self._use_q3d_for_dc

    @use_q3d_for_dc.setter
    def use_q3d_for_dc(self, value):  # pragma: no cover
        if isinstance(value, bool):
            self._use_q3d_for_dc = value

    @property
    def relative_error(self):  # pragma: no cover
        """Retrieve relative error used for the interpolating sweep convergence.

        Returns
        -------
            float
            The value of the error interpolating sweep to reach the convergence criteria.
        """

        return self._relative_error

    @relative_error.setter
    def relative_error(self, value):  # pragma: no cover
        if isinstance(value, float):
            self._relative_error = value

    @property
    def use_error_z0(self):  # pragma: no cover
        """Retrieve value for the error on Z0 for the port.

        Returns
        -------
            float
            The Z0 value.
        """

        return self._use_error_z0

    @use_error_z0.setter
    def use_error_z0(self, value):  # pragma: no cover
        if isinstance(value, bool):
            self._use_error_z0 = value

    @property
    def percentage_error_z0(self):  # pragma: no cover
        """Retrieve boolean to perform the cutout during the project build.

        Returns
        -------
            bool
            'True' when clipping the design is applied 'False' if not.
        """

        return self._percentage_error_z0

    @percentage_error_z0.setter
    def percentage_error_z0(self, value):  # pragma: no cover
        if isinstance(value, float):
            self._percentage_error_z0 = value

    @property
    def enforce_causality(self):  # pragma: no cover
        """Retrieve boolean to enforce causality for the frequency sweep.

        Returns
        -------
            bool
            'True' when causality is enforced 'False' if not.
        """

        return self._enforce_causality

    @enforce_causality.setter
    def enforce_causality(self, value):  # pragma: no cover
        if isinstance(value, bool):
            self._enforce_causality = value

    @property
    def enforce_passivity(self):  # pragma: no cover
        """Retrieve boolean to enforce passivity for the frequency sweep.

        Returns
        -------
            bool
            'True' when passivity is enforced 'False' if not.
        """
        return self._enforce_passivity

    @enforce_passivity.setter
    def enforce_passivity(self, value):  # pragma: no cover
        if isinstance(value, bool):
            self._enforce_passivity = value

    @property
    def passivity_tolerance(self):  # pragma: no cover
        """Retrieve the value for the passivity tolerance when used.

        Returns
        -------
            float
            The passivity tolerance criteria for the frequency sweep.
        """
        return self._passivity_tolerance

    @passivity_tolerance.setter
    def passivity_tolerance(self, value):  # pragma: no cover
        if isinstance(value, float):
            self._passivity_tolerance = value

    @property
    def sweep_name(self):  # pragma: no cover
        return self._sweep_name

    @sweep_name.setter
    def sweep_name(self, value):  # pragma: no cover
        """Retrieve frequency sweep name.

        Returns
        -------
            str
            The name of the frequency sweep defined in the project.
        """
        if isinstance(value, str):
            self._sweep_name = value

    @sweep_name.setter
    def sweep_name(self, value):
        if isinstance(value, str):
            self._sweep_name = value

    @property
    def radiation_box(self):  # pragma: no cover
        """Retrieve RadiationBoxType object selection defined for the radiation box type.

        Returns
        -------
            RadiationBoxType object
            3 values can be chosen, Conformal, BoundingBox or ConvexHull.
        """
        return self._radiation_box

    @radiation_box.setter
    def radiation_box(self, value):
        if validate_enum_class_value(RadiationBoxType, value):
            self._radiation_box = value

    @property
    def start_frequency(self):  # pragma: no cover
        """Retrieve starting frequency for the frequency sweep.

        Returns
        -------
            float
            The value of the frequency point.
        """
        return self._start_frequency

    @start_frequency.setter
    def start_frequency(self, value):  # pragma: no cover
        if isinstance(value, str):
            self._start_frequency = value

    @property
    def stop_freq(self):  # pragma: no cover
        """Retrieve stop frequency for the frequency sweep.

        Returns
        -------
            float
            The value of the frequency point.
        """
        return self._stop_freq

    @stop_freq.setter
    def stop_freq(self, value):  # pragma: no cover
        if isinstance(value, str):
            self._stop_freq = value

    @property
    def sweep_type(self):  # pragma: no cover
        """Retrieve SweepType object for the frequency sweep.

        Returns
        -------
            SweepType
            The SweepType object,2 selections are supported Linear and LogCount.
        """
        return self._sweep_type

    @sweep_type.setter
    def sweep_type(self, value):  # pragma: no cover
        if validate_enum_class_value(SweepType, value):
            self._sweep_type = value

    @property
    def step_freq(self):  # pragma: no cover
        """Retrieve step frequency for the frequency sweep.

        Returns
        -------
            float
            The value of the frequency point.
        """
        return self._step_freq

    @step_freq.setter
    def step_freq(self, value):  # pragma: no cover
        if isinstance(value, str):
            self._step_freq = value

    @property
    def decade_count(self):  # pragma: no cover
        """Retrieve decade count number for the frequency sweep in case of a log sweep selected.

        Returns
        -------
            int
            The value of the decade count number.
        """
        return self._decade_count

    @decade_count.setter
    def decade_count(self, value):  # pragma: no cover
        if isinstance(value, int):
            self._decade_count = value

    @property
    def mesh_freq(self):
        """Retrieve the meshing frequency for the HFSS adaptive convergence.

        Returns
        -------
            float
            The value of the frequency point.
        """
        return self._mesh_freq

    @mesh_freq.setter
    def mesh_freq(self, value):  # pragma: no cover
        if isinstance(value, str):
            self._mesh_freq = value

    @property
    def max_num_passes(self):  # pragma: no cover
        """Retrieve maximum of points for the HFSS adaptive meshing.

        Returns
        -------
            int
            The maximum number of adaptive passes value.
        """
        return self._max_num_passes

    @max_num_passes.setter
    def max_num_passes(self, value):  # pragma: no cover
        if isinstance(value, int):
            self._max_num_passes = value

    @property
    def max_mag_delta_s(self):  # pragma: no cover
        """Retrieve the magnitude of the delta S convergence criteria for the interpolating sweep.

        Returns
        -------
            float
            The value of convergence criteria.
        """
        return self._max_mag_delta_s

    @max_mag_delta_s.setter
    def max_mag_delta_s(self, value):  # pragma: no cover
        if isinstance(value, float):
            self._max_mag_delta_s = value

    @property
    def min_num_passes(self):  # pragma: no cover
        """Retrieve the minimum number of adaptive passes for HFSS convergence.

        Returns
        -------
            int
            The value of minimum number of adaptive passes.
        """
        return self._min_num_passes

    @min_num_passes.setter
    def min_num_passes(self, value):  # pragma: no cover
        if isinstance(value, int):
            self._min_num_passes = value

    @property
    def basis_order(self):  # pragma: no cover
        """Retrieve the BasisOrder object.

        Returns
        -------
            BasisOrder class
            This class supports 4 selections Mixed, Zero, single and Double for the HFSS order matrix.
        """
        return self._basis_order

    @basis_order.setter
    def basis_order(self, value):  # pragma: no cover
        if validate_enum_class_value(BasisOrder, value):
            self._basis_order = value

    @property
    def do_lambda_refinement(self):  # pragma: no cover
        """Retrieve boolean to activate the lambda refinement.

        Returns
        -------
            bool
            'True' Enable the lambda meshing refinement with HFSS, 'False' deactivate.
        """
        return self._do_lambda_refinement

    @do_lambda_refinement.setter
    def do_lambda_refinement(self, value):  # pragma: no cover
        if isinstance(value, bool):
            self._do_lambda_refinement = value

    @property
    def arc_angle(self):  # pragma: no cover
        """Retrieve the value for the HFSS meshing arc angle.

        Returns
        -------
            float
            Value of the arc angle.
        """
        return self._arc_angle

    @arc_angle.setter
    def arc_angle(self, value):  # pragma: no cover
        if isinstance(value, str):
            self._arc_angle = value

    @property
    def start_azimuth(self):  # pragma: no cover
        """Retrieve the value of the starting azimuth for the HFSS meshing.

        Returns
        -------
            float
            Value of the starting azimuth.
        """
        return self._start_azimuth

    @start_azimuth.setter
    def start_azimuth(self, value):  # pragma: no cover
        if isinstance(value, float):
            self._start_azimuth = value

    @property
    def max_arc_points(self):  # pragma: no cover
        """Retrieve the value of the maximum arc points number for the HFSS meshing.

        Returns
        -------
            int
            Value of the maximum arc point number.
        """
        return self._max_arc_points

    @max_arc_points.setter
    def max_arc_points(self, value):  # pragma: no cover
        if isinstance(value, int):
            self._max_arc_points = value

    @property
    def use_arc_to_chord_error(self):  # pragma: no cover
        """Retrieve the boolean for activating the arc to chord for HFSS meshing.

        Returns
        -------
            bool
            Activate when 'True', deactivated when 'False'.
        """
        return self._use_arc_to_chord_error

    @use_arc_to_chord_error.setter
    def use_arc_to_chord_error(self, value):  # pragma: no cover
        if isinstance(value, bool):
            self._use_arc_to_chord_error = value

    @property
    def arc_to_chord_error(self):  # pragma: no cover
        """Retrieve the value of arc to chord error for HFSS meshing.

        Returns
        -------
            flot
            Value of the arc to chord error.
        """
        return self._arc_to_chord_error

    @arc_to_chord_error.setter
    def arc_to_chord_error(self, value):  # pragma: no cover
        if isinstance(value, str):
            self._arc_to_chord_error = value

    @property
    def defeature_abs_length(self):  # pragma: no cover
        """Retrieve the value of arc to chord for HFSS meshing.

        Returns
        -------
            flot
            Value of the arc to chord error.
        """
        return self._defeature_abs_length

    @defeature_abs_length.setter
    def defeature_abs_length(self, value):  # pragma: no cover
        if isinstance(value, str):
            self._defeature_abs_length = value

    @property
    def defeature_layout(self):  # pragma: no cover
        """Retrieve the boolean to activate the layout defeaturing.This method has been developed to simplify polygons
        with reducing the number of points to simplify the meshing with controlling its surface deviation. This method
        should be used at last resort when other methods failed.

        Returns
        -------
            bool
            'True' when activated 'False when deactivated.
        """
        return self._defeature_layout

    @defeature_layout.setter
    def defeature_layout(self, value):  # pragma: no cover
        if isinstance(value, bool):
            self._defeature_layout = value

    @property
    def minimum_void_surface(self):  # pragma: no cover
        """Retrieve the minimum void surface to be considered for the layout defeaturing.
        Voids below this value will be ignored.

        Returns
        -------
            flot
            Value of the minimum surface.
        """
        return self._minimum_void_surface

    @minimum_void_surface.setter
    def minimum_void_surface(self, value):  # pragma: no cover
        if isinstance(value, float):
            self._minimum_void_surface = value

    @property
    def max_suf_dev(self):  # pragma: no cover
        """Retrieve the value for the maximum surface deviation for the layout defeaturing.

        Returns
        -------
            flot
            Value of maximum surface deviation.
        """
        return self._max_suf_dev

    @max_suf_dev.setter
    def max_suf_dev(self, value):  # pragma: no cover
        if isinstance(value, float):
            self._max_suf_dev = value

    @property
    def process_padstack_definitions(self):  # pragma: no cover
        """Retrieve the boolean for activating the padstack definition processing.

        Returns
        -------
            flot
            Value of the arc to chord error.
        """
        return self._process_padstack_definitions

    @process_padstack_definitions.setter
    def process_padstack_definitions(self, value):  # pragma: no cover
        if isinstance(value, bool):
            self._process_padstack_definitions = value

    @property
    def return_current_distribution(self):  # pragma: no cover
        """Boolean to activate the current distribution return with Siwave.

        Returns
        -------
            flot
            Value of the arc to chord error.
        """
        return self._return_current_distribution

    @return_current_distribution.setter
    def return_current_distribution(self, value):  # pragma: no cover
        if isinstance(value, bool):
            self._return_current_distribution = value

    @property
    def ignore_non_functional_pads(self):  # pragma: no cover
        """Boolean to ignore nonfunctional pads with Siwave.

        Returns
         -------
            flot
            Value of the arc to chord error.
        """
        return self._ignore_non_functional_pads

    @ignore_non_functional_pads.setter
    def ignore_non_functional_pads(self, value):  # pragma: no cover
        if isinstance(value, bool):
            self._ignore_non_functional_pads = value

    @property
    def include_inter_plane_coupling(self):  # pragma: no cover
        """Boolean to activate the inter-plane coupling with Siwave.

        Returns
        -------
            bool
            'True' activated 'False' deactivated.
        """
        return self._include_inter_plane_coupling

    @include_inter_plane_coupling.setter
    def include_inter_plane_coupling(self, value):  # pragma: no cover
        if isinstance(value, bool):
            self._include_inter_plane_coupling = value

    @property
    def xtalk_threshold(self):  # pragma: no cover
        """Return the value for Siwave cross talk threshold. THis value specifies the distance for the solver to
        consider lines coupled during the cross-section computation. Decreasing the value below -60dB can
        potentially cause solver failure.

        Returns
        -------
            flot
            Value of cross-talk threshold.
        """
        return self._xtalk_threshold

    @xtalk_threshold.setter
    def xtalk_threshold(self, value):  # pragma: no cover
        if isinstance(value, float):
            self._xtalk_threshold = value

    @property
    def min_void_area(self):  # pragma: no cover
        """Retrieve the value of minimum void area to be considered by Siwave.

        Returns
        -------
            flot
            Value of the arc to chord error.
        """
        return self._min_void_area

    @min_void_area.setter
    def min_void_area(self, value):  # pragma: no cover
        if isinstance(value, str):
            self._min_void_area = value

    @property
    def min_pad_area_to_mesh(self):  # pragma: no cover
        """Retrieve the value of minimum pad area to be meshed by Siwave.

        Returns
        -------
            flot
            Value of minimum pad surface.
        """
        return self._min_pad_area_to_mesh

    @min_pad_area_to_mesh.setter
    def min_pad_area_to_mesh(self, value):  # pragma: no cover
        if isinstance(value, str):
            self._min_pad_area_to_mesh = value

    @property
    def snap_length_threshold(self):  # pragma: no cover
        """Retrieve the boolean to activate the snapping threshold feature.

        Returns
        -------
            bool
            'True' activate 'False' deactivated.
        """
        return self._snap_length_threshold

    @snap_length_threshold.setter
    def snap_length_threshold(self, value):  # pragma: no cover
        if isinstance(value, str):
            self._snap_length_threshold = value

    @property
    def min_plane_area_to_mesh(self):  # pragma: no cover
        """Retrieve the minimum plane area to be meshed by Siwave.

        Returns
        -------
            flot
            Value of the minimum plane area.
        """
        return self._min_plane_area_to_mesh

    @min_plane_area_to_mesh.setter
    def min_plane_area_to_mesh(self, value):  # pragma: no cover
        if isinstance(value, str):
            self._min_plane_area_to_mesh = value

    @property
    def dc_min_plane_area_to_mesh(self):  # pragma: no cover
        """Retrieve the value of the minimum plane area to be meshed by Siwave for DC solution.

        Returns
        -------
            float
            The value of the minimum plane area.
        """
        return self._dc_min_plane_area_to_mesh

    @dc_min_plane_area_to_mesh.setter
    def dc_min_plane_area_to_mesh(self, value):  # pragma: no cover
        if isinstance(value, str):
            self._dc_min_plane_area_to_mesh = value

    @property
    def max_init_mesh_edge_length(self):  # pragma: no cover
        """Retrieve the value of the maximum initial mesh edges for Siwave.

        Returns
        -------
            float
            Value of the maximum initial mesh edge length.
        """
        return self._max_init_mesh_edge_length

    @max_init_mesh_edge_length.setter
    def max_init_mesh_edge_length(self, value):  # pragma: no cover
        if isinstance(value, str):
            self._max_init_mesh_edge_length = value

    @property
    def signal_layers_properties(self):  # pragma: no cover
        """Retrieve the list of layers to have properties changes.

        Returns
        -------
            list[str]
            List of layer name.
        """
        return self._signal_layers_properties

    @signal_layers_properties.setter
    def signal_layers_properties(self, value):  # pragma: no cover
        if isinstance(value, dict):
            self._signal_layers_properties = value

    @property
    def coplanar_instances(self):  # pragma: no cover
        """Retrieve the list of component to be replaced by circuit ports (obsolete).

        Returns
        -------
            list[str]
            List of component name.
        """
        return self._coplanar_instances

    @coplanar_instances.setter
    def coplanar_instances(self, value):  # pragma: no cover
        if isinstance(value, list):
            self._coplanar_instances = value

    @property
    def signal_layer_etching_instances(self):  # pragma: no cover
        """Retrieve the list of layers which has layer etching activated.

        Returns
        -------
            list[str]
            List of layer name.
        """
        return self._signal_layer_etching_instances

    @signal_layer_etching_instances.setter
    def signal_layer_etching_instances(self, value):  # pragma: no cover
        if isinstance(value, list):
            self._signal_layer_etching_instances = value

    @property
    def etching_factor_instances(self):  # pragma: no cover
        """Retrieve the list of etching factor with associated layers.

        Returns
        -------
            list[str]
            list etching parameters with layer name.
        """
        return self._etching_factor_instances

    @etching_factor_instances.setter
    def etching_factor_instances(self, value):  # pragma: no cover
        if isinstance(value, list):
            self._etching_factor_instances = value

    @property
    def dielectric_extent(self):  # pragma: no cover
        """Retrieve the value of dielectric extent.

        Returns
        -------
            float
            Value of the dielectric extent.
        """
        return self._dielectric_extent

    @dielectric_extent.setter
    def dielectric_extent(self, value):  # pragma: no cover
        if isinstance(value, float):
            self._dielectric_extent = value

    @property
    def airbox_horizontal_extent(self):  # pragma: no cover
        """Retrieve the air box horizontal extent size for HFSS.

        Returns
        -------
            float
            Value of the air box horizontal extent.
        """
        return self._airbox_horizontal_extent

    @airbox_horizontal_extent.setter
    def airbox_horizontal_extent(self, value):  # pragma: no cover
        if isinstance(value, float):
            self._airbox_horizontal_extent = value

    @property
    def airbox_negative_vertical_extent(self):  # pragma: no cover
        """Retrieve the air box negative vertical extent size for HFSS.

        Returns
        -------
            float
            Value of the air box negative vertical extent.
        """
        return self._airbox_negative_vertical_extent

    @airbox_negative_vertical_extent.setter
    def airbox_negative_vertical_extent(self, value):  # pragma: no cover
        if isinstance(value, float):
            self._airbox_negative_vertical_extent = value

    @property
    def airbox_positive_vertical_extent(self):  # pragma: no cover
        """Retrieve the air box positive vertical extent size for HFSS.

        Returns
        -------
            float
            Value of the air box positive vertical extent.
        """
        return self._airbox_positive_vertical_extent

    @airbox_positive_vertical_extent.setter
    def airbox_positive_vertical_extent(self, value):  # pragma: no cover
        if isinstance(value, float):
            self._airbox_positive_vertical_extent = value

    @property
    def honor_user_dielectric(self):  # pragma: no cover
        """Retrieve the boolean to activate the feature "'Honor user dielectric'".

        Returns
        -------
            bool
            "'True'" activated, "'False'" deactivated.
        """
        return self._honor_user_dielectric

    @honor_user_dielectric.setter
    def honor_user_dielectric(self, value):  # pragma: no cover
        if isinstance(value, bool):
            self._honor_user_dielectric = value

    @property
    def truncate_airbox_at_ground(self):  # pragma: no cover
        """Retrieve the boolean to truncate hfss air box at ground.

        Returns
        -------
            bool
            "'True'" activated, "'False'" deactivated.
        """
        return self._truncate_airbox_at_ground

    @truncate_airbox_at_ground.setter
    def truncate_airbox_at_ground(self, value):  # pragma: no cover
        if isinstance(value, bool):
            self._truncate_airbox_at_ground = value

    @property
    def solver_type(self):  # pragma: no cover
        """Retrieve the SolverType class to select the solver to be called during the project build.

        Returns
        -------
            SolverType
            selections are supported, Hfss3dLayout and Siwave.
        """
        return self._solver_type

    @solver_type.setter
    def solver_type(self, value):  # pragma: no cover
        if isinstance(value, int):
            self._solver_type = value

    @property
    def use_radiation_boundary(self):  # pragma: no cover
        """Retrieve the boolean to use radiation boundary with HFSS.

        Returns
        -------
            bool
            "'True'" activated, "'False'" deactivated.
        """
        return self._use_radiation_boundary

    @use_radiation_boundary.setter
    def use_radiation_boundary(self, value):  # pragma: no cover
        if isinstance(value, bool):
            self._use_radiation_boundary = value

    @property
    def output_aedb(self):  # pragma: no cover
        """Retrieve the path for the output aedb folder. When provided will copy the initial aedb to the specified
        path. This is used especially to preserve the initial project when several files have to be build based on
        the last one. When the path is None, the initial project will be overwritten. So when cutout is applied mand
        you want to preserve the project make sure you provide the full path for the new aedb folder.

        Returns
        -------
            str
            Absolute path for the created aedb folder.
        """
        return self._output_aedb

    @output_aedb.setter
    def output_aedb(self, value):  # pragma: no cover
        if isinstance(value, str):
            self._output_aedb = value

    @property
    def mesh_sizefactor(self):
        return self._mesh_sizefactor

    @mesh_sizefactor.setter
    def mesh_sizefactor(self, value):
        if isinstance(value, float):
            self._mesh_sizefactor = value
            if value > 0.0:
                self._do_lambda_refinement = False

    @property
    def sources(self):  # pragma: no cover
        return self._sources

    @sources.setter
    def sources(self, value):  # pragma: no cover
        if isinstance(value, Source):
            value = [value]
        if isinstance(value, list):
            if len([src for src in value if isinstance(src, Source)]) == len(value):
                self._sources = value

    def add_source(self, source=None):  # pragma: no cover
        if isinstance(source, Source):
            self._sources.append(source)

    def _get_bool_value(self, value):  # pragma: no cover
        val = value.lower()
        if val in ("y", "yes", "t", "true", "on", "1"):
            return True
        elif val in ("n", "no", "f", "false", "off", "0"):
            return False
        else:
            raise ValueError("Invalid truth value %r" % (val,))

    def _get_list_value(self, value):  # pragma: no cover
        value = value[1:-1]
        if len(value) == 0:
            return []
        else:
            value = value.split(",")
            if isinstance(value, list):
                prop_values = [i.strip() for i in value]
            else:
                prop_values = [value.strip()]
            return prop_values

    def _parse_signal_layer_properties(self, signal_properties):  # pragma: no cover
        for lay in signal_properties:
            lp = lay.split(":")
            try:
                self.signal_layers_properties.update({lp[0]: [lp[1], lp[2], lp[3], lp[4], lp[5]]})
            except:
                print("Missing parameter for layer {0}".format(lp[0]))

    def _read_cfg(self):  # pragma: no cover
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

        if not self.filename or not os.path.exists(self.filename):
            # raise Exception("{} does not exist.".format(self.filename))
            return

        try:
            with open(self.filename) as cfg_file:
                cfg_lines = cfg_file.read().split("\n")
                for line in cfg_lines:
                    if line.strip() != "":
                        if line.find("="):
                            i, prop_value = line.strip().split("=")
                            value = prop_value.replace("'", "").strip()
                            if i.lower().startswith("generatesolderballs"):
                                self.generate_solder_balls = self._get_bool_value(value)
                            elif i.lower().startswith("signalnets"):
                                self.signal_nets = value[1:-1].split(",") if value[0] == "[" else value.split(",")
                                self.signal_nets = [item.strip() for item in self.signal_nets]
                            elif i.lower().startswith("powernets"):
                                self.power_nets = value[1:-1].split(",") if value[0] == "[" else value.split(",")
                                self.power_nets = [item.strip() for item in self.power_nets]
                            elif i.lower().startswith("components"):
                                self.components = value[1:-1].split(",") if value[0] == "[" else value.split(",")
                                self.components = [item.strip() for item in self.components]
                            elif i.lower().startswith("coaxsolderballsdiams"):
                                self.coax_solder_ball_diameter = (
                                    value[1:-1].split(",") if value[0] == "[" else value.split(",")
                                )
                                self.coax_solder_ball_diameter = [
                                    item.strip() for item in self.coax_solder_ball_diameter
                                ]
                            elif i.lower().startswith("usedefaultcoaxportradialextentfactor"):
                                self.signal_nets = self._get_bool_value(value)
                            elif i.lower().startswith("trimrefsize"):
                                self.trim_reference_size = self._get_bool_value(value)
                            elif i.lower().startswith("cutoutsubdesigntype"):
                                if value.lower().startswith("conformal"):
                                    self.cutout_subdesign_type = CutoutSubdesignType.Conformal
                                elif value.lower().startswith("boundingbox"):
                                    self.cutout_subdesign_type = CutoutSubdesignType.BoundingBox
                                else:
                                    print("Unprocessed value for CutoutSubdesignType '{0}'".format(value))
                            elif i.lower().startswith("cutoutsubdesignexpansion"):
                                self.cutout_subdesign_expansion = float(value)
                            elif i.lower().startswith("cutoutsubdesignroundcorners"):
                                self.cutout_subdesign_round_corner = self._get_bool_value(value)
                            elif i.lower().startswith("sweepinterpolating"):
                                self.sweep_interpolating = self._get_bool_value(value)
                            elif i.lower().startswith("useq3dfordc"):
                                self.use_q3d_for_dc = self._get_bool_value(value)
                            elif i.lower().startswith("relativeerrors"):
                                self.relative_error = float(value)
                            elif i.lower().startswith("useerrorz0"):
                                self.use_error_z0 = self._get_bool_value(value)
                            elif i.lower().startswith("percenterrorz0"):
                                self.percentage_error_z0 = float(value)
                            elif i.lower().startswith("enforcecausality"):
                                self.enforce_causality = self._get_bool_value(value)
                            elif i.lower().startswith("enforcepassivity"):
                                self.enforce_passivity = self._get_bool_value(value)
                            elif i.lower().startswith("passivitytolerance"):
                                self.passivity_tolerance = float(value)
                            elif i.lower().startswith("sweepname"):
                                self.sweep_name = value
                            elif i.lower().startswith("radiationbox"):
                                if value.lower().startswith("conformal"):
                                    self.radiation_box = RadiationBoxType.Conformal
                                elif value.lower().startswith("boundingbox"):
                                    self.radiation_box = RadiationBoxType.BoundingBox
                                elif value.lower().startswith("convexhull"):
                                    self.radiation_box = RadiationBoxType.ConvexHull
                                else:
                                    print("Unprocessed value for RadiationBox '{0}'".format(value))
                            elif i.lower().startswith("startfreq"):
                                self.start_frequency = value
                            elif i.lower().startswith("stopfreq"):
                                self.stop_freq = value
                            elif i.lower().startswith("sweeptype"):
                                if value.lower().startswith("linear"):
                                    self.sweep_type = SweepType.Linear
                                elif value.lower().startswith("logcount"):
                                    self.sweep_type = SweepType.LogCount
                                else:
                                    print("Unprocessed value for SweepType '{0}'".format(value))
                            elif i.lower().startswith("stepfreq"):
                                self.step_freq = value
                            elif i.lower().startswith("decadecount"):
                                self.decade_count = int(value)
                            elif i.lower().startswith("mesh_freq"):
                                self.mesh_freq = value
                            elif i.lower().startswith("maxnumpasses"):
                                self.max_num_passes = int(value)
                            elif i.lower().startswith("maxmagdeltas"):
                                self.max_mag_delta_s = float(value)
                            elif i.lower().startswith("minnumpasses"):
                                self.min_num_passes = int(value)
                            elif i.lower().startswith("basisorder"):
                                if value.lower().startswith("mixed"):
                                    self.basis_order = BasisOrder.Mixed
                                elif value.lower().startswith("zero"):
                                    self.basis_order = BasisOrder.Zero
                                elif value.lower().startswith("first"):  # single
                                    self.basis_order = BasisOrder.Single
                                elif value.lower().startswith("second"):  # double
                                    self.basis_order = BasisOrder.Double
                                else:
                                    print("Unprocessed value for BasisOrder '{0}'".format(value))
                            elif i.lower().startswith("dolambdarefinement"):
                                self.do_lambda_refinement = self._get_bool_value(value)
                            elif i.lower().startswith("arcangle"):
                                self.arc_angle = value
                            elif i.lower().startswith("startazimuth"):
                                self.start_azimuth = float(value)
                            elif i.lower().startswith("maxarcpoints"):
                                self.max_arc_points = int(value)
                            elif i.lower().startswith("usearctochorderror"):
                                self.use_arc_to_chord_error = self._get_bool_value(value)
                            elif i.lower().startswith("arctochorderror"):
                                self.arc_to_chord_error = value
                            elif i.lower().startswith("defeatureabsLength"):
                                self.defeature_abs_length = value
                            elif i.lower().startswith("defeaturelayout"):
                                self.defeature_layout = self._get_bool_value(value)
                            elif i.lower().startswith("minimumvoidsurface"):
                                self.minimum_void_surface = float(value)
                            elif i.lower().startswith("maxsurfdev"):
                                self.max_suf_dev = float(value)
                            elif i.lower().startswith("processpadstackdefinitions"):
                                self.process_padstack_definitions = self._get_bool_value(value)
                            elif i.lower().startswith("returncurrentdistribution"):
                                self.return_current_distribution = self._get_bool_value(value)
                            elif i.lower().startswith("ignorenonfunctionalpads"):
                                self.ignore_non_functional_pads = self._get_bool_value(value)
                            elif i.lower().startswith("includeinterplanecoupling"):
                                self.include_inter_plane_coupling = self._get_bool_value(value)
                            elif i.lower().startswith("xtalkthreshold"):
                                self.xtalk_threshold = float(value)
                            elif i.lower().startswith("minvoidarea"):
                                self.min_void_area = value
                            elif i.lower().startswith("minpadareatomesh"):
                                self.min_pad_area_to_mesh = value
                            elif i.lower().startswith("snaplengththreshold"):
                                self.snap_length_threshold = value
                            elif i.lower().startswith("minplaneareatomesh"):
                                self.min_plane_area_to_mesh = value
                            elif i.lower().startswith("dcminplaneareatomesh"):
                                self.dc_min_plane_area_to_mesh = value
                            elif i.lower().startswith("maxinitmeshedgelength"):
                                self.max_init_mesh_edge_length = value
                            elif i.lower().startswith("signallayersproperties"):
                                self._parse_signal_layer_properties = value[1:-1] if value[0] == "[" else value
                                self._parse_signal_layer_properties = [
                                    item.strip() for item in self._parse_signal_layer_properties
                                ]
                            elif i.lower().startswith("coplanar_instances"):
                                self.coplanar_instances = value[1:-1] if value[0] == "[" else value
                                self.coplanar_instances = [item.strip() for item in self.coplanar_instances]
                            elif i.lower().startswith("signallayersetching"):
                                self.signal_layer_etching_instances = value[1:-1] if value[0] == "[" else value
                                self.signal_layer_etching_instances = [
                                    item.strip() for item in self.signal_layer_etching_instances
                                ]
                            elif i.lower().startswith("etchingfactor"):
                                self.etching_factor_instances = value[1:-1] if value[0] == "[" else value
                                self.etching_factor_instances = [item.strip() for item in self.etching_factor_instances]
                            elif i.lower().startswith("docutoutsubdesign"):
                                self.do_cutout_subdesign = self._get_bool_value(value)
                            elif i.lower().startswith("solvertype"):
                                if value.lower() == "hfss":
                                    self.solver_type = 0
                                if value.lower() == "hfss3dlayout":
                                    self.solver_type = 6
                                elif value.lower().startswith("siwavesyz"):
                                    self.solver_type = 6
                                elif value.lower().startswith("siwavedc"):
                                    self.solver_type = 8
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

    def export_json(self, output_file):
        """Export Json file from SimulationConfiguration object.

        Parameters
        ----------
        output_file : str
            Json file name.

        Returns
        -------
        bool
            True when succeeded False when file name not provided.

        Examples
        --------

        >>> from pyaedt.edb_core.EDB_Data import SimulationConfiguration
        >>> config = SimulationConfiguration()
        >>> config.export_json(r"C:\Temp\test_json\test.json")
        """
        dict_out = {}
        for k, v in self.__dict__.items():
            if k[0] == "_":
                if k == "_sources":
                    sources_out = [src._json_format() for src in v]
                    dict_out[k[1:]] = sources_out
                else:
                    dict_out[k[1:]] = v
            else:
                dict_out[k] = v
        if output_file:
            with open(output_file, "w") as write_file:
                json.dump(dict_out, write_file, indent=4)
            return True
        else:
            return False

    def import_json(self, input_file):
        """Import Json file into SimulationConfiguration object instance.

        Parameters
        ----------
        input_file : str
            Json file name.

        Returns
        -------
        bool
            True when succeeded False when file name not provided.

        Examples
        --------
        >>> from pyaedt.edb_core.EDB_Data import SimulationConfiguration
        >>> test = SimulationConfiguration()
        >>> test.import_json(r"C:\Temp\test_json\test.json")
        """
        if input_file:
            f = open(input_file)
            json_dict = json.load(f)  # pragma: no cover
            for k, v in json_dict.items():
                if k == "sources":
                    for src in json_dict[k]:  # pragma: no cover
                        source = Source()
                        source._read_json(src)
                        self.sources.append(source)
                self.__setattr__(k, v)
            self.filename = input_file
            return True
        else:
            return False

    def add_voltage_source(
        self,
        name="",
        voltage_value=1,
        phase_value=0,
        impedance=1e-6,
        positive_node_component="",
        positive_node_net="",
        negative_node_component="",
        negative_node_net="",
    ):
        """Add a voltage source for the current SimulationConfiguration instance.

        Parameters
        ----------
        name : str
            Source name.

        voltage_value : float
            Amplitude value of the source. Either amperes for current source or volts for
            voltage source.

        phase_value : float
            Phase value of the source.

        impedance : float
            Impedance value of the source.

        positive_node_component : str
            Name of the component used for the positive node.

        negative_node_component : str
            Name of the component used for the negative node.

        positive_node_net : str
            Net used for the positive node.

        negative_node_net : str
            Net used for the negative node.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.

        Examples
        --------
        >>> edb = Edb(target_file)
        >>> sim_setup = SimulationConfiguration()
        >>> sim_setup.add_voltage_source(voltage_value=1.0, phase_value=0, positive_node_component="V1",
        >>> positive_node_net="HSG", negative_node_component="V1", negative_node_net="SW")

        """
        if name == "":  # pragma: no cover
            name = generate_unique_name("v_source")
        source = Source()
        source.source_type = SourceType.Vsource
        source.name = name
        source.amplitude = voltage_value
        source.phase = phase_value
        source.positive_node.component = positive_node_component
        source.positive_node.net = positive_node_net
        source.negative_node.component = negative_node_component
        source.negative_node.net = negative_node_net
        source.impedance_value = impedance
        try:  # pragma: no cover
            self.sources.append(source)
            return True
        except:  # pragma: no cover
            return False

    def add_current_source(
        self,
        name="",
        current_value=0.1,
        phase_value=0,
        impedance=5e7,
        positive_node_component="",
        positive_node_net="",
        negative_node_component="",
        negative_node_net="",
    ):
        """Add a current source for the current SimulationConfiguration instance.

        Parameters
        ----------
        name : str
            Source name.

        current_value : float
            Amplitude value of the source. Either amperes for current source or volts for
            voltage source.

        phase_value : float
            Phase value of the source.

        impedance : float
            Impedance value of the source.

        positive_node_component : str
            Name of the component used for the positive node.

        negative_node_component : str
            Name of the component used for the negative node.

        positive_node_net : str
            Net used for the positive node.

        negative_node_net : str
            Net used for the negative node.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.

        Examples
        --------
        >>> edb = Edb(target_file)
        >>> sim_setup = SimulationConfiguration()
        >>> sim_setup.add_voltage_source(voltage_value=1.0, phase_value=0, positive_node_component="V1",
        >>> positive_node_net="HSG", negative_node_component="V1", negative_node_net="SW")
        """

        if name == "":  # pragma: no cover
            name = generate_unique_name("I_source")
        source = Source()
        source.source_type = SourceType.Isource
        source.name = name
        source.amplitude = current_value
        source.phase = phase_value
        source.positive_node.component = positive_node_component
        source.positive_node.net = positive_node_net
        source.negative_node.component = negative_node_component
        source.negative_node.net = negative_node_net
        source.impedance_value = impedance
        try:  # pragma: no cover
            self.sources.append(source)
            return True
        except:  # pragma: no cover
            return False

    def add_rlc(
        self,
        name="",
        r_value=1.0,
        c_value=0.0,
        l_value=0.0,
        positive_node_component="",
        positive_node_net="",
        negative_node_component="",
        negative_node_net="",
        create_physical_rlc=True,
    ):
        """Add a voltage source for the current SimulationConfiguration instance.

        Parameters
        ----------
        name : str
            Source name.

        r_value : float
            Resistor value in Ohms.

        l_value : float
            Inductance value in Henry.

        c_value : float
            Capacitance value in Farrad.

        positive_node_component : str
            Name of the component used for the positive node.

        negative_node_component : str
            Name of the component used for the negative node.

        positive_node_net : str
            Net used for the positive node.

        negative_node_net : str
            Net used for the negative node.

        create_physical_rlc : bool
            When True create a physical Rlc component. Recommended setting to True to be compatible with Siwave.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.

        Examples
        --------
        >>> edb = Edb(target_file)
        >>> sim_setup = SimulationConfiguration()
        >>> sim_setup.add_voltage_source(voltage_value=1.0, phase_value=0, positive_node_component="V1",
        >>> positive_node_net="HSG", negative_node_component="V1", negative_node_net="SW")
        """

        if name == "":  # pragma: no cover
            name = generate_unique_name("Rlc")
        source = Source()
        source.source_type = SourceType.Rlc
        source.name = name
        source.r_value = r_value
        source.l_value = l_value
        source.c_value = c_value
        source.create_physical_resistor = create_physical_rlc
        source.positive_node.component = positive_node_component
        source.positive_node.net = positive_node_net
        source.negative_node.component = negative_node_component
        source.negative_node.net = negative_node_net
        try:  # pragma: no cover
            self.sources.append(source)
            return True
        except:  # pragma: no cover
            return False


class EDBStatistics(object):
    """Statistics object

    Object properties example.
    >>> stat_model = EDBStatistics()
    >>> stat_model.num_capacitors
    >>> stat_model.num_resistors
    >>> stat_model.num_inductors
    >>> stat_model.layout_size
    >>> stat_model.num_discrete_components
    >>> stat_model.num_inductors
    >>> stat_model.num_resistors
    >>> stat_model.num_capacitors
    >>> stat_model.num_nets
    >>> stat_model.num_traces
    >>> stat_model.num_polygons
    >>> stat_model.num_vias
    >>> stat_model.stackup_thickness
    >>> stat_model.occupying_surface
    >>> stat_model.occupying_ratio
    """

    def __init__(self):
        self._nb_layer = 0
        self._stackup_thickness = 0.0
        self._nb_vias = 0
        self._occupying_ratio = 0.0
        self._occupying_surface = 0.0
        self._layout_size = [0.0, 0.0, 0.0, 0.0]
        self._nb_polygons = 0
        self._nb_traces = 0
        self._nb_nets = 0
        self._nb_discrete_components = 0
        self._nb_inductors = 0
        self._nb_capacitors = 0
        self._nb_resistors = 0

    @property
    def num_layers(self):
        return self._nb_layer

    @num_layers.setter
    def num_layers(self, value):
        if isinstance(value, int):
            self._nb_layer = value

    @property
    def stackup_thickness(self):
        return self._stackup_thickness

    @stackup_thickness.setter
    def stackup_thickness(self, value):
        if isinstance(value, float):
            self._stackup_thickness = value

    @property
    def num_vias(self):
        return self._nb_vias

    @num_vias.setter
    def num_vias(self, value):
        if isinstance(value, int):
            self._nb_vias = value

    @property
    def occupying_ratio(self):
        return self._occupying_ratio

    @occupying_ratio.setter
    def occupying_ratio(self, value):
        if isinstance(value, float):
            self._occupying_ratio = value

    @property
    def occupying_surface(self):
        return self._occupying_surface

    @occupying_surface.setter
    def occupying_surface(self, value):
        if isinstance(value, float):
            self._occupying_surface = value

    @property
    def layout_size(self):
        return self._layout_size

    @layout_size.setter
    def layout_size(self, value):
        if isinstance(value, list):
            if len([pt for pt in value if isinstance(pt, float)]) == len(value):
                self._layout_size = value

    @property
    def num_polygons(self):
        return self._nb_polygons

    @num_polygons.setter
    def num_polygons(self, value):
        if isinstance(value, int):
            self._nb_polygons = value

    @property
    def num_traces(self):
        return self._nb_traces

    @num_traces.setter
    def num_traces(self, value):
        if isinstance(value, int):
            self._nb_traces = value

    @property
    def num_nets(self):
        return self._nb_nets

    @num_nets.setter
    def num_nets(self, value):
        if isinstance(value, int):
            self._nb_nets = value

    @property
    def num_discrete_components(self):
        return self._nb_discrete_components

    @num_discrete_components.setter
    def num_discrete_components(self, value):
        if isinstance(value, int):
            self._nb_discrete_components = value

    @property
    def num_inductors(self):
        return self._nb_inductors

    @num_inductors.setter
    def num_inductors(self, value):
        if isinstance(value, int):
            self._nb_inductors = value

    @property
    def num_capacitors(self):
        return self._nb_capacitors

    @num_capacitors.setter
    def num_capacitors(self, value):
        if isinstance(value, int):
            self._nb_capacitors = value

    @property
    def num_resistors(self):
        return self._nb_resistors

    @num_resistors.setter
    def num_resistors(self, value):
        if isinstance(value, int):
            self._nb_resistors = value
