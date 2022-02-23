"""
This module contains the `EdbStackup` class.

"""
from __future__ import absolute_import

import math
import warnings
import os

from pyaedt.edb_core.EDB_Data import EDBLayers
from pyaedt.edb_core.general import convert_py_list_to_net_list
from pyaedt.generic.general_methods import aedt_exception_handler, is_ironpython

try:
    from System import Double
except ImportError:
    if os.name != "posix":
        warnings.warn('This module requires the "pythonnet" package.')


class EdbStackup(object):
    """Manages EDB functionalities for stackups.

    Examples
    --------
    >>> from pyaedt import Edb
    >>> edbapp = Edb("myaedbfolder", edbversion="2021.2")
    >>> edb_stackup = edbapp.core_stackup
    """

    def __init__(self, p_edb):
        self._pedb = p_edb
        self._layer_dict = None

    @property
    def _builder(self):
        """ """
        return self._pedb.builder

    @property
    def _edb_value(self):
        """ """
        return self._pedb.edb_value

    @property
    def _edb(self):
        """ """
        return self._pedb.edb

    @property
    def _active_layout(self):
        """ """
        return self._pedb.active_layout

    @property
    def _cell(self):
        """ """
        return self._pedb.cell

    @property
    def _db(self):
        """ """
        return self._pedb.db

    @property
    def _stackup_methods(self):
        """ """
        return self._pedb.edblib.Layout.StackupMethods

    @property
    def _logger(self):
        """ """
        return self._pedb.logger

    @property
    def stackup_layers(self):
        """Stackup layers.

        Returns
        -------
        :class:`pyaedt.edb_core.EDBData.EDBLayers`
            Dictionary of stackup layers.
        """
        if not self._layer_dict:
            self._layer_dict = EDBLayers(self)
        return self._layer_dict

    @property
    def signal_layers(self):
        """Dictionary of all signal layers.

        Returns
        -------
        dict[str, :class:`pyaedt.edb_core.EDB_Data.EDBLayer`]
            List of signal layers.
        """
        return self.stackup_layers.signal_layers

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
    def materials(self):
        """Materials.

        Returns
        -------
        dict
            Dictionary of materials.
        """
        mats = {}
        for el in self._pedb.edbutils.MaterialSetupInfo.GetFromLayout(self._pedb.active_layout):
            mats[el.Name] = el
        return mats

    @aedt_exception_handler
    def create_dielectric(self, name, permittivity=1, loss_tangent=0):
        """Create a dielectric with simple properties.

        Parameters
        ----------
        name : str
            Name of the dielectic.
        permittivity : float, optional
            Permittivity of the dielectric. The default is ``1``.
        loss_tangent : float, optional
            Loss tangent for the material. The default is ``0``.

        Returns
        -------
        type
            Material definition.
        """
        if self._edb.Definition.MaterialDef.FindByName(self._db, name).IsNull():
            material_def = self._edb.Definition.MaterialDef.Create(self._db, name)
            material_def.SetProperty(
                self._edb.Definition.MaterialPropertyId.Permittivity, self._edb_value(permittivity)
            )
            material_def.SetProperty(
                self._edb.Definition.MaterialPropertyId.DielectricLossTangent, self._edb_value(loss_tangent)
            )
            return material_def
        return False

    @aedt_exception_handler
    def create_conductor(self, name, conductivity=1e6):
        """Create a conductor with simple properties.

        Parameters
        ----------
        name : str
            Name of the conductor.
        conductivity : float, optional
            Conductivity of the conductor. The default is ``1e6``.

        Returns
        -------
        type
            Material definition.
        """
        if self._edb.Definition.MaterialDef.FindByName(self._db, name).IsNull():
            material_def = self._edb.Definition.MaterialDef.Create(self._db, name)
            material_def.SetProperty(
                self._edb.Definition.MaterialPropertyId.Conductivity, self._edb_value(conductivity)
            )
            return material_def
        return False

    @aedt_exception_handler
    def create_debye_material(
        self,
        name,
        relative_permittivity_low,
        relative_permittivity_high,
        loss_tangent_low,
        loss_tangent_high,
        lower_freqency,
        higher_frequency,
    ):
        """Create a dielectric with the Debye model.

        Parameters
        ----------
        name : str
            Name of the dielectic.
        relative_permittivity_low : float
            Relative permittivity of the dielectric at the frequency specified
            for ``lower_frequency``.
        relative_permittivity_high : float
            Relative ermittivity of the dielectric at the frequency specified
            for ``higher_frequency``.
        loss_tangent_low : float
            Loss tangent for the material at the frequency specified
            for ``lower_frequency``.
        loss_tangent_high : float
            Loss tangent for the material at the frequency specified
            for ``higher_frequency``.
        lower_freqency : float
            Value for the lower frequency.
        higher_frequency : float
            Value for the higher frequency.

        Returns
        -------
        type
            Material definition.
        """
        material_def = self._edb.Definition.DebyeModel()
        material_def.SetFrequencyRange(lower_freqency, higher_frequency)
        material_def.SetLossTangentAtHighLowFrequency(loss_tangent_low, loss_tangent_high)
        material_def.SetRelativePermitivityAtHighLowFrequency(
            self._edb_value(relative_permittivity_low), self._edb_value(relative_permittivity_high)
        )
        return self._add_dielectric_material_model(name, material_def)

    @aedt_exception_handler
    def create_multipole_debye_material(
        self,
        name,
        frequencies,
        relative_permittivities,
        loss_tangents,
    ):
        """Create a dielectric with the Multipole Debye model.

        Parameters
        ----------
        name : str
            Name of the dielectic.
        frequencies : list
            Frequencies in GHz.
        relative_permittivities : list
            Relative permittivities at each frequency.
        loss_tangents : list
            Loss tangents at each frequency.

        Returns
        -------
        type
            Material definition.

        Examples
        --------
        >>> from pyaedt import Edb
        >>> edb = Edb()
        >>> freq = [0, 2, 3, 4, 5, 6]
        >>> rel_perm = [1e9, 1.1e9, 1.2e9, 1.3e9, 1.5e9, 1.6e9]
        >>> loss_tan = [0.025, 0.026, 0.027, 0.028, 0.029, 0.030]
        >>> diel = edb.core_stackup.create_multipole_debye_material("My_MP_Debye", freq, rel_perm, loss_tan)
        """
        frequencies = [float(i) for i in frequencies]
        relative_permittivities = [float(i) for i in relative_permittivities]
        loss_tangents = [float(i) for i in loss_tangents]
        material_def = self._edb.Definition.MultipoleDebyeModel()
        material_def.SetParameters(
            convert_py_list_to_net_list(frequencies),
            convert_py_list_to_net_list(relative_permittivities),
            convert_py_list_to_net_list(loss_tangents),
        )
        return self._add_dielectric_material_model(name, material_def)

    @aedt_exception_handler
    def get_top_bottom_elevation_between_designs(
        self, hosting_layout=None, merged_layout=None, place_on_top=True, merged_component=None
    ):
        stackup_target = hosting_layout.GetLayerCollection()
        stackup_source = merged_layout.GetLayerCollection()
        input_layers = self._edb.Cell.LayerTypeSet.SignalLayerSet
        solder_ball_height = 0.0
        if is_ironpython:
            res, topl, topz, bottoml, bottomz = stackup_target.GetTopBottomStackupLayers(input_layers)
            res_s, topl_s, topz_s, bottoml_s, bottomz_s = stackup_source.GetTopBottomStackupLayers(input_layers)
        else:
            topl = None
            topz = Double(0.0)
            bottoml = None
            bottomz = Double(0.0)
            topl_s = None
            topz_s = Double(0.0)
            bottoml_s = None
            bottomz_s = Double(0.0)
            res, topl, topz, bottoml, bottomz = stackup_target.GetTopBottomStackupLayers(
                input_layers, topl, topz, bottoml, bottomz
            )
            res_s, topl_s, topz_s, bottoml_s, bottomz_s = stackup_source.GetTopBottomStackupLayers(
                input_layers, topl_s, topz_s, bottoml_s, bottomz_s
            )
            if merged_component:
                if isinstance(merged_component, str):
                    merged_component_edb = self._edb.Cell.Hierarchy.Component.FindByName(
                        merged_layout, merged_component
                    )
                    merged_sb = self._pedb.core_components.get_solder_ball_height(merged_component_edb)
                    if merged_sb != 0:
                        solder_ball_height = merged_sb
        if place_on_top:
            shift = bottoml.GetThickness() - bottoml_s.GetThickness()
            target_el = topz
            pos_z = target_el - shift + solder_ball_height
        else:
            shift = bottoml.GetThickness() - bottoml_s.GetThickness()
            pos_z = -shift - topz_s - solder_ball_height
        return solder_ball_height

    @aedt_exception_handler
    def adjust_solder_dielectrics(self):
        """Adject the stackup by adding or modifying dielectric layers that contains Solder Balls."""
        for el, val in self._pedb.core_components.components.items():
            if val.solder_ball_height:
                layer = val.placement_layer
                if layer == list(self.signal_layers.keys())[0]:
                    elevation = 0
                    layer1 = layer
                    last_layer_thickess = 0
                    for el in list(self.stackup_layers.layers.keys()):
                        if el == layer:
                            break
                        elevation += self.stackup_layers.layers[el].thickness_value
                        last_layer_thickess = self.stackup_layers.layers[el].thickness_value
                        layer1 = el

                    if layer1 != layer:
                        self.stackup_layers.layers[layer1].thickness_value = (
                            val.solder_ball_height - elevation + last_layer_thickess
                        )
                    elif val.solder_ball_height > elevation:
                        self.stackup_layers.add_layer(
                            "Top_Air",
                            start_layer=layer1,
                            material="air",
                            thickness=val.solder_ball_height - elevation,
                            layerType=1,
                        )
                else:
                    elevation = 0
                    layer1 = layer
                    last_layer_thickess = 0

                    for el in list(self.stackup_layers.layers.keys())[::-1]:
                        if el == layer:
                            break
                        layer1 = el
                        elevation += self.stackup_layers.layers[el].thickness_value
                        last_layer_thickess = self.stackup_layers.layers[el].thickness_value

                    if layer1 != layer:
                        self.stackup_layers.layers[layer1].thickness_value = (
                            val.solder_ball_height - elevation + last_layer_thickess
                        )
                    elif val.solder_ball_height > elevation:
                        self.stackup_layers.add_layer(
                            "Bottom_air",
                            start_layer=None,
                            material="air",
                            thickness=val.solder_ball_height - elevation,
                            layerType=1,
                        )

    @aedt_exception_handler
    def place_in_layout(
        self,
        edb=None,
        angle=0.0,
        offset_x=0.0,
        offset_y=0.0,
        flipped_stackup=True,
        place_on_top=True,
    ):
        """Place current Cell into another cell.
        Flip the current layer stackup of a layout if requested. Transform parameters currently not supported.

        Parameters
        ----------
        edb : Edb
            Cell on which to place the current layout. If None the Cell will be applied on an empty new Cell.
        angle : double
            The rotation angle applied on the design (not supported for the moment).
        offset_x : double
            The x offset value (not supported for the moment.
        offset_y : double
            The y offset value (not supported for the moment.
        flipped_stackup : bool
            Either if the current layout is inverted.
            If `True` and place_on_top is `True` the stackup will be flipped before the merge.
        place_on_top : bool
            Either if place the current layout on Top or Bottom of destination Layout.

        Returns
        -------
        bool
            ``True`` when succeed ``False`` if not.

        Examples
        --------
        >>> edb1 = Edb(edbpath=targetfile1,  edbversion="2021.2")
        >>> edb2 = Edb(edbpath=targetfile2, edbversion="2021.2")

        >>> hosting_cmp = edb1.core_components.get_component_by_name("U100")
        >>> mounted_cmp = edb2.core_components.get_component_by_name("BGA")

        >>> vector, rotation, solder_ball_height = edb1.core_components.get_component_placement_vector(
        ...                                                     mounted_component=mounted_cmp,
        ...                                                     hosting_component=hosting_cmp,
        ...                                                     mounted_component_pin1="A12",
        ...                                                     mounted_component_pin2="A14",
        ...                                                     hosting_component_pin1="A12",
        ...                                                     hosting_component_pin2="A14")
        >>> edb2.core_stackup.place_in_layout(edb1.active_cell, angle=0.0, offset_x=vector[0],
        ...                                   offset_y=vector[1], flipped_stackup=False, place_on_top=True,
        ...                                   solder_height=solder_ball_height)
        """
        # if flipped_stackup and place_on_top or (not flipped_stackup and not place_on_top):
        self.adjust_solder_dielectrics()
        if not place_on_top:
            edb.core_stackup.flip_design()
            place_on_top = True
            if not flipped_stackup:
                self.flip_design()
        elif flipped_stackup:
            self.flip_design()
        edb_cell = edb.active_cell
        _angle = self._edb_value(angle * math.pi / 180.0)
        _offset_x = self._edb_value(offset_x)
        _offset_y = self._edb_value(offset_y)

        if edb_cell.GetName() not in self._pedb.cell_names:
            _dbCell = convert_py_list_to_net_list([edb_cell])
            list_cells = self._pedb.db.CopyCells(_dbCell)
            edb_cell = list_cells[0]
        self._active_layout.GetCell().SetBlackBox(True)
        cell_inst2 = self._edb.Cell.Hierarchy.CellInstance.Create(
            edb_cell.GetLayout(), self._active_layout.GetCell().GetName(), self._active_layout
        )
        cell_trans = cell_inst2.GetTransform()
        cell_trans.SetRotationValue(_angle)
        cell_trans.SetXOffsetValue(_offset_x)
        cell_trans.SetYOffsetValue(_offset_y)
        cell_trans.SetMirror(flipped_stackup)
        cell_inst2.SetTransform(cell_trans)
        cell_inst2.SetSolveIndependentPreference(False)
        stackup_target = edb_cell.GetLayout().GetLayerCollection()

        if place_on_top:
            cell_inst2.SetPlacementLayer(list(stackup_target.Layers(self._edb.Cell.LayerTypeSet.SignalLayerSet))[0])
        else:
            cell_inst2.SetPlacementLayer(list(stackup_target.Layers(self._edb.Cell.LayerTypeSet.SignalLayerSet))[-1])

        return True

    @aedt_exception_handler
    def place_in_layout_3d_placement(
        self,
        edb=None,
        angle=0.0,
        offset_x=0.0,
        offset_y=0.0,
        flipped_stackup=True,
        place_on_top=True,
        solder_height=0,
    ):
        """Place current Cell into another cell.
        Flip the current layer stackup of a layout if requested. Transform parameters currently not supported.

        Parameters
        ----------
        edb : Edb
            Cell on which to place the current layout. If None the Cell will be applied on an empty new Cell.
        angle : double
            The rotation angle applied on the design (not supported for the moment).
        offset_x : double
            The x offset value (not supported for the moment.
        offset_y : double
            The y offset value (not supported for the moment.
        flipped_stackup : bool
            Either if the current layout is inverted.
            If `True` and place_on_top is `True` the stackup will be flipped before the merge.
        place_on_top : bool
            Either if place the current layout on Top or Bottom of destination Layout.
        solder_height : float
            Solder Ball or Bumps eight.
            This value will be added to the elevation to align the two layouts.

        Returns
        -------
        bool
            ``True`` when succeed ``False`` if not.

        Examples
        --------
        >>> edb1 = Edb(edbpath=targetfile1,  edbversion="2021.2")
        >>> edb2 = Edb(edbpath=targetfile2, edbversion="2021.2")

        >>> hosting_cmp = edb1.core_components.get_component_by_name("U100")
        >>> mounted_cmp = edb2.core_components.get_component_by_name("BGA")

        >>> vector, rotation, solder_ball_height = edb1.core_components.get_component_placement_vector(
        ...                                                     mounted_component=mounted_cmp,
        ...                                                     hosting_component=hosting_cmp,
        ...                                                     mounted_component_pin1="A12",
        ...                                                     mounted_component_pin2="A14",
        ...                                                     hosting_component_pin1="A12",
        ...                                                     hosting_component_pin2="A14")
        >>> edb2.core_stackup.place_in_layout(edb1.active_cell, angle=0.0, offset_x=vector[0],
        ...                                   offset_y=vector[1], flipped_stackup=False, place_on_top=True,
        ...                                   solder_height=solder_ball_height)
        """
        # if flipped_stackup and place_on_top or (not flipped_stackup and not place_on_top):
        _angle = angle * math.pi / 180.0

        if flipped_stackup:
            _angle += math.pi
        _angle = self._edb_value(_angle)

        edb_cell = edb.active_cell
        _offset_x = self._edb_value(offset_x)
        _offset_y = self._edb_value(offset_y)

        if edb_cell.GetName() not in self._pedb.cell_names:
            _dbCell = convert_py_list_to_net_list([edb_cell])
            list_cells = self._pedb.db.CopyCells(_dbCell)
            edb_cell = list_cells[0]
        self._active_layout.GetCell().SetBlackBox(True)
        cell_inst2 = self._edb.Cell.Hierarchy.CellInstance.Create(
            edb_cell.GetLayout(), self._active_layout.GetCell().GetName(), self._active_layout
        )

        stackup_target = edb_cell.GetLayout().GetLayerCollection()
        stackup_source = self._active_layout.GetLayerCollection()

        if place_on_top:
            cell_inst2.SetPlacementLayer(list(stackup_target.Layers(self._edb.Cell.LayerTypeSet.SignalLayerSet))[0])
        else:
            cell_inst2.SetPlacementLayer(list(stackup_target.Layers(self._edb.Cell.LayerTypeSet.SignalLayerSet))[-1])
        cell_inst2.SetIs3DPlacement(True)
        input_layers = self._edb.Cell.LayerTypeSet.SignalLayerSet
        if is_ironpython:
            res, topl, topz, bottoml, bottomz = stackup_target.GetTopBottomStackupLayers(input_layers)
            res_s, topl_s, topz_s, bottoml_s, bottomz_s = stackup_source.GetTopBottomStackupLayers(input_layers)
        else:
            topl = None
            topz = Double(0.0)
            bottoml = None
            bottomz = Double(0.0)
            topl_s = None
            topz_s = Double(0.0)
            bottoml_s = None
            bottomz_s = Double(0.0)
            res, topl, topz, bottoml, bottomz = stackup_target.GetTopBottomStackupLayers(
                input_layers, topl, topz, bottoml, bottomz
            )
            res_s, topl_s, topz_s, bottoml_s, bottomz_s = stackup_source.GetTopBottomStackupLayers(
                input_layers, topl_s, topz_s, bottoml_s, bottomz_s
            )

        if place_on_top:
            if flipped_stackup:
                h_stackup = self._edb_value(topz + solder_height + topz_s)
            else:
                h_stackup = self._edb_value(topz + solder_height - bottomz_s)
        elif flipped_stackup:
            h_stackup = self._edb_value(bottomz - solder_height - bottomz_s)
        else:
            h_stackup = self._edb_value(bottomz - solder_height - topz_s)

        zero_data = self._edb_value(0.0)
        one_data = self._edb_value(1.0)
        point3d_t = self._edb.Geometry.Point3DData(_offset_x, _offset_y, h_stackup)
        point_loc = self._edb.Geometry.Point3DData(zero_data, zero_data, zero_data)
        point_from = self._edb.Geometry.Point3DData(zero_data, one_data, zero_data)
        point_to = self._edb.Geometry.Point3DData(zero_data, one_data, zero_data)
        cell_inst2.Set3DTransformation(point_loc, point_from, point_to, _angle, point3d_t)
        return True

    @aedt_exception_handler
    def flip_design(self):
        """
        Flip the current design of a layout.
        Returns
        -------
        bool
            ``True`` when succeed ``False`` if not.

        Examples
        --------
        >>> edb = Edb(edbpath=targetfile,  edbversion="2021.2")
        >>> edb.core_stackup.flip_design()
        >>> edb.save()
        >>> edb.close_edb()
        """
        try:

            lc = self._active_layout.GetLayerCollection()
            new_lc = self._edb.Cell.LayerCollection()
            lc_mode = lc.GetMode()
            new_lc.SetMode(lc_mode)
            max_elevation = 0.0
            for layer in lc.Layers(self._edb.Cell.LayerTypeSet.StackupLayerSet):
                if not "RadBox" in layer.GetName():  # Ignore RadBox
                    lower_elevation = layer.GetLowerElevation() * 1.0e6
                    upper_elevation = layer.GetUpperElevation() * 1.0e6
                    max_elevation = max([max_elevation, lower_elevation, upper_elevation])

            non_stackup_layers = []
            for layer in lc.Layers(self._edb.Cell.LayerTypeSet.AllLayerSet):
                cloned_layer = layer.Clone()
                if not cloned_layer.IsStackupLayer():
                    non_stackup_layers.append(cloned_layer)
                    continue
                if not "RadBox" in layer.GetName() and not layer.IsViaLayer():
                    upper_elevation = layer.GetUpperElevation() * 1.0e6
                    updated_lower_el = max_elevation - upper_elevation
                    val = self._edb_value("{}um".format(updated_lower_el))
                    cloned_layer.SetLowerElevation(val)
                    if cloned_layer.GetTopBottomAssociation() == self._edb.Cell.TopBottomAssociation.TopAssociated:
                        cloned_layer.SetTopBottomAssociation(self._edb.Cell.TopBottomAssociation.BottomAssociated)
                    else:
                        cloned_layer.SetTopBottomAssociation(self._edb.Cell.TopBottomAssociation.TopAssociated)
                    new_lc.AddStackupLayerAtElevation(cloned_layer)

            vialayers = [lay for lay in lc.Layers(self._edb.Cell.LayerTypeSet.StackupLayerSet) if lay.IsViaLayer()]
            for layer in vialayers:
                cloned_via_layer = layer.Clone()
                upper_ref_name = layer.GetRefLayerName(True)
                lower_ref_name = layer.GetRefLayerName(False)
                upper_ref = [
                    lay for lay in lc.Layers(self._edb.Cell.LayerTypeSet.AllLayerSet) if lay.GetName() == upper_ref_name
                ][0]
                lower_ref = [
                    lay for lay in lc.Layers(self._edb.Cell.LayerTypeSet.AllLayerSet) if lay.GetName() == lower_ref_name
                ][0]
                cloned_via_layer.SetRefLayer(lower_ref, True)
                cloned_via_layer.SetRefLayer(upper_ref, False)
                ref_layer_in_flipped_stackup = [
                    lay
                    for lay in new_lc.Layers(self._edb.Cell.LayerTypeSet.AllLayerSet)
                    if lay.GetName() == upper_ref_name
                ][0]
                via_layer_lower_elevation = (
                    ref_layer_in_flipped_stackup.GetLowerElevation() + ref_layer_in_flipped_stackup.GetThickness()
                )
                cloned_via_layer.SetLowerElevation(self._edb_value(via_layer_lower_elevation))
                new_lc.AddStackupLayerAtElevation(cloned_via_layer)

            layer_list = convert_py_list_to_net_list(non_stackup_layers)
            new_lc.AddLayers(layer_list)
            if not self._active_layout.SetLayerCollection(new_lc):
                self._logger.error("Failed to Flip Stackup.")
                return False
            cmp_list = [cmp for cmp in self._active_layout.Groups if cmp.GetComponent() is not None]
            for cmp in cmp_list:
                cmp_type = cmp.GetComponentType()
                cmp_prop = cmp.GetComponentProperty().Clone()
                if cmp_type == self._edb.Definition.ComponentType.IC:
                    die_prop = cmp_prop.GetDieProperty().Clone()
                    chip_orientation = die_prop.GetOrientation()
                    if chip_orientation == self._edb.Definition.DieOrientation.ChipDown:
                        die_prop.SetOrientation(self._edb.Definition.DieOrientation.ChipUp)
                        cmp_prop.SetDieProperty(die_prop)
                    else:
                        die_prop.SetOrientation(self._edb.Definition.DieOrientation.ChipDown)
                        cmp_prop.SetDieProperty(die_prop)
                cmp.SetComponentProperty(cmp_prop)

            lay_list = list(new_lc.Layers(self._edb.Cell.LayerTypeSet.SignalLayerSet))
            for padstack in list(self._pedb.core_padstack.padstack_instances.values()):
                start_layer_id = [lay.GetLayerId() for lay in list(lay_list) if lay.GetName() == padstack.start_layer]
                stop_layer_id = [lay.GetLayerId() for lay in list(lay_list) if lay.GetName() == padstack.stop_layer]
                layer_map = padstack._edb_padstackinstance.GetLayerMap()
                layer_map.SetMapping(stop_layer_id[0], start_layer_id[0])
                padstack._edb_padstackinstance.SetLayerMap(layer_map)
            self.stackup_layers._update_edb_objects()
            return True
        except:
            return False

    @aedt_exception_handler
    def create_djordjevicsarkar_material(self, name, relative_permittivity, loss_tangent, test_frequency):
        """Create a Djordjevic_Sarkar dielectric.

        Parameters
        ----------
        name : str
            Name of the dielectic.
        relative_permittivity : float
            Relative permittivity of the dielectric.
        loss_tangent : float
            Loss tangent for the material.
        test_frequency : float
            Test frequency in GHz for the dielectric.

        Returns
        -------
        type
            Material definition.
        """
        material_def = self._edb.Definition.DjordjecvicSarkarModel()
        material_def.SetFrequency(test_frequency)
        material_def.SetLossTangentAtFrequency(self._edb_value(loss_tangent))
        material_def.SetRelativePermitivityAtFrequency(relative_permittivity)
        return self._add_dielectric_material_model(name, material_def)

    @aedt_exception_handler
    def _add_dielectric_material_model(self, name, material_model):
        if self._edb.Definition.MaterialDef.FindByName(self._db, name).IsNull():
            DieDef = self._edb.Definition.MaterialDef.Create(self._db, name)
            succeeded = DieDef.SetDielectricMaterialModel(material_model)
            if succeeded:
                return DieDef
            return False

    @aedt_exception_handler
    def stackup_limits(self, only_metals=False):
        """Retrieve stackup limits.

        Parameters
        ----------
        only_metals : bool, optional
            Whether to retrieve only metals. The default is ``False``.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.
        """
        stackup = self._active_layout.GetLayerCollection()
        if only_metals:
            input_layers = self._edb.Cell.LayerTypeSet.SignalLayerSet
        else:
            input_layers = self._edb.Cell.LayerTypeSet.StackupLayerSet

        if is_ironpython:
            res, topl, topz, bottoml, bottomz = stackup.GetTopBottomStackupLayers(input_layers)
        else:
            topl = None
            topz = Double(0.0)
            bottoml = None
            bottomz = Double(0.0)
            res, topl, topz, bottoml, bottomz = stackup.GetTopBottomStackupLayers(
                input_layers, topl, topz, bottoml, bottomz
            )
        h_stackup = abs(float(topz) - float(bottomz))
        return topl.GetName(), topz, bottoml.GetName(), bottomz
