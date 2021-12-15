"""This module contains these classes: ``Hfss`` and ``BoundaryType``."""
from __future__ import absolute_import
import os
import warnings
import math
import tempfile

from pyaedt.application.Analysis3D import FieldAnalysis3D
from pyaedt.modeler.GeometryOperators import GeometryOperators
from pyaedt.modules.Boundary import BoundaryObject, NativeComponentObject, FarFieldSetup
from pyaedt.generic.general_methods import generate_unique_name, aedt_exception_handler
from collections import OrderedDict
from pyaedt.modeler.actors import Radar
from pyaedt.generic.constants import INFINITE_SPHERE_TYPE


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
    specified_version : str, optional
        Version of AEDT to use. The default is ``None``, in which case
        the active version or latest installed version is used.
        This parameter is ignored when script is launched within AEDT.
    NG : bool, optional
        Whether to run AEDT in the non-graphical mode. The default
        is ``False``, in which case AEDT is launched in the graphical mode.
        This parameter is ignored when script is launched within AEDT.
    new_desktop_session : bool, optional
        Whether to launch an instance of AEDT in a new thread, even if
        another instance of the ``specified_version`` is active on the
        machine. The default is ``True``. This parameter is ignored when
        script is launched within AEDT.
    close_on_exit : bool, optional
        Whether to release AEDT on exit. The default is ``False``.
    student_version : bool, optional
        Whether to open the AEDT student version. The default is
        ``False``. This parameter is ignored when script is launched
        within AEDT.

    Examples
    --------

    Create an instance of HFSS and connect to an existing HFSS
    design or create a new HFSS design if one does not exist.

    >>> from pyaedt import Hfss
    >>> hfss = Hfss()
    pyaedt info: No project is defined...
    pyaedt info: Active design is set to...

    Create an instance of HFSS and link to a project named
    ``HfssProject``. If this project does not exist, create one with
    this name.

    >>> hfss = Hfss("HfssProject")
    pyaedt info: Project HfssProject has been created.
    pyaedt info: No design is present. Inserting a new design.
    pyaedt info: Added design ...

    Create an instance of HFSS and link to a design named
    ``HfssDesign1`` in a project named ``HfssProject``.

    >>> hfss = Hfss("HfssProject","HfssDesign1")
    pyaedt info: Added design 'HfssDesign1' of type HFSS.

    Create an instance of HFSS and open the specified project,
    which is named ``"myfile.aedt"``.

    >>> hfss = Hfss("myfile.aedt")
    pyaedt info: Project myfile has been created.
    pyaedt info: No design is present. Inserting a new design.
    pyaedt info: Added design...

    Create an instance of HFSS using the 2021 R1 release and open
    the specified project, which is named ``"myfile2.aedt"``.

    >>> hfss = Hfss(specified_version="2021.2", projectname="myfile2.aedt")
    pyaedt info: Project myfile2 has been created.
    pyaedt info: No design is present. Inserting a new design.
    pyaedt info: Added design...

    Create an instance of HFSS using the 2021 R2 student version and open
    the specified project, which is named ``"myfile3.aedt"``.

    >>> hfss = Hfss(specified_version="2021.2", projectname="myfile3.aedt", student_version=True)
    pyaedt info: Project myfile3 has been created.
    pyaedt info: No design is present. Inserting a new design.
    pyaedt info: Added design...

    """

    # def __repr__(self):
    #     try:
    #         return "HFSS {} {}. ProjectName:{} DesignName:{} ".format(
    #             self._aedt_version, self.solution_type, self.project_name, self.design_name
    #         )
    #     except:
    #         return "HFSS Module"

    def __init__(
        self,
        projectname=None,
        designname=None,
        solution_type=None,
        setup_name=None,
        specified_version=None,
        non_graphical=False,
        new_desktop_session=False,
        close_on_exit=False,
        student_version=False,
    ):
        FieldAnalysis3D.__init__(
            self,
            "HFSS",
            projectname,
            designname,
            solution_type,
            setup_name,
            specified_version,
            non_graphical,
            new_desktop_session,
            close_on_exit,
            student_version,
        )
        self.field_setups = self._get_rad_fields()

    def __enter__(self):
        return self

    @property
    def oradfield(self):
        """AEDT Radiation Field Object.

        References
        ----------

        >>> oDesign.GetModule("RadField")
        """
        if self.solution_type not in ["EigenMode", "Characteristic Mode"]:
            return self._odesign.GetModule("RadField")
        else:
            self.logger.warning("Solution %s does not support RadField.", self.solution_type)
            return

    @property
    def omodelsetup(self):
        """AEDT Model Setup Object.

        References
        ----------

        >>> oDesign.GetModule("ModelSetup")
        """
        return self._odesign.GetModule("ModelSetup")

    class BoundaryType(object):
        """Creates and manages boundaries."""

        (PerfectE, PerfectH, Aperture, Radiation, Impedance, LayeredImp, LumpedRLC, FiniteCond) = range(0, 8)

    @aedt_exception_handler
    def _get_rad_fields(self):
        if not self.design_properties:
            return []
        fields = []
        if self.design_properties.get("RadField") and self.design_properties["RadField"].get("FarFieldSetups"):
            for val in self.design_properties["RadField"]["FarFieldSetups"]:
                p = self.design_properties["RadField"]["FarFieldSetups"][val]
                if isinstance(p, (dict, OrderedDict)) and p.get("Type") == "Infinite Sphere":
                    fields.append(FarFieldSetup(self, val, p, "FarFieldSphere"))
        return fields

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
        :class:`pyaedt.modules.Boundary.BoundaryObject`
            Boundary object.

        """

        bound = BoundaryObject(self, name, props, boundary_type)
        result = bound.create()
        if result:
            self.boundaries.append(bound)
            self.logger.info("Boundary %s %s has been correctly created.", boundary_type, name)
            return bound
        self.logger.error("Error in boundary creation for %s %s.", boundary_type, name)

        return result

    @aedt_exception_handler
    def _create_lumped_driven(self, objectname, int_line_start, int_line_stop, impedance, portname, renorm, deemb):
        start = [str(i) + self.modeler.primitives.model_units for i in int_line_start]
        stop = [str(i) + self.modeler.primitives.model_units for i in int_line_stop]
        props = OrderedDict(
            {
                "Objects": [objectname],
                "DoDeembed": deemb,
                "RenormalizeAllTerminals": renorm,
                "Modes": OrderedDict(
                    {
                        "Mode1": OrderedDict(
                            {
                                "ModeNum": 1,
                                "UseIntLine": True,
                                "IntLine": OrderedDict({"Start": start, "End": stop}),
                                "AlignmentGroup": 0,
                                "CharImp": "Zpi",
                                "RenormImp": str(impedance) + "ohm",
                            }
                        )
                    }
                ),
                "ShowReporterFilter": False,
                "ReporterFilter": [True],
                "Impedance": str(impedance) + "ohm",
            }
        )
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
        props = OrderedDict(
            {
                "Edges": edgelist,
                "Impedance": str(impedance) + "ohm",
                "DoDeembed": deemb,
                "RenormalizeAllTerminals": renorm,
            }
        )

        if self.solution_type == "DrivenModal":

            if renorm:
                if isinstance(renorm_impedance, (int, float)) or "i" not in renorm_impedance:
                    renorm_imp = str(renorm_impedance) + "ohm"
                else:
                    renorm_imp = "(" + renorm_impedance + ") ohm"
            else:
                renorm_imp = "0ohm"
            props["RenormImp"] = renorm_imp
        else:
            props["TerminalIDList"] = []
        return self._create_boundary(name, props, "CircuitPort")

    @aedt_exception_handler
    def _create_waveport_driven(
        self,
        objectname,
        int_line_start=None,
        int_line_stop=None,
        impedance=50,
        portname="",
        renorm=True,
        nummodes=1,
        deemb_distance=0,
    ):
        start = None
        stop = None
        if int_line_start and int_line_stop:
            start = [str(i) + self.modeler.primitives.model_units for i in int_line_start]
            stop = [str(i) + self.modeler.primitives.model_units for i in int_line_stop]
            useintline = True
        else:
            useintline = False

        props = OrderedDict({})
        if isinstance(objectname, int):
            props["Faces"] = [objectname]
        else:
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
    def assigncoating(
        self,
        obj,
        mat=None,
        cond=58000000,
        perm=1,
        usethickness=False,
        thickness="0.1mm",
        roughness="0um",
        isinfgnd=False,
        istwoside=False,
        isInternal=True,
        issheelElement=False,
        usehuray=False,
        radius="0.5um",
        ratio="2.9",
    ):
        """Assign finite conductivity to one or more objects of a given material.

        .. deprecated:: 0.4.5
           Use :func:`Hfss.assign_coating` instead.

        """

        warnings.warn("`assigncoating` is deprecated. Use `assign_coating` instead.", DeprecationWarning)
        self.assign_coating(
            obj,
            mat,
            cond,
            perm,
            usethickness,
            thickness,
            roughness,
            isinfgnd,
            istwoside,
            isInternal,
            issheelElement,
            usehuray,
            radius,
            ratio,
        )

    @aedt_exception_handler
    def assign_coating(
        self,
        obj,
        mat=None,
        cond=58000000,
        perm=1,
        usethickness=False,
        thickness="0.1mm",
        roughness="0um",
        isinfgnd=False,
        istwoside=False,
        isInternal=True,
        issheelElement=False,
        usehuray=False,
        radius="0.5um",
        ratio="2.9",
    ):
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
        :class:`pyaedt.modules.Boundary.BoundaryObject`
            Boundary object.

        References
        ----------

        >>> oModule.AssignFiniteCond

        Examples
        --------

        Create a cylinder at the XY working plane and assign a copper coating of 0.2 mm to it.

        >>> origin = hfss.modeler.Position(0, 0, 0)
        >>> inner = hfss.modeler.primitives.create_cylinder(
        ...     hfss.PLANE.XY, origin, 3, 200, 0, "inner"
        ... )
        >>> inner_id = hfss.modeler.primitives.get_obj_id("inner")
        >>> coat = hfss.assign_coating([inner_id], "copper", usethickness=True, thickness="0.2mm")

        """

        listobj = self.modeler.convert_to_selections(obj, True)
        listobjname = "_".join(listobj)
        props = {"Objects": listobj}
        if mat:
            mat = mat.lower()
            if mat in self.materials.material_keys:
                Mat = self.materials.material_keys[mat]
                Mat.update()
                props["UseMaterial"] = True
                props["Material"] = mat
                self.materials._aedmattolibrary(mat)
            elif self.materials.checkifmaterialexists(mat):
                props["UseMaterial"] = True
                props["Material"] = mat
            else:
                return False
        else:
            props["UseMaterial"] = False
            props["Conductivity"] = str(cond)
            props["Permeability"] = str(str(perm))
        props["UseThickness"] = usethickness
        if usethickness:
            props["Thickness"] = thickness
        if usehuray:
            props["Radius"] = str(radius)
            props["Ratio"] = str(ratio)
            props["InfGroundPlane"] = False
        else:
            props["Roughness"] = roughness
            props["InfGroundPlane"] = isinfgnd
        props["IsTwoSided"] = istwoside

        if istwoside:
            props["IsShellElement"] = issheelElement
        else:
            props["IsInternal"] = isInternal
        return self._create_boundary("Coating_" + listobjname[:32], props, "FiniteCond")

    @aedt_exception_handler
    def create_frequency_sweep(
        self,
        setupname,
        unit="GHz",
        freqstart=1e-3,
        freqstop=10,
        sweepname=None,
        num_of_freq_points=451,
        sweeptype="Interpolating",
        interpolation_tol=0.5,
        interpolation_max_solutions=250,
        save_fields=True,
        save_rad_fields=False,
    ):
        """Create a frequency sweep.

        .. deprecated:: 0.4.0
           Use :func:`Hfss.create_linear_count_sweep` instead.

        """
        warnings.warn(
            "`create_frequency_sweep` is deprecated. Use `create_linear_count_sweep` instead.",
            DeprecationWarning,
        )

        return self.create_linear_count_sweep(
            setupname=setupname,
            unit=unit,
            freqstart=freqstart,
            freqstop=freqstop,
            num_of_freq_points=num_of_freq_points,
            sweepname=sweepname,
            save_fields=save_fields,
            save_rad_fields=save_rad_fields,
            sweep_type=sweeptype,
            interpolation_tol=interpolation_tol,
            interpolation_max_solutions=interpolation_max_solutions,
        )

    @aedt_exception_handler
    def create_linear_count_sweep(
        self,
        setupname,
        unit,
        freqstart,
        freqstop,
        num_of_freq_points,
        sweepname=None,
        save_fields=True,
        save_rad_fields=False,
        sweep_type="Discrete",
        interpolation_tol=0.5,
        interpolation_max_solutions=250,
    ):
        """Create a sweep with the specified number of points.

        Parameters
        ----------
        setupname : str
            Name of the setup.
        unit : str
            Unit of the frequency. For example, ``"MHz`` or ``"GHz"``.
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
        sweep_type : str, optional
            Type of the sweep. Options are ``"Fast"``, ``"Interpolating"``,
            and ``"Discrete"``. The default is ``"Discrete"``.
        interpolation_tol : float, optional
            Error tolerance threshold for the interpolation
            process. The default is ``0.5``.
        interpolation_max_solutions : int, optional
            Maximum number of solutions evaluated for the interpolation process.
            The default is ``250``.

        Returns
        -------
        :class:`pyaedt.modules.SetupTemplates.SweepHFSS` or bool
            Sweep object if successful, ``False`` otherwise.

        References
        ----------

        >>> oModule.InsertFrequencySweep

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
            raise AttributeError("Invalid in `sweep_type`. It has to be either 'Discrete', 'Interpolating', or 'Fast'")

        if sweepname is None:
            sweepname = generate_unique_name("Sweep")

        if setupname not in self.setup_names:
            return False
        for s in self.setups:
            if s.name == setupname:
                setupdata = s
                if sweepname in [sweep.name for sweep in setupdata.sweeps]:
                    oldname = sweepname
                    sweepname = generate_unique_name(oldname)
                    self.logger.warning(
                        "Sweep %s is already present. Sweep has been renamed in %s.", oldname, sweepname
                    )
                sweepdata = setupdata.add_sweep(sweepname, sweep_type)
                if not sweepdata:
                    return False
                sweepdata.props["RangeType"] = "LinearCount"
                sweepdata.props["RangeStart"] = str(freqstart) + unit
                sweepdata.props["RangeEnd"] = str(freqstop) + unit
                sweepdata.props["RangeCount"] = num_of_freq_points
                sweepdata.props["Type"] = sweep_type
                if sweep_type == "Interpolating":
                    sweepdata.props["InterpTolerance"] = interpolation_tol
                    sweepdata.props["InterpMaxSolns"] = interpolation_max_solutions
                    sweepdata.props["InterpMinSolns"] = 0
                    sweepdata.props["InterpMinSubranges"] = 1
                sweepdata.props["SaveFields"] = save_fields
                sweepdata.props["SaveRadFields"] = save_rad_fields
                sweepdata.update()
                self.logger.info("Linear count sweep {} has been correctly created".format(sweepname))
                return sweepdata
        return False

    @aedt_exception_handler
    def create_linear_step_sweep(
        self,
        setupname,
        unit,
        freqstart,
        freqstop,
        step_size,
        sweepname=None,
        save_fields=True,
        save_rad_fields=False,
        sweep_type="Discrete",
    ):
        """Create a Sweep with a specified frequency step.

        Parameters
        ----------
        setupname : str
            Name of the setup.
        unit : str
            Unit of the frequency. For example, ``"MHz`` or ``"GHz"``.
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
        :class:`pyaedt.modules.SetupTemplates.SweepHFSS` or bool
            Sweep object if successful, ``False`` otherwise.

        References
        ----------

        >>> oModule.InsertFrequencySweep

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
            raise AttributeError("Invalid in `sweep_type`. It has to either 'Discrete', 'Interpolating', or 'Fast'")
        if sweepname is None:
            sweepname = generate_unique_name("Sweep")

        if setupname not in self.setup_names:
            return False
        for s in self.setups:
            if s.name == setupname:
                setupdata = s
                if sweepname in [sweep.name for sweep in setupdata.sweeps]:
                    oldname = sweepname
                    sweepname = generate_unique_name(oldname)
                    self.logger.warning(
                        "Sweep %s is already present. Sweep has been renamed in %s.", oldname, sweepname
                    )
                sweepdata = setupdata.add_sweep(sweepname, sweep_type)
                if not sweepdata:
                    return False
                sweepdata.props["RangeType"] = "LinearStep"
                sweepdata.props["RangeStart"] = str(freqstart) + unit
                sweepdata.props["RangeEnd"] = str(freqstop) + unit
                sweepdata.props["RangeStep"] = str(step_size) + unit
                sweepdata.props["SaveFields"] = save_fields
                sweepdata.props["SaveRadFields"] = save_rad_fields
                sweepdata.props["ExtrapToDC"] = False
                sweepdata.props["Type"] = sweep_type
                if sweep_type == "Interpolating":
                    sweepdata.props["InterpTolerance"] = 0.5
                    sweepdata.props["InterpMaxSolns"] = 250
                    sweepdata.props["InterpMinSolns"] = 0
                    sweepdata.props["InterpMinSubranges"] = 1
                sweepdata.update()
                self.logger.info("Linear step sweep {} has been correctly created".format(sweepname))
                return sweepdata
        return False

    @aedt_exception_handler
    def create_single_point_sweep(
        self,
        setupname,
        unit,
        freq,
        sweepname=None,
        save_single_field=True,
        save_fields=False,
        save_rad_fields=False,
    ):
        """Create a Sweep with a single frequency point.

        Parameters
        ----------
        setupname : str
            Name of the setup.
        unit : str
            Unit of the frequency. For example, ``"MHz`` or ``"GHz"``.
        freq : float, list
            Frequency of the single point or list of frequencies to create distinct single points.
        sweepname : str, optional
            Name of the sweep. The default is ``None``.
        save_single_field : bool, list, optional
            Whether to save the fields of the single point. The default is ``True``.
            If a list is specified, the length must be the same as freq length.
        save_fields : bool, optional
            Whether to save the fields for all points and subranges defined in the sweep. The default is ``False``.
        save_rad_fields : bool, optional
            Whether to save only the radiating fields. The default is ``False``.

        Returns
        -------
        :class:`pyaedt.modules.SetupTemplates.SweepHFSS` or bool
            Sweep object if successful, ``False`` otherwise.

        References
        ----------

        >>> oModule.InsertFrequencySweep

        Examples
        --------

        Create a setup named ``"LinearStepSetup"`` and use it in a single point sweep
        named ``"SinglePointSweep"``.

        >>> setup = hfss.create_setup("LinearStepSetup")
        >>> single_point_sweep = hfss.create_single_point_sweep(setupname="LinearStepSetup",
        ...                                                   sweepname="SinglePointSweep",
        ...                                                   unit="MHz", freq=1.1e3)
        >>> type(single_point_sweep)
        <class 'pyaedt.modules.SetupTemplates.SweepHFSS'>

        """
        if sweepname is None:
            sweepname = generate_unique_name("SinglePoint")

        if isinstance(save_single_field, list):
            if not isinstance(freq, list) or len(save_single_field) != len(freq):
                raise AttributeError("The length of save_single_field must be the same as freq length.")

        add_subranges = False
        if isinstance(freq, list):
            if not freq:
                raise AttributeError("Frequency list is empty! Specify at least one frequency point.")
            freq0 = freq.pop(0)
            if freq:
                add_subranges = True
        else:
            freq0 = freq

        if isinstance(save_single_field, list):
            save0 = save_single_field.pop(0)
        else:
            save0 = save_single_field
            if add_subranges:
                save_single_field = [save0] * len(freq)

        if setupname not in self.setup_names:
            return False
        for s in self.setups:
            if s.name == setupname:
                setupdata = s
                if sweepname in [sweep.name for sweep in setupdata.sweeps]:
                    oldname = sweepname
                    sweepname = generate_unique_name(oldname)
                    self.logger.warning(
                        "Sweep %s is already present. Sweep has been renamed in %s.", oldname, sweepname
                    )
                sweepdata = setupdata.add_sweep(sweepname, "Discrete")
                sweepdata.props["RangeType"] = "SinglePoints"
                sweepdata.props["RangeStart"] = str(freq0) + unit
                sweepdata.props["RangeEnd"] = str(freq0) + unit
                sweepdata.props["SaveSingleField"] = save0
                sweepdata.props["SaveFields"] = save_fields
                sweepdata.props["SaveRadFields"] = save_rad_fields
                sweepdata.props["SMatrixOnlySolveMode"] = "Auto"
                if add_subranges:
                    for f, s in zip(freq, save_single_field):
                        sweepdata.add_subrange(rangetype="SinglePoints", start=f, unit=unit, save_single_fields=s)
                sweepdata.update()
                self.logger.info("Single point sweep {} has been correctly created".format(sweepname))
                return sweepdata
        return False

    @aedt_exception_handler
    def create_sbr_linked_antenna(
        self,
        source_object,
        target_cs="Global",
        solution=None,
        fieldtype="nearfield",
        use_composite_ports=False,
        use_global_current=True,
        current_conformance="Disable",
        thin_sources=True,
        power_fraction="0.95",
    ):
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

        References
        ----------

        >>> oEditor.InsertNativeComponent

        Examples
        --------
        >>> from pyaedt import Hfss
        >>> target_project = "my/path/to/targetProject.aedt"
        >>> source_project = "my/path/to/sourceProject.aedt"
        >>> target = Hfss(projectname=target_project, solution_type="SBR+",
        ...               specified_version="2021.2", new_desktop_session=False)  # doctest: +SKIP
        >>> source = Hfss(projectname=source_project, designname="feeder",
        ...               specified_version="2021.2", new_desktop_session=False)  # doctest: +SKIP
        >>> target.create_sbr_linked_antenna(source, target_cs="feederPosition",
        ...                                  fieldtype="farfield")  # doctest: +SKIP

        """
        if self.solution_type != "SBR+":
            self.logger.error("This Native components only applies to SBR+ Solution")
            return False
        compName = source_object.design_name
        uniquename = generate_unique_name(compName)
        if source_object.project_name == self.project_name:
            project_name = "This Project*"
        else:
            project_name = os.path.join(source_object.project_path, source_object.project_name + ".aedt")
        design_name = source_object.design_name
        if not solution:
            solution = source_object.nominal_adaptive
        params = OrderedDict({})
        pars = source_object.available_variations.nominal_w_values_dict
        for el in pars:
            params[el] = pars[el]
        native_props = OrderedDict(
            {
                "Type": "Linked Antenna",
                "Unit": self.modeler.model_units,
                "Is Parametric Array": False,
                "Project": project_name,
                "Product": "HFSS",
                "Design": design_name,
                "Soln": solution,
                "Params": params,
                "ForceSourceToSolve": True,
                "PreservePartnerSoln": True,
                "PathRelativeTo": "TargetProject",
                "FieldType": fieldtype,
                "UseCompositePort": use_composite_ports,
                "SourceBlockageStructure": OrderedDict({"NonModelObject": []}),
            }
        )
        if fieldtype == "nearfield":
            native_props["UseGlobalCurrentSrcOption"] = use_global_current
            native_props["Current Source Conformance"] = current_conformance
            native_props["Thin Sources"] = thin_sources
            native_props["Power Fraction"] = power_fraction
        return self._create_native_component(
            "Linked Antenna", target_cs, self.modeler.model_units, native_props, uniquename
        )

    @aedt_exception_handler
    def _create_native_component(
        self, antenna_type, target_cs=None, model_units=None, parameters_dict=None, antenna_name=None
    ):
        if antenna_name is None:
            antenna_name = generate_unique_name(antenna_type.replace(" ", "").replace("-", ""))
        if not model_units:
            model_units = self.modeler.model_units

        native_props = OrderedDict(
            {"NativeComponentDefinitionProvider": OrderedDict({"Type": antenna_type, "Unit": model_units})}
        )
        native_props["TargetCS"] = target_cs
        if isinstance(parameters_dict, dict):
            for el in parameters_dict:
                if (
                    el not in ["antenna_type", "offset", "rotation", "rotation_axis", "mode"]
                    and parameters_dict[el] is not None
                ):
                    native_props["NativeComponentDefinitionProvider"][el.replace("_", " ").title()] = parameters_dict[
                        el
                    ]
        native = NativeComponentObject(self, antenna_type, antenna_name, native_props)
        if native.create():
            self.native_components.append(native)
            self.logger.info("Native Component %s %s has been correctly created", antenna_type, antenna_name)
            return native
        self.logger.error("Error in Native Component creation for %s %s.", antenna_type, antenna_name)

        return None

    class SbrAntennas:
        (
            ConicalHorn,
            CrossDipole,
            HalfWaveDipole,
            HorizontalDipole,
            ParametricBeam,
            ParametricSlot,
            PyramidalHorn,
            QuarterWaveMonopole,
            ShortDipole,
            SmallLoop,
            WireDipole,
            WireMonopole,
        ) = (
            "Conical Horn",
            "Cross Dipole",
            "Half-Wave Dipole",
            "Horizontal Dipole",
            "Parametric Beam",
            "Parametric Slot",
            "Pyramidal Horn",
            "Quarter-Wave Monopole",
            "Short Dipole",
            "Small Loop",
            "Wire Dipole",
            "Wire Monopole",
        )

    class SBRAntennaDefaults:
        _conical = OrderedDict(
            {
                "Is Parametric Array": False,
                "MatchedPortImpedance": "50ohm",
                "Polarization": "Vertical",
                "Representation": "Far Field",
                "Mouth Diameter": "0.3meter",
                "Flare Half Angle": "20deg",
            }
        )
        _cross = OrderedDict(
            {
                "Is Parametric Array": False,
                "MatchedPortImpedance": "50ohm",
                "Polarization": "RHCP",
                "Representation": "Current Source",
                "Density": "1",
                "UseGlobalCurrentSrcOption": True,
                "Resonant Frequency": "0.3GHz",
                "Wire Length": "499.654096666667mm",
                "Mode": 0,
            }
        )
        _horizontal = OrderedDict(
            {
                "Is Parametric Array": False,
                "MatchedPortImpedance": "50ohm",
                "Polarization": "Vertical",
                "Representation": "Current Source",
                "Density": "1",
                "UseGlobalCurrentSrcOption": False,
                "Resonant Frequency": "0.3GHz",
                "Wire Length": "499.654096666667mm",
                "Height Over Ground Plane": "249.827048333333mm",
                "Use Default Height": True,
            }
        )
        _parametricbeam = OrderedDict(
            {
                "Is Parametric Array": False,
                "Size": "0.1meter",
                "MatchedPortImpedance": "50ohm",
                "Polarization": "Vertical",
                "Representation": "Far Field",
                "Vertical BeamWidth": "30deg",
                "Horizontal BeamWidth": "60deg",
            }
        )
        _slot = OrderedDict(
            {
                "Is Parametric Array": False,
                "MatchedPortImpedance": "50ohm",
                "Representation": "Far Field",
                "Resonant Frequency": "0.3GHz",
                "Slot Length": "499.654096666667mm",
            }
        )
        _horn = OrderedDict(
            {
                "Is Parametric Array": False,
                "MatchedPortImpedance": "50ohm",
                "Representation": "Far Field",
                "Mouth Width": "0.3meter",
                "Mouth Height": "0.5meter",
                "Waveguide Width": "0.15meter",
                "Width Flare Half Angle": "20deg",
                "Height Flare Half Angle": "35deg",
            }
        )
        _dipole = OrderedDict(
            {
                "Is Parametric Array": False,
                "Size": "1mm",
                "MatchedPortImpedance": "50ohm",
                "Representation": "Far Field",
            }
        )
        _smallloop = OrderedDict(
            {
                "Is Parametric Array": False,
                "MatchedPortImpedance": "50ohm",
                "Polarization": "Vertical",
                "Representation": "Current Source",
                "Density": "1",
                "UseGlobalCurrentSrcOption": False,
                "Current Source Conformance": "Disable",
                "Thin Sources": True,
                "Power Fraction": "0.95",
                "Mouth Diameter": "0.3meter",
                "Flare Half Angle": "20deg",
            }
        )
        _wiredipole = OrderedDict(
            {
                "Is Parametric Array": False,
                "MatchedPortImpedance": "50ohm",
                "Representation": "Far Field",
                "Resonant Frequency": "0.3GHz",
                "Wire Length": "499.654096666667mm",
            }
        )
        parameters = {
            "Conical Horn": _conical,
            "Cross Dipole": _cross,
            "Half-Wave Dipole": _dipole,
            "Horizontal Dipole": _horizontal,
            "Parametric Beam": _parametricbeam,
            "Parametric Slot": _slot,
            "Pyramidal Horn": _horn,
            "Quarter-Wave Monopole": _dipole,
            "Short Dipole": _dipole,
            "Small Loop": _dipole,
            "Wire Dipole": _wiredipole,
            "Wire Monopole": _wiredipole,
        }
        default_type_id = {
            "Conical Horn": 11,
            "Cross Dipole": 12,
            "Half-Wave Dipole": 3,
            "Horizontal Dipole": 13,
            "Parametric Beam": 0,
            "Parametric Slot": 7,
            "Pyramidal Horn": _horn,
            "Quarter-Wave Monopole": 4,
            "Short Dipole": 1,
            "Small Loop": 2,
            "Wire Dipole": 5,
            "Wire Monopole": 6,
            "File Based Antenna": 8,
        }

    @aedt_exception_handler
    def create_sbr_antenna(
        self,
        antenna_type=SbrAntennas.ConicalHorn,
        target_cs=None,
        model_units=None,
        parameters_dict=None,
        use_current_source_representation=False,
        is_array=False,
        antenna_name=None,
    ):
        """Create a parametric beam antenna in SBR+.

        Parameters
        ----------
        antenna_type : str, `SbrAntennas.ConicalHorn`
            Name of the antenna type. Enumerator SbrAntennas can also be used.
            The default is ``"Conical Horn"``.
        target_cs : str, optional
            Target coordinate system. The default is ``None``, in which case
            the active coodiantes system is used.
        model_units : str, optional
            Model units to apply to the object. The default is
            ``None`` in which case the active modeler units are applied.
        parameters_dict : dict, optional
            The default is ``None``.
        use_current_source_representation : bool, optional
            The default is ``False``.
        is_array : bool, optional
            The default is ``False``.
        antenna_name : str, optional
            Name of the 3D component. The default is ``None``, in which case the
            name is auto-generated based on the antenna type.

        Returns
        -------
        :class:`pyaedt.modules.Boundary.NativeComponentObject`
            NativeComponentObject object.

        References
        ----------

        >>> oEditor.InsertNativeComponent

        Examples
        --------
        >>> from pyaedt import Hfss
        >>> hfss = Hfss(solution_type="SBR+")  # doctest: +SKIP
        pyaedt info: Added design 'HFSS_IPO' of type HFSS.
        >>> parm = {"polarization": "Vertical"}  # doctest: +SKIP
        >>> par_beam = hfss.create_sbr_antenna(hfss.SbrAntennas.ShortDipole,
        ...                                    parameters_dict=parm,
        ...                                    antenna_name="TX1")  # doctest: +SKIP

        """
        if self.solution_type != "SBR+":
            self.logger.error("This native component only applies to a SBR+ solution.")
            return False
        if target_cs is None:
            target_cs = self.modeler.oeditor.GetActiveCoordinateSystem()
        parameters_defaults = self.SBRAntennaDefaults.parameters[antenna_type].copy()
        if use_current_source_representation and antenna_type in [
            "Conical Horn",
            "Horizontal Dipole",
            "Parametric Slot",
            "Pyramidal Horn",
            "Wire Dipole",
            "Wire Monopole",
        ]:
            parameters_defaults["Representation"] = "Current Source"
            parameters_defaults["Density"] = "1"
            parameters_defaults["UseGlobalCurrentSrcOption"] = False
            parameters_defaults["Current Source Conformance"] = "Disable"
            parameters_defaults["Thin Sources"] = False
            parameters_defaults["Power Fraction"] = "0.95"
        if is_array:
            parameters_defaults["Is Parametric Array"] = True
            parameters_defaults["Array Element Type"] = self.SBRAntennaDefaults.default_type_id[antenna_type]
            parameters_defaults["Array Element Angle Phi"] = ("0deg",)
            parameters_defaults["Array Element Angle Theta"] = ("0deg",)
            parameters_defaults["Array Element Offset X"] = "0meter"
            parameters_defaults["Array Element Offset Y"] = "0meter"
            parameters_defaults["Array Element Offset Z"] = "0meter"
            parameters_defaults["Array Element Conformance Type"] = 0
            parameters_defaults["Array Element Conformance Type"] = 0
            parameters_defaults["Array Element Conformance Type"] = 0
            parameters_defaults["Array Element Conform Orientation"] = False
            parameters_defaults["Array Design Frequency"] = "1GHz"
            parameters_defaults["Array Layout Type"] = 1
            parameters_defaults["Array Specify Design In Wavelength"] = True
            parameters_defaults["Array Element Num"] = 5
            parameters_defaults["Array Length"] = "1meter"
            parameters_defaults["Array Width"] = "1meter"
            parameters_defaults["Array Length Spacing"] = "0.1meter"
            parameters_defaults["Array Width Spacing"] = "0.1meter"
            parameters_defaults["Array Length In Wavelength"] = "3"
            parameters_defaults["Array Width In Wavelength"] = "4"
            parameters_defaults["Array Length Spacing In Wavelength"] = "0.5"
            parameters_defaults["Array Stagger Type"] = 0
            parameters_defaults["Array Stagger Angle"] = "0deg"
            parameters_defaults["Array Symmetry Type"] = 0
            parameters_defaults["Array Weight Type"] = 3
            parameters_defaults["Array Beam Angle Theta"] = "0deg"
            parameters_defaults["Array Weight Edge TaperX"] = -200
            parameters_defaults["Array Weight Edge TaperY"] = -200
            parameters_defaults["Array Weight Cosine Exp"] = 1
            parameters_defaults["Array Differential Pattern Type"] = 0
            if is_array:
                antenna_name = generate_unique_name("pAntArray")
        if parameters_dict:
            for el, value in parameters_dict.items():
                parameters_defaults[el] = value
        return self._create_native_component(antenna_type, target_cs, model_units, parameters_defaults, antenna_name)

    @aedt_exception_handler
    def create_sbr_file_based_antenna(
        self,
        ffd_full_path,
        antenna_size="1mm",
        antenna_impedance="50ohm",
        representation_type="Far Field",
        target_cs=None,
        model_units=None,
        antenna_name=None,
    ):
        """Create a linked antenna.


        Parameters
        ----------
        ffd_full_path : str
            Full path to the FFD file.
        antenna_size : str, optional
            Antenna size with units. The default is ``"1mm"``.
        antenna_impedance : str, optional
            Antenna impedance with units. The default is ``"50ohm"``.
        representation_type : str, optional
            Type of the antenna type. Options are ``"Far Field"`` or ``"Near Field"``.
            The default is ``"Far Field"``.
        target_cs : str, optional
            Target coordinate system. The default is ``None``, in which case the
            active coordinate system is used.
        model_units : str, optional
            Model units to apply to the object. The default is
            ``None``, in which case the active modeler units are applied.
        antenna_name : str, optional
            Name of the 3D component. The default is ``None``, in which case
            the name is auto-generated based on the antenna type.

        Returns
        -------
        :class:`pyaedt.modules.Boundary.NativeComponentObject`

        References
        ----------

        >>> oEditor.InsertNativeComponent

        Examples
        --------
        >>> from pyaedt import Hfss
        >>> hfss = Hfss(solution_type="SBR+")  # doctest: +SKIP
        >>> ffd_file = "full_path/to/ffdfile.ffd"
        >>> par_beam = hfss.create_sbr_file_based_antenna(ffd_file)  # doctest: +SKIP

        """
        if self.solution_type != "SBR+":
            self.logger.error("This Native component only applies to a SBR+ Solution.")
            return False
        if target_cs is None:
            target_cs = self.modeler.oeditor.GetActiveCoordinateSystem()

        par_dicts = OrderedDict(
            {
                "Size": antenna_size,
                "MatchedPortImpedance": antenna_impedance,
                "Representation": representation_type,
                "ExternalFile": ffd_full_path,
            }
        )
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
        :class:`pyaedt.modules.Boundary.BoundaryObject`
            Boundary object.

        References
        ----------

        >>> oModule.SetSBRTxRxSettings
        """
        if self.solution_type != "SBR+":
            self.logger.error("This Boundary only applies to SBR+ Solution")
            return False
        id = 0
        props = OrderedDict({})
        for el, val in txrx_settings.items():
            props["Tx/Rx List " + str(id)] = OrderedDict({"Tx Antenna": el, "Rx Antennas": txrx_settings[el]})
            id += 1
        return self._create_boundary("SBRTxRxSettings", props, "SBRTxRxSettings")

    @aedt_exception_handler
    def create_circuit_port_between_objects(
        self, startobj, endobject, axisdir=0, impedance=50, portname=None, renorm=True, renorm_impedance=50, deemb=False
    ):
        """Create a circuit port taking the closest edges of two objects.

        Parameters
        ----------
        startobj :
            First (starting) object for the integration line.
        endobject :
            Second (ending) object for the integration line.
        axisdir : int or :class:`pyaedt.application.Analysis.Analysis.AxisDir`, optional
            Position of the port. It should be one of the values for ``Application.AxisDir``,
            which are: ``XNeg``, ``YNeg``, ``ZNeg``, ``XPos``, ``YPos``, and ``ZPos``.
            The default is ``Application.AxisDir.XNeg``.
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

        References
        ----------

        >>> oModule.AssignCircuitPort

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
            endobject
        ):
            self.logger.error("One or both objects doesn't exists. Check and retry.")
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
    def create_lumped_port_between_objects(
        self, startobj, endobject, axisdir=0, impedance=50, portname=None, renorm=True, deemb=False, port_on_plane=True
    ):
        """Create a lumped port taking the closest edges of two objects.

        Parameters
        ----------
        startobj :
            First (starting) object for the integration line.
        endobject :
            Second (ending) object for the integration line.
        axisdir : int or :class:`pyaedt.application.Analysis.Analysis.AxisDir`, optional
            Position of the port. It should be one of the values for ``Application.AxisDir``,
            which are: ``XNeg``, ``YNeg``, ``ZNeg``, ``XPos``, ``YPos``, and ``ZPos``.
            The default is ``Application.AxisDir.XNeg``.
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

        References
        ----------

        >>> oModule.AssignLumpedPort

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
        pyaedt info: Connection Correctly created
        'LumpedPort'

        """

        if not self.modeler.primitives.does_object_exists(startobj) or not self.modeler.primitives.does_object_exists(
            endobject
        ):
            self.logger.error("One or both objects do not exist. Check and retry.")
            return False

        if self.solution_type in ["DrivenModal", "DrivenTerminal", "Transient Network"]:
            sheet_name, point0, point1 = self.modeler._create_sheet_from_object_closest_edge(
                startobj, endobject, axisdir, port_on_plane
            )

            if not portname:
                portname = generate_unique_name("Port")
            elif portname + ":1" in self.modeler.get_excitations_name():
                portname = generate_unique_name(portname)
            if self.solution_type == "DrivenModal":
                self._create_lumped_driven(sheet_name, point0, point1, impedance, portname, renorm, deemb)
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
        axisdir : int or :class:`pyaedt.application.Analysis.Analysis.AxisDir`, optional
            Position of the port. It should be one of the values for
            ``Application.AxisDir``, which are: ``XNeg``, ``YNeg``,
            ``ZNeg``, ``XPos``, ``YPos``, and ``ZPos``.  The default
            is ``Application.AxisDir.XNeg``.
        sourcename : str, optional
            Name of the source. The default is ``None``.
        source_on_plane : bool, optional
            Whether to create the source on the plane orthogonal to
            ``AxisDir``. The default is ``True``.

        Returns
        -------
        :class:`pyaedt.modules.Boundary.BoundaryObject`
            Boundary object.

        References
        ----------

        >>> oModule.AssignVoltage

        Examples
        --------

        Create two boxes that will be used to create a voltage source
        named ``'VoltageSource'``.

        >>> box1 = hfss.modeler.primitives.create_box([30, 0, 0], [40, 10, 5],
        ...                                           "BoxVolt1", "copper")
        >>> box2 = hfss.modeler.primitives.create_box([30, 0, 10], [40, 10, 5],
        ...                                           "BoxVolt2", "copper")
        >>> v1 = hfss.create_voltage_source_from_objects("BoxVolt1", "BoxVolt2",
        ...                                         hfss.AxisDir.XNeg,
        ...                                         "VoltageSource")
        pyaedt info: Connection Correctly created

        """

        if not self.modeler.primitives.does_object_exists(startobj) or not self.modeler.primitives.does_object_exists(
            endobject
        ):
            self.logger.error("One or both objects doesn't exists. Check and retry")
            return False
        if self.solution_type in ["DrivenModal", "DrivenTerminal", "Transient Network"]:
            sheet_name, point0, point1 = self.modeler._create_sheet_from_object_closest_edge(
                startobj, endobject, axisdir, source_on_plane
            )
            if not sourcename:
                sourcename = generate_unique_name("Voltage")
            elif sourcename + ":1" in self.modeler.get_excitations_name():
                sourcename = generate_unique_name(sourcename)
            return self.create_source_excitation(sheet_name, point0, point1, sourcename, sourcetype="Voltage")
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
        axisdir : int or :class:`pyaedt.application.Analysis.Analysis.AxisDir`, optional
            Position of the port. It should be one of the values for ``Application.AxisDir``,
            which are: ``XNeg``, ``YNeg``, ``ZNeg``, ``XPos``, ``YPos``, and ``ZPos``.
            The default is ``Application.AxisDir.XNeg``.
        sourcename : str, optional
            Name of the source. The default is ``None``.
        source_on_plane : bool, optional
            Whether to create the source on the plane orthogonal to ``axisdir``. The default is ``True``.

        Returns
        -------
        :class:`pyaedt.modules.Boundary.BoundaryObject`
            Boundary object.

        References
        ----------

        >>> oModule.AssignCurrent

        Examples
        --------

        Create two boxes that will be used to create a current source
        named ``'CurrentSource'``.

        >>> box1 = hfss.modeler.primitives.create_box([30, 0, 20], [40, 10, 5],
        ...                                           "BoxCurrent1", "copper")
        >>> box2 = hfss.modeler.primitives.create_box([30, 0, 30], [40, 10, 5],
        ...                                           "BoxCurrent2", "copper")
        >>> i1 = hfss.create_current_source_from_objects("BoxCurrent1", "BoxCurrent2",
        ...                                         hfss.AxisDir.XPos,
        ...                                         "CurrentSource")
        pyaedt info: Connection created 'CurrentSource' correctly.

        """

        if not self.modeler.primitives.does_object_exists(startobj) or not self.modeler.primitives.does_object_exists(
            endobject
        ):
            self.logger.error("One or both objects do not exist. Check and retry.")
            return False
        if self.solution_type in ["DrivenModal", "DrivenTerminal", "Transient Network"]:
            sheet_name, point0, point1 = self.modeler._create_sheet_from_object_closest_edge(
                startobj, endobject, axisdir, source_on_plane
            )
            if not sourcename:
                sourcename = generate_unique_name("Current")
            elif sourcename + ":1" in self.modeler.get_excitations_name():
                sourcename = generate_unique_name(sourcename)
            return self.create_source_excitation(sheet_name, point0, point1, sourcename, sourcetype="Current")
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
        :class:`pyaedt.modules.Boundary.BoundaryObject`
            Boundary object.

        References
        ----------

        >>> oModule.AssignVoltage
        >>> oModule.AssignCurrent
        """

        props = OrderedDict({"Objects": [sheet_name], "Direction": OrderedDict({"Start": point1, "End": point2})})
        return self._create_boundary(sourcename, props, sourcetype)

    @aedt_exception_handler
    def create_wave_port_between_objects(
        self,
        startobj,
        endobject,
        axisdir=0,
        impedance=50,
        nummodes=1,
        portname=None,
        renorm=True,
        deembed_dist=0,
        port_on_plane=True,
        add_pec_cap=False,
    ):
        """Create a waveport taking the closest edges of two objects.

        Parameters
        ----------
        startobj :
            First (starting) object for the integration line.
        endobject :
            Second (ending) object for the integration line.
        axisdir : int or :class:`pyaedt.application.Analysis.Analysis.AxisDir`, optional
            Position of the port. It should be one of the values for ``Application.AxisDir``,
            which are: ``XNeg``, ``YNeg``, ``ZNeg``, ``XPos``, ``YPos``, and ``ZPos``.
            The default is ``Application.AxisDir.XNeg``.
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
        :class:`pyaedt.modules.Boundary.BoundaryObject`
            Boundary object.

        References
        ----------

        >>> oModule.AssignWavePort

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
        pyaedt info: Connection Correctly created

        """

        if not self.modeler.primitives.does_object_exists(startobj) or not self.modeler.primitives.does_object_exists(
            endobject
        ):
            self.logger.error("One or both objects do not exist. Check and retry.")
            return False
        if self.solution_type in ["DrivenModal", "DrivenTerminal", "Transient Network"]:
            sheet_name, point0, point1 = self.modeler._create_sheet_from_object_closest_edge(
                startobj, endobject, axisdir, port_on_plane
            )
            if add_pec_cap:
                dist = GeometryOperators.points_distance(point0, point1)
                self._create_pec_cap(sheet_name, startobj, dist / 10)
            if not portname:
                portname = generate_unique_name("Port")
            elif portname + ":1" in self.modeler.get_excitations_name():
                portname = generate_unique_name(portname)
            if self.solution_type == "DrivenModal":
                return self._create_waveport_driven(
                    sheet_name, point0, point1, impedance, portname, renorm, nummodes, deembed_dist
                )
            else:
                faces = self.modeler.primitives.get_object_faces(sheet_name)
                return self._create_port_terminal(faces[0], endobject, portname, iswaveport=True)
        return False

    @aedt_exception_handler
    def create_floquet_port(
        self,
        face,
        lattice_origin=None,
        lattice_a_end=None,
        lattice_b_end=None,
        nummodes=2,
        portname=None,
        renorm=True,
        deembed_dist=0,
        reporter_filter=True,
        lattice_cs="Global",
    ):
        """Create a Floquet Port on a Face.

        Parameters
        ----------
        face :
            Face or Sheet on which apply the Floquet Port.
        lattice_origin : list
            List of `[x,y,z]` coordinates for the lattice A-B origin. If `None` the method will
            try to compute the A-B automatically.
        lattice_a_end : list
            List of `[x,y,z]` coordinates for the lattice A end point. If `None` the method will
            try to compute the A-B automatically.
        lattice_b_end : list
            List of `[x,y,z]` coordinates for the lattice B end point. If `None` the method will
            try to compute the A-B automatically.
        nummodes : int, optional
            Number of modes. The default is ``2``.
        portname : str, optional
            Name of the port. The default is ``None``.
        renorm : bool, optional
            Whether to renormalize the mode. The default is ``True``.
        deembed_dist : float, str, optional
            Deembed distance in millimeters. The default is ``0``,
            in which case deembed is disabled.
        reporter_filter : bool, list of bool
            Whether to include mode into reported. It can be a bool and applies to all modes or list of bools
            and applies to each mode. List must have `nummodes` elements.
        lattice_cs : str, optional
            Lattice A-B Vector Coordinate System Reference.

        Returns
        -------
        :class:`pyaedt.modules.Boundary.BoundaryObject`
            Boundary object.


        References
        ----------

        >>> oModule.AssignFloquetPort
        """
        face_id = self.modeler._convert_list_to_ids(face, True)
        props = OrderedDict({})
        if isinstance(face_id[0], int):
            props["Faces"] = face_id
        else:
            props["Objects"] = face_id

        props["NumModes"] = nummodes
        if deembed_dist:
            props["DoDeembed"] = True
            props["DeembedDist"] = self.modeler.primitives._arg_with_dim(deembed_dist)
        else:
            props["DoDeembed"] = False
            props["DeembedDist"] = "0mm"
        props["RenormalizeAllTerminals"] = renorm
        props["Modes"] = OrderedDict({})
        for i in range(1, 1 + nummodes):
            props["Modes"]["Mode{}".format(i)] = OrderedDict({})
            props["Modes"]["Mode{}".format(i)]["ModeNum"] = i
            props["Modes"]["Mode{}".format(i)]["UseIntLine"] = False
            props["Modes"]["Mode{}".format(i)]["CharImp"] = "Zpi"
        props["ShowReporterFilter"] = True
        if isinstance(reporter_filter, bool):
            props["ReporterFilter"] = [reporter_filter for i in range(nummodes)]
        else:
            props["ReporterFilter"] = reporter_filter
        if not lattice_a_end or not lattice_origin or not lattice_b_end:
            result, output = self.modeler._find_perpendicular_points(face_id[0])
            lattice_origin = output[0]
            lattice_a_end = output[1]
            lattice_b_end = output[2]
        props["LatticeAVector"] = OrderedDict({})
        props["LatticeAVector"]["Coordinate System"] = lattice_cs
        props["LatticeAVector"]["Start"] = lattice_origin
        props["LatticeAVector"]["End"] = lattice_a_end
        props["LatticeBVector"] = OrderedDict({})
        props["LatticeBVector"]["Coordinate System"] = lattice_cs
        props["LatticeBVector"]["Start"] = lattice_origin
        props["LatticeBVector"]["End"] = lattice_b_end
        if not portname:
            portname = generate_unique_name("Floquet")
        return self._create_boundary(portname, props, "FloquetPort")

    @aedt_exception_handler
    def assign_lattice_pair(
        self,
        face_couple,
        reverse_v=False,
        phase_delay="UseScanAngle",
        phase_delay_param1="0deg",
        phase_delay_param2="0deg",
        pair_name=None,
    ):
        """Assign Lattice Pair to a couple of faces.

        Parameters
        ----------
        face_couple : list
            List of 2 faces to assign the lattice pair to.
        reverse_v : bool, optional
            Reverse V Vector. Default is `False`.
        phase_delay : str, optional
            Define the phase delay approach. Default is `"UseScanAngle"`.
            Options are `"UseScanUV"`, `"InputPhaseDelay"`
        phase_delay_param1 : str, optional
            Phi Angle if "UseScanAngle" is used. U value if "UseScanUV" is used".
            "Phase" if "InputPhaseDelay". Default is `0deg`.
        phase_delay_param2 :  str, optional
            Theta Angle if "UseScanAngle" is used. V value if "UseScanUV" is used".
            Default is `0deg`.
        pair_name : str, optional
            Boundary name.

        Returns
        -------
        :class:`pyaedt.modules.Boundary.BoundaryObject`
            Boundary object.

        References
        ----------

        >>> oModule.AssignLatticePair
        """
        props = OrderedDict({})
        face_id = self.modeler._convert_list_to_ids(face_couple, True)
        props["Faces"] = face_id
        props["ReverseV"] = reverse_v

        props["PhaseDelay"] = phase_delay
        if phase_delay == "UseScanAngle":
            props["Phi"] = phase_delay_param1
            props["Theta"] = phase_delay_param2
        elif phase_delay == "UseScanUV":
            props["ScanU"] = phase_delay_param1
            props["ScanV"] = phase_delay_param2
        else:
            props["Phase"] = phase_delay_param1
        if not pair_name:
            pair_name = generate_unique_name("LatticePair")
        return self._create_boundary(pair_name, props, "Lattice Pair")

    @aedt_exception_handler
    def auto_assign_lattice_pairs(self, object_to_assign, coordinate_system="Global", coordinate_plane="XY"):
        """Auto Assign Lattice Pairs to geometry.

        Parameters
        ----------
        object_to_assign : str, Object3d
            Object to which assign Lattice.
        coordinate_system : str, optional
            Coordinate System on which look for lattice.
        coordinate_plane : str, optional
            Plane on which looks for lattice. Default is `"XY"`. Options are`"XZ"` and `"YZ"`.

        Returns
        -------
        list of str
            list of created pair names.

        References
        ----------

        >>> oModule.AutoIdentifyLatticePair
        """
        objectname = self.modeler._convert_list_to_ids(object_to_assign, True)
        boundaries = list(self.oboundary.GetBoundaries())
        self.oboundary.AutoIdentifyLatticePair("{}:{}".format(coordinate_system, coordinate_plane), objectname[0])
        boundaries = [i for i in list(self.oboundary.GetBoundaries()) if i not in boundaries]
        bounds = [i for i in boundaries if boundaries.index(i) % 2 == 0]
        return bounds

    @aedt_exception_handler
    def assign_secondary(
        self,
        face,
        primary_name,
        u_start,
        u_end,
        reverse_v=False,
        phase_delay="UseScanAngle",
        phase_delay_param1="0deg",
        phase_delay_param2="0deg",
        coord_name="Global",
        secondary_name=None,
    ):
        """Assign Secondary Boundary Condition.

        Parameters
        ----------
        face : int, FacePrimitive
            Face to assign the lattice pair.
        primary_name : str
            Name of the Primary boundary to couple.
        u_start : list
            List of [x,y,z] values for start point of U vector.
        u_end : list
            List of [x,y,z] values for end point of U vector.
        reverse_v : bool, optional
            Reverse V Vector. Default is `False`.
        phase_delay : str, optional
            Define the phase delay approach. Default is `"UseScanAngle"`.
            Options are `"UseScanUV"`, `"InputPhaseDelay"`
        phase_delay_param1 : str, optional
            Phi Angle if "UseScanAngle" is used. U value if "UseScanUV" is used".
            "Phase" if "InputPhaseDelay". Default is `0deg`.
        phase_delay_param2 :  str, optional
            Theta Angle if "UseScanAngle" is used. V value if "UseScanUV" is used".
            Default is `0deg`.
        coord_name : str, optional
            Name of the coordinate system for u coordinates.
        secondary_name : str, optional
            Boundary name.


        Returns
        -------
        :class:`pyaedt.modules.Boundary.BoundaryObject`
            Boundary object.

        References
        ----------

        >>> oModule.AssignSecondary
        """
        props = OrderedDict({})
        face_id = self.modeler._convert_list_to_ids(face, True)
        if isinstance(face_id[0], str):
            props["Objects"] = face_id

        else:
            props["Faces"] = face_id

        props["CoordSysVector"] = OrderedDict({})
        props["CoordSysVector"]["Coordinate System"] = coord_name
        props["CoordSysVector"]["Origin"] = u_start
        props["CoordSysVector"]["UPos"] = u_end
        props["ReverseV"] = reverse_v

        props["Primary"] = primary_name
        props["PhaseDelay"] = phase_delay
        if phase_delay == "UseScanAngle":
            props["Phi"] = phase_delay_param1
            props["Theta"] = phase_delay_param2
        elif phase_delay == "UseScanUV":
            props["ScanU"] = phase_delay_param1
            props["ScanV"] = phase_delay_param2
        else:
            props["Phase"] = phase_delay_param1
        if not secondary_name:
            secondary_name = generate_unique_name("Secondary")
        return self._create_boundary(secondary_name, props, "Secondary")

    @aedt_exception_handler
    def assign_primary(self, face, u_start, u_end, reverse_v=False, coord_name="Global", primary_name=None):
        """Assign Secondary Boundary Condition.

        Parameters
        ----------
        face : int, FacePrimitive
            Face to assign the lattice pair.
        u_start : list
            List of [x,y,z] values for start point of U vector.
        u_end : list
            List of [x,y,z] values for end point of U vector.
        reverse_v : bool, optional
            Reverse V Vector. Default is `False`.
        coord_name : str, optional
            Name of the coordinate system for u coordinates.
        primary_name : str, optional
            Boundary name.

        Returns
        -------
        :class:`pyaedt.modules.Boundary.BoundaryObject`
            Boundary object.

        References
        ----------

        >>> oModule.AssignPrimary
        """
        props = OrderedDict({})
        face_id = self.modeler._convert_list_to_ids(face, True)
        if isinstance(face_id[0], str):
            props["Objects"] = face_id

        else:
            props["Faces"] = face_id
        props["ReverseV"] = reverse_v
        props["CoordSysVector"] = OrderedDict({})
        props["CoordSysVector"]["Coordinate System"] = coord_name
        props["CoordSysVector"]["Origin"] = u_start
        props["CoordSysVector"]["UPos"] = u_end
        if not primary_name:
            primary_name = generate_unique_name("Primary")
        return self._create_boundary(primary_name, props, "Primary")

    def _create_pec_cap(self, sheet_name, obj_name, pecthick):
        # TODO check method
        obj = self.modeler.primitives[sheet_name].clone()
        out_obj = self.modeler.thicken_sheet(obj, pecthick, False)
        bounding2 = out_obj.bounding_box
        bounding1 = self.modeler.primitives[obj_name].bounding_box
        tol = 1e-9
        i = 0
        internal = False
        for a, b in zip(bounding1, bounding2):
            if i < 3:
                if (b - a) > tol:
                    internal = True
            elif (b - a) < tol:
                internal = True
            i += 1
        if internal:
            self.odesign.Undo()
            self.modeler.primitives.cleanup_objects()
            out_obj = self.modeler.thicken_sheet(obj, -pecthick, False)

        out_obj.material_name = "pec"
        return True

    @aedt_exception_handler
    def create_wave_port_microstrip_between_objects(
        self,
        startobj,
        endobject,
        axisdir=0,
        impedance=50,
        nummodes=1,
        portname=None,
        renorm=True,
        deembed_dist=0,
        vfactor=3,
        hfactor=5,
    ):
        """Create a waveport taking the closest edges of two objects.

        Parameters
        ----------
        startobj :
            First (starting) object for the integration line. This is typically the reference plane.
        endobject :
            Second (ending) object for the integration line.
        axisdir : int or :class:`pyaedt.application.Analysis.Analysis.AxisDir`, optional
            Position of the port. It should be one of the values for ``Application.AxisDir``,
            which are: ``XNeg``, ``YNeg``, ``ZNeg``, ``XPos``, ``YPos``, and ``ZPos``.
            The default is ``Application.AxisDir.XNeg``.
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
        :class:`pyaedt.modules.Boundary.BoundaryObject`
            Port object.

        References
        ----------

        >>> oModule.AssignWavePort

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
        pyaedt info: Connection Correctly created

        """
        if not self.modeler.primitives.does_object_exists(startobj) or not self.modeler.primitives.does_object_exists(
            endobject
        ):
            self.logger.error("One or both objects do not exist. Check and retry.")
            return False
        if self.solution_type in ["DrivenModal", "DrivenTerminal", "Transient Network"]:
            sheet_name, point0, point1 = self.modeler._create_microstrip_sheet_from_object_closest_edge(
                startobj, endobject, axisdir, vfactor, hfactor
            )
            dist = GeometryOperators.points_distance(point0, point1)
            self._create_pec_cap(sheet_name, startobj, dist / 10)
            if not portname:
                portname = generate_unique_name("Port")
            elif portname + ":1" in self.modeler.get_excitations_name():
                portname = generate_unique_name(portname)
            if self.solution_type == "DrivenModal":
                return self._create_waveport_driven(
                    sheet_name, point0, point1, impedance, portname, renorm, nummodes, deembed_dist
                )
            else:
                faces = self.modeler.primitives.get_object_faces(sheet_name)
                return self._create_port_terminal(faces[0], endobject, portname, iswaveport=True)
        return False

    @aedt_exception_handler
    def create_perfecte_from_objects(
        self, startobj, endobject, axisdir=0, sourcename=None, is_infinite_gnd=False, bound_on_plane=True
    ):
        """Create a Perfect E taking the closest edges of two objects.

        Parameters
        ----------
        startobj :
            First object (starting object for integration line)
        endobject :
            Second object (ending object for integration line)
        axisdir : int or :class:`pyaedt.application.Analysis.Analysis.AxisDir`, optional
            Position of the port. It should be one of the values for
            ``Application.AxisDir``, which are: ``XNeg``, ``YNeg``,
            ``ZNeg``, ``XPos``, ``YPos``, and ``ZPos``.  The default
            is ``Application.AxisDir.XNeg``.
        sourcename : str, optional
            Perfect E name. The default is ``None``.
        is_infinite_gnd : bool, optional
            Whether the Perfect E is an infinite ground. The default is ``False``.
        bound_on_plane : bool, optional
            Whether to create the Perfect E on the plane orthogonal to
            ``AxisDir``. The default is ``True``.

        Returns
        -------
        :class:`pyaedt.modules.Boundary.BoundaryObject` or bool
            Boundary object if successful, ``False`` otherwise.

        References
        ----------

        >>> oModule.AssignPerfectE

        Examples
        --------

        Create two boxes that will be used to create a Perfect E named ``'PerfectE'``.

        >>> box1 = hfss.modeler.primitives.create_box([0,0,0], [10,10,5],
        ...                                           "perfect1", "Copper")
        >>> box2 = hfss.modeler.primitives.create_box([0, 0, 10], [10, 10, 5],
        ...                                           "perfect2", "copper")
        >>> perfect_e = hfss.create_perfecte_from_objects("perfect1", "perfect2",
        ...                                               hfss.AxisDir.ZNeg, "PerfectE")
        pyaedt info: Connection Correctly created
        >>> type(perfect_e)
        <class 'pyaedt.modules.Boundary.BoundaryObject'>

        """

        if not self.modeler.primitives.does_object_exists(startobj) or not self.modeler.primitives.does_object_exists(
            endobject
        ):
            self.logger.error("One or both objects do not exist. Check and retry.")
            return False
        if self.solution_type in ["DrivenModal", "DrivenTerminal", "Transient Network"]:
            sheet_name, point0, point1 = self.modeler._create_sheet_from_object_closest_edge(
                startobj, endobject, axisdir, bound_on_plane
            )

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
        axisdir : int or :class:`pyaedt.application.Analysis.Analysis.AxisDir`, optional
            Position of the port. It should be one of the values for ``Application.AxisDir``,
            which are: ``XNeg``, ``YNeg``, ``ZNeg``, ``XPos``, ``YPos``, and ``ZPos``.
            The default is ``Application.AxisDir.XNeg``.
        sourcename : str, optional
            Perfect H name. The default is ``None``.
        bound_on_plane : bool, optional
            Whether to create the Perfect H on the plane orthogonal to ``AxisDir``. The default is ``True``.

        Returns
        -------
        :class:`pyaedt.modules.Boundary.BoundaryObject` or bool
            Boundary object if successful, ``False`` otherwise.

        References
        ----------

        >>> oModule.AssignPerfectH

        Examples
        --------

        Create two boxes that will be used to create a Perfect H named ``'PerfectH'``.

        >>> box1 = hfss.modeler.primitives.create_box([0,0,20], [10,10,5],
        ...                                           "perfect1", "Copper")
        >>> box2 = hfss.modeler.primitives.create_box([0, 0, 30], [10, 10, 5],
        ...                                           "perfect2", "copper")
        >>> perfect_h = hfss.create_perfecth_from_objects("perfect1", "perfect2",
        ...                                               hfss.AxisDir.ZNeg, "PerfectH")
        pyaedt info: Connection Correctly created
        >>> type(perfect_h)
        <class 'pyaedt.modules.Boundary.BoundaryObject'>

        """

        if not self.modeler.primitives.does_object_exists(startobj) or not self.modeler.primitives.does_object_exists(
            endobject
        ):
            self.logger.error("One or both objects do not exist. Check and retry.")
            return False
        if self.solution_type in ["DrivenModal", "DrivenTerminal", "Transient Network"]:
            sheet_name, point0, point1 = self.modeler._create_sheet_from_object_closest_edge(
                startobj, endobject, axisdir, bound_on_plane
            )

            if not sourcename:
                sourcename = generate_unique_name("PerfH")
            elif sourcename in self.modeler.get_boundaries_name():
                sourcename = generate_unique_name(sourcename)
            return self.create_boundary(self.BoundaryType.PerfectH, sheet_name, sourcename)
        return None

    @aedt_exception_handler
    def SARSetup(self, Tissue_object_List_ID, TissueMass=1, MaterialDensity=1, voxel_size=1, Average_SAR_method=0):
        """Define SAR settings.

        .. deprecated:: 0.4.5
           Use :func:`Hfss.sar_setup` instead.

        """
        warnings.warn("`SARSetup` is deprecated. Use `sar_setup` instead.", DeprecationWarning)
        self.sar_setup(Tissue_object_List_ID, TissueMass, MaterialDensity, voxel_size, Average_SAR_method)

    @aedt_exception_handler
    def sar_setup(self, Tissue_object_List_ID, TissueMass=1, MaterialDensity=1, voxel_size=1, Average_SAR_method=0):
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
        bool
            ``True`` when successful, ``False`` when failed.

        References
        ----------

        >>> oDesign.SARSetup
        """
        self.odesign.SARSetup(TissueMass, MaterialDensity, Tissue_object_List_ID, voxel_size, Average_SAR_method)
        self.logger.info("SAR Settings correctly applied.")
        return True

    @aedt_exception_handler
    def create_open_region(self, Frequency="1GHz", Boundary="Radiation", ApplyInfiniteGP=False, GPAXis="-z"):
        """Create an open region on the active editor.

        Parameters
        ----------
        Frequency : str, optional
            Frequency with units. The  default is ``"1GHz"``.
        Boundary : str, optional
            Type of the boundary. The default is ``"Radiation"``.
        ApplyInfiniteGP : bool, optional
            Whether to apply an infinite ground plane. The default is ``False``.
        GPAXis : str, optional
            The default is ``"-z"``.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.

        References
        ----------

        >>> oModule.CreateOpenRegion
        """
        vars = ["NAME:Settings", "OpFreq:=", Frequency, "Boundary:=", Boundary, "ApplyInfiniteGP:=", ApplyInfiniteGP]
        if ApplyInfiniteGP:
            vars.append("Direction:=")
            vars.append(GPAXis)

        self.omodelsetup.CreateOpenRegion(vars)
        self.logger.info("Open Region correctly created.")
        return True

    @aedt_exception_handler
    def create_lumped_rlc_between_objects(
        self,
        startobj,
        endobject,
        axisdir=0,
        sourcename=None,
        rlctype="Parallel",
        Rvalue=None,
        Lvalue=None,
        Cvalue=None,
        bound_on_plane=True,
    ):
        """Create a lumped RLC taking the closest edges of two objects.

        Parameters
        ----------
        startobj :
            First (starting) object for the integration line.
        endobject :
            Second (ending) object for the integration line.
        axisdir : int or :class:`pyaedt.application.Analysis.Analysis.AxisDir`, optional
            Position of the port. It should be one of the values for ``Application.AxisDir``,
            which are: ``XNeg``, ``YNeg``, ``ZNeg``, ``XPos``, ``YPos``, and ``ZPos``.
            The default is ``Application.AxisDir.XNeg``.
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
        :class:`pyaedt.modules.Boundary.BoundaryObject` or bool
            Boundary object if successful, ``False`` otherwise.

        References
        ----------

        >>> oModule.AssignLumpedRLC

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
        pyaedt info: Connection Correctly created

        """

        if not self.modeler.primitives.does_object_exists(startobj) or not self.modeler.primitives.does_object_exists(
            endobject
        ):
            self.logger.error("One or both objects do not exist. Check and retry.")
            return False
        if self.solution_type in ["DrivenModal", "DrivenTerminal", "Transient Network"] and (
            Rvalue or Lvalue or Cvalue
        ):
            sheet_name, point0, point1 = self.modeler._create_sheet_from_object_closest_edge(
                startobj, endobject, axisdir, bound_on_plane
            )

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
    def create_impedance_between_objects(
        self,
        startobj,
        endobject,
        axisdir=0,
        sourcename=None,
        resistance=50,
        reactance=0,
        is_infground=False,
        bound_on_plane=True,
    ):
        """Create an impedance taking the closest edges of two objects.

        Parameters
        ----------
        startobj :
            First (starting) object for the integration line.
        endobject :
            Second (ending) object for the integration line.
        axisdir : int or :class:`pyaedt.application.Analysis.Analysis.AxisDir`, optional
            Position of the port. It should be one of the values for ``Application.AxisDir``,
            which are: ``XNeg``, ``YNeg``, ``ZNeg``, ``XPos``, ``YPos``, and ``ZPos``.
            The default is ``Application.AxisDir.XNeg``.
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
        :class:`pyaedt.modules.Boundary.BoundaryObject` or bool
            Boundary object if successful, ``False`` otherwise.

        References
        ----------

        >>> oModule.AssignImpedance

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
        pyaedt info: Connection Correctly created

        """

        if not self.modeler.primitives.does_object_exists(startobj) or not self.modeler.primitives.does_object_exists(
            endobject
        ):
            self.logger.error("One or both objects do not exist. Check and retry.")
            return False
        if self.solution_type in ["DrivenModal", "DrivenTerminal", "Transient Network"]:
            sheet_name, point0, point1 = self.modeler._create_sheet_from_object_closest_edge(
                startobj, endobject, axisdir, bound_on_plane
            )

            if not sourcename:
                sourcename = generate_unique_name("Imped")
            elif sourcename in self.modeler.get_boundaries_name():
                sourcename = generate_unique_name(sourcename)
            props = OrderedDict(
                {
                    "Objects": [sheet_name],
                    "Resistance": str(resistance),
                    "Reactance": str(reactance),
                    "InfGroundPlane": is_infground,
                }
            )
            return self._create_boundary(sourcename, props, "Impedance")
        return False

    @aedt_exception_handler
    def create_boundary(
        self, boundary_type=BoundaryType.PerfectE, sheet_name=None, boundary_name="", is_infinite_gnd=False
    ):
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
        :class:`pyaedt.modules.Boundary.BoundaryObject`
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
            props["InfGroundPlane"] = is_infinite_gnd
            boundary_type = "PerfectE"
        elif boundary_type == self.BoundaryType.PerfectH:
            boundary_type = "PerfectH"
        elif boundary_type == self.BoundaryType.Aperture:
            boundary_type = "Aperture"
        elif boundary_type == self.BoundaryType.Radiation:
            props["IsFssReference"] = False
            props["IsForPML"] = False
            boundary_type = "Radiation"
        else:
            return None
        return self._create_boundary(boundary_name, props, boundary_type)

    @aedt_exception_handler
    def _get_reference_and_integration_points(self, sheet, axisdir, obj_name=None):
        if isinstance(sheet, int):
            objID = [sheet]
            sheet = obj_name
        else:
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
    def create_wave_port_from_sheet(
        self, sheet, deemb=0, axisdir=0, impedance=50, nummodes=1, portname=None, renorm=True
    ):
        """Create a waveport on sheet objects created starting from sheets.

        Parameters
        ----------
        sheet : list
            List of input sheets to create the waveport from.
        deemb : float, optional
            Deembedding value distance in model units. The default is ``0``.
        axisdir : int or :class:`pyaedt.application.Analysis.Analysis.AxisDir`, optional
            Position of the port. It should be one of the values for ``Application.AxisDir``,
            which are: ``XNeg``, ``YNeg``, ``ZNeg``, ``XPos``, ``YPos``, and ``ZPos``.
            The default is ``Application.AxisDir.XNeg``.
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

        References
        ----------

        >>> oModule.AssignWavePort

        Examples
        --------

        Create a circle sheet that will be used to create a wave port named
        ``'WavePortFromSheet'``.

        >>> origin_position = hfss.modeler.Position(0, 0, 0)
        >>> circle = hfss.modeler.primitives.create_circle(hfss.PLANE.YZ,
        ...                                                origin_position, 10, name="WaveCircle")
        >>> hfss.solution_type = "DrivenModal"
        >>> port = hfss.create_wave_port_from_sheet(circle, 5, hfss.AxisDir.XNeg, 40, 2,
        ...                                         "WavePortFromSheet", True)
        >>> port[0].name
        'WavePortFromSheet'

        """

        sheet = self.modeler.convert_to_selections(sheet, True)
        obj_names = []
        for sh in sheet:
            if isinstance(sh, int):
                try:
                    obj_names.append(self.modeler.oeditor.GetObjectNameByFaceID(sh))
                except:
                    obj_names.append("")
            else:
                obj_names.append("")
        portnames = []
        for obj, oname in zip(sheet, obj_names):
            refid, int_start, int_stop = self._get_reference_and_integration_points(obj, axisdir, oname)

            if not portname:
                portname = generate_unique_name("Port")
            elif portname + ":1" in self.modeler.get_excitations_name():
                portname = generate_unique_name(portname)
            if self.solution_type == "DrivenModal":
                b = self._create_waveport_driven(obj, int_start, int_stop, impedance, portname, renorm, nummodes, deemb)
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
    def create_lumped_port_to_sheet(
        self, sheet_name, axisdir=0, impedance=50, portname=None, renorm=True, deemb=False, reference_object_list=[]
    ):
        """Create a lumped port taking one sheet.

        Parameters
        ----------
        sheet_name : str
            Name of the sheet.
        axisdir : int or :class:`pyaedt.application.Analysis.Analysis.AxisDir`, optional
            Position of the port. It should be one of the values for ``Application.AxisDir``,
            which are: ``XNeg``, ``YNeg``, ``ZNeg``, ``XPos``, ``YPos``, and ``ZPos``.
            The default is ``Application.AxisDir.XNeg``.
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
        :class:`pyaedt.modules.Boundary.BoundaryObject`
            Boundary object.

        References
        ----------

        >>> oModule.AssignLumpedPort

        Examples
        --------

        Create a rectangle sheet that will be used to create a lumped port named
        ``'LumpedPortFromSheet'``.

        >>> rectangle = hfss.modeler.primitives.create_rectangle(hfss.PLANE.XY,
        ...                                                      [0, 0, 0], [10, 2], name="lump_port",
        ...                                                      matname="copper")
        >>> h1 = hfss.create_lumped_port_to_sheet(rectangle.name, hfss.AxisDir.XNeg, 50,
        ...                                  "LumpedPortFromSheet", True, False)

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
                port = self._create_lumped_driven(sheet_name, point0, point1, impedance, portname, renorm, deemb)
            else:
                if not reference_object_list:
                    cond = self.get_all_conductors_names()
                    touching = self.modeler.primitives.get_bodynames_from_position(point0)
                    reference_object_list = []
                    for el in touching:
                        if el in cond:
                            reference_object_list.append(el)
                faces = self.modeler.primitives.get_object_faces(sheet_name)
                port = self._create_port_terminal(faces[0], reference_object_list, portname, iswaveport=False)
            return port
        return False

    @aedt_exception_handler
    def assig_voltage_source_to_sheet(self, sheet_name, axisdir=0, sourcename=None):
        """Create a voltage source taking one sheet.

        .. deprecated:: 0.4.0
           Use :func:`Hfss.assign_voltage_source_to_sheet` instead.

        """

        warnings.warn(
            "`assig_voltage_source_to_sheet` is deprecated. Use `assign_voltage_source_to_sheet` instead.",
            DeprecationWarning,
        )
        self.assign_voltage_source_to_sheet(sheet_name, axisdir=0, sourcename=None)

    @aedt_exception_handler
    def assign_voltage_source_to_sheet(self, sheet_name, axisdir=0, sourcename=None):
        """Create a voltage source taking one sheet.

        Parameters
        ----------
        sheet_name : str
            Name of the sheet to apply the boundary to.
        axisdir : int or :class:`pyaedt.application.Analysis.Analysis.AxisDir`, optional
            Position of the port. It should be one of the values for ``Application.AxisDir``,
            which are: ``XNeg``, ``YNeg``, ``ZNeg``, ``XPos``, ``YPos``, and ``ZPos``.
            The default is ``Application.AxisDir.XNeg``.
        sourcename : str, optional
            Name of the source. The default is ``None``.

        Returns
        -------
        :class:`pyaedt.modules.Boundary.BoundaryObject`
            Boundary object.

        References
        ----------

        >>> oModule.AssignVoltage

        Examples
        --------

        Create a sheet and assign to it some voltage.

        >>> sheet = hfss.modeler.primitives.create_rectangle(hfss.PLANE.XY,
        ...                                                  [0, 0, -70], [10, 2], name="VoltageSheet",
        ...                                                  matname="copper")
        >>> v1 = hfss.assign_voltage_source_to_sheet(sheet.name, hfss.AxisDir.XNeg, "VoltageSheetExample")

        """

        if self.solution_type in ["DrivenModal", "DrivenTerminal", "Transient Network"]:
            point0, point1 = self.modeler.primitives.get_mid_points_on_dir(sheet_name, axisdir)
            if not sourcename:
                sourcename = generate_unique_name("Voltage")
            elif sourcename + ":1" in self.modeler.get_excitations_name():
                sourcename = generate_unique_name(sourcename)
            return self.create_source_excitation(sheet_name, point0, point1, sourcename, sourcetype="Voltage")
        return False

    @aedt_exception_handler
    def assign_current_source_to_sheet(self, sheet_name, axisdir=0, sourcename=None):
        """Create a current source taking one sheet.

        Parameters
        ----------
        sheet_name : str
            Name of the sheet to apply the boundary to.
        axisdir : int or :class:`pyaedt.application.Analysis.Analysis.AxisDir`, optional
            Position of the port. It should be one of the values for ``Application.AxisDir``,
            which are: ``XNeg``, ``YNeg``, ``ZNeg``, ``XPos``, ``YPos``, and ``ZPos``.
            The default is ``Application.AxisDir.XNeg``.
        sourcename : str, optional
            Name of the source. The default is ``None``.

        Returns
        -------
        str
            Name of the source created when successful, ``False`` otherwise.

        References
        ----------

        >>> oModule.AssignCurrent

        Examples
        --------

        Create a sheet and assign to it some current.

        >>> sheet = hfss.modeler.primitives.create_rectangle(hfss.PLANE.XY, [0, 0, -50],
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
            status = self.create_source_excitation(sheet_name, point0, point1, sourcename, sourcetype="Current")
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
        :class:`pyaedt.modules.Boundary.BoundaryObject`
            Boundary object.

        References
        ----------

        >>> oModule.AssignPerfectE

        Examples
        --------

        Create a sheet and use it to create a Perfect E.

        >>> sheet = hfss.modeler.primitives.create_rectangle(hfss.PLANE.XY, [0, 0, -90],
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
        :class:`pyaedt.modules.Boundary.BoundaryObject`
            Boundary object.

        References
        ----------

        >>> oModule.AssignPerfectH

        Examples
        --------

        Create a sheet and use it to create a Perfect H.

        >>> sheet = hfss.modeler.primitives.create_rectangle(hfss.PLANE.XY, [0, 0, -90],
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
    def assign_lumped_rlc_to_sheet(
        self, sheet_name, axisdir=0, sourcename=None, rlctype="Parallel", Rvalue=None, Lvalue=None, Cvalue=None
    ):
        """Create a lumped RLC taking one sheet.

        Parameters
        ----------
        sheet_name : str
            Name of the sheet to apply the boundary to.
        axisdir : int or :class:`pyaedt.application.Analysis.Analysis.AxisDir`, optional
            Position of the port. It should be one of the values for ``Application.AxisDir``,
            which are: ``XNeg``, ``YNeg``, ``ZNeg``, ``XPos``, ``YPos``, and ``ZPos``.
            The default is ``Application.AxisDir.XNeg``.
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
        :class:`pyaedt.modules.Boundary.BoundaryObject`
            Boundary object if successful, ``False`` otherwise

        References
        ----------

        >>> oModule.AssignLumpedRLC

        Examples
        --------

        Create a sheet and use it to create a lumped RLC.

        >>> sheet = hfss.modeler.primitives.create_rectangle(hfss.PLANE.XY,
        ...                                                  [0, 0, -90], [10, 2], name="RLCSheet",
        ...                                                  matname="Copper")
        >>> lumped_rlc_to_sheet = hfss.assign_lumped_rlc_to_sheet(sheet.name, hfss.AxisDir.XPos,
        ...                                                       Rvalue=50, Lvalue=1e-9,
        ...                                                       Cvalue=1e-6)
        >>> type(lumped_rlc_to_sheet)
        <class 'pyaedt.modules.Boundary.BoundaryObject'>

        """

        if self.solution_type in ["DrivenModal", "DrivenTerminal", "Transient Network", "SBR+"] and (
            Rvalue or Lvalue or Cvalue
        ):
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
        :class:`pyaedt.modules.Boundary.BoundaryObject`
            Boundary object if successful, ``False`` otherwise.

        References
        ----------

        >>> oModule.AssignImpedance

        Examples
        --------

        Create a sheet and use it to create an impedance.

        >>> sheet = hfss.modeler.primitives.create_rectangle(hfss.PLANE.XY,
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
            props = OrderedDict(
                {
                    "Objects": [sheet_name],
                    "Resistance": str(resistance),
                    "Reactance": str(reactance),
                    "InfGroundPlane": is_infground,
                }
            )
            return self._create_boundary(sourcename, props, "Impedance")
        return False

    @aedt_exception_handler
    def create_circuit_port_from_edges(
        self,
        edge_signal,
        edge_gnd,
        port_name="",
        port_impedance="50",
        renormalize=False,
        renorm_impedance="50",
        deembed=False,
    ):
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

        References
        ----------

        >>> oModule.AssignCircuitPort

        Examples
        --------

        Create two rectangles in the XY plane.
        Select the first edge of each rectangle created previously.
        Create a circuit port from the first edge of the first rectangle
        toward the first edge of the second rectangle.

        >>> plane = hfss.PLANE.XY
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

        result = self._create_circuit_port(
            edge_list, port_impedance, port_name, renormalize, deembed, renorm_impedance=renorm_impedance
        )
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

        References
        ----------

        >>> oModule.EditSources

        Examples
        --------

        Create a circle sheet and use it to create a wave port.
        Set up the thermal power for the port created above.

        >>> sheet = hfss.modeler.primitives.create_circle(hfss.PLANE.YZ,
        ...                                               [-20, 0, 0], 10,
        ...                                               name="sheet_for_source")
        >>> hfss.solution_type = "DrivenModal"
        >>> wave_port = hfss.create_wave_port_from_sheet(sheet, 5, hfss.AxisDir.XNeg, 40,
        ...                                              2, "SheetWavePort", True)
        >>> hfss.edit_source("SheetWavePort" + ":1", "10W")
        pyaedt info: Setting up power to Eigenmode 10W
        True

        """

        self.logger.info("Setting up power to Eigenmode " + powerin)
        if self.solution_type != "Eigenmode":
            self.osolution.EditSources(
                [
                    ["IncludePortPostProcessing:=", True, "SpecifySystemPower:=", False],
                    ["Name:=", portandmode, "Magnitude:=", powerin, "Phase:=", phase],
                ]
            )
        else:
            self.osolution.EditSources(
                [["FieldType:=", "EigenStoredEnergy"], ["Name:=", "Modes", "Magnitudes:=", [powerin]]]
            )
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
        list of int
            List of the port IDs where thickened sheets were created.

        References
        ----------

        >>> oEditor.ThickenSheet

        Examples
        --------

        Create a circle sheet and use it to create a wave port.
        Set the thickness of this circle sheet to ``"2 mm"``.

        >>> sheet_for_thickness = hfss.modeler.primitives.create_circle(hfss.PLANE.YZ,
        ...                                                             [60, 60, 60], 10,
        ...                                                             name="SheetForThickness")
        >>> port_for_thickness = hfss.create_wave_port_from_sheet(sheet_for_thickness, 5, hfss.AxisDir.XNeg,
        ...                                                       40, 2, "WavePortForThickness", True)
        >>> hfss.thicken_port_sheets(["SheetForThickness"], 2)
        pyaedt info: done
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
                    ["NAME:Selections", "Selections:=", el, "NewPartsModelFlag:=", "Model"],
                    ["NAME:SheetThickenParameters", "Thickness:=", str(l) + "mm", "BothSides:=", False],
                )
                # aedt_bounding_box2 = self._oeditor.GetModelBoundingBox()
                aedt_bounding_box2 = self.modeler.primitives.get_model_bounding_box()
                self._odesign.Undo()
                if aedt_bounding_box != aedt_bounding_box2:
                    directions[el] = "External"
                    directionfound = True
                self.modeler.oeditor.ThickenSheet(
                    ["NAME:Selections", "Selections:=", el, "NewPartsModelFlag:=", "Model"],
                    ["NAME:SheetThickenParameters", "Thickness:=", "-" + str(l) + "mm", "BothSides:=", False],
                )
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
                    ["NAME:Selections", "Selections:=", el, "NewPartsModelFlag:=", "Model"],
                    ["NAME:SheetThickenParameters", "Thickness:=", "-" + str(value) + "mm", "BothSides:=", False],
                )
            else:
                self.modeler.oeditor.ThickenSheet(
                    ["NAME:Selections", "Selections:=", el, "NewPartsModelFlag:=", "Model"],
                    ["NAME:SheetThickenParameters", "Thickness:=", str(value) + "mm", "BothSides:=", False],
                )
            if "Vacuum" in el:
                newfaces = self.modeler.oeditor.GetFaceIDs(el)
                for f in newfaces:
                    try:
                        fc2 = self.modeler.oeditor.GetFaceCenter(f)
                        fc2 = [float(i) for i in fc2]
                        fa2 = self.modeler.primitives.get_face_area(int(f))
                        faceoriginal = [float(i) for i in faceCenter]
                        # dist = mat.sqrt(sum([(a*a-b*b) for a,b in zip(faceCenter, fc2)]))
                        if abs(fa2 - maxarea) < tol ** 2 and (
                            abs(faceoriginal[2] - fc2[2]) > tol
                            or abs(faceoriginal[1] - fc2[1]) > tol
                            or abs(faceoriginal[0] - fc2[0]) > tol
                        ):
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
                                ["NAME:Selections", "Selections:=", el, "NewPartsModelFlag:=", "Model"],
                                [
                                    "NAME:Parameters",
                                    [
                                        "NAME:MoveFacesParameters",
                                        "MoveAlongNormalFlag:=",
                                        True,
                                        "OffsetDistance:=",
                                        str(internalvalue) + "mm",
                                        "MoveVectorX:=",
                                        "0mm",
                                        "MoveVectorY:=",
                                        "0mm",
                                        "MoveVectorZ:=",
                                        "0mm",
                                        "FacesToMove:=",
                                        [int(fid)],
                                    ],
                                ],
                            )
                    except:
                        self.logger.info("done")
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
        list of str
            List of all the validation information for later use.
        bool
            Indicates if the validation was successful or not.

        References
        ----------

        >>> oDesign.ValidateDesign

        Examples
        --------

        Validate the current design and save the log file into
        the current project directory.

        >>> validation = hfss.validate_full_design()
        pyaedt info: Design Validation Checks
        >>> validation[1]
        False

        """

        self.logger.info("Design Validation Checks")
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
            temp2_msg = [i.strip("Project: " + pname + ", Design: " + dname + ", ").strip("\r\n") for i in temp_msg]
            val_list.extend(temp2_msg)

        # Run design validation and write out the lines to the log.
        temp_dir = tempfile.gettempdir()
        temp_val_file = os.path.join(temp_dir, "val_temp.log")
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
            with open(temp_val_file, "r") as df:
                temp = df.read().splitlines()
                val_list.extend(temp)
            os.remove(temp_val_file)
        else:
            msg = "** No design validation file is found. **"
            self.logger.info(msg)
            val_list.append(msg)
        msg = "** End of design validation messages. **"
        val_list.append(msg)

        # Find the excitations and check or list them out
        msg = "Excitations Check:"
        val_list.append(msg)
        if self.solution_type != "Eigenmode":
            detected_excitations = self.modeler.get_excitations_name()
            if ports:
                if self.solution_type == "DrivenTerminal":
                    # For each port, there is terminal and reference excitations.
                    ports_t = ports * 2
                else:
                    ports_t = ports
                if ports_t != len(detected_excitations):
                    msg = "** Port number error. Check the model. **"
                    self.logger.error(msg)
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
            self.logger.info(msg)
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
                if self.solution_type != "EigenMode":
                    sweepsname = self.oanalysis.GetSweeps(setup)
                    if sweepsname:
                        for sw in sweepsname:
                            msg = " |__ " + sw
                            val_list.append(msg)
        else:
            msg = "No setup is detected."
            val_list.append(msg)

        with open(validation_log_file, "w") as f:
            for item in val_list:
                f.write("%s\n" % item)
        return val_list, validation_ok  # Return all the information in a list for later use.

    @aedt_exception_handler
    def create_scattering(
        self, plot_name="S Parameter Plot Nominal", sweep_name=None, port_names=None, port_excited=None, variations=None
    ):
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

        References
        ----------

        >>> oModule.CreateReport

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
            self.logger.error("Setup %s doesn't exist in the Setup list.", sweep_name)
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
                plot_name, solution_data, "Rectangular Plot", sweep_name, ["Domain:=", "Sweep"], Families, Trace, []
            )
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

        References
        ----------

        >>> oModule.CreateReport

        """
        npath = os.path.normpath(project_dir)

        # Setup arguments list for createReport function
        args = [Xaxis + ":=", ["All"]]
        args2 = ["X Component:=", Xaxis, "Y Component:=", outputlist]

        self.post.post_oreport_setup.CreateReport(
            plotname, "Eigenmode Parameters", "Rectangular Plot", setupname + " : LastAdaptive", [], args, args2, []
        )
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
                appendix += "_" + v + vv.replace("'", "")
            ext = ".S" + str(self.oboundary.GetNumExcitations()) + "p"
            filename = os.path.join(self.project_path, solutionname + "_" + sweepname + appendix + ext)
        else:
            filename = filename.replace("//", "/").replace("\\", "/")
        print("Exporting Touchstone " + filename)
        DesignVariations = ""
        i = 0
        for el in variation:
            DesignVariations += str(variation[i]) + "='" + str(variations_value[i].replace("'", "")) + "' "
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

        self.osolution.ExportNetworkData(
            DesignVariations,
            SolutionSelectionArray,
            FileFormat,
            OutFile,
            FreqsArray,
            DoRenorm,
            RenormImped,
            DataType,
            Pass,
            ComplexFormat,
            DigitsPrecision,
            False,
            IncludeGammaImpedance,
            NonStandardExtensions,
        )
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

        References
        ----------

        >>> oDesign.SetDesignSettings
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
        obj_names : str or list or int or :class:`pyaedt.modeler.Object3d.Object3d`
             One or more object names or IDs.
        boundary_name : str, optional
             Name of the boundary. The default is ``""``.

        Returns
        -------
        :class:`pyaedt.modules.Boundary.BoundaryObject`
            Boundary object.

        References
        ----------

        >>> oModule.AssignRadiation

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
        :class:`pyaedt.modules.Boundary.BoundaryObject`
            Boundary object.

        References
        ----------

        >>> oModule.AssignRadiation

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
        faces_list = self.modeler.convert_to_selections(faces_id, True)
        if boundary_name:
            rad_name = boundary_name
        else:
            rad_name = generate_unique_name("Rad_")
        return self.create_boundary(self.BoundaryType.Radiation, faces_list, rad_name)

    @aedt_exception_handler
    def _create_sbr_doppler_setup(
        self,
        setup_type,
        time_var,
        center_freq,
        resolution,
        period,
        velocity_resolution,
        min_velocity,
        max_velocity,
        ray_density_per_wavelenght,
        max_bounces,
        setup_name,
        include_coupling_effects=False,
        doppler_ad_sampling_rate=20,
    ):
        setup1 = self.create_setup(setup_name, "SBR+")
        setup1.props["IsSbrRangeDoppler"] = True
        del setup1.props["PTDUTDSimulationSettings"]
        del setup1.props["ComputeFarFields"]
        del setup1.props["Sweeps"]
        if setup_type == "ChirpIQ":
            setup1.props["SbrRangeDopplerWaveformType"] = "ChirpSeqFmcw"
            setup1.props["ChannelConfiguration"] = "IQChannels"
        elif setup_type == "ChirpI":
            setup1.props["SbrRangeDopplerWaveformType"] = "ChirpSeqFmcw"
            setup1.props["ChannelConfiguration"] = "IChannelOnly"
        else:
            setup1.props["SbrRangeDopplerWaveformType"] = setup_type
        setup1.props["SbrRangeDopplerTimeVariable"] = time_var
        setup1.props["SbrRangeDopplerCenterFreq"] = self.modeler.primitives._arg_with_dim(center_freq, "GHz")
        setup1.props["SbrRangeDopplerRangeResolution"] = self.modeler.primitives._arg_with_dim(resolution, "meter")
        setup1.props["SbrRangeDopplerRangePeriod"] = self.modeler.primitives._arg_with_dim(period, "meter")
        setup1.props["SbrRangeDopplerVelocityResolution"] = self.modeler.primitives._arg_with_dim(
            velocity_resolution, "m_per_sec"
        )
        setup1.props["SbrRangeDopplerVelocityMin"] = self.modeler.primitives._arg_with_dim(min_velocity, "m_per_sec")
        setup1.props["SbrRangeDopplerVelocityMax"] = self.modeler.primitives._arg_with_dim(max_velocity, "m_per_sec")
        setup1.props["DopplerRayDensityPerWavelength"] = ray_density_per_wavelenght
        setup1.props["MaxNumberOfBounces"] = max_bounces
        if setup_type != "PulseDoppler":
            setup1.props["IncludeRangeVelocityCouplingEffect"] = include_coupling_effects
            setup1.props["SbrRangeDopplerA/DSamplingRate"] = self.modeler.primitives._arg_with_dim(
                doppler_ad_sampling_rate, "MHz"
            )
        setup1.update()
        return setup1

    @aedt_exception_handler
    def _create_sbr_doppler_sweep(self, setupname, time_var, tstart, tstop, tsweep, parametric_name):
        time_start = self.modeler.primitives._arg_with_dim(tstart, "s")
        time_sweep = self.modeler.primitives._arg_with_dim(tsweep, "s")
        time_stop = self.modeler.primitives._arg_with_dim(tstop, "s")
        sweep_range = "LIN {} {} {}".format(time_start, time_stop, time_sweep)
        return self.opti_parametric.add_parametric_setup(
            time_var, sweep_range, setupname, parametricname=parametric_name
        )

    @aedt_exception_handler
    def create_sbr_chirp_i_doppler_setup(
        self,
        time_var=None,
        sweep_time_duration=0,
        center_freq=76.5,
        resolution=1,
        period=200,
        velocity_resolution=0.4,
        min_velocity=-20,
        max_velocity=20,
        ray_density_per_wavelenght=0.2,
        max_bounces=5,
        include_coupling_effects=False,
        doppler_ad_sampling_rate=20,
        setup_name=None,
    ):
        """Create an SBR+ Chirp IQ Setup.

        Parameters
        ----------
        time_var : str, optional
            Name of the time variable. Default ``None`` which will search for first
            time variable available.
        sweep_time_duration : float, optional
            Sweep Time Duration. If greater than 0, a parametric sweep will be
            created. Default ``0``.
        center_freq : float, optional
            Center frequency in GHz. Default ``76.5``.
        resolution : float, optional
            Doppler resolution in meter. Default ``1``.
        period : float, optional
            Period of analysis in meter. Default ``200``.
        velocity_resolution : float, optional
            Doppler velocity resolution in meters per second. Default ``0.4``.
        min_velocity : str, optional
            Minimum doppler velocity in meters per second. Default ``-20``.
        max_velocity : str, optional
            Maximum doppler velocity in meters per second. Default ``20``.
        ray_density_per_wavelenght : float, optional
            Doppler ray density per wavelength. Default ``0.2``.
        max_bounces : int, optional
            Maximum number of Bounces. Default ``5``.
        include_coupling_effects : float, optional
            Set if coupling effects will be included. Default ``False``.
        doppler_ad_sampling_rate : float, optional
            Doppler AD sampling rate. It works only if ``include_coupling_effects``
            is ``True``. Default ``20``.
        setup_name : str, optional
            Name of the setup. Default ``None``.

        Returns
        -------
        (:class:`pyaedt.modules.SolveSetup.Setup`,
            :class:`pyaedt.modules.DesignXPloration.ParametericsSetups.Optimetrics`)

        References
        ----------

        >>> oModule.InsertSetup

        """
        if self.solution_type != "SBR+":
            self.logger.error("Method Applies only to SBR+ Solution.")
            return False, False
        if not setup_name:
            setup_name = generate_unique_name("ChirpI")
            parametric_name = generate_unique_name("PulseSweep")
        else:
            parametric_name = generate_unique_name(setup_name)

        if not time_var:
            for var_name, var in self.variable_manager.independent_variables.items():
                if var.unit_system == "Time":
                    time_var = var_name
                    break
            if not time_var:
                self.logger.error("No Time Variable Found. Setup or explicitly assign to the method.")
                raise ValueError("No Time Variable Found")
        setup = self._create_sbr_doppler_setup(
            "ChirpI",
            time_var=time_var,
            center_freq=center_freq,
            resolution=resolution,
            period=period,
            velocity_resolution=velocity_resolution,
            min_velocity=min_velocity,
            max_velocity=max_velocity,
            ray_density_per_wavelenght=ray_density_per_wavelenght,
            max_bounces=max_bounces,
            include_coupling_effects=include_coupling_effects,
            doppler_ad_sampling_rate=doppler_ad_sampling_rate,
            setup_name=setup_name,
        )
        if sweep_time_duration > 0:
            sweeptime = math.ceil(300000000 / (2 * center_freq * 1000000000 * velocity_resolution) * 1000) / 1000
            sweep = self._create_sbr_doppler_sweep(
                setup.name, time_var, 0, sweep_time_duration, sweeptime, parametric_name
            )
            return setup, sweep
        return setup, False

    @aedt_exception_handler
    def create_sbr_chirp_iq_doppler_setup(
        self,
        time_var=None,
        sweep_time_duration=0,
        center_freq=76.5,
        resolution=1,
        period=200,
        velocity_resolution=0.4,
        min_velocity=-20,
        max_velocity=20,
        ray_density_per_wavelenght=0.2,
        max_bounces=5,
        include_coupling_effects=False,
        doppler_ad_sampling_rate=20,
        setup_name=None,
    ):
        """Create an SBR+ Chirp IQ Setup.

        Parameters
        ----------
        time_var : str, optional
            Name of the time variable. Default ``None`` which will search for first
            time variable available.
        sweep_time_duration : float, optional
            Sweep Time Duration. If greater than 0, a parametric sweep will be
            created. Default ``0``.
        center_freq : float, optional
            Center Frequency in GHz. Default ``76.5``.
        resolution : float, optional
            Doppler Resolution in meter. Default ``1``.
        period : float, optional
            Period of Analysis in meter. Default ``200``.
        velocity_resolution : float, optional
            Doppler Velocity Resolution in meters per second. Default ``0.4``.
        min_velocity : str, optional
            Minimum Doppler Velocity in meters per second. Default ``-20``.
        max_velocity : str, optional
            Maximum Doppler Velocity in meters per second. Default ``20``.
        ray_density_per_wavelenght : float, optional
            Doppler Ray Density per wavelength. Default ``0.2``.
        max_bounces : int, optional
            Maximum number of Bounces. Default ``5``.
        include_coupling_effects : float, optional
            Set if Coupling Effects will be included. Default ``False``.
        doppler_ad_sampling_rate : float, optional
            Doppler AD Sampling Rate. It works only if ``include_coupling_effects`` is
            ``True``. Default ``20``.
        setup_name : str, optional
            Name of the Setup. Default ``None``.

        Returns
        -------
        (:class:`pyaedt.modules.SolveSetup.Setup`,
            :class:`pyaedt.modules.DesignXPloration.ParametericsSetups.Optimetrics`)

        References
        ----------

        >>> oModule.InsertSetup
        """
        if self.solution_type != "SBR+":
            self.logger.error("Method Applies only to SBR+ Solution.")
            return False, False
        if not setup_name:
            setup_name = generate_unique_name("ChirpIQ")
            parametric_name = generate_unique_name("PulseSweep")
        else:
            parametric_name = generate_unique_name(setup_name)
        if not time_var:
            for var_name, var in self.variable_manager.independent_variables.items():
                if var.unit_system == "Time":
                    time_var = var_name
                    break
            if not time_var:
                raise ValueError("No Time Variable Found")
        setup = self._create_sbr_doppler_setup(
            "ChirpIQ",
            time_var=time_var,
            center_freq=center_freq,
            resolution=resolution,
            period=period,
            velocity_resolution=velocity_resolution,
            min_velocity=min_velocity,
            max_velocity=max_velocity,
            ray_density_per_wavelenght=ray_density_per_wavelenght,
            max_bounces=max_bounces,
            include_coupling_effects=include_coupling_effects,
            doppler_ad_sampling_rate=doppler_ad_sampling_rate,
            setup_name=setup_name,
        )
        if sweep_time_duration > 0:
            sweeptime = math.ceil(300000000 / (2 * center_freq * 1000000000 * velocity_resolution) * 1000) / 1000
            sweep = self._create_sbr_doppler_sweep(
                setup.name, time_var, 0, sweep_time_duration, sweeptime, parametric_name
            )
            return setup, sweep
        return setup, False

    @aedt_exception_handler
    def create_sbr_pulse_doppler_setup(
        self,
        time_var=None,
        sweep_time_duration=0,
        center_freq=76.5,
        resolution=1,
        period=200,
        velocity_resolution=0.4,
        min_velocity=-20,
        max_velocity=20,
        ray_density_per_wavelenght=0.2,
        max_bounces=5,
        setup_name=None,
    ):
        """Create an SBR+ pulse doppler setup.

        Parameters
        ----------
        time_var : str, optional
            Name of the time variable. The default is ``None``, in which case
            the first time variable available is used.
        sweep_time_duration : float, optional
            Sweep time duration. If greater than 0, a parametric sweep is
            created. The default is ``0``.
        center_freq : float, optional
            Center frequency in GHz. The default is ``76.5``.
        resolution : float, optional
            Doppler resolution in meters. The default is ``1``.
        period : float, optional
            Period of analysis in meters. The default is ``200``.
        velocity_resolution : float, optional
            Doppler velocity resolution in meters per second.
            The default is ``0.4``.
        min_velocity : str, optional
            Minimum doppler velocity in meters per second. The default
            is ``-20``.
        max_velocity : str, optional
            Maximum doppler velocity in meters per second. The default
            is ``20``.
        ray_density_per_wavelenght : float, optional
            Doppler ray density per wavelength. The default is ``0.2``.
        max_bounces : int, optional
            Maximum number of bBounces. The default is ``5``.
        setup_name : str, optional
            Name of the setup. The default is ``None``.

        Returns
        -------
        (:class:`pyaedt.modules.SolveSetup.Setup`,
            :class:`pyaedt.modules.DesignXPloration.ParametericsSetups.Optimetrics`)

        References
        ----------

        >>> oModule.InsertSetup
        """
        if self.solution_type != "SBR+":
            self.logger.error("Method Applies only to SBR+ Solution.")
            return False, False
        if not setup_name:
            setup_name = generate_unique_name("PulseSetup")
            parametric_name = generate_unique_name("PulseSweep")
        else:
            parametric_name = generate_unique_name(setup_name)

        if not time_var:
            for var_name, var in self.variable_manager.independent_variables.items():
                if var.unit_system == "Time":
                    time_var = var_name
                    break
            if not time_var:
                raise ValueError("No Time Variable Found")
        setup = self._create_sbr_doppler_setup(
            "PulseDoppler",
            time_var=time_var,
            center_freq=center_freq,
            resolution=resolution,
            period=period,
            velocity_resolution=velocity_resolution,
            min_velocity=min_velocity,
            max_velocity=max_velocity,
            ray_density_per_wavelenght=ray_density_per_wavelenght,
            max_bounces=max_bounces,
            setup_name=setup_name,
        )
        if sweep_time_duration > 0:
            sweeptime = math.ceil(300000000 / (2 * center_freq * 1000000000 * velocity_resolution) * 1000) / 1000
            sweep = self._create_sbr_doppler_sweep(
                setup.name, time_var, 0, sweep_time_duration, sweeptime, parametric_name
            )
            return setup, sweep
        return setup, False

    @aedt_exception_handler
    def create_sbr_radar_from_json(
        self, radar_file, radar_name, offset=[0, 0, 0], speed=0.0, use_relative_cs=False, relative_cs_name=None
    ):
        """Create an SBR+ radar from a JSON file.

        Example of input JSON file:

          .. code-block:: json

            {
                "name": "Example_1Tx_1Rx",
                "version": 1,
                "number_tx":"1",
                "number_rx":"1",
                "units":"mm",
                "antennas": {
                    "tx1": {
                        "antenna_type":"parametric",
                        "mode":"tx",
                        "offset":["0" ,"0" ,"0"],
                        "rotation_axis":null,
                        "rotation":null,
                        "beamwidth_elevation":"10deg",
                        "beamwidth_azimuth":"60deg",
                        "polarization":"Vertical"
                        },
                    "rx1": {
                        "antenna_type":"parametric",
                        "mode":"rx",
                        "offset":["0" ,"1.8" ,"0"],
                        "rotation_axis":null,
                        "rotation":null,
                        "beamwidth_elevation":"10deg",
                        "beamwidth_azimuth":"60deg",
                        "polarization":"Vertical"
                        }
                }
            }

        Parameters
        ----------
        radar_file : str
            Path to the directory with the radar file.
        radar_name : str
            Name of the radar file.
        offset : list, optional
            Offset relative to the global coordinate system.
        speed : float, optional
            Radar movement speed relative to the global coordinate system if greater than ``0``.
        use_relative_cs : bool, optional
            Whether the relative coordinate system must be used. The default is ``False``.
        relative_cs_name : str
            Name of the relative coordinate system to link the radar to.
            The default is ``None``, in which case the global coordinate system is used.

        Returns
        -------
        :class:`pyaedt.modeler.actors.Radar`
            Radar Class object.

        References
        ----------
        AEDT API Commands.

        >>> oEditor.CreateRelativeCS
        >>> oModule.SetSBRTxRxSettings
        >>> oEditor.CreateGroup
        """
        self.modeler.primitives._initialize_multipart()
        if self.solution_type != "SBR+":
            self.logger.error("Method Applies only to SBR+ Solution.")
            return False
        use_motion = abs(speed) > 0.0
        r = Radar(
            radar_file,
            name=radar_name,
            motion=use_motion,
            offset=offset,
            speed=speed,
            use_relative_cs=(use_relative_cs or use_motion),
            relative_cs_name=relative_cs_name,
        )
        r.insert(self, abs(speed) > 0)
        return r

    @aedt_exception_handler
    def insert_infinite_sphere(
        self,
        definition=INFINITE_SPHERE_TYPE.ThetaPhi,
        x_start=0,
        x_stop=180,
        x_step=10,
        y_start=0,
        y_stop=180,
        y_step=10,
        units="deg",
        custom_radiation_faces=None,
        custom_coordinate_system=None,
        use_slant_polarization=False,
        polarization_angle=45,
        name=None,
    ):
        """Create a new infinite Sphere.

        .. note::
           Not supported in all HFSS EigenMode and CharacteristicMode Solution Types.

        Parameters
        ----------
        definition : str
            Coordinate Definition Type. Default is "Theta-Phi".
            It can be a ``pyaedt.generic.constants.INFINITE_SPHERE_TYPE`` Enumerator value.
        x_start : float, str
            First angle start value.
        x_stop : float, str
            First angle stop value.
        x_step : float, str
            First angle step value.
        y_start : float, str
            Second angle start value.
        y_stop : float, str
            Second angle stop value.
        y_step : float, str
            Second angle step value.
        units : str
            Angle units. Default is `"deg"`.
        custom_radiation_faces : str
            Radiation Face list to be used for far field computation.
        custom_coordinate_system : str
            Local Coordinate System to be used for far field computation.
        use_slant_polarization : bool
            Define if Slant Polarization will be used. Default is `False`.
        polarization_angle : float, str
            Slant angle value.
        name : str
            Sphere Name.

        Returns
        -------
        :class:`pyaedt.modules.Boundary.FarFieldSetup`
        """
        if not self.oradfield:
            self.logger.error("Radiation Field not available in this solution.")
        if not name:
            name = generate_unique_name("Infinite")

        props = OrderedDict({"UseCustomRadiationSurface": custom_radiation_faces is not None})
        if custom_radiation_faces:
            props["CustomRadiationSurface"] = custom_radiation_faces
        else:
            props["CustomRadiationSurface"] = ""
        props["CSDefinition"] = definition
        if use_slant_polarization:
            props["Polarization"] = "Slant"
        else:
            props["Polarization"] = "Linear"
        props["SlantAngle"] = self.modeler._arg_with_dim(polarization_angle, units)

        if definition == "Theta-Phi":
            defs = ["ThetaStart", "ThetaStop", "ThetaStep", "PhiStart", "PhiStop", "PhiStep"]
        elif definition == "El Over Az":
            defs = ["AzimuthStart", "AzimuthStop", "AzimuthStep", "ElevationStart", "ElevationStop", "ElevationStep"]
        else:
            defs = ["ElevationStart", "ElevationStop", "ElevationStep", "AzimuthStart", "AzimuthStop", "AzimuthStep"]
        props[defs[0]] = self.modeler._arg_with_dim(x_start, units)
        props[defs[1]] = self.modeler._arg_with_dim(x_stop, units)
        props[defs[2]] = self.modeler._arg_with_dim(x_step, units)
        props[defs[3]] = self.modeler._arg_with_dim(y_start, units)
        props[defs[4]] = self.modeler._arg_with_dim(y_stop, units)
        props[defs[5]] = self.modeler._arg_with_dim(y_step, units)
        props["UseLocalCS"] = custom_coordinate_system is not None
        if custom_coordinate_system:
            props["CoordSystem"] = custom_coordinate_system
        else:
            props["CoordSystem"] = ""
        bound = FarFieldSetup(self, name, props, "FarFieldSphere", units)
        if bound.create():
            self.field_setups.append(bound)
            return bound
        return False

    @aedt_exception_handler
    def set_sbr_current_sources_options(self, conformance=False, thin_sources=False, power_fraction=0.95):
        """Set Current Sources SBR+ Setup Options.

        Parameters
        ----------
        conformance : bool
            ``True`` to Enable current source conformance. Default is ``False``
        thin_sources : bool
            ``True`` to Enable current Thin Sources. Default is ``False``
        power_fraction : float or str
            if thin_sources is enabled then sets the power fraction. Default is ``0.95``

        Returns
        -------
        bool

        References
        ----------

        >>> oModule.EditGlobalCurrentSourcesOption
        """
        if self.solution_type != "SBR+":
            self.logger.error("Method Applies only to SBR+ Solution.")
            return False
        current_conformance = "Disable"
        if conformance:
            current_conformance = "Enable"
        arg = [
            "NAME:CurrentSourceOption",
            "Current Source Conformance:=",
            current_conformance,
            "Thin Sources:=",
            thin_sources,
        ]
        if thin_sources:
            arg.append("Power Fraction:=")
            arg.append(str(power_fraction))
        self.oboundary.EditGlobalCurrentSourcesOption(arg)
        self.logger.info("SBR+ current source options correctly applied.")
        return True
