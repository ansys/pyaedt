"""
Post Processing Library Class
--------------------------------------------------------------------------------


Description
============================================================

This class contains all the functionalities to create and edit plots in all the 3D Tools.

NOTE: Some functionalities are available only in graphical mode

==============================================

"""
from __future__ import absolute_import
import os
import shutil
import random
import string
import time
import math
import itertools
from collections import OrderedDict
from ..modeler.Modeler import CoordinateSystem
from ..generic.general_methods import aedt_exception_handler, generate_unique_name
from ..application.Variables import AEDT_units

report_type = {"DrivenModal": "Modal Solution Data", "DrivenTerminal": "Terminal Solution Data",
               "Eigenmode": "EigenMode Parameters",
               "Transient Network": "Terminal Solution Data", "SBR+": "Modal Solution Data", "Transient": "Transient",
               "EddyCurrent": "EddyCurrent",
               "SteadyTemperatureAndFlow": "Monitor", "SteadyTemperatureOnly": "Monitor", "SteadyFlowOnly": "Monitor",
               "SteadyState": "Monitor", "NexximLNA": "Standard", "NexximDC": "Standard",
               "Magnetostatic": "Magnetostatic", "Electrostatic": "Electrostatic",
               "NexximTransient": "Standard", "HFSS3DLayout": "Terminal Solution Data", "Matrix": "Matrix",
               "HFSS 3D Layout Design": "Standard", "Q3D Extractor": "Matrix", "2D Extractor": "Matrix"}


class SolutionData(object):
    """Data Class containing information from GetSolutionfromVariation call"""


    @property
    def sweeps(self):
        """ """
        return self._sweeps

    @property
    def sweeps_siunits(self):
        """ """
        data = {}
        for el in self._sweeps:
            data[el] = self._convert_list_to_SI(self._sweeps[el], self._quantity(self.units_sweeps[el]), self.units_sweeps[el])
        return data

    @property
    def variations_value(self):
        """ """
        vars = self.nominal_variation.GetDesignVariableNames()
        variationvals = {}
        for v in vars:
            variationvals[v] = self.nominal_variation.GetDesignVariableValue(v)
        return variationvals

    @property
    def nominal_variation(self):
        """ """
        return self._nominal_variation

    @nominal_variation.setter
    def nominal_variation(self, val):
        """

        Parameters
        ----------
        val :
            

        Returns
        -------

        """
        if 0 <= val <= self.number_of_variations:
            self._nominal_variation = self._original_data[val]
        else:
            print(str(val) + " not in Variations")

    @property
    def primary_sweep(self):
        """ """
        return self._primary_sweep

    @primary_sweep.setter
    def primary_sweep(self, ps):
        """Set the primary Sweep to ps

        Parameters
        ----------
        ps :
            

        Returns
        -------

        """
        if ps in self.sweeps.keys():
            self._primary_sweep = ps

    @property
    def expressions(self):
        """ """
        mydata = [i for i in self._nominal_variation.GetDataExpressions()]
        return list(dict.fromkeys(mydata))

    def __init__(self, Data):
        self._original_data = Data
        self.number_of_variations = len(Data)
        self._nominal_variation = None
        self.nominal_variation = 0
        self._sweeps = None
        self._sweeps_names = list(self.nominal_variation.GetSweepNames())
        self.update_sweeps()

        self._primary_sweep = self._sweeps_names[0]
        self.nominal_sweeps = {}
        self.units_sweeps = {}
        for e in self.sweeps.keys():
            try:
                self.nominal_sweeps[e] = self.sweeps[e][0]
                self.units_sweeps[e] = self.nominal_variation.GetSweepUnits(e)
            except:
                self.nominal_sweeps[e] = None
        self.solutions_data_real = self._solution_data_real()
        self.solutions_data_imag = self._solution_data_imag()
        self.solutions_data_mag = {}
        self.units_data = {}
        for expr in self.expressions:
            self.solutions_data_mag[expr] = {}
            self.units_data[expr] = self.nominal_variation.GetDataUnits(expr)
            for i in self.solutions_data_real[expr]:
                self.solutions_data_mag[expr][i] = abs(
                    complex(self.solutions_data_real[expr][i], self.solutions_data_imag[expr][i]))

    @aedt_exception_handler
    def update_sweeps(self):
        """:return:"""
        self._sweeps = OrderedDict({})
        for el in self._sweeps_names:
            self._sweeps[el] = [i for i in self.nominal_variation.GetSweepValues(el, False)]
            self._sweeps[el] = list(dict.fromkeys(self._sweeps[el]))
        return self._sweeps

    @aedt_exception_handler
    def _quantity(self, unit):
        """

        Parameters
        ----------
        unit :
            

        Returns
        -------

        """
        for el in AEDT_units:
            keys_units = [i.lower() for i in list(AEDT_units[el].keys())]
            if unit.lower() in keys_units:
                return el
        return None

    @aedt_exception_handler
    def _solution_data_real(self):
        """ """
        sols_data = {}
        for expression in self.expressions:
            solution = list(self.nominal_variation.GetRealDataValues(expression,False))
            values = []
            for el in reversed(self._sweeps_names):
                values.append(self.sweeps[el])
            solution_Data = {}
            i = 0
            for t in itertools.product(*values):
                solution_Data[t] = solution[i]
                i += 1
            sols_data[expression] = solution_Data
        return sols_data

    def _solution_data_imag(self):
        """ """
        sols_data = {}
        for expression in self.expressions:
            try:
                solution = list(self.nominal_variation.GetImagDataValues(expression,False))
            except:
                solution = [0 for i in range(len(self.solutions_data_real[expression]))]
            values = []
            for el in reversed(self._sweeps_names):
                values.append(self.sweeps[el])
            solution_Data = {}
            i = 0
            for t in itertools.product(*values):
                solution_Data[t] = solution[i]
                i += 1
            sols_data[expression] = solution_Data
        return sols_data

    @aedt_exception_handler
    def to_degrees(self, input_list):
        """Convert input list to degrees from radians

        Parameters
        ----------
        input_list :
            list of input radians

        Returns
        -------
        type
            output list of degrees

        """
        return [i*2*math.pi/360 for i in input_list]

    @aedt_exception_handler
    def to_radians(self, input_list):
        """Convert input list to radians from degrees

        Parameters
        ----------
        input_list :
            list of input degrees

        Returns
        -------
        type
            output list of radians

        """
        return [i*360/(2*math.pi) for i in input_list]

    def data_magnitude(self, expression=None, convert_to_SI=False):
        """Return the data magnitude of the given expression. if no expression is provided, first expression is provided

        Parameters
        ----------
        expression :
            string expression name (Default value = None)
        convert_to_SI :
            Boolean, if True it converts data to SI System (Default value = False)

        Returns
        -------
        type
            List of data

        """
        if not expression:
            expression = self.expressions[0]
        temp = []
        for it in self.nominal_sweeps:
            temp.append(self.nominal_sweeps[it])
        temp = list(reversed(temp))
        try:
            solution_Data = self.solutions_data_mag[expression]
            sol = []
            position = list(reversed(self._sweeps_names)).index(self.primary_sweep)
            for el in self.sweeps[self.primary_sweep]:
                temp[position]=el
                sol.append(solution_Data[tuple(temp)])
        except:
            sol = []
            position = list(reversed(self._sweeps_names)).index(self.primary_sweep)
            for el in self.sweeps[self.primary_sweep]:
                temp[position]=el
                sol.append(0)
        if convert_to_SI and self._quantity(self.units_data[expression]):
            sol = self._convert_list_to_SI(sol, self._quantity(self.units_data[expression]), self.units_data[expression])
        return sol

    @aedt_exception_handler
    def _convert_list_to_SI(self,datalist, dataunits, units):
        """

        Parameters
        ----------
        datalist :
            
        dataunits :
            
        units :
            

        Returns
        -------

        """
        sol = datalist
        if dataunits in AEDT_units and units in AEDT_units[dataunits]:
            sol = [i * AEDT_units[dataunits][units] for i in datalist]
        return sol

    @aedt_exception_handler
    def data_db(self, expression=None, convert_to_SI=False):
        """Return the data in db of the given expression. if no expression is provided, first expression is provided

        Parameters
        ----------
        expression :
            string expression name (Default value = None)
        convert_to_SI :
            Boolean, if True it converts data to SI System (Default value = False)

        Returns
        -------
        type
            List of data

        """
        if not expression:
            expression = self.expressions[0]

        return [10*math.log10(i) for i in self.data_magnitude(expression,convert_to_SI)]


    def data_real(self, expression=None, convert_to_SI=False):
        """Return the real part of data  of the given expression. if no expression is provided, first expression is provided

        Parameters
        ----------
        expression :
            string expression name (Default value = None)
        convert_to_SI :
            Boolean, if True it converts data to SI System (Default value = False)

        Returns
        -------
        type
            List of data

        """
        if not expression:
            expression = self.expressions[0]
        temp = []
        for it in self.nominal_sweeps:
            temp.append(self.nominal_sweeps[it])
        temp = list(reversed(temp))
        try:
            solution_Data = self.solutions_data_real[expression]
            sol = []
            position = list(reversed(self._sweeps_names)).index(self.primary_sweep)
            for el in self.sweeps[self.primary_sweep]:
                temp[position]=el
                sol.append(solution_Data[tuple(temp)])
        except:
            sol = []
            position = list(reversed(self._sweeps_names)).index(self.primary_sweep)
            for el in self.sweeps[self.primary_sweep]:
                temp[position]=el
                sol.append(0)
        if convert_to_SI and self._quantity(self.units_data[expression]):
            sol = self._convert_list_to_SI(sol, self._quantity(self.units_data[expression]), self.units_data[expression])
        return sol

    def data_imag(self, expression=None, convert_to_SI=False):
        """Return the imaginary part of data  of the given expression. if no expression is provided, first expression is provided

        Parameters
        ----------
        expression :
            string expression name (Default value = None)
        convert_to_SI :
            Boolean, if True it converts data to SI System (Default value = False)

        Returns
        -------
        type
            List of data

        """
        if not expression:
            expression = self.expressions[0]
        temp = []
        for it in self.nominal_sweeps:
            temp.append(self.nominal_sweeps[it])
        temp = list(reversed(temp))
        try:
            solution_Data = self.solutions_data_imag[expression]
            sol = []
            position = list(reversed(self._sweeps_names)).index(self.primary_sweep)
            for el in self.sweeps[self.primary_sweep]:
                temp[position]=el
                sol.append(solution_Data[tuple(temp)])
        except:
            sol = []
            position = list(reversed(self._sweeps_names)).index(self.primary_sweep)
            for el in self.sweeps[self.primary_sweep]:
                temp[position]=el
                sol.append(0)
        if convert_to_SI and self._quantity(self.units_data[expression]):
            sol = self._convert_list_to_SI(sol, self._quantity(self.units_data[expression]), self.units_data[expression])
        return sol



class FieldPlot:
    """ """

    def __init__(self, oField, objlist, solutionName, quantityName, intrinsincList={}):
        self.oField = oField
        self.faceIndexes = objlist
        self.solutionName = solutionName
        self.quantityName = quantityName
        self.intrinsincList = intrinsincList
        self.objtype = "Surface"
        self.listtype = "FaceList"
        self.name = "Field_Plot"
        self.Filled = False
        self.IsoVal = "Fringe"
        self.SmoothShade = True
        self.AddGrid = False
        self.MapTransparency = True
        self.Refinement = 0
        self.Transparency = 0
        self.SmoothingLevel = 0
        self.ArrowUniform = True
        self.ArrowSpacing = 0
        self.MinArrowSpacing = 0
        self.MaxArrowSpacing = 0
        self.GridColor = [255, 255, 255]
        self.PlotIsoSurface = True
        self.PointSize = 1
        self.CloudSpacing = 0.5
        self.CloudMinSpacing = -1
        self.CloudMaxSpacing = -1

    @aedt_exception_handler
    def create(self):
        """ """

        self.oField.CreateFieldPlot(self.surfacePlotInstruction, "Field")
        return True


    @aedt_exception_handler
    def update(self):
        """ """
        self.oField.ModifyFieldPlot(self.name, self.surfacePlotInstruction)



    @aedt_exception_handler
    def modify_folder(self):
        """ """
        self.oField.SetFieldPlotSettings(self.plotFolder,
                                         [
                                             "NAME:FieldsPlotItemSettings",
                                             self.plotsettings])
        return True

    @aedt_exception_handler
    def delete(self):
        """ """
        self.oField.DeleteFieldPlot([self.name])

    @property
    def plotFolder(self):
        """ """
        return self.name

    @property
    def plotGeomInfo(self):
        """ """
        info = [1, self.objtype, self.listtype, 0]
        for index in self.faceIndexes:
            info.append(str(index))
            info[3] += 1
        return info

    @property
    def intrinsicVar(self):
        """Support for both list or dictionaries
        :return:var list for field plot

        Parameters
        ----------

        Returns
        -------

        """
        var = ""
        if type(self.intrinsincList) is list:
            l = 0
            while l < len(self.intrinsincList):
                val = self.intrinsincList[l + 1]
                if ":=" in self.intrinsincList[l] and type(self.intrinsincList[l+1]) is list:
                    val = self.intrinsincList[l + 1][0]
                ll=self.intrinsincList[l].split(":=")
                var += ll[0] + "=\'" + str(val) + "\' "
                l += 2
        else:
            for a in self.intrinsincList:
                var += a + "=\'" + str(self.intrinsincList[a]) + "\' "
        return var

    @property
    def plotsettings(self):
        """ """
        if self.objtype == "Surface":
            arg = [
                "NAME:PlotOnSurfaceSettings",
                "Filled:=", self.Filled,
                "IsoValType:=", self.IsoVal,
                "SmoothShade:=", self.SmoothShade,
                "AddGrid:=", self.AddGrid,
                "MapTransparency:=", self.MapTransparency,
                "Refinement:=", self.Refinement,
                "Transparency:=", self.Transparency,
                "SmoothingLevel:=", self.SmoothingLevel,
                [
                    "NAME:Arrow3DSpacingSettings",
                    "ArrowUniform:=", self.ArrowUniform,
                    "ArrowSpacing:=", self.ArrowSpacing,
                    "MinArrowSpacing:=", self.MinArrowSpacing,
                    "MaxArrowSpacing:=", self.MaxArrowSpacing
                ],
                "GridColor:=", self.GridColor
            ]
        else:
            arg = [
                "NAME:PlotOnVolumeSettings",
                "PlotIsoSurface:=", self.PlotIsoSurface,
                "PointSize:=", self.PointSize,
                "Refinement:=", self.Refinement,
                "CloudSpacing:=", self.CloudSpacing,
                "CloudMinSpacing:=", self.CloudMinSpacing,
                "CloudMaxSpacing:=", self.CloudMaxSpacing,
                [
                    "NAME:Arrow3DSpacingSettings",
                    "ArrowUniform:=", self.ArrowUniform,
                    "ArrowSpacing:=", self.ArrowSpacing,
                    "MinArrowSpacing:=", self.MinArrowSpacing,
                    "MaxArrowSpacing:=", self.MaxArrowSpacing
                ]
            ]
        return arg

    @property
    def surfacePlotInstruction(self):
        """ """
        return [
            "NAME:" + self.name,
            "SolutionName:=", self.solutionName,
            "QuantityName:=", self.quantityName,
            "PlotFolder:=", self.plotFolder,
            "UserSpecifyName:=", 0,
            "UserSpecifyFolder:=", 0,
            "StreamlinePlot:=", False,
            "AdjacentSidePlot:=", False,
            "FullModelPlot:=", False,
            "IntrinsicVar:=", self.intrinsicVar,
            "PlotGeomInfo:=", self.plotGeomInfo,
            "FilterBoxes:=", [0],
            self.plotsettings, "EnableGaussianSmoothing:=", False]


class PostProcessor(object):
    """Manage Main AEDT PostProcess Functions
    AEDTConfig Class Inherited contains all the _desktop Hierarchical calls needed to the class
    init data: _desktop and Design Type  "HFSS","Icepak", "HFSS3DLayout"

    Parameters
    ----------

    Returns
    -------

    """

    def __init__(self, parent):
        """
        :param parent:  parent object e.g. AEDT Application
                        - needs to provide members _modeler, _desktop, _odesign, _messenger)
        """
        self._parent = parent
        self.FieldsPlot = {}

    @property
    def _primitives(self):
        """:return: eturn the model units as a string e.g. "mm"
        """
        return self._parent._modeler.primitives

    @property
    def model_units(self):
        """:return: eturn the model units as a string e.g. "mm"
        """
        return retry_ntimes(10, self.oeditor.GetModelUnits)

    @property
    def post_osolution(self):
        """:return: Solutions module"""
        return self.odesign.GetModule("Solutions")

    @property
    def ofieldsreporter(self):
        """:return: Fields Reporter module"""
        return self.odesign.GetModule("FieldsReporter")

    @property
    def oreportsetup(self):
        """:return: Report Setup module"""
        return self.odesign.GetModule("ReportSetup")

    @property
    def post_solution_type(self):
        """:return: Design Solution Typee"""
        try:
            return self.odesign.GetSolutionType()
        except:
            return self._parent._design_type


    @property
    def messenger(self):
        """ """
        return self._parent._messenger

    @property
    def desktop(self):
        """ """
        return self._parent._desktop

    @property
    def odesign(self):
        """ """
        return self._parent._odesign

    @property
    def oproject(self):
        """ """
        return self._parent._oproject

    @property
    def modeler(self):
        """ """
        return self._parent._modeler

    @property
    def oeditor(self):
        """ """
        return self.modeler.oeditor

    @property
    def report_types(self):
        """ """
        return list(self.oreportsetup.GetAvailableReportTypes())

    @aedt_exception_handler
    def display_types(self, report_type):
        """

        Parameters
        ----------
        report_type :
            

        Returns
        -------

        """
        return self.oreportsetup.GetAvailableDisplayTypes(report_type)

    # TODO: define a fields calculator module and make robust !!
    @aedt_exception_handler
    def volumetric_loss(self, object_name):
        """This function creates a new variable in field calculator for volumetric losses

        Parameters
        ----------
        object_name :
            object name on which compute Field Calculator losses

        Returns
        -------
        type
            name of the variable created

        """
        oModule = self.ofieldsreporter
        oModule.EnterQty("OhmicLoss")
        oModule.EnterVol(object_name)
        oModule.CalcOp("Integrate")
        name = "P_{}".format(object_name)  # Need to check for uniqueness !
        oModule.AddNamedExpression(name, "Fields")
        return name

    @aedt_exception_handler
    def change_field_property(self,plotname, propertyname, propertyval):
        """

        Parameters
        ----------
        plotname :
            
        propertyname :
            
        propertyval :
            

        Returns
        -------

        """
        self.odesign.ChangeProperty(
        [
            "NAME:AllTabs",
            [
                "NAME:FieldsPostProcessorTab",
                [
                    "NAME:PropServers",
                    "FieldsReporter:"+plotname
                ],
                [
                    "NAME:ChangedProps",
                    [
                        "NAME:"+propertyname,
                        "Value:="	, propertyval
                    ]
                ]
            ]
        ])

    @aedt_exception_handler
    def export_field_file_on_grid(self, quantity_name, solution=None, variation_dict=None, filename=None,
                                  gridtype="Cartesian", grid_center=[0, 0, 0],
                                  grid_start=[0, 0, 0], grid_stop=[0, 0, 0], grid_step=[0, 0, 0], isvector = False, intrinsics=None, phase=None):
        """This function creates a new field file based on a specific solution and variation available. using Field Calculator

        Parameters
        ----------
        quantity_name :
            name of quantity to export (eg. Temp)
        solution :
            name of solution : sweep (Default value = None)
        variations_dict :
            list of all variations variables with values
        filename :
            output full path filename (Default value = None)
        gridtype :
            type of grid to export. Default Cartesian
        grid_center :
            Center of the grid. Disabled for Cartesian (Default value = [0)
        grid_start :
            Start of the grid. Float list of 3 elements (Default value = [0)
        grid_stop :
            Stop of the grid. Float list of 3 elements (Default value = [0)
        grid_step :
            Step of the grid. Float list of 3 elements (Default value = [0)
        intrinsics :
            str mandatory for Frequency domain field calculation (Default value = None)
        phase :
            str field phase (Default value = None)
        variation_dict :
             (Default value = None)
        0 :
            
        0] :
            
        isvector :
             (Default value = False)

        Returns
        -------
        type
            True (fld exported) | False

        """
        self.messenger.add_info_message("Exporting {} Field. Be Patient".format(quantity_name))
        if not solution:
            solution = self._parent.existing_analysis_sweeps[0]
        if not filename:
            appendix = ""
            ext = ".fld"
            filename = os.path.join(self._parent.project_path, solution.replace(" : ", "_") + appendix + ext)
        else:
            filename = filename.replace("//", "/").replace("\\", "/")
        self.ofieldsreporter.CalcStack("clear")
        if isvector:
            self.ofieldsreporter.EnterQty(quantity_name)
            self.ofieldsreporter.CalcOp("Smooth")
            self.ofieldsreporter.EnterScalar(0)
            self.ofieldsreporter.CalcOp("AtPhase")
            self.ofieldsreporter.CalcOp("Mag")
        else:
            self.ofieldsreporter.EnterQty(quantity_name)
        obj_list = "AllObjects"
        self.ofieldsreporter.EnterVol(obj_list)
        self.ofieldsreporter.CalcOp("Mean")
        units=self.modeler.model_units
        ang_units="deg"
        if gridtype == "Cartesian":
            grid_center =["0mm", "0mm", "0mm"]
            grid_start_wu = [str(i)+units for i in grid_start]
            grid_stop_wu = [str(i)+units for i in grid_stop]
            grid_step_wu = [str(i)+units for i in grid_step]
        elif gridtype == "Cylinidrical":
            grid_center = [str(i)+units for i in grid_center]
            grid_start_wu = [str(grid_start[0])+units, str(grid_start[1])+ang_units, str(grid_start[2])+units]
            grid_stop_wu = [str(grid_stop[0])+units, str(grid_stop[1])+ang_units, str(grid_stop[2])+units]
            grid_step_wu = [str(grid_step[0])+units, str(grid_step[1])+ang_units, str(grid_step[2])+units]
        elif gridtype == "Spherical":
            grid_center = [str(i)+units for i in grid_center]
            grid_start_wu = [str(grid_start[0])+units, str(grid_start[1])+ang_units, str(grid_start[2])+ang_units]
            grid_stop_wu = [str(grid_stop[0])+units, str(grid_stop[1])+ang_units, str(grid_stop[2])+ang_units]
            grid_step_wu = [str(grid_step[0])+units, str(grid_step[1])+ang_units, str(grid_step[2])+ang_units]
        else:
            self._parent._messenger.add_error_message("Error in Type of Grid")
            return False
        if not variation_dict:
            variation_dict = self._parent.available_variations.nominal_w_values
        if intrinsics:
            if "Transient" in solution:
                variation_dict.append("Time:=")
                variation_dict.append(intrinsics)
            else:
                variation_dict.append("Freq:=")
                variation_dict.append(intrinsics)
                variation_dict.append("Phase:=")
                if phase:
                    variation_dict.append(phase)
                else:
                    variation_dict.append("0deg")


        self.ofieldsreporter.ExportOnGrid(filename, grid_start_wu,
                                          grid_stop_wu, grid_step_wu,
                                          solution,
                                          variation_dict, True, gridtype, grid_center, False)
        return os.path.exists(filename)


    @aedt_exception_handler
    def export_field_file(self, quantity_name, solution=None, variation_dict=None, filename=None,
                          obj_list="AllObjects", obj_type="Vol", intrinsics=None, phase=None, sample_points_file=None, sample_points_lists=None):
        """This function creates a new field file based on a specific solution and variation available. using Field Calculator

        Parameters
        ----------
        quantity_name :
            name of quantity to export (eg. Temp)
        solution :
            name of solution : sweep (Default value = None)
        variation_dict :
            list of all variations variables with values (Default value = None)
        filename :
            output full path filename (Default value = None)
        obj_list :
            list of objects to export. Default "AllObjects
        obj_type :
            type of objects to export. Default "Vol" (Volume). Can be "Surf"
        intrinsics :
            str mandatory for Frequency or Transient field calculation (Default value = None)
        phase :
            str field phase (Default value = None)
        sample_points_file :
             (Default value = None)
        sample_points_lists :
             (Default value = None)

        Returns
        -------
        type
            True (fld exported) | False

        """
        self.messenger.add_info_message("Exporting {} Field. Be Patient".format(quantity_name))
        if not solution:
            solution = self._parent.existing_analysis_sweeps[0]
        if not filename:
            appendix = ""
            ext = ".fld"
            filename = os.path.join(self._parent.project_path, solution.replace(" : ","_") + appendix + ext)
        else:
            filename = filename.replace("//", "/").replace("\\", "/")
        self.ofieldsreporter.CalcStack("clear")
        self.ofieldsreporter.EnterQty(quantity_name)


        if not variation_dict:
            if not sample_points_file and not sample_points_lists:
                if obj_type == "Vol":
                    self.ofieldsreporter.EnterVol(obj_list)
                elif obj_type == "Surf":
                    self.ofieldsreporter.EnterSurf(obj_list)
                else:
                    self.messenger.add_error_message("No correct choice")
                    return False
                self.ofieldsreporter.CalcOp("Value")
                variation_dict = self._parent.available_variations.nominal_w_values
            else:
                variations = self._parent.available_variations.nominal_w_values_dict
                variation_dict = []
                for el, value in variations.items():
                    variation_dict.append(el+":=")
                    variation_dict.append(value)
        if intrinsics:
            if "Transient" in solution:
                variation_dict.append("Time:=")
                variation_dict.append(intrinsics)
            else:
                variation_dict.append("Freq:=")
                variation_dict.append(intrinsics)
                variation_dict.append("Phase:=")
                if phase:
                    variation_dict.append(phase)
                else:
                    variation_dict.append("0deg")
        if not sample_points_file and not sample_points_lists:

            self.ofieldsreporter.CalculatorWrite(filename, ["Solution:="	, solution], variation_dict)
        elif sample_points_file:

            self.ofieldsreporter.ExportToFile(filename, sample_points_file, solution, variation_dict, True)
        else:
            sample_points_file = os.path.join(self._parent.project_path, "temp_points.pts")
            with open(sample_points_file, "w") as f:
                for point in sample_points_lists:
                    f.write(" ".join([str(i) for i in point])+"\n")
            self.ofieldsreporter.ExportToFile(filename, sample_points_file, solution, variation_dict, True)

        return os.path.exists(filename)


    @aedt_exception_handler
    def export_field_plot(self, plotname, filepath, filename=""):
        """

        Parameters
        ----------
        plotname :
            
        filepath :
            
        filename :
             (Default value = "")

        Returns
        -------

        """

        if not filename:
            filename = plotname
        self.ofieldsreporter.ExportFieldPlot(plotname, False, os.path.join(filepath, filename + ".aedtplt"))
        return os.path.join(filepath, filename+".aedtplt")

    @aedt_exception_handler
    def _create_fieldplot(self, objlist, quantityName, setup_name, intrinsincList, objtype, listtype):
        """Internal function

        Parameters
        ----------
        objlist :
            
        quantityName :
            
        setup_name :
            
        intrinsincList :
            
        objtype :
            
        listtype :
            

        Returns
        -------

        """
        if not setup_name:
            setup_name = self._parent.existing_analysis_sweeps[0]
        self.desktop.CloseAllWindows()
        self.oproject.SetActiveDesign(self.odesign.GetName())
        self.oeditor.FitAll()
        char_set = string.ascii_uppercase + string.digits
        uName = quantityName + '_' + ''.join(random.sample(char_set, 6))
        plot = FieldPlot(self.ofieldsreporter, objlist, setup_name, quantityName, intrinsincList)
        plot.name = uName
        plot.objtype = objtype
        plot.listtype = listtype
        plt = plot.create()
        if plt:
            self.FieldsPlot[uName] = plot
            return plot
        else:
            return False

    @aedt_exception_handler
    def create_fieldplot_surface(self, objlist, quantityName, setup_name=None, intrinsincDict={}):
        """

        Parameters
        ----------
        objlist :
            list of surfaces to be included in the plot
        quantityName :
            Quantity to be plotted
        setup_name :
            Name of the setup in the format "setupName : sweepName" (Default value = None)
        intrinsincDict :
            Dictionary containing all intrinsic  variables (Default value = {})

        Returns
        -------
        type
            plot object

        """
        plot = self._create_fieldplot(objlist, quantityName, setup_name, intrinsincDict, "Surface", "FacesList")
        return plot

    @aedt_exception_handler
    def create_fieldplot_cutplane(self, objlist, quantityName, setup_name=None, intrinsincDict={}):
        """

        Parameters
        ----------
        objlist :
            list of cut planes to be included in the plot
        quantityName :
            Quantity to be plotted
        setup_name :
            Name of the setup in the format "setupName : sweepName". If none, nominal, lastadaptive will be Applied (Default value = None)
        intrinsincDict :
            Dictionary containing all intrinsic  variables (Default value = {})

        Returns
        -------
        type
            plot object

        """
        plot = self._create_fieldplot(objlist, quantityName, setup_name, intrinsincDict, "Surface", "CutPlane")
        return plot

    @aedt_exception_handler
    def create_fieldplot_volume(self, objlist, quantityName, setup_name=None, intrinsincDict={}):
        """

        Parameters
        ----------
        objlist :
            list of objects to be included in the plot
        quantityName :
            Quantity to be plotted
        setup_name :
            Name of the setup in the format "setupName : sweepName". If none, nominal, lastadaptive will be Applied (Default value = None)
        intrinsincDict :
            Dictionary containing all intrinsic  variables (Default value = {})

        Returns
        -------
        type
            plot object

        """
        plot = self._create_fieldplot(objlist, quantityName, setup_name, intrinsincDict, "Volume", "ObjList")
        return plot

    @aedt_exception_handler
    def createRelativeCoordinateSystemForExport(self, coordinateSystem, origin=None, view=None):
        """

        Parameters
        ----------
        coordinateSystem :
            input coordinate system object
        origin :
            origin of the coordinate system (Default value = None)
        view :
            view type ("iso", "XY", "XZ", "YZ") (Default value = None)

        Returns
        -------
        type
            True

        """
        coordinateSystem.create(origin=origin, view=view)
        coordinateSystem.setWorkingCoordinateSystem()
        return True

    @aedt_exception_handler
    def export_field_jpg(self, fileName, plotName, coordinateSystemName):
        """Given a specific plotname and coordinate system name it export the plot to jpg

        Parameters
        ----------
        fileName :
            full path file name
        plotName :
            plot name
        coordinateSystemName :
            coordinate system name

        Returns
        -------
        type
            True

        """
        time.sleep(2)

        self.ofieldsreporter.ExportPlotImageToFile(fileName, "", plotName, coordinateSystemName)
        return True


    @aedt_exception_handler
    def export_field_image_with_View(self, plotName, exportFilePath, view="iso", wireframe=True):
        """NOTE: on AEDT 2019.3 it works only on ISO view due to a bug in API. It woks fine from 2020R1

        Parameters
        ----------
        plotName :
            name of the plot to be exported
        exportFilePath :
            file path
        view :
            string "iso", "XZ", "XY", "YZ" (Default value = "iso")
        wireframe :
            Boolean if objects has to be put in wireframe mode (Default value = True)

        Returns
        -------
        type
            True

        """
        coordinateSystemForExportPlot = CoordinateSystem(self.modeler)
        bound = self.modeler.get_model_bounding_box()
        center = [(float(bound[0]) + float(bound[3])) / 2,
                  (float(bound[1]) + float(bound[4])) / 2,
                  (float(bound[2]) + float(bound[5])) / 2]
        self.createRelativeCoordinateSystemForExport(coordinateSystemForExportPlot, center, view)
        wireframes = []
        if wireframe:
            names = self._primitives.get_all_objects_names()
            for el in names:
                if not self._primitives[el].wireframe:
                    wireframes.append(el)
                    self._primitives[el].display_wireframe(True)
        status = self.export_field_jpg(exportFilePath, plotName, coordinateSystemForExportPlot.name)
        for solid in wireframes:
            self._primitives[solid].display_wireframe(False)
        coordinateSystemForExportPlot.delete()
        return status

    @aedt_exception_handler
    def delete_field_plot(self, name):
        """Delete Field Plots

        Parameters
        ----------
        name :
            Field Plot to delete

        Returns
        -------

        """
        self.oreportsetup.DeleteFieldPlot([name])
        self.FieldsPlot.pop(name, None)
        return True

    @aedt_exception_handler
    def export_convergence_to_jpg(self, output_dir, name, Xaxis, outputlist, setupname="Setup1 : LastAdaptive"):
        """function that export JPG of Convergence Plot

        Parameters
        ----------
        output_dir :
            Output dir
        name :
            Project Name
        Xaxis :
            Independent Variable
        outputlist :
            List of Parameter to export
        setupname :
            Name of Setupt (Default value = "Setup1 : LastAdaptive")

        Returns
        -------
        type
            Boolean success of command

        """

        # Setup arguments list for createReport function
        args = ["Pass:=", ["All"], Xaxis + ":=", ["All"]]
        args2 = ["X Component:=", "Pass", "Y Component:=", outputlist]

        # Add folder for outputs

        if not os.path.exists(output_dir + "//" + name + "//Results"):
            os.mkdir(output_dir + "//" + name + "//Results")
        if not os.path.exists(output_dir + "//" + name + "//Pictures"):
            os.mkdir(output_dir + "//" + name + "//Pictures")
        self.oreportsetup.CreateReport("Solution Convergence Plot 1", "Eigenmode Parameters", "Rectangular Plot",
                                       setupname, [], args, args2, [])

        self.oreportsetup.ExportImageToFile("Solution Convergence Plot 1",
                                            output_dir + "//" + name + "//Pictures//" + name + "_Convergence.jpg",
                                            0,
                                            0)
        return True

    @aedt_exception_handler
    def export_convergence_to_csv(self, output_dir, name, Xaxis, outputlist, setupname="Setup1 : LastAdaptive"):
        """function that export CSV of Convergence Plot

        Parameters
        ----------
        output_dir :
            Output dir
        name :
            Project Name
        Xaxis :
            independent Variable
        outputlist :
            List of Parameter to export
        setupname :
            Name of Setupt (Default value = "Setup1 : LastAdaptive")

        Returns
        -------
        type
            Boolean success of command

        """

        # Setup arguments list for createReport function
        args = ["Pass:=", ["All"], Xaxis + ":=", ["All"]]
        args2 = ["X Component:=", "Pass", "Y Component:=", outputlist]

        # Add folder for outputs

        if not os.path.exists(output_dir + "//" + name + "//Results"):
            os.mkdir(output_dir + "//" + name + "//Results")
        if not os.path.exists(output_dir + "//" + name + "//Pictures"):
            os.mkdir(output_dir + "//" + name + "//Pictures")
        self.oreportsetup.CreateReport("Solution Convergence Plot 1", "Eigenmode Parameters", "Rectangular Plot",
                                       setupname, [], args, args2, [])

        self.oreportsetup.ExportToFile("Solution Convergence Plot 1",
                                       output_dir + "//" + name + "//Results//" + name + "_Convergence.csv")

        return True

    @aedt_exception_handler
    def export_eigen_plot(self, projectdir, name, Xaxis, outputlist, setupname="Setup1 :  LastAdaptive"):
        """TO BE REFACTORED
        function that export CSV of eigenmode Plot
        dir: Output dir
        name: project name
        Xaxis=
        outputlist= output quantity, in this case, egienmode
        :return:

        Parameters
        ----------
        projectdir :
            
        name :
            
        Xaxis :
            
        outputlist :
            
        setupname :
             (Default value = "Setup1 :  LastAdaptive")

        Returns
        -------

        """

        # Setup arguments list for createReport function
        args = [Xaxis + ":=", ["All"]]

        args2 = ["X Component:=", Xaxis, "Y Component:=", outputlist]

        # Add folder for outputs
        if not os.path.exists(projectdir + "//" + name + "//Results"):
            os.mkdir(projectdir + "//" + name + "//Results")
        if not os.path.exists(projectdir + "//" + name + "//Pictures"):
            os.mkdir(projectdir + "//" + name + "//Pictures")
        self.oreportsetup.CreateReport("Eigen Modes Plot 1", "Eigenmode Parameters", "Rectangular Plot",
                                       setupname, [], args, args2, [])

        self.oreportsetup.ExportImageToFile("Eigen Modes Plot 1",
                                            projectdir + "//" + name + "//Pictures//" + name + "Eigen.jpg", 0,
                                            0)

        self.oreportsetup.ExportToFile("Eigen Modes Plot 1",
                                       projectdir + "//" + name + "//Results//" + name + ".csv")
        return True

    @aedt_exception_handler
    def export_mechanical_script(self, workingDir, name, aMats, aInside, aSurf, emissivity, convection, gravity,
                                 ambienttemp="22", MechNumCores=2, discretesweep=False, WBSuppressSolids=None):
        """export_mechanical_script Function write a PY function for Mechanical API.
        It start from createMech.py file and integrates it with variables and lanuchers.
        
        - Added WBSuppressSolids option:
            1. the objects names specified in the list are suppessed in Workbench
            2. the list defaults to empty list

        Parameters
        ----------
        workingDir :
            
        name :
            
        aMats :
            
        aInside :
            
        aSurf :
            
        emissivity :
            
        convection :
            
        gravity :
            
        ambienttemp :
             (Default value = "22")
        MechNumCores :
             (Default value = 2)
        discretesweep :
             (Default value = False)
        WBSuppressSolids :
             (Default value = None)

        Returns
        -------

        """

        # USE this
        # MechNumCores=oFilterProp.getKey("HFSSNumCores")

        if WBSuppressSolids is None:
            WBSuppressSolids = []
        Filename = os.path.join(workingDir, '{0}.py'.format(name + "New"))
        Filename = Filename.replace('\\', '/')
        myfullpath = os.path.realpath(__file__).replace("\\", "/").replace("//", "/")
        full_split = myfullpath.split("/")
        mypath = full_split[0] + "/" + full_split[1]

        i = 2
        while i < len(full_split) - 2:
            mypath = os.path.join(mypath, full_split[i])
            i += 1
        mypath = os.path.join(mypath, "WBLib", 'createMechandTherm.py')
        shutil.copy2(mypath, Filename)
        with open(Filename, 'a+') as f:
            f.write('\nDesktopMat = { \n')
            iMat = 0
            for matName, tmpObjs in aMats.iteritems():
                iObj = 0
                for objName in tmpObjs:
                    f.write('"{0}" : "{1}"'.format(objName, matName))
                    iObj += 1
                    if iObj < len(tmpObjs):
                        f.write(',\n')
                iMat += 1
                if iMat < len(aMats):
                    f.write(',\n')
            f.write('}\n')
            f.write('AmbientTemp=\"' + str(ambienttemp) + '\"')
            f.write('\nDesktopSolveInside = { \n')
            iObjI = 0
            for objName in aInside:
                f.write('"{0}" : 1'.format(objName))
                iObjI += 1
                if iObjI < len(aInside):
                    f.write(',\n')
            f.write('}\n')
            f.write('\nDesktopSolveSurface = { \n')
            iObjS = 0
            for objName in aSurf:
                f.write('"{0}" : 1'.format(objName))
                iObjS += 1
                if iObjS < len(aSurf):
                    f.write(',\n')
            f.write('}\n')
            # create the list WBSuppressSolids in the script file
            f.write('WBSuppressSolids = %s \n' % str(WBSuppressSolids))
            # calls the createMech class
            f.write('a=createMech()\n')
            # calls the a.assignGeometry method
            f.write('f=a.assignGeometry(DesktopMat,DesktopSolveSurface,DesktopSolveInside,WBSuppressSolids)\n')
            f.write("emissivity={}\n")
            for emi in emissivity:
                f.write("emissivity[\"SYS\\\\" + emi + "\"]=" + emissivity[emi] + "\n")
                f.write("emissivity[\"" + emi + "\"]=" + emissivity[emi] + "\n")
            f.write("convection={}\n")
            for c in convection:
                f.write("convection[" + c + "]=" + convection[c] + "\n")
            f.write('f=a.createThermalBoundaries(convection,emissivity,AmbientTemp)\n')
            # f.write('f=a.importLoads()\n')
            # f.write('f=a.createFrictionless(' + str(gravity) + ')\n')
            # f.write("f=a.createStructuralSetup(True," + str(MechNumCores) + "," + sWorkbenchVersion[-3:] + ")" + "\n")
            # f.write('f=a.setupSweep(' + str(discretesweep) + ')\n')
        return True

    @aedt_exception_handler
    def export_model_picture(self, dir, name, picturename="Model", ShowAxis=True, ShowGrid=True, ShowRuler=True):
        """Synopsis:
        function that export Model Snapshot. It works only in Graphical Mode
        Arguments:

        Parameters
        ----------
        dir :
            Output dir"
        name :
            project name" (use to compose the path)
        picturename :
            image name" (default="Model"; extension ".jpg" is automatically added)
        ShowAxis :
            True (default) | False
        ShowGrid :
            True (default) | False
        ShowRuler :
            True (default) | False

        Returns
        -------
        type
            True (executed) | False

        """

        # Setup arguments list for createReport function
        if not os.path.exists(dir + "//" + name + "//Pictures"):
            os.mkdir(dir + "//" + name + "//Pictures")

        # open the 3D modeler and remove the selection on other objects
        self.oeditor.ShowWindow()
        self.steal_focus_oneditor()
        self.oeditor.FitAll()
        # export the image
        arg = ["NAME:SaveImageParams", "ShowAxis:=", ShowAxis, "ShowGrid:=", ShowGrid, "ShowRuler:=", ShowRuler,
               "ShowRegion:=", "Default", "Selections:=", ""]
        self.oeditor.ExportModelImageToFile(dir + "//" + name + "//Pictures//" + picturename + ".jpg", 0, 0,
                                             arg)
        return True

    @aedt_exception_handler
    def copy_report_data(self, PlotName):
        """Copy Report Data as static data in the report

        Parameters
        ----------
        PlotName :
            Name of the Report

        Returns
        -------
        type
            True (executed)

        """
        # Copy the plot curves as data
        self.oreportsetup.CopyReportsData([PlotName])
        self.oreportsetup.PasteReports()
        return True

    @aedt_exception_handler
    def create_field_exptression(self,expression_name, Quantity, obj_name, obj_type="Volume"):
        """It create a new expression using Field Calculator given specified input

        Parameters
        ----------
        expression_name :
            Name of the output expression
        Quantity :
            Field Quantity to use in expression (eg. E)
        obj_name :
            name of objects on which compute the expression
        obj_type :
            Type of objects: Volume, Surface, Line, Point (Default value = "Volume")

        Returns
        -------
        type
            True if succeeedd

        """

        self.ofieldsreporter.EnterQty(Quantity)
        if obj_type.lower=="volume":
            self.ofieldsreporter.EnterVol(obj_name)
        elif obj_type.lower=="surface":
            self.ofieldsreporter.EnterSurf(obj_name)
        elif obj_type.lower=="point":
            self.ofieldsreporter.EnterPoint(obj_name)
        elif obj_type.lower=="line":
            self.ofieldsreporter.EnterLine(obj_name)
        else:
            return False
        self.ofieldsreporter.CalcOp("Value")
        self.ofieldsreporter.AddNamedExpression(expression_name, "Fields")
        return True

    @aedt_exception_handler
    def delete_report(self, PlotName):
        """Delete Report Data

        Parameters
        ----------
        PlotName :
            Name of the Report

        Returns
        -------
        type
            True (executed) | False

        """

        self.oreportsetup.DeleteReports([PlotName])
        return True

    @aedt_exception_handler
    def rename_report(self, PlotName, newname):
        """Delete Report Data

        Parameters
        ----------
        PlotName :
            Name of the Report
        newname :
            

        Returns
        -------
        type
            True (executed)

        """

        self.oreportsetup.RenameReport(PlotName, newname)
        return True


    @aedt_exception_handler
    def export_report_to_csv(self, ProjectDir, PlotName):
        """Export SParameter  as CSV
        It leaves the data in the plot (as DATA) as reference for the Sparameters plot after the loops

        Parameters
        ----------
        ProjectDir :
            Project Dir (str)
        PlotName :
            name of the plot to export

        Returns
        -------
        type
            True (executed)

        """
        # path
        npath = os.path.normpath(ProjectDir)
        # set name for the csv file

        csvFileName = os.path.join(npath, PlotName+".csv")
        # export the csv
        self.oreportsetup.ExportToFile(PlotName, csvFileName)
        return True

    @aedt_exception_handler
    def export_report_to_jpg(self, ProjectDir, PlotName):
        """Export SParameter as image

        Parameters
        ----------
        ProjectDir :
            Project Dir
        PlotName :
            

        Returns
        -------

        """
        # path
        npath = os.path.normpath(ProjectDir)
        # set name for the plot image file
        jpgFileName = os.path.join(npath, PlotName+".jpg")

        self.oreportsetup.ExportImageToFile(PlotName, jpgFileName, 0, 0)
        return True

    @aedt_exception_handler
    def get_far_field_data(self, expression="GainTotal", setup_sweep_name='', domain="Infinite Sphere1", families_dict=None):
        """Generate Far Field Data using GetSolutionDataPerVariation function. it returns the Data, solData, ThetaVals, PhiVals, ScanPhiVals, ScanThetaVals, FreqVals

        Parameters
        ----------
        setup_sweep_name :
            Name of setup to compute report. if None, nominal sweep will be applied (Default value = '')
        domain :
            Context Type (Sweep or Time) (Default value = "Infinite Sphere1")
        families_dict :
            Dictionary of variables and values. Default {"Freq": ["All"]}
        expression :
            string or list of traces to include (Default value = "GainTotal")

        Returns
        -------
        type
            SolutionData object if successful

        """
        if type(expression) is not list:
            expression = [expression]
        if not setup_sweep_name:
            setup_sweep_name = self._parent.nominal_adaptive
        if families_dict is None:
            families_dict = {"Theta": ["All"], "Phi": ["All"], "Freq": ["All"]}
        solution_data = self.get_solution_data_per_variation("Far Fields", setup_sweep_name, ['Context:=', domain], families_dict, expression)
        if not solution_data:
            print("No Data Available. Check inputs")
            return False
        return solution_data

    @aedt_exception_handler
    def get_report_data(self, expression="dB(S(1,1))", setup_sweep_name='', domain='Sweep', families_dict=None):
        """Generate Report Data using GetSolutionDataPerVariation function. it returns the data object, the solDataArray
        and the FreqVals Array.
        
        
        :Example:
            hfss Sparameters
            hfss = HFSS()
            hfss.post.get_report_data("S(1,1)")   # it will take default sweep and default variation
        
        
            m3d = Maxwell3D()
            m3d.post.get_report_data("SurfaceLoss")   #Eddy Current examples
            m3d.post.get_report_data("Wind(LoadA,LaodA)")    #TransientAnalsysis

        Parameters
        ----------
        setup_sweep_name :
            Name of setup to compute report. if None, nominal sweep will be applied (Default value = '')
        domain :
            Context Type (Sweep or Time) (Default value = 'Sweep')
        families_dict :
            Dictionary of variables and values. Default {"Freq": ["All"]}
        expression :
            string or list of traces to include (Default value = "dB(S(1)
        1))" :
            

        Returns
        -------
        type
            SolutionData object if successful

        """
        if self.post_solution_type == "3DLayout" or self.post_solution_type == "NexximLNA" or self.post_solution_type == "NexximTransient":
            if domain == "Sweep":
                did = 3
            else:
                did = 1
            ctxt = ["NAME:Context", "SimValueContext:=",
                    [did, 0, 2, 0, False, False, -1, 1, 0, 1, 1, "", 0, 0, "IDIID", False, "1"]]
        else:
            ctxt = ["Domain:=", domain]

        if type(expression) is not list:
            expression = [expression]
        if not setup_sweep_name:
            setup_sweep_name = self._parent.nominal_sweep
        if self.post_solution_type not in report_type:
            print("Solution not supported")
            return False
        modal_data = report_type[self.post_solution_type]

        if families_dict is None:
            families_dict = {"Freq": ["All"]}

        solution_data = self.get_solution_data_per_variation(modal_data, setup_sweep_name, ctxt, families_dict, expression)
        if not solution_data:
            print("No Data Available. Check inputs")
            return False
        return solution_data

    @aedt_exception_handler
    def create_rectangular_plot(self, expression="dB(S(1,1))", setup_sweep_name='', families_dict={"Freq": ["All"]},
                                primary_sweep_variable="Freq", context=None, plotname=None):
        """Create a 2D Rectangular plot in AEDT

        Parameters
        ----------
        expression :
            Expression Value or Expressions list (Default value = "dB(S(1)
        setup_sweep_name :
            setup name with sweep (Default value = '')
        families_dict :
            dictionary of all families including Primary Sweep (Default value = {"Freq": ["All"]})
        primary_sweep_variable :
            primary sweep name (Default value = "Freq")
        context :
            str if present (Default value = None)
        plotname :
            str optional (Default value = None)
        1))" :
            

        Returns
        -------
        type
            bool

        """
        ctxt=[]
        if not setup_sweep_name:
            setup_sweep_name = self._parent.nominal_sweep
        if self.post_solution_type == "3DLayout" or self.post_solution_type == "NexximLNA" or self.post_solution_type == "NexximTransient":
            if "Sweep" in setup_sweep_name:
                did = 3
            else:
                did = 1
            ctxt = ["NAME:Context", "SimValueContext:=",
                    [did, 0, 2, 0, False, False, -1, 1, 0, 1, 1, "", 0, 0, "IDIID", False, "1"]]
        elif context:
            if type(context) is  list:
                ctxt = context
            else:
                ctxt = ["Context:=", context]

        if type(expression) is not list:
            expression = [expression]
        if not setup_sweep_name:
            setup_sweep_name = self._parent.nominal_sweep
        if self.post_solution_type not in report_type:
            print("Solution not supported")
            return False
        modal_data = report_type[self.post_solution_type]
        if not plotname:
            plotname = generate_unique_name("Plot")
        families_input = []
        for el in families_dict:
            families_input.append(el+":=")
            families_input.append(families_dict[el])
        self.oreportsetup.CreateReport(plotname, modal_data, "Rectangular Plot", setup_sweep_name, ctxt, families_input,
                                                       ["X Component:=", primary_sweep_variable, "Y Component:=",
                                                   expression])

        return True

    @aedt_exception_handler
    def get_solution_data_per_variation(self, soltype='Far Fields', setup_sweep_name='', ctxt=None,
                                        sweeps=None, expression=''):
        """

        Parameters
        ----------
        soltype :
            string: Solution Type. eg. "Far Fields" "Modal Solution Data"... (Default value = 'Far Fields')
        setup_sweep_name :
            Name of setup to compute report. if None, nominal adaptive will be applied (Default value = '')
        ctxt :
            List of Context variable (Default value = None)
        sweeps :
            Dictionary of variables and values. Default {'Theta': 'All', 'Phi': 'All', 'Freq': 'All'}
        expression :
            string or list of traces to include (Default value = '')

        Returns
        -------
        type
            solution data

        """
        if sweeps is None:
            sweeps = {'Theta': 'All', 'Phi': 'All', 'Freq': 'All'}
        if not ctxt:
            ctxt = []
        if type(expression) is not list:
            expression = [expression]
        if not setup_sweep_name:
            setup_sweep_name = self._parent.nominal_adaptive
        sweep_list=[]
        for el in sweeps:
            sweep_list.append(el+":=")
            if type(sweeps[el]) is list:
                sweep_list.append(sweeps[el])
            else:
                sweep_list.append([sweeps[el]])



        data = self.oreportsetup.GetSolutionDataPerVariation(soltype, setup_sweep_name, ctxt, sweep_list, expression)
        return SolutionData(data)

    @aedt_exception_handler
    def steal_focus_oneditor(self):
        """It can be used to remove the selection to an object
        that would prevent the correct image export

        Parameters
        ----------

        Returns
        -------

        """
        self.desktop.RestoreWindow()
        param = ["NAME:SphereParameters", "XCenter:=", "0mm", "YCenter:=", "0mm", "ZCenter:=", "0mm", "Radius:=", "1mm"]
        attr = ["NAME:Attributes", "Name:=", "DUMMYSPHERE1", "Flags:=", "NonModel#"]
        self.oeditor.CreateSphere(param, attr)
        self.oeditor.Delete(["NAME:Selections", "Selections:=", "DUMMYSPHERE1"])
        return True
