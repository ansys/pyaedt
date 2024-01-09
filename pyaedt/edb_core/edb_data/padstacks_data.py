from collections import OrderedDict
import math
import re
import warnings

from pyaedt import is_ironpython
from pyaedt.edb_core.dotnet.database import PolygonDataDotNet
from pyaedt.edb_core.edb_data.edbvalue import EdbValue
from pyaedt.edb_core.edb_data.primitives_data import EDBPrimitivesMain
from pyaedt.edb_core.general import PadGeometryTpe
from pyaedt.edb_core.general import convert_py_list_to_net_list
from pyaedt.generic.clr_module import String
from pyaedt.generic.clr_module import _clr
from pyaedt.generic.general_methods import generate_unique_name
from pyaedt.generic.general_methods import pyaedt_function_handler
from pyaedt.modeler.geometry_operators import GeometryOperators


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
    >>> edb_pad_properties = edb.padstacks.definitions["MyPad"].pad_by_layer["TOP"]
    """

    def __init__(self, edb_padstack, layer_name, pad_type, p_edb_padstack):
        self._edb_padstack = edb_padstack
        self._pedbpadstack = p_edb_padstack
        self.layer_name = layer_name
        self.pad_type = pad_type

    @property
    def _padstack_methods(self):
        return self._pedbpadstack._padstack_methods

    @property
    def _stackup_layers(self):
        return self._pedbpadstack._stackup_layers

    @property
    def _edb(self):
        return self._pedbpadstack._edb

    def _get_edb_value(self, value):
        return self._pedbpadstack._get_edb_value(value)

    @property
    def _pad_parameter_value(self):
        pad_params = self._edb_padstack.GetData().GetPadParametersValue(
            self.layer_name, self.int_to_pad_type(self.pad_type)
        )
        return pad_params

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
    def shape(self):
        """Get the shape of the pad."""
        return self._pad_parameter_value[1].ToString()

    @shape.setter
    def shape(self, value):
        self._update_pad_parameters_parameters(geom_type=PadGeometryTpe[value].value)

    @property
    def parameters_values(self):
        """Parameters.

        Returns
        -------
        list
            List of parameters.
        """
        return [i.tofloat for i in self.parameters.values()]

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
            if pad_values[1]:
                return PolygonDataDotNet(self._edb._app, pad_values[1])
            else:
                return
        except:
            return

    @property
    def parameters(self):
        """Get parameters.

        Returns
        -------
        dict
        """
        value = list(self._pad_parameter_value[2])
        if self.shape == PadGeometryTpe.Circle.name:
            return OrderedDict({"Diameter": EdbValue(value[0])})
        elif self.shape == PadGeometryTpe.Square.name:
            return OrderedDict({"Size": EdbValue(value[0])})
        elif self.shape == PadGeometryTpe.Rectangle.name:
            return OrderedDict({"XSize": EdbValue(value[0]), "YSize": EdbValue(value[1])})
        elif self.shape in [PadGeometryTpe.Oval.name, PadGeometryTpe.Bullet.name]:
            return OrderedDict(
                {"XSize": EdbValue(value[0]), "YSize": EdbValue(value[1]), "CornerRadius": EdbValue(value[2])}
            )
        elif self.shape == PadGeometryTpe.NSidedPolygon.name:
            return OrderedDict({"Size": EdbValue(value[0]), "NumSides": EdbValue(value[1])})
        elif self.shape in [PadGeometryTpe.Round45.name, PadGeometryTpe.Round90.name]:  # pragma: no cover
            return OrderedDict(
                {"Inner": EdbValue(value[0]), "ChannelWidth": EdbValue(value[1]), "IsolationGap": EdbValue(value[2])}
            )
        else:
            return OrderedDict()  # pragma: no cover

    @parameters.setter
    def parameters(self, value):
        """Set parameters.
        "Circle", {"Diameter": "0.5mm"}

        Parameters
        ----------
        value : dict
            Pad parameters in dictionary.
        >>> pad = Edb.padstacks["PlanarEMVia"]["TOP"]
        >>> pad.shape = "Circle"
        >>> pad.pad_parameters{"Diameter": "0.5mm"}
        >>> pad.shape = "Bullet"
        >>> pad.pad_parameters{"XSize": "0.5mm", "YSize": "0.5mm"}
        """

        if isinstance(value, dict):
            value = {k: v.tostring if isinstance(v, EdbValue) else v for k, v in value.items()}
            if self.shape == PadGeometryTpe.Circle.name:
                params = [self._get_edb_value(value["Diameter"])]
            elif self.shape == PadGeometryTpe.Square.name:
                params = [self._get_edb_value(value["Size"])]
            elif self.shape == PadGeometryTpe.Rectangle.name:
                params = [self._get_edb_value(value["XSize"]), self._get_edb_value(value["YSize"])]
            elif self.shape == [PadGeometryTpe.Oval.name, PadGeometryTpe.Bullet.name]:
                params = [
                    self._get_edb_value(value["XSize"]),
                    self._get_edb_value(value["YSize"]),
                    self._get_edb_value(value["CornerRadius"]),
                ]
            elif self.shape in [PadGeometryTpe.Round45.name, PadGeometryTpe.Round90.name]:  # pragma: no cover
                params = [
                    self._get_edb_value(value["Inner"]),
                    self._get_edb_value(value["ChannelWidth"]),
                    self._get_edb_value(value["IsolationGap"]),
                ]
            else:  # pragma: no cover
                params = None
        elif isinstance(value, list):
            params = [self._get_edb_value(i) for i in value]
        else:
            params = [self._get_edb_value(value)]
        self._update_pad_parameters_parameters(params=params)

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
        newPadstackDefinitionData = self._edb.definition.PadstackDefData(originalPadstackDefinitionData)
        if not pad_type:
            pad_type = self.pad_type
        if not geom_type:
            geom_type = self.geometry_type
        if params:
            params = convert_py_list_to_net_list(params)
        else:
            params = self._pad_parameter_value[2]
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
            params,
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
    >>> edb_padstack = edb.padstacks.definitions["MyPad"]
    """

    def __init__(self, edb_padstack, ppadstack):
        self.edb_padstack = edb_padstack
        self._ppadstack = ppadstack
        self.pad_by_layer = {}
        self.antipad_by_layer = {}
        self.thermalpad_by_layer = {}
        self._bounding_box = []
        self._hole_params = None
        for layer in self.via_layers:
            self.pad_by_layer[layer] = EDBPadProperties(edb_padstack, layer, 0, self)
            self.antipad_by_layer[layer] = EDBPadProperties(edb_padstack, layer, 1, self)
            self.thermalpad_by_layer[layer] = EDBPadProperties(edb_padstack, layer, 2, self)
        pass

    @property
    def instances(self):
        """Definitions Instances."""
        name = self.name
        return [i for i in self._ppadstack.instances.values() if i.padstack_definition == name]

    @property
    def name(self):
        """Padstack Definition Name."""
        return self.edb_padstack.GetName()

    @property
    def _padstack_methods(self):
        return self._ppadstack._padstack_methods

    @property
    def _stackup_layers(self):
        return self._ppadstack._stackup_layers

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
    def hole_params(self):
        """Via Hole parameters values."""

        viaData = self.edb_padstack.GetData()
        self._hole_params = viaData.GetHoleParametersValue()
        return self._hole_params

    @property
    def hole_parameters(self):
        """Hole parameters.

        Returns
        -------
        list
            List of the hole parameters.
        """
        self._hole_parameters = self.hole_params[2]
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
        newPadstackDefinitionData = self._edb.definition.PadstackDefData(originalPadstackDefinitionData)
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
        self._hole_properties = [i.ToDouble() for i in self.hole_params[2]]
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
        self._hole_type = self.hole_params[1]
        return self._hole_type

    @property
    def hole_offset_x(self):
        """Hole offset for the X axis.

        Returns
        -------
        str
            Hole offset value for the X axis.
        """
        self._hole_offset_x = self.hole_params[3].ToString()
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
        self._hole_offset_y = self.hole_params[4].ToString()
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
        self._hole_rotation = self.hole_params[5].ToString()
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
        return self._edb.definition.PadstackDefData(self.edb_padstack.GetData()).GetHolePlatingPercentage()

    @hole_plating_ratio.setter
    def hole_plating_ratio(self, ratio):
        originalPadstackDefinitionData = self.edb_padstack.GetData()
        newPadstackDefinitionData = self._edb.definition.PadstackDefData(originalPadstackDefinitionData)
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
        newPadstackDefinitionData = self._edb.definition.PadstackDefData(originalPadstackDefinitionData)
        newPadstackDefinitionData.SetMaterial(materialname)
        self.edb_padstack.SetData(newPadstackDefinitionData)

    @property
    def padstack_instances(self):
        """Get all the vias that belongs to active Padstack definition.

        Returns
        -------
        dict
        """
        return {
            id: via for id, via in self._ppadstack.padstack_instances.items() if via.padstack_definition == self.name
        }

    @property
    def hole_range(self):
        """Get hole range value from padstack definition.

        Returns
        -------
        str
            Possible returned values are ``"through"``, ``"begin_on_upper_pad"``,
            ``"end_on_lower_pad"``, ``"upper_pad_to_lower_pad"``, and ``"undefined"``.
        """
        cloned_padstackdef_data = self._edb.definition.PadstackDefData(self.edb_padstack.GetData())
        hole_ange_type = int(cloned_padstackdef_data.GetHoleRange())
        if hole_ange_type == 0:  # pragma no cover
            return "through"
        elif hole_ange_type == 1:  # pragma no cover
            return "begin_on_upper_pad"
        elif hole_ange_type == 2:  # pragma no cover
            return "end_on_lower_pad"
        elif hole_ange_type == 3:  # pragma no cover
            return "upper_pad_to_lower_pad"
        else:  # pragma no cover
            return "undefined"

    @hole_range.setter
    def hole_range(self, value):
        if isinstance(value, str):  # pragma no cover
            cloned_padstackdef_data = self._edb.definition.PadstackDefData(self.edb_padstack.GetData())
            if value == "through":  # pragma no cover
                cloned_padstackdef_data.SetHoleRange(self._edb.definition.PadstackHoleRange.Through)
            elif value == "begin_on_upper_pad":  # pragma no cover
                cloned_padstackdef_data.SetHoleRange(self._edb.definition.PadstackHoleRange.BeginOnUpperPad)
            elif value == "end_on_lower_pad":  # pragma no cover
                cloned_padstackdef_data.SetHoleRange(self._edb.definition.PadstackHoleRange.EndOnLowerPad)
            elif value == "upper_pad_to_lower_pad":  # pragma no cover
                cloned_padstackdef_data.SetHoleRange(self._edb.definition.PadstackHoleRange.UpperPadToLowerPad)
            else:  # pragma no cover
                return
            self.edb_padstack.SetData(cloned_padstackdef_data)

    @pyaedt_function_handler()
    def convert_to_3d_microvias(self, convert_only_signal_vias=True, hole_wall_angle=15, delete_padstack_def=True):
        """Convert actual padstack instance to microvias 3D Objects with a given aspect ratio.

        Parameters
        ----------
        convert_only_signal_vias : bool, optional
            Either to convert only vias belonging to signal nets or all vias. Defaults is ``True``.
        hole_wall_angle : float, optional
            Angle of laser penetration in degrees. The angle defines the bottom hole diameter with this formula:
            HoleDiameter -2*tan(laser_angle* Hole depth). Hole depth is the height of the via (dielectric thickness).
            The default is ``15``.
            The bottom hole is ``0.75*HoleDepth/HoleDiam``.
        delete_padstack_def : bool, optional
            Whether to delete the padstack definition. The default is ``True``.
            If ``False``, the padstack definition is not deleted and the hole size is set to zero.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.
        """

        if len(self.hole_properties) == 0:
            self._ppadstack._pedb.logger.error("Microvias cannot be applied on vias using hole shape polygon")
            return False

        if self.via_start_layer == self.via_stop_layer:
            self._ppadstack._pedb.logger.error("Microvias cannot be applied when Start and Stop Layers are the same.")
        layout = self._ppadstack._pedb.active_layout
        layers = self._ppadstack._pedb.stackup.signal_layers
        layer_names = [i for i in list(layers.keys())]
        if convert_only_signal_vias:
            signal_nets = [i for i in list(self._ppadstack._pedb.nets.signal_nets.keys())]
        topl, topz, bottoml, bottomz = self._ppadstack._pedb.stackup.stackup_limits(True)
        try:
            start_elevation = layers[self.via_start_layer].lower_elevation
        except KeyError:  # pragma: no cover
            start_elevation = layers[self.instances[0].start_layer].lower_elevation
        try:
            stop_elevation = layers[self.via_start_layer].upper_elevation
        except KeyError:  # pragma: no cover
            stop_elevation = layers[self.instances[0].stop_layer].upper_elevation

        diel_thick = abs(start_elevation - stop_elevation)
        rad1 = self.hole_properties[0] / 2
        rad2 = self.hole_properties[0] / 2 - math.tan(hole_wall_angle * diel_thick * math.pi / 180)

        if start_elevation < (topz + bottomz) / 2:
            rad1, rad2 = rad2, rad1
        i = 0
        for via in list(self.padstack_instances.values()):
            if convert_only_signal_vias and via.net_name in signal_nets or not convert_only_signal_vias:
                pos = via.position
                started = False
                if len(self.pad_by_layer[self.via_start_layer].parameters) == 0:
                    self._edb.cell.primitive.polygon.create(
                        layout,
                        self.via_start_layer,
                        via._edb_padstackinstance.GetNet(),
                        self.pad_by_layer[self.via_start_layer].polygon_data.edb_api,
                    )
                else:
                    self._edb.cell.primitive.circle.create(
                        layout,
                        self.via_start_layer,
                        via._edb_padstackinstance.GetNet(),
                        self._get_edb_value(pos[0]),
                        self._get_edb_value(pos[1]),
                        self._get_edb_value(self.pad_by_layer[self.via_start_layer].parameters_values[0] / 2),
                    )
                if len(self.pad_by_layer[self.via_stop_layer].parameters) == 0:
                    self._edb.cell.primitive.polygon.create(
                        layout,
                        self.via_stop_layer,
                        via._edb_padstackinstance.GetNet(),
                        self.pad_by_layer[self.via_stop_layer].polygon_data.edb_api,
                    )
                else:
                    self._edb.cell.primitive.circle.create(
                        layout,
                        self.via_stop_layer,
                        via._edb_padstackinstance.GetNet(),
                        self._get_edb_value(pos[0]),
                        self._get_edb_value(pos[1]),
                        self._get_edb_value(self.pad_by_layer[self.via_stop_layer].parameters_values[0] / 2),
                    )
                for layer_name in layer_names:
                    stop = ""
                    if layer_name == via.start_layer or started:
                        start = layer_name
                        stop = layer_names[layer_names.index(layer_name) + 1]
                        cloned_circle = self._edb.cell.primitive.circle.create(
                            layout,
                            start,
                            via._edb_padstackinstance.GetNet(),
                            self._get_edb_value(pos[0]),
                            self._get_edb_value(pos[1]),
                            self._get_edb_value(rad1),
                        )
                        cloned_circle2 = self._edb.cell.primitive.circle.create(
                            layout,
                            stop,
                            via._edb_padstackinstance.GetNet(),
                            self._get_edb_value(pos[0]),
                            self._get_edb_value(pos[1]),
                            self._get_edb_value(rad2),
                        )
                        s3d = self._edb.cell.hierarchy._hierarchy.Structure3D.Create(
                            layout, generate_unique_name("via3d_" + via.aedt_name.replace("via_", ""), n=3)
                        )
                        s3d.AddMember(cloned_circle.prim_obj)
                        s3d.AddMember(cloned_circle2.prim_obj)
                        s3d.SetMaterial(self.material)
                        s3d.SetMeshClosureProp(self._edb.cell.hierarchy._hierarchy.Structure3D.TClosure.EndsClosed)
                        started = True
                        i += 1
                    if stop == via.stop_layer:
                        break
                if delete_padstack_def:  # pragma no cover
                    via.delete()
                else:  # pragma no cover
                    padstack_def = self._ppadstack.definitions[via.padstack_definition]
                    padstack_def.hole_properties = 0
                    self._ppadstack._pedb.logger.info("Padstack definition kept, hole size set to 0.")

        self._ppadstack._pedb.logger.info("{} Converted successfully to 3D Objects.".format(i))
        return True

    @pyaedt_function_handler()
    def split_to_microvias(self):
        """Convert actual padstack definition to multiple microvias definitions.

        Returns
        -------
        List of :class:`pyaedt.edb_core.padstackEDBPadstack`
        """
        if self.via_start_layer == self.via_stop_layer:
            self._ppadstack._pedb.logger.error("Microvias cannot be applied when Start and Stop Layers are the same.")
        layout = self._ppadstack._pedb.active_layout
        layers = self._ppadstack._pedb.stackup.signal_layers
        layer_names = [i for i in list(layers.keys())]
        if abs(layer_names.index(self.via_start_layer) - layer_names.index(self.via_stop_layer)) < 2:
            self._ppadstack._pedb.logger.error(
                "Conversion can be applied only if Padstack definition is composed by more than 2 layers."
            )
            return False
        started = False
        p1 = self.edb_padstack.GetData()
        new_instances = []
        for layer_name in layer_names:
            stop = ""
            if layer_name == self.via_start_layer or started:
                start = layer_name
                stop = layer_names[layer_names.index(layer_name) + 1]
                new_padstack_name = "MV_{}_{}_{}".format(self.name, start, stop)
                included = [start, stop]
                new_padstack_definition_data = self._ppadstack._pedb.edb_api.definition.PadstackDefData.Create()
                new_padstack_definition_data.AddLayers(convert_py_list_to_net_list(included))
                for layer in included:
                    pl = self.pad_by_layer[layer]
                    new_padstack_definition_data.SetPadParameters(
                        layer,
                        self._ppadstack._pedb.edb_api.definition.PadType.RegularPad,
                        pl.int_to_geometry_type(pl.geometry_type),
                        list(
                            pl._edb_padstack.GetData().GetPadParametersValue(
                                pl.layer_name, pl.int_to_pad_type(pl.pad_type)
                            )
                        )[2],
                        pl._edb_padstack.GetData().GetPadParametersValue(
                            pl.layer_name, pl.int_to_pad_type(pl.pad_type)
                        )[3],
                        pl._edb_padstack.GetData().GetPadParametersValue(
                            pl.layer_name, pl.int_to_pad_type(pl.pad_type)
                        )[4],
                        pl._edb_padstack.GetData().GetPadParametersValue(
                            pl.layer_name, pl.int_to_pad_type(pl.pad_type)
                        )[5],
                    )
                    pl = self.antipad_by_layer[layer]
                    new_padstack_definition_data.SetPadParameters(
                        layer,
                        self._ppadstack._pedb.edb_api.definition.PadType.AntiPad,
                        pl.int_to_geometry_type(pl.geometry_type),
                        list(
                            pl._edb_padstack.GetData().GetPadParametersValue(
                                pl.layer_name, pl.int_to_pad_type(pl.pad_type)
                            )
                        )[2],
                        pl._edb_padstack.GetData().GetPadParametersValue(
                            pl.layer_name, pl.int_to_pad_type(pl.pad_type)
                        )[3],
                        pl._edb_padstack.GetData().GetPadParametersValue(
                            pl.layer_name, pl.int_to_pad_type(pl.pad_type)
                        )[4],
                        pl._edb_padstack.GetData().GetPadParametersValue(
                            pl.layer_name, pl.int_to_pad_type(pl.pad_type)
                        )[5],
                    )
                    pl = self.thermalpad_by_layer[layer]
                    new_padstack_definition_data.SetPadParameters(
                        layer,
                        self._ppadstack._pedb.edb_api.definition.PadType.ThermalPad,
                        pl.int_to_geometry_type(pl.geometry_type),
                        list(
                            pl._edb_padstack.GetData().GetPadParametersValue(
                                pl.layer_name, pl.int_to_pad_type(pl.pad_type)
                            )
                        )[2],
                        pl._edb_padstack.GetData().GetPadParametersValue(
                            pl.layer_name, pl.int_to_pad_type(pl.pad_type)
                        )[3],
                        pl._edb_padstack.GetData().GetPadParametersValue(
                            pl.layer_name, pl.int_to_pad_type(pl.pad_type)
                        )[4],
                        pl._edb_padstack.GetData().GetPadParametersValue(
                            pl.layer_name, pl.int_to_pad_type(pl.pad_type)
                        )[5],
                    )
                new_padstack_definition_data.SetHoleParameters(
                    self.hole_type,
                    self.hole_parameters,
                    self._get_edb_value(self.hole_offset_x),
                    self._get_edb_value(self.hole_offset_y),
                    self._get_edb_value(self.hole_rotation),
                )
                new_padstack_definition_data.SetMaterial(self.material)
                new_padstack_definition_data.SetHolePlatingPercentage(self._get_edb_value(self.hole_plating_ratio))
                padstack_definition = self._edb.definition.PadstackDef.Create(
                    self._ppadstack._pedb.active_db, new_padstack_name
                )
                padstack_definition.SetData(new_padstack_definition_data)
                new_instances.append(EDBPadstack(padstack_definition, self._ppadstack))
                started = True
            if self.via_stop_layer == stop:
                break
        i = 0
        for via in list(self.padstack_instances.values()):
            for inst in new_instances:
                instance = inst.edb_padstack
                from_layer = [
                    l
                    for l in self._ppadstack._pedb.stackup._edb_layer_list
                    if l.GetName() == list(instance.GetData().GetLayerNames())[0]
                ][0]
                to_layer = [
                    l
                    for l in self._ppadstack._pedb.stackup._edb_layer_list
                    if l.GetName() == list(instance.GetData().GetLayerNames())[-1]
                ][0]
                padstack_instance = self._edb.cell.primitive.padstack_instance.create(
                    layout,
                    via._edb_padstackinstance.GetNet(),
                    generate_unique_name(instance.GetName()),
                    instance,
                    via._edb_padstackinstance.GetPositionAndRotationValue()[1],
                    via._edb_padstackinstance.GetPositionAndRotationValue()[2],
                    from_layer,
                    to_layer,
                    None,
                    None,
                )
                padstack_instance.SetIsLayoutPin(via.is_pin)
                i += 1
            via.delete()
        self._ppadstack._pedb.logger.info("Created {} new microvias.".format(i))
        return new_instances

    @pyaedt_function_handler()
    def _update_layer_names(self, old_name, updated_name):
        """Update padstack definition layer name when layer name is edited with the layer name setter.

        Parameters
        ----------
        old_name
            old name : str
        updated_name
            new name : str

        Returns
        -------
        bool
            ``True`` when succeed ``False`` when failed.

        """
        cloned_padstack_data = self._edb.definition.PadstackDefData(self.edb_padstack.GetData())
        new_padstack_data = self._edb.definition.PadstackDefData.Create()
        layers_name = cloned_padstack_data.GetLayerNames()
        layers_to_add = []
        for layer in layers_name:
            if layer == old_name:
                layers_to_add.append(updated_name)
            else:
                layers_to_add.append(layer)
        new_padstack_data.AddLayers(convert_py_list_to_net_list(layers_to_add))
        for layer in layers_name:
            updated_pad = self.pad_by_layer[layer]
            if not updated_pad.geometry_type == 0:  # pragma no cover
                pad_type = self._edb.definition.PadType.RegularPad
                geom_type = self.pad_by_layer[layer]._pad_parameter_value[1]
                parameters = self.pad_by_layer[layer]._pad_parameter_value[2]
                offset_x = self.pad_by_layer[layer]._pad_parameter_value[3]
                offset_y = self.pad_by_layer[layer]._pad_parameter_value[4]
                rot = self.pad_by_layer[layer]._pad_parameter_value[5]
                if layer == old_name:  # pragma no cover
                    new_padstack_data.SetPadParameters(
                        updated_name, pad_type, geom_type, parameters, offset_x, offset_y, rot
                    )
                else:
                    new_padstack_data.SetPadParameters(layer, pad_type, geom_type, parameters, offset_x, offset_y, rot)

            updated_anti_pad = self.antipad_by_layer[layer]
            if not updated_anti_pad.geometry_type == 0:  # pragma no cover
                pad_type = self._edb.definition.PadType.AntiPad
                geom_type = self.pad_by_layer[layer]._pad_parameter_value[1]
                parameters = self.pad_by_layer[layer]._pad_parameter_value[2]
                offset_x = self.pad_by_layer[layer]._pad_parameter_value[3]
                offset_y = self.pad_by_layer[layer]._pad_parameter_value[4]
                rotation = self.pad_by_layer[layer]._pad_parameter_value[5]
                if layer == old_name:  # pragma no cover
                    new_padstack_data.SetPadParameters(
                        updated_name, pad_type, geom_type, parameters, offset_x, offset_y, rotation
                    )
                else:
                    new_padstack_data.SetPadParameters(
                        layer, pad_type, geom_type, parameters, offset_x, offset_y, rotation
                    )

            updated_thermal_pad = self.thermalpad_by_layer[layer]
            if not updated_thermal_pad.geometry_type == 0:  # pragma no cover
                pad_type = self._edb.definition.PadType.ThermalPad
                geom_type = self.pad_by_layer[layer]._pad_parameter_value[1]
                parameters = self.pad_by_layer[layer]._pad_parameter_value[2]
                offset_x = self.pad_by_layer[layer]._pad_parameter_value[3]
                offset_y = self.pad_by_layer[layer]._pad_parameter_value[4]
                rotation = self.pad_by_layer[layer]._pad_parameter_value[5]
                if layer == old_name:  # pragma no cover
                    new_padstack_data.SetPadParameters(
                        updated_name, pad_type, geom_type, parameters, offset_x, offset_y, rotation
                    )
                else:
                    new_padstack_data.SetPadParameters(
                        layer, pad_type, geom_type, parameters, offset_x, offset_y, rotation
                    )

        hole_param = cloned_padstack_data.GetHoleParameters()
        if hole_param[0]:
            hole_geom = hole_param[1]
            hole_params = convert_py_list_to_net_list([self._get_edb_value(i) for i in hole_param[2]])
            hole_off_x = self._get_edb_value(hole_param[3])
            hole_off_y = self._get_edb_value(hole_param[4])
            hole_rot = self._get_edb_value(hole_param[5])
            new_padstack_data.SetHoleParameters(hole_geom, hole_params, hole_off_x, hole_off_y, hole_rot)

        new_padstack_data.SetHolePlatingPercentage(self._get_edb_value(cloned_padstack_data.GetHolePlatingPercentage()))

        new_padstack_data.SetHoleRange(cloned_padstack_data.GetHoleRange())
        new_padstack_data.SetMaterial(cloned_padstack_data.GetMaterial())
        new_padstack_data.SetSolderBallMaterial(cloned_padstack_data.GetSolderBallMaterial())
        solder_ball_param = cloned_padstack_data.GetSolderBallParameter()
        if solder_ball_param[0]:
            new_padstack_data.SetSolderBallParameter(
                self._get_edb_value(solder_ball_param[1]), self._get_edb_value(solder_ball_param[2])
            )
        new_padstack_data.SetSolderBallPlacement(cloned_padstack_data.GetSolderBallPlacement())
        new_padstack_data.SetSolderBallShape(cloned_padstack_data.GetSolderBallShape())
        self.edb_padstack.SetData(new_padstack_data)
        return True


class EDBPadstackInstance(EDBPrimitivesMain):
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
    >>> edb_padstack_instance = edb.padstacks.instances[0]
    """

    def __init__(self, edb_padstackinstance, _pedb):
        super().__init__(edb_padstackinstance, _pedb)
        self._edb_padstackinstance = self._edb_object
        self._bounding_box = []
        self._object_instance = None
        self._position = []
        self._pdef = None

    @pyaedt_function_handler
    def get_terminal(self, name=None, create_new_terminal=False):
        """Return PadstackInstanceTerminal object.

        Parameters
        ----------
        name : str, optional
            Name of the terminal. Only applicable when create_new_terminal is True.
        create_new_terminal : bool, optional
            Whether to create a new terminal.

        Returns
        -------
        :class:`pyaedt.edb_core.edb_data.terminals`

        """

        if create_new_terminal:
            term = self._create_terminal(name)
        else:
            from pyaedt.edb_core.edb_data.terminals import PadstackInstanceTerminal

            term = PadstackInstanceTerminal(self._pedb, self._edb_object.GetPadstackInstanceTerminal())
        if not term.is_null:
            return term

    @pyaedt_function_handler
    def _create_terminal(self, name=None):
        """Create a padstack instance terminal"""
        from pyaedt.edb_core.edb_data.terminals import PadstackInstanceTerminal

        term = PadstackInstanceTerminal(self._pedb, self._edb_object.GetPadstackInstanceTerminal())
        return term.create(self, name)

    @pyaedt_function_handler
    def create_coax_port(self, name=None, radial_extent_factor=0):
        """Create a coax port."""

        port = self.create_port(name)
        port.radial_extent_factor = radial_extent_factor
        return port

    @pyaedt_function_handler
    def create_port(self, name=None, reference=None, is_circuit_port=False):
        """Create a port on the padstack.

        Parameters
        ----------
        name : str, optional
            Name of the port. The default is ``None``, in which case a name is automatically assigned.
        reference : class:`pyaedt.edb_core.edb_data.nets_data.EDBNetsData`,
                    class:`pyaedt.edb_core.edb_data.padstacks_data.EDBPadstackInstance`,
                    class:`pyaedt.edb_core.edb_data.sources.PinGroup`, optional
            Negative terminal of the port.
        is_circuit_port : bool, optional
            Whether it is a circuit port.
        """
        terminal = self._create_terminal(name)
        if reference:
            ref_terminal = reference._create_terminal(terminal.name + "_ref")
            if reference._edb_object.ToString() == "PinGroup":
                is_circuit_port = True
        else:
            ref_terminal = None

        return self._pedb.create_port(terminal, ref_terminal, is_circuit_port)

    @property
    def _em_properties(self):
        """Get EM properties."""
        default = (
            r"$begin 'EM properties'\n"
            r"\tType('Mesh')\n"
            r"\tDataId='EM properties1'\n"
            r"\t$begin 'Properties'\n"
            r"\t\tGeneral=''\n"
            r"\t\tModeled='true'\n"
            r"\t\tUnion='true'\n"
            r"\t\t'Use Precedence'='false'\n"
            r"\t\t'Precedence Value'='1'\n"
            r"\t\tPlanarEM=''\n"
            r"\t\tRefined='true'\n"
            r"\t\tRefineFactor='1'\n"
            r"\t\tNoEdgeMesh='false'\n"
            r"\t\tHFSS=''\n"
            r"\t\t'Solve Inside'='false'\n"
            r"\t\tSIwave=''\n"
            r"\t\t'DCIR Equipotential Region'='false'\n"
            r"\t$end 'Properties'\n"
            r"$end 'EM properties'\n"
        )

        pid = self._pedb.edb_api.ProductId.Designer
        _, p = self._edb_padstackinstance.GetProductProperty(pid, 18, "")
        if p:
            return p
        else:
            return default

    @_em_properties.setter
    def _em_properties(self, em_prop):
        """Set EM properties"""
        pid = self._pedb.edb_api.ProductId.Designer
        self._edb_padstackinstance.SetProductProperty(pid, 18, em_prop)

    @property
    def dcir_equipotential_region(self):
        """Check whether dcir equipotential region is enabled.

        Returns
        -------
        bool
        """
        pattern = r"'DCIR Equipotential Region'='([^']+)'"
        em_pp = self._em_properties
        result = re.search(pattern, em_pp).group(1)
        if result == "true":
            return True
        else:
            return False

    @dcir_equipotential_region.setter
    def dcir_equipotential_region(self, value):
        """Set dcir equipotential region."""
        pp = r"'DCIR Equipotential Region'='true'" if value else r"'DCIR Equipotential Region'='false'"
        em_pp = self._em_properties
        pattern = r"'DCIR Equipotential Region'='([^']+)'"
        new_em_pp = re.sub(pattern, pp, em_pp)
        self._em_properties = new_em_pp

    @property
    def object_instance(self):
        """Return Ansys.Ansoft.Edb.LayoutInstance.LayoutObjInstance object."""
        if not self._object_instance:
            self._object_instance = (
                self._edb_padstackinstance.GetLayout()
                .GetLayoutInstance()
                .GetLayoutObjInstance(self._edb_padstackinstance, None)
            )
        return self._object_instance

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
        bbox = self.object_instance.GetBBox()
        self._bounding_box = [
            [bbox.Item1.X.ToDouble(), bbox.Item1.Y.ToDouble()],
            [bbox.Item2.X.ToDouble(), bbox.Item2.Y.ToDouble()],
        ]
        return self._bounding_box

    @pyaedt_function_handler()
    def in_polygon(self, polygon_data, include_partial=True, simple_check=False):
        """Check if padstack Instance is in given polygon data.

        Parameters
        ----------
        polygon_data : PolygonData Object
        include_partial : bool, optional
            Whether to include partial intersecting instances. The default is ``True``.
        simple_check : bool, optional
            Whether to perform a single check based on the padstack center or check the padstack bounding box.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.
        """
        pos = [i for i in self.position]
        int_val = 1 if polygon_data.PointInPolygon(self._pedb.point_data(*pos)) else 0
        if int_val == 0:
            return False

        if simple_check:
            # pos = [i for i in self.position]
            # int_val = 1 if polygon_data.PointInPolygon(self._pedb.point_data(*pos)) else 0
            return True
        else:
            plane = self._pedb.modeler.Shape("rectangle", pointA=self.bounding_box[0], pointB=self.bounding_box[1])
            rectangle_data = self._pedb.modeler.shape_to_polygon_data(plane)
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
        """EDB padstack object."""
        warnings.warn("`pin` is deprecated.", DeprecationWarning)
        return self._edb_padstackinstance

    @property
    def padstack_definition(self):
        """Padstack definition.

        Returns
        -------
        str
            Name of the padstack definition.
        """
        self._pdef = self._edb_padstackinstance.GetPadstackDef().GetName()
        return self._pdef

    @property
    def backdrill_top(self):
        """Backdrill layer from top.

        Returns
        -------
        tuple
            Tuple of the layer name, drill diameter, and offset if it exists.
        """
        layer = self._pedb.edb_api.cell.layer("", self._pedb.edb_api.cell.layer_type.SignalLayer)
        val = self._pedb.edb_value(0)
        offset = self._pedb.edb_value(0.0)
        if is_ironpython:  # pragma: no cover
            diameter = _clr.StrongBox[type(val)]()
            drill_to_layer = _clr.StrongBox[self._pedb.edb_api.Cell.ILayerReadOnly]()
            flag = self._edb_padstackinstance.GetBackDrillParametersLayerValue(drill_to_layer, offset, diameter, False)
        else:
            (
                flag,
                drill_to_layer,
                offset,
                diameter,
            ) = self._edb_padstackinstance.GetBackDrillParametersLayerValue(layer, offset, val, False)
        if flag:
            if offset.ToDouble():
                return drill_to_layer.GetName(), diameter.ToString(), offset.ToString()
            else:
                return drill_to_layer.GetName(), diameter.ToString()
        else:
            return

    def set_backdrill_top(self, drill_depth, drill_diameter, offset=0.0):
        """Set backdrill from top.

        Parameters
        ----------
        drill_depth : str
            Name of the drill to layer.
        drill_diameter : float, str
            Diameter of backdrill size.
        offset : float, str
            Offset for the backdrill. The default is ``0.0``. If the value is other than the
            default, the stub does not stop at the layer. In AEDT, this parameter is called
            "Mfg stub length".

        Returns
        -------
        bool
            True if success, False otherwise.
        """
        layer = self._pedb.stackup.layers[drill_depth]._edb_layer
        val = self._pedb.edb_value(drill_diameter)
        offset = self._pedb.edb_value(offset)
        if offset.ToDouble():
            return self._edb_padstackinstance.SetBackDrillParameters(layer, offset, val, False)
        else:
            return self._edb_padstackinstance.SetBackDrillParameters(layer, val, False)

    @property
    def backdrill_bottom(self):
        """Backdrill layer from bottom.

        Returns
        -------
        tuple
            Tuple of the layer name, drill diameter, and drill offset if it exists.
        """
        layer = self._pedb.edb_api.cell.layer("", self._pedb.edb_api.cell.layer_type.SignalLayer)
        val = self._pedb.edb_value(0)
        offset = self._pedb.edb_value(0.0)
        if is_ironpython:  # pragma: no cover
            diameter = _clr.StrongBox[type(val)]()
            drill_to_layer = _clr.StrongBox[self._pedb.edb_api.Cell.ILayerReadOnly]()
            flag = self._edb_padstackinstance.GetBackDrillParametersLayerValue(drill_to_layer, offset, diameter, True)
        else:
            (
                flag,
                drill_to_layer,
                offset,
                diameter,
            ) = self._edb_padstackinstance.GetBackDrillParametersLayerValue(layer, offset, val, True)
        if flag:
            if offset.ToDouble():
                return drill_to_layer.GetName(), diameter.ToString(), offset.ToString()
            else:
                return drill_to_layer.GetName(), diameter.ToString()
        else:
            return

    def set_backdrill_bottom(self, drill_depth, drill_diameter, offset=0.0):
        """Set backdrill from bottom.

        Parameters
        ----------
        drill_depth : str
            Name of the drill to layer.
        drill_diameter : float, str
            Diameter of the backdrill size.
        offset : float, str, optional
            Offset for the backdrill. The default is ``0.0``. If the value is other than the
            default, the stub does not stop at the layer. In AEDT, this parameter is called
            "Mfg stub length".

        Returns
        -------
        bool
            True if success, False otherwise.
        """
        layer = self._pedb.stackup.layers[drill_depth]._edb_layer
        val = self._pedb.edb_value(drill_diameter)
        offset = self._pedb.edb_value(offset)
        if offset.ToDouble():
            return self._edb_padstackinstance.SetBackDrillParameters(layer, offset, val, True)
        else:
            return self._edb_padstackinstance.SetBackDrillParameters(layer, val, True)

    @property
    def start_layer(self):
        """Starting layer.

        Returns
        -------
        str
            Name of the starting layer.
        """
        layer = self._pedb.edb_api.cell.layer("", self._pedb.edb_api.cell.layer_type.SignalLayer)
        _, start_layer, stop_layer = self._edb_padstackinstance.GetLayerRange()

        if start_layer:
            return start_layer.GetName()
        return None

    @start_layer.setter
    def start_layer(self, layer_name):
        stop_layer = self._pedb.stackup.signal_layers[self.stop_layer]._edb_layer
        layer = self._pedb.stackup.signal_layers[layer_name]._edb_layer
        self._edb_padstackinstance.SetLayerRange(layer, stop_layer)

    @property
    def stop_layer(self):
        """Stopping layer.

        Returns
        -------
        str
            Name of the stopping layer.
        """
        layer = self._pedb.edb_api.cell.layer("", self._pedb.edb_api.cell.layer_type.SignalLayer)
        _, start_layer, stop_layer = self._edb_padstackinstance.GetLayerRange()

        if stop_layer:
            return stop_layer.GetName()
        return None

    @stop_layer.setter
    def stop_layer(self, layer_name):
        start_layer = self._pedb.stackup.signal_layers[self.start_layer]._edb_layer
        layer = self._pedb.stackup.signal_layers[layer_name]._edb_layer
        self._edb_padstackinstance.SetLayerRange(start_layer, layer)

    @property
    def layer_range_names(self):
        """List of all layers to which the padstack instance belongs."""
        _, start_layer, stop_layer = self._edb_padstackinstance.GetLayerRange()
        started = False
        layer_list = []
        start_layer_name = start_layer.GetName()
        stop_layer_name = stop_layer.GetName()
        for layer_name in list(self._pedb.stackup.layers.keys()):
            if started:
                layer_list.append(layer_name)
                if layer_name == stop_layer_name or layer_name == start_layer_name:
                    break
            elif layer_name == start_layer_name:
                started = True
                layer_list.append(layer_name)
                if layer_name == stop_layer_name:
                    break
            elif layer_name == stop_layer_name:
                started = True
                layer_list.append(layer_name)
                if layer_name == start_layer_name:
                    break
        return layer_list

    @property
    def net_name(self):
        """Net name.

        Returns
        -------
        str
            Name of the net.
        """
        return self._edb_padstackinstance.GetNet().GetName()

    @net_name.setter
    def net_name(self, val):
        if not isinstance(val, str):
            try:
                self._edb_padstackinstance.SetNet(val.net_obj)
            except:
                raise AttributeError("Value inserted not found. Input has to be net name or net object.")
        elif val in self._pedb.nets.netlist:
            net = self._pedb.nets.nets[val].net_object
            self._edb_padstackinstance.SetNet(net)
        else:
            raise AttributeError("Value inserted not found. Input has to be net name or net object.")

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
        self._position = []
        out = self._edb_padstackinstance.GetPositionAndRotationValue()
        if self._edb_padstackinstance.GetComponent():
            out2 = self._edb_padstackinstance.GetComponent().GetTransform().TransformPoint(out[1])
            self._position = [out2.X.ToDouble(), out2.Y.ToDouble()]
        elif out[0]:
            self._position = [out[1].X.ToDouble(), out[1].Y.ToDouble()]
        return self._position

    @position.setter
    def position(self, value):
        pos = []
        for v in value:
            if isinstance(v, (float, int, str)):
                pos.append(self._pedb.edb_value(v))
            else:
                pos.append(v)
        point_data = self._pedb.edb_api.geometry.point_data(pos[0], pos[1])
        self._edb_padstackinstance.SetPositionAndRotation(point_data, self._pedb.edb_value(self.rotation))

    @property
    def rotation(self):
        """Padstack instance rotation.

        Returns
        -------
        float
            Rotatation value for the padstack instance.
        """
        point_data = self._pedb.edb_api.geometry.point_data(self._pedb.edb_value(0.0), self._pedb.edb_value(0.0))
        out = self._edb_padstackinstance.GetPositionAndRotationValue()

        if out[0]:
            return out[2].ToDouble()

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
        self._edb_padstackinstance.SetProductProperty(self._pedb.edb_api.ProductId.Designer, 11, value)

    @property
    def metal_volume(self):
        """Metal volume of the via hole instance in cubic units (m3). Metal plating ratio is accounted.

        Returns
        -------
        float
            Metal volume of the via hole instance.

        """
        volume = 0
        if not self.start_layer == self.stop_layer:
            start_layer = self.start_layer
            stop_layer = self.stop_layer
            if self.backdrill_top:  # pragma no cover
                start_layer = self.backdrill_top[0]
            if self.backdrill_bottom:  # pragma no cover
                stop_layer = self.backdrill_bottom[0]
            padstack_def = self._pedb.padstacks.definitions[self.padstack_definition]
            hole_diam = 0
            try:  # pragma no cover
                hole_diam = padstack_def.hole_properties[0]
            except:  # pragma no cover
                pass
            if hole_diam:  # pragma no cover
                hole_finished_size = padstack_def.hole_finished_size
                via_length = (
                    self._pedb.stackup.signal_layers[start_layer].upper_elevation
                    - self._pedb.stackup.signal_layers[stop_layer].lower_elevation
                )
                volume = (math.pi * (hole_diam / 2) ** 2 - math.pi * (hole_finished_size / 2) ** 2) * via_length
        return volume

    @property
    def pin_number(self):
        """Get pin number."""
        return self._edb_padstackinstance.GetName()

    @property
    def aedt_name(self):
        """Retrieve the pin name that is shown in AEDT.

        .. note::
           To obtain the EDB core pin name, use `pin.GetName()`.

        Returns
        -------
        str
            Name of the pin in AEDT.

        Examples
        --------

        >>> from pyaedt import Edb
        >>> edbapp = Edb("myaedbfolder", "project name", "release version")
        >>> edbapp.padstacks.instances[111].get_aedt_pin_name()

        """
        if is_ironpython:
            name = _clr.Reference[String]()
            self._edb_padstackinstance.GetProductProperty(self._pedb.edb_api.ProductId.Designer, 11, name)
        else:
            val = String("")
            _, name = self._edb_padstackinstance.GetProductProperty(self._pedb.edb_api.ProductId.Designer, 11, val)
        name = str(name).strip("'")
        return name

    @pyaedt_function_handler()
    def parametrize_position(self, prefix=None):
        """Parametrize the instance position.

        Parameters
        ----------
        prefix : str, optional
            Prefix for the variable name. Default is ``None``.
            Example `"MyVariableName"` will create 2 Project variables $MyVariableNamesX and $MyVariableNamesY.

        Returns
        -------
        List
            List of variables created.
        """
        p = self.position
        if not prefix:
            var_name = "${}_pos".format(self.name)
        else:
            var_name = "${}".format(prefix)
        self._pedb.add_project_variable(var_name + "X", p[0])
        self._pedb.add_project_variable(var_name + "Y", p[1])
        self.position = [var_name + "X", var_name + "Y"]
        return [var_name + "X", var_name + "Y"]

    @pyaedt_function_handler()
    def delete_padstack_instance(self):
        """Delete this padstack instance.

        .. deprecated:: 0.6.28
           Use :func:`delete` property instead.
        """
        warnings.warn("`delete_padstack_instance` is deprecated. Use `delete` instead.", DeprecationWarning)
        self._edb_padstackinstance.Delete()
        return True

    @pyaedt_function_handler()
    def in_voids(self, net_name=None, layer_name=None):
        """Check if this padstack instance is in any void.

        Parameters
        ----------
        net_name : str
            Net name of the voids to be checked. Default is ``None``.
        layer_name : str
            Layer name of the voids to be checked. Default is ``None``.

        Returns
        -------
        list
            List of the voids that include this padstack instance.
        """
        x_pos = self._pedb.edb_value(self.position[0])
        y_pos = self._pedb.edb_value(self.position[1])
        point_data = self._pedb.modeler._edb.geometry.point_data(x_pos, y_pos)

        voids = []
        for prim in self._pedb.modeler.get_primitives(net_name, layer_name, is_void=True):
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
        try:
            return self._edb_padstackinstance.GetGroup().GetPlacementLayer().Clone().GetLowerElevation()
        except AttributeError:  # pragma: no cover
            return None

    @property
    def upper_elevation(self):
        """Upper elevation of the placement layer.

        Returns
        -------
        float
           Upper elevation of the placement layer.
        """
        try:
            return self._edb_padstackinstance.GetGroup().GetPlacementLayer().Clone().GetUpperElevation()
        except AttributeError:  # pragma: no cover
            return None

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
    def create_rectangle_in_pad(self, layer_name, return_points=False, partition_max_order=16):
        """Create a rectangle inscribed inside a padstack instance pad.

        The rectangle is fully inscribed in the pad and has the maximum area.
        It is necessary to specify the layer on which the rectangle will be created.

        Parameters
        ----------
        layer_name : str
            Name of the layer on which to create the polygon.
        return_points : bool, optional
            If `True` does not create the rectangle and just returns a list containing the rectangle vertices.
            Default is `False`.
        partition_max_order : float, optional
            Order of the lattice partition used to find the quasi-lattice polygon that approximates ``polygon``.
            Default is ``16``.

        Returns
        -------
        bool, List,  :class:`pyaedt.edb_core.edb_data.primitives.EDBPrimitives`
            Polygon when successful, ``False`` when failed, list of list if `return_points=True`.

        Examples
        --------
        >>> from pyaedt import Edb
        >>> edbapp = Edb("myaedbfolder", edbversion="2021.2")
        >>> edb_layout = edbapp.modeler
        >>> list_of_padstack_instances = list(edbapp.padstacks.instances.values())
        >>> padstack_inst = list_of_padstack_instances[0]
        >>> padstack_inst.create_rectangle_in_pad("TOP")
        """

        padstack_center = self.position
        rotation = self.rotation  # in radians
        padstack_name = self.padstack_definition
        try:
            padstack = self._pedb.padstacks.definitions[padstack_name]
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
            while i < polygon_data.edb_api.Count:
                point = polygon_data.edb_api.GetPoint(i)
                i += 1
                if point.IsArc():
                    continue
                else:
                    points.append([point.X.ToDouble(), point.Y.ToDouble()])
            xpoly, ypoly = zip(*points)
            polygon = [list(xpoly), list(ypoly)]
            rectangles = GeometryOperators.find_largest_rectangle_inside_polygon(
                polygon, partition_max_order=partition_max_order
            )
            rect = rectangles[0]
            for i in range(4):
                rect[i] = _translate(_rotate(rect[i]))

        if rect is None or len(rect) != 4:
            return False
        path = self._pedb.modeler.Shape("polygon", points=rect)
        pdata = self._pedb.modeler.shape_to_polygon_data(path)
        new_rect = []
        for point in pdata.Points:
            p_transf = self._edb_padstackinstance.GetComponent().GetTransform().TransformPoint(point)
            new_rect.append([p_transf.X.ToDouble(), p_transf.Y.ToDouble()])
        if return_points:
            return new_rect
        else:
            path = self._pedb.modeler.Shape("polygon", points=new_rect)
            created_polygon = self._pedb.modeler.create_polygon(path, layer_name)
            return created_polygon

    @pyaedt_function_handler()
    def get_connected_object_id_set(self):
        """Produce a list of all geometries physically connected to a given layout object.

        Returns
        -------
        list
            Found connected objects IDs with Layout object.
        """
        layoutInst = self._edb_padstackinstance.GetLayout().GetLayoutInstance()
        layoutObjInst = self.object_instance
        return [loi.GetLayoutObj().GetId() for loi in layoutInst.GetConnectedObjects(layoutObjInst).Items]

    @pyaedt_function_handler()
    def get_reference_pins(self, reference_net="GND", search_radius=5e-3, max_limit=0, component_only=True):
        """Search for reference pins using given criteria.

        Parameters
        ----------
        reference_net : str, optional
            Reference net. The default is ``"GND"``.
        search_radius : float, optional
            Search radius for finding padstack instances. The default is ``5e-3``.
        max_limit : int, optional
            Maximum limit for the padstack instances found. The default is ``0``, in which
            case no limit is applied. The maximum limit value occurs on the nearest
            reference pins from the positive one that is found.
        component_only : bool, optional
            Whether to limit the search to component padstack instances only. The
            default is ``True``. When ``False``, the search is extended to the entire layout.

        Returns
        -------
        list
            List of :class:`pyaedt.edb_core.edb_data.padstacks_data.EDBPadstackInstance`.

        Examples
        --------
        >>> edbapp = Edb("target_path")
        >>> pin = edbapp.components.instances["J5"].pins["19"]
        >>> reference_pins = pin.get_reference_pins(reference_net="GND", search_radius=5e-3, max_limit=0,
        >>> component_only=True)
        """
        return self._pedb.padstacks.get_reference_pins(
            positive_pin=self,
            reference_net=reference_net,
            search_radius=search_radius,
            max_limit=max_limit,
            component_only=component_only,
        )
