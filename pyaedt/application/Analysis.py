"""
This module contains the ``analysis`` class.

It includes common classes for file management and messaging and all
calls to AEDT modules like the modeler, mesh, postprocessing, and setup.
"""

from __future__ import absolute_import  # noreorder

import os
import shutil
import threading
import warnings
from collections import OrderedDict

from pyaedt.application.Design import Design
from pyaedt.application.JobManager import update_hpc_option
from pyaedt.generic.constants import AXIS
from pyaedt.generic.constants import CoordinateSystemAxis
from pyaedt.generic.constants import CoordinateSystemPlane
from pyaedt.generic.constants import GRAVITY
from pyaedt.generic.constants import GravityDirection
from pyaedt.generic.constants import PLANE
from pyaedt.generic.constants import Plane
from pyaedt.generic.constants import SETUPS
from pyaedt.generic.constants import SOLUTIONS
from pyaedt.generic.constants import VIEW
from pyaedt.generic.general_methods import filter_tuple
from pyaedt.generic.general_methods import generate_unique_name
from pyaedt.generic.general_methods import pyaedt_function_handler
from pyaedt.modules.Boundary import NativeComponentObject
from pyaedt.modules.DesignXPloration import OptimizationSetups
from pyaedt.modules.DesignXPloration import ParametricSetups
from pyaedt.modules.MaterialLib import Materials
from pyaedt.modules.SolveSetup import Setup


class Analysis(Design, object):
    """Contains all common analysis functions.

    This class is inherited in the caller application and is accessible through it ( eg. ``hfss.method_name``).


    It is automatically initialized by a call from an application, such as HFSS or Q3D.
    See the application function for its parameter descriptions.

    Parameters
    ----------
    application : str
        Application that is to initialize the call.
    projectname : str
        Name of the project to select or the full path to the project
        or AEDTZ archive to open.
    designname : str
        Name of the design to select.
    solution_type : str
        Solution type to apply to the design.
    setup_name : str
        Name of the setup to use as the nominal.
    specified_version : str
        Version of AEDT  to use.
    NG : bool
        Whether to run AEDT in the non-graphical mode.
    new_desktop_session : bool
        Whether to launch an instance of AEDT in a new thread, even if
        another instance of the ``specified_version`` is active on the
        machine.
    close_on_exit : bool
        Whether to release  AEDT on exit.
    student_version : bool
        Whether to enable the student version of AEDT.

    """

    def __init__(
        self,
        application,
        projectname,
        designname,
        solution_type,
        setup_name,
        specified_version,
        non_graphical,
        new_desktop_session,
        close_on_exit,
        student_version,
    ):
        self.setups = []
        Design.__init__(
            self,
            application,
            projectname,
            designname,
            solution_type,
            specified_version,
            non_graphical,
            new_desktop_session,
            close_on_exit,
            student_version,
        )

        self.logger.info("Design Loaded")
        self._setup = None
        if setup_name:
            self.analysis_setup = setup_name
        self.solution_type = solution_type
        self._materials = Materials(self)
        self.logger.info("Materials Loaded")
        self._available_variations = self.AvailableVariations(self)
        if "HFSS 3D Layout Design" in self.design_type:
            self._oanalysis = self._odesign.GetModule("SolveSetups")
        elif "EMIT" in self.design_type or "Maxwell Circuit" in self.design_type:
            self._oanalysis = None
        elif "Circuit Design" in self.design_type or "Twin Builder" in self.design_type:
            self._oanalysis = self._odesign.GetModule("SimSetup")
        else:
            self._oanalysis = self._odesign.GetModule("AnalysisSetup")

        if self.design_type != "Maxwell Circuit":
            self._ooptimetrics = self._odesign.GetModule("Optimetrics")
            self._ooutput_variable = self._odesign.GetModule("OutputVariable")
            self.setups = [self.get_setup(setup_name) for setup_name in self.setup_names]

        self.parametrics = ParametricSetups(self)
        self.optimizations = OptimizationSetups(self)
        self.native_components = self._get_native_data()
        self.SOLUTIONS = SOLUTIONS()
        self.SETUPS = SETUPS()
        self.AXIS = AXIS()
        self.PLANE = PLANE()
        self.VIEW = VIEW()
        self.GRAVITY = GRAVITY()

    @property
    def ooptimetrics(self):
        """AEDT Optimetrics Module.

        References
        ----------

        >>> oDesign.GetModule("Optimetrics")
        """
        return self._ooptimetrics

    @property
    def ooutput_variable(self):
        """AEDT Output Variable Module.

        References
        ----------

        >>> oDesign.GetModule("OutputVariable")
        """
        return self._ooutput_variable

    @property
    def oanalysis(self):
        """Analysis AEDT Module.

        References
        ----------

        >>> oDesign.GetModule("SolveSetups")
        >>> oDesign.GetModule("SimSetup")
        >>> oDesign.GetModule("AnalysisSetup")
        """
        return self._oanalysis

    @property
    def output_variables(self):
        """List of output variables.

        Returns
        -------
        list of str

        References
        ----------

        >>> oModule.GetOutputVariables()
        """
        return self.ooutput_variable.GetOutputVariables()

    @property
    def materials(self):
        """Materials in the project.

        Returns
        -------
        :class:`pyaedt.modules.MaterialLib.Materials`
           Materials in the project.

        """
        return self._materials

    @property
    def Position(self):
        """Position of the object.

        Returns
        -------
        type
            Position object.

        """
        return self.modeler.Position

    @property
    def available_variations(self):
        """Available variation object.

        Returns
        -------
        :class:`pyaedt.application.Analysis.Analysis.AvailableVariations`
            Available variation object.

        """
        return self._available_variations

    @property
    def CoordinateSystemAxis(self):
        """Coordinate system axis constant.

        .. deprecated:: 0.4.8
           Use :attr:`AXIS` instead.

        Returns
        -------
        :class:`pyaedt.modeler.constants.AXIS`
            Coordinate system axis constants tuple (.X, .Y, .Z).

        """
        return CoordinateSystemAxis()

    @property
    def CoordinateSystemPlane(self):
        """Coordinate system plane constants.

        .. deprecated:: 0.4.8
           Use :attr:`PLANE` instead.

        Returns
        -------
        :class:`pyaedt.modeler.constants.PLANE`
            Coordinate system plane constants tuple (.XY, .YZ, .XZ).

        """
        return CoordinateSystemPlane()

    @property
    def View(self):
        """Planes.

        .. deprecated:: 0.4.8
           Use :attr:`VIEW` instead.

        Returns
        -------
        :class:`pyaedt.modeler.constants.PLANE`
            Coordinate system plane string tuple ("XY", "YZ", "XZ").

        """
        return Plane()

    @property
    def GravityDirection(self):
        """Gravity direction.

        .. deprecated:: 0.4.8
           Use :attr:`GRAVITY` instead.
        Returns
        -------
        tuple
            Gravity direction tuple (XNeg, YNeg, ZNeg, XPos, YPos, ZPos).

        """
        return GravityDirection()

    @property
    def modeler(self):
        """Modeler.

        Returns
        -------
        :class:`pyaedt.modeler.Modeler.Modeler`
            Modeler object.
        """
        return self._modeler

    @property
    def mesh(self):
        """Mesh.

        Returns
        -------
        :class:`pyaedt.modules.Mesh.Mesh`
            Mesh object.
        """
        return self._mesh

    @property
    def post(self):
        """PostProcessor.

        Returns
        -------
        :class:`pyaedt.modules.AdvancedPostProcessing.PostProcessor`
            PostProcessor object.
        """
        return self._post

    @property
    def analysis_setup(self):
        """Analysis setup.

        Returns
        -------
        str
            Name of the active or first analysis setup.

        References
        ----------

        >>> oModule.GetAllSolutionSetups()
        """
        if self._setup:
            return self._setup
        elif self.existing_analysis_setups:
            return self.existing_analysis_setups[0]
        else:
            self._setup = None
            return self._setup

    @analysis_setup.setter
    def analysis_setup(self, setup_name):
        setup_list = self.existing_analysis_setups
        if setup_list:
            assert setup_name in setup_list, "Invalid setup name {}".format(setup_name)
            self._setup = setup_name
        else:
            self._setup = setup_list[0]

    @property
    def existing_analysis_sweeps(self):
        """Existing analysis sweeps.

        Returns
        -------
        list of str
            List of all analysis sweeps in the design.

        References
        ----------

        >>> oModule.GelAllSolutionNames
        >>> oModule.GetSweeps
        """
        setup_list = self.existing_analysis_setups
        sweep_list = []
        if self.solution_type == "HFSS3DLayout" or self.solution_type == "HFSS 3D Layout Design":
            sweep_list = self.oanalysis.GetAllSolutionNames()
            sweep_list = [i for i in sweep_list if "Adaptive Pass" not in i]
            sweep_list.reverse()
        else:
            for el in setup_list:
                if self.solution_type == "HFSS3DLayout" or self.solution_type == "HFSS 3D Layout Design":
                    sweeps = self.oanalysis.GelAllSolutionNames()
                else:
                    setuptype = self.design_solutions.default_adaptive
                    if setuptype:
                        sweep_list.append(el + " : " + setuptype)
                    else:
                        sweep_list.append(el)
                try:
                    sweeps = list(self.oanalysis.GetSweeps(el))
                except:
                    sweeps = []
                for sw in sweeps:
                    if el + " : " + sw not in sweep_list:
                        sweep_list.append(el + " : " + sw)
        return sweep_list

    @property
    def nominal_adaptive(self):
        """Nominal adaptive sweep.

        Returns
        -------
        str
            Name of the nominal adaptive sweep.

        References
        ----------

        >>> oModule.GelAllSolutionNames
        >>> oModule.GetSweeps
        """
        if len(self.existing_analysis_sweeps) > 0:
            return self.existing_analysis_sweeps[0]
        else:
            return ""

    @property
    def nominal_sweep(self):
        """Nominal sweep.

        Returns
        -------
        str
            Name of the last adaptive sweep if a sweep is available or
            the name of the nominal adaptive sweep if present.

        References
        ----------

        >>> oModule.GelAllSolutionNames
        >>> oModule.GetSweeps
        """

        if len(self.existing_analysis_sweeps) > 1:
            return self.existing_analysis_sweeps[1]
        else:
            return self.nominal_adaptive

    @property
    def existing_analysis_setups(self):
        """Existing analysis setups.

        Returns
        -------
        list of str
            List of all analysis setups in the design.

        References
        ----------

        >>> oModule.GetSetups
        """
        setups = list(self.oanalysis.GetSetups())
        return setups

    @property
    def setup_names(self):
        """Setup names.

        Returns
        -------
        list of str
            List of names of all analysis setups in the design.

        References
        ----------

        >>> oModule.GetSetups
        """
        return self.oanalysis.GetSetups()

    @property
    def SimulationSetupTypes(self):
        """Simulation setup types.

        Returns
        -------
        SETUPS
            List of all simulation setup types categorized by application.
        """
        return SETUPS()

    @property
    def SolutionTypes(self):
        """Solution types.

        Returns
        -------
        SOLUTIONS
            List of all solution type categorized by application.
        """
        return SOLUTIONS()

    @property
    def excitations(self):
        """Get all excitation names.

        Returns
        -------
        list
            List of excitation names. Excitations with multiple modes will return one
            excitation for each mode.

        References
        ----------

        >>> oModule.GetExcitations
        """
        try:
            list_names = list(self.oboundary.GetExcitations())
            del list_names[1::2]
            return list_names
        except:
            return []

    @pyaedt_function_handler()
    def get_excitations_name(self):
        """Get all excitation names.

        .. deprecated:: 0.4.27
           Use :func:`excitations` property instead.

        Returns
        -------
        list
            List of excitation names. Excitations with multiple modes will return one
            excitation for each mode.

        References
        ----------

        >>> oModule.GetExcitations
        """
        warnings.warn("`get_excitations_name` is deprecated. Use `excitations` property instead.", DeprecationWarning)
        return self.excitations

    @pyaedt_function_handler()
    def get_traces_for_plot(
        self,
        get_self_terms=True,
        get_mutual_terms=True,
        first_element_filter=None,
        second_element_filter=None,
        category="dB(S",
    ):
        """Retrieve a list of traces of specified designs ready to use in plot reports.

        Parameters
        ----------
        get_self_terms : bool, optional
            Whether to return self terms. The default is ``True``.
        get_mutual_terms : bool, optional
            Whether to return mutual terms. The default is ``True``.
        first_element_filter : str, optional
            Filter to apply to the first element of the equation. This parameter accepts ``*``
            and ``?`` as special characters. The default is ``None``.
        second_element_filter : str, optional
            Filter to apply to the second element of the equation. This parameter accepts ``*``
            and ``?`` as special characters. The default is ``None``.
        category : str
            Plot category name as in the report (including operator). The default is ``"dB(S"`,
            which is the plot category name for capacitance.

        Returns
        -------
        list
            List of traces of specified designs ready to use in plot reports.

        Examples
        --------
        >>> from pyaedt import Q3d
        >>> hfss = hfss(project_path)
        >>> hfss.get_traces_for_plot(first_element_filter="Bo?1",
        ...                           second_element_filter="GND*", category="dB(S")
        """
        if not first_element_filter:
            first_element_filter = "*"
        if not second_element_filter:
            second_element_filter = "*"
        list_output = []
        end_str = ")" * (category.count("(") + 1)
        if get_self_terms:
            for el in self.excitations:
                value = "{}({},{}{}".format(category, el, el, end_str)
                if filter_tuple(value, first_element_filter, second_element_filter):
                    list_output.append(value)
        if get_mutual_terms:
            for el1 in self.excitations:
                for el2 in self.excitations:
                    if el1 != el2:
                        value = "{}({},{}{}".format(category, el1, el2, end_str)
                        if filter_tuple(value, first_element_filter, second_element_filter):
                            list_output.append(value)
        return list_output

    @pyaedt_function_handler()
    def analyze_all(self):
        """Analyze all setups in a design.

        Returns
        -------
        bool
            ``True`` when simulation is finished.
        """
        self.odesign.AnalyzeAll()
        return True

    @pyaedt_function_handler()
    def list_of_variations(self, setup_name=None, sweep_name=None):
        """Retrieve a list of active variations for input setup.

        Parameters
        ----------
        setup_name : str, optional
            Setup name. The default is ``None``, in which case the nominal adaptive
            is used.
        sweep_name : str, optional
            Sweep name. The default is``None``, in which case the nominal adaptive
            is used.

        Returns
        -------
        list
            List of active variations for input setup.

        References
        ----------

        >>> oModule.ListVariations
        """

        if not setup_name and ":" in self.nominal_sweep:
            setup_name = self.nominal_adaptive.split(":")[0].strip()
        elif not setup_name:
            self.logger.warning("No Setup defined.")
            return False
        if not sweep_name and ":" in self.nominal_sweep:
            sweep_name = self.nominal_adaptive.split(":")[1].strip()
        elif not sweep_name:
            self.logger.warning("No Sweep defined.")
            return False
        if self.solution_type == "HFSS3DLayout" or self.solution_type == "HFSS 3D Layout Design":
            try:
                return list(self.osolution.ListVariations("{0} : {1}".format(setup_name, sweep_name)))
            except:
                return [""]
        else:
            try:
                return list(self.odesign.ListVariations("{0} : {1}".format(setup_name, sweep_name)))
            except:
                return [""]

    @pyaedt_function_handler()
    def export_results(self, analyze=False, export_folder=None):
        """Export all available reports to a file, including sNp, profile, and convergence.

        Parameters
        ----------
        analyze : bool
            Whether to analyze before export. Solutions must be present for the design.
        export_folder : str, optional
            Full path to the project folder. The default is ``None``, in which case the
            working directory is used.

        Returns
        -------
        list
            List of all exported files.

        References
        ----------

        >>> oModule.GetAllPortsList
        >>> oDesign.ExportProfile
        >>> oModule.ExportToFile
        >>> oModule.ExportConvergence
        >>> oModule.ExportNetworkData
        """
        exported_files = []
        if not export_folder:
            export_folder = self.working_directory
        if analyze:
            self.analyze_all()
        setups = self.oanalysis.GetSetups()
        if self.solution_type == "HFSS3DLayout" or self.solution_type == "HFSS 3D Layout Design":
            excitations = len(self.oexcitation.GetAllPortsList())
        elif self.design_type == "2D Extractor":
            excitations = self.oboundary.GetNumExcitations("SignalLine")
        else:
            excitations = self.oboundary.GetNumExcitations()
        reportnames = self.post.oreportsetup.GetAllReportNames()
        for report_name in reportnames:
            name_no_space = report_name.replace(" ", "_")
            self.post.oreportsetup.UpdateReports([str(report_name)])
            export_path = os.path.join(
                export_folder, "{0}_{1}_{2}.csv".format(self.project_name, self.design_name, name_no_space)
            )
            self.post.oreportsetup.ExportToFile(str(report_name), export_path)
            self.logger.info("Export Data: {}".format(export_path))
            exported_files.append(export_path)

        for s in setups:
            sweeps = self.oanalysis.GetSweeps(s)
            if len(sweeps) == 0:
                sweeps = ["LastAdaptive"]
            else:
                pass
            for sweep in sweeps:
                variation_array = self.list_of_variations(s, sweep)
                if len(variation_array) == 1:
                    export_path = os.path.join(export_folder, "{}.prof".format(self.project_name))
                    result = self.export_profile(s, variation_array[0], export_path)
                    if result:
                        exported_files.append(export_path)
                    export_path = os.path.join(export_folder, "{}.conv".format(self.project_name))
                    result = self.export_convergence(s, variation_array[0], export_path)
                    if result:
                        exported_files.append(export_path)
                    if self.solution_type in ["HFSS3DLayout", "HFSS 3D Layout Design", "HFSS", "Circuit"]:
                        try:
                            export_path = os.path.join(
                                export_folder, "{0}.s{1}p".format(self.project_name, excitations)
                            )
                            self.osolution.ExportNetworkData(
                                variation_array[0],
                                ["{0}:{1}".format(s, sweep)],
                                3,
                                export_path,
                                ["All"],
                                True,
                                50,
                                "S",
                                -1,
                                0,
                                15,
                                True,
                                False,
                                False,
                            )
                            exported_files.append(export_path)
                            self.logger.info("Exported Touchstone: %s", export_path)
                        except:
                            self.logger.warning("Export SnP failed: no solutions found")

                else:
                    varCount = 0
                    for variation in variation_array:
                        varCount += 1
                        export_path = os.path.join(export_folder, "{0}_{1}.prof".format(self.project_name, varCount))
                        result = self.export_profile(s, variation, export_path)
                        if result:
                            exported_files.append(export_path)
                        export_path = os.path.join(export_folder, "{0}_{1}.conv".format(self.project_name, varCount))
                        self.logger.info("Export Convergence: %s", export_path)
                        result = self.export_convergence(s, variation, export_path)
                        if result:
                            exported_files.append(export_path)
                        if self.solution_type in ["HFSS3DLayout", "HFSS 3D Layout Design", "HFSS", "Circuit"]:
                            try:
                                export_path = os.path.join(
                                    export_folder, "{0}_{1}.s{2}p".format(self.project_name, varCount, excitations)
                                )
                                self.logger.info("Export SnP: {}".format(export_path))
                                self.osolution.ExportNetworkData(
                                    variation,
                                    ["{0}:{1}".format(s, sweep)],
                                    3,
                                    export_path,
                                    ["All"],
                                    True,
                                    50,
                                    "S",
                                    -1,
                                    0,
                                    15,
                                    True,
                                    False,
                                    False,
                                )
                                exported_files.append(export_path)
                                self.logger.info("Exported Touchstone: %s", export_path)
                            except:
                                self.logger.warning("Export SnP failed: no solutions found")
        return exported_files

    @pyaedt_function_handler()
    def export_convergence(self, setup_name, variation_string="", file_path=None):
        """Export a solution convergence to a file.

        Parameters
        ----------
        setup_name : str
            Setup name. For example, ``'Setup1'``.
        variation_string : str
            Variation string with values. For example, ``'radius=3mm'``.
        file_path : str, optional
            Full path to the PROF file. The default is ``None``, in which
            case the working directory is used.


        Returns
        -------
        str
            File path if created.

        References
        ----------

        >>> oModule.ExportConvergence
        """
        if not file_path:
            file_path = os.path.join(self.working_directory, generate_unique_name("Convergence") + ".prop")
        self.odesign.ExportConvergence(setup_name, variation_string, file_path)
        self.logger.info("Export Convergence to  %s", file_path)
        return file_path

    @pyaedt_function_handler()
    def _get_native_data(self):
        """Retrieve Native Components data."""
        boundaries = []
        try:
            data_vals = self.design_properties["ModelSetup"]["GeometryCore"]["GeometryOperations"][
                "SubModelDefinitions"
            ]["NativeComponentDefinition"]
            if not isinstance(data_vals, list) and isinstance(data_vals, (OrderedDict, dict)):
                boundaries.append(
                    NativeComponentObject(
                        self,
                        data_vals["NativeComponentDefinitionProvider"]["Type"],
                        data_vals["BasicComponentInfo"]["ComponentName"],
                        data_vals,
                    )
                )
            for ds in data_vals:
                try:
                    if isinstance(ds, (OrderedDict, dict)):
                        boundaries.append(
                            NativeComponentObject(
                                self,
                                ds["NativeComponentDefinitionProvider"]["Type"],
                                ds["BasicComponentInfo"]["ComponentName"],
                                ds,
                            )
                        )
                except:
                    pass
        except:
            pass
        return boundaries

    class AvailableVariations(object):
        def __init__(self, app):
            """Contains available variations.

            Parameters
            ----------
            app :
                Inherited parent object.

            Returns
            -------
            object
                Parent object.

            """
            self._app = app

        @property
        def variables(self):
            """Variables.

            Returns
            -------
            list of str
                List of names of independent variables.
            """
            return [i for i in self._app.variable_manager.independent_variables]

        @pyaedt_function_handler()
        def variations(self, setup_sweep=None):
            """Variations.

            Parameters
            ----------
            setup_sweep : str, optional
                Setup name with the sweep to search for variations on. The default is ``None``.

            Returns
            -------
            list of lists
                List of variation families.

            References
            ----------

            >>> oModule.GetAvailableVariations
            """
            if not setup_sweep:
                setup_sweep = self._app.existing_analysis_sweeps[0]
            vs = self._app.osolution.GetAvailableVariations(setup_sweep)
            families = []
            for v in vs:
                variations = v.split(" ")
                family = []
                for el in self.variables:
                    family.append(el + ":=")
                    i = 0
                    while i < len(variations):
                        if variations[i][0 : len(el)] == el:
                            family.append([variations[i][len(el) + 2 : -1]])
                        i += 1
                families.append(family)
            return families

        @pyaedt_function_handler()
        def get_variation_strings(self, setup_sweep=None):
            """Return variation strings.

            Parameters
            ----------
            setup_sweep : str, optional
                Setup name with the sweep to search for variations on. The default is ``None``.

            Returns
            -------
            list of str
                List of variation families.

            References
            ----------

            >>> oModule.GetAvailableVariations
            """
            if not setup_sweep:
                setup_sweep = self._app.existing_analysis_sweeps[0]
            return self._app.osolution.GetAvailableVariations(setup_sweep)

        @property
        def nominal(self):
            """Nominal."""
            families = []
            for el in self.variables:
                families.append(el + ":=")
                families.append(["Nominal"])
            return families

        @property
        def nominal_w_values(self):
            """Nominal with values.

            References
            ----------

            >>> oDesign.GetChildObject('Variables').GetChildNames
            >>> oDesign.GetVariables
            >>> oDesign.GetVariableValue
            >>> oDesign.GetNominalVariation"""
            families = []
            if self._app.design_type == "HFSS 3D Layout Design":
                if self._app._is_object_oriented_enabled():
                    listvar = list(self._app._odesign.GetChildObject("Variables").GetChildNames())
                else:
                    listvar = list(self._app._odesign.GetVariables())
                for el in listvar:
                    families.append(el + ":=")
                    families.append([self._app._odesign.GetVariableValue(el)])
            else:
                variation = self._app._odesign.GetNominalVariation()
                for el in self.variables:
                    families.append(el + ":=")
                    families.append([self._app._odesign.GetVariationVariableValue(variation, el)])
            return families

        @property
        def nominal_w_values_dict(self):
            """Nominal with values in a dictionary.

            References
            ----------

            >>> oDesign.GetChildObject('Variables').GetChildNames
            >>> oDesign.GetVariables
            >>> oDesign.GetVariableValue
            >>> oDesign.GetNominalVariation"""
            families = {}
            if self._app.design_type in ["HFSS 3D Layout Design", "Circuit Design", "Twin Builder"]:
                if self._app._is_object_oriented_enabled():
                    listvar = list(self._app._odesign.GetChildObject("Variables").GetChildNames())
                else:
                    listvar = list(self._app._odesign.GetVariables())
                for el in listvar:
                    families[el] = self._app._odesign.GetVariableValue(el)
            else:
                variation = self._app._odesign.GetNominalVariation()
                for el in self.variables:
                    families[el] = self._app._odesign.GetVariationVariableValue(variation, el)
            return families

        @property
        def all(self):
            """All."""
            families = []
            for el in self.variables:
                families.append(el + ":=")
                families.append(["All"])
            return families

    class AxisDir(object):
        """Contains constants for the axis directions."""

        (XNeg, YNeg, ZNeg, XPos, YPos, ZPos) = range(0, 6)

    @pyaedt_function_handler()
    def get_setups(self):
        """Retrieve setups.

        Returns
        -------
        list of str
            List of names of all setups.

        References
        ----------

        >>> oModule.GetSetups
        """
        setups = self.oanalysis.GetSetups()
        return list(setups)

    @pyaedt_function_handler()
    def get_nominal_variation(self):
        """Retrieve the nominal variation.

        Returns
        -------
        list of str
            List of nominal variations.
        """
        return self.available_variations.nominal

    @pyaedt_function_handler()
    def get_sweeps(self, name):
        """Retrieve all sweeps for a setup.

        Parameters
        ----------
        name : str
            Name of the setup.

        Returns
        -------
        list of str
            List of names of all sweeps for the setup.

        References
        ----------

        >>> oModule.GetSweeps
        """
        sweeps = self.oanalysis.GetSweeps(name)
        return list(sweeps)

    @pyaedt_function_handler()
    def export_parametric_results(self, sweepname, filename, exportunits=True):
        """Export a list of all parametric variations solved for a sweep to a CSV file.

        Parameters
        ----------
        sweepname : str
            Name of the optimetrics sweep.
        filename : str
            Full path and name for the CSV file.
        exportunits : bool, optional
            Whether to export units with the value. The default is ``True``. When ``False``,
            only the value is exported.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.

        References
        ----------

        >>> oModule.ExportParametricResults
        """

        self.ooptimetrics.ExportParametricResults(sweepname, filename, exportunits)
        return True

    @pyaedt_function_handler()
    def analyze_from_initial_mesh(self):
        """Revert the solution to the initial mesh and re-run the solve.

        Returns
        -------
        bool
           ``True`` when successful, ``False`` when failed.

        References
        ----------

        >>> oModule.RevertSetupToInitial
        >>> oDesign.Analyze
        """
        self.oanalysis.RevertSetupToInitial(self._setup)
        self.analyze_nominal()
        return True

    @pyaedt_function_handler()
    def analyse_nominal(self):
        """Solve the nominal design.

        .. deprecated:: 0.4.0
           Use :func:`Analysis.analyze_nominal` instead.
        """
        warnings.warn("`analyse_nominal` is deprecated. Use `analyze_nominal` instead.", DeprecationWarning)
        self.analyze_nominal()

    @pyaedt_function_handler()
    def analyze_nominal(self, num_cores=None, num_tasks=None, num_gpu=None, acf_file=None):
        """Solve the nominal design.

        Parameters
        ----------
        num_cores : int, optional
            Number of simulation cores.
        num_tasks : int, optional
            Number of simulation tasks.
        num_gpu : int, optional
            Number of simulation graphic processing units to use.
        acf_file : str, optional
            Full path to the custom ACF file.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.

        References
        ----------

        >>> oDesign.Analyze
        """

        return self.analyze_setup(self.analysis_setup, num_cores, num_tasks, num_gpu, acf_file)

    @pyaedt_function_handler()
    def generate_unique_setup_name(self, setup_name=None):
        """Generate a new setup with an unique name.

        Parameters
        ----------
        setup_name : str, optional
            Name of the setup. The default is ``None``.

        Returns
        -------
        str
            Name of the setup.

        """
        if not setup_name:
            setup_name = "Setup"
        index = 2
        while setup_name in self.existing_analysis_setups:
            setup_name = setup_name + "_{}".format(index)
            index += 1
        return setup_name

    @pyaedt_function_handler()
    def create_setup(self, setupname="MySetupAuto", setuptype=None, props=None):
        """Create a setup.

        Parameters
        ----------
        setupname : str, optional
            Name of the setup. The default is ``"MySetupAuto"``.
        setuptype : optional
            Type of the setup. The default is ``None``, in which case
            the default type is applied.
        props : dict, optional
            Dictionary of analysis properties appropriate for the design and analysis.
            If no values are passed, default values are used.

        Returns
        -------
        :class:`pyaedt.modules.SolveSetup.Setup`

        References
        ----------

        >>> oModule.InsertSetup

        Examples
        --------
        Create a setup for SBR+ setup using advanced Doppler
        processing for automotive radar.

        >>> import pyaedt
        >>> hfss = pyaedt.Hfss(solution_type='SBR+')
        >>> setup1 = hfss.create_setup(setupname='Setup1')
        >>> setup1.props["IsSbrRangeDoppler"] = True
        >>> setup1.props["SbrRangeDopplerTimeVariable"] = "time_var"
        >>> setup1.props["SbrRangeDopplerCenterFreq"] = "76.5GHz"
        >>> setup1.props["SbrRangeDopplerRangeResolution"] = "0.15meter"
        >>> setup1.props["SbrRangeDopplerRangePeriod"] = "100meter"
        >>> setup1.props["SbrRangeDopplerVelocityResolution"] = "0.2m_per_sec"
        >>> setup1.props["SbrRangeDopplerVelocityMin"] = "-30m_per_sec"
        >>> setup1.props["SbrRangeDopplerVelocityMax"] = "30m_per_sec"
        >>> setup1.props["DopplerRayDensityPerWavelength"] = "0.2"
        >>> setup1.props["MaxNumberOfBounces"] = "3"
        >>> setup1.update()
        ...
        pyaedt info: Sweep was created correctly.
        """
        if props == None:
            props = {}

        if setuptype is None:
            setuptype = self.design_solutions.default_setup
        name = self.generate_unique_setup_name(setupname)
        setup = Setup(self, setuptype, name)
        if self.design_type == "HFSS" and not self.excitations and "MaxDeltaS" in setup.props:
            new_dict = OrderedDict()
            for k, v in setup.props.items():
                if k == "MaxDeltaS":
                    new_dict["MaxDeltaE"] = 0.01
                else:
                    new_dict[k] = v

            setup.props = new_dict
        setup.create()
        if props:
            for el in props:
                setup.props[el] = props[el]
            setup.update()

        self.analysis_setup = name
        self.setups.append(setup)
        return setup

    @pyaedt_function_handler()
    def delete_setup(self, setupname):
        """Delete a setup.

        Parameters
        ----------
        setupname : str
            Name of the setup.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.

        References
        ----------

        >>> oModule.DeleteSetups

        Examples
        --------
        Create a setup and then delete it.

        >>> import pyaedt
        >>> hfss = pyaedt.Hfss()
        >>> setup1 = hfss.create_setup(setupname='Setup1')
        >>> hfss.delete_setup(setupname='Setup1')
        ...
        pyaedt info: Sweep was deleted correctly.
        """
        if setupname in self.existing_analysis_setups:
            self.oanalysis.DeleteSetups([setupname])
            for s in self.setups:
                if s.name == setupname:
                    self.setups.remove(s)
            return True
        return False

    @pyaedt_function_handler()
    def edit_setup(self, setupname, properties_dict):
        """Modify a setup.

        Parameters
        ----------
        setupname : str
            Name of the setup.
        properties_dict : dict
            Dictionary containing the property to update with the value.

        Returns
        -------
        :class:`pyaedt.modules.SolveSetup.Setup`

        References
        ----------

        >>> oModule.EditSetup
        """

        setuptype = self.design_solutions.default_setup
        setup = Setup(self, setuptype, setupname, isnewsetup=False)
        setup.update(properties_dict)
        self.analysis_setup = setupname
        return setup

    @pyaedt_function_handler()
    def get_setup(self, setupname):
        """Get the setup from the current design.

        Parameters
        ----------
        setupname : str
            Name of the setup.

        Returns
        -------
        :class:`pyaedt.modules.SolveSetup.Setup`

        """

        setuptype = self.design_solutions.default_setup
        setup = Setup(self, setuptype, setupname, isnewsetup=False)
        if setup.props:
            self.analysis_setup = setupname
        return setup

    @pyaedt_function_handler()
    def create_output_variable(self, variable, expression):
        """Create or modify an output variable.


        Parameters
        ----------
        variable : str
            Name of the variable.
        expression :
            Value for the variable.

        Returns
        -------
        bool
           ``True`` when successful, ``False`` when failed.

        References
        ----------

        >>> oModule.CreateOutputVariable
        """
        oModule = self.ooutput_variable
        if variable in self.output_variables:
            oModule.EditOutputVariable(
                variable, expression, variable, self.existing_analysis_sweeps[0], self.solution_type, []
            )
        else:
            oModule.CreateOutputVariable(variable, expression, self.existing_analysis_sweeps[0], self.solution_type, [])
        return True

    @pyaedt_function_handler()
    def get_output_variable(self, variable):
        """Retrieve the value of the output variable.

        Parameters
        ----------
        variable : str
            Name of the variable.

        Returns
        -------
        type
            Value of the output variable.

        References
        ----------

        >>> oDesign.GetNominalVariation
        >>> oModule.GetOutputVariableValue
        """
        assert variable in self.output_variables, "Output variable {} does not exist.".format(variable)
        nominal_variation = self.odesign.GetNominalVariation()
        value = self.ooutput_variable.GetOutputVariableValue(
            variable, nominal_variation, self.existing_analysis_sweeps[0], self.solution_type, []
        )

        return value

    @pyaedt_function_handler()
    def get_object_material_properties(self, object_list=None, prop_names=None):
        """Retrieve the material properties for a list of objects and return them in a dictionary.

        This high-level function ignores objects with no defined material properties.

        Parameters
        ----------
        object_list : list, optional
            List of objects to get material properties for. The default is ``None``,
            in which case material properties are retrieved for all objects.
        prop_names : str or list
            Property or list of properties to export. The default is ``None``, in
            which case all properties are exported.

        Returns
        -------
        dict
            Dictionary of objects with material properties.
        """
        if object_list:
            if not isinstance(object_list, list):
                object_list = [object_list]
        else:
            object_list = self.modeler.object_names

        if prop_names:
            if not isinstance(prop_names, list):
                prop_names = [prop_names]

        dict = {}
        for entry in object_list:
            mat_name = self.modeler[entry].material_name
            mat_props = self._materials[mat_name]
            if prop_names is None:
                dict[entry] = mat_props._props
            else:
                dict[entry] = {}
                for prop_name in prop_names:
                    dict[entry][prop_name] = mat_props._props[prop_name]
        return dict

    @pyaedt_function_handler()
    def analyze_setup(self, name, num_cores=None, num_tasks=None, num_gpu=None, acf_file=None):
        """Analyze a design setup.

        Parameters
        ----------
        name : str
            Name of the setup, which can be an optimetric setup or a simple setup.
        num_cores : int, optional
            Number of simulation cores. The default is ``None.``
        num_tasks : int, optional
            Number of simulation tasks. The default is ``None.``
        num_gpu : int, optional
            Number of simulation graphics processing units. The default is ``None.``
        acf_file : str, optional
            Full path to custom ACF file. The default is ``None.``

        Returns
        -------
        bool
           ``True`` when successful, ``False`` when failed.

        References
        ----------

        >>> oDesign.Analyze
        """
        set_custom_dso = False
        active_config = self._desktop.GetRegistryString(r"Desktop/ActiveDSOConfigurations/" + self.design_type)
        if acf_file:
            self._desktop.SetRegistryFromFile(acf_file)
            name = ""
            with open(acf_file, "r") as f:
                lines = f.readlines()
                for line in lines:
                    if "ConfigName" in line:
                        name = line.strip().split("=")[1]
                        break
            if name:
                try:
                    self.set_registry_key(r"Desktop/ActiveDSOConfigurations/" + self.design_type, name)
                    set_custom_dso = True
                except:
                    pass
        elif num_gpu or num_tasks or num_cores:
            config_name = "pyaedt_config"
            source_name = os.path.join(self.pyaedt_dir, "misc", "pyaedt_local_config.acf")
            target_name = os.path.join(self.working_directory, config_name + ".acf")
            shutil.copy2(source_name, target_name)
            if num_cores:
                update_hpc_option(target_name, "NumCores", num_cores, False)
            if num_gpu:
                update_hpc_option(target_name, "NumGPUs", num_gpu, False)
            if num_tasks:
                update_hpc_option(target_name, "NumEngines", num_tasks, False)
            update_hpc_option(target_name, "ConfigName", config_name, True)
            update_hpc_option(target_name, "DesignType", self.design_type, True)
            if self.design_type == "Icepak":
                update_hpc_option(target_name, "UseAutoSettings", self.design_type, False)
            try:
                self._desktop.SetRegistryFromFile(target_name)
                self.set_registry_key(r"Desktop/ActiveDSOConfigurations/" + self.design_type, config_name)
                set_custom_dso = True
            except:
                pass

        if name in self.existing_analysis_setups:
            try:
                self.logger.info("Solving design setup %s", name)
                self.odesign.Analyze(name)
            except:
                if set_custom_dso:
                    self.set_registry_key(r"Desktop/ActiveDSOConfigurations/" + self.design_type, active_config)
                self.logger.error("Error in Solving Setup %s", name)
                return False
        else:
            try:
                self.logger.info("Solving Optimetrics")
                self.ooptimetrics.SolveSetup(name)
            except:
                if set_custom_dso:
                    self.set_registry_key(r"Desktop/ActiveDSOConfigurations/" + self.design_type, active_config)
                self.logger.error("Error in Solving or Missing Setup  %s", name)
                return False
        if set_custom_dso:
            self.set_registry_key(r"Desktop/ActiveDSOConfigurations/" + self.design_type, active_config)
        self.logger.info("Design setup %s solved correctly", name)
        return True

    @pyaedt_function_handler()
    def solve_in_batch(self, filename=None, machine="local", run_in_thread=False):
        """Analyze a design setup in batch mode.

        .. note::
           To use this function, the project must be closed.

        Parameters
        ----------
        filename : str, optional
            Name of the setup. The default is ``None``, which means that the active project
            is to be solved.
        machine : str, optional
            Name of the machine if remote.  The default is ``"local"``.
        run_in_thread : bool, optional
            Whether to submit the batch command as a thread. The default is
            ``False``.

        Returns
        -------
         bool
           ``True`` when successful, ``False`` when failed.
        """
        if not filename:
            filename = self.project_file
            self.close_project()
        if machine == "local":
            # -Monitor option used as workaround for R2 BatchSolve not exiting properly at the end of the Batch job
            options = " -ng -BatchSolve -Monitor "
        else:
            options = " -ng -distribute -machinelist list=" + machine + " -Batchsolve "

        self.logger.info("Batch Solve Options: " + options)
        if os.name == "posix":
            batch_run = os.path.join(
                self.desktop_install_dir + "/ansysedt" + chr(34) + options + chr(34) + filename + chr(34)
            )
        else:
            batch_run = (
                chr(34) + self.desktop_install_dir + "/ansysedt.exe" + chr(34) + options + chr(34) + filename + chr(34)
            )

        """
        check for existing solution directory and delete if present so we
        dont have old .asol files etc
        """

        self.logger.info("Solving model in batch mode on " + machine)
        self.logger.info("Batch Job command:" + batch_run)
        if run_in_thread:

            def thread_run():
                """ """
                os.system(batch_run)

            x = threading.Thread(target=thread_run)
            x.start()
        else:
            os.system(batch_run)
        self.logger.info("Batch job finished.")
        return True

    @pyaedt_function_handler()
    def submit_job(
        self, clustername, aedt_full_exe_path=None, numnodes=1, numcores=32, wait_for_license=True, setting_file=None
    ):
        """Submit a job to be solved on a cluster.

        Parameters
        ----------
        clustername : str
            Name of the cluster to submit the job to.
        aedt_full_exe_path : str, optional
            Full path to the AEDT executable file. The default is ``None``, in which
            case ``"/clustername/AnsysEM/AnsysEM2x.x/Win64/ansysedt.exe"`` is used.
        numnodes : int, optional
            Number of nodes. The default is ``1``.
        numcores : int, optional
            Number of cores. The default is ``32``.
        wait_for_license : bool, optional
             Whether to wait for the license to be validated. The default is ``True``.
        setting_file : str, optional
            Name of the file to use as a template. The default value is ``None``.

        Returns
        -------
        type
            ID of the job.

        References
        ----------

        >>> oDesktop.SubmitJob
        """
        project_file = self.project_file
        project_path = self.project_path
        if not aedt_full_exe_path:
            version = self.odesktop.GetVersion()[2:6]
            if os.path.exists(r"\\" + clustername + r"\AnsysEM\AnsysEM{}\Win64\ansysedt.exe".format(version)):
                aedt_full_exe_path = (
                    r"\\\\\\\\" + clustername + r"\\\\AnsysEM\\\\AnsysEM{}\\\\Win64\\\\ansysedt.exe".format(version)
                )
            elif os.path.exists(r"\\" + clustername + r"\AnsysEM\AnsysEM{}\Linux64\ansysedt".format(version)):
                aedt_full_exe_path = (
                    r"\\\\\\\\" + clustername + r"\\\\AnsysEM\\\\AnsysEM{}\\\\Linux64\\\\ansysedt".format(version)
                )
            else:
                self.logger.error("AEDT path does not exist. Please provide a full path.")
                return False
        else:
            if not os.path.exists(aedt_full_exe_path):
                self.logger.error("Aedt Path doesn't exists. Please provide a full path")
                return False
            aedt_full_exe_path.replace("\\", "\\\\")

        self.close_project()
        path_file = os.path.dirname(__file__)
        destination_reg = os.path.join(project_path, "Job_settings.areg")
        if not setting_file:
            setting_file = os.path.join(path_file, "..", "misc", "Job_Settings.areg")
        shutil.copy(setting_file, destination_reg)

        f1 = open(destination_reg, "w")
        with open(setting_file) as f:
            lines = f.readlines()
            for line in lines:
                if "\\	$begin" == line[:8]:
                    lin = "\\	$begin \\'{}\\'\\\n".format(clustername)
                    f1.write(lin)
                elif "\\	$end" == line[:6]:
                    lin = "\\	$end \\'{}\\'\\\n".format(clustername)
                    f1.write(lin)
                elif "NumCores" in line:
                    lin = "\\	\\	\\	\\	NumCores={}\\\n".format(numcores)
                    f1.write(lin)
                elif "NumNodes=1" in line:
                    lin = "\\	\\	\\	\\	NumNodes={}\\\n".format(numnodes)
                    f1.write(lin)
                elif "ProductPath" in line:
                    lin = "\\	\\	ProductPath =\\'{}\\'\\\n".format(aedt_full_exe_path)
                    f1.write(lin)
                elif "WaitForLicense" in line:
                    lin = "\\	\\	WaitForLicense={}\\\n".format(str(wait_for_license).lower())
                    f1.write(lin)
                else:
                    f1.write(line)
        f1.close()
        return self.odesktop.SubmitJob(os.path.join(project_path, "Job_settings.areg"), project_file)
