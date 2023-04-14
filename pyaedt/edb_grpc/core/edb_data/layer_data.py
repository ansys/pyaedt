from __future__ import absolute_import

from collections import OrderedDict

from ansys.edb.layer import LayerCollectionMode
from ansys.edb.layer import LayerTypeSet
from ansys.edb.layer import RoughnessRegion
from ansys.edb.layer import StackupLayer
from ansys.edb.layer.layer import LayerType

from pyaedt import pyaedt_function_handler


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
        return self._layer.clone()

    @property
    def _builder(self):
        return self._pedblayers._builder

    @property
    def _logger(self):
        """Logger."""
        return self._pedblayers._logger

    @property
    def name(self):
        """Layer name.

        Returns
        -------
        str
            Name of the layer.
        """
        if not self._name:
            self._name = self._layer.name
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
            self._id = self._layer.layer_id
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
            self._layer_type = self._layer.type
        return int(self._layer_type)

    @layer_type.setter
    def layer_type(self, value):
        if type(value) is not type(self._layer_type):
            self._layer_type = int(value)
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
            self._material_name = self._cloned_layer.material
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
            self._thickness = self._cloned_layer.thickness
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
        if self._layer_type == LayerType.SIGNAL_LAYER or self._layer_type == LayerType.CONDUCTING_LAYER:
            try:
                self._filling_material_name = self._cloned_layer.get_fill_material()
            except:
                pass
            return self._filling_material_name
        return ""

    @filling_material_name.setter
    def filling_material_name(self, value):
        if self._layer_type == LayerType.SIGNAL_LAYER or self._layer_type == LayerType.CONDUCTING_LAYER:
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
        if self._layer_type == LayerType.SIGNAL_LAYER or self._layer_type == LayerType.CONDUCTING_LAYER:
            try:
                self._negative_layer = self._layer.negative
            except:
                pass
        return self._negative_layer

    @negative_layer.setter
    def negative_layer(self, value):
        if self._layer_type == LayerType.SIGNAL_LAYER or self._layer_type == LayerType.CONDUCTING_LAYER:
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
        if self._layer_type == LayerType.SIGNAL_LAYER or self._layer_type == LayerType.CONDUCTING_LAYER:
            try:
                self._roughness_enabled = self._layer.roughness_enabled
            except:
                pass
        return self._roughness_enabled

    @roughness_enabled.setter
    def roughness_enabled(self, value):
        if self._layer_type == LayerType.SIGNAL_LAYER or self._layer_type == LayerType.CONDUCTING_LAYER:
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
            self._top_bottom_association = int(self._layer.to_bottom_association)
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
            self._lower_elevation = self._cloned_layer.lower_elevation
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
            self._upper_elevation = self._cloned_layer.upper_elevation
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
        if self._layer_type == LayerType.SIGNAL_LAYER or self._layer_type == LayerType.CONDUCTING_LAYER:
            try:
                self._etch_factor = self._cloned_layer.etching_factor
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
            self._etch_factor = value
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
            self._name = self._layer.name
            self._layer_type = self._layer.type
            self._thickness = self._layer.thickness
            if self._layer_type == LayerType.SIGNAL_LAYER or self._layer_type == LayerType.CONDUCTING_LAYER:
                self._etch_factor = self._layer.etch_factor
                self._filling_material_name = self._layer.fill_material
                self._negative_layer = self._layer.negative
                self._roughness_enabled = self._layer.roughness_enabled
            self._material_name = self._layer.get_material()
            self._lower_elevation = self._layer.lower_elevation
            self._upper_elevation = self._layer.upper_elevation
            self._top_bottom_association = self._layer.top_bottom_association
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
        newLayer.name = layerName

        try:
            newLayer.type = layerTypeMap
        except:
            self._logger.error("Layer %s has unknown type %s.", layerName, layerTypeMap)
            return False
        if thicknessMap:
            newLayer.thickness = thicknessMap
        if materialMap:
            newLayer.set_material(materialMap)
        if fillMaterialMap:
            newLayer.SetFillMaterial(fillMaterialMap)
        if negativeMap:
            newLayer.set_fill_material(negativeMap)
        if roughnessMap:
            newLayer.roughness_enabled = roughnessMap
            models = [self._roughness_model_top, self._roughness_model_bottom, self._roughness_model_side]
            regions = [
                RoughnessRegion.TOP,
                RoughnessRegion.SIDE,
                RoughnessRegion.BOTTOM,
            ]
            for mdl, region in zip(models, regions):
                if not mdl:
                    continue
                model_type = mdl[0]
                if model_type == "huray":
                    radius = mdl[1]
                    surface_ratio = mdl[2]
                    # didn't find roughness model to be completed
                    # model = self._edb.Cell.HurrayRoughnessModel(radius, surface_ratio)
                else:
                    roughness = mdl[1]
                    # didn't find roughness model to be completed
                    # model = self._edb.Cell.GroisseRoughnessModel(roughness)
                # newLayer.SetRoughnessModel(region, model)
        if isinstance(etchMap, float) and int(layerTypeMap) in [0, 2]:
            etchVal = float(etchMap)
        else:
            etchVal = 0.0
        if etchVal != 0.0:
            newLayer.etch_factor_enabled = True
            newLayer.etch_factor = etchVal
        else:
            newLayer.etch_factor = etchVal
            newLayer.etch_factor_enabled = False
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
            The layer which was updated.

        """

        layer.lower_elevation = elev
        return layer

    @pyaedt_function_handler()
    def update_layers(self):
        """Update all layers.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.
        """
        lc = self._active_layout.layer_collection.clone()
        layers = lc.get_layers(LayerTypeSet.ALL_LAYER_SET)
        layers.reverse()
        el = 0.0
        for lyr in layers:
            if lyr.is_stackup_layer:
                if lyr.name == self.name:
                    new_layer = lyr.clone()
                    self.update_layer_vals(
                        self._name,
                        new_layer,
                        self._etch_factor,
                        self._material_name,
                        self._filling_material_name,
                        self._thickness,
                        self._negative_layer,
                        self._roughness_enabled,
                        self._layer_type,
                    )
                    new_layer = self.set_elevation(el)
                    el += new_layer.thickness
                else:
                    new_layer = lyr.clone()
                    self.set_elevation(new_layer, el)
                    el += new_layer.thickness
        self._active_layout.layer_collection = lc
        return True


class EDBLayers(object):
    """Manages EDB functionalities for all primitive layers.

    .. deprecated:: 0.6.5
        There is no need to use core_stackup anymore. You can instantiate new class stackup directly from edb class.

    Parameters
    ----------
    edb_stackup : :class:`pyaedt.edb_grpc.core.stackup.EdbStackup`
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
        dict[str, :class:`pyaedt.edb_grpc.core.edb_data.layer_data.EDBLayer`]
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
        stackup_layers = self.layer_collection.get_layers(LayerTypeSet.STACKUP_LAYER_SET)
        return sorted(stackup_layers, key=lambda lyr: lyr.lower_elevation)

    @property
    def signal_layers(self):
        """Signal layers.

        Returns
        -------
        dict[str, :class:`pyaedt.edb_grpc.core.edb_data.layer_data.EDBLayer`]
            Dictionary of signal layers.
        """
        self._signal_layers = OrderedDict({})
        for layer, edblayer in self.layers.items():
            if edblayer._layer_type == LayerType.SIGNAL_LAYER or edblayer._layer_type == LayerType.CONDUCTING_LAYER:
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
            lc = self._pedbstackup._active_layout.layer_collection.clone()
            layers = lc.get_layers(LayerTypeSet.ALL_LAYER_SET)
            flag_first_layer = True
            for lyr in layers:
                if not lyr.is_stackup_layer:
                    continue
                cloned_layer = lyr.clone()
                lyr_name = lyr.name
                if flag_first_layer:
                    lc.add_layer_top(cloned_layer)
                    flag_first_layer = False
                else:
                    lc.add_layer_above(cloned_layer, lyr_name)
            self._edb_layer_collection = lc
        return self._edb_layer_collection

    @property
    def layer_collection(self):
        """Layer collection.

        Returns
        -------
        type
            Collection of layers.
        """
        return self._active_layout.layer_collection

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
        self._stackup_mode = self.layer_collection.mode
        return self._stackup_mode

    @pyaedt_function_handler()
    def _int_to_layer_types(self, val):
        if int(val) == 0:
            return LayerType.SIGNAL_LAYER
        elif int(val) == 1:
            return LayerType.DIELECTRIC_LAYER
        elif int(val) == 2:
            return LayerType.CONDUCTING_LAYER
        elif int(val) == 3:
            return LayerType.AIRLINES_LAYER
        elif int(val) == 4:
            return LayerType.ERRORS_LAYER
        elif int(val) == 5:
            return LayerType.SYMBOL_LAYER
        elif int(val) == 6:
            return LayerType.MEASURE_LAYER
        elif int(val) == 8:
            return LayerType.ASSEMBLY_LAYER
        elif int(val) == 9:
            return LayerType.SILKSCREEN_LAYER
        elif int(val) == 10:
            return LayerType.SOLDER_MASK_LAYER
        elif int(val) == 11:
            return LayerType.SOLDER_PASTE_LAYER
        elif int(val) == 12:
            return LayerType.GLUE_LAYER
        elif int(val) == 13:
            return LayerType.WIREBOND_LAYER
        elif int(val) == 14:
            return LayerType.USER_LAYER
        elif int(val) == 16:
            return LayerType.SIWAVE_HFSS_SOLVER_REGIONS
        elif int(val) == 18:
            return LayerType.OUTLINE_LAYER

    @pyaedt_function_handler()
    def _layer_types_to_int(self, layer_type):
        if not isinstance(layer_type, int):
            if layer_type == LayerType.SIGNAL_LAYER:
                return 0
            elif layer_type == LayerType.DIELECTRIC_LAYER:
                return 1
            elif layer_type == LayerType.CONDUCTING_LAYER:
                return 2
            elif layer_type == LayerType.AIRLINES_LAYER:
                return 3
            elif layer_type == LayerType.ERRORS_LAYER:
                return 4
            elif layer_type == LayerType.SYMBOL_LAYER:
                return 5
            elif layer_type == LayerType.MEASURE_LAYER:
                return 6
            elif layer_type == LayerType.ASSEMBLY_LAYER:
                return 8
            elif layer_type == LayerType.SILKSCREEN_LAYER:
                return 9
            elif layer_type == LayerType.SOLDER_MASK_LAYER:
                return 10
            elif layer_type == LayerType.SOLDER_PASTE_LAYER:
                return 11
            elif layer_type == LayerType.GLUE_LAYER:
                return 12
            elif layer_type == LayerType.WIREBOND_LAYER:
                return 13
            elif layer_type == LayerType.USER_LAYER:
                return 14
            elif layer_type == LayerType.SIWAVE_HFSS_SOLVER_REGIONS:
                return 16
            elif layer_type == LayerType.OUTLINE_LAYER:
                return 18
        elif isinstance(layer_type, int):
            return layer_type

    @stackup_mode.setter
    def stackup_mode(self, value):
        if value == 0 or value == LayerCollectionMode.LAMINATE:
            self.layer_collection.mode = LayerCollectionMode.LAMINATE
        elif value == 1 or value == LayerCollectionMode.OVERLAPPING:
            self.layer_collection.mode = LayerCollectionMode.OVERLAPPING
        elif value == 2 or value == LayerCollectionMode.MULTIZONE:
            self.layer_collection.mode = LayerCollectionMode.MULTIZONE

    @pyaedt_function_handler()
    def _update_edb_objects(self):
        self._edb_object = OrderedDict({})
        layers = self.edb_layers
        for i in range(len(layers)):
            self._edb_object[layers[i].name] = EDBLayer(layers[i], self)
        return True

    @pyaedt_function_handler()
    def _update_stackup(self):
        self._active_layout.layer_collection = self.edb_layer_collection
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
        :class:`pyaedt.edb_grpc.core.edb_data.layer_data.EDBLayer`
            Layer Object for stackup layers.
        """

        new_layer = StackupLayer()
        new_layer.name = layer_name
        new_layer.type = layerType

        edb_layer = EDBLayer(new_layer, self._pedbstackup)
        new_layer = edb_layer.update_layer_vals(
            layer_name,
            new_layer,
            etch_factor,
            material,
            fillMaterial,
            thickness,
            negative_layer,
            roughness_enabled,
            layerType,
        )
        self.edb_layer_collection.add_layer_above(new_layer, base_layer)
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
        layerType=LayerType.SIGNAL_LAYER,
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
        :class:`pyaedt.edb_grpc.core.edb_data.layer_data.EDBLayer`
            Layer Object for stackup layers. Boolean otherwise (True in case of success).
        """
        layers = self._active_layout.layer_collection.get_layers(LayerTypeSet.ALL_LAYER_SET)
        layers.reverse()
        el = 0.0
        lc = self._active_layout.layer_collectionp.clone()
        if not layers or not start_layer:
            if int(layerType) > 2:
                # need to explicit declaration conflict with EDB StackupLayer
                new_layer = StackupLayer()
                new_layer.type = layerType
                lc.add_layer_top(new_layer)
            else:
                new_layer = StackupLayer()
                new_layer.name = layerName
                new_layer.type = layerType
                self._edb_object[layerName] = EDBLayer(new_layer, self._pedbstackup)
                new_layer = self._edb_object[layerName].update_layer_vals(
                    layerName,
                    new_layer,
                    etchMap,
                    material,
                    fillMaterial,
                    thickness,
                    negative_layer,
                    roughness_enabled,
                    self._int_to_layer_types(layerType),
                )
                new_layer.lower_elevation = el
                lc.add_layer_top(new_layer)
                el += new_layer.thickness
            for lyr in layers:
                if not lyr.is_stackup:
                    continue
                new_layer = lyr.clone()
                new_layer.lower_elevation = el
                el += new_layer.thickness
                lc.add_layer_top(new_layer)
            for lyr in layers:
                if not lyr.is_stackup:
                    lc.add_layer_top(lyr.clone())
                    continue
        else:
            for lyr in layers:
                if not lyr.is_stackup:
                    continue
                if lyr.name == start_layer:
                    original_layer = lyr.clone()
                    original_layer.lower_elevation = el
                    lc.add_layer_top(original_layer)
                    el += original_layer.thickness
                    new_layer = StackupLayer()
                    new_layer.name = layerName
                    new_layer.type = layerType
                    self._edb_object[layerName] = EDBLayer(new_layer, self._pedbstackup)
                    new_layer = self._edb_object[layerName].update_layer_vals(
                        layerName,
                        new_layer,
                        etchMap,
                        material,
                        fillMaterial,
                        thickness,
                        negative_layer,
                        roughness_enabled,
                        self._int_to_layer_types(layerType),
                    )
                    new_layer.lower_elevation = el
                    lc.add_layer_top(new_layer)
                    el += new_layer.thickness
                else:
                    new_layer = lyr.clone()
                    new_layer.lower_elevation = el
                    el += new_layer.thickness
                    lc.add_layer_top(new_layer)
            for lyr in layers:
                if not lyr.is_stackup:
                    lc.add_layer_top(lyr.clone())
                    continue
        self._active_layout.layer_collection = lc
        self._update_edb_objects()
        allLayers = self.layer_collection.get_layers(LayerTypeSet.ALL_LAYER_SET)
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
            "True" if succeeded.
        """
        outline_layer = self._active_layout.layer_collection.find_by_name(outline_name)
        if not outline_layer:
            return self.add_layer(
                outline_name,
                layerType=LayerType.OUTLINE_LAYER,
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
        lc = self._active_layout.layer_collection.clone()
        layers = lc.get_layers(LayerTypeSet.ALL_LAYER_SET)
        layers.reverse()
        el = 0.0
        for lyr in layers:
            if lyr.is_stackup:
                if not (layername == lyr.name):
                    new_layer = lyr.clone()
                    new_layer = self._edb_object[lyr.GetName()].set_elevation(new_layer, el)
                    el += new_layer.thickness
        self._pedbstackup._active_layout.layer_collection = lc
        self._update_edb_objects()
        return True


class LayerEdbClass(object):
    """Manages Edb Layers. Replaces EDBLayer."""

    def __init__(self, pclass, name):
        self._pclass = pclass
        self._name = name
        self._color = ()
        self._type = ""
        self._material = ""
        self._conductivity = 0.0
        self._permittivity = 0.0
        self._loss_tangent = 0.0
        self._dielectric_fill = ""
        self._thickness = 0.0
        self._etch_factor = 0.0
        self._roughness_enabled = False
        self._top_hallhuray_nodule_radius = 0.5e-6
        self._top_hallhuray_surface_ratio = 2.9
        self._bottom_hallhuray_nodule_radius = 0.5e-6
        self._bottom_hallhuray_surface_ratio = 2.9
        self._side_hallhuray_nodule_radius = 0.5e-6
        self._side_hallhuray_surface_ratio = 2.9
        self._material = None
        self._upper_elevation = 0.0
        self._lower_elevation = 0.0

    @property
    def lower_elevation(self):
        """Lower elevation.

        Returns
        -------
        float
            Lower elevation.
        """
        try:
            self._lower_elevation = self._edb_layer.lower_elevation
        except:
            pass
        return self._lower_elevation

    @lower_elevation.setter
    def lower_elevation(self, value):
        layer_clone = self._edb_layer
        layer_clone.lower_elevation = value
        self._pclass._set_layout_stackup(layer_clone, "change_attribute")

    @property
    def upper_elevation(self):
        """Upper elevation.

        Returns
        -------
        float
            Upper elevation.
        """
        try:
            self._upper_elevation = self._edb_layer.upper_elevation
        except:
            pass
        return self._upper_elevation

    @property
    def _edb(self):
        return self._pclass._pedb.edb

    @property
    def _edb_layer(self):
        for l in self._pclass._edb_layer_list:
            if l.name == self._name:
                return l.clone()

    @property
    def is_stackup_layer(self):
        """Determine whether this layer is a stackup layer.

        Returns
        -------
        bool
            True if this layer is a stackup layer, False otherwise.
        """
        return self._edb_layer.is_stackup

    @property
    def is_negative(self):
        """Determine whether this layer is a negative layer.

        Returns
        -------
        bool
            True if this layer is a negative layer, False otherwise.
        """
        return self._edb_layer.is_negative

    @is_negative.setter
    def is_negative(self, value):
        layer_clone = self._edb_layer
        layer_clone.is_negative = value
        self._pclass._set_layout_stackup(layer_clone, "change_attribute")

    @property
    def color(self):
        """Retrieve color of the layer.

        Returns
        -------
        tuple
            RGB.
        """
        layer_color = self._edb_layer.color
        return layer_color[0], layer_color[1], layer_color[2]

    @color.setter
    def color(self, rgb):
        layer_clone = self._edb_layer
        layer_clone.color = rgb
        self._pclass._set_layout_stackup(layer_clone, "change_attribute")
        self._color = rgb

    @property
    def transparency(self):
        """Retrieve transparency of the layer.

        Returns
        -------
        int
            An integer between 0 and 100 with 0 being fully opaque and 100 being fully transparent.
        """
        return self._edb_layer.transparency

    @transparency.setter
    def transparency(self, trans):
        layer_clone = self._edb_layer
        layer_clone.transparency = trans
        self._pclass._set_layout_stackup(layer_clone, "change_attribute")

    @property
    def name(self):
        """Retrieve name of the layer.

        Returns
        -------
        str
        """
        return self._edb_layer.name

    @name.setter
    def name(self, name):
        layer_clone = self._edb_layer
        layer_clone.name = name
        self._pclass._set_layout_stackup(layer_clone, "change_name", self._name)
        self._name = name

    @property
    def type(self):
        """Retrieve type of the layer."""
        return self._edb_layer.type

    @type.setter
    def type(self, new_type):
        if new_type == self.type:
            return
        if new_type == "signal":
            self._edb_layer.type = LayerType.SIGNAL_LAYER
            self._type = new_type
        elif new_type == "dielectric":
            self._edb_layer.type = LayerType.DIELECTRIC_LAYER
            self._type = new_type
        else:
            return

    @property
    def material(self):
        """Get/Set the material loss_tangent.

        Returns
        -------
        float
        """
        return self._edb_layer.get_material()

    @material.setter
    def material(self, name):
        layer_clone = self._edb_layer
        layer_clone.set_material(name)
        self._pclass._set_layout_stackup(layer_clone, "change_attribute")
        self._material = name

    @property
    def conductivity(self):
        """Get the material conductivity.

        Returns
        -------
        float
        """
        if self.material in self._pclass._pedb.materials.materials:
            self._conductivity = self._pclass._pedb.materials[self.material].conductivity
            return self._conductivity

        return None

    @property
    def permittivity(self):
        """Get the material permittivity.

        Returns
        -------
        float
        """
        if self.material in self._pclass._pedb.materials.materials:
            self._permittivity = self._pclass._pedb.materials[self.material].permittivity
            return self._permittivity
        return None

    @property
    def loss_tangent(self):
        """Get the material loss_tangent.

        Returns
        -------
        float
        """
        if self.material in self._pclass._pedb.materials.materials:
            self._loss_tangent = self._pclass._pedb.materials[self.material].loss_tangent
            return self._loss_tangent
        return None

    @property
    def dielectric_fill(self):
        """Retrieve material name of the layer dielectric fill."""
        if self.type == "signal":
            self._dielectric_fill = self._edb_layer.get_fill_material()
            return self._dielectric_fill
        else:
            return

    @dielectric_fill.setter
    def dielectric_fill(self, name):
        if self.type == "signal":
            layer_clone = self._edb_layer
            layer_clone.set_fill_material(name)
            self._pclass._set_layout_stackup(layer_clone, "change_attribute")
            self._dielectric_fill = name
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
        self._thickness = self._edb_layer.thickness
        return self._thickness

    @thickness.setter
    def thickness(self, value):
        if not self.is_stackup_layer:  # pragma: no cover
            return
        layer_clone = self._edb_layer
        layer_clone.thickness = value
        self._pclass._set_layout_stackup(layer_clone, "change_attribute")
        self._thickness = value

    @property
    def etch_factor(self):
        """Retrieve etch factor of this layer.

        Returns
        -------
        float
        """
        self._etch_factor = self._edb_layer.etch_factor
        return self._etch_factor

    @etch_factor.setter
    def etch_factor(self, value):
        if not self.is_stackup_layer:  # pragma: no cover
            return
        if not value:
            layer_clone = self._edb_layer
            layer_clone.etch_factor_enabled = False
        else:
            layer_clone = self._edb_layer
            layer_clone.etch_factor_enabled = True
            layer_clone.etch_factor = value
        self._pclass._set_layout_stackup(layer_clone, "change_attribute")
        self._etch_factor = value

    @property
    def roughness_enabled(self):
        """Determine whether roughness is enabled on this layer.

        Returns
        -------
        bool
        """
        if not self.is_stackup_layer:  # pragma: no cover
            return
        self._roughness_enabled = self._edb_layer.roughness_enabled
        return self._roughness_enabled

    @roughness_enabled.setter
    def roughness_enabled(self, set_enable):
        if not self.is_stackup_layer:  # pragma: no cover
            return
        self._roughness_enabled = set_enable
        if set_enable:
            layer_clone = self._edb_layer
            layer_clone.roughness_enabled = True
            self._pclass._set_layout_stackup(layer_clone, "change_attribute")
            self.assign_roughness_model()
        else:
            layer_clone = self._edb_layer
            layer_clone.roughness_enabled = False
            self._pclass._set_layout_stackup(layer_clone, "change_attribute")

    @property
    def top_hallhuray_nodule_radius(self):
        """Retrieve huray model nodule radius on top of the conductor."""
        # to do
        # top_roughness_model = self.get_roughness_model("top")
        # if top_roughness_model:
        #     self._top_hallhuray_nodule_radius = top_roughness_model.NoduleRadius.ToDouble()
        # return self._top_hallhuray_nodule_radius
        pass

    @top_hallhuray_nodule_radius.setter
    def top_hallhuray_nodule_radius(self, value):
        # to do
        # self._top_hallhuray_nodule_radius = value
        pass

    @property
    def top_hallhuray_surface_ratio(self):
        """Retrieve huray model surface ratio on top of the conductor."""
        # to do
        # top_roughness_model = self.get_roughness_model("top")
        # if top_roughness_model:
        #     self._top_hallhuray_surface_ratio = top_roughness_model.SurfaceRatio.ToDouble()
        # return self._top_hallhuray_surface_ratio
        pass

    @top_hallhuray_surface_ratio.setter
    def top_hallhuray_surface_ratio(self, value):
        # to do
        # self._top_hallhuray_surface_ratio = value
        pass

    @property
    def bottom_hallhuray_nodule_radius(self):
        """Retrieve huray model nodule radius on bottom of the conductor."""
        # to do
        # bottom_roughness_model = self.get_roughness_model("bottom")
        # if bottom_roughness_model:
        #     self._bottom_hallhuray_nodule_radius = bottom_roughness_model.NoduleRadius.ToDouble()
        # return self._bottom_hallhuray_nodule_radius
        pass

    @bottom_hallhuray_nodule_radius.setter
    def bottom_hallhuray_nodule_radius(self, value):
        # to do
        # self._bottom_hallhuray_nodule_radius = value
        pass

    @property
    def bottom_hallhuray_surface_ratio(self):
        """Retrieve huray model surface ratio on bottom of the conductor."""
        # to do
        # bottom_roughness_model = self.get_roughness_model("bottom")
        # if bottom_roughness_model:
        #     self._bottom_hallhuray_surface_ratio = bottom_roughness_model.SurfaceRatio.ToDouble()
        # return self._bottom_hallhuray_surface_ratio
        pass

    @bottom_hallhuray_surface_ratio.setter
    def bottom_hallhuray_surface_ratio(self, value):
        # to do
        # self._bottom_hallhuray_surface_ratio = value
        pass

    @property
    def side_hallhuray_nodule_radius(self):
        """Retrieve huray model nodule radius on sides of the conductor."""
        # to do
        # side_roughness_model = self.get_roughness_model("side")
        # if side_roughness_model:
        #     self._side_hallhuray_nodule_radius = side_roughness_model.NoduleRadius.ToDouble()
        # return self._side_hallhuray_nodule_radius
        pass

    @side_hallhuray_nodule_radius.setter
    def side_hallhuray_nodule_radius(self, value):
        # to do
        # self._side_hallhuray_nodule_radius = value
        pass

    @property
    def side_hallhuray_surface_ratio(self):
        """Retrieve huray model surface ratio on sides of the conductor."""
        #  to do
        # side_roughness_model = self.get_roughness_model("side")
        # if side_roughness_model:
        #     self._side_hallhuray_surface_ratio = side_roughness_model.SurfaceRatio.ToDouble()
        # return self._side_hallhuray_surface_ratio
        pass

    @side_hallhuray_surface_ratio.setter
    def side_hallhuray_surface_ratio(self, value):
        # to do
        # self._side_hallhuray_surface_ratio = value
        pass

    @pyaedt_function_handler()
    def get_roughness_model(self, surface="top"):
        """Get roughness model of the layer.

        Parameters
        ----------
        surface : str, optional
            Where to fetch roughness model. The default is ``"top"``. Options are ``"top"``, ``"bottom"``, ``"side"``.

        Returns
        -------
        ``"Ansys.Ansoft.Edb.Cell.RoughnessModel"``

        """
        # to do
        # if not self.is_stackup_layer:  # pragma: no cover
        #     return
        # if surface == "top":
        #     return self._edb_layer.GetRoughnessModel(self._pclass._pedb.edb.Cell.RoughnessModel.Region.Top)
        # elif surface == "bottom":
        #     return self._edb_layer.GetRoughnessModel(self._pclass._pedb.edb.Cell.RoughnessModel.Region.Bottom)
        # elif surface == "side":
        #     return self._edb_layer.GetRoughnessModel(self._pclass._pedb.edb.Cell.RoughnessModel.Region.Side)
        pass

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
        huray_radius : str, float, optional
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
        # to do
        # if not self.is_stackup_layer:  # pragma: no cover
        #     return
        #
        # radius = self._pclass._edb_value(huray_radius)
        # self._hurray_nodule_radius = huray_radius
        # surface_ratio = self._pclass._edb_value(huray_surface_ratio)
        # self._hurray_surface_ratio = huray_surface_ratio
        # groisse_roughness = self._pclass._edb_value(groisse_roughness)
        # regions = []
        # if apply_on_surface == "all":
        #     self._side_roughness = "all"
        #     regions = [
        #         self._pclass._pedb.edb.Cell.RoughnessModel.Region.Top,
        #         self._pclass._pedb.edb.Cell.RoughnessModel.Region.Side,
        #         self._pclass._pedb.edb.Cell.RoughnessModel.Region.Bottom,
        #     ]
        # elif apply_on_surface == "top":
        #     self._side_roughness = "top"
        #     regions = [self._pclass._pedb.edb.Cell.RoughnessModel.Region.Top]
        # elif apply_on_surface == "bottom":
        #     self._side_roughness = "bottom"
        #     regions = [self._pclass._pedb.edb.Cell.RoughnessModel.Region.Bottom]
        # elif apply_on_surface == "side":
        #     self._side_roughness = "side"
        #     regions = [self._pclass._pedb.edb.Cell.RoughnessModel.Region.Side]
        #
        # layer_clone = self._edb_layer
        # layer_clone.SetRoughnessEnabled(True)
        # for r in regions:
        #     if model_type == "huray":
        #         model = self._pclass._pedb.edb.Cell.HurrayRoughnessModel(radius, surface_ratio)
        #     else:
        #         model = self._pclass._pedb.edb.Cell.GroisseRoughnessModel(groisse_roughness)
        #     layer_clone.SetRoughnessModel(r, model)
        # return self._pclass._set_layout_stackup(layer_clone, "change_attribute")
        pass

    @pyaedt_function_handler()
    def _json_format(self):
        dict_out = {}
        self._color = self.color
        self._dielectric_fill = self.dielectric_fill
        self._etch_factor = self.etch_factor
        self._material = self.material
        self._name = self.name
        self._roughness_enabled = self.roughness_enabled
        self._thickness = self.thickness
        self._type = self.type
        self._roughness_enabled = self.roughness_enabled
        self._top_hallhuray_nodule_radius = self.top_hallhuray_nodule_radius
        self._top_hallhuray_surface_ratio = self.top_hallhuray_surface_ratio
        self._side_hallhuray_nodule_radius = self.side_hallhuray_nodule_radius
        self._side_hallhuray_surface_ratio = self.side_hallhuray_surface_ratio
        self._bottom_hallhuray_nodule_radius = self.bottom_hallhuray_nodule_radius
        self._bottom_hallhuray_surface_ratio = self.bottom_hallhuray_surface_ratio
        for k, v in self.__dict__.items():
            if (
                not k == "_pclass"
                and not k == "_conductivity"
                and not k == "_permittivity"
                and not k == "_loss_tangent"
            ):
                dict_out[k[1:]] = v
        return dict_out

    def _load_layer(self, layer):
        if layer:
            self.color = layer["color"]
            self.type = layer["type"]
            if isinstance(layer["material"], str):
                self.material = layer["material"]
            else:
                self._pclass._pedb.materials._load_materials(layer["material"])
                self.material = layer["material"]["name"]
            if layer["dielectric_fill"]:
                if isinstance(layer["dielectric_fill"], str):
                    self.dielectric_fill = layer["dielectric_fill"]
                else:
                    self._pclass._pedb.materials._load_materials(layer["dielectric_fill"])
                    self.dielectric_fill = layer["dielectric_fill"]["name"]
            self.thickness = layer["thickness"]
            self.etch_factor = layer["etch_factor"]
            self.roughness_enabled = layer["roughness_enabled"]
            if self.roughness_enabled:
                self.top_hallhuray_nodule_radius = layer["top_hallhuray_nodule_radius"]
                self.top_hallhuray_surface_ratio = layer["top_hallhuray_surface_ratio"]
                self.assign_roughness_model(
                    "huray",
                    layer["top_hallhuray_nodule_radius"],
                    layer["top_hallhuray_surface_ratio"],
                    apply_on_surface="top",
                )
                self.bottom_hallhuray_nodule_radius = layer["bottom_hallhuray_nodule_radius"]
                self.bottom_hallhuray_surface_ratio = layer["bottom_hallhuray_surface_ratio"]
                self.assign_roughness_model(
                    "huray",
                    layer["bottom_hallhuray_nodule_radius"],
                    layer["bottom_hallhuray_surface_ratio"],
                    apply_on_surface="bottom",
                )
                self.side_hallhuray_nodule_radius = layer["side_hallhuray_nodule_radius"]
                self.side_hallhuray_surface_ratio = layer["side_hallhuray_surface_ratio"]
                self.assign_roughness_model(
                    "huray",
                    layer["side_hallhuray_nodule_radius"],
                    layer["side_hallhuray_surface_ratio"],
                    apply_on_surface="side",
                )
