"""This module contains these classes: `Hfss` and 'BoundaryType`."""
from __future__ import absolute_import
import os
import warnings
from .application.Analysis3D import FieldAnalysis3D
from .desktop import exception_to_desktop
from .modeler.GeometryOperators import GeometryOperators
from .modules.Boundary import BoundaryObject, NativeComponentObject
from .generic.general_methods import generate_unique_name, aedt_exception_handler
from collections import OrderedDict
from .application.DataHandlers import random_string


class Hfss(FieldAnalysis3D, object):
    """Provides the HFSS application interface.

    This class allows you to create an interactive instance of HfSS and
    connect to an existing HFSS design or create a new HFSS design if
    one does not exist.

    Parameters
    ----------
    projectname : str, optional
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
    specified_version: str, optional
        Version of AEDT to use. The default is ``None``, in which case
        the active version or latest installed version is used. This parameter is ignored when Script is launched within AEDT.
    NG : bool, optional
        Whether to run AEDT in the non-graphical mode. The default
        is ``False``, in which case AEDT is launched in the graphical mode. This parameter is ignored when Script is launched within AEDT.
    AlwaysNew : bool, optional
        Whether to launch an instance of AEDT in a new thread, even if
        another instance of the ``specified_version`` is active on the
        machine. The default is ``True``. This parameter is ignored when Script is launched within AEDT.
    release_on_exit : bool, optional
        Whether to release AEDT on exit. The default is ``False``.
    student_version : bool, optional
        Whether to open the AEDT student version. The default is
        ``False``. This parameter is ignored when Script is launched within AEDT.

    Examples
    --------

    Create an instance of HFSS and connect to an existing HFSS
    design or create a new HFSS design if one does not exist.

    >>> from pyaedt import Hfss
    >>> hfss = Hfss()

    Create an instance of HFSS and link to a project named
    ``HfssProject``. If this project does not exist, create one with
    this name.

    >>> hfss = Hfss("HfssProject")
    pyaedt Info: Added design 'HFSS_...' of type HFSS.

    Create an instance of HFSS and link to a design named
    ``HfssDesign1`` in a project named ``HfssProject``.

    >>> hfss = Hfss("HfssProject","HfssDesign1")
    pyaedt Info: Added design 'HfssDesign1' of type HFSS.

    Create an instance of HFSS and open the specified project,
    which is named ``"myfile.aedt"``.

    >>> hfss = Hfss("myfile.aedt")
    pyaedt Info: Added design 'HFSS_...' of type HFSS.

    Create an instance of HFSS using the 2021 R1 release and open
    the specified project, which is named ``"myfile2.aedt"``.

    >>> hfss = Hfss(specified_version="2021.1", projectname="myfile2.aedt")
    pyaedt Info: Added design 'HFSS_...' of type HFSS.

    Create an instance of HFSS using the 2021 R2 student version and open
    the specified project, which is named ``"myfile3.aedt"``.

    >>> hfss = Hfss(specified_version="2021.2", projectname="myfile3.aedt", student_version=True)
    pyaedt Info: Added design 'HFSS_...' of type HFSS.

    """

    def __repr__(self):
        try:
            return "HFSS {} {}. ProjectName:{} DesignName:{} ".format(self._aedt_version, self.solution_type,
                                                                      self.project_name, self.design_name)
        except:
            return "HFSS Module"

    def __init__(self, projectname=None, designname=None, solution_type=None, setup_name=None,
                 specified_version=None, NG=False, AlwaysNew=False, release_on_exit=False, student_version=False):
        FieldAnalysis3D.__init__(self, "HFSS", projectname, designname, solution_type, setup_name,
                                 specified_version, NG, AlwaysNew, release_on_exit, student_version)

    def __enter__(self):
        return self

    def __exit__(self, ex_type, ex_value, ex_traceback):
        """ Push exit up to the parent object ``Design``. """
        if ex_type:
            exception_to_desktop(self, ex_value, ex_traceback)

    class BoundaryType(object):
        """Creates and manages boundaries.

        Parameters
        ----------
        PerfectE :
        PerfectH :
        Aperture :
        Radiation :
        Impedance :
        LayeredImp :
        LumpedRLC :
        FiniteCond :
        """
        (PerfectE, PerfectH, Aperture, Radiation, Impedance,
         LayeredImp, LumpedRLC, FiniteCond) = range(0, 8)

    @aedt_exception_handler
    def _create_boundary(self, name, props, boundary_type):
        """Create a boundary.

        Parameters
        ---------
        name : str
            Name of the boundary
        props : list
            List of properties for the boundary.
        boundary_type :
            Type of the boundary.

        Returns
        -------
        :class: `pyaedt.modules.Boundary.BoundaryObject`
            Boundary object.

        """

        bound = BoundaryObject(self, name, props, boundary_type)
        result = bound.create()
        if result:
            self.boundaries.append(bound)
            return bound
        return result

    @aedt_exception_handler
    def _create_lumped_driven(self, objectname, int_line_start, int_line_stop, impedance, portname, renorm, deemb):
        start = [str(i) + self.modeler.primitives.model_units for i in int_line_start]
        stop = [str(i) + self.modeler.primitives.model_units for i in int_line_stop]
        props = OrderedDict({"Objects": [objectname], "DoDeembed": deemb, "RenormalizeAllTerminals": renorm,
                             "Modes": OrderedDict({"Mode1": OrderedDict({"ModeNum": 1, "UseIntLine": True,
                                                                         "IntLine": OrderedDict(
                                                                             {"Start": start, "End": stop}),
                                                                         "AlignmentGroup": 0, "CharImp": "Zpi",
                                                                         "RenormImp": str(impedance) + "ohm"})}),
                             "ShowReporterFilter": False,
                             "ReporterFilter": [True],
                             "Impedance": str(impedance) + "ohm"})
        return self._create_boundary(portname, props, "LumpedPort")

    @aedt_exception_handler
    def _create_port_terminal(self, objectname, int_line_stop, portname, iswaveport=False):
        ref_conductors = self.modeler.convert_to_selections(int_line_stop, False)
        props = OrderedDict({})
        props["Faces"] = int(objectname)
        props["IsWavePort"] = iswaveport
        props["ReferenceConductors"] = ref_conductors
        props["RenormalizeModes"] = True
        return self._create_boundary(portname, props, "AutoIdentify")

    @aedt_exception_handler
    def _create_circuit_port(self, edgelist, impedance, name, renorm, deemb, renorm_impedance=""):
        edgelist = self.modeler._convert_list_to_ids(edgelist, False)
        props = OrderedDict({"Edges": edgelist, "Impedance": str(impedance) + "ohm", "DoDeembed": deemb,
                             "RenormalizeAllTerminals": renorm})

        if self.solution_type == "DrivenModal":

            if renorm:
                if type(renorm_impedance) is int or type(renorm_impedance) is float or 'i' not in renorm_impedance:
                    renorm_imp = str(renorm_impedance) + 'ohm'
                else:
                    renorm_imp = '(' + renorm_impedance + ') ohm'
            else:
                renorm_imp = '0ohm'
            props["RenormImp"] = renorm_imp
        else:
            props["TerminalIDList"] = []
        return self._create_boundary(name, props, "CircuitPort")

    @aedt_exception_handler
    def _create_waveport_driven(self, objectname, int_line_start=None, int_line_stop=None, impedance=50, portname="",
                                renorm=True, nummodes=1, deemb_distance=0):
        start = None
        stop = None
        if int_line_start and int_line_stop:
            start = [str(i) + self.modeler.primitives.model_units for i in int_line_start]
            stop = [str(i) + self.modeler.primitives.model_units for i in int_line_stop]
            useintline = True
        else:
            useintline = False

        props = OrderedDict({})
        props["Objects"] = [objectname]
        props["NumModes"] = nummodes
        props["UseLineModeAlignment"] = False

        if deemb_distance != 0:
            props["DoDeembed"] = True
            props["DeembedDist"] = str(deemb_distance) + self.modeler.model_units

        else:
            props["DoDeembed"] = False
        props["RenormalizeAllTerminals"] = renorm
        modes = OrderedDict({})
        arg2 = []
        arg2.append("NAME:Modes")
        i = 1
        report_filter = []
        while i <= nummodes:
            if i == 1:
                mode = OrderedDict({})
                mode["ModeNum"] = i
                mode["UseIntLine"] = useintline
                if useintline:
                    mode["IntLine"] = OrderedDict({"Start": start, "End": stop})
                mode["AlignmentGroup"] = 0
                mode["CharImp"] = "Zpi"
                mode["RenormImp"] = str(impedance) + "ohm"
                modes["Mode1"] = mode
            else:
                mode = OrderedDict({})

                mode["ModeNum"] = i
                mode["UseIntLine"] = False
                mode["AlignmentGroup"] = 0
                mode["CharImp"] = "Zpi"
                mode["RenormImp"] = str(impedance) + "ohm"
                modes["Mode" + str(i)] = mode
            report_filter.append(True)
            i += 1
        props["Modes"] = modes
        props["ShowReporterFilter"] = False
        props["ReporterFilter"] = report_filter
        props["UseAnalyticAlignment"] = False
        return self._create_boundary(portname, props, "WavePort")

    @aedt_exception_handler
    def assigncoating(self, obj, mat=None,
                      cond=58000000, perm=1, usethickness=False, thickness="0.1mm", roughness="0um",
                      isinfgnd=False, istwoside=False, isInternal=True, issheelElement=False, usehuray=False,
                      radius="0.5um", ratio="2.9"):
        """Assign finite conductivity to one or more objects of a given material.

        Parameters
        ----------
        obj : str or list
            One or more objects to assign finite conductivity to.
        mat : str, optional
            Material to use. The default is ``None``.
        cond : float, optional
            If no material is provided, a conductivity value must be supplied. The default is ``58000000``.
        perm : float, optional
            If no material is provided, a permittivity value must be supplied. The default is ``1``.
        usethickness : bool, optional
            Whether to use thickness. The default is ``False``.
        thickness : str, optional
            Thickness value if ``usethickness=True``. The default is ``"0.1mm"``.
        roughness : str, optional
            Roughness value  with units. The default is ``"0um"``.
        isinfgnd : bool, optional
            Whether the finite conductivity is an infinite ground. The default is ``False``.
        istwoside : bool, optional
            The default is ``False``.
        isInternal : bool, optional
            The default is ``True``.
        issheelElement : bool, optional
            The default is ``False``.
        usehuray : bool, optional
            Whether to use an Huray coefficient. The default is ``False``.
        radius : str, optional
            Radius value if ``usehuray=True``. The default is ``"0.5um"``.
        ratio : str, optional
            Ratio value if ``usehuray=True``. The default is ``"2.9"``.

        Returns
        -------
        :class: `pyaedt.modules.Boundary.BoundaryObject`
            Boundary object.

        Examples
        --------

        Create a cylinder at the XY working plane and assign a copper coating of 0.2 mm to it.

        >>> origin = hfss.modeler.Position(0, 0, 0)
        >>> inner = hfss.modeler.primitives.create_cylinder(hfss.CoordinateSystemPlane.XYPlane, origin, 3, 200, 0, "inner")
        >>> inner_id = hfss.modeler.primitives.get_obj_id("inner")
        >>> coat = hfss.assigncoating([inner_id], "copper", usethickness=True, thickness="0.2mm")

        """

        listobj = self.modeler.convert_to_selections(obj, True)
        listobjname = "_".join(listobj)
        props = {"Objects": listobj}
        if mat:
            mat = mat.lower()
            if mat in self.materials.material_keys:
                Mat = self.materials.material_keys[mat]
                Mat.update()
                props['UseMaterial'] = True
                props['Material'] = mat
                self.materials._aedmattolibrary(mat)
            elif self.materials.checkifmaterialexists(mat):
                props['UseMaterial'] = True
                props['Material'] = mat
            else:
                return False
        else:
            props['UseMaterial'] = False
            props['Conductivity'] = str(cond)
            props['Permeability'] = str(str(perm))
        props['UseThickness'] = usethickness
        if usethickness:
            props['Thickness'] = thickness
        if usehuray:
            props['Radius'] = str(radius)
            props['Ratio'] = str(ratio)
            props['InfGroundPlane'] = False
        else:
            props['Roughness'] = roughness
            props['InfGroundPlane'] = isinfgnd
        props['IsTwoSided'] = istwoside

        if istwoside:
            props['IsShellElement'] = issheelElement
        else:
            props['IsInternal'] = isInternal
        return self._create_boundary("Coating_" + listobjname[:32], props, "FiniteCond")

    @aedt_exception_handler
    def create_frequency_sweep(self, setupname, unit="GHz", freqstart=1e-3, freqstop=10, sweepname=None,
                               num_of_freq_points=451, sweeptype="Interpolating",
                               interpolation_tol=0.5, interpolation_max_solutions=250, save_fields=True, save_rad_fields=False):
        """Create a frequency sweep.

        Parameters
        ----------
        setupname : str
            Name of the setup that is attached to the sweep.
        unit : str, optional
            Unit of the frequency. For example, ``"MHz"`` or
            ``"GHz"``. The default is ``"GHz"``.
        freqstart : float, optional
            Starting frequency of the sweep. The default is ``1e-3``.
        freqstop : float, optional
            Stopping frequency of the sweep. The default is ``10``.
        sweepname : str, optional
            Name of the sweep. The default is ``None``.
        num_of_freq_points : int, optional
            Number of frequency points in the range. The default is ``451``.
        sweeptype : str, optional
            Type of the sweep. Options are ``"Fast"``, ``"Interpolating"``,
            and ``"Discrete"``. The default is ``"Interpolating"``.
        interpolation_tol : float, optional
            Error tolerance threshold for the interpolation
            process. The default is ``0.5``.
        interpolation_max_solutions : int, optional
            Maximum number of solutions evaluated for the interpolation process. The default is
            ``250``.
        save_fields : bool, optional
            Whether to save the fields. The default is ``True``.
        save_rad_fields : bool, optional
            Whether to save the radiating fields. The default is ``False``.

        Returns
        -------
        pyaedt.modules.SetupTemplates.SweepHFSS, pyaedt.modules.SetupTemplates.SweepQ3D, or bool
            Sweep object if successful. ``False`` if unsuccessful.

        Examples
        --------

        Create a setup named ``'FrequencySweepSetup'`` and use it in a
        frequency sweep named ``'MySweepFast'``.

        >>> setup = hfss.create_setup("FrequencySweepSetup")
        >>> setup.props["Frequency"] = "1GHz"
        >>> setup.props["BasisOrder"] = 2
        >>> setup.props["MaximumPasses"] = 1
        >>> frequency_sweep = hfss.create_frequency_sweep(setupname="FrequencySweepSetup", sweepname="MySweepFast",
        ...                                               unit="MHz", freqstart=1.1e3, freqstop=1200.1,
        ...                                               num_of_freq_points=1234, sweeptype="Fast")
        >>> type(frequency_sweep)
        <class 'pyaedt.modules.SetupTemplates.SweepHFSS'>

        """

        if sweepname is None:
            sweepname = generate_unique_name("Sweep")

        if setupname not in self.setup_names:
            return False
        for i in self.setups:
            if i.name == setupname:
                setupdata = i
                for sw in setupdata.sweeps:
                    if sweepname == sw.name:
                        self._messenger.add_warning_message(
                            "Sweep {} is already present. Rename and retry.".format(sweepname))
                        return False
                sweepdata = setupdata.add_sweep(sweepname, sweeptype)
                sweepdata.props["RangeStart"] = str(freqstart) + unit
                sweepdata.props["RangeEnd"] = str(freqstop) + unit
                sweepdata.props["RangeCount"] = num_of_freq_points
                sweepdata.props["Type"] = sweeptype
                if sweeptype == "Interpolating":
                    sweepdata.props["InterpTolerance"] = interpolation_tol
                    sweepdata.props["InterpMaxSolns"] = interpolation_max_solutions
                    sweepdata.props["InterpMinSolns"] = 0
                    sweepdata.props["InterpMinSubranges"] = 1
                sweepdata.props["SaveFields"] = save_fields
                sweepdata.props["SaveRadFields"] = save_rad_fields
                sweepdata.update()
                return sweepdata
        return False

    @aedt_exception_handler
    def create_linear_count_sweep(self, setupname, unit, freqstart, freqstop, num_of_freq_points,
                                  sweepname=None, save_fields=True, save_rad_fields=False, sweep_type="Discrete"):
        """Create a discrete sweep with the specified number of points.

        Parameters
        ----------
        setupname : str
            Name of the setup.
        unit : str
            Unit of the frequency. For example, ``"MHz`` or ``"GHz"``. The default is ``"GHz"``.
        freqstart : float
            Starting frequency of the sweep, such as ``1``.
        freqstop : float
            Stopping frequency of the sweep.
        num_of_freq_points : int
            Number of frequency points in the range.
        sweepname : str, optional
            Name of the sweep. The default is ``None``.
        save_fields : bool, optional
            Whether to save the fields. The default is ``True``.
        save_rad_fields : bool, optional
            Whether to save the radiating fields. The default is ``False``.
        sweep_type: str, optional

        Returns
        -------
        :class: `pyaedt.modules.SetupTemplates.SweepHFSS` or bool
            Sweep object if successful. ``False`` if unsuccessful.

        Examples
        --------

        Create a setup named ``"LinearCountSetup"`` and use it in a linear count sweep
        named ``"LinearCountSweep"``.

        >>> setup = hfss.create_setup("LinearCountSetup")
        >>> linear_count_sweep = hfss.create_linear_count_sweep(setupname="LinearCountSetup",
        ...                                                     sweepname="LinearCountSweep",
        ...                                                     unit="MHz", freqstart=1.1e3,
        ...                                                     freqstop=1200.1, num_of_freq_points=1658)
        >>> type(linear_count_sweep)
        <class 'pyaedt.modules.SetupTemplates.SweepHFSS'>

        """
        if sweep_type not in ["Discrete", "Interpolating", "Fast"]:
            self.add_error_message("Invalid in `sweep_type`. It has to either 'Discrete', 'Interpolating', or 'Fast'")
            return False
        return self.create_frequency_sweep(setupname, unit, freqstart, freqstop, sweepname, num_of_freq_points,
                                           sweep_type, interpolation_tol=0.5, interpolation_max_solutions=250,
                                           save_fields=save_fields, save_rad_fields=save_rad_fields)

    @aedt_exception_handler
    def create_linear_step_sweep(self, setupname, unit, freqstart, freqstop, step_size,
                                 sweepname=None, save_fields=True, save_rad_fields=False, sweep_type="Discrete"):
        """Create a Sweep with a specified number of points.

        Parameters
        ----------
        setupname : str
            Name of the setup.
        unit : str
            Unit of the frequency. For example, ``"MHz`` or ``"GHz"``. The default is ``"GHz"``.
        freqstart : float
            Starting frequency of the sweep.
        freqstop : float
            Stopping frequency of the sweep.
        step_size : float
            Frequency size of the step.
        sweepname : str, optional
            Name of the sweep. The default is ``None``.
        save_fields : bool, optional
            Whether to save the fields. The default is ``True``.
        save_rad_fields : bool, optional
            Whether to save the radiating fields. The default is ``False``.
        sweep_type : str, optional
            Whether to create a ``"Discrete"``,``"Interpolating"`` or ``"Fast"`` sweep.
            The default is ``"Discrete"``.

        Returns
        -------
        :class: `pyaedt.modules.SetupTemplates.SweepHFSS` or bool
            Sweep object if successful. ``False`` if unsuccessful.

        Examples
        --------

        Create a setup named ``"LinearStepSetup"`` and use it in a linear step sweep
        named ``"LinearStepSweep"``.

        >>> setup = hfss.create_setup("LinearStepSetup")
        >>> linear_step_sweep = hfss.create_linear_step_sweep(setupname="LinearStepSetup",
        ...                                                   sweepname="LinearStepSweep",
        ...                                                   unit="MHz", freqstart=1.1e3,
        ...                                                   freqstop=1200.1, step_size=153.8)
        >>> type(linear_step_sweep)
        <class 'pyaedt.modules.SetupTemplates.SweepHFSS'>

        """
        if sweep_type not in ["Discrete", "Interpolating", "Fast"]:
            self.add_error_message("Invalid in `sweep_type`. It has to either 'Discrete', 'Interpolating', or 'Fast'")
        if sweepname is None:
            sweepname = generate_unique_name("Sweep")

        if setupname not in self.setup_names:
            return False
        for i in self.setups:
            if i.name == setupname:
                setupdata = i
                for sw in setupdata.sweeps:
                    if sweepname == sw.name:
                        self._messenger.add_warning_message(
                            "Sweep {} is already present. Rename and retry.".format(sweepname))
                        return False
                sweepdata = setupdata.add_sweep(sweepname, sweep_type)
                sweepdata.props["RangeStart"] = str(freqstart) + unit
                sweepdata.props["RangeEnd"] = str(freqstop) + unit
                sweepdata.props["RangeStep"] = str(step_size) + unit
                sweepdata.props["SaveFields"] = save_fields
                sweepdata.props["SaveRadFields"] = save_rad_fields
                sweepdata.props["ExtrapToDC"] = False
                sweepdata.props["Type"] = sweep_type
                sweepdata.props["RangeType"] = "LinearStep"
                if sweep_type == "Interpolating":
                    sweepdata.props["InterpTolerance"] = 0.5
                    sweepdata.props["InterpMaxSolns"] = 250
                    sweepdata.props["InterpMinSolns"] = 0
                    sweepdata.props["InterpMinSubranges"] = 1
                sweepdata.update()
                return sweepdata
        return False

    @aedt_exception_handler
    def create_sbr_linked_antenna(self, source_object, target_cs="Global", solution=None, fieldtype="nearfield",
                                  use_composite_ports=False, use_global_current=True, current_conformance="Disable",
                                  thin_sources=True, power_fraction="0.95"):
        """Create a linked antenna.

        Parameters
        ----------
        source_object : pyaedt.Hfss
            Source object.
        target_cs : str, optional
            Target coordinate system. The default is ``"Global"``.
        solution : optional
            The default is ``None``.
        fieldtype : str, optional
            The default is ``"nearfield"``.
        use_composite_ports : bool, optional
            Whether to use composite ports. The default is ``True``.
        use_global_current : bool, optional
            Whether to use global current. The default is ``True``.
        current_conformance, str optional
            The default is ``"Disable'``.
        thin_sources : bool, optional
             The default is ``True``.
        power_fraction : str, optional
             The default is ``"0.95"``.

        Examples
        --------
        >>> from pyaedt import Hfss
        >>> target_project = "my/path/to/targetProject.aedt"
        >>> source_project = "my/path/to/sourceProject.aedt"
        >>> target = Hfss(projectname=target_project, solution_type="SBR+",
        ...               specified_version="2021.1", AlwaysNew=False)  # doctest: +SKIP
        >>> source = Hfss(projectname=source_project, designname="feeder",
        ...               specified_version="2021.1", AlwaysNew=False)  # doctest: +SKIP
        >>> target.create_sbr_linked_antenna(source, target_cs="feederPosition",
        ...                                  fieldtype="farfield")  # doctest: +SKIP

        """
        if self.solution_type != "SBR+":
            self.add_error_message("This Native components only applies to SBR+ Solution")
            return False
        compName = source_object.design_name
        uniquename = generate_unique_name(compName)
        if source_object.project_name == self.project_name:
            project_name = "This Project*"
        else:
            project_name = os.path.join(source_object.project_path,
                                        source_object.project_name + ".aedt")
        design_name = source_object.design_name
        if not solution:
            solution = source_object.nominal_adaptive
        params = OrderedDict({})
        pars = source_object.available_variations.nominal_w_values_dict
        for el in pars:
            params[el] = pars[el]
        native_props = OrderedDict({"Type": "Linked Antenna",
                        "Unit": self.modeler.model_units, "Is Parametric Array": False, "Project": project_name,
                        "Product": "HFSS", "Design": design_name, "Soln": solution, "Params": params,
                        "ForceSourceToSolve": True, "PreservePartnerSoln": True, "PathRelativeTo":
                        "TargetProject", "FieldType": fieldtype, "UseCompositePort": use_composite_ports,
                        "SourceBlockageStructure": OrderedDict({"NonModelObject": []})})
        if fieldtype == "nearfield":
            native_props["UseGlobalCurrentSrcOption"] = use_global_current
            native_props["Current Source Conformance"]= current_conformance
            native_props["Thin Sources"] = thin_sources
            native_props[ "Power Fraction"] = power_fraction
        return self._create_native_component("Linked Antenna", target_cs, self.modeler.model_units, native_props, uniquename )

    @aedt_exception_handler
    def _create_native_component(self, antenna_type, target_cs=None, model_units=None, parameters_dict=None,
                                 antenna_name=None):
        if antenna_name is None:
            antenna_name = generate_unique_name(antenna_type.replace(" ", "").replace("-",""))
        if not model_units:
            model_units = self.modeler.model_units

        native_props = OrderedDict({"NativeComponentDefinitionProvider": OrderedDict({"Type": antenna_type,
                                                                                      "Unit": model_units})})
        native_props["TargetCS"] = target_cs
        if isinstance(parameters_dict, dict):
            for el in parameters_dict:
                if el not in ["antenna_type", "offset", "rotation", "rotation_axis", "mode"] and parameters_dict[el] is not None:
                    native_props["NativeComponentDefinitionProvider"][el.replace(
                        "_", " ").title()] = parameters_dict[el]
        native = NativeComponentObject(self, antenna_type,antenna_name, native_props)
        if native.create():
            self.native_components.append(native)
            return native
        return None

    class SbrAntennas:
        (ConicalHorn, CrossDipole, HalfWaveDipole, HorizontalDipole, ParametricBeam, ParametricSlot, PyramidalHorn,
         QuarterWaveMonopole, ShortDipole, SmallLoop, WireDipole, WireMonopole) = (
            "Conical Horn", "Cross Dipole", "Half-Wave Dipole", "Horizontal Dipole", "Parametric Beam", "Parametric Slot",
            "Pyramidal Horn", "Quarter-Wave Monopole", "Short Dipole", "Small Loop", "Wire Dipole", "Wire Monopole")

    class SBRAntennaDefaults:
        _conical = OrderedDict(
            {"Is Parametric Array": False, "MatchedPortImpedance": "50ohm", "Polarization": "Vertical",
             "Representation": "Far Field", "Mouth Diameter": "0.3meter", "Flare Half Angle": "20deg"})
        _cross = OrderedDict(
            {"Is Parametric Array": False, "MatchedPortImpedance": "50ohm", "Polarization": "RHCP",
             "Representation": "Current Source", "Density": "1", "UseGlobalCurrentSrcOption": True,
             "Resonant Frequency": "0.3GHz", "Wire Length": "499.654096666667mm", "Mode": 0})
        _horizontal = OrderedDict(
            {"Is Parametric Array": False, "MatchedPortImpedance": "50ohm", "Polarization": "Vertical",
             "Representation": "Current Source", "Density": "1", "UseGlobalCurrentSrcOption": False,
             "Resonant Frequency": "0.3GHz", "Wire Length": "499.654096666667mm",
             "Height Over Ground Plane": "249.827048333333mm", "Use Default Height": True})
        _parametricbeam = OrderedDict(
            {"Is Parametric Array": False, "Size": "0.1mm", "MatchedPortImpedance": "50ohm", "Polarization": "Vertical",
             "Representation": "Far Field", "Vertical BeamWidth": "30deg", "Horizontal BeamWidth": "60deg"})
        _slot = OrderedDict(
            {"Is Parametric Array": False, "MatchedPortImpedance": "50ohm", "Representation": "Far Field",
             "Resonant Frequency": "0.3GHz", "Slot Length": "499.654096666667mm"})
        _horn = OrderedDict(
            {"Is Parametric Array": False, "MatchedPortImpedance": "50ohm", "Representation": "Far Field",
             "Mouth Width": "0.3meter", "Mouth Height": "0.5meter", "Waveguide Width": "0.15meter",
             "Width Flare Half Angle": "20deg", "Height Flare Half Angle": "35deg"})
        _dipole = OrderedDict(
            {"Is Parametric Array": False, "Size": "1mm", "MatchedPortImpedance": "50ohm",
             "Representation": "Far Field"})
        _smallloop = OrderedDict(
            {"Is Parametric Array": False, "MatchedPortImpedance": "50ohm", "Polarization": "Vertical",
             "Representation": "Current Source", "Density": "1", "UseGlobalCurrentSrcOption": False,
             "Current Source Conformance": "Disable", "Thin Sources": True, "Power Fraction": "0.95",
             "Mouth Diameter": "0.3meter", "Flare Half Angle": "20deg"})
        _wiredipole = OrderedDict(
            {"Is Parametric Array": False, "MatchedPortImpedance": "50ohm", "Representation": "Far Field",
             "Resonant Frequency": "0.3GHz", "Wire Length": "499.654096666667mm"})
        parameters = {"Conical Horn": _conical, "Cross Dipole": _cross, "Half-Wave Dipole": _dipole,
                      "Horizontal Dipole": _horizontal, "Parametric Beam": _parametricbeam, "Parametric Slot": _slot,
                      "Pyramidal Horn": _horn, "Quarter-Wave Monopole": _dipole, "Short Dipole": _dipole,
                      "Small Loop": _dipole, "Wire Dipole": _wiredipole, "Wire Monopole": _wiredipole}
        default_type_id = {"Conical Horn": 11, "Cross Dipole": 12, "Half-Wave Dipole": 3,
                      "Horizontal Dipole": 13, "Parametric Beam": 0, "Parametric Slot": 7,
                      "Pyramidal Horn": _horn, "Quarter-Wave Monopole": 4, "Short Dipole": 1,
                      "Small Loop": 2, "Wire Dipole": 5, "Wire Monopole": 6, "File Based Antenna": 8}

    @aedt_exception_handler
    def create_sbr_antenna(self, antenna_type=SbrAntennas.ConicalHorn, target_cs=None, model_units=None,
                           parameters_dict=None, use_current_source_representation=False, is_array=False, antenna_name=None):
        """Create a Parametric Beam antenna in SBR+.

        Parameters
        ----------
        antenna_type: str, `SbrAntennas.ConicalHorn`
            Name of the Antenna type. Enumerator SbrAntennas can also be used.
        target_cs : str, optional
            Target coordinate system. The default is the active one.
        model_units: str, optional
            Model units to be applied to the object. Default is
            ``None`` which is the active modeler units.
        parameters_dict : dict, optional
            The default is ``"nearfield"``.
        antenna_name : str, optional
            3D component name. The default is auto-generated based on the antenna type.

        Returns
        -------
        pyaedt.modules.Boundary.NativeComponentObject
            NativeComponentObject object.

        Examples
        --------
        >>> from pyaedt import Hfss
        >>> hfss = Hfss(solution_type="SBR+")  # doctest: +SKIP
        pyaedt Info: Added design 'HFSS_IPO' of type HFSS.
        >>> parm = {"polarization": "Vertical"}  # doctest: +SKIP
        >>> par_beam = hfss.create_sbr_antenna(hfss.SbrAntennas.ShortDipole,
        ...                                    parameters_dict=parm,
        ...                                    antenna_name="TX1")  # doctest: +SKIP

        """
        if self.solution_type != "SBR+":
            self.add_error_message("This Native component only applies to a SBR+ Solution.")
            return False
        if target_cs is None:
            target_cs = self.modeler.oeditor.GetActiveCoordinateSystem()
        parameters_defaults = self.SBRAntennaDefaults.parameters[antenna_type].copy()
        if use_current_source_representation and antenna_type in ["Conical Horn", "Horizontal Dipole",
                                                                  "Parametric Slot", "Pyramidal Horn", "Wire Dipole",
                                                                  "Wire Monopole"]:
            parameters_defaults["Representation"] = "Current Source"
            parameters_defaults["Density"] = "1"
            parameters_defaults["UseGlobalCurrentSrcOption"] =  False
            parameters_defaults["Current Source Conformance"] =  "Disable"
            parameters_defaults["Thin Sources"] = False
            parameters_defaults["Power Fraction"] = "0.95"
        if is_array:
            parameters_defaults["Is Parametric Array"] = True
            parameters_defaults["Array Element Type"]= self.SBRAntennaDefaults.default_type_id[antenna_type]
            parameters_defaults["Array Element Angle Phi"]= "0deg",
            parameters_defaults["Array Element Angle Theta"]= "0deg",
            parameters_defaults["Array Element Offset X"]= "0meter"
            parameters_defaults["Array Element Offset Y"]= "0meter"
            parameters_defaults["Array Element Offset Z"]= "0meter"
            parameters_defaults["Array Element Conformance Type"]= 0
            parameters_defaults["Array Element Conformance Type"]= 0
            parameters_defaults["Array Element Conformance Type"]= 0
            parameters_defaults["Array Element Conform Orientation"]= False
            parameters_defaults["Array Design Frequency"]= "1GHz"
            parameters_defaults["Array Layout Type"]= 1
            parameters_defaults["Array Specify Design In Wavelength"]= True
            parameters_defaults["Array Element Num"]= 5
            parameters_defaults["Array Length"]= "1meter"
            parameters_defaults["Array Width"]= "1meter"
            parameters_defaults["Array Length Spacing"]= "0.1meter"
            parameters_defaults["Array Width Spacing"]= "0.1meter"
            parameters_defaults["Array Length In Wavelength"]= "3"
            parameters_defaults["Array Width In Wavelength"]= "4"
            parameters_defaults["Array Length Spacing In Wavelength"]= "0.5"
            parameters_defaults["Array Stagger Type"]= 0
            parameters_defaults["Array Stagger Angle"]= "0deg"
            parameters_defaults["Array Symmetry Type"]= 0
            parameters_defaults["Array Weight Type"]= 3
            parameters_defaults["Array Beam Angle Theta"]= "0deg"
            parameters_defaults["Array Weight Edge TaperX"]= -200
            parameters_defaults["Array Weight Edge TaperY"]= -200
            parameters_defaults["Array Weight Cosine Exp"]= 1
            parameters_defaults["Array Differential Pattern Type"]= 0
            if is_array:
                antenna_name = generate_unique_name("pAntArray")
        if parameters_dict:
            for el, value in parameters_dict.items():
                parameters_defaults[el] = value
        return self._create_native_component(antenna_type, target_cs, model_units, parameters_defaults, antenna_name)

    @aedt_exception_handler
    def create_sbr_file_based_antenna(self, ffd_full_path, antenna_size="1mm", antenna_impedance="50ohm",
                                      representation_type="Far Field", target_cs=None, model_units=None,
                                      antenna_name=None):
        """Create a linked antenna.

        Parameters
        ----------
        ffd_full_path: str
            Full path to the ffd file.
        antenna_size: str, optional
            Antenna size with units.
        antenna_impedance: str, optional
            Antenna impedance with units.
        representation_type: str, optional
            Antenna type.  Either ``"Far Field"`` or ``"Near Field"``.
        target_cs : str, optional
            Target coordinate system. The default is the active coordinate system.
        model_units: str, optional
            Model units to be applied to the object. Default is
            ``None`` which is the active modeler units.
        antenna_name : str, optional
            3D component name. The default is the auto-generated based
            on the antenna type.

        Returns
        -------
        pyaedt.modules.Boundary.NativeComponentObject
            NativeComponentObject object.

        Examples
        --------
        >>> from pyaedt import Hfss
        >>> hfss = Hfss(solution_type="SBR+")  # doctest: +SKIP
        >>> ffd_file = "full_path/to/ffdfile.ffd"
        >>> par_beam = hfss.create_sbr_file_based_antenna(ffd_file)  # doctest: +SKIP

        """
        if self.solution_type != "SBR+":
            self.add_error_message("This Native component only applies to a SBR+ Solution.")
            return False
        if target_cs is None:
            target_cs = self.modeler.oeditor.GetActiveCoordinateSystem()

        par_dicts = OrderedDict(
            {"Size": antenna_size, "MatchedPortImpedance": antenna_impedance, "Representation": representation_type,
             "ExternalFile": ffd_full_path})
        if not antenna_name:
            antenna_name = generate_unique_name(os.path.basename(ffd_full_path).split(".")[0])

        return self._create_native_component("File Based Antenna", target_cs, model_units, par_dicts, antenna_name)

    @aedt_exception_handler
    def set_sbr_txrx_settings(self, txrx_settings):
        """Set Sbr+ TX RX Antenna Settings.

        Parameters
        ----------
        txrx_settings : dict
            Dictionary containing the TX as key and RX as values

        Returns
        -------
        pyaedt.modules.Boundary.BoundaryObject
            Boundary object.

        Examples
        --------

        """
        if self.solution_type != "SBR+":
            self.add_error_message("This Boundary only applies to SBR+ Solution")
            return False
        id = 0
        props=OrderedDict({})
        for el, val in txrx_settings.items():
            props["Tx/Rx List " + \
                str(id)] = OrderedDict({"Tx Antenna": el, "Rx Antennas": txrx_settings[el]})
            id += 1
        return self._create_boundary("SBRTxRxSettings", props, "SBRTxRxSettings")

    @aedt_exception_handler
    def create_single_point_sweep(self, setupname, sweepname="SinglePoint", freq_start="1GHz", save_field=True,
                              save_radiating_field=False):
        """Create a discrete sweep with a single frequency value.

        Parameters
        ----------
        setupname : str
            Name of the setup.
        sweepname : str, optional
            Name of the sweep. The default is ``"SinglePoint"``.
        freq_start : str, optional
            Sweep frequency point with units. The default is ``"1GHz"``.
        save_field : bool, optional
            Whether to save the field. The default is ``True``.
        save_radiating_field : bool, optional
            Whether to save the radiating field. The default is ``False``.


        Returns
        -------
        :class: `pyaedt.modules.SetupTemplates.SweepHFSS` or bool
            Sweep object if successful. ``False`` if unsuccessful.

        Examples
        --------

        Create a setup named ``"DiscreteSweepSetup"`` and use it in a discrete sweep
        named ``"DiscreteSweep"``.

        >>> setup = hfss.create_setup("DiscreteSweepSetup")
        >>> discrete_sweep = hfss.create_single_point_sweep(setupname="DiscreteSweepSetup",
        ...                                             sweepname="DiscreteSweep", freq_start="2GHz")
        pyaedt Info: Sweep was created correctly.

        """

        if sweepname is None:
            sweepname = generate_unique_name("Sweep")

        if setupname not in self.setup_names:
            return False
        for i in self.setups:
            if i.name == setupname:
                setupdata = i
                for sw in setupdata.sweeps:
                    if sweepname == sw.name:
                        self._messenger.add_warning_message(
                            "Sweep {} is already present. Rename and retry.".format(sweepname))
                        return False
                sweepdata = setupdata.add_sweep(sweepname, "Discrete")
                sweepdata.props["RangeStart"] = freq_start
                sweepdata.props["SaveSingleField"] = save_field
                sweepdata.props["SaveFields"] = save_field
                sweepdata.props["SaveRadFields"] = save_radiating_field
                sweepdata.props["ExtrapToDC"] = False
                sweepdata.props["Type"] = "Discrete"
                sweepdata.props["RangeType"] = "LinearCount"
                sweepdata.update()
                self._messenger.add_info_message("Sweep was created correctly.")
                return sweepdata
        return False

    @aedt_exception_handler
    def create_circuit_port_between_objects(self, startobj, endobject, axisdir="XYNeg", impedance=50, portname=None,
                                            renorm=True, renorm_impedance=50, deemb=False):
        """Create a circuit port taking the closest edges of two objects.

        Parameters
        ----------
        startobj :
            First (starting) object for the integration line.
        endobject :
            Second (ending) object for the integration line.
        axisdir : str, optional
            Position of the port. It should be one of the values for ``Application.AxisDir``,
            which are: ``"XNeg"``, ``"YNeg"``, ``"ZNeg"``, ``"XPos"``, ``"YPos"``, and ``"ZPos"``.
            The default is ``"XYNeg"``.
        impedance : float, optional
            Port impedance. The default is ``50``.
        portname : str, optional
            Name of the port. The default is ``None``.
        renorm : bool, optional
            Whether to renormalize the mode. The default is ``True``.
        renorm_impedance : float or str, optional
            Renormalize impedance. The default is ``50``.
        deemb : bool, optional
            Whether to deembed the port. The default is ``False``.

        Returns
        -------
        str
            Name of port created when successful, ``False`` otherwise.

        Examples
        --------

        Create two boxes that will be used to create a circuit port
        named ``'CircuitExample'``.

        >>> box1 = hfss.modeler.primitives.create_box([0, 0, 80], [10, 10, 5],
        ...                                           "BoxCircuit1", "copper")
        >>> box2 = hfss.modeler.primitives.create_box([0, 0, 100], [10, 10, 5],
        ...                                           "BoxCircuit2", "copper")
        >>> hfss.create_circuit_port_between_objects("BoxCircuit1", "BoxCircuit2",
        ...                                          hfss.AxisDir.XNeg, 50,
        ...                                          "CircuitExample", True, 50, False)
        'CircuitExample'

        """

        if not self.modeler.primitives.does_object_exists(startobj) or not self.modeler.primitives.does_object_exists(
                endobject):
            self._messenger.add_error_message("One or both objects doesn't exists. Check and retry")
            return False
        if self.solution_type in ["DrivenModal", "DrivenTerminal", "Transient Network"]:
            out, parallel = self.modeler.primitives.find_closest_edges(startobj, endobject, axisdir)
            port_edges = []
            if not portname:
                portname = generate_unique_name("Port")
            elif portname + ":1" in self.modeler.get_excitations_name():
                portname = generate_unique_name(portname)
            if self._create_circuit_port(out, impedance, portname, renorm, deemb, renorm_impedance=renorm_impedance):
                return portname
        return False

    @aedt_exception_handler
    def create_lumped_port_between_objects(self, startobj, endobject, axisdir=0, impedance=50, portname=None,
                                           renorm=True, deemb=False, port_on_plane=True):
        """Create a lumped port taking the closest edges of two objects.

        Parameters
        ----------
        startobj :
            First (starting) object for the integration line.
        endobject :
            Second (ending) object for the integration line.
        axisdir :
            Position of the port. It should be one of the values for ``Application.AxisDir``, which are:
            ``"XNeg"``, ``"YNeg"``, ``"ZNeg"``, ``"XPos"``, ``"YPos"``, and ``"ZPos"``. The default is ``"0"``.
        impedance : float, optional
            Port impedance. The default is ``50``.
        portname : str, optional
            Name of the port. The default is ``None``.
        renorm : bool, optional
            Whether to renormalize the mode. The default is ``True``.
        deemb : bool, optional
            Whether to deembed the port. The default is ``False``.
        port_on_plane : bool, optional
            Whether to create the source on the plane orthogonal to ``AxisDir``.
            The default is ``True``.

        Returns
        -------
        str
            Name of port created when successful, ``False`` otherwise.

        Examples
        --------

        Create two boxes that will be used to create a lumped port
        named ``'LumpedPort'``.

        >>> box1 = hfss.modeler.primitives.create_box([0, 0, 50], [10, 10, 5],
        ...                                           "BoxLumped1","copper")
        >>> box2 = hfss.modeler.primitives.create_box([0, 0, 60], [10, 10, 5],
        ...                                           "BoxLumped2", "copper")
        >>> hfss.create_lumped_port_between_objects("BoxLumped1", "BoxLumped2",
        ...                                         hfss.AxisDir.XNeg, 50,
        ...                                         "LumpedPort", True, False)
        pyaedt Info: Connection Correctly created
        'LumpedPort'

        """

        if not self.modeler.primitives.does_object_exists(startobj) or not self.modeler.primitives.does_object_exists(
                endobject):
            self._messenger.add_error_message("One or both objects do not exist. Check and retry.")
            return False

        if self.solution_type in ["DrivenModal", "DrivenTerminal", "Transient Network"]:
            sheet_name, point0, point1 = self.modeler._create_sheet_from_object_closest_edge(startobj, endobject,
                                                                                             axisdir, port_on_plane)

            if not portname:
                portname = generate_unique_name("Port")
            elif portname + ":1" in self.modeler.get_excitations_name():
                portname = generate_unique_name(portname)
            if self.solution_type == "DrivenModal":
                self._create_lumped_driven(sheet_name, point0, point1,
                                           impedance, portname, renorm, deemb)
            else:
                faces = self.modeler.primitives.get_object_faces(sheet_name)
                self._create_port_terminal(faces[0], endobject, portname, iswaveport=False)
            return portname
        return False

    @aedt_exception_handler
    def create_voltage_source_from_objects(self, startobj, endobject, axisdir=0, sourcename=None, source_on_plane=True):
        """Create a voltage source taking the closest edges of two objects.

        Parameters
        ----------
        startobj :
            First (starting) object for the integration line.
        endobject :
            Second (ending) object for the integration line.
        axisdir : str, optional
            Position of the port. It should be one of the values for ``Application.AxisDir``,
            which are: ``"XNeg"``, ``"YNeg"``, ``"ZNeg"``, ``"XPos"``, ``"YPos"``, and ``"ZPos"``.
            The default value is ``"0"``.
        sourcename : str, optional
            Name of the source. The default is ``None``.
        source_on_plane : bool, optional
            Whether to create the source on the plane orthogonal to ``AxisDir``. The default is ``True``.

        Returns
        -------
        str
           Name of source created when successful, ``False`` otherwise.

        Examples
        --------

        Create two boxes that will be used to create a voltage source
        named ``'VoltageSource'``.

        >>> box1 = hfss.modeler.primitives.create_box([30, 0, 0], [40, 10, 5],
        ...                                           "BoxVolt1", "copper")
        >>> box2 = hfss.modeler.primitives.create_box([30, 0, 10], [40, 10, 5],
        ...                                           "BoxVolt2", "copper")
        >>> hfss.create_voltage_source_from_objects("BoxVolt1", "BoxVolt2",
        ...                                         hfss.AxisDir.XNeg,
        ...                                         "VoltageSource")
        pyaedt Info: Connection Correctly created
        'VoltageSource'

        """

        if not self.modeler.primitives.does_object_exists(startobj) or not self.modeler.primitives.does_object_exists(
                endobject):
            self._messenger.add_error_message("One or both objects doesn't exists. Check and retry")
            return False
        if self.solution_type in ["DrivenModal", "DrivenTerminal", "Transient Network"]:
            sheet_name, point0, point1 = self.modeler._create_sheet_from_object_closest_edge(startobj, endobject,
                                                                                             axisdir, source_on_plane)
            if not sourcename:
                sourcename = generate_unique_name("Voltage")
            elif sourcename + ":1" in self.modeler.get_excitations_name():
                sourcename = generate_unique_name(sourcename)
            status = self.create_source_excitation(
                sheet_name, point0, point1, sourcename, sourcetype="Voltage")
            if status:
                return sourcename
            else:
                return False
        return False

    @aedt_exception_handler
    def create_current_source_from_objects(self, startobj, endobject, axisdir=0, sourcename=None, source_on_plane=True):
        """Create a current source taking the closest edges of two objects.

        Parameters
        ----------
        startobj :
            First (starting) object for the integration line.
        endobject :
            Second (ending) object for the integration line.
        axisdir : optional
            Position of the current source. It should be one of the values for ``Application.AxisDir``, which are:
            ``"XNeg"``, ``"YNeg"``, ``"ZNeg"``, ``"XPos"``, ``"YPos"``, and ``"ZPos"``. The default is ``"0"``.
        sourcename : str, optional
            Name of the source. The default is ``None``.
        source_on_plane : bool, optional
            Whether to create the source on the plane orthogonal to ``axisdir``. The default is ``True``.

        Returns
        -------
        str
            Name of the source created when successful, ``False`` otherwise.

        Examples
        --------

        Create two boxes that will be used to create a current source
        named ``'CurrentSource'``.

        >>> box1 = hfss.modeler.primitives.create_box([30, 0, 20], [40, 10, 5],
        ...                                           "BoxCurrent1", "copper")
        >>> box2 = hfss.modeler.primitives.create_box([30, 0, 30], [40, 10, 5],
        ...                                           "BoxCurrent2", "copper")
        >>> hfss.create_current_source_from_objects("BoxCurrent1", "BoxCurrent2",
        ...                                         hfss.AxisDir.XPos,
        ...                                         "CurrentSource")
        pyaedt Info: Connection Correctly created
        'CurrentSource'

        """

        if not self.modeler.primitives.does_object_exists(startobj) or not self.modeler.primitives.does_object_exists(
                endobject):
            self._messenger.add_error_message("One or both objects do not exist. Check and retry.")
            return False
        if self.solution_type in ["DrivenModal", "DrivenTerminal", "Transient Network"]:
            sheet_name, point0, point1 = self.modeler._create_sheet_from_object_closest_edge(startobj, endobject,
                                                                                             axisdir, source_on_plane)
            if not sourcename:
                sourcename = generate_unique_name("Current")
            elif sourcename + ":1" in self.modeler.get_excitations_name():
                sourcename = generate_unique_name(sourcename)
            status = self.create_source_excitation(
                sheet_name, point0, point1, sourcename, sourcetype="Current")
            if status:
                return sourcename
            else:
                return False
        return False

    @aedt_exception_handler
    def create_source_excitation(self, sheet_name, point1, point2, sourcename, sourcetype="Voltage"):
        """Create a source excitation.

        Parameters
        ----------
        sheet_name : str
            Name of the sheet.
        point1 :

        point2 :

        sourcename : str
            Name of the source.

        sourcetype : str, optional
            Type of the source. The default is ``"Voltage"``.

        Returns
        -------
        :class: `pyaedt.modules.Boundary.BoundaryObject`
            Boundary object.

        """

        props = OrderedDict({"Objects": [sheet_name],
                             "Direction": OrderedDict({"Start": point1, "End": point2})})
        return self._create_boundary(sourcename, props, sourcetype)

    @aedt_exception_handler
    def create_wave_port_between_objects(self, startobj, endobject, axisdir=0, impedance=50, nummodes=1, portname=None,
                                         renorm=True, deembed_dist=0, port_on_plane=True, add_pec_cap=False):
        """Create a waveport taking the closest edges of two objects.

        Parameters
        ----------
        startobj :
            First (starting) object for the integration line.
        endobject :
            Second (ending) object for the integration line.
        axisdir : str, optional
            Position of the port. It should be one of the values for ``Application.AxisDir``,
            which are: ``"XNeg"``, ``"YNeg"``, ``"ZNeg"``, ``"XPos"``, ``"YPos"``, and ``"ZPos"``.
            The default is ``"0"``.
        impedance : float, optional
            Port impedance. The default is ``50``.
        nummodes : int, optional
            Number of modes. The default is ``1``.
        portname : str, optional
            Name of the port. The default is ``None``.
        renorm : bool, optional
            Whether to renormalize the mode. The default is ``True``.
        deembed_dist : float, optional
            Deembed distance in millimeters. The default is ``0``,
            in which case deembed is disabled.
        port_on_plane : bool, optional
            Whether to create the port on the plane orthogonal to ``AxisDir``. The default is ``True``.
        add_pec_cap : bool, optional
             The default is ``False``.

        Returns
        -------
        :class: `pyaedt.modules.Boundary.BoundaryObject`
            Boundary object.

        Examples
        --------

        Create two boxes that will be used to create a wave port
        named ``'WavePort'``.

        >>> box1 = hfss.modeler.primitives.create_box([0,0,0], [10,10,5],
        ...                                           "BoxWave1", "copper")
        >>> box2 = hfss.modeler.primitives.create_box([0, 0, 10], [10, 10, 5],
        ...                                           "BoxWave2", "copper")
        >>> wave_port = hfss.create_wave_port_between_objects("BoxWave1", "BoxWave2",
        ...                                                   hfss.AxisDir.XNeg, 50, 1,
        ...                                                   "WavePort", False)
        pyaedt Info: Connection Correctly created

        """

        if not self.modeler.primitives.does_object_exists(startobj) or not self.modeler.primitives.does_object_exists(
                endobject):
            self._messenger.add_error_message("One or both objects do not exist. Check and retry.")
            return False
        if self.solution_type in ["DrivenModal", "DrivenTerminal", "Transient Network"]:
            sheet_name, point0, point1 = self.modeler._create_sheet_from_object_closest_edge(startobj, endobject,
                                                                                             axisdir, port_on_plane)
            if add_pec_cap:
                dist = GeometryOperators.points_distance(point0, point1)
                self._create_pec_cap(sheet_name, startobj, dist / 10)
            if not portname:
                portname = generate_unique_name("Port")
            elif portname + ":1" in self.modeler.get_excitations_name():
                portname = generate_unique_name(portname)
            if self.solution_type == "DrivenModal":
                return self._create_waveport_driven(sheet_name, point0, point1, impedance, portname, renorm, nummodes,
                                                    deembed_dist)
            else:
                faces = self.modeler.primitives.get_object_faces(sheet_name)
                return self._create_port_terminal(faces[0], endobject, portname, iswaveport=True)
        return False

    def _create_pec_cap(self, sheet_name, obj_name, pecthick):
        # TODO check method
        obj= self.modeler.primitives[sheet_name].clone()
        out_obj = self.modeler.thicken_sheet(obj, pecthick, False)
        bounding2 = out_obj.bounding_box
        bounding1 = self.modeler.primitives[obj_name].bounding_box
        tol = 1e-9
        i=0
        internal=False
        for a, b in zip(bounding1,bounding2):
            if i<3:
                if (b-a)>tol:
                    internal=True
            elif (b-a)<tol:
                internal = True
            i += 1
        if internal:
            self.odesign.Undo()
            self.modeler.primitives.cleanup_objects()
            out_obj = self.modeler.thicken_sheet(obj, -pecthick, False)

        out_obj.material_name = "pec"
        return True

    @aedt_exception_handler
    def create_wave_port_microstrip_between_objects(self, startobj, endobject, axisdir=0, impedance=50, nummodes=1,
                                                    portname=None,
                                                    renorm=True, deembed_dist=0, vfactor=3, hfactor=5):
        """Create a waveport taking the closest edges of two objects.

        Parameters
        ----------
        startobj :
            First (starting) object for the integration line. This is typically the reference plane.
        endobject :
            Second (ending) object for the integration line.
        axisdir : int, optional
            Position of the port. It should be one of the values for ``Application.AxisDir``,
            which are: ``0`` for ``"XNeg"``,``1`` for ``"YNeg"``,``2`` for ``"ZNeg"``, ``3`` for``"XPos"``,
            ``4`` for``"YPos"``, and ``5`` for``"ZPos"``.
            The default is ``0``.
        impedance : float, optional
            Port impedance. The default is ``50``.
        nummodes : int, optional
            Number of modes. The default is ``1``.
        portname : str, optional
            Name of the port. The default is ``None``.
        renorm : bool, optional
            Whether to renormalize the mode. The default is ``True``.
        deembed_dist : float, optional
            Deembed distance in millimeters. The default is ``0``,
            in which case deembed is disabled.
        vfactor : int, optional
            Port vertical factor. The default is ``3``.
        hfactor : int, optional
            Port horizontal factor. The default is ``5``.

        Returns
        -------
        :class: `pyaedt.modules.Boundary.BoundaryObject`
            Port object.

        Examples
        --------

        Create a wave port supported by a microstrip line.

        >>> ms = hfss.modeler.primitives.create_box([4, 5, 0], [1, 100, 0.2],
        ...                                         name="MS1", matname="copper")
        >>> sub = hfss.modeler.primitives.create_box([0, 5, -2], [20, 100, 2],
        ...                                          name="SUB1", matname="FR4_epoxy")
        >>> gnd = hfss.modeler.primitives.create_box([0, 5, -2.2], [20, 100, 0.2],
        ...                                          name="GND1", matname="FR4_epoxy")
        >>> port = hfss.create_wave_port_microstrip_between_objects("GND1", "MS1",
        ...                                                         portname="MS1",
        ...                                                         axisdir=1)
        pyaedt Info: Connection Correctly created

        """
        if not self.modeler.primitives.does_object_exists(startobj) or not self.modeler.primitives.does_object_exists(
                endobject):
            self._messenger.add_error_message("One or both objects do not exist. Check and retry.")
            return False
        if self.solution_type in ["DrivenModal", "DrivenTerminal", "Transient Network"]:
            sheet_name, point0, point1 = self.modeler._create_microstrip_sheet_from_object_closest_edge(startobj,
                                                                                                        endobject,
                                                                                                        axisdir,
                                                                                                        vfactor,
                                                                                                        hfactor)
            dist = GeometryOperators.points_distance(point0, point1)
            self._create_pec_cap(sheet_name, startobj, dist / 10)
            if not portname:
                portname = generate_unique_name("Port")
            elif portname + ":1" in self.modeler.get_excitations_name():
                portname = generate_unique_name(portname)
            if self.solution_type == "DrivenModal":
                return self._create_waveport_driven(sheet_name, point0, point1, impedance, portname, renorm, nummodes,
                                                    deembed_dist)
            else:
                faces = self.modeler.primitives.get_object_faces(sheet_name)
                return self._create_port_terminal(faces[0], endobject, portname, iswaveport=True)
        return False

    @aedt_exception_handler
    def create_perfecte_from_objects(self, startobj, endobject, axisdir=0, sourcename=None, is_infinite_gnd=False,
                                     bound_on_plane=True):
        """Create a Perfect E taking the closest edges of two objects.

        Parameters
        ----------
        startobj :
            First object (starting object for integration line)
        endobject :
            Second object (ending object for integration line)
        axisdir : str, optional
            Position of the port. It should be one of the values for ``Application.AxisDir``,
            which are: ``"XNeg"``, ``"YNeg"``, ``"ZNeg"``, ``"XPos"``, ``"YPos"``, and ``"ZPos"``.
            The default is ``"0"``.
        sourcename : str, optional
            Perfect E name. The default is ``None``.
        is_infinite_gnd : bool, optional
            Whether the Perfect E is an infinite ground. The default is ``False``.
        bound_on_plane : bool, optional
            Whether to create the Perfect E on the plane orthogonal to ``AxisDir``. The default is ``True``.

        Returns
        -------
        :class: `pyaedt.modules.Boundary.BoundaryObject` or bool
            Boundary object if successful. ``False`` if unsuccessful.

        Examples
        --------

        Create two boxes that will be used to create a Perfect E named ``'PerfectE'``.

        >>> box1 = hfss.modeler.primitives.create_box([0,0,0], [10,10,5],
        ...                                           "perfect1", "Copper")
        >>> box2 = hfss.modeler.primitives.create_box([0, 0, 10], [10, 10, 5],
        ...                                           "perfect2", "copper")
        >>> perfect_e = hfss.create_perfecte_from_objects("perfect1", "perfect2",
        ...                                               hfss.AxisDir.ZNeg, "PerfectE")
        pyaedt Info: Connection Correctly created
        >>> type(perfect_e)
        <class 'pyaedt.modules.Boundary.BoundaryObject'>

        """

        if not self.modeler.primitives.does_object_exists(startobj) or not self.modeler.primitives.does_object_exists(
                endobject):
            self._messenger.add_error_message("One or both objects do not exist. Check and retry.")
            return False
        if self.solution_type in ["DrivenModal", "DrivenTerminal", "Transient Network"]:
            sheet_name, point0, point1 = self.modeler._create_sheet_from_object_closest_edge(startobj, endobject,
                                                                                             axisdir, bound_on_plane)

            if not sourcename:
                sourcename = generate_unique_name("PerfE")
            elif sourcename in self.modeler.get_boundaries_name():
                sourcename = generate_unique_name(sourcename)
            return self.create_boundary(self.BoundaryType.PerfectE, sheet_name, sourcename, is_infinite_gnd)
        return False

    @aedt_exception_handler
    def create_perfecth_from_objects(self, startobj, endobject, axisdir=0, sourcename=None, bound_on_plane=True):
        """Create a Perfect H taking the closest edges of two objects.

        Parameters
        ----------
        startobj :
            First (starting) object for the integration line.
        endobject :
            Second (ending) object for the integration line.
        axisdir : str, optional
            Position of the port. It should be one of the values for ``Application.AxisDir``,
            which are: ``"XNeg"``, ``"YNeg"``, ``"ZNeg"``, ``"XPos"``, ``"YPos"``, and ``"ZPos"``.
            The default is ``"0"``.
        sourcename : str, optional
            Perfect H name. The default is ``None``.
        bound_on_plane : bool, optional
            Whether to create the Perfect H on the plane orthogonal to ``AxisDir``. The default is ``True``.

        Returns
        -------
        :class: `pyaedt.modules.Boundary.BoundaryObject` or bool
            Boundary object if successful. ``False`` if unsuccessful.

        Examples
        --------

        Create two boxes that will be used to create a Perfect H named ``'PerfectH'``.

        >>> box1 = hfss.modeler.primitives.create_box([0,0,20], [10,10,5],
        ...                                           "perfect1", "Copper")
        >>> box2 = hfss.modeler.primitives.create_box([0, 0, 30], [10, 10, 5],
        ...                                           "perfect2", "copper")
        >>> perfect_h = hfss.create_perfecth_from_objects("perfect1", "perfect2",
        ...                                               hfss.AxisDir.ZNeg, "PerfectH")
        pyaedt Info: Connection Correctly created
        >>> type(perfect_h)
        <class 'pyaedt.modules.Boundary.BoundaryObject'>

        """

        if not self.modeler.primitives.does_object_exists(startobj) or not self.modeler.primitives.does_object_exists(
                endobject):
            self._messenger.add_error_message("One or both objects do not exist. Check and retry.")
            return False
        if self.solution_type in ["DrivenModal", "DrivenTerminal", "Transient Network"]:
            sheet_name, point0, point1 = self.modeler._create_sheet_from_object_closest_edge(startobj, endobject,
                                                                                             axisdir, bound_on_plane)

            if not sourcename:
                sourcename = generate_unique_name("PerfH")
            elif sourcename in self.modeler.get_boundaries_name():
                sourcename = generate_unique_name(sourcename)
            return self.create_boundary(self.BoundaryType.PerfectH, sheet_name, sourcename)
        return None

    @aedt_exception_handler
    def SARSetup(self, Tissue_object_List_ID, TissueMass=1, MaterialDensity=1, voxel_size=1, Average_SAR_method=0):
        """Define SAR settings.

        Parameters
        ----------
        Tissue_object_List_ID : int

        TissueMass : float, optional
            The default is ``1``.
        MaterialDensity : optional
            The default is ``1``.
        voxel_size : optional
            The default is ``1``.
        Average_SAR_method : optional
            The default is ``0``.

        Returns
        -------
        :class: `pyaedt.hfss.SARSetup`
            SARSetup object.

        """
        self.odesign.SARSetup(TissueMass, MaterialDensity,
                              Tissue_object_List_ID, voxel_size, Average_SAR_method)
        return True

    @aedt_exception_handler
    def create_open_region(self, Frequency="1GHz", Boundary="Radiation", ApplyInfiniteGP=False, GPAXis="-z"):
        """Create an open region on the active editor.

        Parameters
        ----------
        Frequency : str, optional
            Frequency with units. The  default is ``"1GHz"``.
        Boundary : str, optional
            Type of the boundary. The default is ``"Radition"``.
        ApplyInfiniteGP : bool, optional
            Whether to apply an infinite ground plane. The default is ``False``.
        GPAXis : str, optional
            The default is ``"-z"``.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.

        """
        vars = [
            "NAME:Settings",
            "OpFreq:=", Frequency,
            "Boundary:=", Boundary,
            "ApplyInfiniteGP:=", ApplyInfiniteGP
        ]
        if ApplyInfiniteGP:
            vars.append("Direction:=")
            vars.append(GPAXis)

        self.omodelsetup.CreateOpenRegion(vars)
        return True

    @aedt_exception_handler
    def create_lumped_rlc_between_objects(self, startobj, endobject, axisdir=0, sourcename=None, rlctype="Parallel",
                                          Rvalue=None, Lvalue=None, Cvalue=None, bound_on_plane=True):
        """Create a lumped RLC taking the closest edges of two objects.

        Parameters
        ----------
        startobj :
            First (starting) object for the integration line.
        endobject :
            Second (ending) object for the integration line.
        axisdir : str, optional
            Position of the port. It should be one of the values for ``Application.AxisDir``,
            which are: ``"XNeg"``, ``"YNeg"``, ``"ZNeg"``, ``"XPos"``, ``"YPos"``, and ``"ZPos"``.
            The default is ``"0"``.
        sourcename : str, optional
            Perfect H name. The default is ``None``.
        rlctype : str, optional
            Type of the RLC. Options are ``"Parallel"`` or ``"Series"``.
            The default is ``"Parallel"``.
        Rvalue : optional
            Resistance value in ohms. The default is ``None``,
            in which case this parameter is disabled.
        Lvalue : optional
            Inductance value in H. The default is ``None``,
            in which case this parameter is disabled.
        Cvalue : optional
            Capacitance value in F. The default is ``None``,
            in which case this parameter is disabled.
        bound_on_plane : bool, optional
            Whether to create the boundary on the plane orthogonal
            to ``AxisDir``. The default is ``True``.

        Returns
        -------
        :class: `pyaedt.modules.Boundary.BoundaryObject` or bool
            Boundary object if successful. ``False`` if unsuccessful.

        Examples
        --------

        Create two boxes that will be used to create a lumped RLC named
        ``'LumpedRLC'``.

        >>> box1 = hfss.modeler.primitives.create_box([0, 0, 50], [10, 10, 5],
        ...                                           "rlc1", "copper")
        >>> box2 = hfss.modeler.primitives.create_box([0, 0, 60], [10, 10, 5],
        ...                                           "rlc2", "copper")
        >>> rlc = hfss.create_lumped_rlc_between_objects("rlc1", "rlc2", hfss.AxisDir.XPos,
        ...                                              "LumpedRLC", Rvalue=50,
        ...                                              Lvalue=1e-9, Cvalue = 1e-6)
        pyaedt Info: Connection Correctly created

        """

        if not self.modeler.primitives.does_object_exists(startobj) or not self.modeler.primitives.does_object_exists(
                endobject):
            self._messenger.add_error_message("One or both objects do not exist. Check and retry.")
            return False
        if self.solution_type in ["DrivenModal", "DrivenTerminal", "Transient Network"] and (
                Rvalue or Lvalue or Cvalue):
            sheet_name, point0, point1 = self.modeler._create_sheet_from_object_closest_edge(startobj, endobject,
                                                                                             axisdir, bound_on_plane)

            if not sourcename:
                sourcename = generate_unique_name("Lump")
            elif sourcename in self.modeler.get_boundaries_name():
                sourcename = generate_unique_name(sourcename)
            start = [str(i) + self.modeler.primitives.model_units for i in point0]
            stop = [str(i) + self.modeler.primitives.model_units for i in point1]

            props = OrderedDict()
            props["Objects"] = [sheet_name]
            props["CurrentLine"] = OrderedDict({"Start": start, "End": stop})
            props["RLC Type"] = [rlctype]
            if Rvalue:
                props["UseResist"] = True
                props["Resistance"] = str(Rvalue) + "ohm"
            if Lvalue:
                props["UseInduct"] = True
                props["Inductance"] = str(Lvalue) + "H"
            if Cvalue:
                props["UseCap"] = True
                props["Capacitance"] = str(Cvalue) + "F"

            return self._create_boundary(sourcename, props, "LumpedRLC")
        return False

    @aedt_exception_handler
    def create_impedance_between_objects(self, startobj, endobject, axisdir=0, sourcename=None, resistance=50,
                                         reactance=0, is_infground=False, bound_on_plane=True):
        """Create an impedance taking the closest edges of two objects.

        Parameters
        ----------
        startobj :
            First (starting) object for the integration line.
        endobject :
            Second (ending) object for the integration line.
        axisdir : str, optional
            Position of the impedance. It should be one of the values
            for ``Application.AxisDir``, which are: ``"XNeg"``,
            ``"YNeg"``, ``"ZNeg"``, ``"XPos"``, ``"YPos"``, and
            ``"ZPos"``.  The default is ``"0"``.
        sourcename : str, optional
            Name of the impedance. The default is ``None``.
        resistance : float, optional
            Resistance value in ohms. The default is ``50``. If ``None``,
            this parameter is disabled.
        reactance : optional
            Reactance value in ohms. The default is ``0``. If ``None``,
            this parameter is disabled.
        is_infground : bool, optional
            Whether the impendance is an infinite ground. The default is ``False``.
        bound_on_plane : bool, optional
            Whether to create the impedance on the plane orthogonal to ``AxisDir``.
            The default is ``True``.

        Returns
        -------
        :class: `pyaedt.modules.Boundary.BoundaryObject` or bool
            Boundary object if successful. ``False`` if unsuccessful.

        Examples
        --------

        Create two boxes that will be used to create an impedance named
        named ``'ImpedanceExample'``.

        >>> box1 = hfss.modeler.primitives.create_box([0, 0, 70], [10, 10, 5],
        ...                                           "box1", "copper")
        >>> box2 = hfss.modeler.primitives.create_box([0, 0, 80], [10, 10, 5],
        ...                                           "box2", "copper")
        >>> impedance = hfss.create_impedance_between_objects("box1", "box2", hfss.AxisDir.XPos,
        ...                                                   "ImpedanceExample", 100, 50)
        pyaedt Info: Connection Correctly created

        """

        if not self.modeler.primitives.does_object_exists(startobj) or not self.modeler.primitives.does_object_exists(
                endobject):
            self._messenger.add_error_message("One or both objects do not exist. Check and retry.")
            return False
        if self.solution_type in ["DrivenModal", "DrivenTerminal", "Transient Network"]:
            sheet_name, point0, point1 = self.modeler._create_sheet_from_object_closest_edge(startobj, endobject,
                                                                                             axisdir, bound_on_plane)

            if not sourcename:
                sourcename = generate_unique_name("Imped")
            elif sourcename in self.modeler.get_boundaries_name():
                sourcename = generate_unique_name(sourcename)
            props = OrderedDict({"Objects": [sheet_name], "Resistance": str(resistance), "Reactance": str(reactance),
                                 "InfGroundPlane": is_infground})
            return self._create_boundary(sourcename, props, "Impedance")
        return False

    @aedt_exception_handler
    def create_boundary(self, boundary_type=BoundaryType.PerfectE, sheet_name=None, boundary_name="",
                        is_infinite_gnd=False):
        """Create a boundary given specific inputs.

        Parameters
        ----------
        boundary_type : str, optional
            Boundary type object. Options are ``"PerfectE"``, ``"PerfectH"``, ``"Aperture"``, and
            ``"Radiation"``. The default is ``PerfectE``.
        sheet_name : in, str, or list, optional
            Name of the sheet. It can be an integer (face ID), a string (sheet), or a list of integers
            and strings. The default is ``None``.
        boundary_name : str, optional
            Name of the boundary. The default is ``""``.
        is_infinite_gnd : bool, optional
            Whether the boundary is an infinite ground. The default is ``False``.

        Returns
        -------
        :class: `pyaedt.modules.Boundary.BoundaryObject`
            Boundary object.

        """

        props = {}
        sheet_name = self.modeler._convert_list_to_ids(sheet_name)
        if type(sheet_name) is list:
            if type(sheet_name[0]) is str:
                props["Objects"] = sheet_name
            else:
                props["Faces"] = sheet_name

        if boundary_type == self.BoundaryType.PerfectE:
            props['InfGroundPlane'] = is_infinite_gnd
            boundary_type = "PerfectE"
        elif boundary_type == self.BoundaryType.PerfectH:
            boundary_type = "PerfectH"
        elif boundary_type == self.BoundaryType.Aperture:
            boundary_type = "Aperture"
        elif boundary_type == self.BoundaryType.Radiation:
            props['IsFssReference'] = False
            props['IsForPML'] = False
            boundary_type = "Radiation"
        else:
            return None
        return self._create_boundary(boundary_name, props, boundary_type)

    @aedt_exception_handler
    def _get_reference_and_integration_points(self, sheet, axisdir):
        objID = self.modeler.oeditor.GetFaceIDs(sheet)
        face_edges = self.modeler.primitives.get_face_edges(objID[0])
        mid_points = [self.modeler.primitives.get_edge_midpoint(i) for i in face_edges]
        if axisdir < 3:
            min_point = [1e6, 1e6, 1e6]
            max_point = [-1e6, -1e6, -1e6]
            for el in mid_points:
                if el[axisdir] < min_point[axisdir]:
                    min_point = el
                if el[axisdir] > max_point[axisdir]:
                    max_point = el
        else:
            min_point = [-1e6, -1e6, -1e6]
            max_point = [1e6, 1e6, 1e6]
            for el in mid_points:
                if el[axisdir - 3] > min_point[axisdir - 3]:
                    min_point = el
                if el[axisdir - 3] < max_point[axisdir - 3]:
                    max_point = el

        refid = self.modeler.primitives.get_bodynames_from_position(min_point)
        refid.remove(sheet)
        diels = self.get_all_dielectrics_names()
        for el in refid:
            if el in diels:
                refid.remove(el)

        int_start = None
        int_stop = None
        if min_point != max_point:
            int_start = min_point
            int_stop = max_point
        return refid, int_start, int_stop

    @aedt_exception_handler
    def create_wave_port_from_sheet(self, sheet, deemb=0, axisdir=0, impedance=50, nummodes=1, portname=None,
                                    renorm=True):
        """Create a waveport on sheet objects created starting from sheets.

        Parameters
        ----------
        sheet : list
            List of input sheets to create the waveport from.
        deemb : float, optional
            Deembedding value distance in model units. The default is ``0``.
        axisdir : str, optional
            Position of the reference object. It should be one of the values for ``Application.AxisDir``,
            which are: ``"XNeg"``, ``"YNeg"``, ``"ZNeg"``, ``"XPos"``, ``"YPos"``, and ``"ZPos"``.
            The default is ``"0"``.
        impedance : float, optional
            Port impedance. The default is ``50``.
        nummodes : int, optional
            Number of modes. The default is ``1``.
        portname : str, optional
            Name of the port. The default is ``None``.
        renorm : bool, optional
            Whether to renormalize the mode. The default is ``True``.
        deembed_dist : float, optional
            Deembed distance in millimeters. The default is ``0``,
            in which case deembed is disabled.

        Returns
        -------
        list
            List of names for the ports created when successful, ``False`` otherwise.

        Examples
        --------

        Create a circle sheet that will be used to create a wave port named
        ``'WavePortFromSheet'``.

        >>> origin_position = hfss.modeler.Position(0, 0, 0)
        >>> circle = hfss.modeler.primitives.create_circle(hfss.CoordinateSystemPlane.YZPlane,
        ...                                                origin_position, 10, name="WaveCircle")
        >>> hfss.solution_type = "DrivenModal"
        >>> port = hfss.create_wave_port_from_sheet(circle, 5, hfss.AxisDir.XNeg, 40, 2,
        ...                                         "WavePortFromSheet", True)
        >>> port[0].name
        'WavePortFromSheet'

        """

        sheet = self.modeler.convert_to_selections(sheet, True)
        portnames = []
        for obj in sheet:
            refid, int_start, int_stop = self._get_reference_and_integration_points(obj, axisdir)

            if not portname:
                portname = generate_unique_name("Port")
            elif portname + ":1" in self.modeler.get_excitations_name():
                portname = generate_unique_name(portname)
            if self.solution_type == "DrivenModal":
                b = self._create_waveport_driven(
                    obj, int_start, int_stop, impedance, portname, renorm, nummodes, deemb)
                if b:
                    portnames.append(b)
            else:
                faces = self.modeler.primitives.get_object_faces(obj)
                if len(refid) > 0:
                    b = self._create_port_terminal(faces[0], refid, portname, iswaveport=True)
                    if b:
                        portnames.append(b)

                else:
                    return False
        return portnames

    @aedt_exception_handler
    def create_lumped_port_to_sheet(self, sheet_name, axisdir=0, impedance=50, portname=None,
                                    renorm=True, deemb=False, reference_object_list=[]):
        """Create a lumped port taking one sheet.

        Parameters
        ----------
        sheet_name : str
            Name of the sheet.
        axisdir : optional
            Direction of the port. It should be one of the values for ``Application.AxisDir``,
            which are: ``"XNeg"``, ``"YNeg"``, ``"ZNeg"``, ``"XPos"``, ``"YPos"``, and ``"ZPos"``.
            The default is ``"0"``.
        impedance : float, optional
            Port impedance. The default is ``50``.
        portname : str, optional
            Name of the port. The default is ``None``.
        renorm : bool, optional
            Whether to renormalize the mode. The default is ``True``.
        deemb : bool, optional
            Whether to deembed the port. The default is ``False``.
        reference_object_list : list, optional
            For a driven terminal solution only, a list of reference conductors. The default is ``[]``.

        Returns
        -------
        str
            Name of the port created when successful, ``False`` otherwise.

        Examples
        --------

        Create a rectangle sheet that will be used to create a lumped port named
        ``'LumpedPortFromSheet'``.

        >>> rectangle = hfss.modeler.primitives.create_rectangle(hfss.CoordinateSystemPlane.XYPlane,
        ...                                                      [0, 0, 0], [10, 2], name="lump_port",
        ...                                                      matname="copper")
        >>> hfss.create_lumped_port_to_sheet(rectangle.name, hfss.AxisDir.XNeg, 50,
        ...                                  "LumpedPortFromSheet", True, False)
        'LumpedPortFromSheet'

        """

        if self.solution_type in ["DrivenModal", "DrivenTerminal", "Transient Network"]:
            point0, point1 = self.modeler.primitives.get_mid_points_on_dir(sheet_name, axisdir)

            cond = self.get_all_conductors_names()
            touching = self.modeler.primitives.get_bodynames_from_position(point0)
            listcond = []
            for el in touching:
                if el in cond:
                    listcond.append(el)

            if not portname:
                portname = generate_unique_name("Port")
            elif portname + ":1" in self.modeler.get_excitations_name():
                portname = generate_unique_name(portname)
            if self.solution_type == "DrivenModal":
                self._create_lumped_driven(sheet_name, point0, point1,
                                           impedance, portname, renorm, deemb)
            else:
                if not reference_object_list:
                    cond = self.get_all_conductors_names()
                    touching = self.modeler.primitives.get_bodynames_from_position(point0)
                    reference_object_list = []
                    for el in touching:
                        if el in cond:
                            reference_object_list.append(el)
                faces = self.modeler.primitives.get_object_faces(sheet_name)
                self._create_port_terminal(
                    faces[0], reference_object_list, portname, iswaveport=False)
            return portname
        return False

    @aedt_exception_handler
    def assig_voltage_source_to_sheet(self, sheet_name, axisdir=0, sourcename=None):
        """Create a voltage source taking one sheet.

        .. deprecated:: 0.4.0
           Use :func:`Hfss.assign_voltage_source_to_sheet` instead.

        """

        warnings.warn('`assig_voltage_source_to_sheet is deprecated`. Use `assign_voltage_source_to_sheet` instead.',
                      DeprecationWarning)
        self.assign_voltage_source_to_sheet(sheet_name, axisdir=0, sourcename=None)

    @aedt_exception_handler
    def assign_voltage_source_to_sheet(self, sheet_name, axisdir=0, sourcename=None):
        """Create a voltage source taking one sheet.

        Parameters
        ----------
        sheet_name : str
            Name of the sheet to apply the boundary to.
        axisdir : str, optional
            Position of the voltage source. It should be one of the values for ``Application.AxisDir``,
            which are: ``"XNeg"``, ``"YNeg"``, ``"ZNeg"``, ``"XPos"``, ``"YPos"``, and ``"ZPos"``.
            The default is ``"0"``.
        sourcename : str, optional
            Name of the source. The default is ``None``.

        Returns
        -------
        str
            Name of the source created when successful, ``False`` otherwise.

        Examples
        --------

        Create a sheet and assign to it some voltage.

        >>> sheet = hfss.modeler.primitives.create_rectangle(hfss.CoordinateSystemPlane.XYPlane,
        ...                                                  [0, 0, -70], [10, 2], name="VoltageSheet",
        ...                                                  matname="copper")
        >>> hfss.assign_voltage_source_to_sheet(sheet.name, hfss.AxisDir.XNeg, "VoltageSheetExample")
        'VoltageSheetExample'

        """

        if self.solution_type in ["DrivenModal", "DrivenTerminal", "Transient Network"]:
            point0, point1 = self.modeler.primitives.get_mid_points_on_dir(sheet_name, axisdir)
            if not sourcename:
                sourcename = generate_unique_name("Voltage")
            elif sourcename + ":1" in self.modeler.get_excitations_name():
                sourcename = generate_unique_name(sourcename)
            status = self.create_source_excitation(
                sheet_name, point0, point1, sourcename, sourcetype="Voltage")
            if status:
                return sourcename
        return False

    @aedt_exception_handler
    def assign_current_source_to_sheet(self, sheet_name, axisdir=0, sourcename=None):
        """Create a current source taking one sheet.

        Parameters
        ----------
        sheet_name : str
            Name of the sheet to apply the boundary to.
        axisdir : str, optional
            Position of the current source. It should be one of the values for ``Application.AxisDir``,
            which are: ``"XNeg"``, ``"YNeg"``, ``"ZNeg"``, ``"XPos"``, ``"YPos"``, and ``"ZPos"``.
            The default is ``"0"``.
        sourcename : str, optional
            Name of the source. The default is ``None``.

        Returns
        -------
        str
            Name of the source created when successful, ``False`` otherwise.

        Examples
        --------

        Create a sheet and assign to it some current.

        >>> sheet = hfss.modeler.primitives.create_rectangle(hfss.CoordinateSystemPlane.XYPlane, [0, 0, -50],
        ...                                                  [5, 1], name="CurrentSheet", matname="copper")
        >>> hfss.assign_current_source_to_sheet(sheet.name, hfss.AxisDir.XNeg, "CurrentSheetExample")
        'CurrentSheetExample'

        """

        if self.solution_type in ["DrivenModal", "DrivenTerminal", "Transient Network"]:
            point0, point1 = self.modeler.primitives.get_mid_points_on_dir(sheet_name, axisdir)
            if not sourcename:
                sourcename = generate_unique_name("Current")
            elif sourcename + ":1" in self.modeler.get_excitations_name():
                sourcename = generate_unique_name(sourcename)
            status = self.create_source_excitation(
                sheet_name, point0, point1, sourcename, sourcetype="Current")
            if status:
                return sourcename
        return False

    @aedt_exception_handler
    def assign_perfecte_to_sheets(self, sheet_list, sourcename=None, is_infinite_gnd=False):
        """Create a Perfect E taking one sheet.

        Parameters
        ----------
        sheet_list : str or list
            Name of the sheet or list to apply the boundary to.
        sourcename : str, optional
            Name of the Perfect E source. The default is ``None``.
        is_infinite_gnd : bool, optional
            Whether the Perfect E is an infinite ground. The default is ``False``.

        Returns
        -------
        :class: `pyaedt.modules.Boundary.BoundaryObject`
            Boundary object.

        Examples
        --------

        Create a sheet and use it to create a Perfect E.

        >>> sheet = hfss.modeler.primitives.create_rectangle(hfss.CoordinateSystemPlane.XYPlane, [0, 0, -90],
        ...                                                  [10, 2], name="PerfectESheet", matname="Copper")
        >>> perfect_e_from_sheet = hfss.assign_perfecte_to_sheets(sheet.name, "PerfectEFromSheet")
        >>> type(perfect_e_from_sheet)
        <class 'pyaedt.modules.Boundary.BoundaryObject'>

        """

        if self.solution_type in ["DrivenModal", "DrivenTerminal", "Transient Network", "SBR+"]:
            if not sourcename:
                sourcename = generate_unique_name("PerfE")
            elif sourcename in self.modeler.get_boundaries_name():
                sourcename = generate_unique_name(sourcename)
            return self.create_boundary(self.BoundaryType.PerfectE, sheet_list, sourcename, is_infinite_gnd)
        return None

    @aedt_exception_handler
    def assign_perfecth_to_sheets(self, sheet_list, sourcename=None):
        """Assign a Perfect H to sheets.

        Parameters
        ----------
        sheet_list : list
            List of sheets to apply the boundary to.
        sourcename : str, optional
            Perfect H name. The default is ``None``.

        Returns
        -------
        :class: `pyaedt.modules.Boundary.BoundaryObject`
            Boundary object.

        Examples
        --------

        Create a sheet and use it to create a Perfect H.

        >>> sheet = hfss.modeler.primitives.create_rectangle(hfss.CoordinateSystemPlane.XYPlane, [0, 0, -90],
        ...                                                  [10, 2], name="PerfectHSheet", matname="Copper")
        >>> perfect_h_from_sheet = hfss.assign_perfecth_to_sheets(sheet.name, "PerfectHFromSheet")
        >>> type(perfect_h_from_sheet)
        <class 'pyaedt.modules.Boundary.BoundaryObject'>

        """

        if self.solution_type in ["DrivenModal", "DrivenTerminal", "Transient Network", "SBR+"]:

            if not sourcename:
                sourcename = generate_unique_name("PerfH")
            elif sourcename in self.modeler.get_boundaries_name():
                sourcename = generate_unique_name(sourcename)
            return self.create_boundary(self.BoundaryType.PerfectH, sheet_list, sourcename)
        return None

    @aedt_exception_handler
    def assign_lumped_rlc_to_sheet(self, sheet_name, axisdir=0, sourcename=None, rlctype="Parallel",
                                   Rvalue=None, Lvalue=None, Cvalue=None):
        """Create a lumped RLC taking one sheet.

        Parameters
        ----------
        sheet_name : str
            Name of the sheet to apply the boundary to.
        axisdir : str, optional
            Position of the port. It should be one of the values for ``Application.AxisDir``,
            which are: ``"XNeg"``, ``"YNeg"``, ``"ZNeg"``, ``"XPos"``, ``"YPos"``, and ``"ZPos"``.
            The default is ``"0"``.
        sourcename : str, optional
            Lumped RLC name. The default is ``None``.
        rlctype : str, optional
            Type of the RLC. Options are ``"Parallel"`` or ``"Series"``. The default is ``"Parallel"``.
        Rvalue : float, optional
            Resistance value in ohms. The default is ``None``, in which
            case this parameter is disabled.
        Lvalue : optional
            Inductance value in H. The default is ``None``, in which
            case this parameter is disabled.
        Cvalue : optional
            Capacitance value in F. The default is ``None``, in which
            case this parameter is disabled.

        Returns
        -------
        :class: `pyaedt.modules.Boundary.BoundaryObject`
            Boundary object if successful. ``False`` if unsuccessful.

        Examples
        --------

        Create a sheet and use it to create a lumped RLC.

        >>> sheet = hfss.modeler.primitives.create_rectangle(hfss.CoordinateSystemPlane.XYPlane,
        ...                                                  [0, 0, -90], [10, 2], name="RLCSheet",
        ...                                                  matname="Copper")
        >>> lumped_rlc_to_sheet = hfss.assign_lumped_rlc_to_sheet(sheet.name, hfss.AxisDir.XPos,
        ...                                                       Rvalue=50, Lvalue=1e-9,
        ...                                                       Cvalue=1e-6)
        >>> type(lumped_rlc_to_sheet)
        <class 'pyaedt.modules.Boundary.BoundaryObject'>

        """

        if self.solution_type in ["DrivenModal", "DrivenTerminal", "Transient Network", "SBR+"] and (
                Rvalue or Lvalue or Cvalue):
            point0, point1 = self.modeler.primitives.get_mid_points_on_dir(sheet_name, axisdir)

            if not sourcename:
                sourcename = generate_unique_name("Lump")
            elif sourcename in self.modeler.get_boundaries_name():
                sourcename = generate_unique_name(sourcename)
            start = [str(i) + self.modeler.primitives.model_units for i in point0]
            stop = [str(i) + self.modeler.primitives.model_units for i in point1]
            props = OrderedDict()
            props["Objects"] = [sheet_name]
            props["CurrentLine"] = OrderedDict({"Start": start, "End": stop})
            props["RLC Type"] = [rlctype]
            if Rvalue:
                props["UseResist"] = True
                props["Resistance"] = str(Rvalue) + "ohm"
            if Lvalue:
                props["UseInduct"] = True
                props["Inductance"] = str(Lvalue) + "H"
            if Cvalue:
                props["UseCap"] = True
                props["Capacitance"] = str(Cvalue) + "F"
            return self._create_boundary(sourcename, props, "LumpedRLC")
        return False

    @aedt_exception_handler
    def assign_impedance_to_sheet(self, sheet_name, sourcename=None, resistance=50, reactance=0, is_infground=False):
        """Create an impedance taking one sheet.

        Parameters
        ----------
        sheet_name : str
            Name of the sheet to apply the boundary to.
        sourcename : str, optional
            Name of the impedance. The default is ``None``.
        resistance : optional
            Resistance value in ohms. The default is ``50``. If ``None``,
            this parameter is disabled.
        reactance : optional
            Reactance value in ohms. The default is ``0``. If ``None``,
            this parameter is disabled.
        is_infground : bool, optional
            Whether the impedance is an infinite ground. The default is ``False``.

        Returns
        -------
        :class: `pyaedt.modules.Boundary.BoundaryObject`
            Boundary object if successful. ``False`` if unsuccessful.

        Examples
        --------

        Create a sheet and use it to create an impedance.

        >>> sheet = hfss.modeler.primitives.create_rectangle(hfss.CoordinateSystemPlane.XYPlane,
        ...                                                  [0, 0, -90], [10, 2], name="ImpedanceSheet",
        ...                                                  matname="Copper")
        >>> impedance_to_sheet = hfss.assign_impedance_to_sheet(sheet.name, "ImpedanceFromSheet", 100, 50)
        >>> type(impedance_to_sheet)
        <class 'pyaedt.modules.Boundary.BoundaryObject'>

        """

        if self.solution_type in ["DrivenModal", "DrivenTerminal", "Transient Network"]:

            if not sourcename:
                sourcename = generate_unique_name("Imped")
            elif sourcename in self.modeler.get_boundaries_name():
                sourcename = generate_unique_name(sourcename)
            props = OrderedDict({"Objects": [sheet_name], "Resistance": str(resistance), "Reactance": str(reactance),
                                 "InfGroundPlane": is_infground})
            return self._create_boundary(sourcename, props, "Impedance")
        return False

    @aedt_exception_handler
    def create_circuit_port_from_edges(self, edge_signal, edge_gnd, port_name="",
                                       port_impedance="50",
                                       renormalize=False, renorm_impedance="50",
                                       deembed=False):
        """Create a circuit port from two edges.

        The integration line is from edge 2 to edge 1.

        Parameters
        ----------
        edge_signal : int
            Edge ID of the signal.
        edge_gnd : int
            Edge ID of the ground.
        port_name : str, optional
            Name of the port. The default is ``""``.
        port_impedance : int, str, or float, optional
            Impedance. The default is ``"50"``. You can also
            enter a string that looks like this: ``"50+1i*55"``.
        renormalize : bool, optional
            Whether to renormalize the mode. The default is ``False``.
            This parameter is ignored for a driven terminal.
        renorm_impedance :  str, optional
            Impedance. The default is ``50``
        deembed : bool. optional
            Whether to deembed the port. The default is ``False``

        Returns
        -------
        str
            Name of the port created when successful, ``False`` otherwise.

        Examples
        --------

        Create two rectangles in the XY plane.
        Select the first edge of each rectangle created previously.
        Create a circuit port from the first edge of the first rectangle
        toward the first edge of the second rectangle.

        >>> plane = hfss.CoordinateSystemPlane.XYPlane
        >>> rectangle1 = hfss.modeler.primitives.create_rectangle(plane, [10, 10, 10], [10, 10],
        ...                                                       name="rectangle1_for_port")
        >>> edges1 = hfss.modeler.primitives.get_object_edges(rectangle1.id)
        >>> first_edge = edges1[0]
        >>> rectangle2 = hfss.modeler.primitives.create_rectangle(plane, [30, 10, 10], [10, 10],
        ...                                                       name="rectangle2_for_port")
        >>> edges2 = hfss.modeler.primitives.get_object_edges(rectangle2.id)
        >>> second_edge = edges2[0]
        >>> hfss.solution_type = "DrivenModal"
        >>> hfss.create_circuit_port_from_edges(first_edge, second_edge, port_name="PortExample",
        ...                                     port_impedance=50.1, renormalize=False,
        ...                                     renorm_impedance="50")
        'PortExample'

        """

        edge_list = [edge_signal, edge_gnd]
        if not port_name:
            port_name = generate_unique_name("Port")
        elif port_name + ":1" in self.modeler.get_excitations_name():
            port_name = generate_unique_name(port_name)

        result = self._create_circuit_port(edge_list, port_impedance, port_name, renormalize,
                                           deembed, renorm_impedance=renorm_impedance)
        if result:
            return port_name
        return False

    @aedt_exception_handler
    def edit_source(self, portandmode, powerin, phase="0deg"):
        """Set up the power loaded to the filter for thermal analysis.

        Parameters
        ----------
        portandmode : str
            Port name and mode, such as ``"Port1:1"``.
        powerin : str
            Power in Watts or the project variable to be put as stored energy in the project.
        phase : str, optional
            The default is ``"0deg"``.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.

        Examples
        --------

        Create a circle sheet and use it to create a wave port.
        Set up the thermal power for the port created above.

        >>> sheet = hfss.modeler.primitives.create_circle(hfss.CoordinateSystemPlane.YZPlane,
        ...                                               [-20, 0, 0], 10,
        ...                                               name="sheet_for_source")
        >>> hfss.solution_type = "DrivenModal"
        >>> wave_port = hfss.create_wave_port_from_sheet(sheet, 5, hfss.AxisDir.XNeg, 40,
        ...                                              2, "SheetWavePort", True)
        >>> hfss.edit_source("SheetWavePort" + ":1", "10W")
        pyaedt Info: Setting up power to Eigenmode 10W
        True

        """

        self._messenger.add_info_message("Setting up power to Eigenmode " + powerin)
        if self.solution_type != "Eigenmode":
            self.osolution.EditSources([["IncludePortPostProcessing:=", True, "SpecifySystemPower:=", False],
                                        ["Name:=", portandmode, "Magnitude:=", powerin, "Phase:=", phase]])
        else:
            self.osolution.EditSources(
                [["FieldType:=", "EigenStoredEnergy"], ["Name:=", "Modes", "Magnitudes:=", [powerin]]])
        return True

    @aedt_exception_handler
    def thicken_port_sheets(self, inputlist, value, internalExtr=True, internalvalue=1):
        """Create thickened sheets over a list of input port sheets.

        Parameters
        ----------
        inputlist : list
            List of the sheets to thicken.
        value :
            Value in millimeters for thickening the faces.
        internalExtr : bool, optional
            Whether to extrude the sheets internally (vgoing into the model).
            The default is ``True``.
        internalvalue : optional
            Value in millimeters for thickening the sheets internally if ``internalExtr=True``.
            The default is ``1``.

        Returns
        -------
        list
            List of the port IDs where thickened sheets were created.

        Examples
        --------

        Create a circle sheet and use it to create a wave port.
        Set the thickness of this circle sheet to ``"2 mm"``.

        >>> sheet_for_thickness = hfss.modeler.primitives.create_circle(hfss.CoordinateSystemPlane.YZPlane,
        ...                                                             [60, 60, 60], 10,
        ...                                                             name="SheetForThickness")
        >>> port_for_thickness = hfss.create_wave_port_from_sheet(sheet_for_thickness, 5, hfss.AxisDir.XNeg,
        ...                                                       40, 2, "WavePortForThickness", True)
        >>> hfss.thicken_port_sheets(["SheetForThickness"], 2)
        pyaedt Info: done
        {}

        """

        tol = 1e-6
        ports_ID = {}
        aedt_bounding_box = self.modeler.primitives.get_model_bounding_box()
        directions = {}
        for el in inputlist:
            objID = self.modeler.oeditor.GetFaceIDs(el)
            faceCenter = self.modeler.oeditor.GetFaceCenter(int(objID[0]))
            directionfound = False
            l = 10
            while not directionfound:
                self.modeler.oeditor.ThickenSheet(
                    [
                        "NAME:Selections",
                        "Selections:=", el,
                        "NewPartsModelFlag:=", "Model"
                    ],
                    [
                        "NAME:SheetThickenParameters",
                        "Thickness:=", str(l) + "mm",
                        "BothSides:=", False
                    ])
                # aedt_bounding_box2 = self._oeditor.GetModelBoundingBox()
                aedt_bounding_box2 = self.modeler.primitives.get_model_bounding_box()
                self._odesign.Undo()
                if aedt_bounding_box != aedt_bounding_box2:
                    directions[el] = "External"
                    directionfound = True
                self.modeler.oeditor.ThickenSheet(
                    [
                        "NAME:Selections",
                        "Selections:=", el,
                        "NewPartsModelFlag:=", "Model"
                    ],
                    [
                        "NAME:SheetThickenParameters",
                        "Thickness:=", "-" + str(l) + "mm",
                        "BothSides:=", False
                    ])
                # aedt_bounding_box2 = self._oeditor.GetModelBoundingBox()
                aedt_bounding_box2 = self.modeler.primitives.get_model_bounding_box()

                self._odesign.Undo()

                if aedt_bounding_box != aedt_bounding_box2:
                    directions[el] = "Internal"
                    directionfound = True
                else:
                    l = l + 10
        for el in inputlist:
            objID = self.modeler.oeditor.GetFaceIDs(el)
            maxarea = 0
            for f in objID:
                faceArea = self.modeler.primitives.get_face_area(int(f))
                if faceArea > maxarea:
                    maxarea = faceArea
                    faceCenter = self.modeler.oeditor.GetFaceCenter(int(f))
            if directions[el] == "Internal":
                self.modeler.oeditor.ThickenSheet(
                    [
                        "NAME:Selections",
                        "Selections:=", el,
                        "NewPartsModelFlag:=", "Model"
                    ],
                    [
                        "NAME:SheetThickenParameters",
                        "Thickness:=", "-" + str(value) + "mm",
                        "BothSides:=", False
                    ])
            else:
                self.modeler.oeditor.ThickenSheet(
                    [
                        "NAME:Selections",
                        "Selections:=", el,
                        "NewPartsModelFlag:=", "Model"
                    ],
                    [
                        "NAME:SheetThickenParameters",
                        "Thickness:=", str(value) + "mm",
                        "BothSides:=", False
                    ])
            if "Vacuum" in el:
                newfaces = self.modeler.oeditor.GetFaceIDs(el)
                for f in newfaces:
                    try:
                        fc2 = self.modeler.oeditor.GetFaceCenter(f)
                        fc2 = [float(i) for i in fc2]
                        fa2 = self.modeler.primitives.get_face_area(int(f))
                        faceoriginal = [float(i) for i in faceCenter]
                        # dist = mat.sqrt(sum([(a*a-b*b) for a,b in zip(faceCenter, fc2)]))
                        if abs(fa2 - maxarea) < tol ** 2 and (abs(faceoriginal[2] - fc2[2]) > tol or abs(
                                faceoriginal[1] - fc2[1]) > tol or abs(faceoriginal[0] - fc2[0]) > tol):
                            ports_ID[el] = int(f)

                        # if (abs(faceoriginal[0] - fc2[0]) < tol and abs(faceoriginal[1] - fc2[1]) < tol and abs(
                        #         faceoriginal[2] - fc2[2]) > tol) or (
                        #         abs(faceoriginal[0] - fc2[0]) < tol and abs(faceoriginal[1] - fc2[1]) > tol and abs(
                        #         faceoriginal[2] - fc2[2]) < tol) or (
                        #         abs(faceoriginal[0] - fc2[0]) > tol and abs(faceoriginal[1] - fc2[1]) < tol and abs(
                        #         faceoriginal[2] - fc2[2]) < tol):
                        #     ports_ID[el] = int(f)
                    except:
                        pass
            if internalExtr:
                objID2 = self.modeler.oeditor.GetFaceIDs(el)
                for fid in objID2:
                    try:
                        faceCenter2 = self.modeler.oeditor.GetFaceCenter(int(fid))
                        if faceCenter2 == faceCenter:
                            self.modeler.oeditor.MoveFaces(
                                [
                                    "NAME:Selections",
                                    "Selections:=", el,
                                    "NewPartsModelFlag:=", "Model"
                                ],
                                [
                                    "NAME:Parameters",
                                    [
                                        "NAME:MoveFacesParameters",
                                        "MoveAlongNormalFlag:=", True,
                                        "OffsetDistance:=", str(internalvalue) + "mm",
                                        "MoveVectorX:=", "0mm",
                                        "MoveVectorY:=", "0mm",
                                        "MoveVectorZ:=", "0mm",
                                        "FacesToMove:=", [int(fid)]
                                    ]
                                ])
                    except:
                        self._messenger.add_debug_message("done")
                        # self.modeler_oproject.ClearMessages()
        return ports_ID

    @aedt_exception_handler
    def validate_full_design(self, dname=None, outputdir=None, ports=None):
        """Validate a design based on an expected value and save information to the log file.

        Parameters
        ----------
        dname : str,  optional
            Name of the design to validate. The default is ``None``, in which case
            the current design is used.
        outputdir : str, optional
            Directory to save the log file to. The default is ``None``,
            in which case the current project path is used.
        ports : int, optional
            Number of excitations (sum of modes) that is expected. The default is ``None``.

        Returns
        -------
        list
            List of all the validation information for later use.
        bool
            Indicates if the validation was successful or not.

        Examples
        --------

        Validate the current design and save the log file into
        the current project directory.

        >>> validation = hfss.validate_full_design()
        pyaedt Info: Design Validation Checks
        >>> validation[1]
        False

        """

        self._messenger.add_debug_message("Design Validation Checks")
        validation_ok = True
        val_list = []
        if not dname:
            dname = self.design_name
        if not outputdir:
            outputdir = self.project_path
        pname = self.project_name
        validation_log_file = os.path.join(outputdir, pname + "_" + dname + "_validation.log")

        # Desktop Messages
        msg = "Desktop Messages:"
        val_list.append(msg)
        temp_msg = list(self._desktop.GetMessages(pname, dname, 0))
        if temp_msg:
            temp2_msg = [i.strip('Project: ' + pname + ', Design: ' + \
                                 dname + ', ').strip('\r\n') for i in temp_msg]
            val_list.extend(temp2_msg)

        # Run design validation and write out the lines to the log.
        temp_val_file = os.path.join(os.environ['TEMP'], "\\val_temp.log")
        simple_val_return = self.validate_simple(temp_val_file)
        if simple_val_return == 1:
            msg = "Design validation check PASSED."
        elif simple_val_return == 0:
            msg = "Design validation check ERROR."
            validation_ok = False
        val_list.append(msg)
        msg = "Design Validation Messages:"
        val_list.append(msg)
        if os.path.isfile(temp_val_file):
            with open(temp_val_file, 'r') as df:
                temp = df.read().splitlines()
                val_list.extend(temp)
            os.remove(temp_val_file)
        else:
            msg = "** No design validation file is found. **"
            self._messenger.add_debug_message(msg)
            val_list.append(msg)
        msg = "** End of design validation messages. **"
        val_list.append(msg)

        # Find the excitations and check or list them out
        msg = "Excitations Check:"
        val_list.append(msg)
        if self.solution_type != 'Eigenmode':
            detected_excitations = self.modeler.get_excitations_name()
            if ports:
                if self.solution_type == 'DrivenTerminal':
                    # For each port, there is terminal and reference excitations.
                    ports_t = ports * 2
                else:
                    ports_t = ports
                if ports_t != len(detected_excitations):
                    msg = "** Port number error. Check the model. **"
                    self._messenger.add_error_message(msg)
                    val_list.append(msg)
                    validation_ok = False
                else:
                    msg1 = "Solution type: " + str(self.solution_type)
                    msg2 = "Ports Requested: " + str(ports)
                    msg3 = "Defined excitations number: " + str(len(detected_excitations))
                    msg4 = "Defined excitations names: " + str(detected_excitations)
                    val_list.append(msg1)
                    val_list.append(msg2)
                    val_list.append(msg3)
                    val_list.append(msg4)
        else:
            msg = "Eigen model is detected. No excitatons are defined."
            self._messenger.add_debug_message(msg)
            val_list.append(msg)

        # Find the number of analysis setups and output the info.
        msg = "Analysis Setup Messages:"
        val_list.append(msg)
        setups = list(self.oanalysis.GetSetups())
        if setups:
            msg = "Detected setup and sweep: "
            val_list.append(msg)
            for setup in setups:
                msg = str(setup)
                val_list.append(msg)
                if self.solution_type != 'EigenMode':
                    sweepsname = self.oanalysis.GetSweeps(setup)
                    if sweepsname:
                        for sw in sweepsname:
                            msg = ' |__ ' + sw
                            val_list.append(msg)
        else:
            msg = 'No setup is detected.'
            val_list.append(msg)

        with open(validation_log_file, "w") as f:
            for item in val_list:
                f.write("%s\n" % item)
        return val_list, validation_ok  # Return all the information in a list for later use.

    @aedt_exception_handler
    def create_scattering(self, plot_name="S Parameter Plot Nominal", sweep_name=None, port_names=None, port_excited=None,
                          variations=None):
        """Create a scattering report.

        Parameters
        ----------
        PlotName : str, optional
             Name of the plot. The default is ``"S Parameter Plot Nominal"``.
        sweep_name : str, optional
             Name of the sweep. The default is ``None``.
        port_names : list, optional
             List of port names. The default is ``None``.
        port_excited : list or str, optional
             The default is ``None``.
        variations : str, optional
             The default is ``None``.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.

        Examples
        --------

        Create a scattering named ``"S Parameter Plot Nominal"`` using
        the default parameters.

        >>> hfss.create_scattering()
        True

        """

        Families = ["Freq:=", ["All"]]
        if variations:
            Families += variations
        else:
            Families += self.get_nominal_variation()
        if not sweep_name:
            sweep_name = self.existing_analysis_sweeps[1]
        elif sweep_name not in self.existing_analysis_sweeps:
            self._messenger.add_error_message(
                "Setup {} doesn't exist in the Setup list.".format(sweep_name))
            return False
        if not port_names:
            port_names = self.modeler.get_excitations_name()
        full_matrix = False
        if not port_excited:
            port_excited = port_names
            full_matrix = True
        if type(port_names) is str:
            port_names = [port_names]
        if type(port_excited) is str:
            port_excited = [port_excited]
        list_y = []
        for p in list(port_names):
            for q in list(port_excited):
                if not full_matrix:
                    list_y.append("dB(S(" + p + "," + q + "))")
                elif port_excited.index(q) >= port_names.index(p):
                    list_y.append("dB(S(" + p + "," + q + "))")

        Trace = ["X Component:=", "Freq", "Y Component:=", list_y]
        solution_data = ""
        if self.solution_type == "DrivenModal":
            solution_data = "Modal Solution Data"
        elif self.solution_type == "DrivenTerminal":
            solution_data = "Terminal Solution Data"
        if solution_data != "":
            # run CreateReport function

            self.post.oreportsetup.CreateReport(
                plot_name,
                solution_data,
                "Rectangular Plot",
                sweep_name,
                ["Domain:=", "Sweep"],
                Families,
                Trace,
                [])
            return True
        return False

    @aedt_exception_handler
    def create_qfactor_report(self, project_dir, outputlist, setupname, plotname, Xaxis="X"):
        """Export a CSV file of the EigenQ plot.

        Parameters
        ----------
        project_dir : str
            Directory to export the CSV file to.
        outputlist : list
            Output quantity, which in this case is the Q-factor.
        setupname : str
            Name of the setup to generate the report from.
        plotname : str
            Name of the plot.
        Xaxis : str, optional
            Value for the X axis. The default is ``"X"``.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.

        """
        npath = os.path.normpath(project_dir)

        # Setup arguments list for createReport function
        args = [Xaxis + ":=", ["All"]]
        args2 = ["X Component:=", Xaxis, "Y Component:=", outputlist]

        self.post.post_oreport_setup.CreateReport(plotname, "Eigenmode Parameters", "Rectangular Plot",
                                                  setupname + " : LastAdaptive", [], args, args2, [])
        return True

    @aedt_exception_handler
    def export_touchstone(self, solutionname, sweepname, filename=None, variation=[], variations_value=[]):
        """Export the Touchstone file to a local folder.

        Parameters
        ----------
        solutionname : str
             Name of the solution that has been solved.
        sweepname : str
             Name of the sweep that has been solved.
        filename : str, optional
             Full path and name for the output file. The default is ``None``.
        variation : list, optional
             List of all parameter variations. For example, ``["$AmbientTemp", "$PowerIn"]``.
             The default is ``[]``.
        variations_value : list, optional
             List of all parameter variation values. For example, ``["22cel", "100"]``.
             The default is ``[]``.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.
        """

        # Normalize the save path
        if not filename:
            appendix = ""
            for v, vv in zip(variation, variations_value):
                appendix += "_" + v + vv.replace("\'", "")
            ext = ".S" + str(self.oboundary.GetNumExcitations()) + "p"
            filename = os.path.join(self.project_path, solutionname + \
                                    "_" + sweepname + appendix + ext)
        else:
            filename = filename.replace("//", "/").replace("\\", "/")
        print("Exporting Touchstone " + filename)
        DesignVariations = ""
        i = 0
        for el in variation:
            DesignVariations += str(variation[i]) + "=\'" + \
                                    str(variations_value[i].replace("\'", "")) + "\' "
            i += 1
            # DesignVariations = "$AmbientTemp=\'22cel\' $PowerIn=\'100\'"
        # array containing "SetupName:SolutionName" pairs (note that setup and solution are separated by a colon)
        SolutionSelectionArray = [solutionname + ":" + sweepname]
        # 2=tab delimited spreadsheet (.tab), 3= touchstone (.sNp), 4= CitiFile (.cit),
        # 7=Matlab (.m), 8=Terminal Z0 spreadsheet
        FileFormat = 3
        OutFile = filename  # full path of output file
        # array containin the frequencies to export, use ["all"] for all frequencies
        FreqsArray = ["all"]
        DoRenorm = True  # perform renormalization before export
        RenormImped = 50  # Real impedance value in ohm, for renormalization
        DataType = "S"  # Type: "S", "Y", or "Z" matrix to export
        Pass = -1  # The pass to export. -1 = export all passes.
        ComplexFormat = 0  # 0=Magnitude/Phase, 1=Real/Immaginary, 2=dB/Phase
        DigitsPrecision = 15  # Touchstone number of digits precision
        IncludeGammaImpedance = True  # Include Gamma and Impedance in comments
        NonStandardExtensions = False  # Support for non-standard Touchstone extensions

        self.osolution.ExportNetworkData(DesignVariations, SolutionSelectionArray, FileFormat,
                                         OutFile, FreqsArray, DoRenorm, RenormImped, DataType, Pass,
                                         ComplexFormat, DigitsPrecision, False, IncludeGammaImpedance,
                                         NonStandardExtensions)
        return True

    @aedt_exception_handler
    def set_export_touchstone(self, activate, export_dir=""):
        """Set automatic export of the Touchstone file after simulation.

        Parameters
        ----------
        activate : bool
            Whether to export the Touchstone file after the simulation finishes.
        export_dir : str, optional
            Directory to export the Touchstone file to. The default is ``""``.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.

        """
        settings = []
        if activate:
            settings.append("NAME:Design Settings Data")
            settings.append("Export After Simulation:=")
            settings.append(True)
            settings.append("Export Dir:=")
            settings.append(export_dir)
        elif not activate:
            settings.append("NAME:Design Settings Data")
            settings.append("Export After Simulation:=")
            settings.append(False)
        self.odesign.SetDesignSettings(settings)
        return True

    @aedt_exception_handler
    def assign_radiation_boundary_to_objects(self, obj_names, boundary_name=""):
        """Assign a radiation boundary to one or more objects (usually airbox objects).

        Parameters
        ----------
        obj_names : str or list
             One or more object names.
        boundary_name : str, optional
             Name of the boundary. The default is ``""``.

        Returns
        -------
        :class: `pyaedt.modules.Boundary.BoundaryObject`
            Boundary object.

        Examples
        --------

        Create a box and assign a radiation boundary to it.

        >>> radiation_box = hfss.modeler.primitives.create_box([0, -200, -200], [200, 200, 200],
        ...                                                    name="Radiation_box")
        >>> radiation = hfss.assign_radiation_boundary_to_objects("Radiation_box")
        >>> type(radiation)
        <class 'pyaedt.modules.Boundary.BoundaryObject'>

        """

        object_list = self.modeler.convert_to_selections(obj_names, return_list=True)
        if boundary_name:
            rad_name = boundary_name
        else:
            rad_name = generate_unique_name("Rad_")
        return self.create_boundary(self.BoundaryType.Radiation, object_list, rad_name)

    @aedt_exception_handler
    def assign_radiation_boundary_to_faces(self, faces_id, boundary_name=""):
        """Assign a radiation boundary to one or more faces.

        Parameters
        ----------
        faces_id :
            Face ID to assign the boundary condition to.
        boundary_name : str, optional
            Name of the boundary. The default is ``""``.

        Returns
        -------
        :class: `pyaedt.modules.Boundary.BoundaryObject`
            Boundary object.

        Examples
        --------

        Create a box. Select the faces of this box and assign a radiation
        boundary to them.

        >>> radiation_box = hfss.modeler.primitives.create_box([0 , -100, 0], [200, 200, 200],
        ...                                                    name="RadiationForFaces")
        >>> ids = [i.id for i in hfss.modeler.primitives["RadiationForFaces"].faces]
        >>> radiation = hfss.assign_radiation_boundary_to_faces(ids)
        >>> type(radiation)
        <class 'pyaedt.modules.Boundary.BoundaryObject'>

        """

        if type(faces_id) is not list:
            faces_list = [int(faces_id)]
        else:
            faces_list = [int(i) for i in faces_id]
        if boundary_name:
            rad_name = boundary_name
        else:
            rad_name = generate_unique_name("Rad_")
        return self.create_boundary(self.BoundaryType.Radiation, faces_list, rad_name)
