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
        self._conductivty = 0.0
        self._loss_tangent = 0.0
        self._magnetic_loss_tangent = 0.0
        self._mass_density = 0.0
        self._permittivity = 0.0
        self._permeability = 0.0
        self._poisson_ratio = 0.0
        self._specific_heat = 0.0
        self._thermal_conductivity = 0.0
        self._youngs_modulus = 0.0
        self._thermal_expansion_coefficient = 0.0
        self._dc_conductivity = 0.0
        self._dc_permittivity = 0.0
        self._dielectric_model_frequency = 0.0
        self._loss_tangent_at_frequency = 0.0
        self._permittivity_at_frequency = 0.0

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
        self._conductivty = self._get_property(material_id)
        return self._conductivty

    @conductivity.setter
    def conductivity(self, value):
        """Retrieve material conductivity."""
        material_id = self._edb.Definition.MaterialPropertyId.Conductivity
        self._edb_material_def.SetProperty(material_id, self._edb_value(value))
        self._conductivty = value

    @property
    def permittivity(self):
        """Retrieve material permittivity."""
        material_id = self._edb.Definition.MaterialPropertyId.Permittivity
        self._permittivity = self._get_property(material_id)
        return self._permittivity

    @permittivity.setter
    def permittivity(self, value):
        material_id = self._edb.Definition.MaterialPropertyId.Permittivity
        self._edb_material_def.SetProperty(material_id, self._edb_value(value))
        self._permittivity = value

    @property
    def permeability(self):
        """Retrieve material permeability."""
        material_id = self._edb.Definition.MaterialPropertyId.Permeability
        self._permeability = self._get_property(material_id)
        return self._permeability

    @permeability.setter
    def permeability(self, value):
        material_id = self._edb.Definition.MaterialPropertyId.Permeability
        self._edb_material_def.SetProperty(material_id, self._edb_value(value))
        self._permeability = value

    @property
    def loss_tangent(self):
        """Retrieve material loss tangent."""
        material_id = self._edb.Definition.MaterialPropertyId.DielectricLossTangent
        self._loss_tangent = self._get_property(material_id)
        return self._loss_tangent

    @loss_tangent.setter
    def loss_tangent(self, value):
        material_id = self._edb.Definition.MaterialPropertyId.DielectricLossTangent
        self._edb_material_def.SetProperty(material_id, self._edb_value(value))
        self._loss_tangent = value

    @property
    def dc_conductivity(self):
        """"""
        if self._edb_material_def.GetDielectricMaterialModel():
            return self._edb_material_def.GetDielectricMaterialModel().GetDCConductivity()

    @dc_conductivity.setter
    def dc_conductivity(self, value):
        if self._edb_material_def.GetDielectricMaterialModel():
            self._edb_material_def.GetDielectricMaterialModel().GetDCConductivity().SetDCConductivity(
                self._edb_value(value)
            )

    @property
    def dc_permittivity(self):
        """"""
        if self._edb_material_def.GetDielectricMaterialModel():
            return self._edb_material_def.GetDielectricMaterialModel().GetDCConductivity()

    @dc_permittivity.setter
    def dc_permittivity(self, value):
        if self._edb_material_def.GetDielectricMaterialModel():
            self._edb_material_def.GetDielectricMaterialModel().SetDCRelativePermitivity(self._edb_value(value))

    @property
    def dielectric_model_frequency(self):
        """"""
        if self._edb_material_def.GetDielectricMaterialModel():
            return self._edb_material_def.GetDielectricMaterialModel().GetFrequency()

    @dielectric_model_frequency.setter
    def dielectric_model_frequency(self, value):
        if self._edb_material_def.GetDielectricMaterialModel():
            self._edb_material_def.GetDielectricMaterialModel().SetDCRelativePermitivity(self._edb_value(value))

    @property
    def loss_tangent_at_frequency(self):
        if self._edb_material_def.GetDielectricMaterialModel():
            return self._edb_material_def.GetDielectricMaterialModel().GetLossTangentAtFrequency()

    @loss_tangent_at_frequency.setter
    def loss_tangent_at_frequency(self, value):
        if self._edb_material_def.GetDielectricMaterialModel():
            self._edb_material_def.GetDielectricMaterialModel().SetLossTangentAtFrequency(self._edb_value(value))

    @property
    def permittivity_at_frequency(self):
        if self._edb_material_def.GetDielectricMaterialModel():
            return self._edb_material_def.GetDielectricMaterialModel().GetRelativePermitivityAtFrequency()

    @permittivity_at_frequency.setter
    def permittivity_at_frequency(self, value):
        if self._edb_material_def.GetDielectricMaterialModel():
            self._edb_material_def.GetDielectricMaterialModel().SetRelativePermitivityAtFrequency(
                self._edb_value(value)
            )

    @property
    def magnetic_loss_tangent(self):
        """Retrieve material magnetic loss tangent."""
        material_id = self._edb.Definition.MaterialPropertyId.MagneticLossTangent
        self._magnetic_loss_tangent = self._get_property(material_id)
        return self._magnetic_loss_tangent

    @magnetic_loss_tangent.setter
    def magnetic_loss_tangent(self, value):
        material_id = self._edb.Definition.MaterialPropertyId.MagneticLossTangent
        self._edb_material_def.SetProperty(material_id, self._edb_value(value))
        self._magnetic_loss_tangent = value

    @property
    def thermal_conductivity(self):
        """Retrieve material thermal conductivity."""
        material_id = self._edb.Definition.MaterialPropertyId.ThermalConductivity
        self._thermal_conductivity = self._get_property(material_id)
        return self._thermal_conductivity

    @thermal_conductivity.setter
    def thermal_conductivity(self, value):
        material_id = self._edb.Definition.MaterialPropertyId.ThermalConductivity
        self._edb_material_def.SetProperty(material_id, self._edb_value(value))
        self._thermal_conductivity = value

    @property
    def mass_density(self):
        """Retrieve material mass density."""
        material_id = self._edb.Definition.MaterialPropertyId.MassDensity
        self._mass_density = self._get_property(material_id)
        return self._mass_density

    @mass_density.setter
    def mass_density(self, value):
        material_id = self._edb.Definition.MaterialPropertyId.MassDensity
        self._edb_material_def.SetProperty(material_id, self._edb_value(value))
        self._mass_density = value

    @property
    def youngs_modulus(self):
        """Retrieve material Young's Modulus."""
        material_id = self._edb.Definition.MaterialPropertyId.YoungsModulus
        self._youngs_modulus = self._get_property(material_id)
        return self._youngs_modulus

    @youngs_modulus.setter
    def youngs_modulus(self, value):
        material_id = self._edb.Definition.MaterialPropertyId.YoungsModulus
        self._edb_material_def.SetProperty(material_id, self._edb_value(value))
        self._youngs_modulus = value

    @property
    def specific_heat(self):
        """Retrieve material Specific Heat."""
        material_id = self._edb.Definition.MaterialPropertyId.SpecificHeat
        self._specific_heat = self._get_property(material_id)
        return self._specific_heat

    @specific_heat.setter
    def specific_heat(self, value):
        material_id = self._edb.Definition.MaterialPropertyId.SpecificHeat
        self._edb_material_def.SetProperty(material_id, self._edb_value(value))
        self._specific_heat = value

    @property
    def poisson_ratio(self):
        """Retrieve material Poisson Ratio."""
        material_id = self._edb.Definition.MaterialPropertyId.PoissonsRatio
        self._poisson_ratio = self._get_property(material_id)
        return self._poisson_ratio

    @poisson_ratio.setter
    def poisson_ratio(self, value):
        material_id = self._edb.Definition.MaterialPropertyId.PoissonsRatio
        self._edb_material_def.SetProperty(material_id, self._edb_value(value))
        self._poisson_ratio = value

    @property
    def thermal_expansion_coefficient(self):
        """Retrieve material Thermal Coefficient.."""
        material_id = self._edb.Definition.MaterialPropertyId.ThermalExpansionCoefficient
        self._thermal_expansion_coefficient = self._get_property(material_id)
        return self._thermal_expansion_coefficient

    @thermal_expansion_coefficient.setter
    def thermal_expansion_coefficient(self, value):
        material_id = self._edb.Definition.MaterialPropertyId.ThermalExpansionCoefficient
        self._edb_material_def.SetProperty(material_id, self._edb_value(value))
        self._thermal_expansion_coefficient = value

    @pyaedt_function_handler()
    def _json_format(self):
        out_dict = {}
        self._name = self.name
        self._conductivty = self.conductivity
        self._loss_tangent = self.loss_tangent
        self._magnetic_loss_tangent = self.magnetic_loss_tangent
        self._mass_density = self.mass_density
        self._permittivity = self.permittivity
        self._permeability = self.permeability
        self._poisson_ratio = self.poisson_ratio
        self._specific_heat = self.specific_heat
        self._thermal_conductivity = self.thermal_conductivity
        self._youngs_modulus = self.youngs_modulus
        self._thermal_expansion_coefficient = self.thermal_expansion_coefficient
        self._dc_conductivity = self.dc_conductivity
        self._dc_permittivity = self.dc_permittivity
        self._dielectric_model_frequency = self.dielectric_model_frequency
        self._loss_tangent_at_frequency = self.loss_tangent_at_frequency
        self._permittivity_at_frequency = self.permittivity_at_frequency
        for k, v in self.__dict__.items():
            if not k == "_pclass" and not k == "_edb_material_def":
                out_dict[k[1:]] = v
        return out_dict


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
    def add_conductor_material(self, name, conductivity):
        """Add a new conductor material in library.

        Parameters
        ----------
        name : str
            Name of the new material.
        conductivity : float
            Conductivity of the new material.
        -------

        """
        if not name in self.materials:
            self._edb.Definition.MaterialDef.Create(self._db, name)
            new_material = self.materials[name]
            new_material.conductivity = conductivity
            return new_material
        else:  # pragma: no cover
            warnings.warn("Material {} already exists in material library.".format(name))
            return False

    @pyaedt_function_handler()
    def add_dielectric_material(self, name, permittivity, loss_tangent):
        """Add a new dielectric material in library.

        Parameters
        ----------
        name : str
            Name of the new material.
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
            new_material.permittivity = permittivity
            new_material.loss_tangent = loss_tangent
            return new_material
        else:
            warnings.warn("Material {} already exists in material library.".format(name))
            return False

    @pyaedt_function_handler()
    def get_djordjevicsarkar_model(self, material_name=None):
        """

        Parameters
        ----------
        material_name

        Returns
        -------

        """
        material = self.materials[material_name]
        if material:
            return material.GetDielectricMaterialModel()

    @pyaedt_function_handler()
    def add_djordjevicsarkar_material(self, name, permittivity, loss_tangent, test_frequency):
        """Create a Djordjevic_Sarkar dielectric.

        Parameters
        ----------
        name : str
            Name of the dielectic.
        permittivity : float
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
        material_def.SetRelativePermitivityAtFrequency(permittivity)
        return self._add_dielectric_material_model(name, material_def)

    @pyaedt_function_handler()
    def add_debye_material(
        self,
        name,
        permittivity_low,
        permittivity_high,
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
        permittivity_low : float
            Relative permittivity of the dielectric at the frequency specified
            for ``lower_frequency``.
        permittivity_high : float
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
            self._edb_value(permittivity_low), self._edb_value(permittivity_high)
        )
        return self._add_dielectric_material_model(name, material_def)

    @pyaedt_function_handler()
    def add_multipole_debye_material(
        self,
        name,
        frequencies,
        permittivities,
        loss_tangents,
    ):
        """Create a dielectric with the Multipole Debye model.

        Parameters
        ----------
        name : str
            Name of the dielectic.
        frequencies : list
            Frequencies in GHz.
        permittivities : list
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
        permittivities = [float(i) for i in permittivities]
        loss_tangents = [float(i) for i in loss_tangents]
        material_def = self._edb.Definition.MultipoleDebyeModel()
        material_def.SetParameters(
            convert_py_list_to_net_list(frequencies),
            convert_py_list_to_net_list(permittivities),
            convert_py_list_to_net_list(loss_tangents),
        )
        return self._add_dielectric_material_model(name, material_def)

    @pyaedt_function_handler()
    def _add_dielectric_material_model(self, name, material_model):
        if self._edb.Definition.MaterialDef.FindByName(self._db, name).IsNull():
            self._edb.Definition.MaterialDef.Create(self._db, name)
        material_def = self._edb.Definition.MaterialDef.FindByName(self._db, name)
        succeeded = material_def.SetDielectricMaterialModel(material_model)
        if succeeded:
            return material_def
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
