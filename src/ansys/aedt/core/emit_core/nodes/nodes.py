
from .EmitNode import EmitNode

from . import generated
from .generated import *

class NodeInterface:
    def __init__(self, oDesign):
        self.oDesign = oDesign
        self.oEmitCom = oDesign.GetModule("EmitCom")
    
    def get_all_component_names(self) -> list[str]:
        component_names = self.oEmitCom.GetComponentNames(0, "")
        return component_names
    
    def get_all_top_level_nodes(self) -> list[EmitNode]:
        top_level_node_names = ["Scene", "Couplings"]
        top_level_node_ids = [self.oEmitCom.GetTopLevelNodeID(0, name) for name in top_level_node_names]
        top_level_nodes = [self.get_node(node_id) for node_id in top_level_node_ids]
        return top_level_nodes
    
    def get_all_component_nodes(self) -> list[EmitNode]:
        component_names = self.get_all_component_names()
        component_node_ids = [self.oEmitCom.GetComponentNodeID(0, name) for name in component_names]
        component_nodes = [self.get_node(node_id) for node_id in component_node_ids]
        return component_nodes

    def get_all_node_ids(self) -> list[int]:
        node_ids = []
        node_ids_to_search = []

        top_level_node_names = ["Scene"]
        top_level_node_ids = [self.oEmitCom.GetTopLevelNodeID(0, name) for name in top_level_node_names]
        node_ids_to_search.extend(top_level_node_ids)

        component_names = self.get_all_component_names()
        component_node_ids = [self.oEmitCom.GetComponentNodeID(0, name) for name in component_names]
        node_ids_to_search.extend(component_node_ids)

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
            type_class = getattr(generated, type)
            node = type_class(self.oDesign, 0, id)
        except AttributeError:
            node = EmitNode(self.oDesign, 0, id)

        return node
    
    def get_child_nodes(self, node: EmitNode) -> list[EmitNode]:
        child_names = self.oEmitCom.GetChildNodeNames(0, node._node_id)
        child_ids = [self.oEmitCom.GetChildNodeID(0, node._node_id, name) for name in child_names]
        child_nodes = [self.get_node(child_id) for child_id in child_ids]
        return child_nodes 

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
