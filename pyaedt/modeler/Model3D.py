from __future__ import absolute_import
from pyaedt.generic.general_methods import aedt_exception_handler
from pyaedt.modeler.Modeler import GeometryModeler
from pyaedt.modeler.Primitives3D import Primitives3D


class Modeler3D(GeometryModeler):
    """Provides the Modeler 3D application interface.

    This class is inherited in the caller application and is accessible through the modeler variable
    object( eg. ``hfss.modeler``).

    Parameters
    ----------
    application : :class:`pyaedt.application.Analysis3D.FieldAnalysis3D`
    Examples
    --------
    >>> from pyaedt import Hfss
    >>> hfss = Hfss()
    >>> my_modeler = hfss.modeler
    """

    def __init__(self, application):
        GeometryModeler.__init__(self, application, is3d=True)
        self._primitives = Primitives3D(self)
        self._primitivesDes = self._app.project_name + self._app.design_name

    def __get__(self, instance, owner):
        self._app = instance
        return self

    @property
    def primitives(self):
        """Primitives.

        Returns
        -------
        :class:`pyaedt.modeler.Primitives3D.Primitives3D`

        """
        if self._primitivesDes != self._app.project_name + self._app.design_name:
            self._primitives.refresh()
            self._primitivesDes = self._app.project_name + self._app.design_name
        return self._primitives

    @aedt_exception_handler
    def create_3dcomponent(self, component_file, component_name=None, variables_to_include=[], exclude_region=False):
        """Create a 3D component file.

        Parameters
        ----------
        component_file : str
            Full path to the A3DCOMP file.
        component_name : str, optional
            Name of the component. The default is ``None``.
        variables_to_include : list, optional
             List of variables to include. The default is ``[]``.
        exclude_region : bool, optional
             Whether to exclude the region. The default is ``False``.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.

        References
        ----------

        >>> oEditor. Create3DComponent
        """
        if self._app.design_type == "Icepak":
            exclude_region = True
        if not component_name:
            component_name = self._app.design_name
        arg = [
            "NAME:CreateData",
            "ComponentName:=",
            component_name,
            "Company:=",
            "",
            "Company URL:=",
            "",
            "Model Number:=",
            "",
            "Help URL:=",
            "",
            "Version:=",
            "1.0",
            "Notes:=",
            "",
            "IconType:=",
            "",
            "Owner:=",
            "pyaedt",
            "Email:=",
            "",
            "Date:=",
            "9:44:15 AM  Mar 03, 2021",
            "HasLabel:=",
            False,
            "IsEncrypted:=",
            False,
            "AllowEdit:=",
            False,
            "SecurityMessage:=",
            "",
            "Password:=",
            "",
            "EditPassword:=",
            "",
            "PasswordType:=",
            "UnknownPassword",
            "HideContents:=",
            True,
            "ReplaceNames:=",
            True,
            "ComponentOutline:=",
            "None",
        ]
        objs = self.primitives.object_names
        for el in objs:
            if "Region" in el and exclude_region:
                objs.remove(el)
        arg.append("IncludedParts:="), arg.append(objs)
        arg.append("HiddenParts:="), arg.append([])
        activecs = self.oeditor.GetActiveCoordinateSystem()
        allcs = self.oeditor.GetCoordinateSystems()
        arg.append("IncludedCS:="), arg.append(allcs)
        arg.append("ReferenceCS:="), arg.append(activecs)
        variables = variables_to_include
        arg.append("IncludedParameters:="), arg.append(variables)
        variables = self._app._variable_manager.dependent_variable_names
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
        arg2.append("Boundaries:="), arg2.append(boundaries)
        if self._app.design_type == "Icepak":
            meshregions = [name for name in self._app.mesh.meshregions.name]
            try:
                meshregions.remove("Global")
            except:
                pass
            arg2.append("MeshRegions:="), arg2.append(meshregions)
        else:
            excitations = self.get_excitations_name()
            arg2.append("Excitations:="), arg2.append(excitations)
        meshops = [el.name for el in self._app.mesh.meshoperations]
        arg2.append("MeshOperations:="), arg2.append(meshops)
        arg3 = ["NAME:ImageFile", "ImageFile:=", ""]
        self.oeditor.Create3DComponent(arg, arg2, component_file, arg3)
        return True
