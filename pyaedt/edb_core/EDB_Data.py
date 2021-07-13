import warnings
import sys
from collections import OrderedDict, defaultdict
from .general import convert_py_list_to_net_list, convert_net_list_to_py_list, convert_pydict_to_netdict, convert_netdict_to_pydict
from ..generic.general_methods import aedt_exception_handler
import time
try:
    import clr
    from System import Double, Array
    from System.Collections.Generic import List
except ImportError:
    warnings.warn("The clr is missing. Install Python.NET or use an IronPython version if you want to use the EDB module.")


class EDBLayer(object):
    """EDBLayer class."""


    def __init__(self, edblayer, parent):
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
        self._edb = parent._edb
        self._active_layout = parent._active_layout
        self._parent = parent
        self.init_vals()

    @property
    def _stackup_methods(self):
        return self._parent._stackup_methods

    @property
    def _builder(self):
        return self._parent._builder

    @property
    def _messenger(self):
        return self._parent._messenger

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
        """Retrieve or update the thickness value.

        Returns
        -------
        str
            Thickness value.
        """
        try:
            self._thickness = self._layer.GetThicknessValue().ToString()
        except:
            pass
        return self._thickness

    @thickness_value.setter
    def thickness_value(self, value):
        self._thickness = value
        self.update_layers()

    @property
    def filling_material_name(self):
        """Retrieve or update the filling material.

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
            self._top_bottom_association = self._layer.GetTopBottomAssociation()
        except:
            pass
        return self._top_bottom_association

    @property
    def lower_elevation(self):
        """Retrieve or update the lower elevation.

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
        """Retrieve or update the etch factor.

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

        if self._layer_type == 0 or self._layer_type==2:
            self._etch_factor = value
            self.update_layers()

    @aedt_exception_handler
    def init_vals(self):
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

    @aedt_exception_handler
    def update_layer_vals(self, layerName, newLayer, etchMap, materialMap, fillMaterialMap, thicknessMap, layerTypeMap):
        newLayer.SetName(layerName)

        try:
            newLayer.SetLayerType(layerTypeMap)
        except:
            self._messenger.add_error_message('Layer {0} has unknown type {1}'.format(layerName, layerTypeMap))
            return False
        newLayer.SetThickness(self._edb.Utility.Value(thicknessMap))
        newLayer.SetMaterial(materialMap)
        newLayer.SetFillMaterial(fillMaterialMap)
        if etchMap and layerTypeMap == 0 or layerTypeMap==2:
            etchVal = float(etchMap)
        else:
            etchVal = 0.0
        if etchVal != 0.0:
            newLayer.SetEtchFactorEnabled(True)
            newLayer.SetEtchFactor(self._edb.Utility.Value(etchVal))
        return newLayer

    @aedt_exception_handler
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
        layer.SetLowerElevation(self._edb.Utility.Value(elev))
        return layer

    @aedt_exception_handler
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
                newLayer = self.update_layer_vals(self._name, newLayer, self._etch_factor, self._material_name, self._filling_material_name, self._thickness,
                                                  self._layer_type)
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
            self._messenger.add_error_message('Failed to set new layers when updating the stackup information.')
            return False
        self._parent._update_edb_objects()
        time.sleep(1)
        return True


class EDBLayers(object):
    """EDBLayers object.

    This class manages all primitives.
    """

    def __init__(self, parent):
        self._stackup_mode = None
        self._parent = parent
        self._edb_object = OrderedDict(defaultdict(EDBLayer))
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
    def _messenger(self):
        return self._parent._messenger

    @property
    def _stackup_methods(self):
        return self._parent._stackup_methods

    @property
    def _edb(self):
        return self._parent._edb

    @property
    def _builder(self):
        return self._parent._builder

    @property
    def _active_layout(self):
        return self._parent._active_layout

    @property
    def layers(self):
        """Dictionary of layers.

        Returns
        -------
        dict
            Dictionary of layers.
        """
        if not self._edb_object:
            self._update_edb_objects()
        return self._edb_object

    @property
    def edb_layers(self):
        """List of EDB layers.

        Returns
        -------
        list
            List of EDB layers
        """
        allLayers = list(list(self.layer_collection.Layers(self._edb.Cell.LayerTypeSet.AllLayerSet)))
        allStckuplayers = filter(lambda lyr: (lyr.GetLayerType() == self._edb.Cell.LayerType.DielectricLayer) or (
                lyr.GetLayerType() == self._edb.Cell.LayerType.SignalLayer or lyr.GetLayerType() == self._edb.Cell.LayerType.ConductingLayer), allLayers)
        return sorted(allStckuplayers, key=lambda lyr=self._edb.Cell.StackupLayer: lyr.GetLowerElevation())

    @property
    def signal_layers(self):
        """Dictionry of signal layers.

        Returns
        -------
        dict
            Dictionary of signal layers.
        """
        self._signal_layers = {}
        for layer, edblayer in self.layers.items():
            if edblayer._layer_type == self._edb.Cell.LayerType.SignalLayer or edblayer._layer_type == self._edb.Cell.LayerType.ConductingLayer:
                self._signal_layers[layer]= edblayer
        return self._signal_layers


    @property
    def layer_collection(self):
        """Collection of layers.

        Returns
        -------
        type
            Collection of layers.
        """
        return self._active_layout.GetLayerCollection()

    @property
    def layer_collection_mode(self):
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
        """Retrieve or update the stackup mode.

        Returns
        -------
        int
            Stackup mode, where:

            * 0 - Laminate
            * 1 - Overlapping
            * 2 - Multizone
        """
        self._stackup_mode = self.layer_collection.GetMode()
        return self._stackup_mode

    @property
    def _messenger(self):
        return self._parent._messenger

    @aedt_exception_handler
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

    @aedt_exception_handler
    def _update_edb_objects(self):
        self._edb_object = OrderedDict(defaultdict(EDBLayer))
        layers = self.edb_layers
        for i in range(len(layers)):
            self._edb_object[layers[i].GetName()] = EDBLayer(layers[i], self)
        return True

    @aedt_exception_handler
    def add_layer(self, layerName, start_layer=None, material="copper", fillMaterial="", thickness="35um", layerType=0,
                  etchMap=None):
        """Add an additional layer after a specific layer.

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
        thisLC = self._parent._active_layout.GetLayerCollection()
        layers = list(list(thisLC.Layers(self._edb.Cell.LayerTypeSet.AllLayerSet)))
        layers.reverse()
        newLayers = List[self._edb.Cell.Layer]()
        el = 0.0
        if not layers or not start_layer:
            if int(layerType)>2:
                newLayer = self._edb.Cell.Layer(layerName, self._int_to_layer_types(layerType))
                newLayers.Add(newLayer)
            else:
                newLayer = self._edb.Cell.StackupLayer(layerName, self._int_to_layer_types(layerType),
                                                              self._edb.Utility.Value(0),
                                                              self._edb.Utility.Value(0), '')
                newLayers.Add(newLayer)
                self._edb_object[layerName] = EDBLayer(newLayer, self._parent)
                newLayer = self._edb_object[layerName].update_layer_vals(layerName, newLayer, etchMap, material,
                                                                         fillMaterial, thickness, self._int_to_layer_types(layerType))
                newLayer = self._edb_object[layerName].set_elevation(newLayer, el)
                el += newLayer.GetThickness()
        else:
            for lyr in layers:
                if not lyr.IsStackupLayer():
                    newLayers.Add(lyr.Clone())
                    continue
                if lyr.GetName() == start_layer:
                    newLayer = lyr.Clone()
                    el += newLayer.GetThickness()
                    newLayers.Add(newLayer)

                    newLayer = self._edb.Cell.StackupLayer(layerName, self._int_to_layer_types(layerType),
                                                                  self._edb.Utility.Value(0),
                                                                  self._edb.Utility.Value(0), '')
                    self._edb_object[layerName] = EDBLayer(newLayer, self._parent)
                    newLayer = self._edb_object[layerName].update_layer_vals(layerName, newLayer, etchMap, material,
                                                                            fillMaterial, thickness, self._int_to_layer_types(layerType))
                    newLayer = self._edb_object[layerName].set_elevation(newLayer, el)
                    el += newLayer.GetThickness()
                else:
                    newLayer = lyr.Clone()
                    newLayer = self._edb_object[lyr.GetName()].set_elevation(newLayer, el)
                    el += newLayer.GetThickness()
                newLayers.Add(newLayer)
        lcNew = self._edb.Cell.LayerCollection()
        newLayers.Reverse()
        if not lcNew.AddLayers(newLayers) or not self._active_layout.SetLayerCollection(lcNew):
            self._messenger.add_error_message('Failed to set new layers when updating the stackup information.')
            return False
        self._update_edb_objects()
        return True

    def add_outline_layer(self, outline_name="Outline"):
        """
        Adds an Outline Layer named "Outline" if not present

        Returns
        -------
        bool
            "True" if succeeded
        """
        outlineLayer = self._edb.Cell.Layer.FindByName(self._active_layout.GetLayerCollection(), outline_name)
        if outlineLayer.IsNull():
            return self.add_layer(outline_name, layerType=self.layer_types.OutlineLayer, material="", thickness="",)
        else:
            return False

    @aedt_exception_handler
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
        thisLC = self._edb.Cell.LayerCollection(self._parent._active_layout.GetLayerCollection())
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
        if not lcNew.AddLayers(newLayers) or not self._parent._active_layout.SetLayerCollection(lcNew):
            self._messenger.add_error_message('Failed to set new layers when updating the stackup information.')
            return False
        self._update_edb_objects()
        return True


class EDBPadProperties(object):
    """EDBPadProperties class."""

    def __init__(self, edb_padstack, layer_name, pad_type, parent):
        self._edb_padstack = edb_padstack
        self._parent = parent
        self.layer_name = layer_name
        self.pad_type = pad_type
        pass

    @property
    def _padstack_methods(self):
        return self._parent._padstack_methods

    @property
    def _stackup_layers(self):
        return self._parent._stackup_layers

    @property
    def _builder(self):
        return self._parent._builder

    @property
    def _edb(self):
        return self._parent._edb

    @property
    def _edb_value(self):
        return self._parent._edb_value

    @property
    def geometry_type(self):
        """Geometry type.

        Returns
        -------
        int
            Type of the geometry.
        """
        padparams = self._padstack_methods.GetPadParametersValue(self._edb_padstack, self.layer_name, self.pad_type)
        return padparams.Item1

    @property
    def parameters(self):
        """Retrieve or update a list of parameters.

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
            propertylist =[self._edb_value(propertylist)]
        else:
            propertylist = [self._edb_value(i) for i in propertylist]
        self._update_pad_parameters_parameters(params= propertylist)

    @property
    def offset_x(self):
        """Retrieve or update the offset for the X axis.

        Returns
        -------
        str
            Offset for the X axis.
        """
        pad_values = self._padstack_methods.GetPadParametersValue(self._edb_padstack, self.layer_name, self.pad_type)
        return pad_values.Item3.ToString()

    @offset_x.setter
    def offset_x(self, offset_value):

        self._update_pad_parameters_parameters(offsetx= offset_value)
    @property
    def offset_y(self):
        """Retrieve or update the offset for the Y axis.

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

    @aedt_exception_handler
    def _update_pad_parameters_parameters(self, layer_name=None, pad_type=None, geom_type=None, params=None, offsetx=None, offsety=None, rotation=None):
        """Update padstack parameters.

        Parameters
        ----------
        layer_name : str, optional
            Name of the layer. The default is ``None``.
        pad_type :
            Type of the pad. The default is ``None``.
        geom_type :
            Type of the geometry. The default is ``None``.
        params :
            The default is ``None``.
        offsetx : float, optional
            Offset value for the X axis. The default is ``None``.
        offsety :  float, optional
            Offset value for the Y axis. The default is ``None``.
        rotation: float, optional
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
            params = [self._edb_value(i) for i in self.parameters]
        if not offsetx:
            offsetx = self.offset_x
        if not offsety:
            offsety = self.offset_y
        if not rotation:
            rotation = self.rotation
        if not layer_name:
            layer_name = self.layer_name
        newPadstackDefinitionData.SetPadParameters(layer_name, pad_type, geom_type, convert_py_list_to_net_list(params),
                                                      self._edb_value(offsetx),
                                                      self._edb_value(offsety),
                                                      self._edb_value(rotation))
        self._edb_padstack.SetData(newPadstackDefinitionData)


class EDBPadstack(object):
    """EDBPadstacks object."""

    def __init__(self, edb_padstack, parent):
        self.edb_padstack = edb_padstack
        self._parent = parent
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
        return self._parent._padstack_methods

    @property
    def _stackup_layers(self):
        return self._parent._stackup_layers

    @property
    def _builder(self):
        return self._parent._builder

    @property
    def _edb(self):
        return self._parent._edb

    @property
    def _edb_value(self):
        return self._parent._edb_value

    @property
    def via_layers(self):
        """List of layers.

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
        return self.via_layers[0]

    @property
    def via_stop_layer(self):
        """Stopping layer.

        Returns
        -------
        str
            Name of the stopping layer.
        """
        return self.via_layers[-1]

    @property
    def _hole_params(self):
        viaData = self.edb_padstack.GetData()
        if "IronPython" in sys.version or ".NETFramework" in sys.version:
            out = viaData.GetHoleParametersValue()
        else:
            value0 = self._edb_value("0.0")
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

    @aedt_exception_handler
    def _update_hole_parameters(self, hole_type=None, params=None, offsetx=None, offsety=None, rotation=None):
        """Update hole parameters.

        Parameters
        ----------
        hole_type :
            Type of the hole. The default is ``None``.
        params :
            The default is ``None``.
        offsetx : float, optional
            Offset value for the X axis. The default is ``None``.
        offsety :  float, optional
            Offset value for the Y axis. The default is ``None``.
        rotation: float, optional
            Rotation value. The default is ``None``.

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
        newPadstackDefinitionData.SetHoleParameters(hole_type, convert_py_list_to_net_list(params),
                                                      self._edb_value(offsetx),
                                                      self._edb_value(offsety),
                                                      self._edb_value(rotation))
        self.edb_padstack.SetData(newPadstackDefinitionData)

    @property
    def hole_properties(self):
        """Retrieve or update the hole properties.

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
            propertylist =[self._edb_value(propertylist)]
        else:
            propertylist = [self._edb_value(i) for i in propertylist]
        self._update_hole_parameters(params= propertylist)

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
        """Retrieve or update the hole offset for the X axis.

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
        """Retrieve or update the hole offset for the Y axis.

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
        """Retrieve or update the hole rotation.

        Returns
        -------
        str
            Value for the hole rotation.
        """
        self._hole_rotation = self._hole_params[5].ToString()
        return self._hole_rotation

    @hole_rotation.setter
    def hole_rotation(self, rotation):

        self._hole_rotation= rotation
        self._update_hole_parameters(rotation=rotation)

    @property
    def hole_plating_ratio(self):
        """Retrieve or update the hole plating ratio.

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
        newPadstackDefinitionData.SetHolePlatingPercentage(self._edb_value(ratio))
        self.edb_padstack.SetData(newPadstackDefinitionData)

    @property
    def hole_plating_thickness(self):
        """Hole plating thickness.

        Returns
        -------
        float
            Thickness of the hole plating if present.
        """
        if len(self.hole_properties)>0:
            return (float(self.hole_properties[0]) * self.hole_plating_ratio/100)/2
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
        if len(self.hole_properties)>0:
            return float(self.hole_properties[0]) - (self.hole_plating_thickness * 2)
        else:
            return 0

    @property
    def material(self):
        """Retrieve or update the hole material

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


class EDBPinInstances(object):
    """EDBPinInstances class."""

    def __init__(self,parent, pin):
        self.parent = parent
        self.pin = pin

    @property
    def placement_layer(self):
        return self.pin.GetGroup().GetPlacementLayer().GetName()

    @property
    def net(self):
        """

        Returns
        -------
        str
        """
        return self.pin.GetNet().GetName()

    @property
    def pingroups(self):
        """Pin groups to which the pin belongs.

        Returns
        -------
        list
            List of pin groups to which the pin belongs.
        """
        return self.pin.GetPinGroups()

    @property
    def position(self):
        """Pin position.

        Returns
        -------
        list
            List of the pin position in the format ``[x, y]``.
        """
        self.parent._edb.Geometry.PointData(self.parent._edb_value(0.0), self.parent._edb_value(0.0))
        out = self.pin.GetPositionAndRotationValue(
            self.parent._edb.Geometry.PointData(self.parent._edb_value(0.0), self.parent._edb_value(0.0)),
            self.parent._edb_value(0.0))
        if out[0]:
            return [out[1].X.ToDouble(), out[1].Y.ToDouble()]

    @property
    def rotation(self):
        """Pin rotation.

        Returns
        -------
        float
            Rotatation value for the pin.
        """
        self.parent._edb.Geometry.PointData(self.parent._edb_value(0.0), self.parent._edb_value(0.0))
        out = self.pin.GetPositionAndRotationValue(
            self.parent._edb.Geometry.PointData(self.parent._edb_value(0.0), self.parent._edb_value(0.0)),
            self.parent._edb_value(0.0))
        if out[0]:
            return out[2].ToDouble()

    @property
    def placement_layer(self):
        """Placement layer.

        Returns
        -------
        str
            Placement layer.
        """
        return self.pin.GetGroup().GetPlacementLayer().GetName()

    @property
    def lower_elevation(self):
        """Lower elevation of the placement layer.

        Returns
        -------
        float
            Lower elavation of the placement layer.
        """
        return self.pin.GetGroup().GetPlacementLayer().GetLowerElevation()

    @property
    def upper_elevation(self):
        """Upper elevation of the placement layer.

        Returns
        -------
        float
           Upper elevation of the placement layer.
        """
        return self.pin.GetGroup().GetPlacementLayer().GetUpperElevation()

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
        return self.pin.GetGroup().GetPlacementLayer().GetTopBottomAssociation()


class EDBComponent(object):
    """EDBComponent class."""

    def __init__(self, parent, component, name):
        self.parent = parent
        self.edbcomponent = component
        self.refdes = name
        self.partname = component.PartName
        self.numpins = component.NumPins
        self.type = component.PartType
        self.pinlist = self.parent.get_pin_from_component(self.refdes)
        self.nets = self.parent.get_nets_from_pin_list(self.pinlist)
        self.res_value = None
        self.pins = defaultdict(EDBPinInstances)
        for el in self.pinlist:
            self.pins[el.GetName()] = EDBPinInstances(self, el)

        try:
            self.res_value = self._edb_value(component.Model.RValue).ToDouble()
        except:
            self.res_value = None
        try:
            self.cap_value = self._edb_value(component.Model.CValue).ToDouble()
        except:
            self.cap_value = None
        try:
            self.ind_value = self._edb_value(component.Model.LValue).ToDouble()
        except:
            self.ind_value = None

    @property
    def _edb_value(self):
        return self.parent._edb_value

    @property
    def _edb(self):
        return self.parent._edb

    @property
    def placement_layer(self):
        """Placement layer.

        Returns
        -------
        str
           Name of the placement layer.
        """
        return self.pinlist[0].GetGroup().GetPlacementLayer().GetName()

    @property
    def lower_elevation(self):
        """Lower elevation of the placement layer.

        Returns
        -------
        float
            Lower elevation of the placement layer.
        """
        return self.pinlist[0].GetGroup().GetPlacementLayer().GetLowerElevation()

    @property
    def upper_elevation(self):
        """Upper elevation of the placement layer.

        Returns
        -------
        float
            Upper elevation of the placement layer.

        """
        return self.pinlist[0].GetGroup().GetPlacementLayer().GetUpperElevation()

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
        return self.pinlist[0].GetGroup().GetPlacementLayer().GetTopBottomAssociation()
