"""This module contains these classes: ``Q2d``, ``Q3d``, and ``QExtractor`."""
from __future__ import absolute_import  # noreorder

import os
import warnings
from collections import OrderedDict

from pyaedt import is_ironpython
from pyaedt import settings
from pyaedt.application.Analysis3D import FieldAnalysis3D
from pyaedt.application.Variables import decompose_variable_value
from pyaedt.generic.constants import MATRIXOPERATIONSQ2D
from pyaedt.generic.constants import MATRIXOPERATIONSQ3D
from pyaedt.generic.general_methods import generate_unique_name
from pyaedt.generic.general_methods import pyaedt_function_handler
from pyaedt.modules.Boundary import BoundaryObject
from pyaedt.modules.Boundary import Matrix

if not is_ironpython:
    try:
        import numpy as np
    except ImportError:
        pass


class QExtractor(FieldAnalysis3D, object):
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
        machine="",
        port=0,
        aedt_process_id=None,
    ):
        FieldAnalysis3D.__init__(
            self,
            Q3DType,
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
        self.matrices = []
        for el in list(self.omatrix.ListReduceMatrixes()):
            self.matrices.append(Matrix(self, el))

    def __enter__(self):
        return self

    @property
    def excitations(self):
        """Get all excitation names.

        Returns
        -------
        list
            List of excitation names. Excitations with multiple modes will return one
            excitation for each mode.

        """
        return self.matrices[0].sources(False)

    @pyaedt_function_handler()
    def insert_reduced_matrix(self, operation_name, source_names=None, rm_name=None):
        """Insert a new reduced matrix.

        Parameters
        ----------
        operation_name : str
            Name of the operation to create.
        source_names : list, str, optional
            List of sources or nets or arguments needed for the operation. The default
            is ``None``.
        rm_name : str, optional
            Name of the reduced matrix. The default is ``None``.

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

    @pyaedt_function_handler()
    def get_all_sources(self):
        """Get all setup sources.

        Returns
        -------
        list of str
            List of all setup sources.

        References
        ----------

        >>> oModule.GetAllSources
        """
        return self.excitations

    @pyaedt_function_handler()
    def get_traces_for_plot(
        self,
        get_self_terms=True,
        get_mutual_terms=True,
        first_element_filter=None,
        second_element_filter=None,
        category="C",
    ):
        """Get a list of traces of specified designs ready to use in plot reports.

        Parameters
        ----------
        get_self_terms : bool, optional
            Whether to get self terms. The default is ``True``.
        get_mutual_terms : bool, optional
            Whether to get mutual terms. The default is ``True``.
        first_element_filter : str, optional
            Filter to apply to the first element of the equation.
            This parameter accepts ``*`` and ``?`` as special characters. The default is ``None``.
        second_element_filter : str, optional
            Filter to apply to the second element of the equation.
            This parameter accepts ``*`` and ``?`` as special characters. The default is ``None``.
        category : str
            Plot category name as in the report, including operator.
            The default is ``"C"``, which is the plot category name for capacitance.

        Returns
        -------
        list
            Traces of specified designs ready to use in plot reports.

        Examples
        --------
        >>> from pyaedt import Q3d
        >>> hfss = Q3d(project_path)
        >>> hfss.get_traces_for_plot(first_element_filter="Bo?1",
        ...                           second_element_filter="GND*", category="C")
        """
        return self.matrices[0].get_sources_for_plot(
            get_self_terms=get_self_terms,
            get_mutual_terms=get_mutual_terms,
            first_element_filter=first_element_filter,
            second_element_filter=second_element_filter,
            category=category,
        )

    @pyaedt_function_handler()
    def export_mesh_stats(self, setup_name, variation_string="", mesh_path=None, setup_type="CG"):
        """Export mesh statistics to a file.

        Parameters
        ----------
        setup_name :str
            Setup name.
        variation_string : str, optional
            Variation list. The default is ``""``.
        mesh_path : str, optional
            Full path to the mesh statistics file. The default is ``None``, in which
            case the working directory is used.
        setup_type : str, optional
            Setup type in Q3D. Options are ``"CG"``, ``"AC RL"``, and ``"DC RL"``. The
            default is ``"CG"``.

        Returns
        -------
        str
            File path.

        References
        ----------
        >>> oDesign.ExportMeshStats
        """
        if not mesh_path:
            mesh_path = os.path.join(self.working_directory, "meshstats.ms")
        self.odesign.ExportMeshStats(setup_name, variation_string, setup_type, mesh_path)
        return mesh_path

    @pyaedt_function_handler()
    def edit_sources(
        self,
        cg=None,
        acrl=None,
        dcrl=None,
    ):
        """Set up the source loaded for Q3D or Q2D in multiple sources simultaneously.

        Parameters
        ----------
        cg : dict, optional
            Dictionary of input sources to modify the module and phase of a CG solution.
            Dictionary values can be:
            - 1 Value to set up ``0deg`` as the default
            - 2 Values tuple or list (magnitude and phase)
        acrl : dict, optional
            Dictionary of input sources to modify the module and phase of an ACRL solution.
            Dictionary values can be:
            - 1 Value to set up 0deg as the default
            - 2 Values tuple or list (magnitude and phase)
        dcrl : dict, optional
            Dictionary of input sources to modify the module and phase of a DCRL solution, This
            parameter is only available for Q3D. Dictionary values can be:
            - 1 Value to set up ``0deg`` as the default
            - 2 Values tuple or list (magnitude and phase)

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.

        Examples
        --------
        >>> sources_cg = {"Box1": ("1V", "0deg"), "Box1_2": "1V"}
        >>> sources_acrl = {"Box1:Source1": ("5A", "0deg")}
        >>> sources_dcrl = {"Box1_1:Source2": ("5V", "0deg")}
        >>> hfss.edit_sources(sources_cg, sources_acrl, sources_dcrl)
        """
        setting_AC = []
        setting_CG = []
        setting_DC = []
        if cg:
            net_list = ["NAME:Source Names"]
            if self.default_solution_type == "Q3D Extractor":
                excitation = self.nets
            else:
                excitation = self.excitations

            for key, value in cg.items():
                if key not in excitation:
                    self.logger.error("Not existing net " + key)
                    return False
                else:
                    net_list.append(key)

            if self.default_solution_type == "Q3D Extractor":
                value_list = ["NAME:Source Values"]
                phase_list = ["NAME:Source Values"]
            else:
                value_list = ["NAME:Magnitude"]
                phase_list = ["NAME:Phase"]

            for key, vals in cg.items():
                if isinstance(vals, str):
                    value = vals
                    phase = "0deg"
                else:
                    value = vals[0]
                    if len(vals) == 1:
                        phase = "0deg"
                    else:
                        phase = vals[1]
                value_list.append(value)
                phase_list.append(phase)
            if self.default_solution_type == "Q3D Extractor":
                setting_CG = ["NAME:Cap", "Value Type:=", "N", net_list, value_list, phase_list]
            else:
                setting_CG = ["NAME:CGSources", net_list, value_list, phase_list]
        if acrl:
            source_list = ["NAME:Source Names"]
            unit = "V"
            for key, value in acrl.items():
                excitation = self.excitations
                if key not in excitation:
                    self.logger.error("Not existing excitation " + key)
                    return False
                else:
                    source_list.append(key)
            if self.default_solution_type == "Q3D Extractor":
                value_list = ["NAME:Source Values"]
                phase_list = ["NAME:Source Values"]
            else:
                value_list = ["NAME:Magnitude"]
                phase_list = ["NAME:Phase"]
            for key, vals in acrl.items():
                if isinstance(vals, str):
                    magnitude = decompose_variable_value(vals)
                    value = vals
                    phase = "0deg"
                else:
                    value = vals[0]
                    magnitude = decompose_variable_value(value)
                    if len(vals) == 1:
                        phase = "0deg"
                    else:
                        phase = vals[1]
                if magnitude[1]:
                    unit = magnitude[1]
                else:
                    value += unit

                value_list.append(value)
                phase_list.append(phase)

            if self.default_solution_type == "Q3D Extractor":
                setting_AC = ["NAME:AC", "Value Type:=", unit, source_list, value_list]
            else:
                setting_AC = ["NAME:RLSources", source_list, value_list, phase_list]
        if dcrl and self.default_solution_type == "Q3D Extractor":
            unit = "V"
            source_list = ["NAME:Source Names"]
            for key, value in dcrl.items():
                excitation = self.excitations
                if key not in excitation:
                    self.logger.error("Not existing excitation " + key)
                    return False
                else:
                    source_list.append(key)
            if self.default_solution_type == "Q3D Extractor":
                value_list = ["NAME:Source Values"]
            else:
                value_list = ["NAME:Magnitude"]
            for key, vals in dcrl.items():
                magnitude = decompose_variable_value(vals)
                if magnitude[1]:
                    unit = magnitude[1]
                else:
                    vals += unit
                if isinstance(vals, str):
                    value = vals
                else:
                    value = vals[0]
                value_list.append(value)
            setting_DC = ["NAME:DC", "Value Type:=", unit, source_list, value_list]

        if self.default_solution_type == "Q3D Extractor":
            self.osolution.EditSources(setting_AC, setting_CG, setting_DC)
        else:
            self.osolution.EditSources(setting_CG, setting_AC)

        return True


class Q3d(QExtractor, object):
    """Provides the Q3D app interface.

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
    non_graphical : bool, optional
        Whether to launch AEDT in non-graphical mode. The default
        is ``False``, in which case AEDT is launched in graphical mode.
        This parameter is ignored when a script is launched within AEDT.
    new_desktop_session : bool, optional
        Whether to launch an instance of AEDT in a new thread, even if
        another instance of the ``specified_version`` is active on the
        machine. The default is ``True``. This parameter is ignored when
        a script is launched within AEDT.
    close_on_exit : bool, optional
        Whether to release AEDT on exit. The default is ``False``.
    student_version : bool, optional
        Whether to open the AEDT student version. The default is ``False``.
        This parameter is ignored when a script is launched within AEDT.
    machine : str, optional
        Machine name to connect the oDesktop session to. This works only in
        2022 R2 and later. The remote server must be up and running with the
        command `"ansysedt.exe -grpcsrv portnum"`. If the machine is `"localhost"`,
        the server also starts if not present.
    port : int, optional
        Port number on which to start the oDesktop communication on an already
        existing server. This parameter is ignored when a new server is created.
        It works only in 2022 R2 and later. The remote server must be up and
        running with the command `"ansysedt.exe -grpcsrv portnum"`.
    aedt_process_id : int, optional
        Process ID for the instance of AEDT to point PyAEDT at. The default is
        ``None``. This parameter is only used when ``new_desktop_session = False``.

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
        machine="",
        port=0,
        aedt_process_id=None,
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
            machine,
            port,
            aedt_process_id,
        )
        self.MATRIXOPERATIONS = MATRIXOPERATIONSQ3D()

    @property
    def nets(self):
        """Nets in a Q3D project.

        Returns
        -------
        List of nets in a Q3D project.

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

    @pyaedt_function_handler()
    def net_sources(self, net_name):
        """Check if a net has sources and return a list of source names.

        Parameters
        ----------
        net_name : str
            Name of the net to search for.

        Returns
        -------
        List
            List of source names.

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

    @pyaedt_function_handler()
    def net_sinks(self, net_name):
        """Check if a net has sinks and return a list of sink names.

        Parameters
        ----------
        net_name : str
            Name of the net to search for.

        Returns
        -------
        List
            List of sink names.

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

    @pyaedt_function_handler()
    def auto_identify_nets(self):
        """Identify nets automatically.

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

    @pyaedt_function_handler()
    def assign_net(self, objects, net_name=None, net_type="Signal"):
        """Assign a net to a list of objects.

        Parameters
        ----------
        objects : list, str
            List of objects to assign the net to. It can be a single object.
        net_name : str, optional
            Name of the net. The default is ```None``, in which case the
            default name is used.
        net_type : str, bool
            Type of net to create. Options are ``"Signal"``, ``"Ground"`` and ``"Floating"``.
            The default is ``"Signal"``.

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

    @pyaedt_function_handler()
    def assign_source_to_objectface(self, object_name, axisdir=0, source_name=None, net_name=None):
        """Generate a source on a face of an object.

        The face ID is selected based on the axis direction. It is the face that
        has the maximum/minimum in this axis direction.

        Parameters
        ----------
        object_name : str, int
            Name of the object or face ID.
        axisdir : int, optional
            Initial axis direction. Options are ``0`` to ``5``. The default is ``0``.
        source_name : str, optional
            Name of the source. The default is ``None``.
        net_name : str, optional
            Name of the net. The default is ``None``, in which case the ``object_name`` is considered.

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

    @pyaedt_function_handler()
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
        sheetname = self.modeler.convert_to_selections(sheetname, True)
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

    @pyaedt_function_handler()
    def assign_sink_to_objectface(self, object_name, axisdir=0, sink_name=None, net_name=None):
        """Generate a sink on a face of an object.

        The face ID is selected based on the axis direction. It is the face that has
        the maximum or minimum in this axis direction.

        Parameters
        ----------
        object_name : str, int
            Name of the object or face ID.
        axisdir : int, optional
            Initial axis direction. Options are ``0`` to ``5``. The default is ``0``.
        sink_name : str, optional
            Name of the sink. The default is ``None``.
        net_name : str, optional
            Name of the net. The default is ``None``, in which case the ``object_name`` is considered.

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

    @pyaedt_function_handler()
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
        sheetname = self.modeler.convert_to_selections(sheetname, True)
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

    @pyaedt_function_handler()
    def create_frequency_sweep(self, setupname, units, freqstart, freqstop, freqstep=None, sweepname=None):
        """Create a frequency sweep.

        Parameters
        ----------
        setupname : str
            Name of the setup that is attached to the sweep.
        units : str
            Units of the frequency. For example, ``"MHz"`` or
            ``"GHz"``. The default is ``"GHz"``.
        freqstart :
            Starting frequency of the sweep.
        freqstop :
            Stopping frequency of the sweep.
        freqstep : optional
            Frequency step point.
        sweepname : str, optional
            Name of the sweep. The default is ``None``, in which case the
            default name is used.

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

    @pyaedt_function_handler()
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
            a single-point sweep is performed.
        freqstep : float, optional
            Step point for the discrete frequency. If ``None``,
            11 points are created.
        units : str, optional
            Units of the discrete frequency. For example, ``"MHz"`` or
            ``"GHz"``. The default is ``"GHz"``.
        sweepname : str, optional
            Name of the sweep. The default is ``None``, in which case
            the default name is used.
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
                        self.logger.warning("Sweep %s already present. Rename and retry.", sweepname)
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

    @pyaedt_function_handler()
    def set_material_thresholds(
        self, insulator_threshold=None, perfect_conductor_threshold=None, magnetic_threshold=None
    ):
        """Set material threshold.

        Parameters
        ----------
        insulator_threshold : float, optional
            Threshold for the insulator or conductor. The default is "None", in which
            case the threshold is set to 10000.
        perfect_conductor_threshold : float, optional
            Threshold that decides whether a conductor is perfectly conducting. This value
            must be higher than the value for the insulator threshold. The default is ``None``,
            in which case the value is set to 1E+030.
        magnetic_threshold : float, optional
            Threshold that decides whether a material is magnetic. The default is "None",
            in which case the value is set to 1.01.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.
        """
        try:
            if not insulator_threshold:
                insulator_threshold = 10000
            if not perfect_conductor_threshold:
                perfect_conductor_threshold = float("1E+30")
            else:
                if perfect_conductor_threshold < insulator_threshold:
                    msg = "Perfect conductor threshold must be higher than insulator threshold."
                    raise ValueError(msg)
            if not magnetic_threshold:
                magnetic_threshold = 1.01

            if not is_ironpython and not settings.use_grpc_api:
                insulator_threshold = np.longdouble(insulator_threshold)
                perfect_conductor_threshold = np.longdouble(perfect_conductor_threshold)
                magnetic_threshold = np.longdouble(magnetic_threshold)

            self.oboundary.SetMaterialThresholds(insulator_threshold, perfect_conductor_threshold, magnetic_threshold)
            return True
        except:
            return False


class Q2d(QExtractor, object):
    """Provides the Q2D app interface.

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
        parameter is ignored when a script is launched within AEDT.
    non_graphical : bool, optional
        Whether to launch AEDT in non-graphical mode. The default
        is ``False``, in which case AEDT is launched in graphical mode.
        This parameter is ignored when a script is launched within AEDT.
    new_desktop_session : bool, optional
        Whether to launch an instance of AEDT in a new thread, even if
        another instance of the ``specified_version`` is active on the
        machine. The default is ``True``. This parameter is ignored
        when a script is launched within AEDT.
    close_on_exit : bool, optional
        Whether to release AEDT on exit. The default is ``False``.
    student_version : bool, optional
        Whether to open the AEDT student version. This parameter is
        ignored when a script is launched within AEDT.
    machine : str, optional
        Machine name to connect the oDesktop session to. This works only in 2022 R2
        and later. The remote server must be up and running with the command
        `"ansysedt.exe -grpcsrv portnum"`. If the machine is `"localhost"`,
        the server also starts if not present.
    port : int, optional
        Port number on which to start the oDesktop communication on an already existing server.
        This parameter is ignored when creating a new server. It works only in 2022 R2 or later.
        The remote server must be up and running with the command `"ansysedt.exe -grpcsrv portnum"`.
    aedt_process_id : int, optional
        Process ID for the instance of AEDT to point PyAEDT at. The default is
        ``None``. This parameter is only used when ``new_desktop_session = False``.

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
        machine="",
        port=0,
        aedt_process_id=None,
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
            machine,
            port,
            aedt_process_id,
        )
        self.MATRIXOPERATIONS = MATRIXOPERATIONSQ2D()

    @pyaedt_function_handler()
    def create_rectangle(self, position, dimension_list, name="", matname=""):
        """
        Create a rectangle.

        Parameters
        ----------
        position : list
            List of ``[x, y]`` coordinates for the starting point of the rectangle.
        dimension_list : list
            List of ``[width, height]`` dimensions.
        name : str, optional
            Name of the rectangle. The default is ``None``, in which case
            the default name is assigned.
        matname : str, optional
            Name of the material. The default is ``None``, in which case
            the default material is used.

        Returns
        -------
        :class:`pyaedt.modeler.Object3d.Object3d`
            3D object.

        References
        ----------

        >>> oEditor.CreateRectangle
        """
        return self.modeler.create_rectangle(position, dimension_list=dimension_list, name=name, matname=matname)

    @pyaedt_function_handler()
    def assign_single_signal_line(self, target_objects, name="", solve_option="SolveInside", thickness=None, unit="um"):
        """Assign the conductor type to sheets.

        Parameters
        ----------
        target_objects : list
            List of Object3D.
        name : str, optional
            Name of the conductor. The default is ``""``, in which case the default name is used.
        solve_option : str, optional
            Method for solving. Options are ``"SolveInside"``, ``"SolveOnBoundary"``, and ``"Automatic"``.
            The default is ``"SolveInside"``.
        thickness : float, optional
            Conductor thickness. The default is ``None``, in which case the conductor thickness
            is obtained by dividing the conductor's area by its perimeter (A/p). If multiple
            conductors are selected, the average conductor thickness is used.
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

    @pyaedt_function_handler()
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
        Assign the conductor type to sheets.

        Parameters
        ----------
        target_objects : list
            List of Object3D.
        name : str, optional
            Name of the conductor. The default is ``""``, in which case the default name is used.
        conductor_type : str
            Type of the conductor. Options are ``"SignalLine"`` and ``"ReferenceGround"``. The default is
            ``"SignalLine"``.
        solve_option : str, optional
            Method for solving. Options are ``"SolveInside"``, ``"SolveOnBoundary"``, and ``"Automatic"``.
            The default is ``"SolveInside"``.
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

    @pyaedt_function_handler()
    def assign_huray_finitecond_to_edges(self, edges, radius, ratio, unit="um", name=""):
        """
        Assign the Huray surface roughness model to edges.

        Parameters
        ----------
        edges :
        radius :
        ratio :
        unit : str, optional
            The default is ``"um"``.
        name : str, optional
            The default is ``""``, in which case the default name is used.

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

        a = self.modeler.convert_to_selections(edges, True)

        props = OrderedDict({"Edges": a, "UseCoating": False, "Radius": ra, "Ratio": str(ratio)})

        bound = BoundaryObject(self, name, props, "Finite Conductivity")
        if bound.create():
            self.boundaries.append(bound)
            return bound
        return False

    @pyaedt_function_handler()
    def auto_assign_conductors(self):
        """Automatically assign conductors to signal lines.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.
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

    @pyaedt_function_handler()
    def export_w_elements(self, analyze=False, export_folder=None):
        """Export all W-elements to files.

        Parameters
        ----------
        analyze : bool, optional
            Whether to analyze before export. Solutions must be present for the design.
            The default is ``False``.
        export_folder : str, optional
            Full path to the folder to export files to. The default is ``None``, in
            which case the working directory is used.

        Returns
        -------
        list
            List of all exported files.
        """
        exported_files = []
        if not export_folder:
            export_folder = self.working_directory
        if not os.path.exists(export_folder):
            os.makedirs(export_folder)
        if analyze:
            self.analyze_all()
        setups = self.oanalysis.GetSetups()

        for s in setups:
            sweeps = self.oanalysis.GetSweeps(s)
            if not sweeps:
                sweeps = ["LastAdaptive"]
            for sweep in sweeps:
                variation_array = self.list_of_variations(s, sweep)
                solution_name = "{} : {}".format(s, sweep)
                if len(variation_array) == 1:
                    try:
                        export_file = "{}_{}_{}.sp".format(self.project_name, s, sweep)
                        export_path = os.path.join(export_folder, export_file)
                        subckt_name = "w_{}".format(self.project_name)
                        self.oanalysis.ExportCircuit(
                            solution_name,
                            variation_array[0],
                            export_path,
                            [
                                "NAME:CircuitData",
                                "MatrixName:=",
                                "Original",
                                "NumberOfCells:=",
                                "1",
                                "UserHasChangedSettings:=",
                                True,
                                "IncludeCap:=",
                                False,
                                "IncludeCond:=",
                                False,
                                ["NAME:CouplingLimits", "CouplingLimitType:=", "None"],
                                "IncludeR:=",
                                False,
                                "IncludeL:=",
                                False,
                                "ExportDistributed:=",
                                True,
                                "LumpedLength:=",
                                "1meter",
                                "RiseTime:=",
                                "1e-09s",
                            ],
                            subckt_name,
                            "WElement",
                            0,
                        )
                        exported_files.append(export_path)
                        self.logger.info("Exported W-element: %s", export_path)
                    except:  # pragma: no cover
                        self.logger.warning("Export W-element failed")
                else:
                    varCount = 0
                    for variation in variation_array:
                        varCount += 1
                        try:
                            export_file = "{}_{}_{}_{}.sp".format(self.project_name, s, sweep, varCount)
                            export_path = os.path.join(export_folder, export_file)
                            subckt_name = "w_{}_{}".format(self.project_name, varCount)
                            self.oanalysis.ExportCircuit(
                                solution_name,
                                variation,
                                export_path,
                                [
                                    "NAME:CircuitData",
                                    "MatrixName:=",
                                    "Original",
                                    "NumberOfCells:=",
                                    "1",
                                    "UserHasChangedSettings:=",
                                    True,
                                    "IncludeCap:=",
                                    False,
                                    "IncludeCond:=",
                                    False,
                                    ["NAME:CouplingLimits", "CouplingLimitType:=", "None"],
                                    "IncludeR:=",
                                    False,
                                    "IncludeL:=",
                                    False,
                                    "ExportDistributed:=",
                                    True,
                                    "LumpedLength:=",
                                    "1meter",
                                    "RiseTime:=",
                                    "1e-09s",
                                ],
                                subckt_name,
                                "WElement",
                                0,
                            )
                            exported_files.append(export_path)
                            self.logger.info("Exported W-element: %s", export_path)
                        except:  # pragma: no cover
                            self.logger.warning("Export W-element failed")
        return exported_files

    @pyaedt_function_handler()
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
            ``True`` when successful, ``False`` when failed.
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
