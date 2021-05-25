from __future__ import absolute_import
from ..generic.general_methods import aedt_exception_handler
from .Modeler import GeometryModeler
from  .Primitives3D import Primitives3D

class Modeler3D(GeometryModeler):
    """AEDT 3D Modeler"""
    def __init__(self, application):
        GeometryModeler.__init__(self, application, is3d=True)
        self._primitives = Primitives3D(self._parent, self)
        self._primitivesDes = self._parent.project_name + self._parent.design_name

    def __get__(self, instance, owner):
        self._parent = instance
        return self

    @property
    def primitives(self):
        """ """
        if self._primitivesDes != self._parent.project_name + self._parent.design_name:
            self._primitives = Primitives3D(self._parent, self)
            self._primitivesDes = self._parent.project_name + self._parent.design_name
        return self._primitives

    @aedt_exception_handler
    def create_3dcomponent(self, component_file, component_name=None, variables_to_include=[], exclude_region=False):
        """Create 3D Component file

        Parameters
        ----------
        component_file :
            full path to the a3dcomp file
        component_name :
            Component name (Default value = None)
        variables_to_include :
             (Default value = [])
        exclude_region :
             (Default value = False)

        Returns
        -------
        type
            Bool

        """
        if self._parent.design_type == "Icepak":
            exclude_region =True
        if not component_name:
            component_name = self._parent.design_name
        arg = ["NAME:CreateData", "ComponentName:=", component_name, "Company:=", "",
               "Company URL:=", "", "Model Number:=", "", "Help URL:=", "",
               "Version:=", "1.0", "Notes:=", "", "IconType:=", "",
               "Owner:=", "pyaedt", "Email:=", "", "Date:=", "9:44:15 AM  Mar 03, 2021",
               "HasLabel:=", False, "IsEncrypted:=", False, "AllowEdit:=", False,
               "SecurityMessage:=", "", "Password:=", "", "EditPassword:=", "",
               "PasswordType:=", "UnknownPassword", "HideContents:=", True,
               "ReplaceNames:=", True, "ComponentOutline:=", "None"]
        objs = self.primitives.get_all_objects_names()
        for el in objs:
            if "Region" in el and exclude_region:
                objs.remove(el)
        arg.append("IncludedParts:="), arg.append(objs)
        arg.append("HiddenParts:="), arg.append([])
        activecs = self.oeditor.GetActiveCoordinateSystem()
        allcs = self.oeditor.GetCoordinateSystems()
        arg.append("IncludedCS:="), arg.append(allcs)
        arg.append("ReferenceCS:="), arg.append(activecs)
        variables =variables_to_include
        arg.append("IncludedParameters:="), arg.append(variables)
        variables = self._parent._variable_manager.dependent_variable_names
        par_description = []
        for el in variables:
            par_description.append(el)
            par_description.append("")
        arg.append("IncludedDependentParameters:="), arg.append(variables)
        for el in variables:
            par_description.append(el)
            par_description.append("")
        arg.append("ParameterDescription:="), arg.append(par_description)
        arg.append("IsLicensed:="), arg.append(False)
        arg.append("LicensingDllName:="), arg.append("")
        arg.append("VendorComponentIdentifier:="), arg.append("")
        arg.append("PublicKeyFile:="), arg.append("")
        arg2 = ["NAME:DesignData"]
        boundaries = self.get_boundaries_name()
        arg2.append("Boundaries:="),arg2.append(boundaries)
        if self._parent.design_type == "Icepak":
            meshregions = [name for name in self._parent.mesh.meshregions.name]
            try:
                meshregions.remove("Global")
            except:
                pass
            arg2.append("MeshRegions:="), arg2.append(meshregions)
        else:
            excitations = self.get_excitations_name()
            arg2.append("Excitations:="), arg2.append(excitations)
        meshops = [el.name for el in self._parent.mesh.meshoperations]
        arg2.append("MeshOperations:="), arg2.append(meshops)
        arg3 = ["NAME:ImageFile", "ImageFile:=", ""]
        self.oeditor.Create3DComponent(arg, arg2, component_file, arg3)
        return True