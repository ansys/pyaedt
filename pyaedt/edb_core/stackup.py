"""
This module contains the `EdbStackup` class.

"""
from __future__ import absolute_import

import math
import warnings

from pyaedt.edb_core.EDB_Data import EDBLayers
from pyaedt.edb_core.general import convert_py_list_to_net_list
from pyaedt.generic.general_methods import aedt_exception_handler, is_ironpython

try:
    from System import Double
except ImportError:
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
        dict
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
        list
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
    def flip_stackup_and_apply_transform(self, angle=0.0, offset_x=0.0, offset_y=0.0, mirror=True):
        """Flip the current layer stackup of a layout. Transform parameters currently not supported.

        Parameters
        ----------
        angle : double
            The rotation angle applied on the design (not supported for the moment).
        offset_x : double
            The x offset value (not supported for the moment.
        offset_y : double
            The y offset value (not supported for the moment.
        mirror : bool
            mirror the flipped design, default value True (not supported for the moment.

        Returns
        -------
        bool
            ``True`` when succeed ``False`` if not.
        """
        lc = self._active_layout.GetLayerCollection()
        new_lc = self._edb.Cell.LayerCollection()
        max_elevation = 0.0
        for layer in lc.Layers(self._edb.Cell.LayerTypeSet.StackupLayerSet):
            if not 'RadBox' in layer.GetName():  # Ignore RadBox
                lower_elevation = layer.GetLowerElevation() * 1.0e6
                upper_elevation = layer.GetUpperElevation() * 1.0e6
                max_elevation = max([max_elevation, lower_elevation, upper_elevation])

        non_stackup_layers = []
        for layer in lc.Layers(self._edb.Cell.LayerTypeSet.AllLayerSet):
            cloned_layer = layer.Clone()
            if not cloned_layer.IsStackupLayer():
                non_stackup_layers.append(cloned_layer)
                continue

            if not 'RadBox' in layer.GetName():
                upper_elevation = layer.GetUpperElevation() * 1.0e6
                updated_lower_el = max_elevation - upper_elevation
                val = self._edb_value("{}um".format(updated_lower_el))
                cloned_layer.SetLowerElevation(val)
                new_lc.AddStackupLayerAtElevation(cloned_layer)

        layer_list = convert_py_list_to_net_list(non_stackup_layers)
        new_lc.AddLayers(layer_list)
        if self._active_layout.SetLayerCollection(new_lc):
            cell_name = self._active_layout.GetCell().GetName()
            cell_inst = self._edb.Cell.Hierarchy.CellInstance.FindByName(self._active_layout, cell_name)
            cell_trans = cell_inst.GetTransform()
            _angle = self._edb_value(angle * math.pi / 180.0)
            _offset_x = self._edb_value(offset_x)
            _offset_y = self._edb_value(offset_y)
            cell_trans.SetRotationValue(_angle)
            cell_trans.SetXOffsetValue(_offset_x)
            cell_trans.SetYOffsetValue(_offset_y)
            cell_trans.SetMirror(mirror)
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
            return True

        else:
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