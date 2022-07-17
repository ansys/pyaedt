import os
import sys

from pyaedt.generic.general_methods import _retry_ntimes
from pyaedt.generic.general_methods import pyaedt_function_handler
from pyaedt.modeler.GeometryOperators import GeometryOperators
from pyaedt.modeler.Object3d import Padstack
from pyaedt.modeler.Object3d import _uname
from pyaedt.modeler.object3dlayout import Circle3dLayout
from pyaedt.modeler.object3dlayout import Components3DLayout
from pyaedt.modeler.object3dlayout import ComponentsSubCircuit3DLayout
from pyaedt.modeler.object3dlayout import Line3dLayout
from pyaedt.modeler.object3dlayout import Nets3DLayout
from pyaedt.modeler.object3dlayout import Pins3DLayout
from pyaedt.modeler.object3dlayout import Polygons3DLayout
from pyaedt.modeler.object3dlayout import Rect3dLayout
from pyaedt.modeler.Primitives import default_materials


class Primitives3DLayout(object):
    """Manages primitives in HFSS 3D Layout.

    This class is inherited in the caller application and is accessible through the primitives variable part
    of modeler object( eg. ``hfss3dlayout.modeler``).

    Parameters
    ----------
    modeler : :class:`pyaedt.modeler.Model3DLayout.Modeler3DLayout`
        Name of the modeler.

    Examples
    --------
    Basic usage demonstrated with an HFSS 3D Layout design:

    >>> from pyaedt import Hfss3dLayout
    >>> aedtapp = Hfss3dLayout()
    >>> prim = aedtapp.modeler
    """

    @pyaedt_function_handler()
    def __getitem__(self, partname):
        """Retrieve a part.

        Parameters
        ----------
        partname : int or str
           Part ID or part name.

        Returns
        -------
        type
          Part object details.

        """
        for el in self.geometries:
            if el == partname:
                return self.geometries[el]
        return None

    def __init__(self, app):
        self.is_outside_desktop = sys.modules["__main__"].isoutsideDesktop
        self._app = app
        self._padstacks = {}
        self._components3d = {}
        self._init_prims()

    @pyaedt_function_handler()
    def _init_prims(self):
        self._components = {}
        self._rectangles = {}
        self._lines = {}
        self._circles = {}
        self._polygons = {}
        self._pins = {}
        self._nets = {}
        self._power_nets = {}
        self._signal_nets = {}
        self._vias = {}

    @property
    def _modeler(self):
        return self._app.modeler

    @property
    def opadstackmanager(self):
        """Aedt oPadstackManager.

        References
        ----------

        >>> oPadstackManger = oDefinitionManager.GetManager("Padstack")
        """
        return self._app.opadstackmanager

    @property
    def components(self):
        """Components.

        Returns
        -------
        dict[str, :class:`pyaedt.modeler.object3dlayout.Components3DLayout`]
            Components objects.

        """
        if self._components:
            return self._components
        objs = self.modeler.oeditor.FindObjects("Type", "component")
        for obj in objs:
            self._components[obj] = Components3DLayout(self, obj)
        return self._components

    @property
    def geometries(self):
        """All Geometries including voids.

        Returns
        -------
        dict
            Dictionary of geometries.

        """
        geom = {}
        for k, v in self.polygons.items():
            geom[k] = v
        for k, v in self.rectangles.items():
            geom[k] = v
        for k, v in self.lines.items():
            geom[k] = v
        for k, v in self.circles.items():
            geom[k] = v
        for k, v in self.voids.items():
            geom[k] = v
        return geom

    @property
    def voids(self):
        """All voids.

        Returns
        -------
        dict
            Dictionary of voids.

        """
        geom = {}
        for k, v in self.polygons_voids.items():
            geom[k] = v
        for k, v in self.rectangles_voids.items():
            geom[k] = v
        for k, v in self.lines_voids.items():
            geom[k] = v
        for k, v in self.circles_voids.items():
            geom[k] = v
        return geom

    @pyaedt_function_handler()
    def objects_by_layer(self, layer_name, object_filter=None, include_voids=False):
        """Retrieve the list of objects that belongs to a specific layer.

        Parameters
        ----------
        layer_name : str
            Name of the layer to filter.
        object_filter : str, list, optional
            Name of the category to include in search. Options are `"poly"`, `"circle"`,
            `"rect"`,`"line"`,`"arc"`, `"via"`,`"pin"` and `"component"`.
        include_voids : bool, optional
            Either if include or not the voids in search.

        Returns
        -------
        list
            Objects found.
        """

        objs = []
        if object_filter:
            if isinstance(object_filter, str):
                object_filter = [object_filter]

            for poly in object_filter:
                objs = self.modeler.oeditor.FilterObjectList(
                    "Type", poly, self.modeler.oeditor.FindObjects("Layer", layer_name)
                )
                if include_voids:
                    objs = self.modeler.oeditor.FilterObjectList(
                        "Type", poly + " void", self.modeler.oeditor.FindObjects("Layer", layer_name)
                    )

        else:
            objs = self.modeler.oeditor.FindObjects("Layer", layer_name)
        return objs

    @pyaedt_function_handler()
    def objects_by_net(self, net_name, object_filter=None, include_voids=False):
        """Retrieve the list of objects that belongs to a specific net.

        Parameters
        ----------
        net_name : str
            Name of the net to filter.
        object_filter : str, list, optional
            Name of the category to include in search. Options are `"poly"`, `"circle"`,
            `"rect"`,`"line"`,`"arc"`, `"via"`,`"pin"` and `"component"`.
        include_voids : bool, optional
            Either if include or not the voids in search.

        Returns
        -------
        list
            Objects found.
        """

        objs = []
        if object_filter:
            if isinstance(object_filter, str):
                object_filter = [object_filter]

            for poly in object_filter:
                objs = self.modeler.oeditor.FilterObjectList(
                    "Type", poly, self.modeler.oeditor.FindObjects("Net", net_name)
                )
                if include_voids:
                    objs = self.modeler.oeditor.FilterObjectList(
                        "Type", poly + " void", self.modeler.oeditor.FindObjects("Net", net_name)
                    )

        else:
            objs = self.modeler.oeditor.FindObjects("Net", net_name)
        return objs

    @property
    def polygons(self):
        """Polygons.

        Returns
        -------
        dict[str, :class:`pyaedt.modeler.object3dlayout.Polygons3DLayout`]
            Pyaedt Objects.
        """
        if self._polygons:
            return self._polygons
        poly_types = ["poly", "plg"]
        for poly in poly_types:
            objs = self.modeler.oeditor.FindObjects("Type", poly)
            for obj in objs:
                self._polygons[obj] = Polygons3DLayout(self, obj, poly, False)
        return self._polygons

    @property
    def lines(self):
        """Lines.

        Returns
        -------
        dict[str, :class:`pyaedt.modeler.object3dlayout.Line3dLayout`]
            Pyaedt Objects.
        """

        if self._lines:
            return self._lines
        poly_types = ["line", "arc"]
        for poly in poly_types:
            objs = self.modeler.oeditor.FindObjects("Type", poly)
            for obj in objs:
                self._lines[obj] = Line3dLayout(self, obj, False)
        return self._lines

    @property
    def circles(self):
        """Circles.

        Returns
        -------
        dict[str, :class:`pyaedt.modeler.object3dlayout.Circle3dLayout`]
            Pyaedt Objects.
        """
        if self._circles:
            return self._circles
        objs = self.modeler.oeditor.FindObjects("Type", "circle")
        for obj in objs:
            self._circles[obj] = Circle3dLayout(self, obj, False)
        return self._circles

    @property
    def rectangles(self):
        """Rectangles.

        Returns
        -------
        dict[str, :class:`pyaedt.modeler.object3dlayout.Rect3dLayout`]
            Pyaedt Objects.
        """
        if self._rectangles:
            return self._rectangles
        objs = self.modeler.oeditor.FindObjects("Type", "rect")
        for obj in objs:
            self._rectangles[obj] = Rect3dLayout(self, obj, False)
        return self._rectangles

    @property
    def polygons_voids(self):
        """Void Polygons.

        Returns
        -------
        dict[str, :class:`pyaedt.modeler.object3dlayout.Polygons3DLayout`]
            Pyaedt Objects.
        """
        if self._polygons:
            return self._polygons
        poly_types = ["poly", "plg"]
        for poly in poly_types:
            objs = self.modeler.oeditor.FindObjects("Type", poly + " void")
            for obj in objs:
                self._polygons[obj] = Polygons3DLayout(self, obj, poly, True)
        return self._polygons

    @property
    def lines_voids(self):
        """Void Lines.

        Returns
        -------
        dict[str, :class:`pyaedt.modeler.object3dlayout.Line3dLayout`]
            Pyaedt Objects.
        """

        if self._lines:
            return self._lines
        poly_types = ["line", "arc"]
        for poly in poly_types:
            objs = self.modeler.oeditor.FindObjects("Type", poly + " void")
            for obj in objs:
                self._lines[obj] = Line3dLayout(self, obj, True)
        return self._lines

    @property
    def circles_voids(self):
        """Void Circles.

        Returns
        -------
        dict[str, :class:`pyaedt.modeler.object3dlayout.Circle3dLayout`]
            Pyaedt Objects.
        """
        if self._circles:
            return self._circles
        objs = self.modeler.oeditor.FindObjects("Type", "circle void")
        for obj in objs:
            self._circles[obj] = Circle3dLayout(self, obj, True)
        return self._circles

    @property
    def rectangles_voids(self):
        """Void Rectangles.

        Returns
        -------
        dict[str, :class:`pyaedt.modeler.object3dlayout.Rect3dLayout`]
            Pyaedt Objects.
        """
        if self._rectangles:
            return self._rectangles
        objs = self.modeler.oeditor.FindObjects("Type", "rect void")
        for obj in objs:
            self._rectangles[obj] = Rect3dLayout(self, obj, True)
        return self._rectangles

    @property
    def components_3d(self):
        """Components.

        Returns
        -------
        dict[str, :class:`pyaedt.modeler.object3dlayout.Components3DLayout`]
            Pyaedt Objects.
        """
        if not self._components3d:
            for i in range(1, 1000):
                cmp_info = self.oeditor.GetComponentInfo(str(i))
                if cmp_info and "ComponentName" in cmp_info[0]:
                    self._components3d[str(i)] = Components3DLayout(self, str(i))
        return self._components3d

    @property
    def pins(self):
        """Pins.

        Returns
        -------
        dict[str, :class:`pyaedt.modeler.object3dlayout.Pins3DLayout`]
            Pins Dictionary.

        """
        if self._pins:
            return self._pins
        objs = self.modeler.oeditor.FindObjects("Type", "pin")
        for obj in objs:
            self._pins[obj] = Pins3DLayout(self, obj)
        return self._pins

    @property
    def vias(self):
        """Vias.

        Returns
        -------
        dict[str, :class:`pyaedt.modeler.object3dlayout.Pins3DLayout`]
            Vias Dictionary.
        """
        if self._vias:
            return self._vias
        objs = self.modeler.oeditor.FindObjects("Type", "via")
        for obj in objs:
            self._vias[obj] = Pins3DLayout(self, obj, is_pin=False)
        return self._vias

    @property
    def nets(self):
        """Nets.

        Returns
        -------
        dict[str, :class:`pyaedt.modeler.object3dlayout.Nets3DLayout`]
            Nets Dictionary.

        """
        n = {}
        for k, v in self.power_nets.items():
            n[k] = v
        for k, v in self.signal_nets.items():
            n[k] = v
        return n

    @property
    def power_nets(self):
        """Nets.

        Returns
        -------
        dict[str, :class:`pyaedt.modeler.object3dlayout.Nets3DLayout`]
            Power Nets Dictionary.

        """
        if self._power_nets:
            return self._power_nets

        objs = self.modeler.oeditor.GetNetClassNets("<Power/Ground>")
        for obj in objs:
            self._power_nets[obj] = Nets3DLayout(self, obj)
        return self._power_nets

    @property
    def signal_nets(self):
        """Nets.

        Returns
        -------
        dict[str, :class:`pyaedt.modeler.object3dlayout.Nets3DLayout`]
            Signal Nets Dictionary.

        """
        if self._signal_nets:
            return self._signal_nets

        objs = self.modeler.oeditor.GetNetClassNets("Non Power/Ground")
        for obj in objs:
            self._signal_nets[obj] = Nets3DLayout(self, obj)
        return self._signal_nets

    @property
    def defaultmaterial(self):
        """Default materials.

        Returns
        -------
        list
            List of default materials.

        """
        return default_materials[self._app._design_type]

    @property
    def logger(self):
        """Logger."""
        return self._app.logger

    @property
    def version(self):
        """AEDT version.

        Returns
        -------
        str
            Version of AEDT.

        """
        return self._app._aedt_version

    @property
    def modeler(self):
        """Modeler."""
        return self._modeler

    @property
    def model_units(self):
        """Model units."""
        return self.modeler.model_units

    @property
    def Padstack(self):
        """Padstack."""
        return Padstack()

    @pyaedt_function_handler()
    def new_padstack(self, name="Padstack"):
        """Create a `Padstack` object that can be used to create a padstack.

        Parameters
        ----------
        name : str, optional
            Name of the padstack. The default is ``"Padstack"``.

        Returns
        -------
        type
            Padstack object if a padstack with this name does not already exist.

        """
        if name in self.padstacks:
            return None
        else:
            self.padstacks[name] = Padstack(name, self.opadstackmanager, self.model_units)
            return self.padstacks[name]

    @property
    def padstacks(self):
        """Read all padstacks from HFSS 3D Layout.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.

        """
        if self._padstacks:
            return self._padstacks
        self._padstacks = {}
        names = GeometryOperators.List2list(self.opadstackmanager.GetNames())

        for name in names:
            props_all = GeometryOperators.List2list(self.opadstackmanager.GetData(name))

            props = []
            for p in props_all:
                try:
                    if p[0] == "NAME:psd":
                        props = p
                except:
                    pass
            self._padstacks[name] = Padstack(name, self.opadstackmanager, self.model_units)

            for prop in props:
                if type(prop) is str:
                    if prop == "mat:=":
                        self._padstacks[name].mat = props[props.index(prop) + 1]
                    elif prop == "plt:=":
                        self._padstacks[name].plating = props[props.index(prop) + 1]
                    elif prop == "hRg:=":
                        self._padstacks[name].holerange = props[props.index(prop) + 1]
                    elif prop == "sbsh:=":
                        self._padstacks[name].solder_shape = props[props.index(prop) + 1]
                    elif prop == "sbpl:=":
                        self._padstacks[name].solder_placement = props[props.index(prop) + 1]
                    elif prop == "sbr:=":
                        self._padstacks[name].solder_rad = props[props.index(prop) + 1]
                    elif prop == "sb2:=":
                        self._padstacks[name].sb2 = props[props.index(prop) + 1]
                    elif prop == "sbn:=":
                        self._padstacks[name].solder_mat = props[props.index(prop) + 1]
                    elif prop == "hle:=":
                        self._padstacks[name].hole.shape = props[props.index(prop) + 1][1]
                        self._padstacks[name].hole.sizes = props[props.index(prop) + 1][3]
                        self._padstacks[name].hole.x = props[props.index(prop) + 1][5]
                        self._padstacks[name].hole.y = props[props.index(prop) + 1][7]
                        self._padstacks[name].hole.rot = props[props.index(prop) + 1][9]
                try:
                    if prop[0] == "NAME:pds":
                        layers_num = len(prop) - 1
                        i = 1
                        while i <= layers_num:
                            lay = prop[i]
                            lay_name = lay[2]
                            lay_id = int(lay[4])
                            if i != 1:
                                self._padstacks[name].add_layer(lay_name)
                            self._padstacks[name].layers[lay_name].layername = lay_name
                            self._padstacks[name].layers[lay_name].pad = self._padstacks[name].add_hole(
                                lay[6][1], list(lay[6][3]), lay[6][5], lay[6][7], lay[6][9]
                            )
                            self._padstacks[name].layers[lay_name].antipad = self._padstacks[name].add_hole(
                                lay[8][1], list(lay[8][3]), lay[8][5], lay[8][7], lay[8][9]
                            )
                            self._padstacks[name].layers[lay_name].thermal = self._padstacks[name].add_hole(
                                lay[10][1], list(lay[10][3]), lay[10][5], lay[10][7], lay[10][9]
                            )
                            self._padstacks[name].layers[lay_name].connectionx = lay[12]
                            self._padstacks[name].layers[lay_name].connectiony = lay[14]
                            self._padstacks[name].layers[lay_name].connectiondir = lay[16]
                            i += 1
                        pass
                except:
                    pass

        return self._padstacks

    @pyaedt_function_handler()
    def change_net_visibility(self, netlist=None, visible=False):
        """Change the visibility of one or more nets.

        Parameters
        ----------
        netlist : str  or list, optional
            One or more nets to visualize. The default is ``None``.
        visible : bool, optional
            Whether to make the selected nets visible. The
            The default value is ``False``.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.

        References
        ----------

        >>> oEditor.SetNetVisible
        """
        if not netlist:
            netlist = self.nets

        if type(netlist) is str:
            netlist = [netlist]
        args = ["NAME:Args"]
        for net in netlist:
            args.append("Name:=")
            args.append(net)
            args.append("Vis:=")
            args.append(visible)
        self.oeditor.SetNetVisible(args)
        return True

    @pyaedt_function_handler()
    def create_via(
        self,
        padstack="PlanarEMVia",
        x=0,
        y=0,
        rotation=0,
        hole_diam=None,
        top_layer=None,
        bot_layer=None,
        name=None,
        netname=None,
    ):
        """Create a via based on an existing padstack.

        Parameters
        ----------
        padstack : str, optional
            Name of the padstack. The default is ``"PlanarEMVia"``.
        x : float, optional
            Position on the X axis. The default is ``0``.
        y : float, optional
            Position on the Y axis. The default is ``0``.
        rotation : float, optional
            Angle rotation in degrees. The default is ``0``.
        hole_diam :
            Diameter of the hole. The default is ``None``, in which case
            the override is disabled.
        top_layer : str, optional
            Top layer. The default is ``None``.
        bot_layer : str, optional
            Bottom layer. The default is ``None``.
        name : str, optional
            Name of the via. The default is ``None``, in which case the
            default name is assigned.
        netname : str, optional
            Name of the net. The default is ``None``, in which case the
            default name is assigned.

        Returns
        -------
        str
            Name of the via created when successful.

        References
        ----------

        >>> oEditor.CreateVia
        """
        layers = self.modeler.layers.all_signal_layers
        if not top_layer:
            top_layer = layers[0]
        if not bot_layer:
            bot_layer = layers[len(layers) - 1]
        if not name:
            name = _uname()
        else:
            listnames = self.oeditor.FindObjects("Name", name)
            if listnames:
                name = _uname(name)
        arg = ["NAME:Contents"]
        arg.append("name:="), arg.append(name)
        arg.append("ReferencedPadstack:="), arg.append(padstack),
        arg.append("vposition:="),
        arg.append(["x:=", self.arg_with_dim(x), "y:=", self.arg_with_dim(y)])
        arg.append("vrotation:="), arg.append([str(rotation) + "deg"])
        if hole_diam:
            arg.append("overrides hole:="), arg.append(True)
            arg.append("hole diameter:="), arg.append([self.arg_with_dim(hole_diam)])

        else:
            arg.append("overrides hole:="), arg.append(False)
            arg.append("hole diameter:="), arg.append([self.arg_with_dim(1)])

        arg.append("Pin:="), arg.append(False)
        arg.append("highest_layer:="), arg.append(top_layer)
        arg.append("lowest_layer:="), arg.append(bot_layer)
        self.oeditor.CreateVia(arg)
        # self.objects[name] = Object3dlayout(self)
        # self.objects[name].name = name
        # if netname:
        #     self.objects[name].set_net_name(netname)
        return name

    @pyaedt_function_handler()
    def create_circle(self, layername, x, y, radius, name=None, netname=None):
        """Create a circle on a layer.

        Parameters
        ----------
        layername : str
            Name of the layer.
        x : float
            Position on the X axis.
        y : float
            Position on the Y axis.
        radius : float
            Radius of the circle.
        name : str, optional
            Name of the circle. The default is ``None``, in which case the
            default name is assigned.
        netname : str, optional
            Name of the net. The default is ``None``, in which case the
            default name is assigned.

        Returns
        -------
        str
            Name of the circle created when successful.

        References
        ----------

        >>> oEditor.CreateCircle
        """
        if not name:
            name = _uname()
        else:
            listnames = self.oeditor.FindObjects("Name", name)
            if listnames:
                name = _uname(name)

        vArg1 = ["NAME:Contents", "circleGeometry:="]
        vArg2 = []
        vArg2.append("Name:="), vArg2.append(name)
        vArg2.append("LayerName:="), vArg2.append(layername)
        vArg2.append("lw:="), vArg2.append("0")
        vArg2.append("x:="), vArg2.append(self.arg_with_dim(x))
        vArg2.append("y:="), vArg2.append(self.arg_with_dim(y))
        vArg2.append("r:="), vArg2.append(self.arg_with_dim(radius))
        vArg1.append(vArg2)
        self.oeditor.CreateCircle(vArg1)
        self._circles[name] = Circle3dLayout(self, name, False)
        return name

    @pyaedt_function_handler()
    def create_rectangle(self, layername, origin, dimensions, corner_radius=0, angle=0, name=None, netname=None):
        """Create a rectangle on a layer.

        Parameters
        ----------
        layername : str
            Name of the layer.
        origin : list
            Origin of the coordinate system in a list of ``[x, y, z]`` coordinates.
        dimensions : list
            Dimensions for the box in a list of ``[x, y, z]`` coordinates.
        corner_radius : float, optional
        angle : float, optional
            Angle rotation in degrees. The default is ``0``.
        name : str, optional
            Name of the rectangle. The default is ``None``, in which case the
            default name is assigned.
        netname : str, optional
            Name of the net. The default is ``None``, in which case the
            default name is assigned.

        Returns
        -------
        str
            Name of the rectangle created when successful.

        References
        ----------

        >>> oEditor.CreateRectangle
        """

        if not name:
            name = _uname()
        else:
            listnames = self.oeditor.FindObjects("Name", name)
            if listnames:
                name = _uname(name)

        vArg1 = ["NAME:Contents", "rectGeometry:="]
        vArg2 = []
        vArg2.append("Name:="), vArg2.append(name)
        vArg2.append("LayerName:="), vArg2.append(layername)
        vArg2.append("lw:="), vArg2.append("0")
        vArg2.append("Ax:="), vArg2.append(self.arg_with_dim(origin[0]))
        vArg2.append("Ay:="), vArg2.append(self.arg_with_dim(origin[1]))
        vArg2.append("Bx:="), vArg2.append(self.arg_with_dim(dimensions[0]))
        vArg2.append("By:="), vArg2.append(self.arg_with_dim(dimensions[1]))
        vArg2.append("cr:="), vArg2.append(self.arg_with_dim(corner_radius))
        vArg2.append("ang="), vArg2.append(self.arg_with_dim(angle))
        vArg1.append(vArg2)
        self.oeditor.CreateRectangle(vArg1)
        self._rectangles[name] = Rect3dLayout(self, name, False)
        return name

    @pyaedt_function_handler()
    def create_line(self, layername, center_line_list, lw=1, start_style=0, end_style=0, name=None, netname=None):
        """Create a line based on a list of points.

        Parameters
        ----------
        layername : str
            Name of the layer to create the line on.
        center_line_list : list
            List of centerline coordinates in the form of ``[x, y, z]``.
        lw : float, optional
            Line width. The default is ``1``.
        start_style :
            Starting style of the line. Options are:

            * ``0`` - Flat
            * ``1`` - Extended
            * ``2`` - Round

            The default is ``0``.
        end_style :
            Ending style of the line. The options are the same as
            those for ``start_style``. The default is ``0``.
        name : str, optional
            Name  of the line. The default is ``None``, in which case the
            default name is assigned.
        netname : str, optional
            Name of the net. The default is ``None``, in which case the
            default name is assigned.

        Returns
        -------
        str
            Name of the line created when successful.

        References
        ----------

        >>> oEditor.CreateLine
        """
        if not name:
            name = _uname()
        else:
            listnames = self.oeditor.FindObjects("Name", name)
            if listnames:
                name = _uname(name)
        arg = ["NAME:Contents", "lineGeometry:="]
        arg2 = [
            "Name:=",
            name,
            "LayerName:=",
            layername,
            "lw:=",
            self.arg_with_dim(lw),
            "endstyle:=",
            end_style,
            "StartCap:=",
            start_style,
            "n:=",
            len(center_line_list),
            "U:=",
            self.model_units,
        ]
        for a in center_line_list:
            arg2.append("x:=")
            arg2.append(a[0])
            arg2.append("y:=")
            arg2.append(a[1])
        arg.append(arg2)
        self.oeditor.CreateLine(arg)
        self._lines[name] = Line3dLayout(self, name, False)
        return name

    @pyaedt_function_handler()
    def arg_with_dim(self, Value, sUnits=None):
        """Format arguments with dimensions.

        Parameters
        ----------
        Value :

        sUnits :
             The default is ``None``.

        Returns
        -------
        str
            String containing the value or value and the units if `sUnits` is not ``None``.
        """
        if type(Value) is str:
            val = Value
        else:
            if sUnits is None:
                sUnits = self.model_units
            val = "{0}{1}".format(Value, sUnits)

        return val

    @pyaedt_function_handler
    def place_3d_component(
        self, component_path, number_of_terminals=1, placement_layer=None, component_name=None, pos_x=0, pos_y=0
    ):  # pragma: no cover
        """Place a Hfss 3d Component in Hfss3dLayout.

        :param component_path:
        :param number_of_terminals:
        :param placement_layer:
        :return:
        """
        if not component_name:
            component_name = os.path.basename(component_path).split(".")[0]
        args = ["NAME:" + component_name]
        infos = [
            "Type:=",
            27,
            "NumTerminals:=",
            number_of_terminals,
            "DataSource:=",
            "",
            "ModifiedOn:=",
            1646294080,
            "Manufacturer:=",
            "",
            "Symbol:=",
            "v1_" + component_name,
            "ModelNames:=",
            "",
            "Footprint:=",
            "",
            "Description:=",
            "",
            "InfoTopic:=",
            "",
            "InfoHelpFile:=",
            "",
            "IconFile:=",
            "BlueDot.bmp",
            "Library:=",
            "",
            "OriginalLocation:=",
            "Project",
            "IEEE:=",
            "",
            "Author:=",
            "",
            "OriginalAuthor:=",
            "",
            "CreationDate:=",
            1646294079,
            "ExampleFile:=",
            "",
            "HiddenComponent:=",
            0,
            "CircuitEnv:=",
            0,
            "GroupID:=",
            0,
        ]
        args.append("Info:=")
        args.append(infos)
        args.append("CircuitEnv:=")
        args.append(0)
        args.append("Refbase:=")
        args.append("U")
        args.append("NumParts:=")
        args.append(1)
        args.append("ModSinceLib:=")
        args.append(True)
        args.append("CompExtID:=")
        args.append(8)
        args.append("3DCompSourceFileName:=")
        args.append(component_path)

        _retry_ntimes(10, self.modeler.o_component_manager.Add, args)
        stack_layers = ["0:{}".format(i) for i in self.modeler.layers.all_layers]
        drawing = ["{}:{}".format(i, i) for i in self.modeler.layers.drawing_layers]
        arg_x = self.modeler._arg_with_dim(pos_x)
        arg_y = self.modeler._arg_with_dim(pos_y)
        args = [
            "NAME:Contents",
            "definition_name:=",
            component_name,
            "placement:=",
            ["x:=", arg_x, "y:=", arg_y],
            "layer:=",
            placement_layer,
            "isCircuit:=",
            False,
            "compInstName:=",
            "1",
            "rect_width:=",
            0.01,
            "StackupLayers:=",
            stack_layers,
            "DrawLayers:=",
            drawing,
        ]
        comp_name = _retry_ntimes(10, self.modeler.oeditor.CreateComponent, args)
        comp = ComponentsSubCircuit3DLayout(self, comp_name.split(";")[-1])
        self.components_3d[comp_name.split(";")[-1]] = comp
        return comp  #
