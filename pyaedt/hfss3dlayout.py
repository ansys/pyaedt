"""This module contains these classes: `Hfss3dLayout`."""

from __future__ import absolute_import

import os
import warnings

from pyaedt.application.Analysis3DLayout import FieldAnalysis3DLayout
from pyaedt.generic.general_methods import aedt_exception_handler, generate_unique_name


class Hfss3dLayout(FieldAnalysis3DLayout):
    """Provides the HFSS 3D Layout application interface.

    This class inherits all objects that belong to HFSS 3D Layout, including EDB
    API queries.

    Parameters
    ----------
    projectname : str, optional
        Name of the project to select or the full path to the project
        or AEDTZ archive to open.  The default is ``None``, in which
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
    non_graphical : bool, optional
        Whether to launch AEDT in the non-graphical mode. The default
        is``False``, in which case AEDT is launched in the graphical mode.
    new_desktop_session : bool, optional
        Whether to launch an instance of AEDT in a new thread, even if
        another instance of the ``specified_version`` is active on the
        machine. The default is ``True``.
    close_on_exit : bool, optional
        Whether to release AEDT on exit.
    student_version : bool, optional
        Whether to open the AEDT student version. The default is ``False``.

    Examples
    --------
    Create an `Hfss3dLayout` object and connect to an existing HFSS
    design or create a new HFSS design if one does not exist.

    >>> from pyaedt import Hfss3dLayout
    >>> aedtapp = Hfss3dLayout()

    Create an `Hfss3dLayout` object and link to a project named
    ``projectname``. If this project does not exist, create one with
    this name.

    >>> aedtapp = Hfss3dLayout(projectname)

    Create an `Hfss3dLayout` object and link to a design named
    ``designname`` in a project named ``projectname``.

    >>> aedtapp = Hfss3dLayout(projectname,designame)

    Create an `Hfss3dLayout` object and open the specified project.

    >>> aedtapp = Hfss3dLayout("myfile.aedt")

    Create an AEDT 2021 R1 object and then create a
    `Hfss3dLayout` object and open the specified project.

    >>> aedtapp = Hfss3dLayout(specified_version="2021.2", projectname="myfile.aedt")

    """

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
        FieldAnalysis3DLayout.__init__(
            self,
            "HFSS 3D Layout Design",
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

    def __enter__(self):
        return self

    @aedt_exception_handler
    def create_edge_port(self, primivitivename, edgenumber, iscircuit=True):
        """Create an edge port.

        Parameters
        ----------
        primivitivename : str
            Name of the primitive to create the edge port on.
        edgenumber :
            Edge number to create the edge port on.
        iscircuit : bool, optional
            Whether the edge port is a circuit port. The default is ``False``.

        Returns
        -------
        type
            Name of the port when successful, ``False`` when failed.

        References
        ----------

        >>> oEditor.CreateEdgePort
        """
        listp = self.port_list
        self.modeler.oeditor.CreateEdgePort(
            [
                "NAME:Contents",
                "edge:=",
                ["et:=", "pe", "prim:=", primivitivename, "edge:=", edgenumber],
                "circuit:=",
                iscircuit,
                "btype:=",
                0,
            ]
        )
        listnew = self.port_list
        a = [i for i in listnew if i not in listp]
        if len(a) > 0:
            return a[0]
        else:
            return False

    @aedt_exception_handler
    def create_wave_port_from_two_conductors(self, primivitivenames=[""], edgenumbers=[""]):
        """Create a wave port.

        Parameters
        ----------
        primivitivenames : list(str)
            List of the of the primitive name to create the wave port on.
            The list length must be 2 e.g. for the two conductors or the command will not be executed.

        edgenumbers :
            List of the edge number to create the wave port on.
            The list length must be 2 e.g. for the two edges or the command will not be executed.

        Returns
        -------
        type
            Name of the port when successful, ``False`` when failed.

        References
        ----------

        >>> oEditor.CreateEdgePort
        """
        if len(primivitivenames) == 2 and len(edgenumbers) == 2:
            listp = self.port_list
            self.modeler.oeditor.CreateEdgePort(
                [
                    "NAME:Contents",
                    "edge:=",
                    ["et:=", "pe", "prim:=", primivitivenames[0], "edge:=", edgenumbers[0]],
                    "edge:=",
                    ["et:=", "pe", "prim:=", primivitivenames[1], "edge:=", edgenumbers[1]],
                    "external:=",
                    True,
                    "btype:=",
                    0,
                ]
            )
            listnew = self.port_list
            a = [i for i in listnew if i not in listp]
            if len(a) > 0:
                return a[0]
            else:
                return False
        else:
            return False

    @aedt_exception_handler
    def create_coax_port(self, vianame, layer, xstart, xend, ystart, yend, archeight=0, arcrad=0, isexternal=True):
        """Create a new coax port.

        Parameters
        ----------
        vianame : str
            Name of the via to create the port on.
        layer : str
            Name of the layer.
        xstart :
            Starting position of the pin on the X axis.
        xend :
            Ending position of the pin on the X axis.
        ystart :
            Starting position of the pin on the Y axis.
        yend :
            Ending postiion of the pin on the Y axis.
        archeight : float, optional
            Arc height. The default is ``0``.
        arcrad : float, optional
            Rotation of the pin in radians. The default is ``0``.
        isexternal : bool, optional
            Whether the pin is external. The default is ``True``.

        Returns
        -------
        str
            Name of the port when successful, ``False`` when failed.

        References
        ----------

        >>> oEditor.CreateEdgePort
        """
        listp = self.port_list
        if isinstance(layer, str):
            layerid = self.modeler.layers.layer_id(layer)
        else:
            layerid = layer
        self.modeler.oeditor.CreateEdgePort(
            [
                "NAME:Contents",
                "edge:=",
                [
                    "et:=",
                    "pse",
                    "sel:=",
                    vianame,
                    "layer:=",
                    layerid,
                    "sx:=",
                    xstart,
                    "sy:=",
                    ystart,
                    "ex:=",
                    xend,
                    "ey:=",
                    yend,
                    "h:=",
                    archeight,
                    "rad:=",
                    arcrad,
                ],
                "external:=",
                isexternal,
            ]
        )
        listnew = self.port_list
        a = [i for i in listnew if i not in listp]
        if len(a) > 0:
            return a[0]
        else:
            return False

    @aedt_exception_handler
    def create_pin_port(self, name, xpos=0, ypos=0, rotation=0, top_layer=None, bot_layer=None):
        """Create a pin port.

        Parameters
        ----------
        name : str
            Name of the pin port.
        xpos : float, optional
            X-axis position of the pin. The default is ``0``.
        ypos : float, optional
            Y-axis position of the pin. The default is ``0``.
        rotation : float, optional
            Rotation of the pin in degrees. The default is ``0``.
        top_layer : str, optional
            Top layer of the pin. The default is ``None``, in which case the top
            layer is assigned automatically.
        bot_layer : str
            Bottom layer of the pin. The default is ``None``, in which case the
            bottom layer is assigned automatically.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.

        References
        ----------

        >>> oEditor.CreatePin
        """
        self.modeler.layers.refresh_all_layers()
        layers = self.modeler.layers.all_signal_layers
        if not top_layer:
            top_layer = layers[0]
        if not bot_layer:
            bot_layer = layers[len(layers) - 1]
        self.modeler.oeditor.CreatePin(
            [
                "NAME:Contents",
                ["NAME:Port", "Name:=", name],
                "ReferencedPadstack:=",
                "Padstacks:NoPad SMT East",
                "vposition:=",
                ["x:=", str(xpos) + self.modeler.model_units, "y:=", str(ypos) + self.modeler.model_units],
                "vrotation:=",
                [str(rotation) + "deg"],
                "overrides hole:=",
                False,
                "hole diameter:=",
                ["0mm"],
                "Pin:=",
                True,
                "highest_layer:=",
                top_layer,
                "lowest_layer:=",
                bot_layer,
            ]
        )
        return True

    @aedt_exception_handler
    def delete_port(self, portname):
        """Delete a port.

        Parameters
        ----------
        portname : str
            Name of the port.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.

        References
        ----------

        >>> oModule.Delete
        """
        self.oexcitation.Delete(portname)
        return True

    @aedt_exception_handler
    def import_edb(self, edb_full_path):
        """Import EDB.

        Parameters
        ----------
        edb_full_path : str
            Full path to EDB.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.

        References
        ----------

        >>> oModule.ImportEDB
        """
        self.oimport_export.ImportEDB(edb_full_path)
        self.oproject = self.odesktop.GetActiveProject().GetName()
        self.odesign = self.odesktop.GetActiveProject().GetActiveDesign().GetName().split(";")[1]
        return True

    @aedt_exception_handler
    def validate_full_design(self, name=None, outputdir=None, ports=None):
        """Validate the design based on the expected value and save the information in the log file.

        Parameters
        ----------
        name : str, optional
            Name of the design to validate. The default is ``None``.
        outputdir : str, optional
            Output directory to save the log file to. The default is ``None``.
        ports : str, optional
            Number of excitations that are expected. The default is ``None``.

        Returns
        -------
        list of str
            List of validation messages.

        References
        ----------

        >>> oDesign.ValidateDesign
        """
        if name is None:
            name = self.design_name
        if outputdir is None:
            outputdir = self.project_path

        self.logger.info("#### Design Validation Checks###")
        #
        # Routine outputs to the validation info to a log file in the project directory and also
        # returns the validation info to be used to update properties.xml file

        validation_ok = True

        #
        # Write an overall validation log file with all output from all checks
        # The design validation inside HFSS outputs to a separate log file which we merge into this overall file
        #
        val_list = []
        all_validate = outputdir + "\\all_validation.log"
        with open(all_validate, "w") as validation:

            # Desktop Messages
            msg = "Desktop Messages:"
            validation.writelines(msg + "\n")
            val_list.append(msg)
            msgs = self._desktop.GetMessages(self.project_name, name, 0)
            # need to check if design name is always this default name HFSSDesign1
            for msg in msgs:
                self.logger.info(msg)
                # msg = msg.replace('"','')
                msg = msg.rstrip("\r\n")
                val_list.append(msg)
                validation.writelines(msg + "\n")

            # Run Design Validation and write out the lines to the logger

            ret = self._odesign.ValidateCircuit()
            msg = "Design Validation Messages:"
            validation.writelines(msg + "\n")
            val_list.append(msg)
            if ret == 0:
                msg = "**** ERRORS Present - please check and confirm"
                self.logger.error(msg)
            else:
                msg = "**** Validation Completed Correctly"
                self.logger.info(msg)

            # Find the Excitations and check or list them out
            msg = "Excitation Messages:"
            validation.writelines(msg + "\n")
            val_list.append(msg)
            numportsdefined = int(len(self.get_excitations_name))
            if ports is not None and ports != numportsdefined:
                msg = "**** Port Number Error! - Please check model"
                self.logger.error(msg)
                validation.writelines(msg + "\n")
                val_list.append(msg)
                validation_ok = False
                # need to stop the simulation athis point
            else:
                msg1 = "Ports Requested: " + str(ports)
                msg2 = "Ports Defined: " + str(numportsdefined)
                self.logger.info(msg1)
                validation.writelines(msg1 + "\n")
                val_list.append(msg1)
                self.logger.info(msg2)
                validation.writelines(msg2 + "\n")
                val_list.append(msg2)

            excitation_names = self.get_excitations_name
            for excitation in excitation_names:
                msg = "Excitation name: " + str(excitation)
                self.logger.info(msg)
                validation.writelines(msg + "\n")
                val_list.append(msg)
        validation.close()
        return val_list, validation_ok  # return all the info in a list for use later

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
        port_names : str or list, optional
             One or more port names. The default is ``None``.
        port_excited : optional
             The default is ``None``.
        variations : optional
             The default is ``None``.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.

        References
        ----------

        >>> oModule.CreateReport
        """
        Families = ["Freq:=", ["All"]]
        if variations:
            Families += variations
        else:
            Families += self.get_nominal_variation()
        if not sweep_name:
            sweep_name = self.existing_analysis_sweeps[1]
        if not port_names:
            port_names = self.get_excitations_name
        if not port_excited:
            port_excited = port_names
        Trace = [
            "X Component:=",
            "Freq",
            "Y Component:=",
            ["dB(S(" + p + "," + q + "))" for p, q in zip(list(port_names), list(port_excited))],
        ]
        solution_data = ""
        if self.solution_type == "DrivenModal":
            solution_data = "Modal Solution Data"
        elif self.solution_type == "DrivenTerminal":
            solution_data = "Terminal Solution Data"
        elif self.solution_type == "HFSS3DLayout":
            solution_data = "Standard"
        if solution_data != "":
            # run CreateReport function
            self.post.oreportsetup.CreateReport(
                plot_name, solution_data, "Rectangular Plot", sweep_name, ["Domain:=", "Sweep"], Families, Trace, []
            )
            return True
        else:
            return False

    @aedt_exception_handler
    def export_touchstone(self, solutionname, sweepname, filename, variation, variations_value):
        """Export a Touchstone file.

        Parameters
        ----------
        solutionname : str
            Name of the solution that has been solved.
        sweepname : str
            Name of the sweep that has been solved.
        filename : str
            Full path for the Touchstone file.
        variation : list
            List of all parameter variations, such  as ``["$AmbientTemp", "$PowerIn"]``.
        variations_value : list
            List of all parameter variation values, such as ``["22cel", "100"]``.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.

        References
        ----------

        >>> oDesign.ExportNetworkData
        """
        # normalize the save path
        if not filename:
            appendix = ""
            for v, vv in zip(variation, variations_value):
                appendix += "_" + v + vv.replace("'", "")
            ext = ".S" + str(len(self.port_list)) + "p"
            filename = os.path.join(self.project_path, solutionname + "_" + sweepname + appendix + ext)
        else:
            filename = filename.replace("//", "/").replace("\\", "/")
        print("Exporting Touchstone " + filename)
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
        variation_str = ""
        for v, vv in zip(variation, variations_value):
            variation_str += v + "=" + vv + " "

        self.odesign.ExportNetworkData(
            variation_str,
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
            IncludeGammaImpedance,
            IncludeGammaImpedance,
            NonStandardExtensions,
        )
        return True

    @aedt_exception_handler
    def set_export_touchstone(self, activate, export_dir=""):
        """Export the Touchstone file automatically if the simulation is successful.

        Parameters
        ----------
        activate : bool
            Whether to export after the simulation.
        eport_dir str, optional
            Path to export the file to. The defaultis ``""``.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.

        References
        ----------

        >>> oDesign.DesignOptions
        """
        settings = []
        if activate:
            settings.append("NAME:options")
            settings.append("ExportAfterSolve:=")
            settings.append(True)
            settings.append("ExportDir:=")
            settings.append(export_dir)
        elif not activate:
            settings.append("NAME:options")
            settings.append("ExportAfterSolve:=")
            settings.append(False)
        self.odesign.DesignOptions(settings, 0)
        return True

    @aedt_exception_handler
    def create_frequency_sweep(
        self,
        setupname,
        unit,
        freqstart,
        freqstop,
        num_of_freq_points,
        sweepname=None,
        sweeptype="interpolating",
        interpolation_tol_percent=0.5,
        interpolation_max_solutions=250,
        save_fields=True,
        save_rad_fields_only=False,
        use_q3d_for_dc=False,
    ):
        """Create a frequency sweep.

        .. deprecated:: 0.4.0
           Use :func:`Hfss3dLayout.create_linear_count_sweep` instead.

        """

        warnings.warn(
            "`create_frequency_sweep` is deprecated. Use `create_linear_count_sweep` instead.",
            DeprecationWarning,
        )
        if sweeptype == "interpolating":
            sweeptype = "Interpolating"
        elif sweeptype == "discrete":
            sweeptype = "Discrete"
        elif sweeptype == "fast":
            sweeptype = "Fast"

        return self.create_linear_count_sweep(
            setupname=setupname,
            unit=unit,
            freqstart=freqstart,
            freqstop=freqstop,
            num_of_freq_points=num_of_freq_points,
            sweepname=sweepname,
            save_fields=save_fields,
            save_rad_fields_only=save_rad_fields_only,
            sweep_type=sweeptype,
            interpolation_tol_percent=interpolation_tol_percent,
            interpolation_max_solutions=interpolation_max_solutions,
            use_q3d_for_dc=use_q3d_for_dc,
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
        save_rad_fields_only=False,
        sweep_type="Interpolating",
        interpolation_tol_percent=0.5,
        interpolation_max_solutions=250,
        use_q3d_for_dc=False,
    ):
        """Create a sweep with the specified number of points.

        Parameters
        ----------
        setupname : str
            Name of the setup to attach to the sweep.
        unit : str
            Unit of the frequency, such as ``"MHz"`` or ``"GHz"``.
        freqstart : float
            Starting frequency of the sweep.
        freqstop : float
            Stopping frequency of the sweep.
        num_of_freq_points : int
            Number of frequency points in the range.
        sweepname : str, optional
            Name of the sweep. The default is ``None``.
        save_fields : bool, optional
            Whether to save the fields for a discrete sweep only. The
            default is ``True``.
        save_rad_fields_only : bool, optional
            Whether to save only the radiated fields if
            ``save_fields=True``. The default is ``False``.
        sweep_type : str, optional
            Type of the sweep. Options are ``"Fast"``,
            ``"Interpolating"``, and ``"Discrete"``.  The default is
            ``"Interpolating"``.
        interpolation_tol_percent : float, optional
            Error tolerance threshold for the interpolation
            process. The default is ``0.5``.
        interpolation_max_solutions : int, optional
            Maximum number of solutions evaluated for the
            interpolation process. The default is ``250``.
        use_q3d_for_dc : bool, optional
            Whether to use Q3D to solve the DC point. The default is ``False``.

        Returns
        -------
        :class:`pyaedt.modules.SetupTemplates.SweepHFSS3DLayout` or bool
            Sweep object if successful, ``False`` otherwise.

        References
        ----------

        >>> oModule.AddSweep
        """
        if sweep_type not in ["Discrete", "Interpolating", "Fast"]:
            raise AttributeError("Invalid in `sweep_type`. It has to be either 'Discrete', 'Interpolating', or 'Fast'")
        if sweepname is None:
            sweepname = generate_unique_name("Sweep")

        interpolation = False
        if sweep_type == "Interpolating":
            interpolation = True
            save_fields = False

        if not save_fields:
            save_rad_fields_only = False

        interpolation_tol = interpolation_tol_percent / 100.0

        for s in self.setups:
            if s.name == setupname:
                setupdata = s
                if sweepname in [sweep.name for sweep in setupdata.sweeps]:
                    oldname = sweepname
                    sweepname = generate_unique_name(oldname)
                    self.logger.warning(
                        "Sweep %s is already present. Sweep has been renamed in %s.", oldname, sweepname
                    )
                sweep = setupdata.add_sweep(sweepname=sweepname)
                if not sweep:
                    return False
                sweep.change_range("LinearCount", freqstart, freqstop, num_of_freq_points, unit)
                sweep.props["GenerateSurfaceCurrent"] = save_fields
                sweep.props["SaveRadFieldsOnly"] = save_rad_fields_only
                sweep.props["FastSweep"] = interpolation
                sweep.props["SAbsError"] = interpolation_tol
                sweep.props["EnforcePassivity"] = interpolation
                sweep.props["UseQ3DForDC"] = use_q3d_for_dc
                sweep.props["MaxSolutions"] = interpolation_max_solutions
                sweep.update()
                self.logger.info("Linear count sweep %s has been correctly created", sweepname)
                return sweep
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
        save_rad_fields_only=False,
        sweep_type="Interpolating",
        interpolation_tol_percent=0.5,
        interpolation_max_solutions=250,
        use_q3d_for_dc=False,
    ):
        """Create a sweep with the specified frequency step.

        Parameters
        ----------
        setupname : str
            Name of the setup to attach to the sweep.
        unit : str
            Unit of the frequency, such as ``"MHz"`` or ``"GHz"``.
        freqstart : float
            Starting frequency of the sweep.
        freqstop : float
            Stopping frequency of the sweep.
        step_size : float
            Frequency size of the step.
        sweepname : str, optional
            Name of the sweep. The default is ``None``.
        save_fields : bool, optional
            Whether to save the fields for a discrete sweep only. The
            default is ``True``.
        save_rad_fields_only : bool, optional
            Whether to save only the radiated fields if
            ``save_fields=True``. The default is ``False``.
        sweep_type : str, optional
            Type of the sweep. Options are ``"Fast"``,
            ``"Interpolating"``, and ``"Discrete"``.  The default is
            ``"Interpolating"``.
        interpolation_tol_percent : float, optional
            Error tolerance threshold for the interpolation
            process. The default is ``0.5``.
        interpolation_max_solutions : int, optional
            Maximum number of solutions evaluated for the
            interpolation process. The default is ``250``.
        use_q3d_for_dc : bool, optional
            Whether to use Q3D to solve the DC point. The default is ``False``.

        Returns
        -------
        :class:`pyaedt.modules.SetupTemplates.SweepHFSS3DLayout` or bool
            Sweep object if successful, ``False`` otherwise.

        References
        ----------

        >>> oModule.AddSweep
        """
        if sweep_type not in ["Discrete", "Interpolating", "Fast"]:
            raise AttributeError("Invalid in `sweep_type`. It has to be either 'Discrete', 'Interpolating', or 'Fast'")
        if sweepname is None:
            sweepname = generate_unique_name("Sweep")

        interpolation = False
        if sweep_type == "Interpolating":
            interpolation = True
            save_fields = False

        if not save_fields:
            save_rad_fields_only = False

        interpolation_tol = interpolation_tol_percent / 100.0

        for s in self.setups:
            if s.name == setupname:
                setupdata = s
                if sweepname in [sweep.name for sweep in setupdata.sweeps]:
                    oldname = sweepname
                    sweepname = generate_unique_name(oldname)
                    self.logger.warning(
                        "Sweep %s is already present. Sweep has been renamed in %s.", oldname, sweepname
                    )
                sweep = setupdata.add_sweep(sweepname=sweepname)
                if not sweep:
                    return False
                sweep.change_range("LinearStep", freqstart, freqstop, step_size, unit)
                sweep.props["GenerateSurfaceCurrent"] = save_fields
                sweep.props["SaveRadFieldsOnly"] = save_rad_fields_only
                sweep.props["FastSweep"] = interpolation
                sweep.props["SAbsError"] = interpolation_tol
                sweep.props["EnforcePassivity"] = interpolation
                sweep.props["UseQ3DForDC"] = use_q3d_for_dc
                sweep.props["MaxSolutions"] = interpolation_max_solutions
                sweep.update()
                self.logger.info("Linear step sweep %s has been correctly created", sweepname)
                return sweep
        return False

    @aedt_exception_handler
    def create_single_point_sweep(
        self,
        setupname,
        unit,
        freq,
        sweepname=None,
        save_fields=False,
        save_rad_fields_only=False,
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
        save_fields : bool, optional
            Whether to save the fields for all points and subranges defined in the sweep. The default is ``False``.
        save_rad_fields_only : bool, optional
            Whether to save only the radiating fields. The default is ``False``.

        Returns
        -------
        :class:`pyaedt.modules.SetupTemplates.SweepHFSS` or bool
            Sweep object if successful, ``False`` otherwise.

        References
        ----------

        >>> oModule.AddSweep
        """
        if sweepname is None:
            sweepname = generate_unique_name("SinglePoint")

        add_subranges = False
        if isinstance(freq, list):
            if not freq:
                raise AttributeError("Frequency list is empty! Specify at least one frequency point.")
            freq0 = freq.pop(0)
            if freq:
                add_subranges = True
        else:
            freq0 = freq

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
                sweepdata.change_range("SinglePoint", freq0, unit=unit)
                sweepdata.props["GenerateSurfaceCurrent"] = save_fields
                sweepdata.props["SaveRadFieldsOnly"] = save_rad_fields_only
                sweepdata.update()
                if add_subranges:
                    for f in freq:
                        sweepdata.add_subrange(rangetype="SinglePoint", start=f, unit=unit)
                self.logger.info("Single point sweep %s has been correctly created", sweepname)
                return sweepdata
        return False

    @aedt_exception_handler
    def import_gds(self, gds_path, aedb_path=None, xml_path=None, set_as_active=True, close_active_project=False):
        """Import grounds into the HFSS 3D Layout and assign the stackup from an XML file if present.

        Parameters
        ----------
        gds_path : str
            Full path to the GDS file.
        aedb_path : str, optional
            Full path to the AEDB file.
        xml_path : str, optional
            Path to the XML file with the stackup information. The default is ``None``, in
            which case the stackup is not edited.
        set_as_active : bool, optional
            Whether to set the GDS file as active. The default is ``True``.
        close_active_project : bool, optional
            Whether to close the active project after loading the GDS file.
            The default is ''False``.
        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.

        References
        ----------

        >>> oModule.ImportGDSII
        >>> oEditor.ImportStackupXML
        """
        active_project = self.project_name
        project_name = os.path.basename(gds_path)[:-4]
        if not aedb_path:
            aedb_path = gds_path.replace(".gds", ".aedb")
        if os.path.exists(aedb_path):
            old_name = project_name
            project_name = generate_unique_name(project_name)
            aedb_path = gds_path.replace(old_name + ".gds", project_name + ".aedb")
            self.logger.warning("aedb_exists. Renaming it to %s", project_name)

        self.oimport_export.ImportGDSII(gds_path, aedb_path, "", "")
        project = self.odesktop.SetActiveProject(project_name)
        oeditor = project.GetActiveDesign().SetActiveEditor("Layout")
        if xml_path:
            oeditor.ImportStackupXML(xml_path)
        if set_as_active:
            self._close_edb()
            self.__init__(project_name)
        if close_active_project:
            self.odesktop.CloseProject(active_project)
        return True

    @aedt_exception_handler
    def edit_cosim_options(
        self,
        simulate_missing_solution=True,
        align_ports=True,
        renormalize_ports=True,
        renorm_impedance=50,
        setup_override_name=None,
        sweep_override_name=None,
        use_interpolating_sweep=False,
        use_y_matrix=True,
        interpolation_algorithm="auto",
    ):
        """Edit Cosimulation Options.

        Parameters
        ----------
        simulate_missing_solution : bool, optional
            Set this to ``True`` if the the solver has to simulate missing solution or
            ``False`` to interpolate the missing solution.
        align_ports : bool, optional
            Set this to ``True`` if the the solver has to align microwave ports.
        renormalize_ports : bool, optional
            Set this to ``True`` if the the port impedance has to be renormalized.
        renorm_impedance : float, optional
            Renormalization impedance in Ohm.
        setup_override_name : str, optional
            The setup name if there is a setup override.
        sweep_override_name : str, optional
            The sweep name if there is a sweep override.
        use_interpolating_sweep : bool, optional
            Set to ``True`` if the the solver has to use an interpolating sweep.
            Set to ``False`` to use a discrete sweep.
        use_y_matrix : bool, optional
            Set to ``True`` if the interpolation algorithm has to use YMatrix.
        interpolation_algorithm : str, optional
                Defines which interpolation algorithm to use. Default is ``"auto"``.
                Options are ``"auto"``, ``"lin"``, ``"shadH"``, ``"shadNH"``

        Returns
        -------
        bool
            ``True`` if successful and ``False`` if failed.

        References
        ----------

        >>> oDesign.EditCoSimulationOptions

        Examples
        --------
        >>> from pyaedt import Hfss3dLayout
        >>> h3d = Hfss3dLayout()
        >>> h3d.edit_cosim_options(
        ...     simulate_missing_solution=True,
        ...     align_ports=True,
        ...     renormalize_ports=True,
        ...     renorm_impedance=50,
        ...     setup_override_name=None,
        ...     sweep_override_name=None,
        ...     use_interpolating_sweep=False,
        ...     use_y_matrix=True,
        ...     interpolation_algorithm="auto"
        ... )

        """
        if interpolation_algorithm not in ["auto", "lin", "shadH", "shadNH"]:
            self.logger.error("Wrong Interpolation Algorithm")
            return False
        arg = ["NAME:CoSimOptions", "Override:="]

        if setup_override_name:
            arg.append(True)
            arg.append("Setup:=")
            arg.append(setup_override_name)
        else:
            arg.append(False)
            arg.append("Setup:=")
            arg.append("")
        arg.append("OverrideSweep:=")

        if sweep_override_name:
            arg.append(True)
            arg.append("Sweep:=")
            arg.append(sweep_override_name)
        else:
            arg.append(False)
            arg.append("Sweep:=")
            arg.append("")
        arg.append("SweepType:=")
        if use_interpolating_sweep:
            arg.append(6)
        else:
            arg.append(4)
        arg.append("Interpolate:=")
        arg.append(not simulate_missing_solution)
        arg.append("YMatrix:=")
        arg.append(use_y_matrix)
        arg.append("AutoAlignPorts:=")
        arg.append(align_ports)
        arg.append("InterpAlg:=")
        arg.append(interpolation_algorithm)
        arg.append("Renormalize:=")
        arg.append(renormalize_ports)
        arg.append("RenormImpedance:=")
        arg.append(renorm_impedance)
        self.odesign.EditCoSimulationOptions(arg)
        return True
