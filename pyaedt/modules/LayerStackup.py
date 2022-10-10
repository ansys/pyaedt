"""
This module contains these classes: `Layer` and `Layers`.

This module provides all layer stackup functionalities for the Circuit and HFSS 3D Layout tools.
"""
from __future__ import absolute_import  # noreorder

from collections import OrderedDict

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


@pyaedt_function_handler()
def _getRGBfromI(value):
    """Retrieve the Integer from a specific layer color.

    Parameters
    ----------
    value : int


    Returns
    -------
    list
    """
    r = (value >> 16) & 0xFF
    g = (value >> 8) & 0xFF
    b = (value >> 0) & 0xFF
    return [r, g, b]


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
        self._color = [255, 0, 0]
        self._transparency = 60
        self.IsVisible = True
        self.IsVisibleShape = True
        self.IsVisiblePath = True
        self.IsVisiblePad = True
        self.IsVisibleHole = True
        self.IsVisibleComponent = True
        self.IsMeshBackgroundMaterial = True
        self.IsMeshOverlay = True
        self._locked = False
        self._topbottom = "neither"
        self._pattern = 1
        self._drawoverride = 0
        self._thickness = 0
        self._lower_elevation = 0
        self._roughness = 0
        self._botroughness = 0
        self._toprounghenss = 0
        self._sideroughness = 0
        self._material = "copper"
        self._fillmaterial = "FR4_epoxy"
        self._index = 1
        self.IsNegative = negative
        # Etch option
        self._useetch = False
        self._etch = 0
        # Rough option
        self._user = False
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
        self._usp = False
        self.hfssSp = {"si": True, "dt": 0, "dtv": 0.1}
        self.planaremSp = {"ifg": False, "vly": False}
        self._zones = None

    @property
    def color(self):
        """Get/Set the property of the active layer. Color it is list of rgb values (0,255).

        Returns
        -------

        """
        return self._color

    @color.setter
    def color(self, val):
        self._color = val

        self.update_stackup_layer()

    @property
    def transparency(self):
        """Get/Set the property to the active layer.

        Returns
        -------
        int
        """
        return self._transparency

    @transparency.setter
    def transparency(self, val):
        self._transparency = val
        self.update_stackup_layer()

    @property
    def is_visible(self):
        """Get/Set the active layer visibility.

        Returns
        -------
        bool
        """
        return self.IsVisible

    @is_visible.setter
    def is_visible(self, val):
        self.IsVisible = val
        self.update_stackup_layer()

    @property
    def is_visible_shape(self):
        """Get/Set the active layer shape visibility.

        Returns
        -------
        bool
        """
        return self.IsVisibleShape

    @is_visible_shape.setter
    def is_visible_shape(self, val):
        self.IsVisibleShape = val
        self.update_stackup_layer()

    @property
    def is_visible_path(self):
        """Get/Set the active layer paths visibility.

        Returns
        -------
        bool
        """
        return self.IsVisiblePath

    @is_visible_path.setter
    def is_visible_path(self, val):
        self.IsVisiblePath = val
        self.update_stackup_layer()

    @property
    def is_visible_pad(self):
        """Get/Set the active layer pad visibility.

        Returns
        -------
        bool
        """
        return self.IsVisiblePad

    @is_visible_pad.setter
    def is_visible_pad(self, val):

        self.IsVisiblePad = val
        self.update_stackup_layer()

    @property
    def is_visible_hole(self):
        """Get/Set the active layer hole visibility.

        Returns
        -------
        bool
        """
        return self.IsVisibleHole

    @is_visible_hole.setter
    def is_visible_hole(self, val):
        self.IsVisibleHole = val
        self.update_stackup_layer()

    @property
    def is_visible_component(self):
        """Get/Set the active layer component visibility.

        Returns
        -------
        bool
        """
        return self.IsVisibleComponent

    @is_visible_component.setter
    def is_visible_component(self, val):
        self.IsVisibleComponent = val
        self.update_stackup_layer()

    @property
    def is_mesh_background(self):
        """Get/Set the active layer mesh backgraound.

        Returns
        -------
        bool
        """
        return self.IsMeshBackgroundMaterial

    @is_mesh_background.setter
    def is_mesh_background(self, val):
        self.IsMeshBackgroundMaterial = val
        self.update_stackup_layer()

    @property
    def is_mesh_overlay(self):
        """Get/Set the active layer mesh overlay.

        Returns
        -------
        bool
        """
        return self.IsMeshOverlay

    @is_mesh_overlay.setter
    def is_mesh_overlay(self, val):
        self.IsMeshOverlay = val
        self.update_stackup_layer()

    @property
    def locked(self):
        """Get/Set the active layer lock flag.

        Returns
        -------
        bool
        """
        return self._locked

    @locked.setter
    def locked(self, val):
        self._locked = val
        self.update_stackup_layer()

    @property
    def top_bottom(self):
        """Get/Set the active layer top bottom alignment.

        Returns
        -------
        str
        """
        return self._topbottom

    @top_bottom.setter
    def top_bottom(self, val):
        self._topbottom = val
        self.update_stackup_layer()

    @property
    def pattern(self):
        """Get/Set the active layer pattern.

        Returns
        -------
        float
        """
        return self._pattern

    @pattern.setter
    def pattern(self, val):
        self._pattern = val
        self.update_stackup_layer()

    @property
    def draw_override(self):
        """Get/Set the active layer draw override value.

        Returns
        -------
        float
        """
        return self._drawoverride

    @draw_override.setter
    def draw_override(self, val):
        self._drawoverride = val
        self.update_stackup_layer()

    @property
    def thickness(self):
        """Get/Set the active layer thickness value.

        Returns
        -------
        float
        """
        return self._thickness

    @thickness.setter
    def thickness(self, val):
        self._thickness = val
        self.update_stackup_layer()

    @property
    def lower_elevation(self):
        """Get/Set the active layer lower elevation.

        Returns
        -------
        float
        """
        return self._lower_elevation

    @lower_elevation.setter
    def lower_elevation(self, val):
        self._lower_elevation = val
        self.update_stackup_layer()

    @property
    def roughness(self):
        """Get/Set the active layer roughness (with units).

        Returns
        -------
        str
        """
        return self._roughness

    @roughness.setter
    def roughness(self, val):
        self._roughness = val
        self.update_stackup_layer()

    @property
    def bottom_roughness(self):
        """Get/Set the active layer bottom roughness (with units).

        Returns
        -------
        str
        """
        return self._botroughness

    @bottom_roughness.setter
    def bottom_roughness(self, val):
        self._botroughness = val
        self.update_stackup_layer()

    @property
    def top_roughness(self):
        """Get/Set the active layer top roughness (with units).

        Returns
        -------
        str
        """
        return self._toprounghenss

    @top_roughness.setter
    def top_roughness(self, val):
        self._toprounghenss = val
        self.update_stackup_layer()

    @property
    def side_roughness(self):
        """Get/Set the active layer side roughness (with units).

        Returns
        -------
        str
        """
        return self._sideroughness

    @side_roughness.setter
    def side_roughness(self, val):
        self._sideroughness = val
        self.update_stackup_layer()

    @property
    def material(self):
        """Get/Set the active layer material name.

        Returns
        -------
        str
        """
        return self._material

    @material.setter
    def material(self, val):
        self._material = val
        self.update_stackup_layer()

    @property
    def fill_material(self):
        """Get/Set the active layer filling material.

        Returns
        -------
        str
        """
        return self._fillmaterial

    @fill_material.setter
    def fill_material(self, val):
        self._fillmaterial = val
        self.update_stackup_layer()

    @property
    def index(self):
        """Get/Set the active layer index.

        Returns
        -------
        int
        """
        return self._index

    @index.setter
    def index(self, val):
        self._index = val
        self.update_stackup_layer()

    @property
    def is_negative(self):
        """Get/Set the active layer negative flag. When `True` the layer will be negative.

        Returns
        -------
        bool
        """
        return self.IsNegative

    @is_negative.setter
    def is_negative(self, val):
        self.IsNegative = val
        self.update_stackup_layer()

    @property
    def use_etch(self):
        """Get/Set the active layer etiching flag. When `True` the layer will use etch.

        Returns
        -------
        bool
        """
        return self._useetch

    @use_etch.setter
    def use_etch(self, val):
        self._useetch = val
        self.update_stackup_layer()

    @property
    def etch(self):
        """Get/Set the active layer etch value.

        Returns
        -------
        float
        """
        return self._etch

    @etch.setter
    def etch(self, val):
        self._etch = val
        self.update_stackup_layer()

    @property
    def user(self):
        """Get/Set the active layer user flag.

        Returns
        -------
        bool
        """
        return self._user

    @user.setter
    def user(self, val):
        self._user = val
        self.update_stackup_layer()

    @property
    def top_roughness_model(self):
        """Get/Set the active layer top roughness model.

        Returns
        -------
        str
        """
        return self.RMdl

    @top_roughness_model.setter
    def top_roughness_model(self, val):
        self.RMdl = val
        self.update_stackup_layer()

    @property
    def top_nodule_radius(self):
        """Get/Set the active layer top roughness radius.

        Returns
        -------
        float
        """
        return self.NR

    @top_nodule_radius.setter
    def top_nodule_radius(self, val):

        self.NR = val
        self.update_stackup_layer()

    @property
    def top_huray_ratio(self):
        """Get/Set the active layer top roughness ratio.

        Returns
        -------
        float
        """
        return self.HRatio

    @top_huray_ratio.setter
    def top_huray_ratio(self, val):
        self.HRatio = val
        self.update_stackup_layer()

    @property
    def bottom_roughness_model(self):
        """Get/Set the active layer bottom roughness model.

        Returns
        -------
        str
        """
        return self.BRMdl

    @bottom_roughness_model.setter
    def bottom_roughness_model(self, val):
        self.BRMdl = val
        self.update_stackup_layer()

    @property
    def bottom_nodule_radius(self):
        """Get/Set the active layer bottom roughness radius.

        Returns
        -------
        float
        """
        return self.BNR

    @bottom_nodule_radius.setter
    def bottom_nodule_radius(self, val):

        self.BNR = val
        self.update_stackup_layer()

    @property
    def bottom_huray_ratio(self):
        """Get/Set the active layer bottom roughness ratio.

        Returns
        -------
        float
        """
        return self.BHRatio

    @bottom_huray_ratio.setter
    def bottom_huray_ratio(self, val):
        self.BHRatio = val
        self.update_stackup_layer()

    @property
    def side_model(self):
        """Get/Set the active layer side roughness model.

        Returns
        -------
        str
        """
        return self.SRMdl

    @side_model.setter
    def side_model(self, val):
        self.SRMdl = val
        self.update_stackup_layer()

    @property
    def side_nodule_radius(self):
        """Get/Set the active layer side roughness radius.

        Returns
        -------
        float
        """
        return self.SNR

    @side_nodule_radius.setter
    def side_nodule_radius(self, val):
        self.SNR = val
        self.update_stackup_layer()

    @property
    def side_huray_ratio(self):
        """Get/Set the active layer bottom roughness ratio.

        Returns
        -------
        float
        """
        return self.SHRatio

    @side_huray_ratio.setter
    def side_huray_ratio(self, val):
        self.SHRatio = val
        self.update_stackup_layer()

    @property
    def usp(self):
        """Get/Set the active layer usp flag.

        Returns
        -------
        bool
        """
        return self._usp

    @usp.setter
    def usp(self, val):
        self._usp = val
        self.update_stackup_layer()

    @property
    def hfss_solver_settings(self):
        """Get/Set the active layer hfss solver settings.

        Returns
        -------
        dict
        """
        return self.hfssSp

    @hfss_solver_settings.setter
    def hfss_solver_settings(self, val):
        self.hfssSp = val
        self.update_stackup_layer()

    @property
    def planar_em_solver_settings(self):
        """Get/Set the active layer PlanarEm solver settings.

        Returns
        -------
        dict
        """
        return self.planaremSp

    @planar_em_solver_settings.setter
    def planar_em_solver_settings(self, val):
        self.planaremSp = val
        self.update_stackup_layer()

    @property
    def zones(self):
        """Get/Set the active layer zoness.

        Returns
        -------
        list
        """
        if self._zones is None:
            self._zones = [i for i in self._layers.all_layers if self.name in i and ";" in i]
        return self._zones

    @zones.setter
    def zones(self, val):
        self._zones = val
        self.update_stackup_layer()

    @property
    def oeditor(self):
        """Oeditor Module."""
        return self._layers.oeditor

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
        self.oeditor.AddStackupLayer(self._get_layer_arg)
        infos = self.oeditor.GetLayerInfo(self.name)
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

    @property
    def _get_layer_arg(self):
        if self.type in ["signal", "via", "dielectric"]:
            args = [
                "NAME:stackup layer",
                "Name:=",
                self.name,
            ]
        else:
            args = [
                "NAME:layer",
                "Name:=",
                self.name,
            ]
        if self.id > 0:
            args.extend(
                ["ID:=", self.id],
            )
        if self.type == "signal":
            args.extend(
                [
                    "Type:=",
                    self.type,
                    "Top Bottom:=",
                    self.top_bottom,
                    "Color:=",
                    _getIfromRGB(self.color),
                    "Transparency:=",
                    self.transparency,
                    "Pattern:=",
                    self.pattern,
                    "VisFlag:=",
                    self.visflag,
                    "Locked:=",
                    self.locked,
                    "DrawOverride:=",
                    self.draw_override,
                    "Zones:=",
                    self.zones,
                    [
                        "NAME:Sublayer",
                        "Thickness:=",
                        self.thickness,
                        "LowerElevation:=",
                        self._arg_with_dim(self.lower_elevation, self.LengthUnit),
                        "Roughness:=",
                        self._arg_with_dim(self.roughness, self.LengthUnitRough),
                        "BotRoughness:=",
                        self._arg_with_dim(self.bottom_roughness, self.LengthUnitRough),
                        "SideRoughness:=",
                        self._arg_with_dim(self.top_roughness, self.LengthUnitRough),
                        "Material:=",
                        self.material.lower(),
                        "FillMaterial:=",
                        self.fill_material.lower(),
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
                    self.use_etch,
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
            args.extend(
                [
                    "Type:=",
                    self.type,
                    "Top Bottom:=",
                    self.top_bottom,
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
                    self.draw_override,
                    "Zones:=",
                    self.zones,
                    [
                        "NAME:Sublayer",
                        "Thickness:=",
                        self.thickness,
                        "LowerElevation:=",
                        self.lower_elevation,
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
            args.extend(
                [
                    "Type:=",
                    self.type,
                    "Top Bottom:=",
                    self.top_bottom,
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
                ]
            )
        return args

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
        self.oeditor.ChangeLayer(self._get_layer_arg)
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
        if self.name in self.oeditor.GetStackupLayerNames():
            self.oeditor.RemoveLayer(self.name)
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
        self.lengthUnitRough = roughnessunits
        self.logger = self._app.logger

    @property
    def oeditor(self):
        """Editor.

        References
        ----------

        >>> oEditor = oDesign.SetActiveEditor("Layout")"""
        return self._modeler.oeditor

    @property
    def zones(self):
        """List of all available zones.

        Returns
        -------
        list
        """
        all_layers = list(self._modeler.oeditor.GetStackupLayerNames())
        zones = []
        for lay in all_layers:
            if ";" in lay:
                zones.append(lay.split(";")[0])
        return list(set(zones))

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
        return [i for i in self.oeditor.GetAllLayerNames() if ";" not in i]

    @property
    def drawing_layers(self):
        """All drawing layers.

        Returns
        -------
        list
           List of drawing layers.

        References
        ----------

        >>> oEditor.GetAllLayerNames()
        """

        return [v.name for k, v in self.layers.items() if v.type not in ["signal", "via", "dielectric"]]

    @property
    def stackup_layers(self):
        """All stackup layers.

        Returns
        -------
        list
           List of stackup layers.

        References
        ----------

        >>> oEditor.GetAllLayerNames()
        """

        return [v.name for k, v in self.layers.items() if v.type in ["signal", "via", "dielectric"]]

    @property
    def all_signal_layers(self):
        """All signal layers.

        Returns
        -------
        list
            List of signal layers.
        """

        return [v.name for k, v in self.layers.items() if v.type == "signal"]

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

            if self.layers[layid].type == "dielectric":
                die.append(lay)
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

    @property
    def layers(self):
        """Refresh all layers in the current stackup.

        Returns
        -------
        int
            Number of layers in the current stackup.
        """
        layers = OrderedDict({})
        for el in self.all_layers:
            o = Layer(self, "signal")
            o.name = el
            infos = self.oeditor.GetLayerInfo(el)
            infos = [i.split(": ") for i in infos]
            infosdict = {i[0].strip(): i[1].strip() for i in infos}
            o.id = int(infosdict["LayerId"])
            if infosdict["Type"] == "metalizedsignal":
                o.type = "signal"
                o.IsNegative = True
            else:
                o.type = infosdict["Type"]
                o.IsNegative = False
            o._locked = _str2bool(infosdict["IsLocked"])
            o._top_bottom = infosdict["TopBottomAssociation"].lower()
            o.IsVisible = infosdict["IsVisible"]
            if "IsVisiblePath" in infosdict:
                o.IsVisiblePath = infosdict["IsVisiblePath"]
                o.IsVisiblePad = infosdict["IsVisiblePad"]
                o.IsVisibleComponent = infosdict["IsVisibleComponent"]
                o.IsVisibleShape = infosdict["IsVisibleShape"]
                o.IsVisibleHole = infosdict["IsVisibleHole"]
            o._color = _getRGBfromI(int(infosdict["Color"][:-1]))
            if o.type in ["signal", "dielectric", "via"]:
                o._index = int(infosdict["Index"])
                o._thickness = _conv_number(infosdict["LayerThickness"])
                o._lower_elevation = _conv_number(infosdict["LowerElevation0"])
                o._fillmaterial = infosdict["FillMaterial0"]
                o._material = infosdict["Material0"]
                if "EtchFactor" in infosdict:
                    o._useetch = True
                    o._etch = _conv_number(infosdict["EtchFactor"])
                if "Roughness0 Type" in infosdict:
                    o._user = True
                    o.RMdl = infosdict["Roughness0 Type"]
                    o.NR = infosdict["Roughness0"].split(", ")[0]
                    o.HRatio = _conv_number(infosdict["Roughness0"].split(", ")[1])
                if "BottomRoughness0 Type" in infosdict:
                    o._user = True
                    o.BRMdl = infosdict["BottomRoughness0 Type"]
                    o.BNR = infosdict["BottomRoughness0"].split(", ")[0]
                    o.BHRatio = _conv_number(infosdict["BottomRoughness0"].split(", ")[1])
                if "SideRoughness0 Type" in infosdict:
                    o._user = True
                    o.SRMdl = infosdict["SideRoughness0 Type"]
                    o.SNR = infosdict["SideRoughness0"].split(", ")[0]
                    o.SHRatio = _conv_number(infosdict["SideRoughness0"].split(", ")[1])
            layers[o.id] = o
        return layers

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
        newlayer._thickness = thickness

        if elevation == "0mm":
            el = (
                0
                if list(self.layers.values())[0].type not in ["dielectric", "signal", "via"]
                else "{}+{}".format(
                    list(self.layers.values())[0].lower_elevation, list(self.layers.values())[0].thickness
                )
            )
            if el:
                self._app.variable_manager.set_variable(
                    "pyaedt_evaluator",
                    expression=el,
                    readonly=True,
                    hidden=True,
                )
                newlayer._lower_elevation = self._app.get_evaluated_value("pyaedt_evaluator")
            else:
                newlayer._lower_elevation = "0mm"
        else:
            newlayer._lower_elevation = elevation
        newlayer._material = material
        newlayer.create_stackup_layer()

        return self.layers[newlayer.id]

    @pyaedt_function_handler()
    def change_stackup_type(self, mode="MultiZone", number_zones=3):
        """Change the stackup type between Multizone, Overlap and Laminate.

        Parameters
        ----------
        mode : str, optional
            Stackup type. Default is `"Multizone"`. Options are `"Overlap"` and `"Laminate"`.
        number_zones : int, optional
            Number of zones of multizone. By default all layers will be enabled in all zones.

        Returns
        -------
        bool
            `True` if successful.
        """
        if mode.lower() == "multizone":
            zones = ["NAME:Zones", "Primary"]
            for i in range(number_zones):
                zones.append("Zone{}".format(i + 1))
            args = ["NAME:layers", "Mode:=", "Multizone", zones, ["NAME:pps"]]
        elif mode.lower() == "overlap":
            args = args = ["NAME:layers", "Mode:=", "Overlap", ["NAME:pps"]]
        elif mode.lower() == "laminate":
            args = args = ["NAME:layers", "Mode:=", "Laminate", ["NAME:pps"]]
        else:
            self.logger.error("Stackup mode has to be Multizone, Overlap or Laminate.")
            return False
        for v in list(self.layers.values()):
            if v.type in ["signal", "dielectric"]:
                if mode.lower() == "multizone":
                    v._zones = [i for i in range(number_zones)]
                else:
                    v._zones = []
            args.append(v._get_layer_arg)
        self.oeditor.ChangeLayers(args)
        return True
