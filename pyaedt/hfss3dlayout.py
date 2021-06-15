"""
Introduction
------------------

This class contains all HFSS 3D Layout functionalities. It inherits
all objects that belong to HFSS 3D Layout, including EDB API queries.


Examples
--------

Create an ``Hfss3dLayout`` object and connect to an existing HFSS design or create a new HFSS design if one does not exist.

>>> aedtapp = Hfss3dLayout()

Create an ``Hfss3dLayout`` object and link to a project named ``projectname``. If this project does not exist, create one with this name.

>>> aedtapp = Hfss3dLayout(projectname)

Create an ``Hfss3dLayout`` object and link to a design named ``designname`` in a project named ``projectname``.

>>> aedtapp = Hfss3dLayout(projectname,designame)

Create an ``Hfss3dLayout`` object and open the specified project.

>>> aedtapp = Hfss3dLayout("myfile.aedt")

Create a ``Desktop on 2021R1`` object and then creates an ``Hfss3dLayout`` object and open the specified project.

>>> aedtapp = Hfss3dLayout(specified_version="2021.1", projectname="myfile.aedt")

"""

from __future__ import absolute_import
import os

from .application.Analysis3DLayout import FieldAnalysis3DLayout
from .desktop import exception_to_desktop

from .generic.general_methods import generate_unique_name, aedt_exception_handler



class SweepString(object):
    """Generate a sweep string like this example: ``"LIN 10GHz 20GHz 0.05GHz LINC 20GHz 30GHz 10 DEC 30GHz 40GHz 10 40GHz``"""
    def __init__(self, unit='GHz'):
        """

        :param unit:
        """
        self.unit = unit
        self.sweep_string = ""

    @aedt_exception_handler
    def add_sweep(self, sweep, line_type, unit=None):
        """Add a sweep line to the string.

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
            Units such as ``"MHz"``, ``"GHz"``, and so on. The default is ``None``.

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


class Hfss3dLayout(FieldAnalysis3DLayout, object):
    """HFSS 3D Layout Object

    Parameters
    ----------
    projectname : str
        Name of the project to select or the full path to the project or AEDTZ archive to open. 
        If ``None``, try to get the active project and, if none exists, create an empty project.
    designname : str
        Name of the design to select. If ``None``, try to get the active design and, if none exists, create an empty design.
    solution_type : str
        Solution type to apply to the design. If ``None``, use the default.
    setup_name :
        Name of the setup to use as the nominal. If ``None``, the active setup is used or nothing is used.

    Returns
    -------

    """

    def __init__(self, projectname=None, designname=None, solution_type=None, setup_name=None,
                 specified_version=None, NG=False, AlwaysNew=False, release_on_exit=False):
        FieldAnalysis3DLayout.__init__(self, "HFSS 3D Layout Design", projectname, designname, solution_type,
                                       setup_name, specified_version, NG, AlwaysNew, release_on_exit)

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
            Edge number on which to create the port.
        iscircuit : bool
            Indicates if it is a circuit port. The default is ``False``.

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
            Name of the via on which to create the port.
        layer : str
            Name of the layer.
        xstart :
            X-axis position of the pin.
        ystart :
            Y-axis position of the pin.
        xend :
            X-axis position of the pin.
        yend :
            Y-axis end position of the pin.
        archeight :
            Arc height. The default is ``0``.
        arcrad :
            Rotation of the pin in rad. The default is ``0``.
        isexternal : bool
            Indicates if the pin is external. If ''True,`` the pin is external. If ''False,`` the pin is internal. The default is ``True``.

        Returns
        -------
        type
            Name of the port | False error

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
        xpos :
            X-axis position of the pin. The default is ``0``.
        ypos :
            Y-axis position of the pin. The default is ``0``.
        rotation :
            Rotation of the pin in degrees. The default is ``0``.
        top_layer : str
            Top layer of the pin. If ``None``, it is automatically assigned to the top. The default is ``None``.
        bot_layer : str
            Bottom layer of the pin. If ``None``, it is automatically assigned to the bottom. The default is ``None``.

        Returns
        -------
        type
            True

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
        """

        Parameters
        ----------
        portname : str
        The name of the port.          

        Returns
        -------

        """
        self.oexcitation.Delete(portname)
        return True

    @aedt_exception_handler
    def import_edb(self, edb_full_path):
        """

        Parameters
        ----------
        edb_full_path : str
            

        Returns
        -------

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
        name : str
            Name of the design to validate. The default is ``None``.
        outputdir : str
            Output directory in which to save the log file. The default is ``None``.
        ports : str
            Number of excitations expected. The default is ``None``.

        Returns
        -------
        type
            All the info in a list for later use

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
        """Create scattering Report
        

        Parameters
        ----------
        PlotName :
             The name of the plot. The default is ``"S Parameter Plot Nominal"``
        sweep_name : str
             The default is ``None``.
        PortNames : str
             The names of the port. The default is ``None``.
        PortExcited : str
             The default is ``None``.
        variations :
             The default is ``None``.

        Returns
        -------

        """
        Families = ["Freq:=", ["All"]]
        if variations:
            Families +=variations
        else:
            Families += self.get_nominal_variation()
        if not sweep_name:
            sweep_name = self.existing_analysis_sweeps[1]
        if not port_names:
            port_names = self.modeler.get_excitations_name()
        if not port_excited:
            port_excited= port_names
        Trace = ["X Component:=", "Freq", "Y Component:=", ["dB(S(" + p + "," + q + "))" for p,q in zip(list(port_names), list(port_excited))]]
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
        else:
            return False

    @aedt_exception_handler
    def export_touchstone(self, solutionname, sweepname, filename, variation, variations_value):
        """Export the Touchstone file.
        
        Parameters
        ----------
        solutionname : str
            Name of the solution that has been solved.    
        sweepname : str
            Name of the sweep that has been solved.
        filename : str
            Full path of the output file.
        variation : list
            List of all parameter variations, such  as ``["$AmbientTemp", "$PowerIn"]``.
        variations_value : list
            List of all parameter variation values, such as ``["22cel", "100"]``.

        Returns
        -------

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
    def set_export_touchstone(self, activate):
        """Set automatic export of the Touchstone file after the simulation is ``True``.

        Parameters
        ----------
        activate : bool
            Export after the simulation.

        Returns
        -------
        type
            True if operation succeeded

        """

        settings = []
        if activate:
            settings.append("NAME:Design Settings Data")
            settings.append("Export After Simulation:=")
            settings.append(True)
            settings.append("Export Dir:=")
            settings.append("")
        elif not activate:
            settings.append("NAME:Design Settings Data")
            settings.append("Export After Simulation:=")
            settings.append(False)
        self.odesign.SetDesignSettings(settings)
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
            Units such as ``"MHz"``, ``"GHz"``, and so on.
        freqstart :
            Starting frequency of the sweep.
        freqstop :
            Stopping frequency of the sweep.
        sweepname : str
            Name of the sweep. The default is ``None``.
        num_of_freq_points :
            Number of frequency points in the range.
        sweeptype : discrete
            Type of sweep. Choices are ``"Fast"``, ``"Interpolating"``, and ``"Discrete"``. The default is ``"Interpolating``.
        interpolation_max_solutions :
            Maximum number of solutions evaluated for the interpolation process. The default is ``250``.
        interpolation_tol_percent :
            Error tolerance threshold for the interpolation process. The default is ``0.5``.
        save_fields : bool
            Save the fields for a discrete sweep only. The default is ``True``.
        save_rad_fields_only : bool
            Save only the radiated fields if ``save_fields = True``. The default is ``False``.
        use_q3d_for_dc : bool
            Use Q3D to solve the DC point. The default is ``False``.

        Returns
        -------
        type
            Setup name if operation succeeded

        """
        if sweepname is None:
            sweepname = generate_unique_name("Sweep")
        if sweeptype == "interpolating":
            interpolation = True
            save_fields = False
        elif sweeptype == "discrete":
            interpolation = False
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

        arg = ["NAME:" + sweepname,
               [
                "NAME:Properties",
                "Enable:=", "true"
               ],
               [
                "NAME:Sweeps",
                "Variable:=", sweepname,
                "Data:=", sweep_string,
                "OffsetF1:=", False,
                "Synchronize:=", 0
               ],
               "GenerateSurfaceCurrent:=", save_fields,
               "SaveRadFieldsOnly:=", save_rad_fields_only,
               "FastSweep:=", interpolation,
               "ZoSelected:=", False,
               "SAbsError:=", interpolation_tol,
               "ZoPercentError:=", 1,
               "GenerateStateSpace:=", False,
               "EnforcePassivity:=", interpolation,
               "PassivityTolerance:=", 0.0001,
               "UseQ3DForDC:=", use_q3d_for_dc,
               "ResimulateDC:=", False,
               "MaxSolutions:=", interpolation_max_solutions,
               "InterpUseSMatrix:=", True,
               "InterpUsePortImpedance:=", True,
               "InterpUsePropConst:=", True,
               "InterpUseFullBasis:=", True,
               "CustomFrequencyString:=", "",
               "AllEntries:=", False,
               "AllDiagEntries:=", False,
               "AllOffDiagEntries:=", False,
               "MagMinThreshold:=", 0.01
               ]

        self.oanalysis.AddSweep(setupname, arg)
        # self.oanalysis_setup.AddSweep(setupname, arg)
        # self._messenger.add_debug_message("Sweep Setup created correctly")
        return sweepname



