"""
This module contains all Maxwell 2D/3D functionalities in the ''maxwell`` class.


Examples
--------

Create an instance of ``Maxwell2d`` and connect to an existing Maxwell 2D design or create a new Maxwell 2D design if one does not exist.

>>> aedtapp = Maxwell2d()

Create an instance of ``Maxwell2d`` and link to a project named ``projectname``. If this project does not exist, create one with this name.

>>> aedtapp = Maxwell2d(projectname)

Create an instance of ``Maxwell2d`` and link to a design named ``designname`` in a project named ``projectname``.

>>> aedtapp = Maxwell2d(projectname,designame)

Create an instance of ``Maxwell3d`` and open the specified project.

>>> aedtapp = Maxwell3d("myfile.aedt")

Create an instance of Maxwell using the 2021 R1 release and open the specified project, which is named ``myfile.aedt``.

>>> aedtapp = Maxwell3d(specified_version="2021.1", projectname="myfile.aedt")

"""

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
    """Class of common Maxwell functionalities.
    
    This class contains all methods that are common to 
    Maxwell 2D and Maxwell 3D.

    Parameters
    ----------
    projectname : str, optional
        Name of the project to select or the full path to the project or AEDTZ archive to open.
        The default is ``None``. If ``None``, try to get an active project and, if no projects are present, 
        create an empty project.
    designname : str, optional
        Name of the design to select. The default is ``None``. If ``None``, try to get an active design, and,
        if no designs are present, create an empty design.
    solution_type : str, optional
        Solution type to apply to the design.  The default is ``None``. If ``None``, the default type is applied.
    setup_name : str, optional
        Name of the setup to use as the nominal.  The default is ``None``.  If ``None``, the active setup 
        is used or nothing is used.

    Returns
    -------

    """

    def __init__(self):
        pass

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
    def windings(self):
        """ """
        oModule = self.odesign.GetModule("BoundarySetup")
        windings = oModule.GetExcitationsOfType('Winding Group')
        return list(windings)

    @property
    def design_file(self):
        """ """
        design_file = os.path.join(self.working_directory, "design_data.json")
        return design_file

    # Set eddy effects
    @aedt_exception_handler
    def eddy_effects_on(self, object_list, activate=True):
        """

        Parameters
        ----------
        object_list : list
            
        activate : bool, optional
             The default is ``True``.

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
                       name=None):  # Assign the current Source
        """

        Parameters
        ----------
        object_list : list
            List of objects to assign to the current source.
        amplitude : optional
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
        :class: BoundaryObject
            Boundary Object
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
        """Assign voltage source to the face list.

        Parameters
        ----------
        face_list : list
            List of objects.
        amplitude : float, optional
            Voltage amplitude in mV. The default is ``1``.
        name : str, optional
            Name of the boundary. The default is ``None``.

        Returns
        -------
        type
            Boundary Object

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
        """Assign voltage source to the face list.

        Parameters
        ----------
        face_list : list
            List of objects.
        amplitude : float, optional
            Voltage amplitude in mV. The default is ``1``.
        swap_direction : bool, optional
            The default value is ``False``.
        name : str, optional
            Name of the boundary. The default is ``None``.

        Returns
        -------
        type
            Boundary Object

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
        """Assign winding to Maxwell design.

        Parameters
        ----------
        coil_terminals : list, optional
            List of faces on which to create the coil terminal. 
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
        type
            bounding object for winding otherwise only bounding object

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
        """Add coils to winding.

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
        type
            Coil Object

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
                self.messenger.add_warning_error("Face Selection is not Allowed in Maxwell 2D. Please provide a 2D Object")
                return False
        if bound.create():
            self.boundaries.append(bound)
            return bound
        return False

    @aedt_exception_handler
    def solve_inside(self, name, activate=True):
        """

        Parameters
        ----------
        name : str
            
        activate : bool, optional
            The default value is ``True``.

        Returns
        -------

        """
        self.modeler.oeditor.ChangeProperty(
            [
                "NAME:AllTabs",
                [
                    "NAME:Geometry3DAttributeTab",
                    [
                        "NAME:PropServers",
                        name
                    ],
                    [
                        "NAME:ChangedProps",
                        [
                            "NAME:Solve Inside",
                            "Value:=", activate
                        ]
                    ]
                ]
            ])
        return True

    @aedt_exception_handler
    def analyse_from_zero(self):
        """ """
        self.oanalysis.ResetSetupToTimeZero(self._setup)
        self.analyse_nominal()
        return True

    @aedt_exception_handler
    def set_initial_angle(self, motion_setup, val):
        """

        Parameters
        ----------
        motion_setup :
            param val:
        val :
            

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
    """Maxwell 3D Object

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
         Solution type to apply to the design. The default is ``None``. If ``None`, the default type is applied.
     setup_name : str, optional
         The name of the setup to use as the nominal. The default is ``None``. If ``None``, the active setup 
         is used or nothing is used.
   
    Returns
    -------

    """

    @property  # for legacy purposes
    def dim(self):
        """ """
        return '3D'

    def __init__(self, projectname=None, designname=None, solution_type=None, setup_name=None,
                 specified_version=None, NG=False, AlwaysNew=True, release_on_exit=True):
        """
        Initialize the ``Maxwell`` class.
        """
        FieldAnalysis3D.__init__(self, "Maxwell 3D", projectname, designname, solution_type, setup_name,
                                 specified_version, NG, AlwaysNew, release_on_exit)
        Maxwell.__init__(self)

    @aedt_exception_handler
    def setup_ctrlprog(self, setup, py_file, file_str=None):
        """Configure the transient design setup to run a specific control program.

        Parameters
        ----------
        setup : str
            Name of the solution setup of the Maxwell design. For example, ``"Setup1"``.
            
        py_file : str, optional
            Name of the Python file that the Maxwell solver process copies to the temp directory and 
            renames to ``setup + ".ctrlprog"``.  For example, assume that ``py_file`` is defined as 
            ``"my_script.py"`` and that the solver setup is called ``"Setup1"``. The resulting file 
            in the temp directory is ``"Setup1.ctrlprog"``. For this reason, it is important to 
            instruct the operating system to use a python interpreter to run any file with the 
            extension ``".ctrlprog"``.
            
        file_str : str, optional
            Name of the python file to run at each timestep. The default is ``None``.

        Returns
        -------

        """
        py_file = os.path.join(self.working_directory, py_file).replace('\\', '\\\\')
        exe_file = r'C:\data\userlib\Toolkits\Maxwell3D\lib\PythonLauncher.exe'
        self._py_file = py_file
        oModule = self._odesign.GetModule("AnalysisSetup")
        oModule.EditSetup(setup,
                          [
                              "NAME:" + setup,
                              "Enabled:=", True,
                              "UseControlProgram:=", True,
                              "ControlProgramName:=", exe_file,
                              "ControlProgramArg:=", py_file,
                              "CallCtrlProgAfterLastStep:=", True
                          ])
        self.save_project()
        if file_str is not None:
            ctl_file = os.path.join(self.working_directory, self._py_file)
            with open(ctl_file, "w") as fo:
                fo.write(file_str)
        return True


class Maxwell2d(Maxwell, FieldAnalysis2D, object):
    """Maxwell 2D Object

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
         Solution type to apply to the design. The default is ``None``. If ``None`, the default type is applied.
     setup_name : str, optional
         The name of the setup to use as the nominal. The default is ``None``. If ``None``, the active setup 
         is used or nothing is used.

    Returns
    -------

    """

    @property  # for legacy purposes
    def dim(self):
        """ """
        return self.modeler.dimension

    @property
    def geometry_mode(self):
        """ """
        return self.odesign.GetGeometryMode()

    def __init__(self, projectname=None, designname=None, solution_type=None, setup_name=None,
                 specified_version=None, NG=False, AlwaysNew=True, release_on_exit=True):
        FieldAnalysis2D.__init__(self, "Maxwell 2D", projectname, designname, solution_type, setup_name,
                                 specified_version, NG, AlwaysNew, release_on_exit)
        Maxwell.__init__(self)

    def get_model_depth(self):
        """ """
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
                    raise Exception('Design data not found by get_model_depth function - inconsistency !!!')
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

        """
        solid_bodies = self.modeler.solid_bodies
        solid_ids = self.modeler.solid_ids(objectfilter)
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
        """Reads back the design data as a dictionary"""
        design_file = os.path.join(self.working_directory, "design_data.json")
        with open(design_file, 'r') as fps:
            design_data = json.load(fps)
        return design_data

    @aedt_exception_handler
    def setup_ctrlprog(self, file_str=None, keep_modifications=False, python_interpreter=None,
                       pymxwl_module_location=None, working_directory=None, aedt_lib_dir=None):
        """Configure the transient design setup to run a specific control program.
              
        Parameters
        ----------
        file_str : str, optional
            The default value is ``None``.
        keep_modifications : bool, optional
            The default value is ``False``.
        python_interpreter : optional
             The default value is ``None``.
        pymxwl_module_location : optional
             The default value is ``None``.
        working_directory : str, optional
             The default value is ``None``.
        aedt_lib_dir : str, optional
             The default value is ``None``.

        Returns
        -------

        """
        setup = self.analysis_setup
        self._py_file = setup + ".py"
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

        assert os.path.exists(ctl_file_compute), "Control Program {} does not exist.".format(ctl_file_compute)
        oModule = self._odesign.GetModule("AnalysisSetup")
        oModule.EditSetup(setup,
                          [
                              "NAME:" + setup,
                              "Enabled:=", True,
                              "UseControlProgram:=", True,
                              "ControlProgramName:=", ctl_file_compute,
                              "ControlProgramArg:=", "",
                              "CallCtrlProgAfterLastStep:=", True
                          ])

        '''
        self._messenger.add_info_message(
            "Successfully set up the control program: {0}\nUsing pymxwl module located at:{1}".format(ctl_file,
                                                                                                   pymxwl_module_location),
            self.setup_des_name)
        '''  # send an info message to give the user a feedback about the generaed user control program file
        return True

    @aedt_exception_handler
    def assign_balloon(self, edge_list, bound_name= None):
        """
        Assign a balloon boundary to a list of edges.

        Parameters
        ----------
        edge_list: list
            List of edges.
        bound_name: str, optional
            Name of the boundary. The default is ``None``.

        Returns
        -------
        :class: BoundaryObject
            boundary object

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
            The value of the vector. The default is ``0``.
        bound_name : str, optional
            The name of the boundary. The default is ``None``.

        Returns
        -------
        type
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
