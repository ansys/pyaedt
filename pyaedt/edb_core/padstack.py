"""
This module contains all EDB functionalities in the ``EDB Padstack`` class.


"""
import warnings
from .general import *
from ..generic.general_methods import get_filename_without_extension, generate_unique_name
from .EDB_Data import EDBPadstack
try:
    import clr
    from System import Convert, String
    from System import Double, Array
    from System.Collections.Generic import List
except ImportError:
    warnings.warn('This module requires pythonnet.')


class EdbPadstacks(object):
    """EDB Padstacks class."""


    def __init__(self, parent):
        self.parent = parent

    @property
    def builder(self):
        """ """
        return self.parent.builder

    @property
    def edb(self):
        """ """
        return self.parent.edb

    @property
    def edb_value(self):
        """ """
        return self.parent.edb_value

    @property
    def active_layout(self):
        """ """
        return self.parent.active_layout

    @property
    def db(self):
        """ """
        return self.parent.db

    @property
    def padstack_methods(self):
        """ """
        return self.parent.edblib.Layout.PadStackMethods

    @property
    def messenger(self):
        """ """
        return self.parent._messenger

    @property
    def _layers(self):
        """ """
        return self.parent.core_stackup.stackup_layers
    @property
    def padstacks(self):
        """List all padstacks via padstack definitions.
        
        Returns
        -------
        list
            List of padstack definitions.

        """
        viadefList = {}
        for padstackdef in self.db.PadstackDefs:
            PadStackData = padstackdef.GetData()
            if len(PadStackData.GetLayerNames()) > 1:
                viadefList[padstackdef.GetName()] = EDBPadstack(padstackdef, self)
        return viadefList

    @aedt_exception_handler
    def create_circular_padstack(self, padstackname=None, holediam='300um', paddiam='400um', antipaddiam='600um',
                        startlayer=None, endlayer=None):
        """Create a new circular padstack.

        Parameters
        ----------
        padstackname : str, optional
            Name of the padstack. The default is ``None``.
        holediam : str, optional
           Diameter of the hole with units. The default is ``"300um"``.
        paddiam : str, optional
            Diameter of the pad with units. The default is ``"400um"``.
        antipaddiam : str, optional
            Diameter of the antipad with units. The default is``"600um"``.
        startlayer : str, optional
            Starting layer. The default is ``None``. If ``None``, the top
            is the starting layer.
        endlayer : str, optional
            Ending layer. The default is ``None``. If ``None``, the bottom
            is the ending layer.
     
        Returns
        -------
        str
            Name of the padstack if the operation is successful.

        """
        return self.padstack_methods.CreateCircularPadStackDef(self.builder, padstackname, holediam, paddiam,
                                                               antipaddiam, startlayer, endlayer)

    @aedt_exception_handler
    def get_pinlist_from_component_and_net(self, refdes=None, netname=None):
        """Retrieve pins given a component's reference designator and net name.

        Parameters
        ----------
        refdes : str, optional
            Reference designator of the component. The default is ``None``.
        netname : str optional
            Name of the net for which to search. The default is ``None``.
            .. note::
               ``False`` is returned if the net does not belong to the component.
        
        Returns
        -------
        dict
            Dictionary of pins.

        """
        if self.builder:
            pinlist = self.padstack_methods.GetPinsFromComponentAndNets(self.builder, refdes, netname)
            if pinlist.Item1:
                return pinlist.Item2

    @aedt_exception_handler
    def create_padstack(self, padstackname=None, holediam='300um', paddiam='400um', antipaddiam='600um',
                        startlayer=None, endlayer=None):
        """Create a new padstack.

        Parameters
        ----------
        padstackname : str, optional
            Name of the padstack. The default is ``None``.
        holediam : str, optional
           Diameter of the hole with units. The default is ``"300um"``.
        paddiam : str, optional
            Diameter of the pad with units. The default is ``"400um"``.
        antipaddiam : str, optional
            Diameter of the antipad with units. The default is``"600um"``.
        startlayer : str, optional
            Starting layer. The default is ``None``. If ``None``, the top
            is the starting layer.
        endlayer : str, optional
            Ending layer. The default is ``None``. If ``None``, the bottom
            is the ending layer.
            
        Returns
        -------
        str
            Name of the padstack if the operation is successful.

        """
        if not padstackname:
            padstackname = generate_unique_name("VIA")
        # assert not self.isreadonly, "Write Functions are not available within AEDT"
        padstackData = self.edb.Definition.PadstackDefData.Create()
        ptype = self.edb.Definition.PadGeometryType.Circle
        holparam = Array[type(self.edb_value(holediam))]([self.edb_value(holediam)])
        value0 = self.edb_value("0.0")

        padstackData.SetHoleParameters(ptype, holparam, value0, value0, value0)

        padstackData.SetHolePlatingPercentage(self.edb_value(20.0))
        padstackData.SetHoleRange(self.edb.Definition.PadstackHoleRange.UpperPadToLowerPad)
        padstackData.SetMaterial('copper')
        if not startlayer:
            layers = list(self.parent.core_stackup.signal_layers.keys())
            startlayer = layers[0]
        if not endlayer:
            layers = list(self.parent.core_stackup.signal_layers.keys())
            endlayer = layers[len(layers) - 1]
        for layer in [startlayer, 'Default', endlayer]:
            padparam_array = Array[type(self.edb_value(paddiam))]([self.edb_value(paddiam)])
            padstackData.SetPadParameters(
                layer,
                self.edb.Definition.PadType.RegularPad,
                self.edb.Definition.PadGeometryType.Circle,
                padparam_array,
                value0,
                value0,
                value0
            )
            antipad_array = Array[type(self.edb_value(antipaddiam))]([self.edb_value(antipaddiam)])

            padstackData.SetPadParameters(
                layer,
                self.edb.Definition.PadType.AntiPad,
                self.edb.Definition.PadGeometryType.Circle,
                antipad_array,
                value0,
                value0,
                value0
            )
        padstackLayerIdMap = {k: v for k, v in zip(padstackData.GetLayerNames(), padstackData.GetLayerIds())}
        padstackLayerMap = self.edb.Utility.LayerMap(self.edb.Utility.UniqueDirection.ForwardUnique)
        for layer, padstackLayerName in zip(
                self.active_layout.GetLayerCollection().Layers(
                    self.edb.Cell.LayerTypeSet.SignalLayerSet
                ),
                [startlayer, 'Default', endlayer]
        ):
            padstackLayerMap.SetMapping(
                layer.GetLayerId(),
                padstackLayerIdMap[padstackLayerName]
            )
        padstackDefinition = self.edb.Definition.PadstackDef.Create(self.db, padstackname)
        padstackDefinition.SetData(padstackData)
        self.messenger.add_info_message("Padstack {} create correctly".format(padstackname))
        return padstackname

    @aedt_exception_handler
    def place_padstack(self, position, definition_name, net_name='',
                       via_name="", rotation = 0, fromlayer = None, tolayer = None, solderlayer=None):
        padstack = None
        for pad in list(self.padstacks.keys()):
            if pad == definition_name:
                padstack = self.padstacks[pad].edb_padstack
        position = self.edb.Geometry.PointData(self.edb_value(position[0]), self.edb_value(position[1]))
        net = self.parent.core_nets.find_or_create_net(net_name)
        rotation = self.edb_value(rotation)
        sign_layers = list(self.parent.core_stackup.signal_layers.keys())
        if not fromlayer:
            fromlayer = self.parent.core_stackup.signal_layers[sign_layers[-1]]._layer
        else:
            fromlayer = self.parent.core_stackup.signal_layers[fromlayer]._layer

        if not tolayer:
            tolayer = self.parent.core_stackup.signal_layers[sign_layers[0]]._layer
        else:
            tolayer = self.parent.core_stackup.signal_layers[tolayer]._layer
        if solderlayer:
            solderlayer = self.parent.core_stackup.signal_layers[solderlayer]._layer
        if padstack:
            via = self.edb.Cell.Primitive.PadstackInstance.Create(self.active_layout, net, via_name, padstack,
                                                                  position, rotation, fromlayer, tolayer, solderlayer,
                                                                  None)
            return via
        else:
            return False
