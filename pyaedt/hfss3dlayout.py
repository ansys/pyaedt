"""
HFSS 3DLayout Class
----------------------------------------------------------------

Disclaimer
==================================================

**Copyright (c) 1986-2021, ANSYS Inc. unauthorised use, distribution or duplication is prohibited**

**This tool release is unofficial and not covered by standard Ansys Support license.**


Description
==================================================

This class contains all the HFSS 3DLayout Functionalities. It inherites all the objects that belongs to HFSS 3DLayout


:Example:

hfss = HFSS3DLayout()     creates and hfss 3DLayout object and connect to existing hfss 3DLayout design (create a new 3DLayout design if not present)


hfss = HFSS3DLayout(projectname)     creates and 3DLayout object and link to projectname project


hfss = HFSS3DLayout(projectname,designame)     creates and 3DLayout object and link to designname design in projectname project


hfss = HFSS3DLayout("myfile.aedt")     creates and 3DLayout object and open specified project



========================================================

"""
from __future__ import absolute_import
import os

from .application.Analysis3DLayout import FieldAnalysis3DLayout
from .desktop import exception_to_desktop

from .generic.general_methods import generate_unique_name, aedt_exception_handler



class SweepString(object):
    """
    generate a sweep string like for example "LIN 10GHz 20GHz 0.05GHz LINC 20GHz 30GHz 10 DEC 30GHz 40GHz 10 40GHz"
    """
    def __init__(self, unit='GHz'):
        """

        :param unit:
        """
        self.unit = unit
        self.sweep_string = ""

    @aedt_exception_handler
    def add_sweep(self, sweep, line_type, unit=None):
        """
        Add a sweep line to the string

        :param sweep: list of frequencies,
                        if linear_step [start, stop, step]
                        if linear_count [start, stop, number of steps]
                        if log_scale [start, stop, samples]
                        if single [f1, f2,... fn]
        :param line_type: "linear_step", "linear_count", "log_scale", "single"
        :param unit: "MHz", "GHz",...
        :return:
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
        if self.sweep_string:
            return self.sweep_string
        else:
            return None


class Hfss3dLayout(FieldAnalysis3DLayout, object):
    """HFSS 3D Layout Object

    :param projectname: name of the project to be selected or full path to the project to be opened  or to the AEDTZ archive. if None try to get active project and, if nothing present to create an empy one
    :param designname: name of the design to be selected. if None, try to get active design and, if nothing present to create an empy one
    :param solution_type: solution type to be applied to design. if None default is taken
    :param setup_name: setup_name to be used as nominal. if none active setup is taken or nothing
    """

    def __init__(self, projectname=None, designname=None, solution_type=None, setup_name=None):
        FieldAnalysis3DLayout.__init__(self, "HFSS 3D Layout Design", projectname, designname, solution_type,
                                       setup_name)

    def __enter__(self):
        return self

    def __exit__(self, ex_type, ex_value, ex_traceback):
        ''' Push exit up to parent object Design '''
        if ex_type:
            exception_to_desktop(self, ex_value, ex_traceback)

    @aedt_exception_handler
    def create_edge_port(self, primivitivename, edgenumber, iscircuit=True):
        """
        Create a new edge port


        :param primivitivename: name of the primitive
        :param edgenumber: edge number on which create a port
        :param iscircuit: True (Circuit Port) | False
        :return: Name of the port
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
        """Create a new Coax Port


        :param vianame: Name of the Via on which create a new Port
        :param layer: layer name
        :param xstart: x position of pin
        :param ystart: y position of pin
        :param xend: x end position of pin
        :param yend: y end position of pin
        :param archeight: arc height
        :param arcrad: rotation of pin in rad
        :param isexternal: True (is external pin) | False is internal Pin
        :return: name of the port | False error
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
        """
        Create a new Pin Port


        :param name: Name of the Pin Port
        :param xpos: x position of pin
        :param ypos: y position of pin
        :param rotation: rotation of pin in deg
        :param top_layer: top layer of pin. if None, it will be automatically assigned to the top
        :param bot_layer: bottom layer of pin. if None, it will be automatically assigned to the bottom
        :return: True
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
        self.oexcitation.Delete(portname)
        return True

    @aedt_exception_handler
    def import_edb(self, edb_full_path):
        oTool = self.odesktop.GetTool("ImportExport")
        oTool.ImportEDB(edb_full_path)
        self.oproject = self.odesktop.GetActiveProject().GetName()
        self.odesign = self.odesktop.GetActiveProject().GetActiveDesign().GetName().split(";")[1]
        return True

    @aedt_exception_handler
    def validate_full_design(self, name=None, outputdir=None, ports=None):
        """
        Validate the design based on expected value and save infos on log file


        :param name: name of design to validate
        :param outputdir: output dir where to save the log file
        :param ports: number of excitations expected
        :return: all the info in a list for use later
        """
        if name is None:
            name= self.design_name
        if outputdir is None:
            outputdir = self.project_path

        self._messenger.add_info_message("#### Design Validation Checks###")
        #
        # Routine outputs to the validtaion info to a log file in the project directory and also
        # returns the validation info to be used to update properties.xml file

        validation_ok = True

        #
        # Write an overall validation log file with all output from all checks
        # the design validation inside HFSS outputs to a separate log file which we merge into this overall file
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
                msg = "**** ERRRORS Present - please check and confirm"
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
    def create_scattering(self, PlotName="S Parameter Plot Nominal", sweep_name=None, PortNames=None, PortExcited=None, variations=None ):
        """
        Create Scattering Report


        sweeps = design eXploration variations (list of str)
        PortNames = (list of str)
        PortExcited = (str)
        :return:
        """
        # set plot name
        # Setup arguments list for CreateReport function
        Families = ["Freq:=", ["All"]]
        if variations:
            Families +=variations
        else:
            Families += self.get_nominal_variation()
        if not sweep_name:
            sweep_name = self.existing_analysis_sweeps[1]
        if not PortNames:
            PortNames = self.modeler.get_excitations_name()
        if not PortExcited:
            PortExcited= PortNames
        Trace = ["X Component:=", "Freq", "Y Component:=", ["dB(S(" + p + "," + q + "))" for p,q in zip(list(PortNames), list(PortExcited))]]
        solution_data = ""
        if self.solution_type == "DrivenModal":
            solution_data = "Modal Solution Data"
        elif self.solution_type == "DrivenTerminal":
            solution_data = "Terminal Solution Data"
        if solution_data != "":
            # run CreateReport function
            self.post.oreportsetup.CreateReport(
                PlotName,
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

        # export the image

    @aedt_exception_handler
    def export_touchstone(self, solutionname, sweepname, filename, variation, variations_value):
        """
        Export the touchstone file


        solutionname = name of the solution solved
        sweepname = name of the sweep solved
        FileName = full path of output file
        Variations = list (list of all parameters variations e.g. ["$AmbientTemp", "$PowerIn"] )
        VariationsValue = list (list of all parameters variations value) e.g. ["22cel", "100"] )
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
        """
        Set Automatic export of touchstone after simulation to True


        :param activate: Export after simulation
        :type activate: bool
        :return: True if operation succeeded
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
        """ Create a Frequency Sweep


        :param setupname: name of the setup to which is attached the sweep
        :param unit: Units ("MHz", "GHz"....)
        :param freqstart: Starting Frequency of sweep
        :param freqstop:  Stop Frequency of Sweep
        :param sweepname: name of the Sweep
        :param num_of_freq_points: Number of frequency point in the range
        :param sweeptype: "discrete"|"interpolating" (default)
        :param interpolation_max_solutions: max number of solutions evaluated for the interpolation process
        :param interpolation_tol_percent: error tolerance threshold for the interpolation process
        :param save_fields: save the fields (only for discrete sweep)
        :param save_rad_fields_only: save only the radiated fields (only if save_fields = True)
        :param use_q3d_for_dc: Use Q3D to solve DC point
        :return: Setup Name if operation succeeded
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





