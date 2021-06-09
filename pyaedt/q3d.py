"""
Q3D Class
---------------------

This class contains all Q3D functionalities. It inherits all objects that belong to Q3D.


Examples:

app = Q3d()     Creates a ``Q3d`` object and connects to an existing Q3D design or create a new Q3D design if one is not present.


app = Q2d(projectname)     Creates a ``Q2d`` object and links to a project named projectname.


app = Q2d(projectname,designame)     Creates a ``Q2d`` object and links to a design named designname in a project named projectname.


app = Q2d("myfile.aedt")     Creates a ``Q2d`` object and opens the specified project.



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
        BoundaryObject
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
    def assign_source_to_sheet(self, sheetname, objectname=None, netname=None, sourcename=None):
        """Generate a source on aobject.  It will be the face that
        has the maximum/minimum in that axis dir

        Parameters
        ----------
        sheetname :
            name of the sheet/object on which create a source
        objectname :
            name of the parent object
        netname :
            name of the net (optional) (Default value = None)
        sourcename :
            name of the source (optional) (Default value = None)

        Returns
        -------
        BoundaryObject
            source object

        """

        if not sourcename:
            sourcename = generate_unique_name("Source")
        sheetname = self.modeler._convert_list_to_ids(sheetname)
        props = OrderedDict({"Objects": [sheetname]})
        if objectname:
            props["ParentBndID"] = objectname
        props["TerminalType"] = "ConstantVoltage"
        if netname:
            props["Net"] = netname
        props = OrderedDict({"Objects": sheetname, "TerminalType": "ConstantVoltage", "Net": netname})
        bound = BoundaryObject(self, sourcename, props, "Source")
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
        BoundaryObject
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
    def assign_sink_to_sheet(self, sheetname, objectname=None, netname=None, sinkname=None):
        """Generate a sink on aobject.  It will be the face that
        has the maximum/minimum in that axis dir

        Parameters
        ----------
        sheetname :
            name of the sheet/object on which create a sink
        objectname :
            name of the parent object
        netname :
            name of the net (optional) (Default value = None)
        sinkname :
            name of the sink (optional) (Default value = None)

        Returns
        -------
        BoundaryObject
            source object

        """

        if not sinkname:
            sinkname = generate_unique_name("Source")
        sheetname = self.modeler._convert_list_to_ids(sheetname)
        props = OrderedDict({"Objects": [sheetname]})
        if objectname:
            props["ParentBndID"] = objectname
        props["TerminalType"] = "ConstantVoltage"
        if netname:
            props["Net"] = netname

        props = OrderedDict({"Objects": sheetname, "TerminalType": "ConstantVoltage", "Net": netname})
        bound = BoundaryObject(self, sinkname, props, "Sink")
        if bound.create():
            self.boundaries.append(bound)
            return bound
        return False

    @aedt_exception_handler
    def create_frequency_sweep(self, setupname, unit, freqstart, freqstop, freqstep=None, sweepname=None):
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


        Returns
        -------

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
                        self.messenger.add_warning_message("Sweep {} already present. Please rename and retry".format(sweepname))
                        return False
                sweepdata = setupdata.add_sweep(sweepname, "Discrete")
                sweepdata.props["RangeStart"] = freqstart
                if not freqstop:
                    freqstop = freqstart
                if not freqstep:
                    freq_step = (freqstop-freqstart)/11
                    if freq_step == 0:
                        freqstep = freqstart
                sweepdata.props["RangeEnd"] = freqstop
                sweepdata.props["RangeStep"] = freqstep
                sweepdata.props["SaveFields"] = False
                sweepdata.props["SaveRadFields"] = False
                sweepdata.props["Type"] = "Interpolating"
                sweepdata.props["RangeType"] = "LinearStep"
                sweepdata.update()
                return sweepdata
        return False

    @aedt_exception_handler
    def create_discrete_sweep(self, setupname, freqstart, freqstop=None, freqstep=None, units="GHz", sweepname=None, savefields=False):
        """Create a Discrete Sweep with a single frequency value

        Parameters
        ----------
        setupname : str
            name of setup to which sweeps belongs
            
        sweepname : str
            name of sweep
            
        freqstart : float
            discrete frequency start point
        freqstop : float
            discrete frequency stop point. If None, single point sweep
        freqstep : float
            discrete frequency step point. If None, 11 points will be created
        units  : str
            Default GHz
        savefields : bool
            define if field will be generated

        Returns
        -------
        SweepQ3D:
            sweep option
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
                        self.messenger.add_warning_message("Sweep {} already present. Please rename and retry".format(sweepname))
                        return False
                sweepdata = setupdata.add_sweep(sweepname, "Discrete")
                sweepdata.props["RangeStart"] = freqstart
                if not freqstop:
                    freqstop = freqstart
                if not freqstep:
                    freqstep = (freqstop - freqstart) / 11
                    if freqstep == 0:
                        freqstep = freqstart
                sweepdata.props["RangeEnd"] = freqstop
                sweepdata.props["RangeStep"] = freqstep
                sweepdata.props["SaveFields"] = savefields
                sweepdata.props["SaveRadFields"] = False
                sweepdata.props["Type"] = "Discrete"
                sweepdata.props["RangeType"] = "LinearStep"
                sweepdata.update()
                return sweepdata
        return False

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


    def __init__(self, projectname=None, designname=None, solution_type=None, setup_name=None):
        QExtractor.__init__(self, "2D Extractor", projectname, designname, solution_type, setup_name)
