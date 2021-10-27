"""
This module contains the `EdbPadstacks` class.
"""

import warnings

from pyaedt.generic.general_methods import aedt_exception_handler, generate_unique_name
from pyaedt.edb_core.general import convert_py_list_to_net_list

from pyaedt.edb_core.EDB_Data import EDBPadstack

try:
    from System import Array
except ImportError:
    warnings.warn('This module requires the "pythonnet" package.')


class EdbPadstacks(object):
    """Manages EDB functionalities for padstacks."""

    def __init__(self, p_edb):
        self._pedb = p_edb
        self._padstacks = {}

    @property
    def _builder(self):
        """ """
        return self._pedb.builder

    @property
    def _edb(self):
        """ """
        return self._pedb.edb

    @property
    def _edb_value(self):
        """ """
        return self._pedb.edb_value

    @property
    def _active_layout(self):
        """ """
        return self._pedb.active_layout

    @property
    def db(self):
        """Db object."""
        return self._pedb.db

    @property
    def _padstack_methods(self):
        """ """
        return self._pedb.edblib.Layout.PadStackMethods

    @property
    def _logger(self):
        """ """
        return self._pedb.logger

    @property
    def _layers(self):
        """ """
        return self._pedb.core_stackup.stackup_layers

    @property
    def padstacks(self):
        """Padstacks via padstack definitions.

        Returns
        -------
        dict of :class:`pyaedt.edb_core.Edb_Data.EdbPadstack`
            List of padstacks via padstack definitions.

        """
        if self._padstacks:
            return self._padstacks
        self.update_padstacks()
        return self._padstacks

    @property
    def pingroups(self):
        """All Layout Pin groups.

        Returns
        -------
        list
            List of all layout pin groups.
        """
        pingroups = []
        for el in self._active_layout.PinGroups:
            pingroups.append(el)
        return pingroups

    @aedt_exception_handler
    def update_padstacks(self):
        """Update Padstack Dictionary.

        Returns
        -------
        dict
            Dictionary of Padstacks.
        """
        self._padstacks = {}
        for padstackdef in self.db.PadstackDefs:
            PadStackData = padstackdef.GetData()
            if len(PadStackData.GetLayerNames()) >= 1:
                self._padstacks[padstackdef.GetName()] = EDBPadstack(padstackdef, self)

    @aedt_exception_handler
    def create_circular_padstack(
        self, padstackname=None, holediam="300um", paddiam="400um", antipaddiam="600um", startlayer=None, endlayer=None
    ):
        """Create a circular padstack.

        Parameters
        ----------
        padstackname : str, optional
            Name of the padstack. The default is ``None``.
        holediam : str, optional
            Diameter of the hole with units. The default is ``"300um"``.
        paddiam : str, optional
            Diameter of the pad with units. The default is ``"400um"``.
        antipaddiam : str, optional
            Diameter of the antipad with units. The default is ``"600um"``.
        startlayer : str, optional
            Starting layer. The default is ``None``, in which case the top
            is the starting layer.
        endlayer : str, optional
            Ending layer. The default is ``None``, in which case the bottom
            is the ending layer.

        Returns
        -------
        str
            Name of the padstack if the operation is successful.
        """
        pad = self._padstack_methods.CreateCircularPadStackDef(
            self._builder, padstackname, holediam, paddiam, antipaddiam, startlayer, endlayer
        )
        self.update_padstacks()

    @aedt_exception_handler
    def get_pinlist_from_component_and_net(self, refdes=None, netname=None):
        """Retrieve pins given a component's reference designator and net name.

        Parameters
        ----------
        refdes : str, optional
            Reference designator of the component. The default is ``None``.
        netname : str optional
            Name of the net. The default is ``None``.

        Returns
        -------
        dict
            Dictionary of pins if the operation is successful.
            ``False`` is returned if the net does not belong to the component.

        """
        if self._builder:
            pinlist = self._padstack_methods.GetPinsFromComponentAndNets(self._active_layout, refdes, netname)
            if pinlist.Item1:
                return pinlist.Item2

    @aedt_exception_handler
    def create_padstack(
        self, padstackname=None, holediam="300um", paddiam="400um", antipaddiam="600um", startlayer=None, endlayer=None
    ):
        """Create a padstack.

        Parameters
        ----------
        padstackname : str, optional
            Name of the padstack. The default is ``None``.
        holediam : str, optional
            Diameter of the hole with units. The default is ``"300um"``.
        paddiam : str, optional
            Diameter of the pad with units. The default is ``"400um"``.
        antipaddiam : str, optional
            Diameter of the antipad with units. The default is ``"600um"``.
        startlayer : str, optional
            Starting layer. The default is ``None``, in which case the top
            is the starting layer.
        endlayer : str, optional
            Ending layer. The default is ``None``, in which case the bottom
            is the ending layer.

        Returns
        -------
        str
            Name of the padstack if the operation is successful.
        """
        holediam = self._edb_value(holediam)
        paddiam = self._edb_value(paddiam)
        antipaddiam = self._edb_value(antipaddiam)
        if not padstackname:
            padstackname = generate_unique_name("VIA")
        # assert not self.isreadonly, "Write Functions are not available within AEDT"
        padstackData = self._edb.Definition.PadstackDefData.Create()
        ptype = self._edb.Definition.PadGeometryType.Circle
        holparam = Array[type(holediam)]([holediam])
        value0 = self._edb_value("0.0")

        padstackData.SetHoleParameters(ptype, holparam, value0, value0, value0)

        padstackData.SetHolePlatingPercentage(self._edb_value(20.0))
        padstackData.SetHoleRange(self._edb.Definition.PadstackHoleRange.UpperPadToLowerPad)
        padstackData.SetMaterial("copper")
        layers = list(self._pedb.core_stackup.signal_layers.keys())
        if not startlayer:
            startlayer = layers[0]
        if not endlayer:
            endlayer = layers[len(layers) - 1]
        for layer in ["Default"]+layers:
            padparam_array = Array[type(paddiam)]([paddiam])
            padstackData.SetPadParameters(
                layer,
                self._edb.Definition.PadType.RegularPad,
                self._edb.Definition.PadGeometryType.Circle,
                padparam_array,
                value0,
                value0,
                value0,
            )
            antipad_array = Array[type(antipaddiam)]([antipaddiam])

            padstackData.SetPadParameters(
                layer,
                self._edb.Definition.PadType.AntiPad,
                self._edb.Definition.PadGeometryType.Circle,
                antipad_array,
                value0,
                value0,
                value0,
            )
        padstackLayerIdMap = {k: v for k, v in zip(padstackData.GetLayerNames(), padstackData.GetLayerIds())}
        padstackLayerMap = self._edb.Utility.LayerMap(self._edb.Utility.UniqueDirection.ForwardUnique)
        for layer, padstackLayerName in zip(
            self._active_layout.GetLayerCollection().Layers(self._edb.Cell.LayerTypeSet.SignalLayerSet),
            [startlayer, "Default", endlayer],
        ):
            padstackLayerMap.SetMapping(layer.GetLayerId(), padstackLayerIdMap[padstackLayerName])
        padstackDefinition = self._edb.Definition.PadstackDef.Create(self.db, padstackname)
        padstackDefinition.SetData(padstackData)
        self._logger.info("Padstack {} create correctly".format(padstackname))
        self.update_padstacks()
        return padstackname

    @aedt_exception_handler
    def place_padstack(
        self,
        position,
        definition_name,
        net_name="",
        via_name="",
        rotation=0,
        fromlayer=None,
        tolayer=None,
        solderlayer=None,
    ):
        """Place the padstack.

        Parameters
        ----------
        position : list
            List of float values for the [x,y] positions where the via is to be placed.
        definition_name : str
            Name of the padstack definition.
        net_name : str, optional
            Name of the net. The default is ``""``.
        via_name : str, optional
            The default is ``""``.
        rotation : float, optional
            Rotation of the padstack in degrees. The default
            is ``0``.
        fromlayer :
            The default is ``None``.
        tolayer :
            The default is ``None``.
        solderlayer :
            The default is ``None``.

        Returns
        -------

        """
        padstack = None
        for pad in list(self.padstacks.keys()):
            if pad == definition_name:
                padstack = self.padstacks[pad].edb_padstack
        position = self._edb.Geometry.PointData(self._edb_value(position[0]), self._edb_value(position[1]))
        net = self._pedb.core_nets.find_or_create_net(net_name)
        rotation = self._edb_value(rotation)
        sign_layers = list(self._pedb.core_stackup.signal_layers.keys())
        if not fromlayer:
            fromlayer = self._pedb.core_stackup.signal_layers[sign_layers[-1]]._layer
        else:
            fromlayer = self._pedb.core_stackup.signal_layers[fromlayer]._layer

        if not tolayer:
            tolayer = self._pedb.core_stackup.signal_layers[sign_layers[0]]._layer
        else:
            tolayer = self._pedb.core_stackup.signal_layers[tolayer]._layer
        if solderlayer:
            solderlayer = self._pedb.core_stackup.signal_layers[solderlayer]._layer
        if padstack:
            via = self._edb.Cell.Primitive.PadstackInstance.Create(
                self._active_layout, net, via_name, padstack, position, rotation, fromlayer, tolayer, solderlayer, None
            )
            return via
        else:
            return False

    @aedt_exception_handler
    def remove_pads_from_padstack(self, padstack_name, layer_name=None):
        """Remove the Pad from a padstack on a specific layer by setting it as a 0 thickness circle.

        Parameters
        ----------
        padstack_name : str
            padstack name
        layer_name : str, optional
            Layer name on which remove the PadParameters. If None, all layers will be taken.

        Returns
        -------
        bool
            ``True`` if successful.
        """
        pad_type = self._edb.Definition.PadType.RegularPad
        pad_geo = self._edb.Definition.PadGeometryType.Circle
        vals = self._edb_value(0)
        params = convert_py_list_to_net_list([self._edb_value(0)])
        p1 = self.padstacks[padstack_name].edb_padstack.GetData()
        newPadstackDefinitionData = self._edb.Definition.PadstackDefData(p1)

        if not layer_name:
            layer_name = list(self._pedb.core_stackup.signal_layers.keys())
        elif isinstance(layer_name, str):
            layer_name = [layer_name]
        for lay in layer_name:
            newPadstackDefinitionData.SetPadParameters(lay, pad_type, pad_geo, params, vals, vals, vals)

        self.padstacks[padstack_name].edb_padstack.SetData(newPadstackDefinitionData)
        self.update_padstacks()
        return True
