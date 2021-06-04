"""
EdbStackup Class
-------------------

This class manages Edb Stackup and related methods




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
    """Stackup object"""

    def __init__(self, parent):
        self.parent = parent
        self._layer_dict = None

    @property
    def builder(self):
        """ """
        return self.parent.builder

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
        """Get all stackup layers
        
        :return: list of all stackup layers

        Parameters
        ----------

        Returns
        -------

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
        type
            :return:list of signal layers

        """
        signal_layers = EDBLayers(self).signal_layers

        return signal_layers


    @property
    def materials(self):
        """:return: Dictionary of Materials"""
        mats = {}
        for el in self.parent.edbutils.MaterialSetupInfo.GetFromLayout(self.parent.active_layout):
            mats[el.Name] = el
        return mats

    @aedt_exception_handler
    def stackup_limits(self, only_metals=False):
        """

        Parameters
        ----------
        only_metals :
             (Default value = False)

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
