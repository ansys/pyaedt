"""This module contains these Maxwell classes: ``Maxwell``, ``Maxwell2d``, and ``Maxwell3d``."""

from __future__ import absolute_import
import math
import os
import json
import re
import io
from .application.Analysis2D import FieldAnalysis2D
from .application.Analysis3D import FieldAnalysis3D
from .desktop import exception_to_desktop
from .generic.general_methods import generate_unique_name, aedt_exception_handler
from .modules.Boundary import BoundaryObject
from collections import OrderedDict

unit_val = {
    "": 1.0,
    "uV": 1e-6,
    "mV": 1e-3,
    "V": 1.0,
    "kV": 1e3,
    "MegV": 1e6,
    "ns": 1e-9,
    "us": 1e-6,
    "ms": 1e-3,
    "s": 1.0,
    "min": 60,
    "hour": 3600,
    "rad": 1.0,
    "deg": math.pi / 180,
    "Hz": 1.0,
    "kHz": 1e3,
    "MHz": 1e6,
    "nm": 1e-9,
    "um": 1e-6,
    "mm": 1e-3,
    "cm": 1e-2,
    "dm": 1e-1,
    "meter": 1.0,
    "km": 1e3

}

# Utility scripts
resynch_maxwell2D_control_program_for_design = '''
from pyaedt.Desktop import Desktop
from pyaedt.Maxwell import Maxwell2D
design_name = os.getenv('design')
setup = os.getenv('setup')

with Desktop() as d:
    mxwl = Maxwell2D(designname=design_name, setup_name=setup)
    mxwl.setup_ctrlprog(keep_modifications=True )
    oDesktop.AddMessage( mxwl.project_name, mxwl.design_name, 0, "Successfully updated project definitions")
    mxwl.save_project()
'''


def float_units(val_str, units=""):
    """

    Parameters
    ----------
    val_str : str
        
    units : str, optional
         The default is ``""``.

    Returns
    -------

    """
    if not units in unit_val:
        raise Exception("Specified unit string " + units + " not known!")

    loc = re.search('[a-zA-Z]', val_str)
    try:
        b = loc.span()[0]
        var = [float(val_str[0:b]), val_str[b:]]
        val = var[0] * unit_val[var[1]]
    except:
        val = float(val_str)

    val = val / unit_val[units]
    return val


class Maxwell(object):
    """Maxwell class.
    
    .. note::
       This class contains all methods that are common to Maxwell 2D and Maxwell 3D.

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
    specified_version: str, optional
        Version of AEDT to use. The default is ``None``, in which case
        the active version or latest installed version is used.
    NG : bool, optional
        Whether to run AEDT in the non-graphical mode. The default
        is ``False``, in which case AEDT launches in the graphical mode.
    AlwaysNew : bool, optional
        Whether to launch an instance of AEDT in a new thread, even if
        another instance of the ``specified_version`` is active on the
        machine. The default is ``True``.
    release_on_exit : bool, optional
        Whether to release AEDT on exit. The default is ``False``.

    Returns
    -------

    """

    def __init__(self):
        pass

    @property
    def odefinition_manager(self):
        """Definition manager. """
        return self.oproject.GetDefinitionManager()

    @property
    def omaterial_manager(self):
        """Material manager."""
        return self.odefinition_manager.GetManager("Material")

    '''
    @property
    def oeditor(self):
        """Editor."""
        return self.odesign.SetActiveEditor("3D Modeler")
    '''

    @property
    def symmetry_multiplier(self):
        """Symmetry multiplier."""
        omodule = self._odesign.GetModule("ModelSetup")
        return int(omodule.GetSymmetryMultiplier())

    @property
    def windings(self):
        """Windings."""
        oModule = self.odesign.GetModule("BoundarySetup")
        windings = oModule.GetExcitationsOfType('Winding Group')
        return list(windings)

    @property
    def o_maxwell_parameters(self):
        """Maxwell parameters."""
        return self.odesign.GetModule("MaxwellParameterSetup")

    @property
    def design_file(self):
        """Design files."""
        design_file = os.path.join(self.working_directory, "design_data.json")
        return design_file

    @aedt_exception_handler
    def setup_ctrlprog(self, setupname, file_str=None, keep_modifications=False, python_interpreter=None, aedt_lib_dir=None):
        """Configure the transient design setup to run a specific control program.

        Parameters
        ----------
        setupname : str
            Name of the setup
        file_str : str, optional
            Name of the file. The default value is ``None``.
        keep_modifications : bool, optional
            Whether to save changes. The default value is ``False``.
        python_interpreter : optional
             The default value is ``None``.
        aedt_lib_dir : str, optional
             The default value is ``None``.

        Returns
        -------
        bool
            ``True`` when successful and ``False`` when failed.

        """

        self._py_file = setupname + ".py"
        ctl_path = self.working_directory
        ctl_file_compute = os.path.join(ctl_path, self._py_file)
        ctl_file = os.path.join(self.working_directory, self._py_file)

        if aedt_lib_dir:
            source_dir = aedt_lib_dir
        else:
            source_dir = self.pyaedt_dir

        if os.path.exists(ctl_file) and keep_modifications:
            with open(ctl_file, "r") as fi:
                existing_data = fi.readlines()
            with open(ctl_file, "w") as fo:
                first_line = True
                for line in existing_data:
                    if first_line:
                        first_line = False
                        if python_interpreter:
                            fo.write("#!{0}\n".format(python_interpreter))
                    if line.startswith("work_dir"):
                        fo.write("work_dir = r'{0}'\n".format(ctl_path))
                    elif line.startswith("lib_dir"):
                        fo.write("lib_dir = r'{0}'\n".format(source_dir))
                    else:
                        fo.write(line)
        else:
            if file_str is not None:
                with io.open(ctl_file, "w", newline='\n') as fo:
                    fo.write(file_str)
                assert os.path.exists(ctl_file), "Control Program file could not be created."

        self.oanalysis_setup.EditSetup(setupname,
                          [
                              "NAME:" + setupname,
                              "Enabled:=", True,
                              "UseControlProgram:=", True,
                              "ControlProgramName:=", ctl_file_compute,
                              "ControlProgramArg:=", "",
                              "CallCtrlProgAfterLastStep:=", True
                          ])

        return True

    # Set eddy effects
    @aedt_exception_handler
    def eddy_effects_on(self, object_list, activate=True):
        """Assign eddy effects on objects.

        Parameters
        ----------
        object_list : list
            List of objects.    
        activate : bool, optional
            Whether to activate. The default is ``True``.

        Returns
        -------

        """
        EddyVector = ["NAME:EddyEffectVector"]
        for obj in object_list:
            EddyVector.append([
                "NAME:Data",
                "Object Name:=", obj,
                "Eddy Effect:=", activate
            ])

        oModule = self.odesign.GetModule("BoundarySetup")
        oModule.SetEddyEffect(["NAME:Eddy Effect Setting", EddyVector])
        return True

    @aedt_exception_handler
    def assign_current(self, object_list, amplitude=1, phase="0deg", solid=True, swap_direction=False,
                       name=None):
        """Assign the source of the current.
        
        Parameters
        ----------
        object_list : list
            List of objects to assign to the source of the current.
        amplitude : float, optional
            The default is ``1``.
        phase : str, optional
            The default is ``"0deg"``.
        solid : bool, optional
            The default is ``True``.
        swap_direction : bool, optional
            The default is ``False``.
        name : str, optional
            The default is ``None``.

        Returns
        -------
        BoundaryObject
            Boundary object
            
        """

        amplitude = str(amplitude) + "A"

        if not name:
            name = generate_unique_name("Current")
        
        object_list = self.modeler._convert_list_to_ids(object_list)
        if type(object_list[0]) is int:
            props = OrderedDict(
                {"Faces": object_list, "Current": amplitude, "IsSolid": solid, "Point out of terminal": swap_direction})
        else:
            props = OrderedDict(
                {"Objects": object_list, "Current": amplitude,"Phase":phase, "IsSolid": solid, "Point out of terminal": swap_direction})
        bound = BoundaryObject(self, name, props, "Current")
        if bound.create():
            self.boundaries.append(bound)
            return bound
        return False

    @aedt_exception_handler
    def assign_voltage(self, face_list, amplitude=1, name=None):
        """Assign a voltage source to a list of faces.

        Parameters
        ----------
        face_list : list
            List of faces.
        amplitude : float, optional
            Voltage amplitude in mV. The default is ``1``.
        name : str, optional
            Name of the boundary. The default is ``None``.

        Returns
        -------
        BoundaryObject
            Boundary object.

        """

        amplitude = str(amplitude) + "mV"

        if not name:
            name = generate_unique_name("Voltage")
        face_list = self.modeler._convert_list_to_ids(face_list)

        # if type(face_list) is not list and type(face_list) is not tuple:
        #     face_list = [face_list]
        props = OrderedDict({"Faces": face_list, "Voltage": amplitude})
        bound = BoundaryObject(self, name, props, "Voltage")
        if bound.create():
            self.boundaries.append(bound)
            return bound
        return False

    @aedt_exception_handler
    def assign_voltage_drop(self, face_list, amplitude=1, swap_direction=False, name=None):
        """Assign a voltage drop to a list of faces.

        Parameters
        ----------
        face_list : list
            List of faces.
        amplitude : float, optional
            Voltage amplitude in mV. The default is ``1``.
        swap_direction : bool, optional
            The default value is ``False``.
        name : str, optional
            Name of the boundary. The default is ``None``.

        Returns
        -------
        BoundaryObject
            Boundary object.

        """

        amplitude = str(amplitude) + "mV"

        if not name:
            name = generate_unique_name("VoltageDrop")
        face_list = self.modeler._convert_list_to_ids(face_list)

        props = OrderedDict({"Faces": face_list, "Voltage Drop": amplitude, "Point out of terminal": swap_direction})
        bound = BoundaryObject(self, name, props, "VoltageDrop")
        if bound.create():
            self.boundaries.append(bound)
            return bound
        return False

    @aedt_exception_handler
    def assign_winding(self, coil_terminals=None, winding_type="Current", current_value=1, res=0, ind=0, voltage=0,
                       parallel_branches=1, name=None):
        """Assign a winding to a Maxwell design.

        Parameters
        ----------
        coil_terminals : list, optional
            List of faces to create the coil terminal on.
            The default is ``None``.
        winding_type : str, optional
            Type of the winding. Options are ``"Current"``, ``"Voltage"``, 
            and ``"External"``. The default is ``"Current"``.
        current_value : float, optional
            Value of the current in amperes. The default is ``1``.
        res : float, optional
            Resistance in ohms. The default is ``0``.
        ind : float, optional
            Henry. The default is ``0``.
        voltage : float, optional
            Voltage. The default is ``0``.
        parallel_branches : int, optional
            The default is ``1``.
        name : str, optional
            Name to assign the winding. The default is ``None``.

        Returns
        -------
        BoundaryObject
            Bounding object for the winding; otherwise only the bounding object.

        """

        if not name:
            name = generate_unique_name("Winding")

        props = OrderedDict({"Type": winding_type, "IsSolid": True, "Current": str(current_value) + "A",
                             "Resistance": str(res) + "ohm", "Inductance": str(ind) + "H",
                             "Voltage": str(voltage) + "V", "ParallelBranchesNum": str(parallel_branches)})
        bound = BoundaryObject(self, name, props, "Winding")
        if bound.create():
            self.boundaries.append(bound)
            if type(coil_terminals) is not list:
                coil_terminals = [coil_terminals]
            coil_names=[]
            for coil in coil_terminals:
                c=self.assign_coil(coil)
                if c:
                    coil_names.append(c.name)

            self.add_winding_coils(bound.name, coil_names)
            return bound
        return False

    @aedt_exception_handler
    def add_winding_coils(self, windingname, coil_names):
        """Add coils to the winding.

        Parameters
        ----------
        windingname : str
            Name of the winding.
        coil_names : list
            List of the one or more coil names.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.   

        """
        if self.modeler._is3d:
            self.oboundary.AddWindingTerminals(windingname, coil_names)
        else:
            self.oboundary.AddWindingCoils(windingname, coil_names)
        return True

    @aedt_exception_handler
    def assign_coil(self, input_object, conductor_number=1, polarity="Positive", name=None):
        """Assign coils to a list of objects or face IDs.

        Parameters
        ----------
        input_object : list
            List of objects or face IDs to input.
        conductor_number : int, optional
            Number of conductors. The default is ``1``.
        polarity : str, optional
            Type of the polarity. The default is ``"Positive"``.         
        name : str, optional
             The default is ``None``.

        Returns
        -------
        CoilObject
            Coil object.

        """
        if polarity == "Positive":
            point = False
        else:
            point = True

        input_object = self.modeler._convert_list_to_ids(input_object)

        if not name:
            name = generate_unique_name("Coil")

        if type(input_object[0]) is str:
            if self.modeler._is3d:
                props2 = OrderedDict(
                    {"Objects": input_object, "Conductor number": str(conductor_number), "Point out of terminal": point})
                bound = BoundaryObject(self, name, props2, "CoilTerminal")
            else:
                props2 = OrderedDict(
                    {"Objects": input_object, "Conductor number": str(conductor_number), "PolarityType": polarity})
                bound = BoundaryObject(self, name, props2, "Coil")
        else:
            if self.modeler._is3d:
                props2 = OrderedDict(
                    {"Faces": input_object, "Conductor number": str(conductor_number), "Point out of terminal": point})
                bound = BoundaryObject(self, name, props2, "CoilTerminal")

            else:
                self._messenger.add_warning_message("Face Selection is not allowed in Maxwell 2D. Provide a 2D object.")
                return False
        if bound.create():
            self.boundaries.append(bound)
            return bound
        return False

    @aedt_exception_handler
    def assign_force(self, input_object, reference_cs="Global", is_virtual=True, force_name=None):
        """
        Assign a force to one or more objects.

        Parameters
        ----------
        input_object : str, list
            One or more objects to assign the force to.
        reference_cs : str, optional
            The default is ``"Global"``.
        is_virtual : bool, optional
            Whether the force is virtual. The default is ``True.``
        force_name : str, optional
            Name of the force. The default is ``None``.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.
        
        """

        input_object = self.modeler._convert_list_to_ids(input_object, True)
        if not force_name:
            force_name = generate_unique_name("Force")
        if self.design_type == "Maxwell 3D":
            self.o_maxwell_parameters.AssignForce(
                [
                    "NAME:"+force_name,
                    "Reference CS:=", reference_cs,
                    "Is Virtual:="	, is_virtual,
                    "Objects:="		, input_object
                ])
        else:
            self.o_maxwell_parameters.AssignForce(
                [
                    "NAME:"+force_name,
                    "Reference CS:=", reference_cs,
                    "Objects:="		, input_object
                ])
        return True

    @aedt_exception_handler
    def assign_torque(self, input_object, reference_cs="Global", is_positive=True, is_virtual=True, axis="Z", torque_name=None):
        """
        Assign a torque to one or more objects.

        Parameters
        ----------
        input_object : str or list
           One or objects to assign the torque to
        reference_cs : str, optional
            The default is ``"Global"``.
        is_positive : bool, optional
            Whether the torque is positive. The default is ``True``. 
        is_virtual : bool, optional
            Whether the torque is virtual. The default is ``True``.
        axis : str, optional
            Axis to apply the torque to. The default is ``"Z"``.
        torque_name : str, optional
            Name of the torque. The default is ``None``.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.
        
        """

        input_object = self.modeler._convert_list_to_ids(input_object, True)
        if not torque_name:
            torque_name = generate_unique_name("Torque")
        if self.design_type == "Maxwell 3D":
            self.o_maxwell_parameters.AssignTorque(
                ["NAME:" + torque_name, "Is Virtual:=", is_virtual, "Coordinate System:=", reference_cs, "Axis:=", axis,
                 "Is Positive:=", is_positive, "Objects:=", input_object])
        else:
            self.o_maxwell_parameters.AssignTorque(
                ["NAME:" + torque_name, "Coordinate System:=", reference_cs,
                 "Is Positive:=", is_positive, "Objects:=", input_object])
        return True

    @aedt_exception_handler
    def assign_force(self, input_object, reference_cs="Global", is_virtual=True, force_name=None):
        """
        Assign a force to the selection.

        Parameters
        ----------
        input_object : str, list
        reference_cs : str, optional
        is_virtual : bool, optional
            Whether the force is virtual. The default is ``True``.
        force_name : str, optional
            Name of the force. The default is ``None``.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.
        
        """

        input_object = self.modeler._convert_list_to_ids(input_object, True)
        if not force_name:
            force_name = generate_unique_name("Force")
        self.o_maxwell_parameters.AssignForce(
            [
                "NAME:" + force_name,
                "Reference CS:=", reference_cs,
                "Is Virtual:=", is_virtual,
                "Objects:="	, input_object
            ])
        return True

    @aedt_exception_handler
    def solve_inside(self, name, activate=True):
        """Solve inside.

        Parameters
        ----------
        name : str
            
        activate : bool, optional
            The default value is ``True``.

        Returns
        -------

        """
        self.modeler.primitives[name].solve_inside = activate
        return True

    @aedt_exception_handler
    def analyse_from_zero(self):
        """Analyze from zero."""
        self.oanalysis.ResetSetupToTimeZero(self._setup)
        self.analyse_nominal()
        return True

    @aedt_exception_handler
    def set_initial_angle(self, motion_setup, val):
        """Set the initial angle.

        Parameters
        ----------
        motion_setup : str
            Name of the motion setup.
        val : 
            Value of the angle.

        Returns
        -------

        """
        self.odesign.ChangeProperty(
            [
                "NAME:AllTabs",
                [
                    "NAME:Maxwell2D",
                    [
                        "NAME:PropServers",
                        "ModelSetup:" + motion_setup
                    ],
                    [
                        "NAME:ChangedProps",
                        [
                            "NAME:Initial Position",
                            "Value:=", val
                        ]
                    ]
                ]
            ])
        return True

    def __enter__(self):
        return self

    def __exit__(self, ex_type, ex_value, ex_traceback):
        """ Push exit up to parent object Design """
        if ex_type:
            exception_to_desktop(self, ex_value, ex_traceback)


class Maxwell3d(Maxwell, FieldAnalysis3D, object):
    """Maxwell 3D application interface.

    This class allows you to connect to an existing Maxwell 3D design or create a
    new Maxwell 3D design if one does not exist.

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
    specified_version: str, optional
        Version of AEDT to use. The default is ``None``, in which case
        the active version or latest installed version is used.
    NG : bool, optional
        Whether to run AEDT in the non-graphical mode. The default
        is ``False``, in which case AEDT is launched in the graphical mode.
    AlwaysNew : bool, optional
        Whether to launch an instance of AEDT in a new thread, even if
        another instance of the ``specified_version`` is active on the
        machine. The default is ``True``.
    release_on_exit : bool, optional
        Whether to release AEDT on exit. The default is ``False``.
     student_version : bool, optional
        Whether open AEDT Student Version. The default is ``False``.

    Examples
    --------
    Create an instance of `Maxwell3d` and open the specified
    project, which is named ``myfile.aedt``.

    >>> from pyaedt import Maxwell3d
    >>> aedtapp = Maxwell3d("myfile.aedt")

    Create an instance of `Maxwell3d` using the 2021 R1 release and open
    the specified project, which is named ``myfile.aedt``.

    >>> aedtapp = Maxwell3d(specified_version="2021.1", projectname="myfile.aedt")

    """

    @property  # for legacy purposes
    def dim(self):
        """ """
        return '3D'

    def __init__(self, projectname=None, designname=None, solution_type=None, setup_name=None,
                 specified_version=None, NG=False, AlwaysNew=False, release_on_exit=False,student_version=False):
        """
        Initialize the ``Maxwell`` class.
        """
        FieldAnalysis3D.__init__(self, "Maxwell 3D", projectname, designname, solution_type, setup_name,
                                 specified_version, NG, AlwaysNew, release_on_exit, student_version)
        Maxwell.__init__(self)


class Maxwell2d(Maxwell, FieldAnalysis2D, object):
    """Maxwell 2D application interface.

    Allows you to connect to an existing Maxwell 2D design or create a
    new Maxwell 2D design if one does not exist.

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
    specified_version: str, optional
        Version of AEDT to use. The default is ``None``, in which case
        the active version or latest installed version is used.
    NG : bool, optional
        Whether to run AEDT in the non-graphical mode. The default
        is ``False``, in which case AEDT is launched in the graphical mode.
    AlwaysNew : bool, optional
        Whether to launch an instance of AEDT in a new thread, even if
        another instance of the ``specified_version`` is active on the
        machine. The default is ``True``.
    release_on_exit : bool, optional
        Whether to release AEDT on exit. The default is ``False``.
    student_version : bool, optional
        Whether open AEDT Student Version. The default is ``False``.

    Examples
    --------
    Create an instance of `Maxwell2d` and connect to an existing
    Maxwell 2D design or create a new Maxwell 2D design if one does
    not exist.

    >>> from pyaedt import Maxwell2d
    >>> aedtapp = Maxwell2d()

    Create an instance of `Maxwell2d` and link to a project named
    ``projectname``. If this project does not exist, create one with
    this name.

    >>> aedtapp = Maxwell2d(projectname)

    Create an instance of `Maxwell2d` and link to a design named
    ``designname`` in a project named ``projectname``.

    >>> aedtapp = Maxwell2d(projectname,designame)

    """

    @property  # for legacy purposes
    def dim(self):
        """Dimension."""
        return self.modeler.dimension

    @property
    def geometry_mode(self):
        """Geometry mode."""
        return self.odesign.GetGeometryMode()

    def __init__(self, projectname=None, designname=None, solution_type=None, setup_name=None,
                 specified_version=None, NG=False, AlwaysNew=False, release_on_exit=False, student_version=False):
        FieldAnalysis2D.__init__(self, "Maxwell 2D", projectname, designname, solution_type, setup_name,
                                 specified_version, NG, AlwaysNew, release_on_exit, student_version)
        Maxwell.__init__(self)

    def get_model_depth(self):
        """Get model depth."""
        if self.modeler.dimension == '2D':
            with open(self.project_file, 'r') as fi:
                design_str = "\t$begin 'Maxwell2DModel'"
                found_design = False
                found_correct_design = False
                item_str = "\t\tModelDepth='"
                for line in fi:
                    if not found_design:
                        if line.startswith(design_str):
                            found_design = True
                    else:
                        if line.startswith("\t\tName='"):
                            if self.design_name in line:
                                found_correct_design = True
                            else:
                                found_design = False
                    if found_correct_design:
                        if line.startswith(item_str):
                            break
                if found_correct_design:
                    value_str = line.replace(item_str, "").replace("'\n", "")
                    # TODO Still messy!
                    try:
                        a = float_units(value_str)
                    except:
                        a = self.variable_manager[value_str].value
                    return a
                else:
                    raise RuntimeError('Design data is not found by the get_model_depth function. Find and fix the inconsistency.')
        else:
            return None

    @aedt_exception_handler
    def generate_design_data(self, linefilter=None, objectfilter=None):
        """Generate a generic set of design data and store it in the extension directory as ``design_data.json``.

        Parameters
        ----------
        linefilter : optional
             The default is ``None``.
        objectfilter : optional
             The default is ``None``.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.

        """
        solid_bodies = self.modeler.solid_bodies
        if objectfilter:
            solid_ids = [i for i,j in self.modeler.primitives.object_id_dict.items() if j.name in objectfilter]
        else:
            solid_ids = [i for i in list(self.modeler.primitives.object_id_dict.keys())]
        model_depth = self.get_model_depth()
        self.design_data = {
            "Project Directory": self.project_path,
            "Working Directory": self.working_directory,
            "Library Directories": self.library_list,
            "Dimension": self.modeler.dimension,
            "GeoMode": self.geometry_mode,
            "ModelUnits": self.modeler.model_units,
            "Symmetry": self.symmetry_multiplier,
            "ModelDepth": model_depth,
            "ObjectList": solid_ids,
            "LineList": self.modeler.vertex_data_of_lines(linefilter),
            "VarList": self.variable_manager.variable_names,
            "Setups": self.existing_analysis_setups,
            "MaterialProperties": self.get_object_material_properties(solid_bodies)
        }

        design_file = os.path.join(self.working_directory, "design_data.json")
        with open(design_file, 'w') as fps:
            json.dump(self.design_data, fps, indent=4)
        return True

    @aedt_exception_handler
    def read_design_data(self):
        """Read back the design data as a dictionary."""
        design_file = os.path.join(self.working_directory, "design_data.json")
        with open(design_file, 'r') as fps:
            design_data = json.load(fps)
        return design_data

    @aedt_exception_handler
    def assign_balloon(self, edge_list, bound_name= None):
        """Assign a balloon boundary to a list of edges.

        Parameters
        ----------
        edge_list: list
            List of edges.
        bound_name: str, optional
            Name of the boundary. The default is ``None``.

        Returns
        -------
        BoundaryObject
            Boundary object.

        """
        edge_list = self.modeler._convert_list_to_ids(edge_list)

        if not bound_name:
            bound_name = generate_unique_name("Balloon")

        props2 = OrderedDict(
            {"Edges": edge_list})
        bound = BoundaryObject(self, bound_name, props2, "Balloon")

        if bound.create():
            self.boundaries.append(bound)
            return bound
        return False

    @aedt_exception_handler
    def assign_vector_potential(self, input_edge, vectorvalue=0, bound_name=None):
        """Assign coils to a list of objects or face IDs.

        Parameters
        ----------
        input_edge : list
            List of edges or edge IDs to input.
        vectorvalue : float, optional
            Value of the vector. The default is ``0``.
        bound_name : str, optional
            Name of the boundary. The default is ``None``.

        Returns
        -------
        BoundaryObject
            Vector Potential Object

        """
        input_edge= self.modeler._convert_list_to_ids(input_edge)

        if not bound_name:
            bound_name=generate_unique_name("Vector")
        if type(input_edge[0]) is str:
            props2 = OrderedDict(
                {"Objects": input_edge, "Value": str(vectorvalue), "CoordinateSystem": ""})
        else:
            props2 = OrderedDict(
                {"Edges": input_edge, "Value": str(vectorvalue), "CoordinateSystem": ""})
        bound = BoundaryObject(self, bound_name, props2, "VectorPotential")

        if bound.create():
            self.boundaries.append(bound)
            return bound
        return False
