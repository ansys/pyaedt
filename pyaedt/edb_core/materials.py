from __future__ import absolute_import  # noreorder

import logging
import warnings

from pyaedt import is_ironpython
from pyaedt.edb_core.general import convert_py_list_to_net_list
from pyaedt.generic.general_methods import pyaedt_function_handler

try:
    import clr
except ImportError:
    warnings.warn("This module requires the PythonNET package.")

logger = logging.getLogger(__name__)


class Material(object):
    """Manages EDB methods for material property management."""

    def __init__(self, pclass, edb_material_def):
        self._pclass = pclass
        self._name = edb_material_def.GetName()
        self._edb_material_def = edb_material_def

    def _edb_value(self, value):
        return self._pclass._edb_value(value)

    @property
    def name(self):
        """Retrieve material name."""
        return self._name

    @property
    def _db(self):
        return self._pclass._db

    @property
    def _edb(self):
        return self._pclass._edb

    @pyaedt_function_handler()
    def _get_property(self, property_name):
        if is_ironpython:  # pragma: no cover
            property_box = clr.StrongBox[float]()
            self._edb_material_def.GetProperty(property_name, property_box)
            return float(property_box)
        else:
            _, property_box = self._edb_material_def.GetProperty(property_name)
            return property_box.ToDouble()

    @property
    def conductivity(self):
        material_id = self._edb.Definition.MaterialPropertyId.Conductivity
        return self._get_property(material_id)

    @conductivity.setter
    def conductivity(self, value):
        """Retrieve material conductivity."""
        material_id = self._edb.Definition.MaterialPropertyId.Conductivity
        self._edb_material_def.SetProperty(material_id, self._edb_value(value))

    @property
    def permittivity(self):
        """Retrieve material permittivity."""
        material_id = self._edb.Definition.MaterialPropertyId.Permittivity
        return self._get_property(material_id)

    @permittivity.setter
    def permittivity(self, value):
        material_id = self._edb.Definition.MaterialPropertyId.Permittivity
        self._edb_material_def.SetProperty(material_id, self._edb_value(value))

    @property
    def permeability(self):
        """Retrieve material permeability."""
        material_id = self._edb.Definition.MaterialPropertyId.Permeability
        return self._get_property(material_id)

    @permeability.setter
    def permeability(self, value):
        material_id = self._edb.Definition.MaterialPropertyId.Permeability
        self._edb_material_def.SetProperty(material_id, self._edb_value(value))

    @property
    def loss_tangent(self):
        """Retrieve material loss tangent."""
        material_id = self._edb.Definition.MaterialPropertyId.DielectricLossTangent
        return self._get_property(material_id)

    @loss_tangent.setter
    def loss_tangent(self, value):
        material_id = self._edb.Definition.MaterialPropertyId.DielectricLossTangent
        self._edb_material_def.SetProperty(material_id, self._edb_value(value))

    @property
    def magnetic_loss_tangent(self):
        """Retrieve material magnetic loss tangent."""
        material_id = self._edb.Definition.MaterialPropertyId.MagneticLossTangent
        return self._get_property(material_id)

    @magnetic_loss_tangent.setter
    def magnetic_loss_tangent(self, value):
        material_id = self._edb.Definition.MaterialPropertyId.MagneticLossTangent
        self._edb_material_def.SetProperty(material_id, self._edb_value(value))

    @property
    def thermal_conductivity(self):
        """Retrieve material thermal conductivity."""
        material_id = self._edb.Definition.MaterialPropertyId.ThermalConductivity
        return self._get_property(material_id)

    @thermal_conductivity.setter
    def thermal_conductivity(self, value):
        material_id = self._edb.Definition.MaterialPropertyId.ThermalConductivity
        self._edb_material_def.SetProperty(material_id, self._edb_value(value))

    @property
    def mass_density(self):
        """Retrieve material mass density."""
        material_id = self._edb.Definition.MaterialPropertyId.MassDensity
        return self._get_property(material_id)

    @mass_density.setter
    def mass_density(self, value):
        material_id = self._edb.Definition.MaterialPropertyId.MassDensity
        self._edb_material_def.SetProperty(material_id, self._edb_value(value))

    @property
    def youngs_modulus(self):
        """Retrieve material Young's Modulus."""
        material_id = self._edb.Definition.MaterialPropertyId.YoungsModulus
        return self._get_property(material_id)

    @youngs_modulus.setter
    def youngs_modulus(self, value):
        material_id = self._edb.Definition.MaterialPropertyId.YoungsModulus
        self._edb_material_def.SetProperty(material_id, self._edb_value(value))

    @property
    def specific_heat(self):
        """Retrieve material Specific Heat."""
        material_id = self._edb.Definition.MaterialPropertyId.SpecificHeat
        return self._get_property(material_id)

    @specific_heat.setter
    def specific_heat(self, value):
        material_id = self._edb.Definition.MaterialPropertyId.SpecificHeat
        self._edb_material_def.SetProperty(material_id, self._edb_value(value))

    @property
    def poisson_ratio(self):
        """Retrieve material Poisson Ratio."""
        material_id = self._edb.Definition.MaterialPropertyId.PoissonsRatio
        return self._get_property(material_id)

    @poisson_ratio.setter
    def poisson_ratio(self, value):
        material_id = self._edb.Definition.MaterialPropertyId.PoissonsRatio
        self._edb_material_def.SetProperty(material_id, self._edb_value(value))

    @property
    def thermal_expansion_coefficient(self):
        """Retrieve material Thermal Coefficient.."""
        material_id = self._edb.Definition.MaterialPropertyId.ThermalExpansionCoefficient
        return self._get_property(material_id)

    @thermal_expansion_coefficient.setter
    def thermal_expansion_coefficient(self, value):
        material_id = self._edb.Definition.MaterialPropertyId.ThermalExpansionCoefficient
        self._edb_material_def.SetProperty(material_id, self._edb_value(value))


class Materials(object):
    """Manages EDB methods for material management accessible from `Edb.materials` property."""

    def __getitem__(self, item):
        return self.materials[item]

    def __init__(self, pedb):
        self._pedb = pedb

    @pyaedt_function_handler()
    def _edb_value(self, value):
        return self._pedb.edb_value(value)

    @property
    def _edb(self):
        return self._pedb.edb

    @property
    def _db(self):
        return self._pedb.db

    @property
    def materials(self):
        """Retrieve dictionary of material from material library."""
        return {obj.GetName(): Material(self, obj) for obj in list(self._db.MaterialDefs)}

    @pyaedt_function_handler()
    def add_conductor_material(self, name, conductivity, permittivity, loss_tangent):
        """Add a new material in library.

        Parameters
        ----------
        name : str
            Name of the new material.
        conductivity : float
            Conductivity of the new material.
        permittivity : float
            Permittivity of the new material.
        loss_tangent : float
            Loss tangent of the new material.
        Returns
        -------

        """
        if not name in self.materials:
            self._edb.Definition.MaterialDef.Create(self._db, name)
            new_material = self.materials[name]
            new_material.conductivity = conductivity
            new_material.permittivity = permittivity
            new_material.loss_tangent = loss_tangent
            return new_material
        else:
            warnings.warn("Material {} already exists in material library.".format(name))
            return False

    @pyaedt_function_handler()
    def add_djordjevicsarkar_material(self, name, relative_permittivity, loss_tangent, test_frequency):
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

    @pyaedt_function_handler()
    def add_debye_material(
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

    @pyaedt_function_handler()
    def add_multipole_debye_material(
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
    def _add_dielectric_material_model(self, name, material_model):
        if self._edb.Definition.MaterialDef.FindByName(self._db, name).IsNull():
            DieDef = self._edb.Definition.MaterialDef.Create(self._db, name)
            succeeded = DieDef.SetDielectricMaterialModel(material_model)
            if succeeded:
                return DieDef
            return False

    @pyaedt_function_handler()
    def duplicate(self, material_name, new_material_name):
        """Duplicate a material from the database.


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
        if material_name in self.materials:
            permittivity = self._edb_value(self.materials[material_name].permittivity)
            permeability = self._edb_value(self.materials[material_name].permeability)
            conductivity = self._edb_value(self.materials[material_name].conductivity)
            dielectric_loss_tangent = self._edb_value(self.materials[material_name].loss_tangent)
            magnetic_loss_tangent = self._edb_value(self.materials[material_name].magnetic_loss_tangent)
            thermal_conductivity = self._edb_value(self.materials[material_name].thermal_conductivity)
            thermal_expansion_coefficient = self._edb_value(self.materials[material_name].thermal_expansion_coefficient)
            youngs_modulus = self._edb_value(self.materials[material_name].youngs_modulus)
            poisson_ratio = self._edb_value(self.materials[material_name].poisson_ratio)
            mass_density = self._edb_value(self.materials[material_name].mass_density)
            material_model = self.materials[material_name]._edb_material_def.GetDielectricMaterialModel()
            edb_material = self._edb.Definition.MaterialDef.Create(self._db, new_material_name)
            edb_material.SetProperty(self._edb.Definition.MaterialPropertyId.Permittivity, permittivity)
            edb_material.SetProperty(self._edb.Definition.MaterialPropertyId.Permeability, permeability)
            edb_material.SetProperty(self._edb.Definition.MaterialPropertyId.Conductivity, conductivity)
            edb_material.SetProperty(
                self._edb.Definition.MaterialPropertyId.DielectricLossTangent, dielectric_loss_tangent
            )
            edb_material.SetProperty(self._edb.Definition.MaterialPropertyId.ThermalConductivity, thermal_conductivity)
            edb_material.SetProperty(
                self._edb.Definition.MaterialPropertyId.ThermalExpansionCoefficient, thermal_expansion_coefficient
            )
            edb_material.SetProperty(self._edb.Definition.MaterialPropertyId.MassDensity, mass_density)
            edb_material.SetProperty(self._edb.Definition.MaterialPropertyId.YoungsModulus, youngs_modulus)
            edb_material.SetProperty(self._edb.Definition.MaterialPropertyId.PoissonsRatio, poisson_ratio)
            edb_material.SetProperty(self._edb.Definition.MaterialPropertyId.MagneticLossTangent, magnetic_loss_tangent)
            edb_material.SetProperty(self._edb.Definition.MaterialPropertyId.MagneticLossTangent, magnetic_loss_tangent)
            edb_material.SetDielectricMaterialModel(material_model)

            return edb_material
