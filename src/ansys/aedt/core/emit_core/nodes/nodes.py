
from .GenericEmitNode import GenericEmitNode, props_to_dict

from . import generated

from .generated.Node_Amplifier import Node_Amplifier 
from .generated.Node_AntennaGroup import Node_AntennaGroup 
from .generated.Node_AntennaNode import Node_AntennaNode 
# from .generated.Node_AntennaPassband import Node_AntennaPassband 
# from .generated.Node_Band import Node_Band 
# from .generated.Node_BandFolder import Node_BandFolder 
# from .generated.Node_BandTraceNode import Node_BandTraceNode 
# from .generated.Node_Cable import Node_Cable 
# from .generated.Node_CADNode import Node_CADNode 
# from .generated.Node_Circulator import Node_Circulator 
# from .generated.Node_ComponentGroup import Node_ComponentGroup 
# from .generated.Node_ConfigurationGroup import Node_ConfigurationGroup 
# from .generated.Node_ConfigurationNode import Node_ConfigurationNode 
# from .generated.Node_CouplingLinkNode import Node_CouplingLinkNode 
from .generated.Node_CouplingsNode import Node_CouplingsNode 
# from .generated.Node_CouplingTraceNode import Node_CouplingTraceNode 
# from .generated.Node_CustomCouplingNode import Node_CustomCouplingNode 
# from .generated.Node_EmiPlotMarkerNode import Node_EmiPlotMarkerNode 
from .generated.Node_EmitSceneNode import Node_EmitSceneNode 
# from .generated.Node_ErcegCouplingNode import Node_ErcegCouplingNode 
# from .generated.Node_Filter import Node_Filter 
# from .generated.Node_FiveGChannelModel import Node_FiveGChannelModel 
# from .generated.Node_HataCouplingNode import Node_HataCouplingNode 
# from .generated.Node_IndoorPropagationCouplingNode import Node_IndoorPropagationCouplingNode 
# from .generated.Node_InteractionDiagramNode import Node_InteractionDiagramNode 
# from .generated.Node_Isolator import Node_Isolator 
# from .generated.Node_LogDistanceCouplingNode import Node_LogDistanceCouplingNode 
# from .generated.Node_MPlexBandTraceNode import Node_MPlexBandTraceNode 
# from .generated.Node_Multiplexer import Node_Multiplexer 
# from .generated.Node_MultiplexerBand import Node_MultiplexerBand 
# from .generated.Node_Node import Node_Node 
# from .generated.Node_OutboardTraceNode import Node_OutboardTraceNode 
# from .generated.Node_ParametricCouplingTraceNode import Node_ParametricCouplingTraceNode 
# from .generated.Node_PlotMarkerNode import Node_PlotMarkerNode 
# from .generated.Node_PlotNode import Node_PlotNode 
# from .generated.Node_PowerDivider import Node_PowerDivider 
# from .generated.Node_PowerTraceNode import Node_PowerTraceNode 
# from .generated.Node_ProfileTraceNode import Node_ProfileTraceNode 
# from .generated.Node_PropagationLossCouplingNode import Node_PropagationLossCouplingNode 
# from .generated.Node_RadioGroup import Node_RadioGroup 
# from .generated.Node_RadioNode import Node_RadioNode 
# from .generated.Node_ResultPlotNode import Node_ResultPlotNode 
# from .generated.Node_RfSystemGroup import Node_RfSystemGroup 
# from .generated.Node_RFSystemNode import Node_RFSystemNode 
# from .generated.Node_RxMeasNode import Node_RxMeasNode 
# from .generated.Node_RxMixerProductNode import Node_RxMixerProductNode 
# from .generated.Node_RxSaturationNode import Node_RxSaturationNode 
# from .generated.Node_RxSelectivityNode import Node_RxSelectivityNode 
# from .generated.Node_RxSpurNode import Node_RxSpurNode 
# from .generated.Node_RxSusceptibilityProfNode import Node_RxSusceptibilityProfNode 
# from .generated.Node_SamplingNode import Node_SamplingNode 
# from .generated.Node_SceneGroupNode import Node_SceneGroupNode 
# from .generated.Node_SelectivityTraceNode import Node_SelectivityTraceNode 
# from .generated.Node_SolutionCouplingNode import Node_SolutionCouplingNode 
# from .generated.Node_SolutionsNode import Node_SolutionsNode 
# from .generated.Node_Sparameter import Node_Sparameter 
# from .generated.Node_SparameterTraceNode import Node_SparameterTraceNode 
# from .generated.Node_SpurTraceNode import Node_SpurTraceNode 
# from .generated.Node_Terminator import Node_Terminator 
# from .generated.Node_TestNoiseTraceNode import Node_TestNoiseTraceNode 
# from .generated.Node_TopLevelSimulation import Node_TopLevelSimulation 
# from .generated.Node_TouchstoneCouplingNode import Node_TouchstoneCouplingNode 
# from .generated.Node_TR_Switch import Node_TR_Switch 
# from .generated.Node_TRSwitchTraceNode import Node_TRSwitchTraceNode 
# from .generated.Node_TunableTraceNode import Node_TunableTraceNode 
# from .generated.Node_TwoRayPathLossCouplingNode import Node_TwoRayPathLossCouplingNode 
# from .generated.Node_TwoToneTraceNode import Node_TwoToneTraceNode 
# from .generated.Node_TxBbEmissionNode import Node_TxBbEmissionNode 
# from .generated.Node_TxHarmonicNode import Node_TxHarmonicNode 
# from .generated.Node_TxMeasNode import Node_TxMeasNode 
# from .generated.Node_TxNbEmissionNode import Node_TxNbEmissionNode 
# from .generated.Node_TxSpectralProfNode import Node_TxSpectralProfNode 
# from .generated.Node_TxSpurNode import Node_TxSpurNode 
# from .generated.Node_WalfischCouplingNode import Node_WalfischCouplingNode 

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

    def get_node(self, id: int) -> GenericEmitNode:
        props = self.oEmitCom.GetEmitNodeProperties(0, id)
        props = props_to_dict(props)
        parent_props = self.oEmitCom.GetEmitNodeProperties(0, id, True)
        parent_props = props_to_dict(parent_props)

        type = parent_props['Type']
        type = f'Node_{type}'

        node = None
        try:
            type_module = getattr(generated, type)
            type_class = getattr(type_module, type)
            node = type_class(self.oDesign, 0, id)
        except AttributeError:
            node = GenericEmitNode(self.oDesign, 0, id)

        return node

    def get_all_nodes(self) -> list[GenericEmitNode]:
        ids = self.get_all_node_ids()
        nodes = [self.get_node(id) for id in ids]
        return nodes

    def get_scene_node(self) -> Node_EmitSceneNode:
        scene_node_id = self.oEmitCom.GetTopLevelNodeID(0, "Scene")
        scene_node = self.get_node(scene_node_id)
        return scene_node

    def get_couplings_node(self) -> Node_CouplingsNode:
        couplings_node_id = self.oEmitCom.GetTopLevelNodeID(0, "Couplings")
        couplings_node = self.get_node(couplings_node_id)
        return couplings_node