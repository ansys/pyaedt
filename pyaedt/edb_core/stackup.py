"""
This module contains the `EdbStackup` class.

"""

from __future__ import absolute_import  # noreorder

import difflib
import logging
import math
import warnings

from pyaedt.edb_core.EDB_Data import EDBLayers
from pyaedt.edb_core.EDB_Data import SimulationConfiguration
from pyaedt.edb_core.general import convert_py_list_to_net_list
from pyaedt.generic.general_methods import is_ironpython
from pyaedt.generic.general_methods import pyaedt_function_handler

try:
    import clr
except ImportError:
    warnings.warn("This module requires the PythonNET package.")

logger = logging.getLogger(__name__)


class EdbStackup(object):
    """Manages EDB methods for stackup and material management accessible from `Edb.core_stackup` property.

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

    def _get_edb_value(self, value):
        return self._pedb.edb_value(value)

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

    @pyaedt_function_handler()
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
                self._edb.Definition.MaterialPropertyId.Permittivity,
                self._get_edb_value(permittivity),
            )
            material_def.SetProperty(
                self._edb.Definition.MaterialPropertyId.DielectricLossTangent,
                self._get_edb_value(loss_tangent),
            )
            return material_def
        return False

    @pyaedt_function_handler()
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
                self._edb.Definition.MaterialPropertyId.Conductivity, self._get_edb_value(conductivity)
            )
            return material_def
        return False

    @pyaedt_function_handler()
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
            self._get_edb_value(relative_permittivity_low), self._get_edb_value(relative_permittivity_high)
        )
        return self._add_dielectric_material_model(name, material_def)

    @pyaedt_function_handler()
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

    @pyaedt_function_handler()
    def get_layout_thickness(self):
        """Return the layout thickness.

        Returns
        --------
        Float, the thickness value.
        """
        layers_name = list(self.stackup_layers.layers.keys())
        bottom_layer = self.stackup_layers.layers[layers_name[0]]
        top_layer = self.stackup_layers.layers[layers_name[-1]]
        thickness = top_layer.lower_elevation + top_layer.thickness_value - bottom_layer.lower_elevation
        return thickness

    @pyaedt_function_handler()
    def duplicate_material(self, material_name, new_material_name):
        """Duplicate a material from the database.
        It duplicates these five properties: ``permittivity``, ``permeability``, ` conductivity,``
        ``dielectriclosstangent``, and ``magneticlosstangent``.

        Parameters
        ----------
        material_name : str
            Name of the existing material.
        new_material_name : str
            Name of the new duplicated material.

        Returns
        -------
        EDB material : class: 'Ansys.Ansoft.Edb.Definition.MaterialDef'


        Examples
        --------

        >>> from pyaedt import Edb
        >>> edb_app = Edb()
        >>> my_material = edb_app.core_stackup.duplicate_material("copper", "my_new_copper")

        """
        if self._edb.Definition.MaterialDef.FindByName(self._db, material_name).IsNull():
            self._logger.error("This material doesn't exists.")
        else:
            permittivity = self._get_edb_value(self.get_property_by_material_name("permittivity", material_name))
            permeability = self._get_edb_value(
                self.get_property_by_material_name(
                    "permeability",
                    material_name,
                )
            )
            conductivity = self._get_edb_value(
                self.get_property_by_material_name(
                    "conductivity",
                    material_name,
                )
            )
            dielectric_loss_tangent = self._get_edb_value(
                self.get_property_by_material_name("dielectric_loss_tangent", material_name)
            )
            magnetic_loss_tangent = self._get_edb_value(
                self.get_property_by_material_name("magnetic_loss_tangent", material_name)
            )
            edb_material = self._edb.Definition.MaterialDef.Create(self._db, new_material_name)
            edb_material.SetProperty(self._edb.Definition.MaterialPropertyId.Permittivity, permittivity)
            edb_material.SetProperty(self._edb.Definition.MaterialPropertyId.Permeability, permeability)
            edb_material.SetProperty(self._edb.Definition.MaterialPropertyId.Conductivity, conductivity)
            edb_material.SetProperty(
                self._edb.Definition.MaterialPropertyId.DielectricLossTangent, dielectric_loss_tangent
            )
            edb_material.SetProperty(self._edb.Definition.MaterialPropertyId.MagneticLossTangent, magnetic_loss_tangent)
            return edb_material

    @pyaedt_function_handler
    def material_name_to_id(self, property_name):
        """Convert a material property name to a material property ID.

        Parameters
        ----------
        property_name : str
            Name of the material property.

        Returns
        -------
        ID of the material property.
        """
        props = {
            "Permittivity": self._edb.Definition.MaterialPropertyId.Permittivity,
            "Permeability": self._edb.Definition.MaterialPropertyId.Permeability,
            "Conductivity": self._edb.Definition.MaterialPropertyId.Conductivity,
            "DielectricLossTangent": self._edb.Definition.MaterialPropertyId.DielectricLossTangent,
            "MagneticLossTangent": self._edb.Definition.MaterialPropertyId.MagneticLossTangent,
            "ThermalConductivity": self._edb.Definition.MaterialPropertyId.ThermalConductivity,
            "MassDensity": self._edb.Definition.MaterialPropertyId.MassDensity,
            "SpecificHeat": self._edb.Definition.MaterialPropertyId.SpecificHeat,
            "YoungsModulus": self._edb.Definition.MaterialPropertyId.YoungsModulus,
            "PoissonsRatio": self._edb.Definition.MaterialPropertyId.PoissonsRatio,
            "ThermalExpansionCoefficient": self._edb.Definition.MaterialPropertyId.ThermalExpansionCoefficient,
            "InvalidProperty": self._edb.Definition.MaterialPropertyId.InvalidProperty,
        }

        found_el = difflib.get_close_matches(property_name, list(props.keys()), 1, 0.7)
        if found_el:
            return props[found_el[0]]
        else:
            return self._edb.Definition.MaterialPropertyId.InvalidProperty

    @pyaedt_function_handler()
    def get_property_by_material_name(self, property_name, material_name):
        """Get the property of a material. If it is executed in IronPython,
         you must only use the first element of the returned tuple, which is a float.

        Parameters
        ----------
        material_name : str
            Name of the existing material.
        property_name : str
            Name of the material property.
            ``permittivity``
            ``permeability``
            ``conductivity``
            ``dielectric_loss_tangent``
            ``magnetic_loss_tangent``

        Returns
        -------
        float
            the float value of the property.


        Examples
        --------
        >>> from pyaedt import Edb
        >>> edb_app = Edb()
        >>> returned_tuple = edb_app.core_stackup.get_property_by_material_name("conductivity", "copper")
        >>> edb_value = returned_tuple[0]
        >>> float_value = returned_tuple[1]

        """
        if self._edb.Definition.MaterialDef.FindByName(self._db, material_name).IsNull():
            self._logger.error("This material doesn't exists.")
        else:
            original_material = self._edb.Definition.MaterialDef.FindByName(self._db, material_name)
            if is_ironpython:  # pragma: no cover
                property_box = clr.StrongBox[float]()
                original_material.GetProperty(self.material_name_to_id(property_name), property_box)
                return float(property_box)
            else:
                _, property_box = original_material.GetProperty(
                    self.material_name_to_id(property_name), self._get_edb_value(0.0)
                )
                return property_box.ToDouble()
        return False

    @pyaedt_function_handler()
    def _get_solder_height(self, layer_name):
        for el, val in self._pedb.core_components.components.items():
            if val.solder_ball_height and val.placement_layer == layer_name:
                return val.solder_ball_height
        return 0

    @pyaedt_function_handler()
    def _remove_solder_pec(self, layer_name):
        for el, val in self._pedb.core_components.components.items():
            if val.solder_ball_height and val.placement_layer == layer_name:
                comp_prop = val.component_property
                port_property = comp_prop.GetPortProperty().Clone()
                port_property.SetReferenceSizeAuto(False)
                port_property.SetReferenceSize(self._get_edb_value(0.0), self._get_edb_value(0.0))
                comp_prop.SetPortProperty(port_property)
                val.edbcomponent.SetComponentProperty(comp_prop)

    @pyaedt_function_handler()
    def adjust_solder_dielectrics(self):
        """Adjust the stack-up by adding or modifying dielectric layers that contains Solder Balls.
        This method identifies the solder-ball height and adjust the dielectric thickness on top (or bottom) to fit
        the thickness in order to merge another layout.

        Returns
        -------
        bool
        """
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
        return True

    @pyaedt_function_handler()
    def place_in_layout(
        self,
        edb,
        angle=0.0,
        offset_x=0.0,
        offset_y=0.0,
        flipped_stackup=True,
        place_on_top=True,
    ):
        """Place current Cell into another cell using layer placement method.
        Flip the current layer stackup of a layout if requested. Transform parameters currently not supported.

        Parameters
        ----------
        edb : Edb
            Cell on which to place the current layout. If None the Cell will be applied on an empty new Cell.
        angle : double, optional
            The rotation angle applied on the design.
        offset_x : double, optional
            The x offset value.
        offset_y : double, optional
            The y offset value.
        flipped_stackup : bool, optional
            Either if the current layout is inverted.
            If `True` and place_on_top is `True` the stackup will be flipped before the merge.
        place_on_top : bool, optional
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
        ...                                   )
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
        _angle = self._get_edb_value(angle * math.pi / 180.0)
        _offset_x = self._get_edb_value(offset_x)
        _offset_y = self._get_edb_value(offset_y)

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

    @pyaedt_function_handler()
    def place_in_layout_3d_placement(
        self,
        edb,
        angle=0.0,
        offset_x=0.0,
        offset_y=0.0,
        flipped_stackup=True,
        place_on_top=True,
        solder_height=0,
    ):
        """Place current Cell into another cell using 3d placement method.
        Flip the current layer stackup of a layout if requested. Transform parameters currently not supported.

        Parameters
        ----------
        edb : Edb
            Cell on which to place the current layout. If None the Cell will be applied on an empty new Cell.
        angle : double, optional
            The rotation angle applied on the design.
        offset_x : double, optional
            The x offset value.
        offset_y : double, optional
            The y offset value.
        flipped_stackup : bool, optional
            Either if the current layout is inverted.
            If `True` and place_on_top is `True` the stackup will be flipped before the merge.
        place_on_top : bool, optional
            Either if place the current layout on Top or Bottom of destination Layout.
        solder_height : float, optional
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
        >>> edb2.core_stackup.place_in_layout(edb1.active_cell, angle=0.0, offset_x="1mm",
        ...                                   offset_y="2mm", flipped_stackup=False, place_on_top=True,
        ...                                   )
        """
        _angle = angle * math.pi / 180.0

        if solder_height <= 0:
            if flipped_stackup and not place_on_top or (place_on_top and not flipped_stackup):
                minimum_elevation = None
                for lay in self.signal_layers.values():
                    if minimum_elevation is None:
                        minimum_elevation = lay.lower_elevation
                    elif lay.lower_elevation > minimum_elevation:
                        break
                    lay_solder_height = self._get_solder_height(lay.name)
                    solder_height = max(lay_solder_height, solder_height)
                    self._remove_solder_pec(lay.name)
            else:
                maximum_elevation = None
                layers_from_the_top = sorted(self.signal_layers.values(), key=lambda lay: -lay.upper_elevation)
                for lay in layers_from_the_top:
                    if maximum_elevation is None:
                        maximum_elevation = lay.upper_elevation
                    elif lay.upper_elevation < maximum_elevation:
                        break
                    lay_solder_height = self._get_solder_height(lay.name)
                    solder_height = max(lay_solder_height, solder_height)
                    self._remove_solder_pec(lay.name)

        rotation = self._get_edb_value(0.0)
        if flipped_stackup:
            rotation = self._get_edb_value(math.pi)

        edb_cell = edb.active_cell
        _offset_x = self._get_edb_value(offset_x)
        _offset_y = self._get_edb_value(offset_y)

        if edb_cell.GetName() not in self._pedb.cell_names:
            _dbCell = convert_py_list_to_net_list([edb_cell])
            list_cells = self._pedb.db.CopyCells(_dbCell)
            edb_cell = list_cells[0]
        self._active_layout.GetCell().SetBlackBox(True)
        cell_inst2 = self._edb.Cell.Hierarchy.CellInstance.Create(
            edb_cell.GetLayout(), self._active_layout.GetCell().GetName(), self._active_layout
        )

        stackup_target = self._edb.Cell.LayerCollection(edb_cell.GetLayout().GetLayerCollection())
        stackup_source = self._edb.Cell.LayerCollection(self._active_layout.GetLayerCollection())

        if place_on_top:
            cell_inst2.SetPlacementLayer(list(stackup_target.Layers(self._edb.Cell.LayerTypeSet.SignalLayerSet))[0])
        else:
            cell_inst2.SetPlacementLayer(list(stackup_target.Layers(self._edb.Cell.LayerTypeSet.SignalLayerSet))[-1])
        cell_inst2.SetIs3DPlacement(True)
        sig_set = self._edb.Cell.LayerTypeSet.SignalLayerSet
        res = stackup_target.GetTopBottomStackupLayers(sig_set)
        target_top_elevation = res[2]
        target_bottom_elevation = res[4]
        res_s = stackup_source.GetTopBottomStackupLayers(sig_set)
        source_stack_top_elevation = res_s[2]
        source_stack_bot_elevation = res_s[4]

        if place_on_top and flipped_stackup:
            elevation = target_top_elevation + source_stack_top_elevation
        elif place_on_top:
            elevation = target_top_elevation - source_stack_bot_elevation
        elif flipped_stackup:
            elevation = target_bottom_elevation + source_stack_bot_elevation
            solder_height = -solder_height
        else:
            elevation = target_bottom_elevation - source_stack_top_elevation
            solder_height = -solder_height

        h_stackup = self._get_edb_value(elevation + solder_height)

        zero_data = self._get_edb_value(0.0)
        one_data = self._get_edb_value(1.0)
        point3d_t = self._edb.Geometry.Point3DData(_offset_x, _offset_y, h_stackup)
        point_loc = self._edb.Geometry.Point3DData(zero_data, zero_data, zero_data)
        point_from = self._edb.Geometry.Point3DData(one_data, zero_data, zero_data)
        point_to = self._edb.Geometry.Point3DData(
            self._get_edb_value(math.cos(_angle)), self._get_edb_value(-1 * math.sin(_angle)), zero_data
        )
        cell_inst2.Set3DTransformation(point_loc, point_from, point_to, rotation, point3d_t)
        return True

    @pyaedt_function_handler()
    def place_a3dcomp_3d_placement(self, a3dcomp_path, angle=0.0, offset_x=0.0, offset_y=0.0, place_on_top=True):
        """Place current Cell into another cell using 3d placement method.
        Flip the current layer stackup of a layout if requested. Transform parameters currently not supported.

        Parameters
        ----------
        a3dcomp_path : str
            Path to 3D Component file (*.a3dcomp) to place.
        angle : double, optional
            Clockwise rotation angle applied to the a3dcomp.
        offset_x : double, optional
            The x offset value.
        offset_y : double, optional
            The y offset value.
        place_on_top : bool, optional
            Whether to place the 3D Component on the top or bottom of this layout.
            If False then the 3D Component will also be flipped over around its X axis.

        Returns
        -------
        bool
            ``True`` if successful and ``False`` if not.

        Examples
        --------
        >>> edb1 = Edb(edbpath=targetfile1,  edbversion="2021.2")
        >>> a3dcomp_path = "connector.a3dcomp"
        >>> edb1.core_stackup.place_a3dcomp_3d_placement(a3dcomp_path, angle=0.0, offset_x="1mm",
        ...                                   offset_y="2mm", flipped_stackup=False, place_on_top=True,
        ...                                   )
        """
        zero_data = self._get_edb_value(0.0)
        one_data = self._get_edb_value(1.0)
        local_origin = self._edb.Geometry.Point3DData(zero_data, zero_data, zero_data)
        rotation_axis_from = self._edb.Geometry.Point3DData(one_data, zero_data, zero_data)
        _angle = angle * math.pi / 180.0
        rotation_axis_to = self._edb.Geometry.Point3DData(
            self._get_edb_value(math.cos(_angle)), self._get_edb_value(-1 * math.sin(_angle)), zero_data
        )

        stackup_target = self._edb.Cell.LayerCollection(self._active_layout.GetLayerCollection())
        sig_set = self._edb.Cell.LayerTypeSet.SignalLayerSet
        res = stackup_target.GetTopBottomStackupLayers(sig_set)
        target_top_elevation = res[2]
        target_bottom_elevation = res[4]
        flip_angle = self._get_edb_value("0deg")
        if place_on_top:
            elevation = target_top_elevation
        else:
            flip_angle = self._get_edb_value("180deg")
            elevation = target_bottom_elevation
        h_stackup = self._get_edb_value(elevation)
        location = self._edb.Geometry.Point3DData(
            self._get_edb_value(offset_x), self._get_edb_value(offset_y), h_stackup
        )

        mcad_model = self._edb.McadModel.Create3DComp(self._active_layout, a3dcomp_path)
        if mcad_model.IsNull():  # pragma: no cover
            logger.error("Failed to create MCAD model from a3dcomp")
            return False

        cell_instance = mcad_model.GetCellInstance()
        if cell_instance.IsNull():  # pragma: no cover
            logger.error("Cell instance of a3dcomp is null")
            return False

        if not cell_instance.SetIs3DPlacement(True):  # pragma: no cover
            logger.error("Failed to set 3D placement on a3dcomp cell instance")
            return False

        if not cell_instance.Set3DTransformation(
            local_origin, rotation_axis_from, rotation_axis_to, flip_angle, location
        ):  # pragma: no cover
            logger.error("Failed to set 3D transform on a3dcomp cell instance")
            return False

        return True

    @pyaedt_function_handler()
    def flip_design(self):
        """Flip the current design of a layout.

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
                    val = self._get_edb_value("{}um".format(updated_lower_el))
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
                cloned_via_layer.SetLowerElevation(self._get_edb_value(via_layer_lower_elevation))
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
                try:
                    if (
                        cmp_prop.GetSolderBallProperty().GetPlacement()
                        == self._edb.Definition.SolderballPlacement.AbovePadstack
                    ):
                        sball_prop = cmp_prop.GetSolderBallProperty().Clone()
                        sball_prop.SetPlacement(self._edb.Definition.SolderballPlacement.BelowPadstack)
                        cmp_prop.SetSolderBallProperty(sball_prop)
                    elif (
                        cmp_prop.GetSolderBallProperty().GetPlacement()
                        == self._edb.Definition.SolderballPlacement.BelowPadstack
                    ):
                        sball_prop = cmp_prop.GetSolderBallProperty().Clone()
                        sball_prop.SetPlacement(self._edb.Definition.SolderballPlacement.AbovePadstack)
                        cmp_prop.SetSolderBallProperty(sball_prop)
                except:
                    pass
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

    @pyaedt_function_handler()
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
        material_def.SetLossTangentAtFrequency(self._get_edb_value(loss_tangent))
        material_def.SetRelativePermitivityAtFrequency(relative_permittivity)
        return self._add_dielectric_material_model(name, material_def)

    @pyaedt_function_handler()
    def _add_dielectric_material_model(self, name, material_model):
        if self._edb.Definition.MaterialDef.FindByName(self._db, name).IsNull():
            DieDef = self._edb.Definition.MaterialDef.Create(self._db, name)
            succeeded = DieDef.SetDielectricMaterialModel(material_model)
            if succeeded:
                return DieDef
            return False

    @pyaedt_function_handler()
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
        stackup = self._edb.Cell.LayerCollection(self._active_layout.GetLayerCollection())
        if only_metals:
            input_layers = self._edb.Cell.LayerTypeSet.SignalLayerSet
        else:
            input_layers = self._edb.Cell.LayerTypeSet.StackupLayerSet

        res, topl, topz, bottoml, bottomz = stackup.GetTopBottomStackupLayers(input_layers)
        return topl.GetName(), topz, bottoml.GetName(), bottomz

    def create_symmetric_stackup(
        self,
        layer_count,
        inner_layer_thickness="17um",
        outer_layer_thickness="50um",
        dielectric_thickness="100um",
        dielectric_material="FR4_epoxy",
        soldermask=True,
        soldermask_thickness="20um",
    ):
        """Create a symmetric stackup.

        Parameters
        ----------
        layer_count : int
            Number of layer count.
        inner_layer_thickness : str, float, optional
            Thickness of inner conductor layer.
        outer_layer_thickness : str, float, optional
            Thickness of outer conductor layer.
        dielectric_thickness : str, float, optional
            Thickness of dielectric layer.
        dielectric_material : str, optional
            Material of dielectric layer.
        soldermask : bool, optional
            Whether to create soldermask layers. The default is``True``.
        soldermask_thickness : str, optional
            Thickness of soldermask layer.
        Returns
        -------
        bool
        """
        if not layer_count % 2 == 0:
            return False

        if soldermask:
            self.stackup_layers.add_layer("SMB", None, "SolderMask", thickness=soldermask_thickness, layerType=1)
            layer_name = "BOTTOM"
            self.stackup_layers.add_layer(layer_name, "SMB", fillMaterial="SolderMask", thickness=outer_layer_thickness)
        else:
            layer_name = "BOTTOM"
            self.stackup_layers.add_layer(layer_name, fillMaterial="Air", thickness=outer_layer_thickness)

        for layer in range(layer_count - 1, 1, -1):
            new_layer_name = "D" + str(layer - 1)
            self.stackup_layers.add_layer(
                new_layer_name, layer_name, dielectric_material, thickness=dielectric_thickness, layerType=1
            )
            layer_name = new_layer_name
            new_layer_name = "L" + str(layer - 1)
            self.stackup_layers.add_layer(
                new_layer_name, layer_name, "copper", dielectric_material, inner_layer_thickness
            )
            layer_name = new_layer_name

        new_layer_name = "D1"
        self.stackup_layers.add_layer(
            new_layer_name, layer_name, dielectric_material, thickness=dielectric_thickness, layerType=1
        )
        layer_name = new_layer_name

        if soldermask:
            new_layer_name = "TOP"
            self.stackup_layers.add_layer(
                new_layer_name, layer_name, fillMaterial="SolderMask", thickness=outer_layer_thickness
            )
            layer_name = new_layer_name
            self.stackup_layers.add_layer("SMT", layer_name, "SolderMask", thickness=soldermask_thickness, layerType=1)
        else:
            new_layer_name = "TOP"
            self.stackup_layers.add_layer(
                new_layer_name, layer_name, fillMaterial="Air", thickness=outer_layer_thickness
            )
        return True

    @pyaedt_function_handler()
    def set_etching_layers(self, simulation_setup=None):
        """Set the etching layer parameters for a layout stackup.

        Parameters
        ----------
        simulation_setup : EDB_DATA_SimulationConfiguration object

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.
        """
        if not isinstance(simulation_setup, SimulationConfiguration):
            return False
        cell = self._builder.cell
        this_lc = self._edb.Cell.LayerCollection(cell.GetLayout().GetLayerCollection())
        all_layers = list(this_lc.Layers(self._edb.Cell.LayerTypeSet.AllLayerSet))

        signal_layers = [lay for lay in all_layers if lay.GetLayerType() == self._edb.Cell.LayerType.SignalLayer]

        new_layers = list(all_layers.Where(lambda lyr: lyr.GetLayerType() != self._edb.Cell.LayerType.SignalLayer))

        if simulation_setup.signal_layer_etching_instances:
            for layer in signal_layers:
                if not layer.GetName() in simulation_setup.signal_layer_etching_instances:
                    self._logger.error(
                        "Signal layer {0} is not found in the etching layers specified in the cfg, "
                        "skipping the etching factor assignment".format(layer.GetName())
                    )
                    new_signal_lay = layer.Clone()
                else:
                    new_signal_lay = layer.Clone()
                    new_signal_lay.SetEtchFactorEnabled(True)
                    etching_factor = float(
                        simulation_setup.etching_factor_instances[
                            simulation_setup.signal_layer_etching_instances.index(layer.GetName())
                        ]
                    )
                    new_signal_lay.SetEtchFactor(etching_factor)
                    self._logger.info(
                        "Setting etching factor {0} on layer {1}".format(str(etching_factor), layer.GetName())
                    )

                new_layers.Add(new_signal_lay)

            layers_with_etching = self._edb.Cell.LayerCollection()
            if not layers_with_etching.AddLayers(new_layers):
                return False

            if not cell.GetLayout().SetLayerCollection(layers_with_etching):
                return False

            return True
        return True
