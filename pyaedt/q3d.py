"""This module contains these classes: `Q2d`, `Q3d`, and `QExtractor`."""
from __future__ import absolute_import

from pyaedt.application.Analysis2D import FieldAnalysis2D
from pyaedt.application.Analysis3D import FieldAnalysis3D
from pyaedt.generic.general_methods import aedt_exception_handler, generate_unique_name
from collections import OrderedDict
from pyaedt.modules.Boundary import BoundaryObject, Matrix
import os
import warnings


class QExtractor(FieldAnalysis3D, FieldAnalysis2D, object):
    """Extracts a 2D or 3D field analysis.

    Parameters
    ----------
    FieldAnalysis3D :

    FieldAnalysis2D :

    object :


    """

    @property
    def design_file(self):
        """Design file."""
        design_file = os.path.join(self.working_directory, "design_data.json")
        return design_file

    def __init__(
        self,
        Q3DType,
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
        if Q3DType == "Q3D Extractor":
            FieldAnalysis3D.__init__(
                self,
                "Q3D Extractor",
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
        else:
            FieldAnalysis2D.__init__(
                self,
                "2D Extractor",
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
        self.omatrix = self.odesign.GetModule("ReduceMatrix")
        self.matrices = []
        for el in list(self.omatrix.ListReduceMatrixes()):
            self.matrices.append(Matrix(self, el))

    def __enter__(self):
        return self

    @aedt_exception_handler
    def insert_reduced_matrix(self, operation_name, source_names=None, rm_name=None):
        """Insert a new reduced matrix.

        Parameters
        ----------
        operation_name : str
            Name of the Operation to create.
        source_names : list, str, optional
            List of sources or nets or arguments needed for specific operation.
        rm_name : str, optional
            Name of the reduced matrix, optional.

        Returns
        -------
        :class:`pyaedt.modules.Boundary.Matrix`
            Matrix object.
        """
        if not rm_name:
            rm_name = generate_unique_name(operation_name)
        matrix = Matrix(self, rm_name, operation_name)
        if matrix.create(source_names):
            self.matrices.append(matrix)
        return matrix


class Q3d(QExtractor, object):
    """Provides the Q3D application interface.

    This class allows you to create an instance of Q3D and link to an
    existing project or create a new one.

    Parameters
    ----------
    projectname : str, optional
        Name of the project to select or the full path to the project
        or AEDTZ archive to open. The default is ``None``, in which
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
        ``None``, in which case the active setup is used or nothing
        is used.
    specified_version : str, optional
        Version of AEDT to use. The default is ``None``, in which case
        the active version or latest installed version is used.
        This parameter is ignored when Script is launched within AEDT.
    NG : bool, optional
        Whether to launch AEDT in the non-graphical mode. The default
        is ``False``, in which case AEDT is launched in the graphical mode.
        This parameter is ignored when Script is launched within AEDT.
    new_desktop_session : bool, optional
        Whether to launch an instance of AEDT in a new thread, even if
        another instance of the ``specified_version`` is active on the
        machine. The default is ``True``. This parameter is ignored when Script is launched within AEDT.
    close_on_exit : bool, optional
        Whether to release AEDT on exit. The default is ``False``.
    student_version : bool, optional
        Whether to open the AEDT student version. The default is ``False``.
        This parameter is ignored when Script is launched within AEDT.

    Examples
    --------
    Create an instance of Q3D and connect to an existing Q3D
    design or create a new Q3D design if one does not exist.

    >>> from pyaedt import Q3d
    >>> app = Q3d()

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
        QExtractor.__init__(
            self,
            "Q3D Extractor",
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

    @property
    def nets(self):
        """Return the list of available nets in actual Q3d Project.

        Returns
        -------
        list

        References
        ----------

        >>> oModule.ListNets
        """
        nets_data = list(self.oboundary.ListNets())
        net_names = []
        for i in nets_data:
            if isinstance(i, (list, tuple)):
                net_names.append(i[0].split(":")[1])
        return net_names

    @aedt_exception_handler
    def net_sources(self, net_name):
        """Check if a net has sources and returns the list of names.

        Parameters
        ----------
        net_name : str
            Name of the net to search for.

        Returns
        -------
        List
            List of Source names.

        Examples
        --------
        >>> from pyaedt import Q3d
        >>> q3d = Q3d("my_project")
        >>> net = q3d.net_sources("Net1")
        """
        sources = []
        net_id = -1
        for i in self.boundaries:
            if i.type == "SignalNet" and i.name == net_name and i.props.get("ID", None) is not None:
                net_id = i.props.get("ID", None)  # pragma: no cover
                break  # pragma: no cover
        for i in self.boundaries:
            if i.type == "Source":
                if i.props.get("Net", None) == net_name or i.props.get("Net", None) == net_id:
                    sources.append(i.name)

        return sources

    @aedt_exception_handler
    def net_sinks(self, net_name):
        """Check if a net has sinks and returns the list of them.

        Parameters
        ----------
        net_name : str
            Name of the net to search for.

        Returns
        -------
        List
            List of Sink names.

        Examples
        --------
        >>> from pyaedt import Q3d
        >>> q3d = Q3d("my_project")
        >>> net = q3d.net_sinks("Net1")
        """
        sinks = []
        net_id = -1
        for i in self.boundaries:
            if i.type == "SignalNet" and i.name == net_name and i.props.get("ID", None) is not None:
                net_id = i.props.get("ID", None)  # pragma: no cover
                break  # pragma: no cover
        for i in self.boundaries:
            if i.type == "Sink" and i.props.get("Net", None) == net_name or i.props.get("Net", None) == net_id:
                sinks.append(i.name)
        return sinks

    @aedt_exception_handler
    def auto_identify_nets(self):
        """Automatically identify nets.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.

        References
        ----------

        >>> oModule.AutoIdentifyNets
        """
        original_nets = [i for i in self.nets]
        self.oboundary.AutoIdentifyNets()
        new_nets = [i for i in self.nets if i not in original_nets]
        for net in new_nets:
            objects = self.modeler.convert_to_selections(
                [int(i) for i in list(self.oboundary.GetExcitationAssignment(net))], True
            )
            props = OrderedDict({"Objects": objects})
            bound = BoundaryObject(self, net, props, "SignalNet")
            self.boundaries.append(bound)
        if new_nets:
            self.logger.info("{} Nets have been identified: {}".format(len(new_nets), ", ".join(new_nets)))
        else:
            self.logger.info("No new nets identified")
        return True

    @aedt_exception_handler
    def assign_net(self, objects, net_name=None, net_type="Signal"):
        """Assign a net to a list of objects.

        Parameters
        ----------
        objects : List, str
            List of objects to assign net. Can be a single object.
        net_name : str, optional
            Name of the net. If `None`, default net name will be provided.
        net_type : str, boolean
            Type of net to create. Can be `Signal`, `Ground` or `Floating`.

        Returns
        -------
        :class:`pyaedt.modules.Boundary.BoundaryObject`
            Source object.

        References
        ----------

        >>> oModule.AssignSignalNet
        >>> oModule.AssignGroundNet
        >>> oModule.AssignFloatingNet

        Examples
        --------
        >>> from pyaedt import Q3d
        >>> q3d = Q3d()
        >>> box = q3d.modeler.create_box([30, 30, 30], [10, 10, 10], name="mybox")
        >>> net_name = "my_net"
        >>> net = q3d.assign_net(box, net_name)
        """
        objects = self.modeler.convert_to_selections(objects, True)
        if not net_name:
            net_name = generate_unique_name("Net")
        props = OrderedDict({"Objects": objects})
        type_bound = "SignalNet"
        if net_type.lower() == "ground":
            type_bound = "GroundNet"
        elif net_type.lower() == "floating":
            type_bound = "FloatingNet"
        bound = BoundaryObject(self, net_name, props, type_bound)
        if bound.create():
            self.boundaries.append(bound)
            return bound
        return False

    @aedt_exception_handler
    def assign_source_to_objectface(self, object_name, axisdir=0, source_name=None, net_name=None):
        """Generate a source on a face of an object.

        The face ID is selected based on ``axisdir``. It is the face that
        has the maximum/minimum in this axis direction.

        Parameters
        ----------
        object_name : str, int
            Name of the object or face id.
            Name of the object.
        axisdir : optional
            Initial axis direction. Options are ``0`` through ``5``. The default is ``0``.
        source_name : str, optional
            Name of the source. The default is ``None``.
        net_name : str, optional
            Name of the net. The default is ``None``, in which case ``object_name`` is considered.

        Returns
        -------
        :class:`pyaedt.modules.Boundary.BoundaryObject`
            Source object.

        References
        ----------

        >>> oModule.AssignSource
        """
        object_name = self.modeler.convert_to_selections(object_name, True)[0]
        if isinstance(object_name, int):
            a = object_name
        else:
            a = self.modeler._get_faceid_on_axis(object_name, axisdir)
        if not source_name:
            source_name = generate_unique_name("Source")
        if not net_name:
            net_name = object_name
        if a:
            props = OrderedDict(
                {"Faces": [a], "ParentBndID": object_name, "TerminalType": "ConstantVoltage", "Net": net_name}
            )
            bound = BoundaryObject(self, source_name, props, "Source")
            if bound.create():
                self.boundaries.append(bound)
                return bound
        return False

    @aedt_exception_handler
    def assign_source_to_sheet(self, sheetname, objectname=None, netname=None, sourcename=None):
        """Generate a source on a sheet.

        Parameters
        ----------
        sheetname : str
            Name of the sheet to create the source on.
        objectname :  str, optional
            Name of the parent object. The default is ``None``.
        netname : str, optional
            Name of the net. The default is ``None``.
        sourcename : str,  optional
            Name of the source. The default is ``None``.

        Returns
        -------
        :class:`pyaedt.modules.Boundary.BoundaryObject`
            Source object.

        References
        ----------

        >>> oModule.AssignSource
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
        """Generate a sink on a face of an object.

        The face ID is selected based on ``axisdir``. It is the face that has
        the maximum/minimum in this axis direction.

        Parameters
        ----------
        object_name : str, int
            Name of the object or face id.
        axisdir : int, optional
            Initial axis direction. Options are ``0`` through ``5``. The default is ``0``.
        sink_name : str, optional
            Name of the sink. The default is ``None``.
        net_name : str, optional
            Name of the net. The default is ``None``, in which case ``object_name`` is considered.

        Returns
        -------
        :class:`pyaedt.modules.Boundary.BoundaryObject`
            Sink object.

        References
        ----------

        >>> oModule.AssignSink
        """
        object_name = self.modeler.convert_to_selections(object_name, True)[0]
        if isinstance(object_name, int):
            a = object_name
            object_name = self.modeler.oeditor.GetObjectNameByFaceID(a)
        else:
            a = self.modeler._get_faceid_on_axis(object_name, axisdir)
        if not sink_name:
            sink_name = generate_unique_name("Sink")
        if not net_name:
            net_name = object_name
        if a:
            props = OrderedDict(
                {"Faces": [a], "ParentBndID": object_name, "TerminalType": "ConstantVoltage", "Net": net_name}
            )
            bound = BoundaryObject(self, sink_name, props, "Sink")
            if bound.create():
                self.boundaries.append(bound)
                return bound
        return False

    @aedt_exception_handler
    def assign_sink_to_sheet(self, sheetname, objectname=None, netname=None, sinkname=None):
        """Generate a sink on a sheet.

        Parameters
        ----------
        sheetname :
            Name of the sheet to create the sink on.
        objectname : str, optional
            Name of the parent object. The default is ``None``.
        netname : str, optional
            Name of the net. The default is ``None``.
        sinkname : str, optional
            Name of the sink. The default is ``None``.

        Returns
        -------
        :class:`pyaedt.modules.Boundary.BoundaryObject`
            Source object.

        References
        ----------

        >>> oModule.AssignSink
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
    def create_frequency_sweep(self, setupname, units, freqstart, freqstop, freqstep=None, sweepname=None):
        """Create a frequency sweep.

        Parameters
        ----------
        setupname : str
            Name of the setup that is attached to the sweep.
        units : str
            Unit of the frequency. For example, ``"MHz"`` or
            ``"GHz"``. The default is ``"GHz"``.
        freqstart :
            Starting frequency of the sweep.
        freqstop :
            Stopping frequency of the sweep.
        freqstep : optional
            Frequency step point.
        sweepname : str, optional
            Name of the sweep. The default is ``None``.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.

        References
        ----------

        >>> oModule.InsertSweep
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
                        self.logger.warning("Sweep %s is already present. Rename and retry.", sweepname)
                        return False
                sweepdata = setupdata.add_sweep(sweepname, "Discrete")
                sweepdata.props["RangeStart"] = str(freqstart) + "GHz"
                if not freqstop:
                    freqstop = freqstart
                if not freqstep:
                    freqstep = (freqstop - freqstart) / 11
                    if freqstep == 0:
                        freqstep = freqstart
                sweepdata.props["RangeEnd"] = str(freqstop) + "GHz"
                sweepdata.props["RangeStep"] = str(freqstep) + "GHz"
                sweepdata.props["SaveFields"] = False
                sweepdata.props["SaveRadFields"] = False
                sweepdata.props["Type"] = "Interpolating"
                sweepdata.props["RangeType"] = "LinearStep"
                sweepdata.update()
                return sweepdata
        return False

    @aedt_exception_handler
    def create_discrete_sweep(
        self, setupname, freqstart, freqstop=None, freqstep=None, units="GHz", sweepname=None, savefields=False
    ):
        """Create a discrete sweep with a single frequency value.

        Parameters
        ----------
        setupname : str
            Name of the setup that the sweeps belongs to.
        freqstart : float
            Starting point for the discrete frequency.
        freqstop : float, optional
            Stopping point for the discrete frequency. If ``None``,
            a single-point sweep is to be performed.
        freqstep : float, optional
            Step point for the discrete frequency. If ``None``,
            11 points will be created.
        units : str, optional
            Unit of the discrete frequency. For example, ``"MHz"`` or
            ``"GHz"``.The default is ``"GHz"``.
        sweepname : str, optional
            Name of the sweep.
        savefields : bool, optional
            Whether to save fields. The default is ``False``.

        Returns
        -------
        SweepQ3D
            Sweep option.

        References
        ----------

        >>> oModule.InsertSweep
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
                        self.logger.warning("Sweep %s already present. Please rename and retry", sweepname)
                        return False
                sweepdata = setupdata.add_sweep(sweepname, "Discrete")
                sweepdata.props["RangeStart"] = str(freqstart) + "GHz"
                if not freqstop:
                    freqstop = freqstart
                if not freqstep:
                    freqstep = (freqstop - freqstart) / 11
                    if freqstep == 0:
                        freqstep = freqstart
                sweepdata.props["RangeEnd"] = str(freqstop) + "GHz"
                sweepdata.props["RangeStep"] = str(freqstep) + "GHz"
                sweepdata.props["SaveFields"] = savefields
                sweepdata.props["SaveRadFields"] = False
                sweepdata.props["Type"] = "Discrete"
                sweepdata.props["RangeType"] = "LinearStep"
                sweepdata.update()
                return sweepdata
        return False


class Q2d(QExtractor, object):
    """Provides the Q2D application interface.

    This class allows you to create an instance of Q2D and link to an
    existing project or create a new one.

    Parameters
    ----------
    projectname : str, optional
        Name of the project to select or the full path to the project
        or AEDTZ archive to open. The default is ``None``, in which
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
        the active version or latest installed version is used.  This
        parameter is ignored when Script is launched within AEDT.
    NG : bool, optional
        Whether to launch AEDT in the non-graphical mode. The default
        is ``False``, in which case AEDT is launched in the graphical mode.
        This parameter is ignored when Script is launched within AEDT.
    new_desktop_session : bool, optional
        Whether to launch an instance of AEDT in a new thread, even if
        another instance of the ``specified_version`` is active on the
        machine. The default is ``True``. This parameter is ignored
        when Script is launched within AEDT.
    close_on_exit : bool, optional
        Whether to release AEDT on exit. The default is ``False``.
    student_version : bool, optional
        Whether to open the AEDT student version. This parameter is
        ignored when Script is launched within AEDT.

    Examples
    --------
    Create an instance of Q2D and link to a project named
    ``projectname``. If this project does not exist, create one with
    this name.

    >>> from pyaedt import Q2d
    >>> app = Q2d(projectname)

    Create an instance of Q2D and link to a design named
    ``designname`` in a project named ``projectname``.

    >>> app = Q2d(projectname,designame)

    Create an instance of Q2D and open the specified project,
    which is named ``myfile.aedt``.

    >>> app = Q2d("myfile.aedt")

    """

    @property  # for legacy purposes
    def dim(self):
        """Dimension."""
        return self.modeler.dimension

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
        QExtractor.__init__(
            self,
            "2D Extractor",
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

    @aedt_exception_handler
    def create_rectangle(self, position, dimension_list, name="", matname=""):
        """
        Create a rectangle.

        Parameters
        ----------
        position : list
            List of [x, y] coordinates for the starting point of the rectangle.
        dimension_list : list
            List of [width, height] dimensions.
        name : str, optional
            Name of the rectangle. The default is ``None``, in which case
            the default name is assigned.
        matname : str, optional
            Name of the material. The default is ``None``, in which case
            the default material is assigned.
        Returns
        -------
        pyaedt.modeler.Object3d.Object3d
            3D object.

        References
        ----------

        >>> oEditor.CreateRectangle
        """
        return self.modeler.primitives.create_rectangle(
            position, dimension_list=dimension_list, name=name, matname=matname
        )

    @aedt_exception_handler
    def assign_single_signal_line(self, target_objects, name="", solve_option="SolveInside", thickness=None, unit="um"):
        """Assign conductor type to sheets.

        Parameters
        ----------
        target_objects : list
            List of Object3D.
        name : str
            Name of the conductor.
        solve_option : str, optional
            Method for solving. Options are ``"SolveInside"``, ``"SolveOnBoundary"`` or ``"Automatic"``. The default is
            ``"SolveInside"``.
        thickness : float, optional
            Conductor thickness. The default is ``None``, in which case the conductor thickness is obtained by dividing
            the conductor's area by its perimeter (A/p). If multiple conductors are selected, the average conductor
            thickness is used.
        unit : str, optional
            Thickness unit. The default is ``"um"``.

        References
        ----------

        >>> oModule.AssignSingleSignalLine
        >>> oModule.AssignSingleReferenceGround
        """

        warnings.warn(
            "`assign_single_signal_line` is deprecated. Use `assign_single_conductor` instead.", DeprecationWarning
        )
        self.assign_single_conductor(target_objects, name, "SignalLine", solve_option, thickness, unit)

    @aedt_exception_handler
    def assign_single_conductor(
        self,
        target_objects,
        name="",
        conductor_type="SignalLine",
        solve_option="SolveInside",
        thickness=None,
        unit="um",
    ):
        """
        Assign conductor type to sheets.

        Parameters
        ----------
        target_objects : list
            List of Object3D.
        name : str
            Name of the conductor.
        conductor_type : str
            Type of conductor. Options are ``"SignalLine"``, ``"ReferenceGround"``. The default is SignalLine.
        solve_option : str, optional
            Method for solving. Options are ``"SolveInside"``, ``"SolveOnBoundary"`` or ``"Automatic"``. The default is
            ``"SolveInside"``.
        thickness : float, optional
            Conductor thickness. The default is ``None``, in which case the conductor thickness is obtained by dividing
            the conductor's area by its perimeter (A/p). If multiple conductors are selected, the average conductor
            thickness is used.
        unit : str, optional
            Thickness unit. The default is ``"um"``.

        Returns
        -------
        :class:`pyaedt.modules.Boundary.BoundaryObject`
            Source object.

        References
        ----------

        >>> oModule.AssignSingleSignalLine
        >>> oModule.AssignSingleReferenceGround
        """
        if not name:
            name = generate_unique_name(name)

        if isinstance(target_objects, list):
            a = target_objects
            obj_names = [i.name for i in target_objects]
        else:
            a = [target_objects]
            obj_names = [target_objects.name]

        if not thickness:
            t_list = []
            for t_obj in a:
                perimeter = 0
                for edge in t_obj.edges:
                    perimeter = perimeter + edge.length
                t_list.append(t_obj.faces[0].area / perimeter)
            thickness = sum(t_list) / len(t_list)

        props = OrderedDict({"Objects": obj_names, "SolveOption": solve_option, "Thickness": str(thickness) + unit})

        bound = BoundaryObject(self, name, props, conductor_type)
        if bound.create():
            self.boundaries.append(bound)
            return bound
        return False

    @aedt_exception_handler
    def assign_huray_finitecond_to_edges(self, edges, radius, ratio, unit="um", name=""):
        """
        Assign Huray surface roughness model to edges.

        Parameters
        ----------
        radius :
        ratio :
        unit :
        edges :
        name :
        model_type :

        Returns
        -------
        :class:`pyaedt.modules.Boundary.BoundaryObject`
            Source object.

        References
        ----------

        >>> oMdoule.AssignFiniteCond
        """
        if not name:
            name = generate_unique_name(name)

        if not isinstance(radius, str):
            ra = str(radius) + unit
        else:
            ra = radius

        a = self.modeler._convert_list_to_ids(edges, convert_objects_ids_to_name=False)

        props = OrderedDict({"Edges": a, "UseCoating": False, "Radius": ra, "Ratio": str(ratio)})

        bound = BoundaryObject(self, name, props, "FiniteCond")
        if bound.create():
            self.boundaries.append(bound)
            return bound
        return False

    @aedt_exception_handler
    def auto_assign_conductors(self):
        """Auto Assign Conductors to Signal Lines.

        Returns
        -------
        bool
        """
        original_nets = list(self.oboundary.GetExcitations())
        self.oboundary.AutoAssignSignals()
        new_nets = [i for i in list(self.oboundary.GetExcitations()) if i not in original_nets]
        i = 0
        while i < len(new_nets):
            objects = self.modeler.convert_to_selections(
                [int(k) for k in list(self.oboundary.GetExcitationAssignment(new_nets[i]))], True
            )
            props = OrderedDict({"Objects": objects})
            bound = BoundaryObject(self, new_nets[i], props, new_nets[i + 1])
            self.boundaries.append(bound)
            i += 2
        if new_nets:
            self.logger.info("{} Nets have been identified: {}".format(len(new_nets), ", ".join(new_nets)))
        else:
            self.logger.info("No new nets identified")
        return True

    @aedt_exception_handler
    def toggle_conductor_type(self, conductor_name, new_type):
        """Change the conductor type.

        Parameters
        ----------
        conductor_name : str
            Name of the conductor to update.
        new_type : str
            New conductor type.

        Returns
        -------
        bool
        """
        try:
            self.oboundary.ToggleConductor(conductor_name, new_type)
            for bound in self.boundaries:
                if bound.name == conductor_name:
                    bound.type = new_type
            self.logger.info("Conductor type correctly updated")
            return True
        except:
            self.logger.error("Error in updating conductor type")
            return False
