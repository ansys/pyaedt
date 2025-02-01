
from .EmitNode import EmitNode

from . import generated

from .generated.Amplifier import Amplifier
from .generated.ReadOnlyAmplifier import ReadOnlyAmplifier
from .generated.Circulator import Circulator
from .generated.CouplingLinkNode import CouplingLinkNode
from .generated.CouplingsNode import CouplingsNode
from .generated.CouplingTraceNode import CouplingTraceNode
from .generated.CustomCouplingNode import CustomCouplingNode
from .generated.EmiPlotMarkerNode import EmiPlotMarkerNode
from .generated.EmitSceneNode import EmitSceneNode
from .generated.ErcegCouplingNode import ErcegCouplingNode
from .generated.Filter import Filter
from .generated.FiveGChannelModel import FiveGChannelModel
from .generated.HataCouplingNode import HataCouplingNode
from .generated.IndoorPropagationCouplingNode import IndoorPropagationCouplingNode
from .generated.Isolator import Isolator
from .generated.LogDistanceCouplingNode import LogDistanceCouplingNode
from .generated.MPlexBandTraceNode import MPlexBandTraceNode
from .generated.Multiplexer import Multiplexer
from .generated.MultiplexerBand import MultiplexerBand
from .generated.OutboardTraceNode import OutboardTraceNode
from .generated.ParametricCouplingTraceNode import ParametricCouplingTraceNode
from .generated.PlotMarkerNode import PlotMarkerNode
from .generated.PlotNode import PlotNode
from .generated.PowerDivider import PowerDivider
from .generated.PowerTraceNode import PowerTraceNode
from .generated.ProfileTraceNode import ProfileTraceNode
from .generated.PropagationLossCouplingNode import PropagationLossCouplingNode
from .generated.RadioNode import RadioNode
from .generated.ReadOnlyAntennaNode import ReadOnlyAntennaNode
from .generated.ReadOnlyAntennaPassband import ReadOnlyAntennaPassband
from .generated.ReadOnlyBand import ReadOnlyBand
from .generated.ReadOnlyBandFolder import ReadOnlyBandFolder
from .generated.ReadOnlyCable import ReadOnlyCable
from .generated.ReadOnlyCADNode import ReadOnlyCADNode
from .generated.ReadOnlyCirculator import ReadOnlyCirculator
from .generated.ReadOnlyCouplingLinkNode import ReadOnlyCouplingLinkNode
from .generated.ReadOnlyCouplingsNode import ReadOnlyCouplingsNode
from .generated.ReadOnlyCustomCouplingNode import ReadOnlyCustomCouplingNode
from .generated.ReadOnlyEmitSceneNode import ReadOnlyEmitSceneNode
from .generated.ReadOnlyErcegCouplingNode import ReadOnlyErcegCouplingNode
from .generated.ReadOnlyFilter import ReadOnlyFilter
from .generated.ReadOnlyFiveGChannelModel import ReadOnlyFiveGChannelModel
from .generated.ReadOnlyHataCouplingNode import ReadOnlyHataCouplingNode
from .generated.ReadOnlyIndoorPropagationCouplingNode import ReadOnlyIndoorPropagationCouplingNode
from .generated.ReadOnlyIsolator import ReadOnlyIsolator
from .generated.ReadOnlyLogDistanceCouplingNode import ReadOnlyLogDistanceCouplingNode
from .generated.ReadOnlyMultiplexer import ReadOnlyMultiplexer
from .generated.ReadOnlyMultiplexerBand import ReadOnlyMultiplexerBand
from .generated.ReadOnlyPowerDivider import ReadOnlyPowerDivider
from .generated.ReadOnlyPropagationLossCouplingNode import ReadOnlyPropagationLossCouplingNode
from .generated.ReadOnlyRadioNode import ReadOnlyRadioNode
from .generated.ReadOnlyRfSystemGroup import ReadOnlyRfSystemGroup
from .generated.ReadOnlyRxMeasNode import ReadOnlyRxMeasNode
from .generated.ReadOnlyRxMixerProductNode import ReadOnlyRxMixerProductNode
from .generated.ReadOnlyRxSaturationNode import ReadOnlyRxSaturationNode
from .generated.ReadOnlyRxSelectivityNode import ReadOnlyRxSelectivityNode
from .generated.ReadOnlyRxSpurNode import ReadOnlyRxSpurNode
from .generated.ReadOnlyRxSusceptibilityProfNode import ReadOnlyRxSusceptibilityProfNode
from .generated.ReadOnlySamplingNode import ReadOnlySamplingNode
from .generated.ReadOnlySceneGroupNode import ReadOnlySceneGroupNode
from .generated.ReadOnlySolutionCouplingNode import ReadOnlySolutionCouplingNode
from .generated.ReadOnlySolutionsNode import ReadOnlySolutionsNode
from .generated.ReadOnlySparameter import ReadOnlySparameter
from .generated.ReadOnlyTerminator import ReadOnlyTerminator
from .generated.ReadOnlyTouchstoneCouplingNode import ReadOnlyTouchstoneCouplingNode
from .generated.ReadOnlyTR_Switch import ReadOnlyTR_Switch
from .generated.ReadOnlyTwoRayPathLossCouplingNode import ReadOnlyTwoRayPathLossCouplingNode
from .generated.ReadOnlyTxBbEmissionNode import ReadOnlyTxBbEmissionNode
from .generated.ReadOnlyTxHarmonicNode import ReadOnlyTxHarmonicNode
from .generated.ReadOnlyTxMeasNode import ReadOnlyTxMeasNode
from .generated.ReadOnlyTxNbEmissionNode import ReadOnlyTxNbEmissionNode
from .generated.ReadOnlyTxSpectralProfNode import ReadOnlyTxSpectralProfNode
from .generated.ReadOnlyTxSpurNode import ReadOnlyTxSpurNode
from .generated.ReadOnlyWalfischCouplingNode import ReadOnlyWalfischCouplingNode
from .generated.ResultPlotNode import ResultPlotNode
from .generated.RfSystemGroup import RfSystemGroup
from .generated.RxMeasNode import RxMeasNode
from .generated.RxMixerProductNode import RxMixerProductNode
from .generated.RxSaturationNode import RxSaturationNode
from .generated.RxSelectivityNode import RxSelectivityNode
from .generated.RxSpurNode import RxSpurNode
from .generated.RxSusceptibilityProfNode import RxSusceptibilityProfNode
from .generated.SamplingNode import SamplingNode
from .generated.SceneGroupNode import SceneGroupNode
from .generated.SelectivityTraceNode import SelectivityTraceNode
from .generated.SolutionCouplingNode import SolutionCouplingNode
from .generated.SolutionsNode import SolutionsNode
from .generated.Sparameter import Sparameter
from .generated.SpurTraceNode import SpurTraceNode
from .generated.Terminator import Terminator
from .generated.TestNoiseTraceNode import TestNoiseTraceNode
from .generated.TopLevelSimulation import TopLevelSimulation
from .generated.TouchstoneCouplingNode import TouchstoneCouplingNode
from .generated.TR_Switch import TR_Switch
from .generated.TRSwitchTraceNode import TRSwitchTraceNode
from .generated.TunableTraceNode import TunableTraceNode
from .generated.TwoRayPathLossCouplingNode import TwoRayPathLossCouplingNode
from .generated.TwoToneTraceNode import TwoToneTraceNode
from .generated.TxBbEmissionNode import TxBbEmissionNode
from .generated.TxHarmonicNode import TxHarmonicNode
from .generated.TxMeasNode import TxMeasNode
from .generated.TxNbEmissionNode import TxNbEmissionNode
from .generated.TxSpectralProfNode import TxSpectralProfNode
from .generated.TxSpurNode import TxSpurNode
from .generated.WalfischCouplingNode import WalfischCouplingNode
from .generated.AntennaNode import AntennaNode
from .generated.AntennaPassband import AntennaPassband
from .generated.Band import Band
from .generated.BandFolder import BandFolder
from .generated.BandTraceNode import BandTraceNode
from .generated.Cable import Cable
from .generated.CADNode import CADNode
from .generated.CategoriesViewNode import CategoriesViewNode

class NodeInterface:
    def __init__(self, oDesign):
        self.oDesign = oDesign
        self.oEmitCom = oDesign.GetModule("EmitCom")

    def get_all_node_ids(self) -> list[int]:
        scene_node_id = self.oEmitCom.GetToplevelNodeID(0, "Scene")

        node_ids = []
        node_ids_to_search = [scene_node_id]

        while len(node_ids_to_search) > 0:
            node_id_to_search = node_ids_to_search.pop()
            if node_id_to_search not in node_ids:
                node_ids.append(node_id_to_search)

                child_names = self.oEmitCom.GetChildNodeNames(0, node_id_to_search)
                child_ids = [self.oEmitCom.GetChildNodeID(0, node_id_to_search, name) for name in child_names]
                if len(child_ids) > 0:
                    node_ids_to_search.extend(child_ids)
        
        return node_ids

    def get_node(self, id: int) -> EmitNode:
        props = self.oEmitCom.GetEmitNodeProperties(0, id)
        props = EmitNode.props_to_dict(props)
        parent_props = self.oEmitCom.GetEmitNodeProperties(0, id, True)
        parent_props = EmitNode.props_to_dict(parent_props)

        type = parent_props['Type']

        node = None
        try:
            type_module = getattr(generated, type)
            type_class = getattr(type_module, type)
            node = type_class(self.oDesign, 0, id)
        except AttributeError:
            node = EmitNode(self.oDesign, 0, id)

        return node

    def get_all_nodes(self) -> list[EmitNode]:
        ids = self.get_all_node_ids()
        nodes = [self.get_node(id) for id in ids]
        return nodes

    def get_scene_node(self) -> EmitSceneNode:
        scene_node_id = self.oEmitCom.GetTopLevelNodeID(0, "Scene")
        scene_node = self.get_node(scene_node_id)
        return scene_node

    def get_couplings_node(self) -> CouplingsNode:
        couplings_node_id = self.oEmitCom.GetTopLevelNodeID(0, "Couplings")
        couplings_node = self.get_node(couplings_node_id)
        return couplings_node
