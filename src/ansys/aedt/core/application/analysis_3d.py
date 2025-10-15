# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 - 2025 ANSYS, Inc. and/or its affiliates.
# SPDX-License-Identifier: MIT
#
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import csv
import os
from pathlib import Path
from typing import List
from typing import Union
import warnings

from ansys.aedt.core.application.analysis import Analysis
from ansys.aedt.core.base import PyAedtBase
from ansys.aedt.core.generic.configurations import Configurations
from ansys.aedt.core.generic.constants import unit_converter
from ansys.aedt.core.generic.file_utils import check_if_path_exists
from ansys.aedt.core.generic.file_utils import generate_unique_name
from ansys.aedt.core.generic.file_utils import get_dxf_layers
from ansys.aedt.core.generic.file_utils import open_file
from ansys.aedt.core.generic.file_utils import read_component_file
from ansys.aedt.core.generic.general_methods import pyaedt_function_handler
from ansys.aedt.core.generic.settings import settings
from ansys.aedt.core.internal.checks import graphics_required
from ansys.aedt.core.internal.checks import min_aedt_version


class FieldAnalysis3D(Analysis, PyAedtBase):
    """Manages 3D field analysis setup in HFSS, Maxwell 3D, and Q3D.

    This class is automatically initialized by an application call from one of
    the 3D tools. See the application function for parameter definitions.

    Parameters
    ----------
    application : str
        3D application that is to initialize the call.
    projectname : str or :class:`pathlib.Path`, optional
        Name of the project to select or the full path to the project
        or AEDTZ archive to open. The default is ``None``, in which
        case an attempt is made to get an active project. If no
        projects are present, an empty project is created.
    designname : str, optional
        Name of the design to select. The default is ``None``, in
        which case an attempt is made to get an active design. If no
        designs are present, an empty design is created.
    solution_type : str, optional
        Solution type to apply to the design. The default is
        ``None``, in which case the default type is applied.
    setup_name : str, optional
        Name of the setup to use as the nominal. The default is
        ``None``, in which case the active setup is used or
        nothing is used.
    version : str, int, float, optional
        Version of AEDT  to use. The default is ``None``, in which case
        the active version or latest installed version is used.
    non_graphical : bool, optional
        Whether to run AEDT in non-graphical mode. The default
        is ``False``, in which case AEDT is launched in the graphical mode.
    new_desktop : bool, optional
        Whether to launch an instance of AEDT in a new thread, even if
        another instance of the ``specified_version`` is active on the
        machine. The default is ``False``.
    close_on_exit : bool, optional
        Whether to release AEDT on exit. The default is ``False``.
    student_version : bool, optional
        Whether to enable the student version of AEDT. The default
        is ``False``.
    aedt_process_id : int, optional
        Only used when ``new_desktop = False``, specifies by process ID which instance
        of Electronics Desktop to point PyAEDT at.
    remove_lock : bool, optional
        Whether to remove lock to project before opening it or not.
        The default is ``False``, which means to not unlock
        the existing project if needed and raise an exception.
    """

    def __init__(
        self,
        application,
        projectname,
        designname,
        solution_type,
        setup_name=None,
        version=None,
        non_graphical=False,
        new_desktop=False,
        close_on_exit=False,
        student_version=False,
        machine="",
        port=0,
        aedt_process_id=None,
        remove_lock=False,
    ):
        Analysis.__init__(
            self,
            application,
            projectname,
            designname,
            solution_type,
            setup_name,
            version,
            non_graphical,
            new_desktop,
            close_on_exit,
            student_version,
            machine,
            port,
            aedt_process_id,
            remove_lock=remove_lock,
        )
        self._post = None
        self._modeler = None
        self._mesh = None
        self._configurations = Configurations(self)
        if not settings.lazy_load:
            self._modeler = self.modeler
            self._mesh = self.mesh
            self._post = self.post

    @property
    def configurations(self):
        """Property to import and export configuration files.

        Returns
        -------
        :class:`ansys.aedt.core.generic.configurations.Configurations`
        """
        return self._configurations

    @property
    def modeler(self):
        """Modeler.

        Returns
        -------
        :class:`ansys.aedt.core.modeler.modeler_3d.Modeler3D` or :class:`ansys.aedt.core.modeler.modeler_2d.Modeler2D`
            Modeler object.
        """
        if self._modeler is None and self._odesign:
            self.logger.reset_timer()

            from ansys.aedt.core.modeler.modeler_2d import Modeler2D
            from ansys.aedt.core.modeler.modeler_3d import Modeler3D

            self._modeler = Modeler2D(self) if self.design_type in ["Maxwell 2D", "2D Extractor"] else Modeler3D(self)
            self.logger.info_timer("Modeler class has been initialized!")
        return self._modeler

    @property
    def mesh(self):
        """Mesh.

        Returns
        -------
        :class:`ansys.aedt.core.modules.mesh.Mesh`
            Mesh object.
        """
        if self._mesh is None and self._odesign:
            self.logger.reset_timer()

            from ansys.aedt.core.modules.mesh import Mesh

            self._mesh = Mesh(self)
            self.logger.info_timer("Mesh class has been initialized!")

        return self._mesh

    @property
    def post(self):
        """PostProcessor.

        Returns
        -------
        :class:`ansys.aedt.core.visualization.post.post_common_3d.PostProcessor3D`
            PostProcessor object.
        """
        if self._post is None and self._odesign:
            from ansys.aedt.core.visualization.post import post_processor

            self._post = post_processor(self)
        return self._post

    @property
    def components3d(self):
        """3D components.

        Returns
        -------
        dict
            Dictionary of 3D components with their absolute paths.

        """
        components_dict = {}

        # Define libraries where 3d components may exist.
        # libs = [syslib, userlib]

        libs = [
            Path(self.syslib) / "3DComponents" / self._design_type,
            Path(self.userlib) / "3DComponents" / self._design_type,
        ]

        for lib in libs:
            if lib.exists():
                for file in lib.rglob("*.a3dcomp"):
                    components_dict[file.stem] = str(file)
        return components_dict

    @pyaedt_function_handler(objects="assignment", export_path="output_file")
    @min_aedt_version("2021.2")
    def plot(
        self,
        assignment=None,
        show=True,
        output_file=None,
        plot_as_separate_objects=True,
        plot_air_objects=True,
        force_opacity_value=None,
        clean_files=False,
        view="isometric",
        show_legend=True,
        dark_mode=False,
        show_grid=False,
        show_bounding=False,
    ):
        """Plot the model or a subset of objects.

        Parameters
        ----------
        assignment : list, optional
            List of objects to plot. The default is ``None``, in which case all objects
            are exported.
        show : bool, optional
            Whether to show the plot after generation. The default is ``True``. If
            ``False``, the generated class is returned for more customization before
            plot generation.
        output_file : str, optional
            Output file path to save the image to. If ``None`` no image will be saved.
        plot_as_separate_objects : bool, optional
            Whether to plot each object separately. The default is ``True``, which may
            require more time to export from AEDT.
        plot_air_objects : bool, optional
            Whether to also plot air and vacuum objects. The default is ``True``.
        force_opacity_value : float, optional
            Opacity value between 0 and 1 to applied to all the models. The
            default is ``None``, which means the AEDT opacity is applied to each object.
        clean_files : bool, optional
            Whether to clean created files after plot generation. The default is ``False``,
            which means that the cache is maintained in the model object that is returned.
        view : str, optional
           View to export. Options are ``"isometric"``, ``"xy"``, ``"xz"``, ``"yz"``.
           The default is ``"isometric"``.
        show_legend : bool, optional
            Whether to display the legend or not. The default is ``True``.
        dark_mode : bool, optional
            Whether to display the model in dark mode or not. The default is ``False``.
        show_grid : bool, optional
            Whether to display the axes grid or not. The default is ``False``.
        show_bounding : bool, optional
            Whether to display the axes bounding box or not. The default is ``False``.

        Returns
        -------
        :class:`ansys.aedt.core.generic.plot.ModelPlotter`
            Model Object.
        """
        return self.post.plot_model_obj(
            objects=assignment,
            show=show,
            export_path=output_file,
            plot_as_separate_objects=plot_as_separate_objects,
            plot_air_objects=plot_air_objects,
            force_opacity_value=force_opacity_value,
            clean_files=clean_files,
            view=view,
            show_legend=show_legend,
            dark_mode=dark_mode,
            show_bounding=show_bounding,
            show_grid=show_grid,
        )

    @pyaedt_function_handler(setup_name="setup", variation_string="variations", mesh_path="output_file")
    def export_mesh_stats(self, setup, variations="", output_file=None):
        """Export mesh statistics to a file.

        Parameters
        ----------
        setup : str
            Setup name.
        variations : str, optional
            Variation list. The default is ``""``.
        output_file : str, optional
            Full path to the mesh statistics file. The default is ``None``, in which
            caswe the working directory is used.

        Returns
        -------
        str
            File path to the mesh statistics file.

        References
        ----------
        >>> oDesign.ExportMeshStats
        """
        if not output_file:
            output_file = str(Path(self.working_directory) / "meshstats.ms")
        self.odesign.ExportMeshStats(setup, variations, output_file)
        return output_file

    @pyaedt_function_handler()
    def get_component_variables(self, name: Union[str, Path]) -> dict:
        """Read component file and extract variables.

        Parameters
        ----------
        name : str or :class:`pathlib.Path`
            Name of the 3D component, which must be in the ``syslib`` or ``userlib`` directory.
            Otherwise, you must specify the full absolute path to the component file.

        Returns
        -------
        dict
            Dictionary of variables in the component file.
        """
        if isinstance(name, Path):
            name = str(name)
        if name not in self.components3d:
            return read_component_file(name)
        else:
            return read_component_file(self.components3d[name])

    @pyaedt_function_handler(component3dname="component_name")
    def get_components3d_vars(self, component_name):
        """Read the A3DCOMP file and check for variables.

        .. deprecated:: 0.15.1
            Use :func:`get_component_variables` method instead.

        Parameters
        ----------
        component_name :
            Name of the 3D component, which must be in the ``syslib`` or ``userlib`` directory. Otherwise,
            you must specify the full absolute path to the AEDTCOMP file with the file name and the extension.

        Returns
        -------
        dict
            Dictionary of variables in the A3DCOMP file.
        """
        warnings.warn(
            "`get_components3d_vars` is deprecated. Use `get_component_variables` method instead.", DeprecationWarning
        )
        return self.get_component_variables(component_name)

    @pyaedt_function_handler(objectname="assignment", property="property_name", type="property_type")
    def get_property_value(self, assignment, property_name, property_type=None):
        """Retrieve a property value.

        Parameters
        ----------
        assignment : str
            Name of the object.
        property_name : str
            Name of the property.
        property_type : str, optional
            Type of the property. Options are ``"boundary"``, ``"excitation"``,
            ``"setup",`` and ``"mesh"``. The default is ``None``.

        Returns
        -------
        type
            Value of the property.

        References
        ----------
        >>> oDesign.GetPropertyValue
        """
        boundary = {"HFSS": "HfssTab", "Icepak": "Icepak", "Q3D": "Q3D", "Maxwell3D": "Maxwell3D"}
        excitation = {"HFSS": "HfssTab", "Icepak": "Icepak", "Q3D": "Q3D", "Maxwell3D": "Maxwell3D"}
        setup = {"HFSS": "HfssTab", "Icepak": "Icepak", "Q3D": "General", "Maxwell3D": "General"}
        mesh = {"HFSS": "MeshSetupTab", "Icepak": "Icepak", "Q3D": "Q3D", "Maxwell3D": "Maxwell3D"}
        all = {
            "HFSS": ["HfssTab", "MeshSetupTab"],
            "Icepak": ["Icepak"],
            "Q3D": ["Q3D", "General"],
            "Maxwell3D": ["Maxwell3D", "General"],
        }
        if property_type == "Boundary":
            propserv = boundary[self._design_type]
            val = self.odesign.GetPropertyValue(propserv, assignment, property_name)
            return val
        elif property_type == "Setup":
            propserv = setup[self._design_type]
            val = self.odesign.GetPropertyValue(propserv, assignment, property_name)
            return val

        elif property_type == "Excitation":
            propserv = excitation[self._design_type]
            val = self.odesign.GetPropertyValue(propserv, assignment, property_name)
            return val

        elif property_type == "Mesh":
            propserv = mesh[self._design_type]
            val = self.odesign.GetPropertyValue(propserv, assignment, property_name)
            return val
        else:
            propservs = all[self._design_type]
            for propserv in propservs:
                properties = list(self.odesign.GetProperties(propserv, assignment))
                if property_name in properties:
                    val = self.odesign.GetPropertyValue(propserv, assignment, property_name)
                    return val
        return None

    @pyaedt_function_handler(object_list="assignment")
    def copy_solid_bodies_from(self, design, assignment=None, no_vacuum=True, no_pec=True, include_sheets=False):
        """Copy a list of objects and user defined models from one design to the active design.

        If user defined models are selected, the project will be saved automatically.

        Parameters
        ----------
        design :
            Starting application object. For example, ``hfss1= HFSS3DLayout``.
        assignment : list, optional
            List of objects and user defined components to copy. The default is ``None``.
        no_vacuum : bool, optional
            Whether to include vacuum objects for the copied objects.
            The default is ``True``.
        no_pec :
            Whether to include pec objects for the copied objects. The
            default is ``True``.
        include_sheets :
            Whether to include sheets for the copied objects. The
            default is ``False``.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.

        References
        ----------
        >>> oEditor.Copy
        >>> oEditor.Paste
        """
        body_list = design.modeler.solid_names
        udc_list = design.modeler.user_defined_component_names
        original_design_type = design.design_type
        dest_design_type = self.design_type
        new_udc_list = []
        if include_sheets:
            body_list += design.modeler.sheet_names
        if udc_list:
            for udc in udc_list:
                if (
                    original_design_type != dest_design_type
                    and not design.modeler.user_defined_components[udc].is3dcomponent
                    or original_design_type == dest_design_type
                ):
                    new_udc_list.append(udc)
                parts = design.modeler.user_defined_components[udc].parts
                for part_id in parts:
                    part_name = parts[part_id].name
                    if part_name in body_list:
                        body_list.remove(part_name)

        selection_list = []
        udc_selection = []
        material_properties = design.modeler.objects
        selections = self.modeler.convert_to_selections(assignment, True)

        if selections:
            selection_list = [i for i in selections if i in body_list]
            for udc in new_udc_list:
                if udc in selections:
                    udc_selection.append(udc)
        else:
            for body in body_list:
                include_object = True
                for key, val in material_properties.items():
                    if val.name == body:
                        if no_vacuum and val.material_name.lower() == "vacuum":
                            include_object = False
                        if no_pec and val.material_name == "pec":
                            include_object = False
                if include_object:
                    selection_list.append(body)
            for udm in new_udc_list:
                udc_selection.append(udm)
        selection_list = selection_list + udc_selection
        design.modeler.oeditor.Copy(["NAME:Selections", "Selections:=", ",".join(selection_list)])
        self.modeler.oeditor.Paste()
        if udc_selection:
            self.save_project()
            self._project_dictionary = None
        self.modeler.refresh_all_ids()
        return True

    @pyaedt_function_handler(filename="input_file")
    def import_3d_cad(
        self,
        input_file,
        healing=False,
        refresh_all_ids=True,
        import_materials=False,
        create_lightweigth_part=False,
        group_by_assembly=False,
        create_group=True,
        separate_disjoints_lumped_object=False,
        import_free_surfaces=False,
        point_coicidence_tolerance=1e-6,
        reduce_stl=False,
        reduce_percentage=0,
        reduce_error=0,
        merge_planar_faces=True,
    ):
        """Import a CAD model.

        Parameters
        ----------
        input_file : str
            Full path and name of the CAD file.
        healing : bool, optional
            Whether to perform healing. The default is ``False``.
        refresh_all_ids : bool, optional
            Whether to refresh all IDs after the CAD file is loaded. The
            default is ``True``. Refreshing IDs can take a lot of time in
            a big project.
        import_materials : bool optional
            Whether to import material names from the file if present. The
            default is ``False``.
        create_lightweigth_part : bool ,optional
            Whether to import a lightweight part. The default is ``True``.
        group_by_assembly : bool, optional
            Whether to import by subassembly. The default is ``False``, in which
            case the import is by individual parts.
        create_group : bool, optional
            Whether to create a group of imported objects. The default is ``True``.
        separate_disjoints_lumped_object : bool, optional
            Whether to automatically separate disjoint parts. The default is ``False``.
        import_free_surfaces : bool, optional
            Whether to import free surfaces parts. The default is ``False``.
        point_coicidence_tolerance : float, optional
            Tolerance on the point. The default is ``1e-6``.
        reduce_stl : bool, optional
            Whether to reduce the STL file on import. The default is ``True``.
        reduce_percentage : int, optional
            Percentage to reduce the STL file by if ``reduce_stl=True``. The default is ``0``.
        reduce_error : int, optional
            Error percentage during STL reduction operation. The default is ``0``.
        merge_planar_faces : bool, optional
            Whether to merge planar faces during import. The default is ``True``.

        Returns
        -------
         bool
            ``True`` when successful, ``False`` when failed.

        References
        ----------
        >>> oEditor.Import
        """
        return self.modeler.import_3d_cad(
            input_file=input_file,
            healing=healing,
            refresh_all_ids=refresh_all_ids,
            import_materials=import_materials,
            create_lightweigth_part=create_lightweigth_part,
            group_by_assembly=group_by_assembly,
            create_group=create_group,
            separate_disjoints_lumped_object=separate_disjoints_lumped_object,
            import_free_surfaces=import_free_surfaces,
            point_coicidence_tolerance=point_coicidence_tolerance,
            reduce_stl=reduce_stl,
            reduce_percentage=reduce_percentage,
            reduce_error=reduce_error,
            merge_planar_faces=merge_planar_faces,
        )

    @pyaedt_function_handler(
        object_list="assignment_to_export",
        removed_objects="assignment_to_remove",
        fileName="file_name",
        filePath="file_path",
        fileFormat="file_format",
    )
    def export_3d_model(
        self,
        file_name="",
        file_path="",
        file_format=".step",
        assignment_to_export=None,
        assignment_to_remove=None,
        major_version=-1,
        minor_version=-1,
    ):
        """Export the 3D model.

        Parameters
        ----------
        file_name : str, optional
            Name of the file.
        file_path : str, optional
            Path for the file.
        file_format : str, optional
            Format of the file. The default is ``".step"``.
        assignment_to_export : list, optional
            List of objects to export. The default is ``None``.
        assignment_to_remove : list, optional
            List of objects to remove. The default is ``None``.
        major_version : int, optional
            File format major version. Default is -1.
        minor_version : int, optional
            File format major version. Default is -1.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.

        References
        ----------
        >>> oEditor.Export
        """
        return self.modeler.export_3d_model(
            file_name=file_name,
            file_path=file_path,
            file_format=file_format,
            assignment_to_export=assignment_to_export,
            assignment_to_remove=assignment_to_remove,
            major_version=major_version,
            minor_version=minor_version,
        )

    @pyaedt_function_handler()
    def get_all_sources(self):
        """Retrieve all setup sources.

        Returns
        -------
        list of str
            List of all setup sources.

        References
        ----------
        >>> oModule.GetAllSources
        """
        return list(self.osolution.GetAllSources())

    @pyaedt_function_handler()
    def get_all_source_modes(self):
        """Retrieve all source modes.

        Returns
        -------
        list of str
            List of all source modes.

        References
        ----------
        >>> oModule.GetAllSources
        """
        return list(self.osolution.GetAllSourceModes())

    @pyaedt_function_handler()
    def set_source_context(self, sources, number_of_modes=1):
        """Set the source context.

        Parameters
        ----------
        sources : list
            List of source names.
        number_of_modes : int, optional
            Number of modes. The default is ``1``.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.

        References
        ----------
        >>> oModule.SetSourceContexts
        """
        contexts = []
        for s in sources:
            value = s
            if number_of_modes > 0:
                for i in range(number_of_modes):
                    value += ":" + str(i + 1)
            contexts.append(value)  # use one based indexing
        self.osolution.SetSourceContexts(contexts)
        return True

    @pyaedt_function_handler(obj="assignment", mat="material")
    def assign_material(self, assignment, material):
        """Assign a material to one or more objects.

        Parameters
        ----------
        assignment : str, list
            One or more objects to assign materials to.
        material : str
            Material to assign. If this material is not present, it is
            created.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.

        References
        ----------
        >>> oEditor.AssignMaterial

        Examples
        --------
        The method :func:`assign_material` is used to assign a material to a list of objects.

        Open a design and create the objects.

        >>> from ansys.aedt.core import Hfss
        >>> hfss = Hfss()
        >>> box1 = hfss.modeler.create_box([10, 10, 10], [4, 5, 5])
        >>> box2 = hfss.modeler.create_box([0, 0, 0], [2, 3, 4])
        >>> cylinder1 = hfss.modeler.create_cylinder(orientation="X", origin=[5, 0, 0], radius=1, height=20)
        >>> cylinder2 = hfss.modeler.create_cylinder(orientation="Z", origin=[0, 0, 5], radius=1, height=10)

        Assign the material ``"copper"`` to all the objects.

        >>> objects_list = [box1, box2, cylinder1, cylinder2]
        >>> hfss.assign_material(objects_list, "copper")

        The method also accepts a list of object names.

        >>> obj_names_list = [box1.name, box2.name, cylinder1.name, cylinder2.name]
        >>> hfss.assign_material(obj_names_list, "aluminum")
        """
        matobj = None
        selections = self.modeler.convert_to_selections(assignment, True)

        if material.lower() in self.materials.material_keys:
            matobj = self.materials.material_keys[material.lower()]
        elif self.materials._get_aedt_case_name(material) or settings.remote_api or settings.remote_rpc_session:
            matobj = self.materials._aedmattolibrary(material)
        if matobj:
            if self.design_type == "HFSS":
                solve_inside = matobj.is_dielectric()
            elif self.design_type in ["Maxwell 2D", "Maxwell 3D"]:
                solve_inside = True
                if material in ["pec", "perfect conductor"]:
                    solve_inside = False
            else:
                solve_inside = True
            slice_sel = min(50, len(selections))
            num_objects = len(selections)
            remaining = num_objects
            while remaining >= 1:
                objs = selections[:slice_sel]
                szSelections = self.modeler.convert_to_selections(objs)
                vArg1 = [
                    "NAME:Selections",
                    "AllowRegionDependentPartSelectionForPMLCreation:=",
                    True,
                    "AllowRegionSelectionForPMLCreation:=",
                    True,
                    "Selections:=",
                    szSelections,
                ]
                vArg2 = [
                    "NAME:Attributes",
                    "MaterialValue:=",
                    f'"{matobj.name}"',
                    "SolveInside:=",
                    solve_inside,
                    "ShellElement:=",
                    False,
                    "ShellElementThickness:=",
                    "nan ",
                    "IsMaterialEditable:=",
                    True,
                    "UseMaterialAppearance:=",
                    True,
                    "IsLightweight:=",
                    False,
                ]
                self.oeditor.AssignMaterial(vArg1, vArg2)
                for el in objs:
                    self.modeler[el]._material_name = matobj.name
                    self.modeler[el]._color = matobj.material_appearance
                    self.modeler[el]._solve_inside = solve_inside
                remaining -= slice_sel
                if remaining > 0:
                    selections = selections[slice_sel:]

            return True
        else:
            self.logger.error("Material does not exist.")
            return False

    @pyaedt_function_handler()
    def get_all_conductors_names(self):
        """Retrieve all conductors in the active design.

        Returns
        -------
        list of str
            List of all conductors.

        References
        ----------
        >>> oEditor.GetObjectsByMaterial
        """
        if len(self.modeler.objects) != len(self.modeler.object_names):
            self.modeler.refresh_all_ids()
        obj_names = []
        for _, val in self.modeler.objects.items():
            try:
                if val.material_name and self.materials[val.material_name].is_conductor():
                    obj_names.append(val.name)
            except KeyError:
                pass
        return obj_names

    @pyaedt_function_handler()
    def get_all_dielectrics_names(self):
        """Retrieve all dielectrics in the active design.

        Returns
        -------
        list of str
           List of all dielectrics.

        References
        ----------
        >>> oEditor.GetObjectsByMaterial
        """
        if len(self.modeler.objects) != len(self.modeler.object_names):
            self.modeler.refresh_all_ids()
        obj_names = []
        for _, val in self.modeler.objects.items():
            try:
                if val.material_name and self.materials[val.material_name].is_dielectric():
                    obj_names.append(val.name)
            except KeyError:
                pass
        return obj_names

    @pyaedt_function_handler()
    def _create_dataset_from_sherlock(self, material_string, property_name="Mass_Density"):
        mats = material_string.split(",")
        mat_temp = [[i.split("@")[0], i.split("@")[1]] for i in mats]
        nominal_id = int(len(mat_temp) / 2)
        nominal_val = float(mat_temp[nominal_id - 1][0])
        ds_name = generate_unique_name(property_name)
        self.create_dataset(
            ds_name,
            [float(i[1].replace("C", "").replace("K", "").replace("F", "")) for i in mat_temp],
            [float(i[0]) / nominal_val for i in mat_temp],
        )
        return nominal_val, "$" + ds_name

    @pyaedt_function_handler(csv_component="component_file", csv_material="material_file")
    def assignmaterial_from_sherlock_files(self, component_file, material_file):
        """Assign material to objects in a design based on a CSV file obtained from Sherlock.

        Parameters
        ----------
        component_file :  str
            Name of the CSV file containing the component properties, including the
            material name.
        material_file : str
            Name of the CSV file containing the material properties.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.

        References
        ----------
        >>> oEditor.AssignMaterial
        """
        with open_file(material_file) as csvfile:
            csv_input = csv.reader(csvfile)
            material_header = next(csv_input)
            data = list(csv_input)
            k = 0
            material_data = {}
            for el in material_header:
                material_data[el] = [i[k] for i in data]
                k += 1
        with open_file(component_file) as csvfile:
            csv_input = csv.reader(csvfile)
            component_header = next(csv_input)
            data = list(csv_input)
            k = 0
            component_data = {}
            for el in component_header:
                component_data[el] = [i[k] for i in data]
                k += 1
        all_objs = self.modeler.object_names
        i = 0
        for mat in material_data["Name"]:
            list_mat_obj = [
                "COMP_" + rd for rd, md in zip(component_data["Ref Des"], component_data["Material"]) if md == mat
            ]
            list_mat_obj += [rd for rd, md in zip(component_data["Ref Des"], component_data["Material"]) if md == mat]
            list_mat_obj = [mo for mo in list_mat_obj if mo in all_objs]
            if list_mat_obj:
                newmat = self.materials.exists_material(mat)
                if not newmat:
                    newmat = self.materials.add_material(mat.lower())
                if "Material Density" in material_data:
                    if "@" in material_data["Material Density"][i] and "," in material_data["Material Density"][i]:
                        nominal_val, dataset_name = self._create_dataset_from_sherlock(
                            material_data["Material Density"][i], "Mass_Density"
                        )
                        newmat.mass_density = nominal_val
                        newmat.mass_density.thermalmodifier = f"pwl({dataset_name}, Temp)"
                    else:
                        value = material_data["Material Density"][i]
                        newmat.mass_density = value
                if "Thermal Conductivity" in material_data:
                    if (
                        "@" in material_data["Thermal Conductivity"][i]
                        and "," in material_data["Thermal Conductivity"][i]
                    ):
                        nominal_val, dataset_name = self._create_dataset_from_sherlock(
                            material_data["Thermal Conductivity"][i], "Thermal_Conductivity"
                        )
                        newmat.thermal_conductivity = nominal_val
                        newmat.thermal_conductivity.thermalmodifier = f"pwl({dataset_name}, Temp)"
                    else:
                        value = material_data["Thermal Conductivity"][i]
                        newmat.thermal_conductivity = value
                if "Material CTE" in material_data:
                    if "@" in material_data["Material CTE"][i] and "," in material_data["Material CTE"][i]:
                        nominal_val, dataset_name = self._create_dataset_from_sherlock(
                            material_data["Material CTE"][i], "CTE"
                        )
                        newmat.thermal_expansion_coefficient = nominal_val
                        newmat.thermal_expansion_coefficient.thermalmodifier = f"pwl({dataset_name}, Temp)"
                    else:
                        value = material_data["Material CTE"][i]
                        newmat.thermal_expansion_coefficient = value
                if "Poisson Ratio" in material_data:
                    if "@" in material_data["Poisson Ratio"][i] and "," in material_data["Poisson Ratio"][i]:
                        nominal_val, dataset_name = self._create_dataset_from_sherlock(
                            material_data["Poisson Ratio"][i], "Poisson_Ratio"
                        )
                        newmat.poissons_ratio = nominal_val
                        newmat.poissons_ratio.thermalmodifier = f"pwl({dataset_name}, Temp)"
                    else:
                        value = material_data["Poisson Ratio"][i]
                        newmat.poissons_ratio = value
                if "Elastic Modulus" in material_data:
                    if "@" in material_data["Elastic Modulus"][i] and "," in material_data["Elastic Modulus"][i]:
                        nominal_val, dataset_name = self._create_dataset_from_sherlock(
                            material_data["Elastic Modulus"][i], "Youngs_Modulus"
                        )
                        newmat.youngs_modulus = nominal_val
                        newmat.youngs_modulus.thermalmodifier = f"pwl({dataset_name}, Temp)"
                    else:
                        value = material_data["Elastic Modulus"][i]
                        newmat.youngs_modulus = value
                self.assign_material(list_mat_obj, mat)

                for obj_name in list_mat_obj:
                    if not self.modeler[obj_name].surface_material_name:
                        self.modeler[obj_name].surface_material_name = "Steel-oxidised-surface"
            i += 1
            all_objs = [ao for ao in all_objs if ao not in list_mat_obj]
        return True

    @pyaedt_function_handler()
    def cleanup_solution(self, variations="All", entire_solution=True, field=True, mesh=True, linked_data=True):
        """Delete a set of Solution Variations or part of them.

        Parameters
        ----------
        variations : List, str, optional
            All variations to delete. Default is `"All"` which deletes all available solutions.
        entire_solution : bool, optional
            Either if delete entire Solution or part of it. If `True` other booleans will be ignored
            as solution will be entirely deleted.
        field : bool, optional
            Either if delete entire Fields of variation or not. Default is `True`.
        mesh : bool, optional
            Either if delete entire Mesh of variation or not. Default is `True`.
        linked_data : bool, optional
            Either if delete entire Linked Data of variation or not. Default is `True`.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.
        """
        if isinstance(variations, str):
            variations = [variations]
        if entire_solution:
            self.odesign.DeleteFullVariation(variations, linked_data)
        elif field:
            self.odesign.DeleteFieldVariation(variations, mesh, linked_data)
        elif linked_data:
            self.odesign.DeleteLinkedDataVariation(variations)
        return True

    @pyaedt_function_handler
    def add_stackup_3d(self):
        """Create a stackup 3D object.

        Returns
        -------
        :class:`ansys.aedt.core.modeler.stackup_3d.Stackup3D`
            Stackup class.
        """
        from ansys.aedt.core.modeler.advanced_cad.stackup_3d import Stackup3D

        return Stackup3D(self)

    @pyaedt_function_handler(component_name="components")
    def flatten_3d_components(self, components=None, purge_history=True, password=None):
        """Flatten one or multiple 3d components in the actual layout.

        Each 3d Component is replaced with objects.
        This function will work only if the reference coordinate system of the 3d component is the global one.

        Parameters
        ----------
        components : str, list, optional
            List of user defined components. The Default is ``None`` for all 3d Components.
        purge_history : bool, optional
            Define if the 3D Component will be purged before copied.
            This is needed when more than 1 component with the same definition is present.
        password : str, optional
            Password for encrypted 3d component.
            The Default is ``None``.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.
        """
        if password is None:
            password = os.getenv("PYAEDT_ENCRYPTED_PASSWORD", "")
        native_comp_names = [nc.definition_name for nc in self.native_components.values()]
        if not components:
            components = [
                key
                for key, val in self.modeler.user_defined_components.items()
                if val.definition_name not in native_comp_names
            ]
        else:
            if isinstance(components, str):
                components = [components]
            for cmp in components:
                if cmp not in self.modeler.user_defined_component_names:
                    raise ValueError(f"Component definition was not found for '{cmp}'.")

        for cmp in components:
            comp = self.modeler.user_defined_components[cmp]
            # TODO: Call edit_definition only once
            target_cs = self.modeler._create_reference_cs_from_3dcomp(comp, password=password)
            app = comp.edit_definition(password=password)
            for var, val in comp.parameters.items():
                self[var] = val
            if purge_history:
                app.modeler.purge_history(app.modeler._all_object_names)
            monitor_cache = {}
            if self.design_type == "Icepak":
                objs_monitors = [part.name for _, part in comp.parts.items()]
                all_monitors = self.monitor.all_monitors.items()
                for _, mon_obj in all_monitors:
                    obj_name = mon_obj.properties["Geometry Assignment"]
                    if obj_name in objs_monitors:
                        monitor_cache.update({mon_obj.name: mon_obj.properties})
                        monitor_cache[mon_obj.name]["Native Assignment"] = "placeholder"
                        if monitor_cache[mon_obj.name]["Type"] == "Face":
                            monitor_cache[mon_obj.name]["Area Assignment"] = self.modeler.get_face_area(
                                monitor_cache[mon_obj.name]["ID"]
                            )
                        elif monitor_cache[mon_obj.name]["Type"] == "Surface":
                            monitor_cache[mon_obj.name]["Area Assignment"] = self.modeler.get_face_area(
                                self.modeler.get_object_from_name(monitor_cache[mon_obj.name]["ID"]).faces[0].id
                            )
                        elif monitor_cache[mon_obj.name]["Type"] == "Object":
                            monitor_cache[mon_obj.name]["Volume Assignment"] = self.modeler.get_object_from_name(
                                monitor_cache[mon_obj.name]["ID"]
                            ).volume
                for _, mon_dict in monitor_cache.items():
                    del mon_dict["Object"]
            oldcs = self.oeditor.GetActiveCoordinateSystem()
            self.modeler.set_working_coordinate_system(target_cs)
            comp.delete()
            obj_set = set(self.modeler.objects.values())
            self.copy_solid_bodies_from(app, no_vacuum=False, no_pec=False, include_sheets=True)
            self.modeler.refresh_all_ids()
            self.modeler.set_working_coordinate_system(oldcs)
            if self.design_type == "Icepak":
                for monitor_obj, mon_dict in monitor_cache.items():
                    if not self.monitor.insert_monitor_object_from_dict(mon_dict, mode=1):
                        dict_in = {"monitor": {monitor_obj: mon_dict}}
                        self.configurations._monitor_assignment_finder(dict_in, monitor_obj, obj_set)
                        m_type = dict_in["monitor"][monitor_obj]["Type"]
                        m_obj = dict_in["monitor"][monitor_obj]["ID"]
                        if not self.configurations.update_monitor(
                            m_type, m_obj, dict_in["monitor"][monitor_obj]["Quantity"], monitor_obj
                        ):  # pragma: no cover
                            return False
            app.close_project()

        if not self.design_type == "Icepak":
            self.mesh._refresh_mesh_operations()
        return True

    @pyaedt_function_handler(object_name="assignment")
    @graphics_required
    @min_aedt_version("2023.2")
    def identify_touching_conductors(self, assignment=None):
        """Identify all touching components and group in a dictionary.

        This method requires that the ``pyvista`` package is installed.

        Parameters
        ----------
        assignment : str, optional
            Starting object to check for touching elements. The default is ``None``.

        Returns
        -------
        dict

        """
        import pyvista as pv

        if self.design_type == "HFSS":  # pragma: no cover
            nets_aedt = self.oboundary.IdentifyNets(True)
            nets = {}
            for net in nets_aedt[1:]:
                nets[net[0].split(":")[1]] = list(net[1][1:])
            if assignment:
                for net, net_vals in nets.items():
                    if assignment in net_vals:
                        output = {"Net1": net_vals}
                        return output
            return nets
        plt_obj = self.plot(assignment=self.get_all_conductors_names(), show=False)

        nets = {}
        inputs = []
        for cad in plt_obj.objects:
            # if (self.modeler[cad.name].is_conductor):
            filedata = pv.read(cad.path)
            cad._cached_polydata = filedata
            inputs.append(cad)

        if assignment:
            cad_to_investigate = [i for i in inputs if i.name == assignment][0]
            inputs = [i for i in inputs if i.name != assignment]

        else:
            cad_to_investigate = inputs[0]
            inputs = inputs[1:]
        if not inputs:
            self.logger.error("At least one conductor is needed.")
            return {}

        def check_intersections(output, input_list, cad_in=None):
            if cad_in is None:
                cad_in = output[-1]
            temp_out = []
            for cad in input_list:
                if cad != cad_in and cad not in output:
                    col, n_contacts = cad_in._cached_polydata.collision(cad._cached_polydata, 1)
                    if n_contacts > 0:
                        output.append(cad)
                        temp_out.append(cad)
                        input_list = [i for i in input_list if i != cad]
            for cad in temp_out:
                check_intersections(output, input_list, cad)
                list(set(output))
            return output

        k = 1
        while len(inputs) > 0:
            net = [cad_to_investigate]
            check_intersections(net, inputs)
            inputs = [i for i in inputs if i not in net]
            nets[f"Net{k}"] = [i.name for i in net]
            if assignment:
                break
            if inputs:
                cad_to_investigate = inputs[0]
                inputs = inputs[1:]
                k += 1
                if len(inputs) == 0:
                    nets[f"Net{k}"] = [cad_to_investigate.name]
                    break
        return nets

    @pyaedt_function_handler(file_path="input_file")
    def get_dxf_layers(self, input_file: Union[str, Path]) -> List[str]:
        """Read a DXF file and return all layer names.

        .. deprecated:: 0.15.1
            Use :func:`ansys.aedt.core.generic.file_utils.get_dxf_layers` method instead.

        Parameters
        ----------
        input_file : str or :class:`pathlib.Path`
            Full path to the DXF file.

        Returns
        -------
        list
            List of layers in the DXF file.
        """
        warnings.warn(
            "`get_dxf_layers` is deprecated. Use `ansys.aedt.core.generic.file_utils.get_dxf_layers` method instead.",
            DeprecationWarning,
        )

        return get_dxf_layers(input_file)

    @pyaedt_function_handler(layers_list="layers", file_path="input_file")
    def import_dxf(
        self,
        input_file: Union[str, Path],
        layers: List[str],
        auto_detect_close: bool = True,
        self_stitch: bool = True,
        self_stitch_tolerance: float = 0.0,
        scale: float = 0.001,
        defeature_geometry: bool = False,
        defeature_distance: float = 0.0,
        round_coordinates: bool = False,
        round_num_digits: int = 4,
        write_poly_with_width_as_filled_poly: bool = False,
        import_method: Union[int, bool] = 1,
    ) -> bool:  # pragma: no cover
        """Import a DXF file.

        Parameters
        ----------
        input_file : str or :class:`pathlib.Path`
            Path to the DXF file.
        layers : list
            List of layer names to import. To get the dxf_layers in the DXF file,
            you can call the ``get_dxf_layers`` method.
        auto_detect_close : bool, optional
            Whether to check polylines to see if they are closed.
            The default is ``True``. If a polyline is closed, the modeler
            creates a polygon in the design.
        self_stitch : bool, optional
            Whether to join multiple straight line segments to form polylines.
            The default is ``True``.
        self_stitch_tolerance : float, optional
            Self stitch tolerance value. If negative, let importer use its default tolerance. The default is ``0``.
        scale : float, optional
            Scaling factor. The default is ``0.001``. The units are ``mm``.
        defeature_geometry : bool, optional
            Whether to defeature the geometry to reduce complexity.
            The default is ``False``.
        defeature_distance : float, optional
            Defeature tolerance distance. The default is ``0``.
        round_coordinates : bool, optional
            Whether to round all imported data to the number
            of decimal points specified by the next parameter.
            The default is ``False``.
        round_num_digits : int, optional
            Number of digits to which to round all imported data.
            The default is ``4``.
        write_poly_with_width_as_filled_poly : bool, optional
            Imports wide polylines as polygons. The default is ``False``.
        import_method : int or bool, optional
            Whether the import method is ``Script`` or ``Parasolid``.
            The default is ``1``, which means that the ``Parasolid`` is used.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.

        References
        ----------
        >>> oEditor.ImportDXF

        """
        input_file = Path(input_file)
        if self.desktop_class.non_graphical and self.desktop_class.aedt_version_id < "2024.2":  # pragma: no cover
            self.logger.error("Method is supported only in graphical mode.")
            return False
        dxf_layers = get_dxf_layers(input_file)
        for layer in layers:
            if layer not in dxf_layers:
                self.logger.error(f"{layer} does not exist in specified dxf.")
                return False

        if hasattr(self, "is3d") and self.is3d:
            sheet_bodies_2d = False
        else:
            sheet_bodies_2d = True

        vArg1 = ["NAME:options"]
        vArg1.append("FileName:="), vArg1.append(str(input_file.as_posix()))
        vArg1.append("Scale:="), vArg1.append(scale)
        vArg1.append("AutoDetectClosed:="), vArg1.append(auto_detect_close)
        vArg1.append("SelfStitch:="), vArg1.append(self_stitch)
        if self_stitch_tolerance >= 0.0:
            vArg1.append("SelfStitchTolerance:="), vArg1.append(self_stitch_tolerance)
        vArg1.append("DefeatureGeometry:="), vArg1.append(defeature_geometry)
        vArg1.append("DefeatureDistance:="), vArg1.append(defeature_distance)
        vArg1.append("RoundCoordinates:="), vArg1.append(round_coordinates)
        vArg1.append("RoundNumDigits:="), vArg1.append(round_num_digits)
        vArg1.append("WritePolyWithWidthAsFilledPoly:="), vArg1.append(write_poly_with_width_as_filled_poly)
        vArg1.append("ImportMethod:="), vArg1.append(import_method)
        vArg1.append("2DSheetBodies:="), vArg1.append(sheet_bodies_2d)
        vArg2 = ["NAME:LayerInfo"]
        for layer in layers:
            vArg3 = ["Name:" + layer]
            vArg3.append("source:="), vArg3.append(layer)
            vArg3.append("display_source:="), vArg3.append(layer)
            vArg3.append("import:="), vArg3.append(True)
            vArg3.append("dest:="), vArg3.append(layer)
            vArg3.append("dest_selected:="), vArg3.append(False)
            vArg3.append("layer_type:="), vArg3.append("signal")
            vArg2.append(vArg3)
        vArg1.append(vArg2)
        self.oeditor.ImportDXF(vArg1)
        return True

    @pyaedt_function_handler(gds_file="input_file", gds_number="mapping_layers", unit="units")
    def import_gds_3d(self, input_file: str, mapping_layers: dict, units: str = "um", import_method: int = 1) -> bool:
        """Import a GDSII file.

        Parameters
        ----------
        input_file : str
            Path to the GDS file.
        mapping_layers : dict
            Dictionary keys are GDS layer numbers, and the value is a tuple with the elevation and thickness.
        units : str, optional
            Length unit values. The default is ``"um"``.
        import_method : integer, optional
            GDSII import method. The default is ``1``. Options are:

            - ``0`` for script.
            - ``1`` for Parasolid.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.

        References
        ----------
        >>> oEditor.ImportGDSII

        Examples
        --------
        Import a GDS file in an HFSS 3D project.

        >>> gds_path = r"C:\\temp\\gds1.gds"
        >>> from ansys.aedt.core import Hfss
        >>> hfss = Hfss()
        >>> gds_number = {7: (100, 10), 9: (110, 5)}
        >>> hfss.import_gds_3d(gds_path, gds_number, units="um", import_method=1)

        """
        if self.desktop_class.non_graphical and self.desktop_class.aedt_version_id < "2024.1":  # pragma: no cover
            self.logger.error("Method is supported only in graphical mode.")
            return False
        if not check_if_path_exists(input_file):
            self.logger.error("GDSII file does not exist. No layer is imported.")
            return False
        if len(mapping_layers) == 0:
            self.logger.error("Dictionary for GDSII layer numbers is empty. No layer is imported.")
            return False

        layermap = ["NAME:LayerMap"]
        ordermap = []
        for i, k in enumerate(mapping_layers):
            layername = "signal" + str(k)
            layermap.append(
                [
                    "NAME:LayerMapInfo",
                    "LayerNum:=",
                    k,
                    "DestLayer:=",
                    layername,
                    "layer_type:=",
                    "signal",
                ]
            )
            ordermap1 = [
                "entry:=",
                [
                    "order:=",
                    i,
                    "layer:=",
                    layername,
                    "LayerNumber:=",
                    k,
                    "Thickness:=",
                    unit_converter(mapping_layers[k][1], unit_system="Length", input_units=units, output_units="meter"),
                    "Elevation:=",
                    unit_converter(mapping_layers[k][0], unit_system="Length", input_units=units, output_units="meter"),
                    "Color:=",
                    "color",
                ],
            ]
            ordermap.extend(ordermap1)

        self.oeditor.ImportGDSII(
            [
                "NAME:options",
                "FileName:=",
                input_file,
                "FlattenHierarchy:=",
                True,
                "ImportMethod:=",
                import_method,
                layermap,
                "OrderMap:=",
                ordermap,
            ]
        )
        self.logger.info("GDS layer imported with elevations and thickness.")
        return True
