from __future__ import absolute_import  # noreorder

import logging
import warnings

try:
    import clr
except ImportError:
    warnings.warn("This module requires the PythonNET package.")

logger = logging.getLogger(__name__)


class Material(object):
    """Manages EDB methods for material management accessible from `Edb.material` property."""

    class _material:
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

        @property
        def conductivity(self):
            material_id = self._edb.Definition.MaterialPropertyId.Conductivity
            _, value = self._edb_material_def.GetProperty(material_id)
            return value.ToDouble()

        @conductivity.setter
        def conductivity(self, value):
            """Retrieve material conductivity."""
            material_id = self._edb.Definition.MaterialPropertyId.Conductivity
            self._edb_material_def.SetProperty(material_id, self._edb_value(value))

        @property
        def permittivity(self):
            """Retrieve material permittivity."""
            material_id = self._edb.Definition.MaterialPropertyId.Permittivity
            _, value = self._edb_material_def.GetProperty(material_id)
            return value.ToDouble()

        @permittivity.setter
        def permittivity(self, value):
            material_id = self._edb.Definition.MaterialPropertyId.Permittivity
            self._edb_material_def.SetProperty(material_id, self._edb_value(value))

        @property
        def loss_tangent(self):
            """Retrieve material loss tangent."""
            material_id = self._edb.Definition.MaterialPropertyId.DielectricLossTangent
            _, value = self._edb_material_def.GetProperty(material_id)
            return value.ToDouble()

        @loss_tangent.setter
        def loss_tangent(self, value):
            material_id = self._edb.Definition.MaterialPropertyId.DielectricLossTangent
            self._edb_material_def.SetProperty(material_id, self._edb_value(value))

        @property
        def thermal_conductivity(self):
            """Retrieve material thernal conductivity."""
            material_id = self._edb.Definition.MaterialPropertyId.ThermalConductivity
            _, value = self._edb_material_def.GetProperty(material_id)
            return value.ToDouble()

    def __getitem__(self, item):
        return self.material[item]

    def __init__(self, pedb):
        self._pedb = pedb

    def _edb_value(self, value):
        return self._pedb.edb_value(value)

    @property
    def _edb(self):
        return self._pedb.edb

    @property
    def _db(self):
        return self._pedb.db

    @property
    def material(self):
        """Retrieve dictionary of material from material library."""
        return {obj.GetName(): self._material(self, obj) for obj in list(self._db.MaterialDefs)}

    def add_material(self, name, conductivity, permittivity, loss_tangent):
        """Add a new material in library.

        Parameters
        ----------
        name : str
            Name of the new material.
        conductivity : float
            conductivity of the new material.
        permittivity : float
            Permittivity of the new material.
        loss_tangent : float
            Loss tangent of the new material.
        Returns
        -------

        """
        if not name in self.material:
            self._edb.Definition.MaterialDef.Create(self._db, name)
            new_material = self.material[name]
            new_material.conductivity = conductivity
            new_material.permittivity = permittivity
            new_material.loss_tangent = loss_tangent
            return new_material
        else:
            warnings.warn("Material {} already exist in material library.".format(name))
            return False
