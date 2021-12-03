"""This module contains these Maxwell classes: `Maxwell`, `Maxwell2d`, and `Maxwell3d`."""

from __future__ import absolute_import
import os
import json
import io
from pyaedt.application.Analysis2D import FieldAnalysis2D
from pyaedt.application.Analysis3D import FieldAnalysis3D
from pyaedt.generic.DataHandlers import float_units
from pyaedt.generic.general_methods import generate_unique_name, aedt_exception_handler
from pyaedt.modules.Boundary import BoundaryObject
from collections import OrderedDict
from pyaedt.modeler.GeometryOperators import  GeometryOperators
from pyaedt.generic.constants import SOLUTIONS


class Maxwell(object):
    def __init__(self):
        self._odefinition_manager = self.materials.odefinition_manager
        self._omaterial_manager = self.materials.omaterial_manager
        self._o_maxwell_parameters = self.odesign.GetModule("MaxwellParameterSetup")
        pass

    @property
    def o_maxwell_parameters(self):
        """AEDT MaxwellParameterSetup Object.

        References
        ----------

        >>> oDesign.GetModule("MaxwellParameterSetup")
        """
        return self._o_maxwell_parameters

    @property
    def omodelsetup(self):
        """AEDT Model Setup Object.

        References
        ----------

        >>> oDesign.GetModule("ModelSetup")
        """
        if self.solution_type != "Transient":
            return None
        else:
            return self._odesign.GetModule("ModelSetup")

    @property
    def symmetry_multiplier(self):
        """Symmetry multiplier.

        References
        ----------

        >>> oModule.GetSymmetryMultiplier()
        """
        return int(self.omodelsetup.GetSymmetryMultiplier())

    @property
    def windings(self):
        """Windings.

        References
        ----------

        >>> oModule.GetExcitationsOfType("Winding Group")"""
        windings = self.oboundary.GetExcitationsOfType("Winding Group")
        return list(windings)

    @property
    def design_file(self):
        """Design file."""
        design_file = os.path.join(self.working_directory, "design_data.json")
        return design_file

    @aedt_exception_handler
    def change_inductance_computation(self, compute_transient_inductance=True, incremental_matrix=False):
        """Enable the inductance computation (for Transient Analysis) and sets the incremental_matrix.

        Parameters
        ----------
        compute_transient_inductance : bool
            Enable or disable the Inductance Calculation for Transient Analysis.
        incremental_matrix : bool
            Set the Inductance Calculation to Incremental if ``True``.

        Returns
        -------
        bool

        References
        ----------

        >>> oDesign.SetDesignSettings
        """
        self.odesign.SetDesignSettings(
            ["NAME:Design Settings Data", "ComputeTransientInductance:=", compute_transient_inductance,
             "ComputeIncrementalMatrix:=", incremental_matrix])
        return True

    @aedt_exception_handler
    def setup_ctrlprog(
        self, setupname, file_str=None, keep_modifications=False, python_interpreter=None, aedt_lib_dir=None
    ):
        """Configure the transient design setup to run a specific control program.

        Parameters
        ----------
        setupname : str
            Name of the setup
        file_str : str, optional
            Name of the file. The default value is ``None``.
        keep_modifications : bool, optional
            Whether to save the changes. The default value is ``False``.
        python_interpreter : str, optional
             The default value is ``None``.
        aedt_lib_dir : str, optional
             Full path to the ``PyAEDT`` directory. The default value is ``None``.

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
                with io.open(ctl_file, "w", newline="\n") as fo:
                    fo.write(file_str)
                assert os.path.exists(ctl_file), "Control Program file could not be created."

        self.oanalysis.EditSetup(
            setupname,
            [
                "NAME:" + setupname,
                "Enabled:=",
                True,
                "UseControlProgram:=",
                True,
                "ControlProgramName:=",
                ctl_file_compute,
                "ControlProgramArg:=",
                "",
                "CallCtrlProgAfterLastStep:=",
                True,
            ],
        )

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
            Whether to activate eddy effects. The default is ``True``.

        Returns
        -------
        bool
            ``True`` when successful and ``False`` when failed.

        References
        ----------

        >>> oModule.SetEddyEffect
        """
        EddyVector = ["NAME:EddyEffectVector"]
        for obj in object_list:
            EddyVector.append(["NAME:Data", "Object Name:=", obj, "Eddy Effect:=", activate])

        oModule = self.odesign.GetModule("BoundarySetup")
        oModule.SetEddyEffect(["NAME:Eddy Effect Setting", EddyVector])
        return True

    @aedt_exception_handler
    def assign_current(self, object_list, amplitude=1, phase="0deg", solid=True, swap_direction=False, name=None):
        """Assign the source of the current.

        Parameters
        ----------
        object_list : list
            List of objects to assign the current source to.
        amplitude : float, optional
            Voltage amplitude in mV. The default is ``1``.
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
        :class:`pyaedt.modules.Boundary.BoundaryObject`
            Boundary object.

        References
        ----------

        >>> oModule.AssignCurrent
        """
        if isinstance(amplitude, (int, float)):
            amplitude = str(amplitude) + "A"

        if not name:
            name = generate_unique_name("Current")

        object_list = self.modeler._convert_list_to_ids(object_list)
        if self.is3d:
            if type(object_list[0]) is int:
                props = OrderedDict(
                    {
                        "Faces": object_list,
                        "Current": amplitude,
                        "IsSolid": solid,
                        "Point out of terminal": swap_direction,
                    }
                )
            else:
                props = OrderedDict(
                    {
                        "Objects": object_list,
                        "Current": amplitude,
                        "Phase": phase,
                        "IsSolid": solid,
                        "Point out of terminal": swap_direction,
                    }
                )
        else:
            if type(object_list[0]) is str:
                props = OrderedDict({"Objects": object_list, "Current": amplitude, "IsPositive": swap_direction})
            else:
                self.logger.warning("Input has to be a 2D Object.")
                return False
        bound = BoundaryObject(self, name, props, "Current")
        if bound.create():

            self.boundaries.append(bound)
            return bound
        return False

    @aedt_exception_handler
    def assign_translate_motion(
            self,
            band_object,
            coordinate_system="Global",
            axis="Z",
            positive_movement=True,
            start_position= 0,
            periodic_translate=True,
            negative_limit = 0,
            positive_limit=0,
            velocity=0,
            mechanical_transient=False,
            mass=1,
            damping=0,
            load_force=0,
            motion_name=None
    ):
        """Assign a Translation Motion to an object container.

        Parameters
        ----------
        band_object : str,
            Object container.
        coordinate_system : str, optional
            Coordinate System Name. Default is ``"Global``.
        axis :str or int, optional
            Coordinate System Axis. Default is ``"Z"``.
            It can be a ``pyaedt.generic.constants.AXIS`` Enumerator value.
        positive_movement : bool, Optional
            Either if movement is Positive or not. Default is ``True``.
        start_position : float or str, optional
            Movement Start Position. If float, default modeler units will be applied.
        periodic_translate : bool, Optional
            Either if Periodic Movement or not. Default is ``False``.
        negative_limit : float or str, optional
            Movement negative limit. If float, default modeler units will be applied.
        positive_limit : float or str, optional
            Movement positive limit. If float, default modeler units will be applied.
        velocity : float or str, optional
            Movement velocity. If float, "m_per_sec" units will be applied.
        mechanical_transient : bool, Optional
            Either to consider or not mechanical movement. Default is ``False``.
        mass : float or str, optional
            mechanical mass. If float, "Kg" units will be applied.
        damping : float, optional
            Damping Factor. Default ``0``.
        load_force : float or str, optional
            Load Force. If float, "newton" units will be applied.
        motion_name : str, optional
            Motion Name.

        Returns
        -------
        :class:`pyaedt.modules.Boundary.BoundaryObject`
            Boundary object.

        References
        ----------

        >>> oModule.AssignBand
        """
        assert self.solution_type == SOLUTIONS.Maxwell3d.Transient, "Motion applies only to Transient Setup"
        if not motion_name:
            motion_name = generate_unique_name("Motion")
        object_list = self.modeler._convert_list_to_ids(band_object)
        props = OrderedDict(
            {
                "Move Type": "Translate",
                "Coordinate System": coordinate_system,
                "PostProcessing Coordinate System": coordinate_system,
                "Axis": GeometryOperators.cs_axis_str(axis),
                "Is Positive": positive_movement,
                "InitPos": self._arg_with_units(start_position),
                "TranslatePeriodic": periodic_translate,
                "NegativePos": self._arg_with_units(negative_limit),
                "PositivePos": self._arg_with_units(positive_limit),
                "Consider Mechanical Transient": mechanical_transient,
                "Velocity": self._arg_with_units(velocity, "m_per_sec"),
                "Mass": self._arg_with_units(mass, "Kg"),
                "Damping": str(damping),
                "Load Force": self._arg_with_units(load_force, "newton"),
                "Objects": object_list,

            }
        )
        bound = BoundaryObject(self, motion_name, props, "Band")
        if bound.create():
            self.boundaries.append(bound)
            return bound
        return False

    @aedt_exception_handler
    def assign_rotate_motion(
            self,
            band_object,
            coordinate_system="Global",
            axis="Z",
            positive_movement=True,
            start_position=0,
            has_rotation_limits=True,
            negative_limit=0,
            positive_limit=360,
            non_cylindrical=False,
            mechanical_transient=False,
            angular_velocity="0rpm",
            inertia="1",
            damping=0,
            load_torque="0newton",
            motion_name=None
    ):
        """Assign a Rotation Motion to an object container.

        Parameters
        ----------
        band_object : str,
            Object container.
        coordinate_system : str, optional
            Coordinate System Name. Default is ``"Global``.
        axis : str or int, optional
            Coordinate System Axis. Default is ``"Z"``.
            It can be a ``pyaedt.generic.constants.AXIS`` Enumerator value.
        positive_movement : bool, Optional
            Either if movement is Positive or not. Default is ``True``.
        start_position : float or str, optional
            Movement Start Position. If float, "deg" units will be applied.
        has_rotation_limits : bool, Optional
            Either if there will be a limit in rotation or not. Default is ``False``.
        negative_limit : float or str, optional
            Movement negative limit. If float, "deg" units will be applied.
        positive_limit : float or str, optional
            Movement positive limit. If float, "deg" units will be applied.
        non_cylindrical : bool, optional
            Either if Non Cylindrical rotation has to be considered. Default is ``False``.
        angular_velocity : float or str, optional
            Movement velocity. If float, "rpm" units will be applied.
        mechanical_transient : bool, Optional
            Either to consider or not mechanical movement. Default is ``False``.
        inertia : float, optional
            mechanical inertia.
        damping : float, optional
            Damping Factor. Default ``0``.
        load_torque : float or str, optional
            Load Force. If float, "NewtonMeter" units will be applied.
        motion_name : str, optional
            Motion Name.

        Returns
        -------
        :class:`pyaedt.modules.Boundary.BoundaryObject`
            Boundary object.

        References
        ----------

        >>> oModule.AssignBand
        """
        assert self.solution_type == SOLUTIONS.Maxwell3d.Transient, "Motion applies only to Transient Setup"
        if not motion_name:
            motion_name = generate_unique_name("Motion")
        object_list = self.modeler._convert_list_to_ids(band_object)
        props = OrderedDict(
            {
                "Move Type": "Rotate",
                "Coordinate System": coordinate_system,
                "Axis": GeometryOperators.cs_axis_str(axis),
                "Is Positive": positive_movement,
                "InitPos": self._arg_with_units(start_position, "deg"),
                "HasRotateLimit": has_rotation_limits,
                "NegativePos": self._arg_with_units(negative_limit, "deg"),
                "PositivePos": self._arg_with_units(positive_limit, "deg"),
                "NonCylindrical": non_cylindrical,
                "Consider Mechanical Transient": mechanical_transient,
                "Angular Velocity": self._arg_with_units(angular_velocity, "rpm"),
                "Moment of Inertia": str(inertia),
                "Damping": str(damping),
                "Load Torque": self._arg_with_units(load_torque, "NewtonMeter"),
                "Objects": object_list,

            }
        )
        bound = BoundaryObject(self, motion_name, props, "Band")
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
            List of faces to assign a voltrage source to.
        amplitude : float, optional
            Voltage amplitude in mV. The default is ``1``.
        name : str, optional
            Name of the boundary. The default is ``None``.

        Returns
        -------
        :class:`pyaedt.modules.Boundary.BoundaryObject`
            Boundary object.

        References
        ----------

        >>> oModule.AssignVoltage
        """
        if isinstance(amplitude, (int, float)):
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
            List of faces to assign a voltage drop to.
        amplitude : float, optional
            Voltage amplitude in mV. The default is ``1``.
        swap_direction : bool, optional
            The default value is ``False``.
        name : str, optional
            Name of the boundary. The default is ``None``.

        Returns
        -------
        :class:`pyaedt.modules.Boundary.BoundaryObject`
            Boundary object.

        References
        ----------

        >>> oModule.AssignVoltageDrop
        """
        if isinstance(amplitude, (int, float)):
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
    def assign_winding(
        self,
        coil_terminals=None,
        winding_type="Current",
        is_solid=True,
        current_value=1,
        res=0,
        ind=0,
        voltage=0,
        parallel_branches=1,
        name=None,
    ):
        """Assign a winding to a Maxwell design.

        Parameters
        ----------
        coil_terminals : list, optional
            List of faces to create the coil terminal on.
            The default is ``None``.
        winding_type : str, optional
            Type of the winding. Options are ``"Current"``, ``"Voltage"``,
            and ``"External"``. The default is ``"Current"``.
        is_solid : bool, optional
            Type of the winding.  ``True`` is solid, ``False`` is stranded. The default is ``True``.
        current_value : float, optional
            Value of the current in amperes. The default is ``1``.
        res : float, optional
            Resistance in ohms. The default is ``0``.
        ind : float, optional
            Henry. The default is ``0``.
        voltage : float, optional
            Voltage value. The default is ``0``.
        parallel_branches : int, optional
            The default is ``1``.
        name : str, optional
            Name of the boundary. The default is ``None``.

        Returns
        -------
        :class:`pyaedt.modules.Boundary.BoundaryObject`
            Bounding object for the winding, otherwise only the bounding object.

        References
        ----------

        >>> oModule.AssignWindingGroup
        """

        if not name:
            name = generate_unique_name("Winding")

        props = OrderedDict(
            {
                "Type": winding_type,
                "IsSolid": is_solid,
                "Current": str(current_value) + "A",
                "Resistance": str(res) + "ohm",
                "Inductance": str(ind) + "H",
                "Voltage": str(voltage) + "V",
                "ParallelBranchesNum": str(parallel_branches),
            }
        )
        bound = BoundaryObject(self, name, props, "Winding")
        if bound.create():
            self.boundaries.append(bound)
            if type(coil_terminals) is not list:
                coil_terminals = [coil_terminals]
            coil_names = []
            for coil in coil_terminals:
                c = self.assign_coil(coil)
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
            List of the coil names.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.

        References
        ----------

        >>> oModule.AddWindingTerminals
        >>> oModule.AddWindingCoils
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
            List of objects or face IDs.
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

        References
        ----------

        >>> oModule.AssignCoil
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
                    {"Objects": input_object, "Conductor number": str(conductor_number), "Point out of terminal": point}
                )
                bound = BoundaryObject(self, name, props2, "CoilTerminal")
            else:
                props2 = OrderedDict(
                    {"Objects": input_object, "Conductor number": str(conductor_number), "PolarityType": polarity}
                )
                bound = BoundaryObject(self, name, props2, "Coil")
        else:
            if self.modeler._is3d:
                props2 = OrderedDict(
                    {"Faces": input_object, "Conductor number": str(conductor_number), "Point out of terminal": point}
                )
                bound = BoundaryObject(self, name, props2, "CoilTerminal")

            else:
                self.logger.warning("Face Selection is not allowed in Maxwell 2D. Provide a 2D object.")
                return False
        if bound.create():
            self.boundaries.append(bound)
            return bound
        return False

    @aedt_exception_handler
    def assign_force(self, input_object, reference_cs="Global", is_virtual=True, force_name=None):
        """Assign a force to one or more objects.

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

        References
        ----------

        >>> oModule.AssignForce
        """
        input_object = self.modeler._convert_list_to_ids(input_object, True)
        if not force_name:
            force_name = generate_unique_name("Force")
        if self.design_type == "Maxwell 3D":
            self.o_maxwell_parameters.AssignForce(
                [
                    "NAME:" + force_name,
                    "Reference CS:=",
                    reference_cs,
                    "Is Virtual:=",
                    is_virtual,
                    "Objects:=",
                    input_object,
                ]
            )
        else:
            self.o_maxwell_parameters.AssignForce(
                ["NAME:" + force_name, "Reference CS:=", reference_cs, "Objects:=", input_object]
            )
        return True

    @aedt_exception_handler
    def assign_torque(
        self, input_object, reference_cs="Global", is_positive=True, is_virtual=True, axis="Z", torque_name=None
    ):
        """Assign a torque to one or more objects.

        Parameters
        ----------
        input_object : str or list
           One or more objects to assign the torque to.
        reference_cs : str, optional
            Name of the reference coordinate system. The default is ``"Global"``.
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

        References
        ----------

        >>> oModule.AssignTorque
        """
        input_object = self.modeler._convert_list_to_ids(input_object, True)
        if not torque_name:
            torque_name = generate_unique_name("Torque")
        if self.design_type == "Maxwell 3D":
            self.o_maxwell_parameters.AssignTorque(
                [
                    "NAME:" + torque_name,
                    "Is Virtual:=",
                    is_virtual,
                    "Coordinate System:=",
                    reference_cs,
                    "Axis:=",
                    axis,
                    "Is Positive:=",
                    is_positive,
                    "Objects:=",
                    input_object,
                ]
            )
        else:
            self.o_maxwell_parameters.AssignTorque(
                [
                    "NAME:" + torque_name,
                    "Coordinate System:=",
                    reference_cs,
                    "Is Positive:=",
                    is_positive,
                    "Objects:=",
                    input_object,
                ]
            )
        return True

    @aedt_exception_handler
    def assign_force(self, input_object, reference_cs="Global", is_virtual=True, force_name=None):
        """Assign a force to the selection.

        Parameters
        ----------
        input_object : str, list
            One or more objects to assign a force to.
        reference_cs : str, optional
            Name of the reference coordinate system. The default is ``Global``.
        is_virtual : bool, optional
            Whether the force is virtual. The default is ``True``.
        force_name : str, optional
            Name of the force. The default is ``None``.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.

        References
        ----------

        >>> oModule.AssignForce
        """
        input_object = self.modeler._convert_list_to_ids(input_object, True)
        if not force_name:
            force_name = generate_unique_name("Force")
        self.o_maxwell_parameters.AssignForce(
            [
                "NAME:" + force_name,
                "Reference CS:=",
                reference_cs,
                "Is Virtual:=",
                is_virtual,
                "Objects:=",
                input_object,
            ]
        )
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
        bool
            ``True`` when successful, ``False`` when failed.

        References
        ----------

        >>> oEditor.ChangeProperty
        """
        self.modeler.primitives[name].solve_inside = activate
        return True

    @aedt_exception_handler
    def analyze_from_zero(self):
        """Analyze from zero.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.

        References
        ----------

        >>> oModule.ResetSetupToTimeZero
        """
        self.oanalysis.ResetSetupToTimeZero(self._setup)
        self.analyze_nominal()
        return True

    @aedt_exception_handler
    def set_initial_angle(self, motion_setup, val):
        """Set the initial angle.

        Parameters
        ----------
        motion_setup : str
            Name of the motion setup.
        val : float
            Value of the angle in degrees.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.

        References
        ----------

        >>> oDesign.ChangeProperty
        """
        self.odesign.ChangeProperty(
            [
                "NAME:AllTabs",
                [
                    "NAME:Maxwell2D",
                    ["NAME:PropServers", "ModelSetup:" + motion_setup],
                    ["NAME:ChangedProps", ["NAME:Initial Position", "Value:=", val]],
                ],
            ]
        )
        return True

    def __enter__(self):
        return self


class Maxwell3d(Maxwell, FieldAnalysis3D, object):
    """Provides the Maxwell 3D application interface.

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
    specified_version : str, optional
        Version of AEDT to use. The default is ``None``, in which case
        the active version or latest installed version is used. This
        parameter is ignored when Script is launched within AEDT.
    NG : bool, optional
        Whether to launch AEDT in the non-graphical mode. The default
        is ``False``, in which case AEDT is launched in the graphical
        mode. This parameter is ignored when Script is launched within
        AEDT.
    new_desktop_session : bool, optional
        Whether to launch an instance of AEDT in a new thread, even if
        another instance of the ``specified_version`` is active on the
        machine. The default is ``True``. This parameter is ignored
        when Script is launched within AEDT.
    close_on_exit : bool, optional
        Whether to release AEDT on exit. The default is ``False``.
    student_version : bool, optional
        Whether to open the AEDT student version. The default is
        ``False``. This parameter is ignored when Script is launched
        within AEDT.

    Examples
    --------
    Create an instance of Maxwell 3D and open the specified
    project, which is named ``mymaxwell.aedt``.

    >>> from pyaedt import Maxwell3d
    >>> aedtapp = Maxwell3d("mymaxwell.aedt")
    pyaedt info: Added design ...

    Create an instance of Maxwell 3D using the 2021 R1 release and open
    the specified project, which is named ``mymaxwell2.aedt``.

    >>> aedtapp = Maxwell3d(specified_version="2021.2", projectname="mymaxwell2.aedt")
    pyaedt info: Added design ...

    """

    @property  # for legacy purposes
    def dim(self):
        """Dimensions."""
        return "3D"

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
        """
        Initialize the `Maxwell` class.
        """
        self.is3d = True
        FieldAnalysis3D.__init__(
            self,
            "Maxwell 3D",
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
        Maxwell.__init__(self)


class Maxwell2d(Maxwell, FieldAnalysis2D, object):
    """Provides the Maxwell 2D application interface.

    This class allows you to connect to an existing Maxwell 2D design or create a
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
    Create an instance of Maxwell 2D and connect to an existing
    Maxwell 2D design or create a new Maxwell 2D design if one does
    not exist.

    >>> from pyaedt import Maxwell2d
    >>> aedtapp = Maxwell2d()

    Create an instance of Maxwell 2D and link to a project named
    ``projectname``. If this project does not exist, create one with
    this name.

    >>> aedtapp = Maxwell2d(projectname)

    Create an instance of Maxwell 2D and link to a design named
    ``designname`` in a project named ``projectname``.

    >>> aedtapp = Maxwell2d(projectname,designame)

    """

    @property  # for legacy purposes
    def dim(self):
        """Dimensions."""
        return self.modeler.dimension

    @property
    def geometry_mode(self):
        """Geometry mode.

        References
        ----------

        >>> oDesign.GetGeometryMode"""
        return self.odesign.GetGeometryMode()

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
        self.is3d = False
        FieldAnalysis2D.__init__(
            self,
            "Maxwell 2D",
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
        Maxwell.__init__(self)

    @aedt_exception_handler
    def get_model_depth(self):
        """Get model depth."""
        if "ModelDepth" in self.design_properties:
            value_str = self.design_properties["ModelDepth"]
            try:
                a = float_units(value_str)
            except:
                a = self.variable_manager[value_str].value
            return a
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

        def convert(obj):
            if isinstance(obj, bool):
                return str(obj).lower()
            if isinstance(obj, (list, tuple)):
                return [convert(item) for item in obj]
            if isinstance(obj, dict):
                return {convert(key): convert(value) for key, value in obj.items()}
            return obj

        solid_bodies = self.modeler.solid_bodies
        if objectfilter:
            solid_ids = [i for i, j in self.modeler.primitives.object_id_dict.items() if j.name in objectfilter]
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
            "MaterialProperties": self.get_object_material_properties(solid_bodies),
        }

        design_file = os.path.join(self.working_directory, "design_data.json")
        with open(design_file, "w") as fps:
            json.dump(convert(self.design_data), fps, indent=4)
        return True

    @aedt_exception_handler
    def read_design_data(self):
        """Read back the design data as a dictionary.

        Returns
        -------
        dict
            Dictionary of design data.

        """
        design_file = os.path.join(self.working_directory, "design_data.json")
        with open(design_file, "r") as fps:
            design_data = json.load(fps)
        return design_data

    @aedt_exception_handler
    def assign_balloon(self, edge_list, bound_name=None):
        """Assign a balloon boundary to a list of edges.

        Parameters
        ----------
        edge_list : list
            List of edges.
        bound_name : str, optional
            Name of the boundary. The default is ``None``.

        Returns
        -------
        :class:`pyaedt.modules.Boundary.BoundaryObject`
            Boundary object.

        References
        ----------

        >>> oModule.AssignBalloon
        """
        edge_list = self.modeler._convert_list_to_ids(edge_list)

        if not bound_name:
            bound_name = generate_unique_name("Balloon")

        props2 = OrderedDict({"Edges": edge_list})
        bound = BoundaryObject(self, bound_name, props2, "Balloon")

        if bound.create():
            self.boundaries.append(bound)
            return bound
        return False

    @aedt_exception_handler
    def assign_vector_potential(self, input_edge, vectorvalue=0, bound_name=None):
        """Assign a vector to a list of edges.

        Parameters
        ----------
        input_edge : list
            List of edge names or edge IDs to assign a vector to.
        vectorvalue : float, optional
            Value of the vector. The default is ``0``.
        bound_name : str, optional
            Name of the boundary. The default is ``None``.

        Returns
        -------
        :class:`pyaedt.modules.Boundary.BoundaryObject`
            Vector Potential Object

        References
        ----------

        >>> oModule.AssignVectorPotential
        """
        input_edge = self.modeler._convert_list_to_ids(input_edge)

        if not bound_name:
            bound_name = generate_unique_name("Vector")
        if type(input_edge[0]) is str:
            props2 = OrderedDict({"Objects": input_edge, "Value": str(vectorvalue), "CoordinateSystem": ""})
        else:
            props2 = OrderedDict({"Edges": input_edge, "Value": str(vectorvalue), "CoordinateSystem": ""})
        bound = BoundaryObject(self, bound_name, props2, "VectorPotential")

        if bound.create():
            self.boundaries.append(bound)
            return bound
        return False

    @aedt_exception_handler
    def assign_master_slave(self, master_edge, slave_edge, reverse_master=False, reverse_slave=False,
                            same_as_master=True, bound_name=None):
        """Assign master and slave boundary conditions to two edges of the same object.

        Parameters
        ----------
        master_edge : int
            ID of the master edge.
        slave_edge : int
            ID of the slave edge.
        reverse_master : bool, optional
            Whether to reverse the master edge to the V direction. The default is ``False``.
        reverse_slave : bool, optional
            Whether to reverse the master edge to the U direction. The default is ``False``.
        same_as_master : bool, optional
            Whether the B-Field of the slave edge and master edge are the same. The default is ``True``.
        bound_name : str, optional
            Name of the master boundary. The name of the slave boundary will have a ``_dep`` suffix.

        Returns
        -------
        :class:`pyaedt.modules.Boundary.BoundaryObject`, :class:`pyaedt.modules.Boundary.BoundaryObject`
            Master and slave objects.

        References
        ----------

        >>> oModule.AssignIndependent
        >>> oModule.AssignDependent
        """
        master_edge = self.modeler._convert_list_to_ids(master_edge)
        slave_edge = self.modeler._convert_list_to_ids(slave_edge)
        if not bound_name:
            bound_name_m = generate_unique_name("Independent")
            bound_name_s = generate_unique_name("Dependent")
        else:
            bound_name_m = bound_name
            bound_name_s = bound_name + "_dep"
        props2 = OrderedDict({"Edges": master_edge, "ReverseV": reverse_master})
        bound = BoundaryObject(self, bound_name_m, props2, "Independent")
        if bound.create():
            self.boundaries.append(bound)

            props2 = OrderedDict({"Edges": slave_edge, "ReverseU": reverse_slave, "Independent": bound_name_m,
                                  "SameAsMaster": same_as_master})
            bound2 = BoundaryObject(self, bound_name_s, props2, "Dependent")
            if bound2.create():
                self.boundaries.append(bound2)
                return bound, bound2
            else:
                return bound, False
        return False, False
