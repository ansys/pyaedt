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
        """List of all signal layers.

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
    def place_in_layout(
        self,
        edb_cell=None,
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
        edb_cell : Cell
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
        if flipped_stackup and place_on_top or (not flipped_stackup and not place_on_top):
            model_flip = True
        else:
            model_flip = False
        if model_flip:
            lc = self._active_layout.GetLayerCollection()
            new_lc = self._edb.Cell.LayerCollection()
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

                if not "RadBox" in layer.GetName():
                    upper_elevation = layer.GetUpperElevation() * 1.0e6
                    updated_lower_el = max_elevation - upper_elevation
                    val = self._edb_value("{}um".format(updated_lower_el))
                    cloned_layer.SetLowerElevation(val)
                    new_lc.AddStackupLayerAtElevation(cloned_layer)

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

        _angle = self._edb_value(angle * math.pi / 180.0)
        _offset_x = self._edb_value(offset_x)
        _offset_y = self._edb_value(offset_y)
        edb_was_none = False
        if edb_cell is None:
            cell_name = self._active_layout.GetCell().GetName()
            self._active_layout.GetCell().SetName(cell_name + "_Transform")
            edb_cell = self._edb.Cell.Cell.Create(self._db, self._edb.Cell.CellType.CircuitCell, cell_name)
            edb_cell.GetLayout().SetLayerCollection(self._active_layout.GetLayerCollection())
            edb_was_none = True
            cell_inst2 = self._edb.Cell.Hierarchy.CellInstance.Create(
                edb_cell.GetLayout(), edb_cell.GetName() + "_Transform", self._active_layout
            )
        else:
            if edb_cell.GetName() not in self._pedb.cell_names:
                _dbCell = convert_py_list_to_net_list([edb_cell])
                list_cells = self._pedb.db.CopyCells(_dbCell)
                edb_cell = list_cells[0]
            cell_inst2 = self._edb.Cell.Hierarchy.CellInstance.Create(
                edb_cell.GetLayout(), self._active_layout.GetCell().GetName(), self._active_layout
            )

        cell_trans = cell_inst2.GetTransform()
        cell_trans.SetRotationValue(_angle)
        cell_trans.SetXOffsetValue(_offset_x)
        cell_trans.SetYOffsetValue(_offset_y)
        cell_trans.SetMirror(model_flip)
        cell_inst2.SetTransform(cell_trans)
        cell_inst2.SetSolveIndependentPreference(True)
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
            h_stackup = self._edb_value(topz + solder_height - bottomz_s)
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
