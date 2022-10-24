from __future__ import absolute_import

import os
import sys
import time
import warnings
from collections import OrderedDict

from pyaedt import pyaedt_function_handler

try:
    import clr

    clr.AddReference("System.Collections")
    from System.Collections.Generic import List
except ImportError:  # pragma: no cover
    if os.name != "posix":
        warnings.warn("PythonNET is needed to run PyAEDT.")
    elif sys.version[0] == 3 and sys.version[1] < 7:
        warnings.warn("EDB requires Linux Python 3.7 or later.")

from pyaedt.generic.general_methods import pyaedt_function_handler


class EDBLayer(object):
    """Manages EDB functionalities for a layer.

    .. deprecated:: 0.6.5
        There is no need to use core_stackup anymore. You can instantiate new class stackup directly from edb class.

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
        self._lower_elevation = None
        self._upper_elevation = None
        self._top_bottom_association = None
        self._id = None
        self._edb = app._edb
        self._active_layout = app._active_layout
        self._pedblayers = app
        self._roughness_enabled = False
        self._roughness_model_top = None
        self._roughness_model_bottom = None
        self._roughness_model_side = None
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

    @pyaedt_function_handler()
    def assign_roughness_model_top(
        self, model_type="huray", huray_radius="0.5um", huray_surface_ratio="2.9", groisse_roughness="1um"
    ):
        """Assign roughness model on conductor top.

        Parameters
        ----------
        model_type : str, optional
            Type of roughness model. The default is ``"huray"``. Options are ``"huray"``, ``"groisse"``.
        huray_radius : str, optional
            Radius of huray model. The default is ``"0.5um"``.
        huray_surface_ratio : str, float, optional.
            Surface ratio of huray model. The default is ``"2.9"``.
        groisse_roughness : str, float, optional
            Roughness of groisse model. The default is ``"1um"``.
        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.
        """
        if model_type == "huray":
            self._roughness_model_top = [model_type, huray_radius, huray_surface_ratio]
        elif model_type == "groisse":
            self._roughness_model_top = [model_type, groisse_roughness]
        else:
            self._roughness_model_top = None
        return self.update_layers()

    @pyaedt_function_handler()
    def assign_roughness_model_bottom(
        self, model_type="huray", huray_radius="0.5um", huray_surface_ratio="2.9", groisse_roughness="1um"
    ):
        """Assign roughness model on conductor bottom.

        Parameters
        ----------
        model_type : str, optional
            Type of roughness model. The default is ``"huray"``. Options are ``"huray"``, ``"groisse"``.
        huray_radius : str, optional
            Radius of huray model. The default is ``"0.5um"``.
        huray_surface_ratio : str, float, optional.
            Surface ratio of huray model. The default is ``"2.9"``.
        groisse_roughness : str, float, optional
            Roughness of groisse model. The default is ``"1um"``.
        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.
        """
        if model_type == "huray":
            self._roughness_model_bottom = [model_type, huray_radius, huray_surface_ratio]
        elif model_type == "groisse":
            self._roughness_model_bottom = [model_type, groisse_roughness]
        else:
            self._roughness_model_bottom = None
        return self.update_layers()

    @pyaedt_function_handler()
    def assign_roughness_model_side(
        self, model_type="huray", huray_radius="0.5um", huray_surface_ratio="2.9", groisse_roughness="1um"
    ):
        """Assign roughness model on conductor side.

        Parameters
        ----------
        model_type : str, optional
            Type of roughness model. The default is ``"huray"``. Options are ``"huray"``, ``"groisse"``.
        huray_radius : str, optional
            Radius of huray model. The default is ``"0.5um"``.
        huray_surface_ratio : str, float, optional.
            Surface ratio of huray model. The default is ``"2.9"``.
        groisse_roughness : str, float, optional
            Roughness of groisse model. The default is ``"1um"``.
        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.
        """
        if model_type == "huray":
            self._roughness_model_side = [model_type, huray_radius, huray_surface_ratio]
        elif model_type == "groisse":
            self._roughness_model_side = [model_type, groisse_roughness]
        else:
            self._roughness_model_side = None
        return self.update_layers()

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
            models = [self._roughness_model_top, self._roughness_model_bottom, self._roughness_model_side]
            regions = [
                self._edb.Cell.RoughnessModel.Region.Top,
                self._edb.Cell.RoughnessModel.Region.Side,
                self._edb.Cell.RoughnessModel.Region.Bottom,
            ]
            for mdl, region in zip(models, regions):
                if not mdl:
                    continue
                model_type = mdl[0]
                if model_type == "huray":
                    radius = self._get_edb_value(mdl[1])
                    surface_ratio = self._get_edb_value(mdl[2])
                    model = self._edb.Cell.HurrayRoughnessModel(radius, surface_ratio)
                else:
                    roughness = self._get_edb_value(mdl[1])
                    model = self._edb.Cell.GroisseRoughnessModel(roughness)
                newLayer.SetRoughnessModel(region, model)
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

    .. deprecated:: 0.6.5
        There is no need to use core_stackup anymore. You can instantiate new class stackup directly from edb class.

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
        self._edb_layer_collection = None
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
        dict[str, :class:`pyaedt.edb_core.edb_data.layer_data.EDBLayer`]
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
        dict[str, :class:`pyaedt.edb_core.edb_data.layer_data.EDBLayer`]
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
    def edb_layer_collection(self):
        """Copy of EDB layer collection.

        Returns
        -------
        class : Ansys.Ansoft.Edb.Cell.LayerCollection
            Collection of layers.
        """
        if not self._edb_layer_collection:
            lc_readonly = self._pedbstackup._active_layout.GetLayerCollection()
            layers = list(list(lc_readonly.Layers(self._edb.Cell.LayerTypeSet.AllLayerSet)))
            layer_collection = self._edb.Cell.LayerCollection()

            flag_first_layer = True
            for lyr in layers:
                if not lyr.IsStackupLayer():
                    continue
                lyr_clone = lyr.Clone()
                lyr_name = lyr.GetName()
                if flag_first_layer:
                    layer_collection.AddLayerTop(lyr_clone)
                    flag_first_layer = False
                else:
                    layer_collection.AddLayerAbove(lyr_clone, lyr_name)
            self._edb_layer_collection = layer_collection

        return self._edb_layer_collection

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
    def _update_stackup(self):
        self._active_layout.SetLayerCollection(self.edb_layer_collection)
        self._update_edb_objects()
        return True

    @pyaedt_function_handler()
    def insert_layer_above(
        self,
        layer_name,
        base_layer,
        material="copper",
        fillMaterial="",
        thickness="35um",
        layerType=0,
        negative_layer=False,
        roughness_enabled=False,
        etch_factor=None,
    ):
        """Insert a layer above the specified base layer.

        Parameters
        ----------
        layer_name : str
            Name of the layer to add.
        base_layer : str
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
        etch_factor : optional
            Etch value if any. The default is ``None``.

        Returns
        -------
        :class:`pyaedt.edb_core.edb_data.layer_data.EDBLayer`
            Layer Object for stackup layers.
        """

        new_layer = self._edb.Cell.StackupLayer(
            layer_name,
            self._int_to_layer_types(layerType),
            self._get_edb_value(0),
            self._get_edb_value(0),
            "",
        )
        edb_layer = EDBLayer(new_layer.Clone(), self._pedbstackup)
        new_layer = edb_layer.update_layer_vals(
            layer_name,
            new_layer,
            etch_factor,
            material,
            fillMaterial,
            thickness,
            negative_layer,
            roughness_enabled,
            self._int_to_layer_types(layerType),
        )
        self.edb_layer_collection.AddLayerAbove(new_layer, base_layer)
        self._edb_object[layer_name] = edb_layer
        self._update_stackup()
        return self.layers[layer_name]

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
        :class:`pyaedt.edb_core.edb_data.layer_data.EDBLayer`
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


class LayerEdbClass(object):
    """New Edb Layer management class. Replaces EDBLayer."""

    def __init__(self, pclass, name):
        self._pclass = pclass
        self._name = name

    @property
    def _edb(self):
        return self._pclass._pedb.edb

    @property
    def _edb_layer(self):
        for l in self._pclass._edb_layer_list:
            if l.GetName() == self._name:
                return l.Clone()

    @property
    def is_stackup_layer(self):
        """Determine whether this layer is a stackup layer.

        Returns
        -------
        bool
            True if this layer is a stackup layer, False otherwise.
        """
        return self._edb_layer.IsStackupLayer()

    @property
    def color(self):
        """Retrieve color of the layer.

        Returns
        -------
        tuple
            RGB.
        """
        layer_color = self._edb_layer.GetColor()
        return layer_color.Item1, layer_color.Item2, layer_color.Item3

    @color.setter
    def color(self, rgb):
        layer_clone = self._edb_layer
        layer_clone.SetColor(*rgb)
        self._pclass._set_layout_stackup(layer_clone, "change_attribute")

    @property
    def name(self):
        """Retrieve name of the layer.

        Returns
        -------
        str
        """
        return self._edb_layer.GetName()

    @name.setter
    def name(self, name):
        layer_clone = self._edb_layer
        layer_clone.SetName(name)
        self._pclass._set_layout_stackup(layer_clone, "change_name", self._name)
        self._name = name

    @property
    def type(self):
        """Retrieve type of the layer."""
        if self._edb_layer.GetLayerType() == self._edb.Cell.LayerType.SignalLayer:
            return "signal"
        elif self._edb_layer.GetLayerType() == self._edb.Cell.LayerType.DielectricLayer:
            return "dielectric"
        else:
            return

    @type.setter
    def type(self, new_type):
        if new_type == self.type:
            return
        if new_type == "signal":
            self._edb_layer.SetLayerType(self._edb.Cell.LayerType.SignalLayer)
        elif new_type == "dielectric":
            self._edb_layer.SetLayerType(self._edb.Cell.LayerType.DielectricLayer)
        else:
            return

    @property
    def material(self):
        """Get/Set the material loss_tangent.

        Returns
        -------
        float
        """
        return self._edb_layer.GetMaterial()

    @material.setter
    def material(self, name):
        layer_clone = self._edb_layer
        layer_clone.SetMaterial(name)
        self._pclass._set_layout_stackup(layer_clone, "change_attribute")

    @property
    def conductivity(self):
        """Get the material conductivity.

        Returns
        -------
        float
        """
        if self.material in self._pclass._pedb.materials.materials:
            return self._pclass._pedb.materials[self.material].conductivity
        return None

    @property
    def permittivity(self):
        """Get the material permittivity.

        Returns
        -------
        float
        """
        if self.material in self._pclass._pedb.materials.materials:
            return self._pclass._pedb.materials[self.material].permittivity
        return None

    @property
    def loss_tangent(self):
        """Get the material loss_tangent.

        Returns
        -------
        float
        """
        if self.material in self._pclass._pedb.materials.materials:
            return self._pclass._pedb.materials[self.material].loss_tangent
        return None

    @property
    def dielectric_fill(self):
        """Retrieve material name of the layer dielectric fill."""
        if self.type == "signal":
            return self._edb_layer.GetFillMaterial()
        else:
            return

    @dielectric_fill.setter
    def dielectric_fill(self, name):
        if self.type == "signal":
            layer_clone = self._edb_layer
            layer_clone.SetFillMaterial(name)
            self._pclass._set_layout_stackup(layer_clone, "change_attribute")
        else:
            pass

    @property
    def thickness(self):
        """Retrieve thickness of the layer.

        Returns
        -------
        float
        """
        if not self.is_stackup_layer:  # pragma: no cover
            return
        return self._edb_layer.GetThicknessValue().ToDouble()

    @thickness.setter
    def thickness(self, value):
        if not self.is_stackup_layer:  # pragma: no cover
            return
        layer_clone = self._edb_layer
        layer_clone.SetThickness(self._pclass._edb_value(value))
        self._pclass._set_layout_stackup(layer_clone, "change_attribute")

    @property
    def etch_factor(self):
        """Retrieve etch factor of this layer.

        Returns
        -------
        float
        """
        return self._edb_layer.GetEtchFactor().ToDouble()

    @etch_factor.setter
    def etch_factor(self, value):
        if not self.is_stackup_layer:  # pragma: no cover
            return
        if not value:
            layer_clone = self._edb_layer
            layer_clone.SetEtchFactorEnabled(False)
        else:
            layer_clone = self._edb_layer
            layer_clone.SetEtchFactorEnabled(True)
            layer_clone.SetEtchFactor(self._pclass._edb_value(value))
        self._pclass._set_layout_stackup(layer_clone, "change_attribute")

    @property
    def roughness_enabled(self):
        """Determine whether roughness is enabled on this layer.

        Returns
        -------
        bool
        """
        if not self.is_stackup_layer:  # pragma: no cover
            return
        return self._edb_layer.IsRoughnessEnabled()

    @roughness_enabled.setter
    def roughness_enabled(self, set_enable):
        if not self.is_stackup_layer:  # pragma: no cover
            return
        if set_enable:
            layer_clone = self._edb_layer
            layer_clone.SetRoughnessEnabled(True)
            self._pclass._set_layout_stackup(layer_clone, "change_attribute")
            self.assign_roughness_model()
        else:
            layer_clone = self._edb_layer
            layer_clone.SetRoughnessEnabled(False)
            self._pclass._set_layout_stackup(layer_clone, "change_attribute")

    @pyaedt_function_handler()
    def assign_roughness_model(
        self,
        model_type="huray",
        huray_radius="0.5um",
        huray_surface_ratio="2.9",
        groisse_roughness="1um",
        apply_on_surface="all",
    ):
        """Assign roughness model on this layer.

        Parameters
        ----------
        model_type : str, optional
            Type of roughness model. The default is ``"huray"``. Options are ``"huray"``, ``"groisse"``.
        huray_radius : str, optional
            Radius of huray model. The default is ``"0.5um"``.
        huray_surface_ratio : str, float, optional.
            Surface ratio of huray model. The default is ``"2.9"``.
        groisse_roughness : str, float, optional
            Roughness of groisse model. The default is ``"1um"``.
        apply_on_surface : str, optional.
            Where to assign roughness model. The default is ``"all"``. Options are ``"top"``, ``"bottom"``,
             ``"side"``.
        Returns
        -------

        """
        if not self.is_stackup_layer:  # pragma: no cover
            return
        radius = self._pclass._edb_value(huray_radius)
        surface_ratio = self._pclass._edb_value(huray_surface_ratio)
        groisse_roughness = self._pclass._edb_value(groisse_roughness)
        regions = []
        if apply_on_surface == "all":
            regions = [
                self._pclass._pedb.edb.Cell.RoughnessModel.Region.Top,
                self._pclass._pedb.edb.Cell.RoughnessModel.Region.Side,
                self._pclass._pedb.edb.Cell.RoughnessModel.Region.Bottom,
            ]
        elif apply_on_surface == "top":
            regions = [
                self._pclass._pedb.edb.Cell.RoughnessModel.Region.Top,
            ]
        elif apply_on_surface == "bottom":
            regions = [
                self._pclass._pedb.edb.Cell.RoughnessModel.Region.Bottom,
            ]
        elif apply_on_surface == "side":
            regions = [
                self._pclass._pedb.edb.Cell.RoughnessModel.Region.Side,
            ]

        layer_clone = self._edb_layer
        for r in regions:
            if model_type == "huray":
                model = self._pclass._pedb.edb.Cell.HurrayRoughnessModel(radius, surface_ratio)
            else:
                model = self._pclass._pedb.edb.Cell.GroisseRoughnessModel(groisse_roughness)
            layer_clone.SetRoughnessModel(r, model)
        return self._pclass._set_layout_stackup(layer_clone, "change_attribute")
