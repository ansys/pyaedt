
import warnings
import sys
from collections import OrderedDict, defaultdict
import time
try:
    import clr
    from System import Double, Array
    from System.Collections.Generic import List
except ImportError:
    warnings.warn("The clr is missing. Install Pythonnet or use Ironpython version if you want to use EDB Module")


# class EDBLayer(object):
#     def __init__(self, builder, stackup_methods, edblayer):
#         self.layer = edblayer
#         self.stackup_methods = stackup_methods
#         self._builder = builder
#         self._name = None
#         self._layer_type = None
#         self._thickness = None
#         self._etch_factor = None
#         self._material_name = None
#         self._filling_material_name = None
#         self._lower_elevation = None
#         self.id = self.layer.GetLayerId()
#
#
#     @property
#     def layout(self):
#         return self._builder.EdbHandler.layout
#
#     @property
#     def name(self):
#         if not self._name:
#             self._name = self.layer.GetName()
#         return self._name
#
#     @name.setter
#     def name(self, value):
#         self.stackup_methods.EditLayerName(self._builder, self.name, value)
#         self._name = value
#
#     @property
#     def layer_type(self):
#         if not self._layer_type:
#             self._layer_type = self.layer.GetLayerType()
#         return self._layer_type
#
#     @layer_type.setter
#     def layer_type(self, value):
#         #self.stackup_methods.EditLayerName(self.layout, self._name, value)
#         self._layer_type = value
#
#     @property
#     def material_name(self):
#         if not self._material_name:
#             try:
#                 self._material_name = self.layer.GetMaterial()
#             except:
#                 self._material_name = None
#         return self._material_name
#
#     @material_name.setter
#     def material_name(self, value):
#         self._material_name = value
#
#     @property
#     def thickness(self):
#         if not self._thickness:
#             try:
#                 self._thickness = self.layer.GetThicknessValue().ToString()
#             except:
#                 self._thickness = ""
#         return self._thickness
#
#     @thickness.setter
#     def thickness(self, value):
#         self.stackup_methods.SetLayerThickness(self._builder, self.name, value)
#         self._thickness = value
#
#     @property
#     def filling_material_name(self):
#         if not self._filling_material_name:
#             try:
#                 self._filling_material_name = self.layer.GetFillMaterial()
#             except:
#                 self._filling_material_name = None
#         return self._filling_material_name
#
#     @filling_material_name.setter
#     def filling_material_name(self, value):
#         self._filling_material_name = value
#
#     @property
#     def lower_elevation(self):
#         if not self._lower_elevation:
#             try:
#                 self._lower_elevation = self.layer.GetLowerElevation()
#             except:
#                 self._lower_elevation = None
#         return self._lower_elevation
#
#     @lower_elevation.setter
#     def lower_elevation(self, value):
#         self._lower_elevation = value
#
#     @property
#     def upper_elevation(self):
#         try:
#             return self.layer.GetUpperElevation()
#         except:
#             return None
#
#     @property
#     def etch_factor(self):
#         if not self._etch_factor:
#             try:
#                 self._etch_factor = self.layer.GetEtchFactor().ToString()
#             except:
#                 self._etch_factor = None
#         return self._etch_factor
#
#     @etch_factor.setter
#     def etch_factor(self, value):
#         self._etch_factor = value


class EDBLayer(object):
    """ """
    @property
    def stackup_methods(self):
        """ """
        return self._parent.stackup_methods

    @property
    def builder(self):
        """ """
        return self._parent.builder

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
        self._id = None
        self.edb = parent.edb
        self.active_layout = parent.active_layout
        self._parent = parent
        self.init_vals()


    def init_vals(self):
        """ """
        self._name = self._layer.GetName()
        self._layer_type = self._layer.GetLayerType()
        self._thickness = self._layer.GetThicknessValue().ToString()
        self._etch_factor = self._layer.GetEtchFactor().ToString()
        self._material_name = self._layer.GetMaterial()
        self._filling_material_name = self._layer.GetFillMaterial()
        self._lower_elevation = self._layer.GetLowerElevation()
        self._upper_elevation = self._layer.GetUpperElevation()

    @property
    def messenger(self):
        """ """
        return self._parent._messenger

    @property
    def name(self):
        """ """
        if not self._name:
            self._name = self._layer.GetName()
        return self._name

    @property
    def id(self):
        """ """
        if not self._id:
            self._id = self._layer.GetLayerId()
        return self._id

    @property
    def layer_type(self):
        """ """
        if not self._layer_type:
            self._layer_type = self._layer.GetLayerType()
        return self._layer_type

    @layer_type.setter
    def layer_type(self, value):
        """

        Parameters
        ----------
        value :
            

        Returns
        -------

        """
        self._layer_type = value
        self.update_layers()

    @property
    def material_name(self):
        """ """
        try:
            self._material_name = self._layer.GetMaterial()
        except:
            pass
        return self._material_name

    @material_name.setter
    def material_name(self, value):
        """

        Parameters
        ----------
        value :
            

        Returns
        -------

        """
        #self.stackup_methods.EditLayerName(self.builder, self._name, value)
        self._material_name = value
        self.update_layers()

    @property
    def thickness_value(self):
        """ """
        try:
            self._thickness = self._layer.GetThicknessValue().ToString()
        except:
            pass
        return self._thickness

    @thickness_value.setter
    def thickness_value(self, value):
        """

        Parameters
        ----------
        value :
            

        Returns
        -------

        """
        #self.stackup_methods.SetLayerThickness(self.builder, self.name, value)
        self._thickness = value
        self.update_layers()

    @property
    def filling_material_name(self):
        """ """
        try:
            self._filling_material_name = self._layer.GetFillMaterial()
        except:
            pass
        return self._filling_material_name

    @filling_material_name.setter
    def filling_material_name(self, value):
        """

        Parameters
        ----------
        value :
            

        Returns
        -------

        """
        self._filling_material_name = value
        self.update_layers()

    @property
    def lower_elevation(self):
        """ """
        try:
            self._lower_elevation = self._layer.GetLowerElevation()
        except:
            pass
        return self._lower_elevation

    @lower_elevation.setter
    def lower_elevation(self, value):
        """

        Parameters
        ----------
        value :
            

        Returns
        -------

        """
        self._lower_elevation = value
        self.update_layers()

    @property
    def upper_elevation(self):
        """ """
        try:
            self._upper_elevation = self._layer.GetUpperElevation()
        except:
            pass
        return self._upper_elevation

    @property
    def etch_factor(self):
        """ """
        try:
            self._etch_factor = self._layer.GetEtchFactor().ToString()
        except:
            pass
        return self._etch_factor

    @etch_factor.setter
    def etch_factor(self, value):
        """

        Parameters
        ----------
        value :
            

        Returns
        -------

        """
        self._etch_factor = value
        self.update_layers()

    def update_layer_vals(self, layerName, newLayer, etchMap, materialMap, fillMaterialMap, thicknessMap, layerTypeMap):
        """

        Parameters
        ----------
        layerName :
            
        newLayer :
            
        etchMap :
            
        materialMap :
            
        fillMaterialMap :
            
        thicknessMap :
            
        layerTypeMap :
            

        Returns
        -------

        """
        newLayer.SetName(layerName)

        if layerTypeMap == 0 or layerTypeMap == self.edb.Cell.LayerType.SignalLayer:
            newLayer.SetLayerType(self.edb.Cell.LayerType.SignalLayer)
        elif layerTypeMap == 2 or layerTypeMap == self.edb.Cell.LayerType.ConductingLayer:
            newLayer.SetLayerType(self.edb.Cell.LayerType.ConductingLayer)
        elif layerTypeMap == 1 or layerTypeMap == self.edb.Cell.LayerType.DielectricLayer:
            newLayer.SetLayerType(self.edb.Cell.LayerType.DielectricLayer)
        else:
            self.messenger.add_error_message('Layer {0} has unknown type {1}'.format(layerName, layerTypeMap))
            return False
        newLayer.SetThickness(self.edb.Utility.Value(thicknessMap))
        newLayer.SetMaterial(materialMap)
        newLayer.SetFillMaterial(fillMaterialMap)
        if etchMap:
            etchVal = float(etchMap)
        else:
            etchVal = 0.0
        if etchVal != 0.0:
            newLayer.SetEtchFactorEnabled(True)
            newLayer.SetEtchFactor(self.edb.Utility.Value(etchVal))
        return newLayer

    def set_elevation(self, layer, elev):
        """Set layer Elevation

        Parameters
        ----------
        layer :
            layer object
        elev :
            float Elevation

        Returns
        -------
        type
            layer

        """
        layer.SetLowerElevation(self.edb.Utility.Value(elev))
        return layer

    def update_layers(self):
        """update all layers
        
        :return: bool

        Parameters
        ----------

        Returns
        -------

        """
        thisLC = self.edb.Cell.LayerCollection(self.active_layout.GetLayerCollection())
        layers = list(list(thisLC.Layers(self.edb.Cell.LayerTypeSet.AllLayerSet)))
        layers.reverse()
        newLayers = List[self.edb.Cell.Layer]()
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

        lcNew = self.edb.Cell.LayerCollection()
        newLayers.Reverse()
        if not lcNew.AddLayers(newLayers) or not self.active_layout.SetLayerCollection(lcNew):
            self.messenger.add_error_message('Failed to set new layers when updating stackup info')
            return False
        self._parent._update_edb_objects()
        time.sleep(1)
        return True


class EDBLayers(object):
    """Class for management of all Primitives."""


    def __init__(self, parent):
        self._stackup_mode = None
        self._parent = parent
        self._edb_object = OrderedDict(defaultdict(EDBLayer))
        self._update_edb_objects()


    def __getitem__(self, layername):
        """
        :return: part object details
        """
        return self.layers[layername]


    @property
    def edb(self):
        """ """
        return self._parent.edb

    @property
    def builder(self):
        """ """
        return self._parent.builder

    @property
    def active_layout(self):
        """ """
        return self._parent.active_layout

    @property
    def layers(self):
        """ """
        self._update_edb_objects()
        return self._edb_object

    @property
    def edb_layers(self):
        """ """
        allLayers = list(list(self.layer_collection.Layers(self.edb.Cell.LayerTypeSet.AllLayerSet)))
        allStckuplayers = filter(lambda lyr: (lyr.GetLayerType() == self.edb.Cell.LayerType.DielectricLayer) or (
                lyr.GetLayerType() == self.edb.Cell.LayerType.SignalLayer), allLayers)
        return sorted(allStckuplayers, key=lambda lyr=self.edb.Cell.StackupLayer: lyr.GetLowerElevation())

    @property
    def signal_layers(self):
        layers = self.edb_layers
        signal_layers = {}
        for lyr in layers:
            if lyr.GetLayerType() == self.edb.Cell.LayerType.SignalLayer:
                lyr_name = lyr.GetName()
                signal_layers[lyr_name] = lyr
        return signal_layers


    @property
    def layer_collection(self):
        """ """
        return self._parent.edb.Cell.LayerCollection(self._parent.active_layout.GetLayerCollection())

    @property
    def layer_collection_mode(self):
        """ """
        return self._parent.edb.Cell.LayerCollectionMode

    @property
    def layer_types(self):
        """ """
        return self._parent.edb.Cell.LayerType

    @property
    def stackup_mode(self):
        """ """
        self._stackup_mode = self.layer_collection.GetMode()
        return self._stackup_mode

    @property
    def messenger(self):
        """ """
        return self._parent._messenger

    @stackup_mode.setter
    def stackup_mode(self, value):
        """

        Parameters
        ----------
        value :
            

        Returns
        -------

        """
        if value == 0 or value == self.layer_collection_mode.Laminate:
            self.layer_collection.SetMode(self.layer_collection_mode.Laminate)
        elif value == 1 or value == self.layer_collection_mode.Overlapping:
            self.layer_collection.SetMode(self.layer_collection_mode.Overlapping)
        elif value == 2 or value == self.layer_collection_mode.MultiZone:
            self.layer_collection.SetMode(self.layer_collection_mode.MultiZone)

    def _update_edb_objects(self):
        """ """
        self._edb_object = OrderedDict(defaultdict(EDBLayer))
        layers = self.edb_layers
        for i in range(len(layers)):
            self._edb_object[layers[i].GetName()] = EDBLayer(layers[i], self)
        return True

    def add_layer(self, layerName, start_layer, material="copper", fillMaterial="", thickness="35um", layerType=0,
                  etchMap=None):
        """Add an additional layer after a specific layer

        Parameters
        ----------
        layerName :
            name of new layer
        start_layer :
            name of layer after which the new layer will be placed
        material :
            name of material (Default value = "copper")
        fillMaterial :
            name of fillmaterial (Default value = "")
        thickness :
            thickness value (Default value = "35um")
        layerType :
            layer type default signal layer
        etchMap :
            etch value if any (Default value = None)

        Returns
        -------
        type
            True if successful

        """
        thisLC = self._parent.edb.Cell.LayerCollection(self._parent.active_layout.GetLayerCollection())
        layers = list(list(thisLC.Layers(self._parent.edb.Cell.LayerTypeSet.AllLayerSet)))
        layers.reverse()
        newLayers = List[self._parent.edb.Cell.Layer]()
        el = 0.0
        for lyr in layers:
            if not lyr.IsStackupLayer():
                newLayers.Add(lyr.Clone())
                continue
            if lyr.GetName() == start_layer:
                newLayer = lyr.Clone()
                el += newLayer.GetThickness()
                newLayers.Add(newLayer)
                newLayer = self._parent.edb.Cell.StackupLayer(layerName, self.layer_types.SignalLayer,
                                                              self._parent.edb.Utility.Value(0),
                                                              self._parent.edb.Utility.Value(0), '')
                self._edb_object[layerName] = EDBLayer(newLayer, self._parent)
                newLayer = self._edb_object[layerName].update_layer_vals(layerName, newLayer, etchMap, material,
                                                                        fillMaterial, thickness, layerType)
                newLayer = self._edb_object[layerName].set_elevation(newLayer, el)
                el += newLayer.GetThickness()
            else:
                newLayer = lyr.Clone()
                newLayer = self._edb_object[lyr.GetName()].set_elevation(newLayer, el)
                el += newLayer.GetThickness()
            newLayers.Add(newLayer)
        lcNew = self._parent.edb.Cell.LayerCollection()
        newLayers.Reverse()
        if not lcNew.AddLayers(newLayers) or not self._parent.active_layout.SetLayerCollection(lcNew):
            self.messenger.add_error_message('Failed to set new layers when updating stackup info')
            return False
        self._update_edb_objects()
        return True

    def remove_layer(self, layername):
        """Remove a specific layer "layername"

        Parameters
        ----------
        layername :
            name of the layer to remove

        Returns
        -------
        type
            True if operation successfully complete

        """
        thisLC = self._parent.edb.Cell.LayerCollection(self._parent.active_layout.GetLayerCollection())
        layers = list(list(thisLC.Layers(self._parent.edb.Cell.LayerTypeSet.AllLayerSet)))
        layers.reverse()
        newLayers = List[self._parent.edb.Cell.Layer]()
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
        lcNew = self._parent.edb.Cell.LayerCollection()
        newLayers.Reverse()
        if not lcNew.AddLayers(newLayers) or not self._parent.active_layout.SetLayerCollection(lcNew):
            self.messenger.add_error_message('Failed to set new layers when updating stackup info')
            return False
        self._update_edb_objects()
        return True

class EDBComponent(object):
    """ """

    @property
    def component_methods(self):
        """ """
        return self._parent.component_methods

    @property
    def builder(self):
        """ """
        return self._parent.builder

    def __init__(self, edb_component, parent):
        self.component = edb_component
        self._refdes = None
        self._type = None
        self._placementlayer = None
        self._pin_number = None
        self._pins = {}
        self._nets = {}
        self.edb = parent.edb
        self.active_layout = parent.active_layout
        self._parent = parent
        self.init_vals()

    def init_vals(self):
        """ """
        self._refdes = self.component.GetName()
        self._type = self.component.GetComponentType()

    @property
    def messenger(self):
        """ """
        return self._parent._messenger

    @property
    def name(self):
        """ """
        if not self._name:
            self._name = self.layer.GetName()
        return self._name

    @property
    def placement_layer(self):
        """ """
        self._placementlayer = self.component.GetPlacementLayer()
        return self._placementlayer

    @property
    def pin_number(self):
        """ """
        self._pin_number = self.component.GetNumberOfPins()
        return self._pin_number

    @placement_layer.setter
    def placement_layer(self, value):
        """

        Parameters
        ----------
        value :
            

        Returns
        -------

        """
        self._placementlayer = value
        return self._placementlayer

    @property
    def pins(self):
        """ """
        pinlist = list(list(self.component.LayoutObjs).Where(lambda obj: obj.GetObjType() == self._parent.edb.Cell.LayoutObjType.PadstackInstance))
        for pin in pinlist:
            self._pins[pin.GetName()] = pin
        return self._pins

    @property
    def nets(self):
        """ """
        pins = self .get_pins()
        for pin in pins:
            pin_name = pin.GetNet().GetName()
            if pin_name not in self._nets:
                self._nets[pin_name] = pin
        return self._nets







