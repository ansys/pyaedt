"""
Mesh Library Class
----------------------------------------------------------------


Description
==================================================

This class contains all the functionalities to create and edit mesh in all the 3D Tools



========================================================

"""

from __future__ import absolute_import

from ..generic.general_methods import aedt_exception_handler, generate_unique_name, MethodNotSupportedError
from ..application.DataHandlers import dict2arg
from collections import OrderedDict, defaultdict

class Mesh3DOperation(object):
    """ """
    def __init__(self, parent, hfss_setup_name, name, props):
        self._parent = parent
        self.name = name
        self.props = props
        self.hfss_setup_name = hfss_setup_name

    @aedt_exception_handler
    def _get_args(self, props=None):
        """

        Parameters
        ----------
        props :
             (Default value = None)

        Returns
        -------

        """
        if not props:
            props = self.props
        arg = ["NAME:" + self.name]
        dict2arg(props, arg)
        return arg

    @aedt_exception_handler
    def create(self):
        """ """
        self._parent.omeshmodule.AddMeshOperation(self.hfss_setup_name, self._get_args())
        return True

    @aedt_exception_handler
    def update(self):
        """ """
        self._parent.omeshmodule.EditMeshOperation(self.hfss_setup_name, self.name, self._get_args())
        return True

    @aedt_exception_handler
    def delete(self):
        """ """
        self._parent.omeshmodule.DeleteMeshOperation(self.hfss_setup_name, self.name,)

        return True



class Mesh(object):
    """""
    Manage Main AEDT Mesh Functions
    AEDTConfig Class Inherited contains all the _desktop Hierarchical calls needed to the class
    ""

    Parameters
    ----------

    Returns
    -------

    """

    def __init__(self, parent):
        self._parent = parent
        self.id = 0
        self.meshoperations = self._get_design_mesh_operations()


        pass

    @property
    def omeshmodule(self):
        """:return: Mesh Module"""
        return self.odesign.GetModule("SolveSetups")

    @property
    def messenger(self):
        """ """
        return self._parent._messenger

    @property
    def odesign(self):
        """ """
        return self._parent._odesign

    @property
    def modeler(self):
        """ """
        return self._parent._modeler

    @aedt_exception_handler
    def delete_mesh_operations(self, setup_name, mesh_name):
        """Remove mesh operations from a setup.
        
        :return: Boolean

        Parameters
        ----------
        setup_name :
            
        mesh_name :
            

        Returns
        -------

        """
        for el in self.meshoperations:
            if el.hfss_setup_name == setup_name and el.name == mesh_name:
                el.delete()
                self.meshoperations.remove(el)

        return True

    @aedt_exception_handler
    def _get_design_mesh_operations(self):
        """ """
        meshops = []
        try:
            for ds in self._parent.design_properties['Setup']['Data']:
                if 'MeshOps' in self._parent.design_properties['Setup']['Data'][ds]:
                    for ops in self._parent.design_properties['Setup']['Data'][ds]['MeshOps']:
                        props = self._parent.design_properties['Setup']['Data'][ds]['MeshOps'][ops]
                        meshops.append(Mesh3DOperation(self, ds, ops, props))
        except:
            pass
        return meshops

    @aedt_exception_handler
    def assign_length_mesh(self, setupname, layer_name, net_name, isinside=True, maxlength=1, maxel=1000, meshop_name=None):
        """

        Parameters
        ----------
        setupname :
            name of HFSS setup to be applied
        names :
            net lists.
        isinside :
            True if length mesh is inside selection, False if outside (Default value = True)
        maxlength :
            maxlength maximum element length. None to disable (Default value = 1)
        maxel :
            max number of element. None to disable (Default value = 1000)
        meshop_name :
            optional mesh operation name (Default value = None)
        layer_name :
            
        net_name :
            

        Returns
        -------
        type
            meshoperation object

        """
        if meshop_name:
            for el in self.meshoperations:
                if el.name == meshop_name:
                    meshop_name = generate_unique_name(meshop_name)
        else:
            meshop_name = generate_unique_name("Length")

        if maxlength is None:
            restrictlength = False
        else:
            restrictlength = True
        length = self.modeler.modeler_variable(maxlength)

        if maxel is None:
            restrictel = False
            numel = "1000"
        else:
            restrictel = True
            numel = str(maxel)
        if maxlength is None and maxel is None:
            self.messenger.add_error_message("mesh not assigned due to incorrect settings")
            return
        if type(layer_name) is list and type(net_name) is list:
            assignment = OrderedDict({"MeshEntityInfo":[]})
            for l, n in zip(layer_name,net_name):
                meshbody = OrderedDict({"Id": -1, "Nam": "", "Layer": l, "Net": n, "OrigNet": n})
                assignment["MeshEntityInfo"].append(OrderedDict({"IsFcSel": False, "EntID": -1, "FcIDs": [], "MeshBody": meshbody, "BBox": []}))
        else:
            meshbody = OrderedDict({"Id": -1, "Nam": "", "Layer": layer_name, "Net": net_name, "OrigNet": net_name})
            assignment = OrderedDict({"MeshEntityInfo": OrderedDict(
                {"IsFcSel": False, "EntID": -1, "FcIDs": [], "MeshBody": meshbody, "BBox": []})})
        props = OrderedDict({"Type": "LengthBased", "RefineInside": isinside, "Enabled": True, "Assignment": assignment,
                             "Region":"", "RestrictElem": restrictel, "NumMaxElem": numel, "RestrictLength": restrictlength,
                             "MaxLength": length})

        mop = Mesh3DOperation(self,setupname,meshop_name, props)
        mop.create()
        self.meshoperations.append(mop)
        return mop


    @aedt_exception_handler
    def assign_skin_depth(self, setupname, layer_name, net_name, skindepth=1, maxelements=None, triangulation_max_length=0.1, numlayers="2",
                          meshop_name=None):
        """

        Parameters
        ----------
        layer_name :
            name of the layer
        net_name :
            name of the net
        skindepth :
            Skin Depth length (Default value = 1)
        maxelements :
            maxlength maximum element length. None to disable (Default value = None)
        triangulation_max_length :
            maximum surface triangulation length (Default value = 0.1)
        numlayers :
            number of layers (Default value = "2")
        setupname :
            
        meshop_name :
             (Default value = None)

        Returns
        -------
        type
            meshoperation object

        """
        if meshop_name:
            for el in self.meshoperations:
                if el.name == meshop_name:
                    meshop_name = generate_unique_name(meshop_name)
        else:
            meshop_name = generate_unique_name("SkinDepth")

        if maxelements is None:
            restrictlength = False
            maxelements = "1000"
        else:
            restrictlength = True
        skindepth = self.modeler.modeler_variable(skindepth)
        triangulation_max_length= self.modeler.modeler_variable(triangulation_max_length)
        meshbody = OrderedDict({"Id": -1, "Nam": "", "Layer": layer_name,  "Net": net_name, "OrigNet": net_name})
        assignment = OrderedDict({"MeshEntityInfo": OrderedDict({"IsFcSel": False, "EntID": -1, "FcIDs": [], "MeshBody": meshbody, "BBox": []})})
        props = OrderedDict({"Type": "SkinDepthLengthBased", "Enabled": True, "Assignment": assignment,
                             "Region":"", "SkinDepth": skindepth, "SurfTriMaxLength": triangulation_max_length, "NumLayers": numlayers,
                             "RestrictElem": restrictlength, "NumMaxElem": maxelements})

        mop = Mesh3DOperation(self, setupname, meshop_name, props)
        mop.create()
        self.meshoperations.append(mop)
        return mop
