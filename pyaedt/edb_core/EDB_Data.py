import math
import os
import time
import warnings
from collections import OrderedDict

from pyaedt.edb_core.general import convert_py_list_to_net_list
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
    def plot(self, layers=None, show_legend=True, save_plot=None, outline=None, size=(2000, 1000)):
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
            self.name, layers=layers, show_legend=show_legend, save_plot=save_plot, outline=outline, size=size
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
    def plot(self, nets=None, show_legend=True, save_plot=None, outline=None, size=(2000, 1000)):
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
    def update_layer_vals(self, layerName, newLayer, etchMap, materialMap, fillMaterialMap, thicknessMap, layerTypeMap):
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
        return sorted(allStackuplayers, key=lambda lyr=self._edb.Cell.StackupLayer: lyr.GetLowerElevation())

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
                    layerName, newLayer, etchMap, material, fillMaterial, thickness, self._int_to_layer_types(layerType)
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
        self, layer_name=None, pad_type=None, geom_type=None, params=None, offsetx=None, offsety=None, rotation=None
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
    def create_rectangle_in_pad(self, layer_name):
        """Create a rectangle inscribed inside a padstack instance pad. The rectangle is fully inscribed in the
        pad and has the maximum area. It is necessary to specify the layer on which the rectangle will be created.

        Parameters
        ----------
        layer_name : str
            Name of the layer on which to create the polygon.

        Returns
        -------
        bool, :class:`pyaedt.edb_core.EDB_Data.EDBPrimitives`
            Polygon when successful, ``False`` when failed.

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
        padstack_name = self.padstack_definition
        try:
            padstack = self._pedb.core_padstack.padstacks[padstack_name]
        except KeyError:  # pragma: no cover
            return False
        try:
            padstack_pad = padstack.pad_by_layer[layer_name]
        except KeyError:  # pragma: no cover
            return False

        pad_shape = padstack_pad.geometry_type
        params = padstack_pad.parameters_values
        polygon_data = padstack_pad.polygon_data

        rect = None
        pcx = padstack_center[0]
        pcy = padstack_center[1]

        if pad_shape == 1:
            # Circle
            diameter = params[0]
            r = diameter * 0.5
            p1 = [pcx + r, pcy]
            p2 = [pcx, pcy + r]
            p3 = [pcx - r, pcy]
            p4 = [pcx, pcy - r]
            rect = [p1, p2, p3, p4]
        elif pad_shape == 2:
            # Square
            square_size = params[0]
            s2 = square_size * 0.5
            p1 = [pcx + s2, pcy + s2]
            p2 = [pcx - s2, pcy + s2]
            p3 = [pcx - s2, pcy - s2]
            p4 = [pcx + s2, pcy - s2]
            rect = [p1, p2, p3, p4]
        elif pad_shape == 3:
            # Rectangle
            x_size = float(params[0])
            y_size = float(params[1])
            sx2 = x_size * 0.5
            sy2 = y_size * 0.5
            p1 = [pcx + sx2, pcy + sy2]
            p2 = [pcx - sx2, pcy + sy2]
            p3 = [pcx - sx2, pcy - sy2]
            p4 = [pcx + sx2, pcy - sy2]
            rect = [p1, p2, p3, p4]
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
            p1 = [pcx + sx + k, pcy + sy + k]
            p2 = [pcx - sx - k, pcy + sy + k]
            p3 = [pcx - sx - k, pcy - sy - k]
            p4 = [pcx + sx + k, pcy - sy - k]
            rect = [p1, p2, p3, p4]
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
            p1 = [pcx + sx + k, pcy + sy + k]
            p2 = [pcx - x_size * 0.5, pcy + sy + k]
            p3 = [pcx - x_size * 0.5, pcy - sy - k]
            p4 = [pcx + sx + k, pcy - sy - k]
            rect = [p1, p2, p3, p4]
        elif pad_shape == 6:
            # N-Sided Polygon
            size = params[0]
            num_sides = params[1]
            ext_radius = size * 0.5
            apothem = ext_radius * math.cos(math.pi / num_sides)
            p1 = [pcx + apothem, pcy]
            p2 = [pcx, pcy + apothem]
            p3 = [pcx - apothem, pcy]
            p4 = [pcx, pcy - apothem]
            rect = [p1, p2, p3, p4]
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
                rect[i][0] = rect[i][0] + pcx
                rect[i][1] = rect[i][1] + pcy

        if rect is None or len(rect) != 4:
            return False
        path = self._pedb.core_primitives.Shape("polygon", points=rect)
        created_polygon = self._pedb.core_primitives.create_polygon(path, padstack_pad.layer_name)
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
