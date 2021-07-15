"""This module contains these classes: `Hfss3dLayout` and `SweepString`."""

from __future__ import absolute_import
import os

from .application.Analysis3DLayout import FieldAnalysis3DLayout
from .desktop import exception_to_desktop
from .modules.SolveSetup import Setup3DLayout
from .generic.general_methods import generate_unique_name, aedt_exception_handler



class SweepString(object):
    """SweepString class.
    
    This class allows you to generate a sweep string like in this example: 
    ``"LIN 10GHz 20GHz 0.05GHz LINC 20GHz 30GHz 10 DEC 30GHz 40GHz 10 40GHz``
    
    Parameters
    ----------
    unit : str, optional
        Units for the sweep string. The default is ``"GHz"``.
     """
        
    def __init__(self, unit='GHz'):
    
        self.unit = unit
        self.sweep_string = ""

    @aedt_exception_handler
    def add_sweep(self, sweep, line_type, unit=None):
        """Add a line to the sweep string.

        Parameters
        ----------
        sweep : list
            List of frequencies,
            if linear_step [start, stop, step]
            if linear_count [start, stop, number of steps]
            if log_scale [start, stop, samples]
            if single [f1, f2,... fn]
        line_type :
            linear_step", "linear_count", "log_scale", "single"
        unit : str
            Units such as ``"MHz"`` or ``"GHz"``. The default is ``None``.

        Returns
        -------

        """
        if not unit:
            unit = self.unit
        if self.sweep_string != "":
            self.sweep_string += " "
        if line_type == "linear_step" and len(sweep) == 3:
            string = "LIN " + str(sweep[0]) + unit + " " + str(sweep[1]) + unit + " " + str(sweep[2]) + unit
        elif line_type == "linear_count" and len(sweep) == 3:
            string = "LINC " + str(sweep[0]) + unit + " " + str(sweep[1]) + unit + " " + str(sweep[2])
        elif line_type == "log_scale" and len(sweep) == 3:
            string = "DEC " + str(sweep[0]) + unit + " " + str(sweep[1]) + unit + " " + str(sweep[2])
        elif line_type == "single":
            string = ""
            for f in sweep:
                string += str(f) + unit + " "
            string = string[:-1]
        else:
            raise ValueError('Wrong format for sweep list!')
        self.sweep_string += string

    @aedt_exception_handler
    def get_string(self):
        """ """
        if self.sweep_string:
            return self.sweep_string
        else:
            return None


class Hfss3dLayout(FieldAnalysis3DLayout):
    """HFSS 3D Layout instance interface.

    This class contains all HFSS 3D Layout functionalities. It
    inherits all objects that belong to HFSS 3D Layout, including EDB
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
        ``None``, which applies the default type.
    setup_name : str, optional
        Name of the setup to use as the nominal. The default is
        ``None``, in which case the active setup is used or 
        nothing is used.
    specified_version: str, optional
        Version of AEDT  to use. The default is ``None``, in which case
        the active version or latest installed version is used.
    NG : bool, optional
        Whether to run AEDT in the non-graphical mode. The default 
        is``False``, which launches AEDT in the graphical mode.  
    AlwaysNew : bool, optional
        Whether to launch an instance of AEDT in a new thread, even if
        another instance of the ``specified_version`` is active on the
        machine.  The default is ``True``.
    release_on_exit : bool, optional
        Whether to release AEDT on exit. 
    student_version : bool, optional
        Whether open AEDT Student Version. The default is ``False``.

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

    Create a `Desktop on 2021R1` object and then create a
    `Hfss3dLayout` object and open the specified project.

    >>> aedtapp = Hfss3dLayout(specified_version="2021.1", projectname="myfile.aedt")
    """

    def __init__(self, projectname=None, designname=None, solution_type=None, setup_name=None,
                 specified_version=None, NG=False, AlwaysNew=False, release_on_exit=False, student_version=False):
        FieldAnalysis3DLayout.__init__(self, "HFSS 3D Layout Design", projectname, designname, solution_type,
                                       setup_name, specified_version, NG, AlwaysNew, release_on_exit, student_version)

    def __enter__(self):
        return self

    def __exit__(self, ex_type, ex_value, ex_traceback):
        ''' Push exit up to parent object Design '''
        if ex_type:
            exception_to_desktop(self, ex_value, ex_traceback)

    @aedt_exception_handler
    def create_edge_port(self, primivitivename, edgenumber, iscircuit=True):
        """Create a new edge port.

        Parameters
        ----------
        primivitivename : str
            Name of the primitive.
        edgenumber :
            Edge number to create the port on.
        iscircuit : bool, optional
            Whether the edge port is a circuit port. The default is ``False``.

        Returns
        -------
        type
            Port name

        """
        listp = self.port_list
        self.modeler.oeditor.CreateEdgePort(
            ["NAME:Contents", "edge:=", ["et:=", "pe", "prim:=", primivitivename, "edge:=", edgenumber], "circuit:=",
             iscircuit, "btype:=", 0])
        listnew = self.port_list
        a=[i for i in listnew if i not in listp]
        if len(a)>0:
            return a[0]
        else:
            return False

    @aedt_exception_handler
    def create_coax_port(self, vianame, layer, xstart, xend,ystart, yend, archeight=0, arcrad=0, isexternal=True):
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
        """
        listp = self.port_list
        if type(layer) is str:
            layerid = self.modeler.layers.layer_id(layer)
        else:
            layerid = layer
        self.modeler.oeditor.CreateEdgePort(["NAME:Contents", "edge:=",
                                             ["et:=", "pse", "sel:=", vianame, "layer:=", layerid, "sx:=", xstart, "sy:=",
                                              ystart, "ex:=", xend, "ey:=", yend, "h:=", archeight, "rad:=", arcrad],
                                             "external:=", isexternal])
        listnew = self.port_list
        a=[i for i in listnew if i not in listp]
        if len(a)>0:
            return a[0]
        else:
            return False

    @aedt_exception_handler
    def create_pin_port(self,name,xpos=0, ypos=0, rotation=0, top_layer=None, bot_layer=None):
        """Create a new pin port.

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
            bottom is assigned automatically.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.
        """
        self.modeler.layers.refresh_all_layers()
        layers = self.modeler.layers.all_signal_layers
        if not top_layer:
            top_layer = layers[0]
        if not bot_layer:
            bot_layer = layers[len(layers)-1]
        self.modeler.oeditor.CreatePin(
            [
                "NAME:Contents",
                [
                    "NAME:Port",
                    "Name:="	, name
                ],
                "ReferencedPadstack:="	, "Padstacks:NoPad SMT East",
                "vposition:=",
                ["x:=", str(xpos) + self.modeler.model_units, "y:=", str(ypos) + self.modeler.model_units],
                "vrotation:="		, [str(rotation) + "deg"],
                "overrides hole:="	, False,
                "hole diameter:="	, ["0mm"],
                "Pin:="			, True,
                "highest_layer:="	, top_layer,
                "lowest_layer:="	, bot_layer
            ])
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
        """
        self.oexcitation.Delete(portname)
        return True

    @aedt_exception_handler
    def import_edb(self, edb_full_path):
        """Import EDB.

        Parameters
        ----------
        edb_full_path : str
            Full path to the EDB.
            
        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed. 
        """
        oTool = self.odesktop.GetTool("ImportExport")
        oTool.ImportEDB(edb_full_path)
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
        list
            List of validation messages.

        """
        if name is None:
            name= self.design_name
        if outputdir is None:
            outputdir = self.project_path

        self._messenger.add_info_message("#### Design Validation Checks###")
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
            msgs = self._desktop.GetMessages(name, "HFSSDesign1", 0)
            # need to check if design name is always this default name HFSSDesign1
            for msg in msgs:
                self._messenger.add_info_message(msg)
                # msg = msg.replace('"','')
                msg = msg.rstrip('\r\n')
                val_list.append(msg)
                validation.writelines(msg + "\n")

            # Run Design Validation and write out the lines to the logger

            ret = self._odesign.ValidateCircuit()
            msg = "Design Validation Messages:"
            validation.writelines(msg + "\n")
            val_list.append(msg)
            if ret == 0:
                msg = "**** ERRORS Present - please check and confirm"
                self._messenger.add_error_message(msg)
            else:
                msg = "**** Validation Completed Correctly"
                self._messenger.add_info_message(msg)

            # Find the Excitations and check or list them out
            msg = "Excitation Messages:"
            validation.writelines(msg + "\n")
            val_list.append(msg)
            numportsdefined = int(len(self.get_excitations_name))
            if ports is not None and ports != numportsdefined:
                msg = "**** Port Number Error! - Please check model"
                self._messenger.add_error_message(msg)
                validation.writelines(msg + "\n")
                val_list.append(msg)
                validation_ok = False
                # need to stop the simulation athis point
            else:
                msg1 = "Ports Requested: " + str(ports)
                msg2 = "Ports Defined: " + str(numportsdefined)
                self._messenger.add_info_message(msg1)
                validation.writelines(msg1 + "\n")
                val_list.append(msg1)
                self._messenger.add_info_message(msg2)
                validation.writelines(msg2 + "\n")
                val_list.append(msg2)

            excitation_names = self.get_excitations_name
            for excitation in excitation_names:
                msg = "Excitation name: " + str(excitation)
                self._messenger.add_info_message(msg)
                validation.writelines(msg + "\n")
                val_list.append(msg)
        validation.close()
        return val_list, validation_ok  # return all the info in a list for use later

    @aedt_exception_handler
    def create_scattering(self, plot_name="S Parameter Plot Nominal", sweep_name=None, port_names=None, port_excited=None, variations=None):
        """Create a scattering report.
        

        Parameters
        ----------
        PlotName : str, optional
             Name of the plot. The default is ``"S Parameter Plot Nominal"``.
        sweep_name : str, optional
             Name of the sweep. The default is ``None``.
        PortNames : str or list, optional
             Names of one or more ports. The default is ``None``.
        PortExcited : optional
             The default is ``None``.
        variations : optional
             The default is ``None``.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.
        """
        Families = ["Freq:=", ["All"]]
        if variations:
            Families +=variations
        else:
            Families += self.get_nominal_variation()
        if not sweep_name:
            sweep_name = self.existing_analysis_sweeps[1]
        if not port_names:
            port_names = self.get_excitations_name
        if not port_excited:
            port_excited= port_names
        Trace = ["X Component:=", "Freq", "Y Component:=", ["dB(S(" + p + "," + q + "))" for p,q in zip(list(port_names), list(port_excited))]]
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
                plot_name,
                solution_data,
                "Rectangular Plot",
                sweep_name,
                ["Domain:=", "Sweep"],
                Families,
                Trace,
                [])
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
        """
        # normalize the save path
        if not filename:
            appendix = ""
            for v, vv in zip(variation, variations_value):
                appendix += "_" + v + vv.replace("\'", "")
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
        FreqsArray = ["all"]  # array containin the frequencies to export, use ["all"] for all frequencies
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

        self.odesign.ExportNetworkData(variation_str, SolutionSelectionArray, FileFormat,
                                       OutFile, FreqsArray, DoRenorm, RenormImped, DataType, Pass, ComplexFormat,
                                       DigitsPrecision, IncludeGammaImpedance, IncludeGammaImpedance,
                                       NonStandardExtensions)
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
    def create_frequency_sweep(self, setupname, unit, freqstart, freqstop, num_of_freq_points,
                               sweepname=None, sweeptype="interpolating",
                               interpolation_tol_percent=0.5, interpolation_max_solutions=250,
                               save_fields=True, save_rad_fields_only=False,
                               use_q3d_for_dc=False):
        """Create a frequency sweep.

        Parameters
        ----------
        setupname : str
            Name of the setup that is attached to the sweep.
        unit :
            Units, such as ``"MHz"`` or ``"GHz"``.
        freqstart : float
            Starting frequency of the sweep.
        freqstop : float
            Stopping frequency of the sweep.
        num_of_freq_points : int
            Number of frequency points in the range.
        sweepname : str
            Name of the sweep. The default is ``None``.
        sweeptype : str, optional
            Type of the sweep. Options are ``"Fast"``, ``"Interpolating"``, and ``"Discrete"``. The default is ``"Interpolating``.
        interpolation_tol_percent : float, optional
            Error tolerance threshold for the interpolation process. The default is ``0.5``.
        interpolation_max_solutions : int, optional
            Maximum number of solutions evaluated for the interpolation process. The default is ``250``.
        save_fields : bool, optional
            Whether to save the fields for a discrete sweep only. The default is ``True``.
        save_rad_fields_only : bool, optional
            Whether to save only the radiated fields if ``save_fields=True``. The default is ``False``.
        use_q3d_for_dc : bool, optional
            Whether to use Q3D to solve the DC point. The default is ``False``.

        Returns
        -------
        str
            Setup name if operation is successful.
        """
        if sweepname is None:
            sweepname = generate_unique_name("Sweep")
        interpolation = False
        if sweeptype == "interpolating":
            interpolation = True
            save_fields = False

        if not save_fields:
            save_rad_fields_only = False
        interpolation_tol = interpolation_tol_percent / 100.
        sweep = SweepString()
        sweep.add_sweep([freqstart, freqstop, num_of_freq_points], "linear_count", unit)
        # the add_sweep function supports all sweeps type e.g.
        #   sweep.add_sweep([10, 20, 1], "linear_step", "MHz")
        #   sweep.add_sweep([1, 1000, 100], "log_scale", "kHz")
        #   sweep.add_sweep([7,13,17,19,23], "single", unit)
        sweep_string = sweep.get_string()
        setup = self.get_setup(setupname)
        if sweepname in [name.name for name in setup.sweeps]:
            sweepname = generate_unique_name(sweepname)
        sweep= setup.add_sweep(sweepname=sweepname)
        sweep.change_range("LinearCount", freqstart,freqstop, num_of_freq_points )
        setup.props["GenerateSurfaceCurrent"]=save_fields
        setup.props["SaveRadFieldsOnly"] = save_rad_fields_only
        setup.props["FastSweep"] = interpolation
        setup.props["SAbsError"] = interpolation_tol
        setup.props["EnforcePassivity"] = interpolation
        setup.props["UseQ3DForDC"] = use_q3d_for_dc
        setup.props["MaxSolutions"] = interpolation_max_solutions
        setup.update()
        # arg = ["NAME:" + sweepname,
        #        [
        #         "NAME:Properties",
        #         "Enable:=", "true"
        #        ],
        #        [
        #         "NAME:Sweeps",
        #         "Variable:=", sweepname,
        #         "Data:=", sweep_string,
        #         "OffsetF1:=", False,
        #         "Synchronize:=", 0
        #        ],
        #        "GenerateSurfaceCurrent:=", save_fields,
        #        "SaveRadFieldsOnly:=", save_rad_fields_only,
        #        "FastSweep:=", interpolation,
        #        "ZoSelected:=", False,
        #        "SAbsError:=", interpolation_tol,
        #        "ZoPercentError:=", 1,
        #        "GenerateStateSpace:=", False,
        #        "EnforcePassivity:=", interpolation,
        #        "PassivityTolerance:=", 0.0001,
        #        "UseQ3DForDC:=", use_q3d_for_dc,
        #        "ResimulateDC:=", False,
        #        "MaxSolutions:=", interpolation_max_solutions,
        #        "InterpUseSMatrix:=", True,
        #        "InterpUsePortImpedance:=", True,
        #        "InterpUsePropConst:=", True,
        #        "InterpUseFullBasis:=", True,
        #        "CustomFrequencyString:=", "",
        #        "AllEntries:=", False,
        #        "AllDiagEntries:=", False,
        #        "AllOffDiagEntries:=", False,
        #        "MagMinThreshold:=", 0.01
        #        ]
        #
        # self.oanalysis.AddSweep(setupname, arg)
        # self.oanalysis_setup.AddSweep(setupname, arg)
        # self._messenger.add_debug_message("Sweep Setup created correctly")
        return setup

    @aedt_exception_handler
    def import_gds(self, gds_path, aedb_path=None, xml_path=None, set_as_active=True, close_active_project=False):
        """Import grounds into HFSS 3D Layout and assign the stackup from an XML file if present.

        Parameters
        ----------
        gds_path : str
            Full path to the GDS file.
        aedb_path : str, optional
            Full path to the AEDB file
        xml_path : str, optional
            Path to the XML file with stackup information. The default is ``None``, in 
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
        """
        active_project = self.project_name
        project_name = os.path.basename(gds_path)[:-4]
        if not aedb_path:
            aedb_path = gds_path.replace('.gds', '.aedb')
        if os.path.exists(aedb_path):
            old_name = project_name
            project_name = generate_unique_name(project_name)
            aedb_path = gds_path.replace(old_name + '.gds', project_name + '.aedb')
            self._messenger.add_warning_message("aedb_exists. Renaming it to {}".format(project_name))

        oTool = self.odesktop.GetTool("ImportExport")
        oTool.ImportGDSII(gds_path, aedb_path, "", "")
        project = self.odesktop.SetActiveProject(project_name)
        oeditor = project.GetActiveDesign().SetActiveEditor("Layout")
        if xml_path:
            oeditor.ImportStackupXML(xml_path)
        if set_as_active:
            self.__init__(project_name)
        if close_active_project:
            self.odesktop.CloseProject(active_project)
        return True
