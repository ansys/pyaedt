"""
Analysis Classes
----------------

Description
===========

This module contains all the Common classes of PyAEDT, including file
management, messaging, and all the calls to AEDT modules like modeler,
mesh, postprocessing, setup.


"""
from __future__ import absolute_import
import os
import itertools
import threading
import shutil
from ..modeler.modeler_constants import CoordinateSystemPlane, CoordinateSystemAxis, GravityDirection, Plane
from ..modules.SolveSetup import Setup
from ..modules.SolutionType import SolutionType, SetupTypes
from ..modules.SetupTemplates import SetupKeys
from ..modules.DesignXPloration import DOESetups, DXSetups, ParametericsSetups, SensitivitySetups, StatisticalSetups, OptimizationSetups
from .Design import Design
from ..modules.MaterialLib import Materials
from ..generic.general_methods import aedt_exception_handler
from ..desktop import _pythonver
import sys
if "IronPython" in sys.version or ".NETFramework" in sys.version:
    from ..modules.PostProcessor import PostProcessor
else:
    from ..modules.AdvancedPostProcessing import PostProcessor


class Analysis(Design, object):
    """**Class Analysis**
    
    Main lower level Analysis Class.
    Container of all Common Functions.
    
    It is automatically initialized by Application call (like HFSS, Q3D...). Refer to Application function for inputs definition

    Parameters
    ----------

    Returns
    -------

    """

    def __init__(self, application, projectname, designname, solution_type, setup_name):
        self.setups = []
        Design.__init__(self, application, projectname, designname, solution_type)
        self.messenger.add_info_message("Design Loaded")
        self._setup = None
        if setup_name:
            self.analysis_setup = setup_name
        self.solution_type = solution_type
        self._materials = Materials(self)
        self.messenger.add_info_message("Materials Loaded")
        self._post = PostProcessor(self)
        self._available_variations = self.AvailableVariations(self)
        self.setups = [self.get_setup(setup_name) for setup_name in self.setup_names]
        self.opti_parametric = ParametericsSetups(self)
        self.opti_optimization = OptimizationSetups(self)
        self.opti_doe = DOESetups(self)
        self.opti_designxplorer = DXSetups(self)
        self.opti_sensitivity = SensitivitySetups(self)
        self.opti_statistical = StatisticalSetups(self)


    @property
    def materials(self):
        """Property
        
        :return: Material Manager that is used to manage materials in the project

        Parameters
        ----------

        Returns
        -------

        """
        return self._materials

    @property
    def Position(self):
        """Position Object
        
        :return: Position object

        Parameters
        ----------

        Returns
        -------

        """
        return self.modeler.Position


    @property
    def available_variations(self):
        """Available Variation Object
        
        :return: Available Variation Object

        Parameters
        ----------

        Returns
        -------

        """

        return self._available_variations

    @property
    def CoordinateSystemAxis(self):
        """CoordinateSystemAxis Constant
        
        :return: Coordinate System Axis Constants Tuple (.X, .Y, .Z)

        Parameters
        ----------

        Returns
        -------

        """
        return CoordinateSystemAxis()

    @property
    def CoordinateSystemPlane(self):
        """CoordinateSystemPlane Constants
        
        :return: Coordinate System Plane Constants Tuple(.XY, .YZ, .XZ)

        Parameters
        ----------

        Returns
        -------

        """
        return CoordinateSystemPlane()

    @property
    def View(self):
        """Planes To check if redundant to CoordinateSystemPlane
        
        
        :return: Coordinate System Plane String Tuple("XY", "YZ", "XZ")

        Parameters
        ----------

        Returns
        -------

        """
        return Plane()

    @property
    def GravityDirection(self):
        """To check if redundant
        
        :return: Gravity Direction Tuple (XNeg, YNeg, ZNeg, XPos, YPos, ZPos)

        Parameters
        ----------

        Returns
        -------

        """
        return GravityDirection()

    @property
    def modeler(self):
        """:return: modeler object"""
        return self._modeler

    @property
    def mesh(self):
        """Mesh Object
        
        :return: mesh object

        Parameters
        ----------

        Returns
        -------

        """
        return self._mesh

    @property
    def post(self):
        """Post Processor Object
        
        :return: post processor object

        Parameters
        ----------

        Returns
        -------

        """
        return self._post

    @property
    def osolution(self):
        """osolution Object
        
        :return: Solutions Module object

        Parameters
        ----------

        Returns
        -------

        """
        return self.odesign.GetModule("Solutions")

    @property
    def oanalysis(self):
        """ """
        return self.odesign.GetModule("AnalysisSetup")

    @property
    def analysis_setup(self):
        """Analysis Setup
        
        
        :return: Active or first Analysis Setup Name

        Parameters
        ----------

        Returns
        -------

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
        """

        Parameters
        ----------
        setup_name :
            

        Returns
        -------

        """
        setup_list = self.existing_analysis_setups
        if setup_list:
            assert setup_name in setup_list, "Invalid setup name {}".format(setup_name)
            self._setup = setup_name
        else:
            self._setup = setup_list[0]
        #return self._setup

    @property
    def existing_analysis_sweeps(self):
        """Existing Analysis Setup List
        
        
        :return: Return a list of all defined analysis setup names in the maxwell design.

        Parameters
        ----------

        Returns
        -------

        """
        setup_list = self.existing_analysis_setups
        sweep_list=[]
        for el in setup_list:
            if self.solution_type in SetupKeys.defaultAdaptive.keys():
                setuptype = SetupKeys.defaultAdaptive[self.solution_type]
                if setuptype:
                    sweep_list.append(el + " : " + setuptype)
            try:
                sweeps = list(self.oanalysis.GetSweeps(el))
            except:
                sweeps = []
            for sw in sweeps:
                sweep_list.append(el + " : " + sw)
        return sweep_list

    @property
    def nominal_adaptive(self):
        """

        Parameters
        ----------

        Returns
        -------
        type
            :return: str nominal adaptive setup

        """
        if len(self.existing_analysis_sweeps)>0:
            return self.existing_analysis_sweeps[0]
        else:
            return ""

    @property
    def nominal_sweep(self):
        """Return nominal sweep

        Returns
        -------
        str
            sweep is available it will return the lastadaptive
            
            :return: str nominal setup sweep if present
        """

        if len(self.existing_analysis_sweeps)>1:
            return self.existing_analysis_sweeps[1]
        else:
            return self.nominal_adaptive

    @property
    def existing_analysis_setups(self):
        """Existing Analysis Setup List
        
        
        :return: Return a list of all defined analysis setup names in the maxwell design.

        Parameters
        ----------

        Returns
        -------

        """
        setups = list(self.oanalysis.GetSetups())
        return setups

    @property
    def output_variables(self):
        """OutputVariable Object
        
        
        :return: Solutions OutputVariable object

        Parameters
        ----------

        Returns
        -------

        """
        oModule = self.odesign.GetModule("OutputVariable")
        return oModule.GetOutputVariables()

    @property
    def setup_names(self):
        """Setup Lists
        
        
        :return:  list of all defined analysis setup names in the design

        Parameters
        ----------

        Returns
        -------

        """
        setups = self.oanalysis.GetSetups()
        return setups


    @property
    def ooptimetrics(self):
        """Optimetrics Object
        
        :return: Solutions Optimetrics object

        Parameters
        ----------

        Returns
        -------

        """
        return self.odesign.GetModule("Optimetrics")

    @property
    def ooutput_variable(self):
        """OutputVariable Object
        
        :return: Solutions OutputVariable object

        Parameters
        ----------

        Returns
        -------

        """
        return self.odesign.GetModule("OutputVariable")

    @property
    def SimulationSetupTypes(self):
        """:return:List of all Simulation Setup Types categorized by Application"""
        return SetupTypes()


    @property
    def SolutionTypes(self):
        """:return:List of all Solution type categorized by Application"""
        return SolutionType()


    class AvailableVariations(object):

        def __init__(self, parent):
            """class Containing Available Variations

            Parameters
            ----------
            parent :
                parent object

            Returns
            -------

            """
            self._parent = parent

        @property
        def variables(self):
            """:return:List of independent variables"""
            return [i for i in self._parent.variable_manager.independent_variables]

        @aedt_exception_handler
        def variations(self, setup_sweep=None):
            """

            Parameters
            ----------
            setup_sweep :
                Setup and Sweep on which search variations (Default value = None)

            Returns
            -------
            type
                variation families list

            """
            if not setup_sweep:
                setup_sweep = self._parent.existing_analysis_sweeps[0]
            vs = self._parent.osolution.GetAvailableVariations(setup_sweep)
            families=[]
            for v in vs:
                variations = v.split(" ")
                family=[]
                for el in self.variables:
                    family.append(el + ":=")
                    i=0
                    while i<len(variations):
                        if variations[i][0:len(el)] == el:
                            family.append([variations[i][len(el)+2:-1]])
                        i += 1
                families.append(family)
            return families

        @property
        def nominal(self):
            """ """
            families = []
            for el in self.variables:
                families.append(el+":=")
                families.append(["Nominal"])
            return families

        @property
        def nominal_w_values(self):
            """ """
            families = []
            variation = self._parent.odesign.GetNominalVariation()
            for el in self.variables:
                families.append(el+":=")
                families.append([self._parent.odesign.GetVariationVariableValue(variation, el)])
            return families

        @property
        def nominal_w_values_dict(self):
            """ """
            families = {}
            variation = self._parent.odesign.GetNominalVariation()
            for el in self.variables:
                families[el] = self._parent.odesign.GetVariationVariableValue(variation, el)
            return families

        @property
        def all(self):
            """ """
            families=[]
            for el in self.variables:
                families.append(el+":=")
                families.append(["All"])
            return families



    class AxisDir(object):
        """Data Class containing Axis directions constants"""
        (XNeg, YNeg, ZNeg, XPos, YPos, ZPos) = range(0, 6)

    @aedt_exception_handler
    def get_setups(self):
        """

        Parameters
        ----------

        Returns
        -------
        type
            :return: List of all Setup names

        """
        setups = self.oanalysis.GetSetups()
        return list(setups)

    @aedt_exception_handler
    def get_nominal_variation(self):
        """:return: nominal variation"""
        return self.available_variations.nominal

    @aedt_exception_handler
    def get_sweeps(self, name):
        """

        Parameters
        ----------
        name :
            

        Returns
        -------
        type
            :return: list of all available sweep names of specific setup

        """
        sweeps=[]

        sweeps = self.oanalysis.GetSweeps(name)

        return list(sweeps)

    @aedt_exception_handler
    def export_parametric_results(self, sweepname, filename, exportunits=True):
        """Given a specific sweep, it export the list of all available parametric variation solved to a file

        Parameters
        ----------
        sweepname : str
            optimetrics sweep name
        filename : str
            full path filename  (.csv)
        exportunits : bool
            True (export units with value) | False (export only value) (Default value = True)

        Returns
        -------
        type
            True (succeeded) | False (Failed)

        """

        self.ooptimetrics.ExportParametricResults(sweepname, filename, exportunits)
        return True


    @aedt_exception_handler
    def analyse_from_initial_mesh(self):
        """Revert solution to initial mesh and re-run it
        
        
        :return: True (succeeded) | False (Failed)

        Parameters
        ----------

        Returns
        -------

        """
        self.oanalysis.RevertSetupToInitial(self._setup)
        self.analyse_nominal()
        return True


    @aedt_exception_handler
    def analyse_nominal(self):
        """Revert solution to initial mesh and re-run it
        
        
        :return: True (succeeded) | False (Failed)

        Parameters
        ----------

        Returns
        -------

        """

        self.odesign.Analyze(self.analysis_setup)
        return True


    @aedt_exception_handler
    def generate_unique_setup_name(self, setup_name=None):
        """Generate a new, unique design name
        
        
        :return: setup_name

        Parameters
        ----------
        setup_name :
             (Default value = None)

        Returns
        -------

        """
        if not setup_name:
            setup_name = "Setup"
        index = 2
        while setup_name in self.existing_analysis_setups:
            setup_name = setup_name + "_{}".format(index)
            index += 1
        return setup_name

    @aedt_exception_handler
    def create_setup(self, setupname="MySetupAuto", setuptype=None, props={}):
        """Create a new Setup.

        Parameters
        ----------
        setupname :
            optional, name of the new setup (Default value = "MySetupAuto")
        setuptype :
            optional, setup type. if None, default type will be applied
        props :
            optional dictionary of properties with values (Default value = {})

        Returns
        -------
        :class: Setup
            setup object

        """
        if setuptype is None:
            if self.design_type == "Icepak" and self.solution_type=="Transient":
                setuptype = SetupKeys.defaultSetups["TransientTemperatureAndFlow"]
            else:
                setuptype = SetupKeys.defaultSetups[self.solution_type]
        name = self.generate_unique_setup_name(setupname)
        setup = Setup(self, setuptype, name)
        setup.create()
        if props:
            for el in props:
                setup.props[el] = props[el]
        setup.update()
        self.analysis_setup = name
        self.setups.append(setup)
        return setup

    @aedt_exception_handler
    def edit_setup(self, setupname, properties_dict):
        """Edit current Setup.

        Parameters
        ----------
        setupname : str
            name of the setup
        properties_dict : dict: dict
            dictionary containing the property to update with the value

        Returns
        -------
        type
            setup object

        """
        setuptype = SetupKeys.defaultSetups[self.solution_type]
        setup = Setup(self, setuptype, setupname, isnewsetup=False)
        setup.update(properties_dict)
        self.analysis_setup = setupname
        return setup


    @aedt_exception_handler
    def get_setup(self, setupname):
        """Get Setup from current design.

        Parameters
        ----------
        setupname : str
            name of the setup

        Returns
        -------
        :class: Setup
            setup object

        """

        setuptype = SetupKeys.defaultSetups[self.solution_type]
        setup = Setup(self, setuptype, setupname, isnewsetup=False)
        if setup.props:
            self.analysis_setup = setupname
        return setup

    @aedt_exception_handler
    def create_output_variable(self, variable, expression):
        """Create or modify the output variable

        Parameters
        ----------
        variable :
            name of the variable
        expression :
            value

        Returns
        -------
        type
            True  object

        """
        oModule = self.odesign.GetModule("OutputVariable")
        if variable in self.output_variables:
            oModule.EditOutputVariable(variable, expression, variable, self.existing_analysis_sweeps[0], self.solution_type, [])
        else:
            oModule.CreateOutputVariable(variable, expression, self.existing_analysis_sweeps[0], self.solution_type, [])
        return True

    @aedt_exception_handler
    def set_output_variable(self, variable, expression):
        """Set output variable value

        Parameters
        ----------
        variable :
            name of the variable
        expression :
            string expression of the value

        Returns
        -------
        type
            None

        """
        oModule = self.odesign.GetModule("OutputVariable")
        if variable in self.output_variables:
            oModule.EditOutputVariable(variable, expression, variable, self.existing_analysis_sweeps[0], self.solution_type, [])
        else:
            oModule.CreateOutputVariable(variable, expression, self.existing_analysis_sweeps[0], self.solution_type, [])
        return True

    @aedt_exception_handler
    def get_output_variable(self, variable, solution_name=None, report_type_name=None):
        """Get output variable value

        Parameters
        ----------
        variable :
            name of the variable
        solution_name :
            optional Solution Name (Default value = None)
        report_type_name :
            optional report type name (Default value = None)

        Returns
        -------
        type
            Value

        """
        oModule = self.odesign.GetModule("OutputVariable")
        assert variable in self.output_variables, "Output Variable {} does not exist".format(variable)
        nominal_variation = self.odesign.GetNominalVariation()
        sol_type = self.solution_type
        value = oModule.GetOutputVariableValue(variable, nominal_variation, self.existing_analysis_sweeps[0], self.solution_type, [])
        return value

    @aedt_exception_handler
    def get_object_material_properties(self, object_list=None, prop_names=None):
        """High  level function to return the conductivities of a list of specified objects as a dictionary.  Objects with no defined conductivity property will be ignored

        Parameters
        ----------
        object_list :
            list) objects for which get material_properties. if None, all objects will be considered (Default value = None)
        prop_names :
            str or list) property to be exported. If None, all properties will be exported. Objects with no defined property will be ignored (Default value = None)

        Returns
        -------
        type
            dictionary of object with material properties

        """

        if object_list:
            if not isinstance(object_list, list):
                object_list = [object_list]
        else:
            object_list = self.modeler.primitives.get_all_objects_names()

        if prop_names:
            if not isinstance(prop_names, list):
                prop_names = [prop_names]

        dict = {}
        for entry in object_list:
            mat_name = self.modeler.primitives[entry].material_name
            mat_props = self.materials.get_material_properties(mat_name)
            if prop_names is None:
                dict[entry] = mat_props
            else:
                for prop_name in prop_names:
                    dict[entry] = mat_props[prop_name]
        return dict


    @aedt_exception_handler
    def create_dx_component_with_goal(self, name, paramlist, inputlist, copy_mesh, inputfreq=None, deltasweep=None,
                            pointsnum=451):
        """

        Parameters
        ----------
        name :
            
        paramlist :
            
        inputlist :
            
        copy_mesh :
            
        inputfreq :
             (Default value = None)
        deltasweep :
             (Default value = None)
        pointsnum :
             (Default value = 451)

        Returns
        -------

        """
        #TODO make it more general
        """Create a DesignXplorer object

        :param name: name of the simulation + Type of Simulation. Example "dB(S(Port1,Port1))Adaptive" or " (dB(S(Port2,Port2)), -3 )Sweep"
        :param paramlist: list of output parameters
        :param copy_mesh: Copy equivalent mesh
        :param inputlist: list of input variables
        :param inputfreq: Frequency at which the parameter must be evaluated. None for Eigen mode analysis
        :param deltasweep: optional
        :param pointsnum: number of points
        :return: Nothing
        """

        self._messenger.add_info_message("Creating DesignXplorer Setup")
        setup1 = self.opti_designxplorer.add_dx_setup(inputlist)
        setup1.props["SaveFields"] = True

        vargs1 = ["NAME:DesignXplorerSetup1", "IsEnabled:=", True]
        varg2 = ["NAME:ProdOptiSetupDataV2", "SaveFields:=", True, "CopyMesh:=", copy_mesh, "SolveWithCopiedMeshOnly:=",
                 True]
        vargs1.append(varg2)
        varg2 = ["NAME:StartingPoint"]
        vargs1.append(varg2)
        vargs1.append("Sim. Setups:="), vargs1.append([name])
        if inputlist:
            varg2 = ["NAME:Sweeps"]
            for l in inputlist:
                if "$" in l:
                    varg3 = ["NAME:SweepDefinition", "Variable:=", l, "Data:=", self.oproject.GetVariableValue(l),
                             "OffsetF1:=", False, "Synchronize:=", 0]
                else:
                    varg3 = ["NAME:SweepDefinition", "Variable:=", l, "Data:=", self.odesign.GetVariableValue(l),
                             "OffsetF1:=", False, "Synchronize:=", 0]
                varg2.append(varg3)
        vargs1.append(varg2)
        vargs1.append(["NAME:Sweep Operations"])
        vargs1.append("CostFunctionName:="), vargs1.append("Cost")
        vargs1.append("CostFuncNormType:="), vargs1.append("L2")
        vargs1.append(["NAME:CostFunctionGoals"])
        vargs1.append("EmbeddedParamSetup:="), vargs1.append(-1)
        vargs2 = ["NAME:Goals"]
        for param in paramlist:
            vargs3 = ["NAME:Goal", "ReportType:="]
            if not inputfreq:
                vargs3.append("Eigenmode Parameters")
            else:
                vargs3.append("Modal Solution Data")
            vargs3.append("Solution:=")
            if "Adaptive" in param:
                vargs3.append(name + " : LastAdaptive")
            else:
                vargs3.append(name + " : Sweep")
            if "Adaptive" in param:
                vargs3.append(["NAME:SimValueContext"])
            else:
                vargs3.append(["NAME:SimValueContext", "Domain:=", "Sweep"])
            if not inputfreq:
                vargs3.append("Calculation:="), vargs3.append(param)
                vargs3.append("Name:="), vargs3.append(param)
                vargs3.append(["NAME:Ranges"])
            else:
                if "Adaptive" in param:
                    vargs3.append("Calculation:="),vargs3.append(param)
                    vargs3.append("Name:="), vargs3.append(param)
                    vargs3.append(["NAME:Ranges", "Range:=",
                                   ["Var:=", "Freq", "Type:=", "d", "DiscreteValues:=", inputfreq + "MHz"]])
                else:
                    vargs3.append("Calculation:="), vargs3.append("min(" + param + ")")
                    vargs3.append("Name:="), vargs3.append(param)
                    startf = (float(inputfreq) - float(deltasweep)) / 1000
                    stopf = (float(inputfreq) + float(deltasweep)) / 1000
                    listf = str(startf) + "GHz,"
                    deltaf = (stopf - startf) / (pointsnum - 1)
                    f = startf + deltaf
                    while f < stopf:
                        listf = listf + str(round(f, 15)) + "GHz,"
                        f = f + deltaf
                    listf = listf + str(round(f, 15)) + "GHz"
                    vargs3.append(["NAME:Ranges", "Range:=",
                                   ["Var:=", "Freq", "Type:=", "rd", "Start:=", str(startf) + "GHz", "Stop:=",
                                    str(stopf) + "GHz", "DiscreteValues:=", listf]])
            vargs2.append(vargs3)
        for param in paramlist:
            '''
            Creating Twice to have original and after iteration loops. this part can be removed in case of single 
            variable export
            '''
            vargs3 = ["NAME:Goal", "ReportType:="]
            if not inputfreq:
                vargs3.append("Eigenmode Parameters")
            else:
                vargs3.append("Modal Solution Data")
            vargs3.append("Solution:=")
            if "Adaptive" in param:
                vargs3.append(name + " : LastAdaptive")
            else:
                vargs3.append(name + " : Sweep")
            if "Adaptive" in param:
                vargs3.append(["NAME:SimValueContext"])
            else:
                vargs3.append(["NAME:SimValueContext", "Domain:=", "Sweep"])

            if not inputfreq:
                vargs3.append("Calculation:=")
                vargs3.append(param)

                vargs3.append("Name:=")
                vargs3.append(param + "_initial")
                vargs3.append(["NAME:Ranges"])
            else:
                if "Adaptive" in param:
                    vargs3.append("Calculation:=")
                    vargs3.append(param)

                    vargs3.append("Name:=")
                    vargs3.append(param + "_initial")
                    vargs3.append(["NAME:Ranges", "Range:=",
                                   ["Var:=", "Freq", "Type:=", "d", "DiscreteValues:=", inputfreq + "MHz"]])
                else:
                    vargs3.append("Calculation:=")
                    vargs3.append("min(" + param + ")")

                    vargs3.append("Name:=")
                    vargs3.append(param + "_initial")
                    startf = (float(inputfreq) - float(deltasweep)) / 1000
                    stopf = (float(inputfreq) + float(deltasweep)) / 1000
                    listf = str(startf) + "GHz,"
                    deltaf = (stopf - startf) / (pointsnum - 1)
                    f = startf + deltaf
                    while f < stopf:
                        listf = listf + str(round(f, 15)) + "GHz,"
                        f = f + deltaf
                    listf = listf + str(round(f, 15)) + "GHz"
                    vargs3.append(["NAME:Ranges", "Range:=",
                                   ["Var:=", "Freq", "Type:=", "rd", "Start:=", str(startf) + "GHz", "Stop:=",
                                    str(stopf) + "GHz", "DiscreteValues:=", listf]])
            vargs2.append(vargs3)

        vargs1.append(vargs2)
        self.ooptimetrics.InsertSetup("OptiDesignExplorer", vargs1)
        return True

    @aedt_exception_handler
    def create_parametric_sweep(self, name="ParametricSetup1", copymesh=False, simsetup=[],
                            varlist=[], varvalues=[]):
        """

        Parameters
        ----------
        name :
             (Default value = "ParametricSetup1")
        copymesh :
             (Default value = False)
        simsetup :
             (Default value = [])
        varlist :
             (Default value = [])
        varvalues :
             (Default value = [])

        Returns
        -------

        """
        if not simsetup:
            simsetup = self.setup_names
        self._insert_parametrics(optitype="OptiParametric", name=name, copymesh=copymesh, simsetup=simsetup,
                            varlist=varlist, varvalues=varvalues)
        infostring = "Parametric Sweep  " + name + " added "
        self._messenger.add_info_message(infostring)
        return True

    @aedt_exception_handler
    def create_dx_component(self, name="ParametricSetup1", copymesh=False, simsetup=[],
                            varlist=[], varvalues=[]):
        """Create a Design Xplorer setup and setup a parametric sweep

        Parameters
        ----------
        name :
            name of setup (Default value = "ParametricSetup1")
        copymesh :
            Bool Copy equivalent mesh (Default value = False)
        simsetup :
            List of setups to include. if None all setups will be added (Default value = [])
        varlist :
            list of variables (Default value = [])
        varvalues :
            list of list of variation for each variable. An expression can be entered but all variations has to be expressions (Default value = [])

        Returns
        -------
        type
            True if succeeded

        """
        if not simsetup:
            simsetup = self.setup_names
        self._insert_parametrics(optitype="DesignXplorerSetup1", name=name, copymesh=copymesh, simsetup=simsetup,
                            varlist=varlist, varvalues=varvalues)
        infostring = "Parametric Sweep  " + name + " added "
        self._messenger.add_info_message(infostring)
        return True

    @aedt_exception_handler
    def _insert_parametrics(self, optitype="OptiParametric", name="ParametricSetup1", copymesh=False, simsetup=[],
                            varlist=[], varvalues=[]):
        """Create an Optimetrics setup and setup a parametric sweep

        Parameters
        ----------
        name :
            name of setup (Default value = "ParametricSetup1")
        copymesh : bool
            Copy equivalent mesh (Default value = False)
        simsetup :
            List of setups to include. if None all setups will be added (Default value = [])
        varlist :
            list of variables (Default value = [])
        varvalues :
            list of list of variation for each variable. An expression can be entered but all variations has to be expressions (Default value = [])
        optitype :
             (Default value = "OptiParametric")

        Returns
        -------
        type
            True if succeeded

        """

        arg = ["NAME:" + name, "IsEnabled:=", True]
        arg.append(["NAME:ProdOptiSetupDataV2", "SaveFields:=", False, "CopyMesh:=", copymesh, "SolveWithCopiedMeshOnly:=", True])
        arg.append(["NAME:StartingPoint"])
        arg.append("Sim. Setups:=")
        arg.append(simsetup)
        arg2 = ["NAME:Sweeps"]
        hastable=False
        firstvalues=[]
        fulllist=[]
        for var, val in zip(varlist, varvalues):
            arg2.append(
                ["NAME:SweepDefinition", "Variable:=", var, "Data:=", val[0], "OffsetF1:=", False, "Synchronize:=", 0])
            firstvalues.append((val[0]))
            if len(val) > 1:
                hastable = True
        if hastable:
            arg3 = ["NAME:Sweep Operations"]
            arg3.append("add:=")
            arg3.append(firstvalues)
            arg3.append("edit:=")
            combination_table = list(sum(list(itertools.product(*varvalues)), ()))
            arg3.append(combination_table)
            arg.append(arg3)
        arg.append(arg2)
        arg.append([ "NAME:Goals"])
        self.ooptimetrics.InsertSetup(optitype, arg)

        infostring = "Parametric Sweep  " + name + " added "
        self._messenger.add_info_message(infostring)
        return True

    @aedt_exception_handler
    def analyze_setup(self, name):
        """Analyze a specific design setup

        Parameters
        ----------
        name :
            name of the setup. it can be an optimetric setup or a simple setup

        Returns
        -------

        """
        if name in self.existing_analysis_setups:
            self._messenger.add_info_message("Solving design setup {}".format(name))
            self.odesign.Analyze(name)
        else:
            try:
                self._messenger.add_info_message("Solving Optimetrics")
                self.ooptimetrics.SolveSetup(name)
            except:
                self._messenger.add_error_message("Setup Not found {}".format(name))
                return False
        return True

    @aedt_exception_handler
    def solve_in_batch(self, filename=None, machine="local", run_in_thread=False):
        """Analyze a specific design setup in batch mode. AEDT project needs to be closed

        Parameters
        ----------
        filename :
            Optional name of the setup. if none the active project will be solved (Default value = None)
        machine :
            optional remote machine name (Default value = "local")
        run_in_thread :
            bool if true the batch command is submitted as thread (Default value = False)

        Returns
        -------

        """
        if not filename:
            filename = self.project_file
            self.close_project()
        if machine == "local":
            # -Monitor option used as workaround for R2 BatchSolve not exiting properly at the end of the Batch job
            options = " -ng -BatchSolve -Monitor "
        else:
            options = " -ng -distribute -machinelist list=" + machine + " -Batchsolve "

        print("Batch Solve Options: " + options)
        if os.name == 'posix':
            batch_run = os.path.join(self.desktop_install_dir + "/ansysedt" + chr(34) + options + chr(
                34) + filename + chr(34))
        else:
            batch_run = chr(34) + self.desktop_install_dir + "/ansysedt.exe" + chr(34) + options + chr(
                34) + filename + chr(34)

        '''
        check for existing solution directory and delete if present so we
        dont have old .asol files etc
        '''

        print("Solving model in batch mode on " + machine)
        print("Batch Job command:" + batch_run)
        if run_in_thread:
            def thread_run():
                """ """
                os.system(batch_run)
            x = threading.Thread(target=thread_run)
            x.start()
        else:
            os.system(batch_run)
        print("Batch Job finished")
        return True


    @aedt_exception_handler
    def submit_job(self, clustername, aedt_full_exe_path=None, numnodes=1, numcores=32, wait_for_license=True, setting_file=None):
        """

        Parameters
        ----------
        clustername :
            name of the cluster to which submit the job
        aedt_full_exe_path :
            if None it will be \\clustername\AnsysEM\AnsysEM2x.x\Win64\ansysedt(.exe) (Default value = None)
        numnodes :
            number of nodes (Default value = 1)
        numcores :
            number of cores (Default value = 32)
        setting_file :
            Optional if provided it will be used as template (Default value = None)
        wait_for_license :
             (Default value = True)

        Returns
        -------
        type
            Job Id

        """
        project_file=self.project_file
        project_path = self.project_path
        if not aedt_full_exe_path:
            version = self.odesktop.GetVersion()[2:6]
            if os.path.exists(r"\\"+clustername+r"\AnsysEM\AnsysEM{}\Win64\ansysedt.exe".format(version)):
                aedt_full_exe_path = r"\\\\\\\\"+clustername+r"\\\\AnsysEM\\\\AnsysEM{}\\\\Win64\\\\ansysedt.exe".format(version)
            elif os.path.exists(r"\\"+clustername+r"\AnsysEM\AnsysEM{}\Linux64\ansysedt".format(version)):
                aedt_full_exe_path = r"\\\\\\\\"+clustername+r"\\\\AnsysEM\\\\AnsysEM{}\\\\Linux64\\\\ansysedt".format(version)
            else:
                self.messenger.add_error_message("Aedt Path doesn't exists. Please provide a full path")
                return False
        else:
            if not os.path.exists(aedt_full_exe_path):
                self.messenger.add_error_message("Aedt Path doesn't exists. Please provide a full path")
                return False
            aedt_full_exe_path.replace("\\", "\\\\")

        self.close_project()
        path_file = os.path.dirname(__file__)
        destination_reg = os.path.join(project_path, "Job_settings.areg")
        if not setting_file:
            setting_file = os.path.join(path_file, "..", "misc","Job_Settings.areg")
        shutil.copy(setting_file, destination_reg)

        f1 = open(destination_reg, 'w')
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
