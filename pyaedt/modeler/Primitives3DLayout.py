import sys
from collections import defaultdict

from ..generic.general_methods import aedt_exception_handler
from .Object3d import Padstack, Components3DLayout, Geometries3DLayout, Pins3DLayout, Nets3DLayout, \
    _uname
from .Primitives import _ironpython, default_materials
from .GeometryOperators import GeometryOperators
import pkgutil
modules = [tup[1] for tup in pkgutil.iter_modules()]
if 'clr' in modules:
    import clr
    from System import String


class Primitives3DLayout(object):
    """Class for management of all Primitives of HFSS3DLayout"""
    @aedt_exception_handler
    def __getitem__(self, partname):
        """
        :param partname: if integer try to get the object id. if string, trying to get object Name
        :return: part object details
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
        """:return: Component List from EDB. If no EDB is present none is returned"""
        try:
            comps = list(self.modeler.edb.core_components.components.keys())
        except:
            comps=[]
        for el in comps:
            self._components[el] = Components3DLayout(self, el)
        return self._components

    @property
    def geometries(self):
        """:return: Geometries List from EDB. If no EDB is present none is returned"""
        try:
            prims = self.modeler.edb.active_layout.Primitives
        except:
            prims = []
        for el in prims:

            if _ironpython:
                name = clr.Reference[System.String]()
                response = el.GetProductProperty(0, 1, name)
            else:
                name = String("")
                response, name = el.GetProductProperty(0, 1, name)
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
        """:return: Pins List from EDB. If no EDB is present none is returned"""
        try:
            pins_objs = list(self.modeler.edb.pins)
        except:
            pins_objs = []
        for el in pins_objs:
            val = String("")
            response, name = el.GetProductProperty(0, 11, val)
            #name = el.GetComponent().GetName() + "-" + el.GetName()
            self._pins[name] = Pins3DLayout(self, el.GetComponent().GetName(), el.GetName(), name)
        return self._pins

    @property
    def nets(self):
        """:return: Nets List from EDB. If no EDB is present none is returned"""
        try:
            nets_objs = list(self.modeler.edb.core_nets.nets)
        except:
            nets_objs = {}
        for el in nets_objs:
            self._nets[el] = Nets3DLayout(self, el)
        return self._nets

    @property
    def defaultmaterial(self):
        """ """
        return default_materials[self._parent._design_type]

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
    def oeditor(self):
        """ """
        return self.modeler.oeditor

    @property
    def opadstackmanager(self):
        """ """
        return self._parent._oproject.GetDefinitionManager().GetManager("Padstack")

    @property
    def model_units(self):
        """ """
        return self.modeler.model_units

    @property
    def Padstack(self):
        """ """
        return Padstack()

    @aedt_exception_handler
    def new_padstack(self, name="Padstack"):
        """Return a new Padstack object that can be used in HFSS 3D Layout to create a new Padstack

        Parameters
        ----------
        name :
            Padstack Name (Default value = "Padstack")

        Returns
        -------
        type
            Padstack Object if name is doesn't already exists

        """
        if name in self.padstacks:
            return None
        else:
            self.padstacks[name] = Padstack(name, self.opadstackmanager, self.model_units)
            return self.padstacks[name]

    @aedt_exception_handler
    def init_padstacks(self):
        """Read all Padstack from HFSS 3D Layout
        
        :return: True

        Parameters
        ----------

        Returns
        -------

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
        """Change the visibility of a net or net list

        Parameters
        ----------
        netlist :
            single net or netlist to visualize (Default value = None)
        visible :
            Boolean (Default value = False)

        Returns
        -------
        type
            Boolean

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
        """Create a Via based on existing padstack

        Parameters
        ----------
        padstack :
            String containing the Padstack Name (Default value = "PlanarEMVia")
        x :
            x position (Default value = 0)
        y :
            y position (Default value = 0)
        rotation :
            angle rotation in deg (Default value = 0)
        hole_diam :
            hole diameter. If None Override is disabled (Default value = None)
        top_layer :
            top layer (Default value = None)
        bot_layer :
            bottom layer (Default value = None)
        name :
            Via Name (Default value = None)
        netname :
            optional Netname (Default value = None)

        Returns
        -------
        type
            Name of the created object, if successful

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
        """Create Circle on specific layer

        Parameters
        ----------
        layername :
            layername
        x :
            x position float
        y :
            y position float
        radius :
            radius float
        name :
            Object Name (Default value = None)
        netname :
            optional Netname (Default value = None)

        Returns
        -------
        type
            Name of the created object, if successful

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
    def create_rectangle(self, layername, ax, ay, bx, by, cr=0, ang=0, name=None, netname=None):
        """Create a Rectangle on specific layer

        Parameters
        ----------
        layername :
            layername
        x :
            x position float
        y :
            y position float
        radius :
            radius float
        name :
            Object Name (Default value = None)
        netname :
            optional Netname (Default value = None)
        ax :
            
        ay :
            
        bx :
            
        by :
            
        cr :
             (Default value = 0)
        ang :
             (Default value = 0)

        Returns
        -------
        type
            Name of the created object, if successful

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
        vArg2.append("Ax:="), vArg2.append(self.arg_with_dim(ax))
        vArg2.append("Ay:="), vArg2.append(self.arg_with_dim(ay))
        vArg2.append("Bx:="), vArg2.append(self.arg_with_dim(bx))
        vArg2.append("By:="), vArg2.append(self.arg_with_dim(by))
        vArg2.append("cr:="), vArg2.append(self.arg_with_dim(cr))
        vArg2.append("ang="), vArg2.append(self.arg_with_dim(ang))
        vArg1.append(vArg2)
        self.oeditor.CreateRectangle(vArg1)
        if self.isoutsideDesktop:
            self._geometries[name] = Geometries3DLayout(self, name)
            if netname:
                self._geometries[name].set_net_name(netname)
        return name

    @aedt_exception_handler
    def create_line(self, layername, lw=1, x=[], y=[], start_style=0, end_style=0, name=None, netname=None):
        """Create Line based on specific list of point

        Parameters
        ----------
        layername :
            layer name on which create the object
        lw :
            line width (Default value = 1)
        x :
            array of float containing x point of each point of the line (Default value = [])
        y :
            array of float containing y point of each point of the line (Default value = [])
        start_style :
            start style of the line. 0 Flat, 1 Extended, 2 Round (Default value = 0)
        end_style :
            end style of the line. 0 Same as start, 1 Flat, 2 Extended, 3 Round (Default value = 0)
        name :
            Object Name (Default value = None)
        netname :
            optional Netname (Default value = None)

        Returns
        -------
        type
            Name of the created object, if successful

        """
        if not name:
            name = _uname()
        else:
            listnames = self.oeditor.FindObjects("Name", name)
            if listnames:
                name = _uname(name)
        arg = ["NAME:Contents", "lineGeometry:="]
        arg2 = ["Name:=", name, "LayerName:=", layername, "lw:=", self.arg_with_dim(lw), "endstyle:=", end_style,
                "StartCap:=", start_style, "n:=", len(x), "U:=", self.model_units]
        for a, b in zip(x, y):
            arg2.append("x:=")
            arg2.append(a)
            arg2.append("y:=")
            arg2.append(b)
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
             (Default value = None)

        Returns
        -------

        """
        if type(Value) is str:
            val = Value
        else:
            if sUnits is None:
                sUnits = self.model_units
            val = "{0}{1}".format(Value, sUnits)

        return val