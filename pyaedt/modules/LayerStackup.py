"""
This module contains these classes: `Layer` and `Layers`.

This module provides all layer stackup functionalities for the Circuit and HFSS 3D Layout tools.
"""
from __future__ import absolute_import  # noreorder
from pyaedt.generic.general_methods import pyaedt_function_handler


@pyaedt_function_handler()
def _str2bool(str0):
    """Convert a string to a Boolean value.

    Parameters
    ----------
    str0 : str
       String to convert.

    Returns
    -------
    bool
        ``True`` when successful, ``False`` when failed.
    """
    if str0.lower() == "false":
        return False
    elif str0 == "true":
        return True
    else:
        return ""


def _conv_number(number, typen=float):
    """Convert a number.

    Parameters
    ----------
    number
       Number represented a float.

    typen :
         The default is ``float``.

    Returns
    -------

    """
    if typen is float:
        try:
            return float(number)
        except:
            return number
    elif typen is int:
        try:
            return int(number)
        except:
            return number


@pyaedt_function_handler()
def _getIfromRGB(rgb):
    """Retrieve if from a specific layer color.

    Parameters
    ----------
    rgb :


    Returns
    -------

    """
    red = rgb[2]
    green = rgb[1]
    blue = rgb[0]
    RGBint = (red << 16) + (green << 8) + blue
    return RGBint


class Layer(object):
    """Manages the stackup layer.

    Parameters
    ----------
    app : :class:`pyaedt.modules.LayerStackup.Layers`

    layertype : string, optional
        The default is ``"signal"``.
    negative : bool, optional
        Whether the geometry on the layer is cut away
        from the layer. The default is ``False``.

    Examples
    --------
    >>> from pyaedt import Hfss3dLayout
    >>> app = Hfss3dLayout()
    >>> layers = app.modeler.layers["Top"]
    """

    def __init__(self, app, layertype="signal", negative=False):
        self.LengthUnit = app.LengthUnit
        self.LengthUnitRough = app.LengthUnit
        self._layers = app
        self.name = None
        self.type = layertype
        self.id = 0
        self.color = 8026109
        self.transparency = 60
        self.IsVisible = True
        self.IsVisibleShape = True
        self.IsVisiblePath = True
        self.IsVisiblePad = True
        self.IsVisibleHole = True
        self.IsVisibleComponent = True
        self.IsMeshBackgroundMaterial = True
        self.IsMeshOverlay = True
        self.locked = False
        self.topbottom = "neither"
        self.pattern = 1
        self.drawoverride = 0
        self.thickness = 0
        self.lowerelevation = 0
        self.roughness = 0
        self.botroughness = 0
        self.toprounghenss = 0
        self.sideroughness = 0
        self.material = "copper"
        self.fillmaterial = "FR4_epoxy"
        self.index = 1
        self.IsNegative = negative
        # Etch option
        self.useetch = False
        self.etch = 0
        # Rough option
        self.user = False
        self.RMdl = "Huray"
        self.NR = 0.5
        self.HRatio = 2.9
        self.BRMdl = "Huray"
        self.BNR = 0.5
        self.BHRatio = 2.9
        self.SRMdl = "Huray"
        self.SNR = 0.5
        self.SHRatio = 2.9
        # Solver option
        self.usp = False
        self.hfssSp = {"si": True, "dt": 0, "dtv": 0.1}
        self.planaremSp = {"ifg": False, "vly": False}

    @property
    def _oeditor(self):
        return self._layers._oeditor

    @property
    def visflag(self):
        """Visibility flag for objects on the layer."""
        visflag = 0
        if not self.IsVisible:
            visflag = 0
        else:
            if self.IsMeshBackgroundMaterial:
                visflag += 64
            if self.IsMeshOverlay:
                visflag += 32
            if self.IsVisibleShape:
                visflag += 1
            if self.IsVisiblePath:
                visflag += 2
            if self.IsVisiblePad:
                visflag += 4
            if self.IsVisibleHole:
                visflag += 8
            if self.IsVisibleComponent:
                visflag += 16
        return visflag

    @pyaedt_function_handler()
    def set_layer_color(self, r, g, b):
        """Update the color of the layer.

        Parameters
        ----------
        r : int
            Red color value.
        g : int
            Green color value.
        b :  int
            Blue color value.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.

        References
        ----------

        >>> oEditor.ChangeLayer
        """
        rgb = [r, g, b]
        self.color = _getIfromRGB(rgb)
        self.update_stackup_layer()
        return True

    @pyaedt_function_handler()
    def create_stackup_layer(self):
        """Create a stackup layer.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.

        References
        ----------

        >>> oEditor.AddStackupLayer
        """
        self.remove_stackup_layer()
        if self.type == "signal":
            self._oeditor.AddStackupLayer(
                [
                    "NAME:stackup layer",
                    "Name:=",
                    self.name,
                    "Type:=",
                    self.type,
                    "Top Bottom:=",
                    self.topbottom,
                    "Color:=",
                    self.color,
                    "Transparency:=",
                    self.transparency,
                    "Pattern:=",
                    self.pattern,
                    "VisFlag:=",
                    self.visflag,
                    "Locked:=",
                    self.locked,
                    "DrawOverride:=",
                    self.drawoverride,
                    [
                        "NAME:Sublayer",
                        "Thickness:=",
                        self.thickness,
                        "LowerElevation:=",
                        self.lowerelevation,
                        "Roughness:=",
                        self._arg_with_dim(self.roughness, self.LengthUnitRough),
                        "BotRoughness:=",
                        self._arg_with_dim(self.botroughness, self.LengthUnitRough),
                        "SideRoughness:=",
                        self._arg_with_dim(self.toprounghenss, self.LengthUnitRough),
                        "Material:=",
                        self.material.lower(),
                        "FillMaterial:=",
                        self.fillmaterial.lower(),
                    ],
                    "Neg:=",
                    self.IsNegative,
                    "Usp:=",
                    self.usp,
                    [
                        "NAME:Sp",
                        "Sn:=",
                        "HFSS",
                        "Sv:=",
                        "so(si="
                        + str(self.hfssSp["si"]).lower()
                        + " , dt="
                        + str(self.hfssSp["dt"])
                        + ", dtv='"
                        + self._arg_with_dim(self.hfssSp["dtv"])
                        + "')",
                    ],
                    [
                        "NAME:Sp",
                        "Sn:=",
                        "PlanarEM",
                        "Sv:=",
                        "so(ifg="
                        + str(self.planaremSp["ifg"]).lower()
                        + ", vly="
                        + str(self.planaremSp["vly"]).lower()
                        + ")",
                    ],
                    "Etch:=",
                    str(self.etch),
                    "UseEtch:=",
                    self.useetch,
                    "UseR:=",
                    self.user,
                    "RMdl:=",
                    self.RMdl,
                    "NR:=",
                    self._arg_with_dim(self.NR, self.LengthUnitRough),
                    "HRatio:=",
                    str(self.HRatio),
                    "BRMdl:=",
                    self.BRMdl,
                    "BNR:=",
                    self._arg_with_dim(self.BNR, self.LengthUnitRough),
                    "BHRatio:=",
                    str(self.BHRatio),
                    "SRMdl:=",
                    self.SRMdl,
                    "SNR:=",
                    self._arg_with_dim(self.SNR, self.LengthUnitRough),
                    "SHRatio:=",
                    str(self.SHRatio),
                ]
            )
        else:
            self._oeditor.AddStackupLayer(
                [
                    "NAME:stackup layer",
                    "Name:=",
                    self.name,
                    "Type:=",
                    self.type,
                    "Top Bottom:=",
                    self.topbottom,
                    "Color:=",
                    self.color,
                    "Transparency:=",
                    self.transparency,
                    "Pattern:=",
                    self.pattern,
                    "VisFlag:=",
                    self.visflag,
                    "Locked:=",
                    self.locked,
                    "DrawOverride:=",
                    self.drawoverride,
                    [
                        "NAME:Sublayer",
                        "Thickness:=",
                        self.thickness,
                        "LowerElevation:=",
                        self.lowerelevation,
                        "Roughness:=",
                        0,
                        "BotRoughness:=",
                        0,
                        "SideRoughness:=",
                        0,
                        "Material:=",
                        self.material.lower(),
                    ],
                ]
            )
        infos = self._oeditor.GetLayerInfo(self.name)
        infos = [i.split(": ") for i in infos]
        infosdict = {i[0]: i[1] for i in infos}
        self.id = int(infosdict["LayerId"])
        return True

    @pyaedt_function_handler()
    def _arg_with_dim(self, value, units=None):
        """Argument with dimensions.

        Parameters
        ----------
        value :

        units :
             The default is ``None``.

        Returns
        -------

        """
        if isinstance(value, str):
            val = value
        else:
            if units is None:
                units = self.LengthUnit
            val = "{0}{1}".format(value, units)

        return val

    @pyaedt_function_handler()
    def update_stackup_layer(self):
        """Update the stackup layer.

        .. note::
           This method is valid for release 2021 R1 and later.
           This method works only for signal and dielectric layers.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.

        References
        ----------

        >>> oEditor.ChangeLayer
        """
        if self.type == "signal":
            self._oeditor.ChangeLayer(
                [
                    "NAME:SLayer",
                    "Name:=",
                    self.name,
                    "ID:=",
                    self.id,
                    "Type:=",
                    self.type,
                    "Top Bottom:=",
                    self.topbottom,
                    "Color:=",
                    self.color,
                    "Transparency:=",
                    self.transparency,
                    "Pattern:=",
                    self.pattern,
                    "VisFlag:=",
                    self.visflag,
                    "Locked:=",
                    self.locked,
                    "DrawOverride:=",
                    self.drawoverride,
                    "Zones:=",
                    [0],
                    [
                        "NAME:Sublayer",
                        "Thickness:=",
                        self.thickness,
                        "LowerElevation:=",
                        self.lowerelevation,
                        "Roughness:=",
                        self._arg_with_dim(self.roughness, self.LengthUnitRough),
                        "BotRoughness:=",
                        self._arg_with_dim(self.botroughness, self.LengthUnitRough),
                        "SideRoughness:=",
                        self._arg_with_dim(self.toprounghenss, self.LengthUnitRough),
                        "Material:=",
                        self.material.lower(),
                        "FillMaterial:=",
                        self.fillmaterial.lower(),
                    ],
                    "Neg:=",
                    self.IsNegative,
                    "Usp:=",
                    self.usp,
                    [
                        "NAME:Sp",
                        "Sn:=",
                        "HFSS",
                        "Sv:=",
                        "so(si="
                        + str(self.hfssSp["si"]).lower()
                        + " , dt="
                        + str(self.hfssSp["dt"])
                        + ", dtv='"
                        + self._arg_with_dim(self.hfssSp["dtv"])
                        + "')",
                    ],
                    [
                        "NAME:Sp",
                        "Sn:=",
                        "PlanarEM",
                        "Sv:=",
                        "so(ifg="
                        + str(self.planaremSp["ifg"]).lower()
                        + ", vly="
                        + str(self.planaremSp["vly"]).lower()
                        + ")",
                    ],
                    "Etch:=",
                    str(self.etch),
                    "UseEtch:=",
                    self.useetch,
                    "UseR:=",
                    self.user,
                    "RMdl:=",
                    self.RMdl,
                    "NR:=",
                    self._arg_with_dim(self.NR, self.LengthUnitRough),
                    "HRatio:=",
                    str(self.HRatio),
                    "BRMdl:=",
                    self.BRMdl,
                    "BNR:=",
                    self._arg_with_dim(self.BNR, self.LengthUnitRough),
                    "BHRatio:=",
                    str(self.BHRatio),
                    "SRMdl:=",
                    self.SRMdl,
                    "SNR:=",
                    self._arg_with_dim(self.SNR, self.LengthUnitRough),
                    "SHRatio:=",
                    str(self.SHRatio),
                ]
            )
        elif self.type == "dielectric":
            self._oeditor.ChangeLayer(
                [
                    "NAME:SLayer",
                    "Name:=",
                    self.name,
                    "ID:=",
                    self.id,
                    "Type:=",
                    self.type,
                    "Top Bottom:=",
                    self.topbottom,
                    "Color:=",
                    self.color,
                    "Transparency:=",
                    self.transparency,
                    "Pattern:=",
                    self.pattern,
                    "VisFlag:=",
                    self.visflag,
                    "Locked:=",
                    self.locked,
                    "DrawOverride:=",
                    self.drawoverride,
                    "Zones:=",
                    [],
                    [
                        "NAME:Sublayer",
                        "Thickness:=",
                        self.thickness,
                        "LowerElevation:=",
                        self.lowerelevation,
                        "Roughness:=",
                        0,
                        "BotRoughness:=",
                        0,
                        "SideRoughness:=",
                        0,
                        "Material:=",
                        self.material.lower(),
                    ],
                ]
            )
        else:
            return False
        return True

    @pyaedt_function_handler()
    def remove_stackup_layer(self):
        """Remove the stackup layer.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.

        References
        ----------

        >>> oEditor.RemoveLayer
        """
        if self.name in self._oeditor.GetStackupLayerNames():
            self._oeditor.RemoveLayer(self.name)
            return True
        return False


class Layers(object):
    """Manages layers for the Circuit and HFSS 3D Layout tools.

    Parameters
    ----------
    modeler : :class:`pyaedt.modeler.Model3DLayout.Modeler3DLayout`

    roughnessunits : str, optional
       Units for the roughness of layers. The default is ``"um"``.

    Examples
    --------
    >>> from pyaedt import Hfss3dLayout
    >>> app = Hfss3dLayout()
    >>> layers = app.modeler.layers
    """

    def __init__(self, modeler, roughnessunits="um"):
        self._modeler = modeler
        self._app = self._modeler._app
        self._currentId = 0
        self.layers = {}
        self.lengthUnitRough = roughnessunits
        self.logger = self._app.logger

    @property
    def _oeditor(self):
        """Editor.

        References
        ----------

        >>> oEditor = oDesign.SetActiveEditor("Layout")"""
        return self._modeler._app._odesign.SetActiveEditor("Layout")

    @property
    def LengthUnit(self):
        """Length units."""
        return self._modeler.model_units

    @property
    def all_layers(self):
        """All stackup layers.

        Returns
        -------
        list
           List of stackup layers.

        References
        ----------

        >>> oEditor.GetStackupLayerNames()
        """
        return self._oeditor.GetStackupLayerNames()

    @property
    def drawing_layers(self):
        """All drawing layers.

        Returns
        -------
        list
           List of stackup layers.

        References
        ----------

        >>> oEditor.GetAllLayerNames()
        """
        stackup = self.all_layers
        return [i for i in list(self._oeditor.GetAllLayerNames()) if i not in stackup]

    @property
    def all_signal_layers(self):
        """All signal layers.

        Returns
        -------
        list
            List of signal layers.
        """
        a = self.all_layers
        sig = []
        for lay in a:
            layid = self.layer_id(lay)
            if layid not in self.layers:
                self.refresh_all_layers()
            if self.layers[layid].type == "signal":
                sig.append(lay)
        return sig

    @property
    def all_diel_layers(self):
        """All dielectric layers.

        Returns
        -------
        list
            List of dielectric layers.
        """
        a = self.all_layers
        die = []
        for lay in a:
            layid = self.layer_id(lay)

            if layid not in self.layers:
                self.refresh_all_layers()
            if self.layers[layid].type == "dielectric":
                die.append(layid)
        return die

    @pyaedt_function_handler()
    def layer_id(self, name):
        """Retrieve a layer ID.

        Parameters
        ----------
        name :  str
            Name of the layer.

        Returns
        -------
        type
            Layer ID if the layer name exists.
        """
        for el in self.layers:
            if self.layers[el].name == name:
                return el
        return None

    @pyaedt_function_handler()
    def refresh_all_layers(self):
        """Refresh all layers in the current stackup.

        Returns
        -------
        int
            Number of layers in the current stackup.
        """
        layernames = self._oeditor.GetStackupLayerNames()
        for el in layernames:
            o = Layer(self, "signal")
            o.name = el
            infos = self._oeditor.GetLayerInfo(el)
            infos = [i.split(": ") for i in infos]
            infosdict = {i[0].strip(): i[1].strip() for i in infos}
            if infosdict["Type"] == "metalizedsignal":
                o.type = "signal"
            else:
                o.type = infosdict["Type"]
            o.locked = _str2bool(infosdict["IsLocked"])
            o.id = int(infosdict["LayerId"])
            o.topbottom = infosdict["TopBottomAssociation"].lower()
            o.IsVisible = infosdict["IsVisible"]
            if "IsVisiblePath" in infosdict:
                o.IsVisiblePath = infosdict["IsVisiblePath"]
                o.IsVisiblePad = infosdict["IsVisiblePad"]
                o.IsVisibleComponent = infosdict["IsVisibleComponent"]
                o.IsVisibleShape = infosdict["IsVisibleShape"]
                o.IsVisibleHole = infosdict["IsVisibleHole"]
            o.color = int(infosdict["Color"][:-1])
            o.index = int(infosdict["Index"])
            o.thickness = _conv_number(infosdict["LayerThickness"])
            o.lowerelevation = _conv_number(infosdict["LowerElevation0"])
            o.fillmaterial = infosdict["FillMaterial0"]
            o.material = infosdict["Material0"]
            if "EtchFactor" in infosdict:
                o.useetch = True
                o.etch = _conv_number(infosdict["EtchFactor"])
            if "Roughness0 Type" in infosdict:
                o.user = True
                o.RMdl = infosdict["Roughness0 Type"]
                o.NR = infosdict["Roughness0"].split(", ")[0]
                o.HRatio = _conv_number(infosdict["Roughness0"].split(", ")[1])
            if "BottomRoughness0 Type" in infosdict:
                o.user = True
                o.BRMdl = infosdict["BottomRoughness0 Type"]
                o.BNR = infosdict["BottomRoughness0"].split(", ")[0]
                o.BHRatio = _conv_number(infosdict["BottomRoughness0"].split(", ")[1])
            if "SideRoughness0 Type" in infosdict:
                o.user = True
                o.SRMdl = infosdict["SideRoughness0 Type"]
                o.SNR = infosdict["SideRoughness0"].split(", ")[0]
                o.SHRatio = _conv_number(infosdict["SideRoughness0"].split(", ")[1])

            if o.id in self.layers:  # updating the existing one
                layer = self.layers[o.id]
                layer.name = o.name
                layer.type = o.type
                layer.locked = o.locked
                layer.topbottom = o.topbottom
                layer.IsVisible = o.IsVisible
                layer.IsVisiblePath = o.IsVisiblePath
                layer.IsVisiblePad = o.IsVisiblePad
                layer.IsVisibleComponent = o.IsVisibleComponent
                layer.IsVisibleShape = o.IsVisibleShape
                layer.IsVisibleHole = o.IsVisibleHole
                layer.color = o.color
                layer.index = o.index
                layer.thickness = o.thickness
                layer.lowerelevation = o.lowerelevation
                layer.fillmaterial = o.fillmaterial
                layer.material = o.material
                layer.useetch = o.useetch
                layer.etch = o.etch
                layer.user = o.user
                layer.RMdl = o.RMdl
                layer.NR = o.NR
                layer.HRatio = o.HRatio
                layer.BRMdl = o.BRMdl
                layer.BNR = o.BNR
                layer.BHRatio = o.BHRatio
                layer.SRMdl = o.SRMdl
                layer.SNR = o.SNR
                layer.SHRatio = o.SHRatio
            else:  # creating the new layer
                self.layers[o.id] = o
        return len(self.layers)

    @pyaedt_function_handler()
    def add_layer(
        self, layername, layertype="signal", thickness="0mm", elevation="0mm", material="copper", isnegative=False
    ):
        """Add a layer.

        Parameters
        ----------
        layername : str
            Name of the layer.
        layertype : str, optional
            Type of the layer. The default is ``"signal"``.
        thickness : str, optional
            Thickness with units. The default is ``"0mm"``.
        elevation : str, optional
            Elevation with units. The default is ``"0mm"``.
        material : str, optional
            Name of the material. The default is ``"copper"``.
        isnegative : bool, optional
            If ``True``, the geometry on the layer is cut away from the layer. The default is ``False``.

        Returns
        -------
        :class:`pyaedt.modules.LayerStackup.Layer`
            Layer object.
        """
        newlayer = Layer(self, layertype, isnegative)
        newlayer.name = layername
        newlayer.thickness = thickness
        newlayer.lowerelevation = elevation
        newlayer.material = material
        newlayer.create_stackup_layer()
        self.layers[newlayer.id] = newlayer
        return self.layers[newlayer.id]
