"""
EdbPadstack Class
-------------------

This class manages Edb Padstacks and related methods


"""
import warnings
from .general import *
from ..generic.general_methods import get_filename_without_extension, generate_unique_name

try:
    import clr
    from System import Convert, String
    from System import Double, Array
    from System.Collections.Generic import List
except ImportError:
    warnings.warn('This module requires pythonnet.')


class EdbPadstacks(object):
    """HFSS 3DLayout object"""


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
    def cell(self):
        """ """
        return self.parent.cell

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
        return self.parent.messenger

    @property
    def padstacks(self):
        """Get all via padstack definitions
        
        
        :return: List of padstack definitions

        Parameters
        ----------

        Returns
        -------

        """
        viadefList = {}
        for padstackdef in self.db.PadstackDefs:
            PadStackData = padstackdef.GetData()
            if len(PadStackData.GetLayerNames()) > 1:
                viadefList[padstackdef.GetName()] = padstackdef
        return viadefList

    @aedt_exception_handler
    def get_padstack_info(self):
        """Get All Via padstack definition

        Parameters
        ----------
        vianame :
            optional via name

        Returns
        -------
        type
            dictionary of vias

        """
        # Via padstack definition
        ViaDefinition = self.padstacks
        vias = {}
        for name, via in ViaDefinition.items():
            try:
                viaDefName = name
                viaData = via.GetData()

                if "IronPython" in sys.version or ".NETFramework" in sys.version:
                    out = viaData.GetHoleParametersValue()
                    HoleParam = out[2]
                else:
                    value0 = self.parent.edb_value("0.0")
                    ptype = self.edb.Definition.PadGeometryType.Circle
                    HoleParam = Array[type(value0)]([])
                    out = viaData.GetHoleParametersValue(ptype, HoleParam, value0, value0, value0)
                    HoleParam = out[2]
                HoleDiameter = HoleParam[0].ToDouble()
                PlatingRatio = viaData.GetHolePlatingPercentage()
                # PlatingRatio = 30.0
                PlatingThickness = (HoleDiameter*PlatingRatio/100)/2
                # PlatingThickness = 25.0 * 1e-6
                FinishedHole = HoleDiameter - (PlatingThickness * 2)
                viaLayers = viaData.GetLayerNames()
                StartLay = viaLayers[0]
                StopLay = viaLayers[len(viaLayers)-1]
                vias[viaDefName] = {"Diameter": str(HoleDiameter * 1e6) + 'um', "Thickness": str(
                    PlatingThickness * 1e6) + 'um', "FinishedHole": str(FinishedHole * 1e6) + 'um',
                                    "StartLayer": StartLay, "StopLayer": StopLay}
            except Exception:
                pass

        return vias

    @aedt_exception_handler
    def create_circular_padstack(self, padstackname=None, holediam='300um', paddiam='400um', antipaddiam='600um',
                        startlayer=None, endlayer=None):
        """Create a new Padskack

        Parameters
        ----------
        endlayer :
            End Layer. If none is entered, default is bottom
        startlayer :
            Start Layer. If none is entered, default is top
        padstackname :
            name of the padstack (Default value = None)
        holediam :
            hole diameter with units (Default value = '300um')
        paddiam :
            pad diameter with units (Default value = '400um')
        antipaddiam :
            antipad diameter with units (Default value = '600um')

        Returns
        -------
        type
            padstackname if operation is completed

        """
        if self.builder:
            return self.padstack_methods.CreateCircularPadStackDef(self.builder, padstackname, holediam, paddiam,
                                                                   antipaddiam, startlayer, endlayer)

    @aedt_exception_handler
    def get_pinlist_from_component_and_net(self, refdes = None, netname = None):
        """Get Pins from given component refdes and net name

        Parameters
        ----------
        Component :
            refdes: Component name
        netname :
            the name of the nets to search for. Will return False if the net does not belong to the component (Default value = None)
        refdes :
             (Default value = None)

        Returns
        -------
        type
            dictionary of vias

        """
        if self.builder:
            pinlist = self.padstack_methods.GetPinsFromComponentAndNets(self.builder, refdes, netname)
            if pinlist.Item1:
                return pinlist.Item2

    @aedt_exception_handler
    def create_padstack(self, padstackname=None, holediam='300um', paddiam='400um', antipaddiam='600um',
                        startlayer=None, endlayer=None):
        """Create a new Padskack

        Parameters
        ----------
        endlayer :
            End Layer. If none is entered, default is bottom
        startlayer :
            Start Layer. If none is entered, default is top
        padstackname :
            name of the padstack (Default value = None)
        holediam :
            hole diameter with units (Default value = '300um')
        paddiam :
            pad diameter with units (Default value = '400um')
        antipaddiam :
            antipad diameter with units (Default value = '600um')

        Returns
        -------
        type
            padstackname if operation is completed

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
