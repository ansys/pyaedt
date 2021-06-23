"""
This module contains the ``EdbStackup`` class.

"""
from __future__ import absolute_import
import warnings
from .general import *

try:
    from System import Double
    from System.Collections.Generic import List
except ImportError:
    warnings.warn('This module requires pythonnet.')


from .EDB_Data import EDBLayers, EDBLayer


class EdbStackup(object):
    """EdbStackup class."""

    def __init__(self, parent):
        self.parent = parent
        self._layer_dict = None

    @property
    def builder(self):
        """ """
        return self.parent.builder

    @property
    def edb_value(self):
        """ """
        return self.parent.edb_value

    @property
    def edb(self):
        """ """
        return self.parent.edb

    @property
    def active_layout(self):
        """ """
        return self.parent.active_layout

    @property
    def cell(self):
        """ """
        return self.parent.cell

    @property
    def db(self):
        """ """
        return self.parent.db

    @property
    def stackup_methods(self):
        """ """
        return self.parent.edblib.Layout.StackupMethods

    @property
    def stackup_layers(self):
        """List all stackup layers.
        
        Parameters
        ----------

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
        """

        Parameters
        ----------

        Returns
        -------
        list
            List of signal layers.

        """
        return self.stackup_layers.signal_layers



    @property
    def materials(self):
        """:return: Dictionary of Materials"""
        mats = {}
        for el in self.parent.edbutils.MaterialSetupInfo.GetFromLayout(self.parent.active_layout):
            mats[el.Name] = el
        return mats

    @aedt_exception_handler
    def create_dielectric(self, name, permittivity=1, loss_tangent=0):
        """Create a new dielectric with simple properties.

        Parameters
        ----------
        name : str
            Name of the dielectic.
        permittivity : float, optional
            Permittivity of the dielectric.
        loss_tangent : float
            Loss tangent for the material. 

        Returns
        -------
        type
        Material definition.
        
        """
        if self.edb.Definition.MaterialDef.FindByName(self.db, name).IsNull():
            material_def = self.edb.Definition.MaterialDef.Create(self.db,name)
            material_def.SetProperty(self.edb.Definition.MaterialPropertyId.Permittivity,
                                                self.edb_value(permittivity))
            material_def.SetProperty(self.edb.Definition.MaterialPropertyId.DielectricLossTangent,self.edb_value(loss_tangent))
            return material_def
        return False

    @aedt_exception_handler
    def create_conductor(self, name, conductivity=1e6):
        """Create a new conductor with simple properties.

        Parameters
        ----------
        name: str
            Name of the conductor.
        conductivity : float, optional
            Conductivity of the conductor. The default is ``1e6``.

        Returns
        -------
        type
        Material definition.
        
        """
        if self.edb.Definition.MaterialDef.FindByName(self.db, name).IsNull():
            material_def = self.edb.Definition.MaterialDef.Create(self.db, name)
            material_def.SetProperty(self.edb.Definition.MaterialPropertyId.Conductivity,
                                     self.edb_value(conductivity))
            return material_def
        return False

    @aedt_exception_handler
    def create_debye_material(self, name, relative_permittivity_low, relative_permittivity_high, loss_tangent_low, loss_tangent_high, lower_freqency, higher_frequency):
        """Create a new dielectric with the Debye model.

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
            Value to use for lower frequency.
        higher_frequency: float
            Value to use for higher frequency.

        Returns
        -------
        type
        Material definition.
        """
        material_def = self.edb.Definition.DebyeModel()
        material_def.SetFrequencyRange(lower_freqency, higher_frequency)
        material_def.SetLossTangentAtHighLowFrequency(loss_tangent_low, loss_tangent_high)
        material_def.SetRelativePermitivityAtHighLowFrequency(self.edb_value(relative_permittivity_low),
                                                              self.edb_value(relative_permittivity_high))
        return self._add_dielectric_material_model(name, material_def)



    @aedt_exception_handler
    def create_djordjevicsarkar_material(self, name, relative_permittivity, loss_tangent, test_frequency):
        """Create a new Djordjevic_Sarkar dielectric.

        Parameters
        ----------
        name : str
            Name of the dielectic.
        relative_permittivity : float
            Relative permittivity of the dielectric.
        loss_tangent : float
            Loss tangent for the material.
        test_frequency : float
            Test frequency for the dielectric in GHz.

        Returns
        -------
        type
        Material definition.
        
        """
        material_def = self.edb.Definition.DjordjecvicSarkarModel()
        material_def.SetFrequency(test_frequency)
        material_def.SetLossTangentAtFrequency(self.edb_value(loss_tangent))
        material_def.SetRelativePermitivityAtFrequency(relative_permittivity)
        return self._add_dielectric_material_model(name, material_def)

    @aedt_exception_handler
    def _add_dielectric_material_model(self, name, material_model):
        if self.edb.Definition.MaterialDef.FindByName(self.db, name).IsNull():
            DieDef = self.edb.Definition.MaterialDef.Create(self.db, name)
            succeeded = DieDef.SetDielectricMaterialModel(material_model)
            if succeeded:
                return DieDef
            return False


    @aedt_exception_handler
    def stackup_limits(self, only_metals=False):
        """

        Parameters
        ----------
        only_metals : bool, optional
            The default is ``False``.

        Returns
        -------

        """
        stackup = self.builder.EdbHandler.layout.GetLayerCollection()
        if only_metals:
            input_layers = self.parent.edb.Cell.LayerTypeSet.SignalLayerSet
        else:
            input_layers = self.parent.edb.Cell.LayerTypeSet.StackupLayerSet

        if is_ironpython:
            res, topl, topz, bottoml, bottomz = stackup.GetTopBottomStackupLayers(input_layers)
        else:
            topl = None
            topz = Double(0.)
            bottoml = None
            bottomz = Double(0.)
            res, topl, topz, bottoml, bottomz = stackup.GetTopBottomStackupLayers(input_layers, topl, topz, bottoml, bottomz)
        h_stackup = abs(float(topz) - float(bottomz))
        return topl.GetName(), topz, bottoml.GetName(), bottomz
