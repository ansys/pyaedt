"""
This module contains all Q3D functionalities in the ``q3d`` class. It inherits all objects that belong to Q3D.


Examples:

Create a ``Q3d`` object and connect to an existing Q3D design or create a new Q3D design if one does not exist.

>>> app = Q3d()

Create a ``Q2d`` object and link to a project named ``projectname``. If this project does not exist, create one with this name.

>>> app = Q2d(projectname)

Create a ``Q2d`` object and link to a design named ``designname`` in a project named ``projectname``.

>>> app = Q2d(projectname,designame)

Create a ``Q2d`` object and open the specified project.

>>> app = Q2d("myfile.aedt")

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

    def __init__(self, Q3DType, projectname=None, designname=None, solution_type=None, setup_name=None,
                 specified_version=None, NG=False, AlwaysNew=False, release_on_exit=False):
        if Q3DType == "Q3D Extractor":
            FieldAnalysis3D.__init__(self, "Q3D Extractor", projectname, designname, solution_type, setup_name,
                                     specified_version, NG, AlwaysNew, release_on_exit)
        else:
            FieldAnalysis2D.__init__(self, "2D Extractor", projectname, designname, solution_type, setup_name,
                                     specified_version, NG, AlwaysNew, release_on_exit)

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
    projectname : str, optional
        Name of the project to select or the full path to the project or AEDTZ archive to open. 
        The default is ``None``. If ``None``, try to get an active project and, if no projects are present, 
        create an empty project.
    designname : str, optional
        Name of the design to select. The default is ``None``. If ``None``, try to get an active design and, 
        if no designs are present, create an empty design.
    solution_type : str, optional
        Solution type to apply to design. The default is ``None``. If ``None`, the default type is applied.
    setup_name : str, optional
        Name of the setup to use as the nominal. The default is ``None``. If ``None``, the active setup 
        is used or nothing is used.
    
    Returns
    -------

    """
    def __init__(self, projectname=None, designname=None, solution_type=None, setup_name=None,
                 specified_version=None, NG=False, AlwaysNew=False, release_on_exit=False):
        QExtractor.__init__(self, "Q3D Extractor", projectname, designname, solution_type, setup_name,
                            specified_version, NG, AlwaysNew, release_on_exit)

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
        """Generate a source on a face ID of an object. The face ID is selected based on ``axisdir``. It will 
        be the face that has the maximum/minimum in this axis direction.

        Parameters
        ----------
        object_name : str
            Name of the object.
        axisdir : optional
            Initial axis direction. Choices are ``0`` through ``5``. The default is ``0``.
        source_name : str, optional
            Name of the source. The default is ``None``.
        net_name : str, optional
            Name of the net. The default is ``None`` in which case ``object_name`` will be considered.

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
        """Generate a source on an object.  It will be the face that
        has the maximum/minimum in this axis.

        Parameters
        ----------
        sheetname : str
            Name of the sheet or object on which to create the source.
        objectname :  str, optional
            Name of the parent object. The default is ``None``.
        netname : str, optional
            Name of the net. The default is ``None``.
        sourcename : str,  optional
            Name of the source. The default is ``None``.

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
        """Generate a sink on a face ID of an object. The face ID is selected based on ``axisdir``. It will 
        be the face that has the maximum/minimum in this axis direction.

        Parameters
        ----------
        object_name : str
            Name of the object.
        axisdir : optional
            The initial axis direction. Choices are ``0`` through ``5``. The default is ``None``.
        sink_name : str, optional
            Name of the sink. The default is ``None``.
        net_name : str, optional
            Name of the net. The default is ``None`` in which case ``object_name`` will be considered.

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
        """Generate a sink on an object.  It will be the face that
        has the maximum/minimum in this axis direction.

        Parameters
        ----------
        sheetname :
            Name of the sheet or object on which to create the sink.
        objectname : str, optional
            Name of the parent object. The default is ``None``.
        netname : str, optional
            Name of the net. The default is ``None``.
        sinkname : str, optional
            Name of the sink. The default is ``None``.

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
        setupname : str
            Name of the setup that is attached to the sweep.
        unit : str
            Unit of the frequency. For example, ``"MHz"`` or ``"GHz"``. The default is ``"GHz"`.
        freqstart :
            Starting frequency of the sweep.
        freqstop : 
            Stopping frequency of the sweep.
        freqstep : optional
            Frequency step point.
        sweepname : str, optional
            Name of the sweep.

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
                        self.messenger.add_warning_message("Sweep {} is already present. Rename and retry.".format(sweepname))
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
        """Create a discrete sweep with a single frequency value.

        Parameters
        ----------
        setupname : str
            Name of the setup to which the sweeps belongs.
        freqstart : float
            Discrete frequency starting point.
        freqstop : float, optional
            Discrete frequency stopping point. If ``None``, a single-point sweep will be performed.
        freqstep : float, optional
            Discrete frequency step point. If ``None``, 11 points will be created.
        units  : str, optional
            Unit of the discrete frequency. The default is ``"GHz"``.    
        sweepname : str, optional
            Name of the sweep.
        savefields : bool, optional
            Whether to generate fields. The default is ``False``.

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
    projectname : str, optional
        Name of the project to select or the full path to the project or AEDTZ archive to open. 
        The default is ``None``. If ``None``, try to get an active project and, if no projects are present, 
        create an empty project.
    designname : str, optional
        Name of the design to select. The default is ``None``. If ``None``, try to get an active design and, 
        if no designs are present, create an empty design.
    solution_type : str, optional
        Solution type to apply to design. The default is ``None``. If ``None`, the default type is applied.
    setup_name : str, optional
        The name of the setup to use as the nominal. The default is ``None``. If ``None``, the active setup 
        is used or nothing is used.
    
    Returns
    -------

    """

    @property   # for legacy purposes
    def dim(self):
        """ """
        return self.modeler.dimension


    def __init__(self, projectname=None, designname=None, solution_type=None, setup_name=None,
                 specified_version=None, NG=False, AlwaysNew=False, release_on_exit=False):
        QExtractor.__init__(self, "2D Extractor", projectname, designname, solution_type, setup_name,
                            specified_version, NG, AlwaysNew, release_on_exit)
