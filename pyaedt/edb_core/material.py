
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


class Material(object):
    class _material:
        def __init__(self, pclass, edb_material_def):
            self._pclass = pclass
            self._name = edb_material_def.GetName()
            self._edb_material_def = edb_material_def

        def _edb_value(self, value):
            return self._pclass._edb_value(value)

        @property
        def name(self):
            return self._name

        @property
        def _db(self):
            return self._pclass._db

        @property
        def _edb(self):
            return self._pclass._edb

        @property
        def primitivity(self):
            material_id = self._edb.Definition.MaterialPropertyId.Permittivity
            _, value = self._edb_material_def.GetProperty(material_id)
            return value.ToDouble()

        @primitivity.setter
        def primitivity(self, value):
            material_id = self._edb.Definition.MaterialPropertyId.Permittivity
            self._edb_material_def.SetProperty(material_id, self._edb_value(value))

        @property
        def dielectric_loss_tangent(self):
            material_id = self._edb.Definition.MaterialPropertyId.DielectricLossTangent
            _, value = self._edb_material_def.GetProperty(material_id)
            return value.ToDouble()

        @dielectric_loss_tangent.setter
        def dielectric_loss_tangent(self, value):
            material_id = self._edb.Definition.MaterialPropertyId.DielectricLossTangent
            self._edb_material_def.SetProperty(material_id, self._edb_value(value))

        @property
        def thermal_conductivity(self):
            material_id = self._edb.Definition.MaterialPropertyId.ThermalConductivity
            _, value = self._edb_material_def.GetProperty(material_id)
            return value.ToDouble()

        @property
        def mass_density(self):
            material_id = self._edb.Definition.MaterialPropertyId.MassDensity
            _, value = self._edb_material_def.GetProperty(material_id)
            return value.ToDouble()

        @property
        def specific_heat(self):
            material_id = self._edb.Definition.MaterialPropertyId.SpecificHeat
            _, value = self._edb_material_def.GetProperty(material_id)
            return value.ToDouble()

        @property
        def youngs_modulus(self):
            material_id = self._edb.Definition.MaterialPropertyId.YoungsModulus
            _, value = self._edb_material_def.GetProperty(material_id)
            return value.ToDouble()

        @property
        def poissons_ratio(self):
            material_id = self._edb.Definition.MaterialPropertyId.DielectricLossTangent
            _, value = self._edb_material_def.GetProperty(material_id)
            return value.ToDouble()

        @property
        def thermal_expansion_coefficient(self):
            material_id = self._edb.Definition.MaterialPropertyId.DielectricLossTangent
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
        return {obj.GetName(): self._material(self, obj) for obj in list(self._db.MaterialDefs)}

    def add_material(self, name):
        self._edb.Definition.MaterialDef.Create(self._db, name)
        self.material[name]
