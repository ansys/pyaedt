"""This module contains the ``Hfss3dLayout`` class."""

from __future__ import absolute_import  # noreorder

import io
import os
import warnings

from pyaedt import settings
from pyaedt.application.Analysis3DLayout import FieldAnalysis3DLayout
from pyaedt.generic.general_methods import generate_unique_name
from pyaedt.generic.general_methods import open_file
from pyaedt.generic.general_methods import pyaedt_function_handler


class Hfss3dLayout(FieldAnalysis3DLayout):
    """Provides the HFSS 3D Layout application interface.

    This class inherits all objects that belong to HFSS 3D Layout, including EDB
    API queries.

    Parameters
    ----------
    projectname : str, optional
        Name of the project to select or the full path to the project
        or AEDTZ archive to open or the path to the ``aedb`` folder or
        ``edb.def`` file. The default is ``None``, in which case an
        attempt is made to get an active project. If no projects are present,
        an empty project is created.
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
        Whether to launch AEDT in non-graphical mode. The default
        is ``False```, in which case AEDT is launched in graphical mode.
        This parameter is ignored when a script is launched within AEDT.
    new_desktop_session : bool, optional
        Whether to launch an instance of AEDT in a new thread, even if
        another instance of the ``specified_version`` is active on the
        machine. The default is ``True``.
    close_on_exit : bool, optional
        Whether to release AEDT on exit. The default is ``False``.
    student_version : bool, optional
        Whether to open the AEDT student version. The default is ``False``.
    machine : str, optional
        Machine name to connect the oDesktop session to. This works only in 2022 R2 or later.
        The remote server must be up and running with the command `"ansysedt.exe -grpcsrv portnum"`.
        If the machine is `"localhost"`. the server also starts if not present.
    port : int, optional
        Port number on which to start the oDesktop communication on an already existing server.
        This parameter is ignored when creating a new server. It works only in 2022 R2 or later.
        The remote server must be up and running with the command `"ansysedt.exe -grpcsrv portnum"`.
    aedt_process_id : int, optional
        Process ID for the instance of AEDT to point PyAEDT at. The default is
        ``None``. This parameter is only used when ``new_desktop_session = False``.

    Examples
    --------
    Create an ``Hfss3dLayout`` object and connect to an existing HFSS
    design or create a new HFSS design if one does not exist.

    >>> from pyaedt import Hfss3dLayout
    >>> aedtapp = Hfss3dLayout()

    Create an ``Hfss3dLayout`` object and link to a project named
    ``projectname``. If this project does not exist, create one with
    this name.

    >>> aedtapp = Hfss3dLayout(projectname)

    Create an ``Hfss3dLayout`` object and link to a design named
    ``designname`` in a project named ``projectname``.

    >>> aedtapp = Hfss3dLayout(projectname,designame)

    Create an ``Hfss3dLayout`` object and open the specified project.

    >>> aedtapp = Hfss3dLayout("myfile.aedt")

    Create an AEDT 2021 R1 object and then create a
    ``Hfss3dLayout`` object and open the specified project.

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
        machine="",
        port=0,
        aedt_process_id=None,
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
            machine,
            port,
            aedt_process_id,
        )

    def __enter__(self):
        return self

    @pyaedt_function_handler()
    def create_edge_port(
        self,
        primivitivename,
        edgenumber,
        iscircuit=False,
        iswave=False,
        wave_horizontal_extension=5,
        wave_vertical_extension=3,
        wave_launcher="1mm",
    ):
        """Create an edge port.

        Parameters
        ----------
        primivitivename : str
            Name of the primitive to create the edge port on.
        edgenumber :
            Edge number to create the edge port on.
        iscircuit : bool, optional
            Whether the edge port is a circuit port. The default is ``False``.
        iswave : bool, optional
            Whether the edge port is a wave port. The default is ``False``.
        wave_horizontal_extension : float, optional
            Horizontal port extension factor. The default is `5`.
        wave_vertical_extension : float, optional
            Vertical port extension factor. The default is `5`.
        wave_launcher : str, optional
            PEC (perfect electrical conductor) launcher size with units. The
            default is `"1mm"`.

        Returns
        -------
        str
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
            if iswave:
                self.modeler.change_property(
                    property_object="Excitations:{}".format(a[0]),
                    property_name="HFSS Type",
                    property_value="Wave",
                    property_tab="EM Design",
                )
                self.modeler.change_property(
                    property_object="Excitations:{}".format(a[0]),
                    property_name="Horizontal Extent Factor",
                    property_value=str(wave_horizontal_extension),
                    property_tab="EM Design",
                )
                if "Vertical Extent Factor" in list(
                    self.modeler.oeditor.GetProperties("EM Design", "Excitations:{}".format(a[0]))
                ):
                    self.modeler.change_property(
                        property_object="Excitations:{}".format(a[0]),
                        property_name="Vertical Extent Factor",
                        property_value=str(wave_vertical_extension),
                        property_tab="EM Design",
                    )
                self.modeler.change_property(
                    property_object="Excitations:{}".format(a[0]),
                    property_name="PEC Launch Width",
                    property_value=str(wave_launcher),
                    property_tab="EM Design",
                )
            return a[0]
        else:
            return False

    @pyaedt_function_handler()
    def create_wave_port_from_two_conductors(self, primivitivenames=[""], edgenumbers=[""]):
        """Create a wave port.

        Parameters
        ----------
        primivitivenames : list(str)
            List of the primitive names to create the wave port on.
            The list must have two entries, one entry for each of the two conductors,
            or the method is not executed.

        edgenumbers :
            List of the edge number to create the wave port on.
            The list must have two entries, one entry for each of the two edges,
            or the method is not executed.

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

    @pyaedt_function_handler()
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
            Ending position of the pin on the Y axis.
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

    @pyaedt_function_handler()
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

    @pyaedt_function_handler()
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

    @pyaedt_function_handler()
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
        if "edb.def" not in edb_full_path:
            edb_full_path = os.path.join(edb_full_path, "edb.def")
        self.oimport_export.ImportEDB(edb_full_path)
        self._close_edb()
        project_name = self.odesktop.GetActiveProject().GetName()
        design_name = self.odesktop.GetActiveProject().GetActiveDesign().GetName().split(";")[-1]
        self.__init__(projectname=project_name, designname=design_name)
        return True

    @pyaedt_function_handler()
    def validate_full_design(self, name=None, outputdir=None, ports=None):
        """Validate the design based on the expected value and save the information in the log file.

        Parameters
        ----------
        name : str, optional
            Name of the design to validate. The default is ``None``.
        outputdir : str, optional
            Output directory to save the log file to. The default is ``None``,
            in which case the file is exported to the working directory.

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
            outputdir = self.working_directory

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
        with open_file(all_validate, "w") as validation:

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
            numportsdefined = int(len(self.excitations))
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

            excitation_names = self.excitations
            for excitation in excitation_names:
                msg = "Excitation name: " + str(excitation)
                self.logger.info(msg)
                validation.writelines(msg + "\n")
                val_list.append(msg)
        validation.close()
        return val_list, validation_ok  # return all the info in a list for use later

    @pyaedt_function_handler()
    def create_scattering(
        self, plot_name="S Parameter Plot Nominal", sweep_name=None, port_names=None, port_excited=None, variations=None
    ):
        """Create a scattering report.

        Parameters
        ----------
        plot_name : str, optional
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
        solution_data = "Standard"
        if "Modal" in self.solution_type:
            solution_data = "Modal Solution Data"
        elif "Terminal" in self.solution_type:
            solution_data = "Terminal Solution Data"
        if not port_names:
            port_names = self.excitations
        if not port_excited:
            port_excited = port_names
        traces = ["dB(S(" + p + "," + q + "))" for p, q in zip(list(port_names), list(port_excited))]
        return self.post.create_report(
            traces, sweep_name, variations=variations, report_category=solution_data, plotname=plot_name
        )

    @pyaedt_function_handler()
    def export_touchstone(
        self, solution_name=None, sweep_name=None, file_name=None, variations=None, variations_value=None
    ):
        """Export a Touchstone file.

        Parameters
        ----------
        solution_name : str, optional
            Name of the solution that has been solved.
        sweep_name : str, optional
            Name of the sweep that has been solved.
        file_name : str, optional
            Full path and name for the Touchstone file.
            The default is ``None``, in which case the Touchstone file is exported to
            the working directory.
        variations : list, optional
            List of all parameter variations. For example, ``["$AmbientTemp", "$PowerIn"]``.
            The default is ``None``.
        variations_value : list, optional
            List of all parameter variation values. For example, ``["22cel", "100"]``.
            The default is ``None``.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.

        References
        ----------

        >>> oDesign.ExportNetworkData
        """
        return self._export_touchstone(
            solution_name=solution_name,
            sweep_name=sweep_name,
            file_name=file_name,
            variations=variations,
            variations_value=variations_value,
        )

    @pyaedt_function_handler()
    def set_export_touchstone(self, activate, export_dir=""):
        """Export the Touchstone file automatically if the simulation is successful.

        Parameters
        ----------
        activate : bool
            Whether to export the Touchstone file after the simulation.
        export_dir str, optional
            Path to export the Touchstone file to. The default is ``""``.

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

    @pyaedt_function_handler()
    def create_frequency_sweep(
        self,
        setupname,
        unit,
        freqstart,
        freqstop,
        num_of_freq_points,
        sweepname=None,
        sweeptype="Interpolating",
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

    @pyaedt_function_handler()
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
            Unit of the frequency. For example, ``"MHz"`` or ``"GHz"``.
        freqstart : float
            Starting frequency of the sweep.
        freqstop : float
            Stopping frequency of the sweep.
        num_of_freq_points : int
            Number of frequency points in the range.
        sweepname : str, optional
            Name of the sweep. The default is ``None``.
        save_fields : bool, optional
            Whether to save fields for a discrete sweep only. The
            default is ``True``.
        save_rad_fields_only : bool, optional
            Whether to save only radiated fields if
            ``save_fields=True``. The default is ``False``.
        sweep_type : str, optional
            Type of the sweep. Options are ``"Fast"``,
            ``"Interpolating"``, and ``"Discrete"``.  The default is
            ``"Interpolating"``.
        interpolation_tol_percent : float, optional
            Error tolerance threshold for the interpolation process.
            The default is ``0.5``.
        interpolation_max_solutions : int, optional
            Maximum number of solutions to evaluate for the
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
            raise AttributeError(
                "Invalid value for `sweep_type`. The value must be 'Discrete', 'Interpolating', or 'Fast'."
            )
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
                self.logger.info("Linear count sweep %s has been correctly created.", sweepname)
                return sweep
        return False

    @pyaedt_function_handler()
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
            Unit of the frequency. For example, ``"MHz"`` or ``"GHz"``.
        freqstart : float
            Starting frequency of the sweep.
        freqstop : float
            Stopping frequency of the sweep.
        step_size : float
            Frequency size of the step.
        sweepname : str, optional
            Name of the sweep. The default is ``None``.
        save_fields : bool, optional
            Whether to save fields for a discrete sweep only. The
            default is ``True``.
        save_rad_fields_only : bool, optional
            Whether to save only radiated fields if
            ``save_fields=True``. The default is ``False``.
        sweep_type : str, optional
            Type of the sweep. Options are ``"Fast"``,
            ``"Interpolating"``, and ``"Discrete"``.  The default is
            ``"Interpolating"``.
        interpolation_tol_percent : float, optional
            Error tolerance threshold for the interpolation
            process. The default is ``0.5``.
        interpolation_max_solutions : int, optional
            Maximum number of solutions to evaluate for the
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
            raise AttributeError(
                "Invalid value for `sweep_type`. The value must be 'Discrete', 'Interpolating', or 'Fast'."
            )
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
                self.logger.info("Linear step sweep %s has been correctly created.", sweepname)
                return sweep
        return False

    @pyaedt_function_handler()
    def create_single_point_sweep(
        self,
        setupname,
        unit,
        freq,
        sweepname=None,
        save_fields=False,
        save_rad_fields_only=False,
    ):
        """Create a sweep with a single frequency point.

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
            Whether to save fields for all points and subranges defined in the sweep. The default is ``False``.
        save_rad_fields_only : bool, optional
            Whether to save only radiating fields. The default is ``False``.

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
                raise AttributeError("Frequency list is empty. Specify at least one frequency point.")
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
                self.logger.info("Single point sweep %s has been correctly created.", sweepname)
                return sweepdata
        return False

    @pyaedt_function_handler()
    def _import_cad(
        self, cad_path, cad_format="gds", aedb_path=None, xml_path=None, set_as_active=True, close_active_project=False
    ):
        method = None
        if cad_format == "gds":
            method = self.oimport_export.ImportGDSII
        elif cad_format == "dxf":
            method = self.oimport_export.ImportAutoCAD
        elif cad_format == "gerber":
            method = self.oimport_export.ImportGerber
        elif cad_format == "awr":
            method = self.oimport_export.ImportAWRMicrowaveOffice
        elif cad_format == "brd":
            method = self.oimport_export.ImportExtracta
        elif cad_format == "ipc2581":
            method = self.oimport_export.ImportIPC
        elif cad_format == "odb++":
            method = self.oimport_export.ImportODB
        if not method:
            return False
        active_project = self.project_name
        path_ext = os.path.splitext(cad_path)
        project_name = os.path.splitext(os.path.basename(cad_path))[0]
        if not aedb_path:
            aedb_path = path_ext[0] + ".aedb"
        if os.path.exists(aedb_path):
            old_name = project_name
            project_name = generate_unique_name(project_name)
            aedb_path = aedb_path.replace(old_name, project_name)
            self.logger.warning("aedb_exists. Renaming it to %s", project_name)
        if not xml_path:
            xml_path = ""
        if cad_format == "gds":
            method(cad_path, aedb_path, xml_path, "")
        else:
            method(cad_path, aedb_path, xml_path)

        if set_as_active:
            self._close_edb()
            self.__init__(project_name)
        if close_active_project:
            self.odesktop.CloseProject(active_project)
        return True

    @pyaedt_function_handler()
    def import_gds(self, gds_path, aedb_path=None, control_file=None, set_as_active=True, close_active_project=False):
        """Import a GDS file into HFSS 3D Layout and assign the stackup from an XML file if present.

        Parameters
        ----------
        gds_path : str
            Full path to the GDS file.
        aedb_path : str, optional
            Full path to the AEDB file.
        control_file : str, optional
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
        """
        return self._import_cad(gds_path, "gds", aedb_path, control_file, set_as_active, close_active_project)

    @pyaedt_function_handler()
    def import_dxf(self, dxf_path, aedb_path=None, control_file=None, set_as_active=True, close_active_project=False):
        """Import a DXF file into HFSS 3D Layout and assign the stackup from an XML file if present.

        Parameters
        ----------
        gds_path : str
            Full path to the DXF file.
        aedb_path : str, optional
            Full path to the AEDB file.
        control_file : str, optional
            Path to the XML file with the stackup information. The default is ``None``, in
            which case the stackup is not edited.
        set_as_active : bool, optional
            Whether to set the DXF file as active. The default is ``True``.
        close_active_project : bool, optional
            Whether to close the active project after loading the DXF file.
            The default is ''False``.
        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.

        References
        ----------

        >>> oModule.ImportDXF
        """
        return self._import_cad(dxf_path, "dxf", aedb_path, control_file, set_as_active, close_active_project)

    @pyaedt_function_handler()
    def import_gerber(
        self, gerber_path, aedb_path=None, control_file=None, set_as_active=True, close_active_project=False
    ):
        """Import a Gerber zip file into HFSS 3D Layout and assign the stackup from an XML file if present.

        Parameters
        ----------
        gerber_path : str
            Full path to the Gerber zip file.
        aedb_path : str, optional
            Full path to the AEDB file.
        control_file : str, optional
            Path to the XML file with the stackup information. The default is ``None``, in
            which case the stackup is not edited.
        set_as_active : bool, optional
            Whether to set the Gerber zip file file as active. The default is ``True``.
        close_active_project : bool, optional
            Whether to close the active project after loading the Gerber zip file file.
            The default is ''False``.
        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.

        References
        ----------

        >>> oModule.ImportGerber
        """
        return self._import_cad(gerber_path, "gerber", aedb_path, control_file, set_as_active, close_active_project)

    @pyaedt_function_handler()
    def import_brd(
        self, input_file, aedb_path=None, set_as_active=True, close_active_project=False
    ):  # pragma: no cover
        """Import a board file into HFSS 3D Layout and assign the stackup from an XML file if present.

        Parameters
        ----------
        input_file : str
            Full path to the board file.
        aedb_path : str, optional
            Full path to the AEDB file.
        set_as_active : bool, optional
            Whether to set the board file as active. The default is ``True``.
        close_active_project : bool, optional
            Whether to close the active project after loading the board file.
            The default is ''False``.
        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.

        References
        ----------

        >>> oModule.ImportExtracta
        """
        return self._import_cad(input_file, "brd", aedb_path, "", set_as_active, close_active_project)

    @pyaedt_function_handler()
    def import_awr(
        self, input_file, aedb_path=None, control_file=None, set_as_active=True, close_active_project=False
    ):  # pragma: no cover
        """Import an AWR Microwave Office file into HFSS 3D Layout and assign the stackup from an XML file if present.

        Parameters
        ----------
        input_file : str
            Full path to the AWR Microwave Office file.
        aedb_path : str, optional
            Full path to the AEDB file.
        control_file : str, optional
            Path to the XML file with the stackup information. The default is ``None``, in
            which case the stackup is not edited.
        set_as_active : bool, optional
            Whether to set the AWR Microwave Office file as active. The default is ``True``.
        close_active_project : bool, optional
            Whether to close the active project after loading the AWR Microwave Office file.
            The default is ''False``.
        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.

        References
        ----------

        >>> oModule.ImportAWRMicrowaveOffice
        """
        return self._import_cad(input_file, "awr", aedb_path, control_file, set_as_active, close_active_project)

    @pyaedt_function_handler()
    def import_ipc2581(
        self, input_file, aedb_path=None, control_file=None, set_as_active=True, close_active_project=False
    ):
        """Import an IPC2581 file into HFSS 3D Layout and assign the stackup from an XML file if present.

        Parameters
        ----------
        input_file : str
            Full path to the IPC2581 file.
        aedb_path : str, optional
            Full path to the AEDB file.
        control_file : str, optional
            Path to the XML file with the stackup information. The default is ``None``, in
            which case the stackup is not edited.
        set_as_active : bool, optional
            Whether to set the IPC2581 file as active. The default is ``True``.
        close_active_project : bool, optional
            Whether to close the active project after loading the IPC2581 file.
            The default is ''False``.
        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.

        References
        ----------

        >>> oModule.ImportAWRMicrowaveOffice
        """
        return self._import_cad(input_file, "ipc2581", aedb_path, control_file, set_as_active, close_active_project)

    @pyaedt_function_handler()
    def import_odb(self, input_file, aedb_path=None, control_file=None, set_as_active=True, close_active_project=False):
        """Import an ODB++ file into HFSS 3D Layout and assign the stackup from an XML file if present.

        Parameters
        ----------
        input_file : str
            Full path to the ODB++ file.
        aedb_path : str, optional
            Full path to the AEDB file.
        control_file : str, optional
            Path to the XML file with the stackup information. The default is ``None``, in
            which case the stackup is not edited.
        set_as_active : bool, optional
            Whether to set the ODB++ file as active. The default is ``True``.
        close_active_project : bool, optional
            Whether to close the active project after loading the ODB++ file.
            The default is ''False``.
        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.

        References
        ----------

        >>> oModule.ImportAWRMicrowaveOffice
        """
        return self._import_cad(input_file, "odb++", aedb_path, control_file, set_as_active, close_active_project)

    @pyaedt_function_handler()
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
        """Edit cosimulation options.

        Parameters
        ----------
        simulate_missing_solution : bool, optional
            Whether the solver is to simulate a missing solution. The default is ``True``. If
            ``False``, the solver interpolates a missing solution.
        align_ports : bool, optional
            Whether the solver is to align microwave parts. The default is ``True``.
        renormalize_ports : bool, optional
            Whether to renormalize port impendance. The default is ``True``.
        renorm_impedance : float, optional
            Renormalization impedance in ohms. The default is ``50``.
        setup_override_name : str, optional
            Setup name if there is a setup override. The default is ``None``.
        sweep_override_name : str, optional
            Sweep name if there is a sweep override. The default is ``None``.
        use_interpolating_sweep : bool, optional
            Whether the solver is to use an interpolating sweep. The default is ``True``.
            If ``False``, the solver is to use a discrete sweep.
        use_y_matrix : bool, optional
            Whether the interpolation algorithm is to use the Y matrix. The default is
            ``True``.
        interpolation_algorithm : str, optional
            Interpolation algorithm to use. Options are ``"auto"``, ``"lin"``, ``"shadH"``,
            and ``"shadNH"``. The default is ``"auto"``.

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

    @pyaedt_function_handler()
    def set_differential_pair(
        self,
        positive_terminal,
        negative_terminal,
        common_name=None,
        diff_name=None,
        common_ref_z=25,
        diff_ref_z=100,
        active=True,
        matched=False,
    ):
        """Add a differential pair definition.

        Parameters
        ----------
        positive_terminal : str
            Name of the terminal to use as the positive terminal.
        negative_terminal : str
            Name of the terminal to use as the negative terminal.
        common_name : str, optional
            Name for the common mode. The default is ``None``, in which case a unique name is assigned.
        diff_name : str, optional
            Name for the differential mode. The default is ``None``, in which case a unique name is assigned.
        common_ref_z : float, optional
            Reference impedance for the common mode in ohms. The default is ``25``.
        diff_ref_z : float, optional
            Reference impedance for the differential mode in ohms. The default is ``100``.
        active : bool, optional
            Whether to set the differential pair as active. The default is ``True``.
        matched : bool, optional
            Whether to set the differential pair as active. The default is ``False``.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.

        References
        ----------
        >>> oModule.SetDiffPairs
        """
        if not diff_name:
            diff_name = generate_unique_name("Diff")
        if not common_name:
            common_name = generate_unique_name("Comm")

        arg1 = [
            "Pos:=",
            positive_terminal,
            "Neg:=",
            negative_terminal,
            "On:=",
            active,
            "matched:=",
            matched,
            "Dif:=",
            diff_name,
            "DfZ:=",
            [float(diff_ref_z), 0],
            "Com:=",
            common_name,
            "CmZ:=",
            [float(common_ref_z), 0],
        ]

        arg = ["NAME:DiffPairs"]
        arg.append("Pair:=")
        arg.append(arg1)

        tmpfile1 = os.path.join(self.working_directory, generate_unique_name("tmp"))
        self.oexcitation.SaveDiffPairsToFile(tmpfile1)
        with open_file(tmpfile1, "r") as fh:
            lines = fh.read().splitlines()
        old_arg = []
        for line in lines:
            data = line.split(",")
            data_arg = [
                "Pos:=",
                data[0],
                "Neg:=",
                data[1],
                "On:=",
                data[2] == "1",
                "matched:=",
                data[3] == "1",
                "Dif:=",
                data[4],
                "DfZ:=",
                [float(data[5]), 0],
                "Com:=",
                data[6],
                "CmZ:=",
                [float(data[7]), 0],
            ]
            old_arg.append(data_arg)

        for arg2 in old_arg:
            arg.append("Pair:=")
            arg.append(arg2)

        try:
            os.remove(tmpfile1)
        except:  # pragma: no cover
            self.logger.warning("ERROR: Cannot remove temp files.")

        try:
            self.oexcitation.SetDiffPairs(arg)
        except:  # pragma: no cover
            return False
        return True

    @pyaedt_function_handler()
    def load_diff_pairs_from_file(self, filename):
        """Load differtential pairs definition from file.

        You can use the ``save_diff_pairs_to_file`` method to obtain the file format.
        The ``File End Of Line`` must be UNIX (LF).
        New definitions are added only if compatible with the existing definition already defined in the project.

        Parameters
        ----------
        filename : str
            Fully qualified name of the file containing the differential pairs definition.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.

        References
        ----------
        >>> oModule.LoadDiffPairsFromFile
        """
        if not os.path.isfile(filename):  # pragma: no cover
            raise ValueError("{}: unable to find the specified file.".format(filename))

        try:
            new_file = os.path.join(os.path.dirname(filename), generate_unique_name("temp") + ".txt")
            with open_file(filename, "r") as file:
                filedata = file.read().splitlines()
            with io.open(new_file, "w", newline="\n") as fh:
                for line in filedata:
                    fh.write(line + "\n")

            self.oexcitation.LoadDiffPairsFromFile(new_file)
            os.remove(new_file)
        except:  # pragma: no cover
            return False
        return True

    @pyaedt_function_handler()
    def save_diff_pairs_to_file(self, filename):
        """Save differtential pairs definition to a file.

        If a filee with the specified name already exists, it is overwritten.

        Parameters
        ----------
        filename : str
            Fully qualified name of the file containing the differential pairs definition.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.

        References
        ----------
        >>> oModule.SaveDiffPairsToFile
        """
        self.oexcitation.SaveDiffPairsToFile(filename)

        return os.path.isfile(filename)

    @pyaedt_function_handler()
    def export_3d_model(self, file_name=None):
        """Export the Ecad model to an ACIS 3D file.

        Parameters
        ----------
        file_name : str, optional
            Full name of the file to export. The default is None, in which case the file name is
            set to the design name and saved as a SAT file in the working directory.
            Extensions available are ``"sat"``, ``"sab"``, and ``"sm3"``.

        Returns
        -------
        str
            File name if successful.
        """
        if not file_name:
            file_name = os.path.join(self.working_directory, self.design_name + ".sat")

        self.modeler.oeditor.ExportAcis(["NAME:options", "FileName:=", file_name])
        return file_name

    @pyaedt_function_handler()
    def enable_rigid_flex(self):
        """Turn on or off the rigid flex of a board with bending if available.

        This function is the same for both turning on and off rigid flex.

        Returns
        -------
        bool
            ``True`` if rigid flex is turned off, ``False``` if rigid flex is turned off.
            In non-graphical, ``True`` is always returned due to a bug in the native API.
        """
        if settings.aedt_version >= "2022.2":
            self.modeler.oeditor.ProcessBentModelCmd()
        if settings.non_graphical:
            return True
        return True if self.variable_manager["BendModel"].expression == "1" else False

    @pyaedt_function_handler
    def edit_hfss_extents(
        self,
        diel_extent_type=None,
        diel_extent_horizontal_padding=None,
        diel_honor_primitives_on_diel_layers="keep",
        air_extent_type=None,
        air_truncate_model_at_ground_layer="keep",
        air_vertical_positive_padding=None,
        air_vertical_negative_padding=None,
    ):
        """Edit HFSS 3D Layout extents.

        Parameters
        ----------
        diel_extent_type : str, optional
            Dielectric extent type. The default is ``None``. Options are ``"BboxExtent"``,
            ``"ConformalExtent"``, and ``"ConvexHullExtent"``.
        diel_extent_horizontal_padding : str, optional
            Dielectric extent horizontal padding. The default is ``None``.
        diel_honor_primitives_on_diel_layers : str, optional
            Whether to set dielectric honor primitives on dielectric layers. The default is ``None``.
        air_extent_type : str, optional
            Airbox extent type. The default is ``None``. Options are ``"BboxExtent"``,
            ``"ConformalExtent"``, and ``"ConvexHullExtent"``.
        air_truncate_model_at_ground_layer : str, optional
            Whether to set airbox truncate model at ground layer. The default is ``None``.
        air_vertical_positive_padding : str, optional
            Airbox vertical positive padding. The default is ``None``.
        air_vertical_negative_padding : str, optional
            Airbox vertical negative padding. The default is ``None``.
        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.
        """
        arg = ["NAME:HfssExportInfo"]
        if diel_extent_type:
            arg.append("DielExtentType:=")
            arg.append(diel_extent_type)
        if diel_extent_horizontal_padding:
            arg.append("DielExt:=")
            arg.append(["Ext:=", diel_extent_horizontal_padding, "Dim:=", False])
        if not diel_honor_primitives_on_diel_layers == "keep":
            arg.append("HonorUserDiel:=")
            arg.append(diel_honor_primitives_on_diel_layers)
        if air_extent_type:
            arg.append("ExtentType:=")
            arg.append(air_extent_type)
        if not air_truncate_model_at_ground_layer == "keep":
            arg.append("TruncAtGnd:=")
            arg.append(air_truncate_model_at_ground_layer)
        if air_vertical_positive_padding:
            arg.append("AirPosZExt:=")
            arg.append(["Ext:=", air_vertical_positive_padding, "Dim:=", True])
        if air_vertical_negative_padding:
            arg.append("AirNegZExt:=")
            arg.append(["Ext:=", air_vertical_negative_padding, "Dim:=", True])

        self.odesign.EditHfssExtents(arg)
        return True
