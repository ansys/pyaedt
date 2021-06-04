"""
Q3D Class
---------------------


Description
==================================================

This class contains all the Q3D Functionalities. It inherites all the objects that belongs to Q3D


:Example:

app = Q3d()     creates and Q3D object and connect to existing Q3D design (create a new Q3D design if not present)


app = Q2d(projectname)     creates and Q2d and link to projectname project


app = Q2d(projectname,designame)     creates and Q3D object and link to designname design in projectname project


app = Q2dD("myfile.aedt")     creates and Q2d object and open specified project



"""
from __future__ import absolute_import

from .application.Analysis2D import FieldAnalysis2D
from .application.Analysis3D import FieldAnalysis3D
from .desktop import exception_to_desktop
from .generic.general_methods import aedt_exception_handler, generate_unique_name
from collections import OrderedDict
from .modules.Boundary import BoundaryObject
import os

class QExtractor(FieldAnalysis3D, FieldAnalysis2D, object):
    """ """
    @property
    def odefinition_manager(self):
        """ """
        return self.oproject.GetDefinitionManager()

    @property
    def omaterial_manager(self):
        """ """
        return self.odefinition_manager.GetManager("Material")

    '''
    @property
    def oeditor(self):
        """ """
        return self.odesign.SetActiveEditor("3D Modeler")
    '''

    @property
    def symmetry_multiplier(self):
        """ """
        omodule = self._odesign.GetModule("ModelSetup")
        return int(omodule.GetSymmetryMultiplier())


    @property
    def design_file(self):
        """ """
        design_file = os.path.join(self.working_directory, "design_data.json")
        return design_file

    def __init__(self, Q3DType, projectname=None, designname=None, solution_type=None, setup_name=None):
        if Q3DType == "Q3D Extractor":
            FieldAnalysis3D.__init__(self, "Q3D Extractor", projectname, designname, solution_type, setup_name)
        else:
            FieldAnalysis2D.__init__(self, "2D Extractor", projectname, designname, solution_type, setup_name)

    def __enter__(self):
        return self

    def __exit__(self, ex_type, ex_value, ex_traceback):
        """ Push exit up to parent object Design """
        if ex_type:
            exception_to_desktop(self, ex_value, ex_traceback)


class Q3d(QExtractor, object):
    """Q3D Object

    Parameters
    ----------
    projectname :
        name of the project to be selected or full path to the project to be opened  or to the AEDTZ
        archive. if None try to get active project and, if nothing present to create an empty one
    designname :
        name of the design to be selected. if None, try to get active design and, if nothing present to create an empty one
    solution_type :
        solution type to be applied to design. if None default is taken
    setup_name :
        setup_name to be used as nominal. if none active setup is taken or nothing

    Returns
    -------

    """
    def __init__(self, projectname=None, designname=None, solution_type=None, setup_name=None):
        QExtractor.__init__(self, "Q3D Extractor", projectname, designname, solution_type, setup_name)

    @aedt_exception_handler
    def auto_identify_nets(self):
        """Automatically Iddentify Nets
        :return:

        Parameters
        ----------

        Returns
        -------

        """
        self.oboundary.AutoIdentifyNets()
        return True

    @aedt_exception_handler
    def assign_source_to_objectface(self, object_name, axisdir=0, source_name=None, net_name=None):
        """Generate a source on a face id of an object. Face ID is selected based on axisdir. It will be the face that
        has the maximum/minimum in that axis dir

        Parameters
        ----------
        object_name :
            name of the object
        axisdir :
            int axis direction. 0-5 (Default value = 0)
        source_name :
            name of the source (optional) (Default value = None)
        net_name :
            optional net name. in None, object_name will be considered (Default value = None)

        Returns
        -------
        type
            source object

        """
        a = self.modeler._get_faceid_on_axis(object_name, axisdir)

        if not source_name:
            source_name = generate_unique_name("Source")
        if not net_name:
            net_name =object_name
        if a:
            props = OrderedDict(
                {"Faces": [a], "ParentBndID": object_name, "TerminalType": "ConstantVoltage", "Net": net_name})
            bound = BoundaryObject(self, source_name, props, "Source")
            if bound.create():
                self.boundaries.append(bound)
                return bound
        return False


    @aedt_exception_handler
    def assign_source_to_object(self, sheetname, obj_name, netname=None, source_name=None):
        """Generate a source on a face id of an object. Face ID is selected based on axisdir. It will be the face that
        has the maximum/minimum in that axis dir

        Parameters
        ----------
        sheetname :
            name of the sheet/object on which create a source
        obj_name :
            name of the parent object
        netname :
            name of the net (optional) (Default value = None)
        source_name :
            name of the source (optional) (Default value = None)

        Returns
        -------
        type
            source object

        """
        if not netname:
            netname = obj_name
        if not source_name:
            source_name = generate_unique_name("Source")
        sheetname = self.modeler._convert_list_to_ids(sheetname)

        props = OrderedDict({"Faces": sheetname, "ParentBndID": obj_name, "Net": netname})
        bound = BoundaryObject(self, source_name, props, "Source")
        if bound.create():
            self.boundaries.append(bound)
            return bound
        return False


    @aedt_exception_handler
    def assign_sink_to_objectface(self, object_name, axisdir=0, sink_name=None, net_name=None):
        """Generate a sink on a face id of an object. Face ID is selected based on axisdir. It will be the face that
        has the maximum/minimum in that axis dir

        Parameters
        ----------
        object_name :
            name of the object
        axisdir :
            int axis direction. 0-5 (Default value = 0)
        netname :
            name of the net (optional)
        sink_name :
            name of the sink (optional) (Default value = None)
        net_name :
            optional net name. in None, object_name will be considered (Default value = None)

        Returns
        -------
        type
            sink object

        """
        a = self.modeler._get_faceid_on_axis(object_name, axisdir)

        if not sink_name:
            sink_name = generate_unique_name("Sink")
        if not net_name:
            net_name = object_name
        if a:
            props = OrderedDict(
                {"Faces": [a], "ParentBndID": object_name, "TerminalType": "ConstantVoltage", "Net": net_name})
            bound = BoundaryObject(self, sink_name, props, "Sink")
            if bound.create():
                self.boundaries.append(bound)
                return bound
        return False

    @aedt_exception_handler
    def assign_sink_to_sheet(self, sheetname, obj_name, netname=None, sink_name=None):
        """Generate a sink on a face id of an object. Face ID is selected based on axisdir. It will be the face that
        has the maximum/minimum in that axis dir

        Parameters
        ----------
        sheetname :
            name of the sheet/object on which create a sink
        obj_name :
            name of the parent object
        netname :
            name of the net (optional) (Default value = None)
        sink_name :
            name of the source (optional) (Default value = None)

        Returns
        -------
        type
            sink object

        """
        if not netname:
            netname = obj_name
        if not sink_name:
            sink_name = generate_unique_name("Sink")
        props = OrderedDict({"Objects": [sheetname], "ParentBndID": obj_name, "Net": netname})
        bound = BoundaryObject(self, sink_name, props, "Sink")
        if bound.create():
            self.boundaries.append(bound)
            return bound
        return False


    @aedt_exception_handler
    def create_frequency_sweep(self, setupname, unit, freqstart, freqstop, fastsweep=False):
        """

        Parameters
        ----------
        setupname :
            name of the setup to which is attached the sweep
        unit :
            Units ("MHz", "GHz"....)
        freqstart :
            Starting Frequency of sweep
        freqstop :
            Stop Frequency of Sweep
        fastsweep :
            boolean =False for Fast sweep, True for interpolating (Default value = False)

        Returns
        -------

        """

        arg = ["Name:Sweep", "IsEnabled:=", True, "RangeType:=", "LinearCount", "RangeStart:=",
               str(freqstart) + unit,
               "RangeEnd:=", str(freqstop) + unit]
        sweeptype = "Fast" if fastsweep is True else "Interpolating"
        arg += ["RangeCount:=", 451, "Type:="]
        arg.append(sweeptype)
        arg += ["SaveFields:=", False, "SaveRadFields:=", False]
        if fastsweep:
            arg += ["GenerateFieldsForAllFreqs:=", False, "ExtrapToDC:=", False]
            print("Fast Sweep Setup")
        else:
            arg += ["InterpTolerance:=", 0.5, "InterpMaxSolns:=", 250, "InterpMinSolns:=", 0,
                    "InterpMinSubranges:=", 1]
            arg += ["ExtrapToDC:=", False, "InterpUseS:=", True, "InterpUsePortImped:=", False,
                    "InterpUsePropConst:=", True]
            arg += ["UseDerivativeConvergence:=", False, "InterpDerivTolerance:=", 0.2, "UseFullBasis:=", True]
            arg += ["EnforcePassivity:=", True, "PassivityErrorTolerance:=", 0.0001]
            print("Interpolating Sweep Setup")
        self.oanalysis.InsertFrequencySweep(setupname, arg)
        print("Setup Created Correctly")
        return setupname


    @aedt_exception_handler
    def create_discrete_sweep(self, setup_name, sweep_name, freq):
        """Create a Discrete Sweep with a single frequency value
        name: Setup name
        freq: sweep freq (including Units) as string
        sweepname: name of the sweep

        Parameters
        ----------
        setup_name :
            
        sweep_name :
            
        freq :
            

        Returns
        -------

        """
        self.oanalysis.InsertFrequencySweep(setup_name,
                                                  [
                                                      "NAME:" + sweep_name,
                                                      "IsEnabled:=", True,
                                                      "RangeType:=", "SinglePoints",
                                                      "RangeStart:=", freq,
                                                      "RangeEnd:=", freq,
                                                      "SaveSingleField:=", False,
                                                      "Type:=", "Discrete",
                                                      "SaveFields:=", True,
                                                      "SaveRadFields:=", False,
                                                      "ExtrapToDC:=", False
                                                  ])
        return True


class Q2d(QExtractor, object):
    """Q2D Object

    Parameters
    ----------
    projectname :
        name of the project to be selected or full path to the project to be opened  or to the AEDTZ
        archive. if None try to get active project and, if nothing present to create an empty one
    designname :
        name of the design to be selected. if None, try to get active design and, if nothing present to create an empty one
    solution_type :
        solution type to be applied to design. if None default is taken
    setup_name :
        setup_name to be used as nominal. if none active setup is taken or nothing

    Returns
    -------

    """

    @property   # for legacy purposes
    def dim(self):
        """ """
        return self.modeler.dimension

    @property
    def geometry_mode(self):
        """ """
        return self.odesign.GetGeometryMode()

    def __init__(self, projectname=None, designname=None, solution_type=None, setup_name=None):
        QExtractor.__init__(self, "2D Extractor", projectname, designname, solution_type, setup_name)
