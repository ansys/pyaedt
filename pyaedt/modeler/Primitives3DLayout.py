import sys
from collections import defaultdict

from ..generic.general_methods import aedt_exception_handler
from .Object3d import Padstack, Components3DLayout, Geometries3DLayout, Pins3DLayout, Nets3DLayout, \
    _uname
from .Primitives import _ironpython, default_materials
from .GeometryOperators import GeometryOperators
import pkgutil
modules = [tup[1] for tup in pkgutil.iter_modules()]
if 'clr' in modules or _ironpython:
    import clr
    from System import String


class Primitives3DLayout(object):
    """Primitives3DLayout class.
    
    This class provides all functionalities for managing primitives in HFSS 3D Layout.
    
    Parameters
    ----------
    parent : str
        Name of the parent AEDT application.
    modeler : str
        Name of the modeler.
    
    """
    @aedt_exception_handler
    def __getitem__(self, partname):
        """Retrieve a part.
        
        Parameters
        ----------
        partname: int or str
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

    def __init__(self, parent, modeler):
        self._modeler = modeler
        self._parent = parent
        self._currentId = 0
        self.padstacks = defaultdict(Padstack)
        self._components = defaultdict(Components3DLayout)
        self._geometries = defaultdict(Geometries3DLayout)
        self._pins = defaultdict(Pins3DLayout)
        self._nets = defaultdict(Nets3DLayout)
        self._main = sys.modules['__main__']
        self.isoutsideDesktop = self._main.isoutsideDesktop
        pass

    @property
    def components(self):
        """Components.
        
        Returns
        -------
        list
            List of components from EDB. If no EDB is present, ``None`` is returned.
        
        """
        try:
            comps = list(self.modeler.edb.core_components.components.keys())
        except:
            comps=[]
        for el in comps:
            self._components[el] = Components3DLayout(self, el)
        return self._components

    @property
    def geometries(self):
        """Geometries.
        
        Returns
        -------
        list
            List of geometries from EDB. If no EDB is present, ``None`` is returned.
           
           """
        try:
            prims = self.modeler.edb.core_primitives.primitives
        except:
            prims = []
        for el in prims:

            if _ironpython:
                name = clr.Reference[System.String]()
                response = el.GetProductProperty(0, 1, name)
            else:
                val = String("")
                response, name = el.GetProductProperty(0, 1, val)
            elval = el.GetType()
            elid = el.GetId()
            if not name:
                if "Rectangle" in elval.ToString():
                    name = "rect_" + str(elid)
                elif "Circle" in elval.ToString():
                    name = "circle_" + str(elid)
                elif "Polygon" in elval.ToString():
                    name = "poly_" + str(elid)
                elif "Path" in elval.ToString():
                    name = "line_" + str(elid)
                elif "Bondwire" in elval.ToString():
                    name = "bondwire_" + str(elid)
                else:
                    continue
            self._geometries[name] = Geometries3DLayout(self, name,  elid)
        return self._geometries

    @property
    def pins(self):
        """Pins.
        
        Returns
        -------
        list
            List of pins from EDB. If no EDB is present, ``None`` is returned.
        
        """
        try:
            pins_objs = list(self.modeler.edb.pins)
        except:
            pins_objs = []
        for el in pins_objs:
            if _ironpython:
                name = clr.Reference[System.String]()
                response = el.GetProductProperty(0, 11, name)
            else:
                val = String("")
                response, name = el.GetProductProperty(0, 11, val)
            name = str(name).strip("'")
            self._pins[name] = Pins3DLayout(self, el.GetComponent().GetName(), el.GetName(), name)
        return self._pins

    @property
    def nets(self):
        """Nets.
        
        Returns
        -------
        list
            List of nets from EDB. If no EDB is present, ``None`` is returned.
        
        """
        try:
            nets_objs = list(self.modeler.edb.core_nets.nets)
        except:
            nets_objs = {}
        for el in nets_objs:
            self._nets[el] = Nets3DLayout(self, el)
        return self._nets

    @property
    def defaultmaterial(self):
        """Default materials.
        
        Returns
        -------
        list
            List of default materials.
          
        """
        return default_materials[self._parent._design_type]

    @property
    def _messenger(self):
        """_messenger."""
        return self._parent._messenger

    @property
    def version(self):
        """AEDT version.
        
        Returns
        -------
        str
            Version of AEDT.
        
        """
        return self._parent._aedt_version

    @property
    def modeler(self):
        """Modeler."""
        return self._modeler

    @property
    def oeditor(self):
        """Editor object."""
        return self.modeler.oeditor

    @property
    def opadstackmanager(self):
        """Padstack manager. """
        return self._parent._oproject.GetDefinitionManager().GetManager("Padstack")

    @property
    def model_units(self):
        """Model units."""
        return self.modeler.model_units

    @property
    def Padstack(self):
        """Padstack."""
        return Padstack()

    @aedt_exception_handler
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

    @aedt_exception_handler
    def init_padstacks(self):
        """Read all padstacks from HFSS 3D Layout.
        
        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.

        """
        names = GeometryOperators.List2list(self.opadstackmanager.GetNames())

        for name in names:
            props_all = GeometryOperators.List2list(self.opadstackmanager.GetData(name))

            props = []
            for p in props_all:
                try:
                    if p[0] == 'NAME:psd':
                        props = p
                except:
                    pass
            self.padstacks[name] = Padstack(name, self.opadstackmanager, self.model_units)

            for prop in props:
                if type(prop) is str:
                    if prop == "mat:=":
                        self.padstacks[name].mat = props[props.index(prop)+1]
                    elif prop == "plt:=":
                        self.padstacks[name].plating = props[props.index(prop) + 1]
                    elif prop == "hRg:=":
                        self.padstacks[name].holerange = props[props.index(prop) + 1]
                    elif prop == "sbsh:=":
                        self.padstacks[name].solder_shape = props[props.index(prop) + 1]
                    elif prop == "sbpl:=":
                        self.padstacks[name].solder_placement = props[props.index(prop) + 1]
                    elif prop == "sbr:=":
                        self.padstacks[name].solder_rad = props[props.index(prop) + 1]
                    elif prop == "sb2:=":
                        self.padstacks[name].sb2 = props[props.index(prop) + 1]
                    elif prop == "sbn:=":
                        self.padstacks[name].solder_mat = props[props.index(prop) + 1]
                    elif prop == "hle:=":
                        self.padstacks[name].hole.shape = props[props.index(prop) + 1][1]
                        self.padstacks[name].hole.sizes = props[props.index(prop) + 1][3]
                        self.padstacks[name].hole.x = props[props.index(prop) + 1][5]
                        self.padstacks[name].hole.y = props[props.index(prop) + 1][7]
                        self.padstacks[name].hole.rot = props[props.index(prop) + 1][9]
                try:
                    if prop[0] == 'NAME:pds':
                        layers_num = len(prop)-1
                        i=1
                        while i<=layers_num:
                            lay = prop[i]
                            lay_name = lay[2]
                            lay_id = int(lay[4])
                            if i!= 1:
                                self.padstacks[name].add_layer(lay_name)
                            self.padstacks[name].layers[lay_name].layername = lay_name
                            self.padstacks[name].layers[lay_name].pad = self.padstacks[name].add_hole(lay[6][1],list(lay[6][3]),lay[6][5],lay[6][7],lay[6][9])
                            self.padstacks[name].layers[lay_name].antipad = self.padstacks[name].add_hole(lay[8][1],list(lay[8][3]),lay[8][5],lay[8][7],lay[8][9])
                            self.padstacks[name].layers[lay_name].thermal = self.padstacks[name].add_hole(lay[10][1],list(lay[10][3]),lay[10][5],lay[10][7],lay[10][9])
                            self.padstacks[name].layers[lay_name].connectionx = lay[12]
                            self.padstacks[name].layers[lay_name].connectiony = lay[14]
                            self.padstacks[name].layers[lay_name].connectiondir = lay[16]
                            i +=1
                        pass
                except:
                    pass

        return True

    @aedt_exception_handler
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

    @aedt_exception_handler
    def create_via(self, padstack="PlanarEMVia", x=0, y=0, rotation=0, hole_diam=None, top_layer=None, bot_layer=None,
                   name=None, netname=None):
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
            Name of the created via when successful.

        """
        layers = self.modeler.layers.all_signal_layers
        if not top_layer:
            top_layer = layers[0]
        if not bot_layer:
            bot_layer = layers[len(layers)-1]
        if not name:
            name = _uname()
        else:
            listnames = self.oeditor.FindObjects("Name", name)
            if listnames:
                name = _uname(name)
        arg = ["NAME:Contents"]
        arg.append("name:="),  arg.append(name)
        arg.append("ReferencedPadstack:=")	, arg.append(padstack),
        arg.append("vposition:="),
        arg.append(["x:=", self.arg_with_dim(x), "y:=", self.arg_with_dim(y)])
        arg.append("vrotation:="), arg.append([str(rotation) + "deg"])
        if hole_diam:
            arg.append("overrides hole:="), arg.append(True)
            arg.append("hole diameter:="), arg.append([self.arg_with_dim("hole_diam")])

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

    @aedt_exception_handler
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
            Name of the created circle when successful.

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
        if self.isoutsideDesktop:
            self._geometries[name] = Geometries3DLayout(self, name)
            if netname:
                self._geometries[name].set_net_name(netname)
        return name

    @aedt_exception_handler
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
            Name of the created rectangle when successful.

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
        if self.isoutsideDesktop:
            self._geometries[name] = Geometries3DLayout(self, name)
            if netname:
                self._geometries[name].set_net_name(netname)
        return name

    @aedt_exception_handler
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
            Name of the created line when successful.

        """
        if not name:
            name = _uname()
        else:
            listnames = self.oeditor.FindObjects("Name", name)
            if listnames:
                name = _uname(name)
        arg = ["NAME:Contents", "lineGeometry:="]
        arg2 = ["Name:=", name, "LayerName:=", layername, "lw:=", self.arg_with_dim(lw), "endstyle:=", end_style,
                "StartCap:=", start_style, "n:=", len(center_line_list), "U:=", self.model_units]
        for a in center_line_list:
            arg2.append("x:=")
            arg2.append(a[0])
            arg2.append("y:=")
            arg2.append(a[1])
        arg.append(arg2)
        self.oeditor.CreateLine(arg)
        if self.isoutsideDesktop:
            self._geometries[name] = Geometries3DLayout(self, name)
            if netname:
                self._geometries[name].set_net_name(netname)
        return name


    @aedt_exception_handler
    def arg_with_dim(self, Value, sUnits=None):
        """

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
