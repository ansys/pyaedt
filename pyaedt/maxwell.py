"""This module contains these Maxwell classes: ``Maxwell``, ``Maxwell2d``, and ``Maxwell3d``."""

from __future__ import absolute_import  # noreorder

import io
import json
import os
from collections import OrderedDict

from pyaedt.application.Analysis3D import FieldAnalysis3D
from pyaedt.generic.constants import SOLUTIONS
from pyaedt.generic.DataHandlers import float_units
from pyaedt.generic.general_methods import generate_unique_name
from pyaedt.generic.general_methods import open_file
from pyaedt.generic.general_methods import pyaedt_function_handler
from pyaedt.modeler.GeometryOperators import GeometryOperators
from pyaedt.modeler.Object3d import EdgePrimitive
from pyaedt.modeler.Object3d import FacePrimitive
from pyaedt.modules.Boundary import BoundaryObject
from pyaedt.modules.Boundary import MaxwellParameters


class Maxwell(object):
    def __init__(self):
        pass

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

    @pyaedt_function_handler()
    def change_symmetry_multiplier(self, value=1):
        """Set the Design Symmetry Multiplier to a specified value.

        Parameters
        ----------
        value : int, optional
            Value to use as the Design Symmetry Multiplier coefficient. The default value is ``1``.

        Returns
        -------
        bool
        """
        return self.change_design_settings({"Multiplier": value})

    @pyaedt_function_handler()
    def change_inductance_computation(self, compute_transient_inductance=True, incremental_matrix=False):
        """Enable the inductance computation for the transient analysis and set the incremental matrix.

        Parameters
        ----------
        compute_transient_inductance : bool, optional
            Whether to enable the inductance calculation for the transient analysis.
            The default is ``True``.
        incremental_matrix : bool, optional
            Whether to set the inductance calculation to ``Incremental`` if
            ``compute_transient_inductance=True``. The default is ``False``.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.

        References
        ----------

        >>> oDesign.SetDesignSettings
        """
        return self.change_design_settings(
            {"ComputeTransientInductance": compute_transient_inductance, "ComputeIncrementalMatrix": incremental_matrix}
        )

    @pyaedt_function_handler()
    def set_core_losses(self, objects, value=True):
        """Whether to enable core losses for a set of objects.

        This method works only on ``EddyCurrent`` and ``Transient`` solutions.

        Parameters
        ----------
        objects : list, str
            List of object to apply core losses to.
        value : bool, optional
            Whether to enable core losses for the given list. The default is
            ``True``.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.

        References
        ----------

        >>> oModule.SetCoreLoss

        Examples
        --------
        Set core losses in Maxwell 3D.

        >>> from pyaedt import Maxwell3d
        >>> maxwell_3d = Maxwell3d()
        >>> maxwell_3d.set_core_losses(["PQ_Core_Bottom", "PQ_Core_Top"], True)

        """
        if self.solution_type in ["EddyCurrent", "Transient"]:
            objects = self.modeler.convert_to_selections(objects, True)
            self.oboundary.SetCoreLoss(objects, value)
            return True
        else:
            raise Exception("Core losses is only available with `EddyCurrent` and `Transient` solutions.")
        return False

    @pyaedt_function_handler()
    def assign_matrix(
        self,
        sources,
        matrix_name=None,
        turns=None,
        return_path=None,
        group_sources=None,
        branches=None,
    ):
        """Assign a matrix to the selection.

        Parameters
        ----------
        sources : list, str
            List of sources to assign a matrix to.
        matrix_name : str, optional
            Name of the matrix. The default is ``None``.
        turns : list, int, optional
            Number of turns. The default is 1.
        return_path : list, str, optional
            Return path. The default is ``infinite``
        group_sources : dict, list optional
            Dictionary consisting of ``{Group Name: list of source names}`` to add
            multiple groups. You can also define a list of strings. The default is ``None``.
        branches : : list, int, optional
            Number of branches. The default is ``None``, which indicates that only one
            branch exists.

        Returns
        -------
        :class:`pyaedt.modules.Boundary.BoundaryObject`
            Boundary object.

        References
        ----------

        >>> oModule.AssignMatrix

        Examples
        --------
        Set matrix in a Maxwell analysis.

        >>> m2d = Maxwell2d(solution_type="MagnetostaticXY", close_on_exit=True, specified_version="2022.1")
        >>> coil1 = m2d.modeler.create_rectangle([0, 1.5, 0], [8, 3], is_covered=True, name="Coil_1")
        >>> coil2 = m2d.modeler.create_rectangle([8.5, 1.5, 0], [8, 3], is_covered=True, name="Coil_2")
        >>> coil3 = m2d.modeler.create_rectangle([16, 1.5, 0], [8, 3], is_covered=True, name="Coil_3")
        >>> coil4 = m2d.modeler.create_rectangle([32, 1.5, 0], [8, 3], is_covered=True, name="Coil_4")
        >>> current1 = m2d.assign_current("Coil_1", amplitude=1, swap_direction=False, name="Current1")
        >>> current2 = m2d.assign_current("Coil_2", amplitude=1, swap_direction=True, name="Current2")
        >>> current3 = m2d.assign_current("Coil_3", amplitude=1, swap_direction=True, name="Current3")
        >>> current4 = m2d.assign_current("Coil_4", amplitude=1, swap_direction=True, name="Current4")
        >>> group_sources = {"Group1_Test": ["Current1", "Current3"], "Group2_Test": ["Current2", "Current4"]}
        >>> selection = ['Current1', 'Current2', 'Current3', 'Current4']
        >>> turns = [5, 1, 2, 3]
        >>> L = m2d.assign_matrix(sources=selection, matrix_name="Test2", turns=turns, group_sources=group_sources)
        """
        sources = self.modeler.convert_to_selections(sources, True)
        if self.solution_type in ["Electrostatic", "ACConduction", "DCConduction"]:
            turns = ["1"] * len(sources)
            branches = None
            if self.design_type == "Maxwell 2D":
                if group_sources:
                    if isinstance(group_sources, dict):
                        first_key = next(iter(group_sources))
                        group_sources = group_sources[first_key]
                        self.logger.warning("First Ground is selected")
                    group_sources = self.modeler.convert_to_selections(group_sources, True)
                    if any(item in group_sources for item in sources):
                        self.logger.error("Ground must be different than selected sources")
                        return False
            else:
                group_sources = None

        elif self.solution_type in ["EddyCurrent", "Magnetostatic"]:
            if self.solution_type == "Magnetostatic":
                if group_sources:
                    if isinstance(group_sources, (dict, OrderedDict)):
                        new_group = group_sources.copy()
                        for element in new_group:
                            if not all(item in sources for item in group_sources[element]):
                                self.logger.warning("Sources in group " + element + " are not selected")
                                group_sources.pop(element)
                        if not branches or len(group_sources) != len(
                            self.modeler.convert_to_selections(branches, True)
                        ):
                            if branches:
                                branches = self.modeler.convert_to_selections(branches, True)
                                num = abs(len(group_sources) - len(self.modeler.convert_to_selections(branches, True)))
                                if len(group_sources) < len(self.modeler.convert_to_selections(branches, True)):
                                    branches = branches[:-num]
                                else:
                                    new_element = [branches[0]] * num
                                    branches.extend(new_element)
                            else:
                                branches = [1] * len(group_sources)
                    elif isinstance(group_sources, list):
                        group_name = generate_unique_name("Group")
                        group_sources = {group_name: group_sources}
                    else:
                        self.logger.warning("Group of sources is not a dictionary")
                        group_sources = None
            else:
                group_sources = None
                branches = None
                turns = ["1"] * len(sources)
                self.logger.info("Infinite is the only return path option in EddyCurrent.")
                return_path = ["infinite"] * len(sources)

        if self.solution_type not in ["Transient", "ElectricTransient"]:
            if not matrix_name:
                matrix_name = generate_unique_name("Matrix")
            if not turns or len(sources) != len(self.modeler.convert_to_selections(turns, True)):
                if turns:
                    turns = self.modeler.convert_to_selections(turns, True)
                    num = abs(len(sources) - len(self.modeler.convert_to_selections(turns, True)))
                    if len(sources) < len(self.modeler.convert_to_selections(turns, True)):
                        turns = turns[:-num]
                    else:
                        new_element = [turns[0]] * num
                        turns.extend(new_element)
                else:
                    turns = ["1"] * len(sources)
            else:
                turns = self.modeler.convert_to_selections(turns, True)
            if not return_path or len(sources) != len(self.modeler.convert_to_selections(return_path, True)):
                return_path = ["infinite"] * len(sources)
            else:
                return_path = self.modeler.convert_to_selections(return_path, True)
            if any(item in return_path for item in sources):
                self.logger.error("Return path specified must not be included in sources")
                return False

            if group_sources and self.solution_type in ["EddyCurrent", "Magnetostatic"]:
                props = OrderedDict(
                    {"MatrixEntry": OrderedDict({"MatrixEntry": []}), "MatrixGroup": OrderedDict({"MatrixGroup": []})}
                )
            else:
                props = OrderedDict({"MatrixEntry": OrderedDict({"MatrixEntry": []}), "MatrixGroup": []})

            for element in range(len(sources)):
                if self.solution_type == "Magnetostatic" and self.design_type == "Maxwell 2D":
                    prop = OrderedDict(
                        {
                            "Source": sources[element],
                            "NumberOfTurns": turns[element],
                            "ReturnPath": return_path[element],
                        }
                    )
                elif self.solution_type == "EddyCurrent":
                    prop = OrderedDict({"Source": sources[element], "ReturnPath": return_path[element]})
                else:
                    prop = OrderedDict({"Source": sources[element], "NumberOfTurns": turns[element]})
                props["MatrixEntry"]["MatrixEntry"].append(prop)

            if group_sources:
                if self.solution_type in ["Electrostatic", "ACConduction", "DCConduction"]:
                    source_list = ",".join(group_sources)
                    props["GroundSources"] = source_list
                else:
                    cont = 0
                    for element in group_sources:
                        source_list = ",".join(group_sources[element])
                        # GroundSources
                        prop = OrderedDict(
                            {"GroupName": element, "NumberOfBranches": branches[cont], "Sources": source_list}
                        )
                        props["MatrixGroup"]["MatrixGroup"].append(prop)
                        cont += 1

            bound = MaxwellParameters(self, matrix_name, props, "Matrix")
            if bound.create():
                self.boundaries.append(bound)
                return bound
        else:
            self.logger.error("Solution type does not have matrix parameters")
            return False

    @pyaedt_function_handler()
    def setup_ctrlprog(
        self, setupname, file_str=None, keep_modifications=False, python_interpreter=None, aedt_lib_dir=None
    ):
        """Configure the transient design setup to run a specific control program.

        Parameters
        ----------
        setupname : str
            Name of the setup.
        file_str : str, optional
            Name of the file. The default value is ``None``.
        keep_modifications : bool, optional
            Whether to save the changes. The default value is ``False``.
        python_interpreter : str, optional
             Python interpreter to use. The default value is ``None``.
        aedt_lib_dir : str, optional
             Full path to the ``pyaedt`` directory. The default value is ``None``.

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
                assert os.path.exists(ctl_file), "Control program file could not be created."

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
    @pyaedt_function_handler()
    def eddy_effects_on(self, object_list, activate_eddy_effects=True, activate_displacement_current=True):
        """Assign eddy effects on objects.

        Parameters
        ----------
        object_list : list
            List of objects.
        activate_eddy_effects : bool, optional
            Whether to activate eddy effects. The default is ``True``.
        activate_displacement_current : bool, optional
            Whether to activate the displacement current. The default is ``True``.

        Returns
        -------
        bool
            ``True`` when successful and ``False`` when failed.

        References
        ----------

        >>> oModule.SetEddyEffect
        """
        solid_objects_names = self.get_all_conductors_names()

        EddyVector = ["NAME:EddyEffectVector"]
        if self.modeler._is3d:
            if not activate_eddy_effects:
                activate_displacement_current = False
            for obj in solid_objects_names:
                if obj in object_list:
                    EddyVector.append(
                        [
                            "NAME:Data",
                            "Object Name:=",
                            obj,
                            "Eddy Effect:=",
                            activate_eddy_effects,
                            "Displacement Current:=",
                            activate_displacement_current,
                        ]
                    )
                else:
                    EddyVector.append(
                        [
                            "NAME:Data",
                            "Object Name:=",
                            obj,
                            "Eddy Effect:=",
                            bool(self.oboundary.GetEddyEffect(obj)),
                            "Displacement Current:=",
                            bool(self.oboundary.GetDisplacementCurrent(obj)),
                        ]
                    )
        else:
            for obj in solid_objects_names:
                if obj in object_list:
                    EddyVector.append(
                        [
                            "NAME:Data",
                            "Object Name:=",
                            obj,
                            "Eddy Effect:=",
                            activate_eddy_effects,
                        ]
                    )
                else:
                    EddyVector.append(
                        [
                            "NAME:Data",
                            "Object Name:=",
                            obj,
                            "Eddy Effect:=",
                            bool(self.oboundary.GetEddyEffect(obj)),
                        ]
                    )

        self.oboundary.SetEddyEffect(["NAME:Eddy Effect Setting", EddyVector])
        return True

    @pyaedt_function_handler()
    def setup_y_connection(self, windings_name=None):
        """Setup the Y connection.

        Parameters
        ----------
        winding_name : list, optional
            List of windings. For example, ``["PhaseA", "PhaseB", "PhaseC"]``.
            The default value is ``None``, in which case the design has no Y connection.

        Returns
        -------
        bool
            ``True`` when successful and ``False`` when failed.

        References
        ----------

        >>> oModule.SetupYConnection

        Examples
        --------
        Set up the Y connection for three existing windings named ``PhaseA``, ``PhaseB``, and ``PhaseC``.
        This creates one ``YConnection`` group containing these three phases.

        >>> from pyaedt import Maxwell2d
        >>> aedtapp = Maxwell2d("Motor_EM_R2019R3.aedt")
        >>> aedtapp.set_active_design("Basis_Model_For_Test")
        >>> aedtapp.setup_y_connection(["PhaseA", "PhaseB", "PhaseC"])
        """

        if windings_name:
            connection = ["NAME:YConnection"]
            connection.append("Windings:=")
            connection.append(",".join(windings_name))
            windings = ["NAME:YConnection"]
            windings.append(connection)
            self.oboundary.SetupYConnection(windings)
        else:
            self.oboundary.SetupYConnection()
        return True

    @pyaedt_function_handler()
    def assign_current(self, object_list, amplitude=1, phase="0deg", solid=True, swap_direction=False, name=None):
        """Assign the source of the current.

        Parameters
        ----------
        object_list : list
            List of objects to assign the current source to.
        amplitude : float, optional
            Current amplitude in mA. The default is ``1``.
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

        object_list = self.modeler.convert_to_selections(object_list, True)
        if self.is3d:
            if type(object_list[0]) is int:
                props = OrderedDict(
                    {
                        "Faces": object_list,
                        "Current": amplitude,
                    }
                )
            else:
                props = OrderedDict(
                    {
                        "Objects": object_list,
                        "Current": amplitude,
                    }
                )
            if self.solution_type not in [
                "Magnetostatic",
                "DCConduction",
                "ElectricTransient",
                "TransientAPhiFormulation",
            ]:
                props["Phase"] = phase
                if self.solution_type not in ["DCConduction", "ElectricTransient"]:
                    props["IsSolid"] = solid
            props["Point out of terminal"] = swap_direction
        else:
            if type(object_list[0]) is str:
                props = OrderedDict({"Objects": object_list, "Current": amplitude, "IsPositive": swap_direction})
            else:
                self.logger.warning("Input must be a 2D object.")
                return False
        bound = BoundaryObject(self, name, props, "Current")
        if bound.create():
            self.boundaries.append(bound)
            return bound
        return False

    @pyaedt_function_handler()
    def assign_translate_motion(
        self,
        band_object,
        coordinate_system="Global",
        axis="Z",
        positive_movement=True,
        start_position=0,
        periodic_translate=True,
        negative_limit=0,
        positive_limit=0,
        velocity=0,
        mechanical_transient=False,
        mass=1,
        damping=0,
        load_force=0,
        motion_name=None,
    ):
        """Assign a translation motion to an object container.

        Parameters
        ----------
        band_object : str
            Object container.
        coordinate_system : str, optional
            Coordinate system name. The default is ``"Global"``.
        axis :str or int, optional
            Coordinate system axis. The default is ``"Z"``.
            It can be a ``pyaedt.generic.constants.AXIS`` enumerator value.
        positive_movement : bool, optional
            Whether movement is positive. The default is ``True``.
        start_position : float or str, optional
            Starting position of the movement. The default is ``0``. If a float
            value is used, default modeler units are applied.
        periodic_translate : bool, optional
            Whether movement is periodic. The default is ``False``.
        negative_limit : float or str, optional
            Negative limit of the movement. The default is ``0``. If a float
            value is used, the default modeler units are applied.
        positive_limit : float or str, optional
            Positive limit of the movement. The default is ``0``. If a float
            value is used, the default modeler units are applied.
        velocity : float or str, optional
            Movement velocity. The default is ``0``. If a float value
            is used, "m_per_sec" units are applied.
        mechanical_transient : bool, optional
            Whether to consider the mechanical movement. The default is ``False``.
        mass : float or str, optional
            Mechanical mass. The default is ``1``. If a float value is used, "Kg" units
            are applied.
        damping : float, optional
            Damping factor. The default is ``0``.
        load_force : float or str, optional
            Load force. The default is ``0``. If a float value is used, "newton"
            units are applied.
        motion_name : str, optional
            Motion name. The default is ``None``.

        Returns
        -------
        :class:`pyaedt.modules.Boundary.BoundaryObject`
            Boundary object.

        References
        ----------

        >>> oModule.AssignBand
        """
        assert self.solution_type == SOLUTIONS.Maxwell3d.Transient, "Motion applies only to the Transient setup."
        if not motion_name:
            motion_name = generate_unique_name("Motion")
        object_list = self.modeler.convert_to_selections(band_object, True)
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

    @pyaedt_function_handler()
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
    ):
        """Assign a rotation motion to an object container.

        Parameters
        ----------
        band_object : str,
            Object container.
        coordinate_system : str, optional
            Coordinate system name. The default is ``"Global"``.
        axis : str or int, optional
            Coordinate system axis. The default is ``"Z"``.
            It can be a ``pyaedt.generic.constants.AXIS`` enumerator value.
        positive_movement : bool, optional
            Whether the movement is positive. The default is ``True``.
        start_position : float or str, optional
            Starting position of the movement. The default is ``0``. If a float value
            is used, "deg" units are applied.
        has_rotation_limits : bool, optional
            Whether there is a limit in rotation. The default is ``False``.
        negative_limit : float or str, optional
            Negative limit of the movement. The default is ``0``. If a float value is
            used, "deg" units are applied.
        positive_limit : float or str, optional
            Positive limit of the movement. The default is ``360``. If a float value is used,
            "deg" units are applied.
        non_cylindrical : bool, optional
            Whether to consider non-cylindrical rotation. The default is ``False``.
        angular_velocity : float or str, optional
            Movement velocity. The default is ``"0rpm"``. If a float value is used,
            "rpm" units are applied.
        mechanical_transient : bool, optional
            Whether to consider mechanical movement. The default is ``False``.
        inertia : float, optional
            Mechanical inertia. The default is ``1``.
        damping : float, optional
            Damping factor. The default is ``0``.
        load_torque : float or str, optional
            Load force. The default is ``"0newton"``. If a float value is used,
            "NewtonMeter" units are applied.

        Returns
        -------
        :class:`pyaedt.modules.Boundary.BoundaryObject`
            Boundary object.

        References
        ----------

        >>> oModule.AssignBand
        """
        assert self.solution_type == SOLUTIONS.Maxwell3d.Transient, "Motion applies only to the Transient setup."
        names = list(self.omodelsetup.GetMotionSetupNames())
        motion_name = "MotionSetup" + str(len(names) + 1)
        object_list = self.modeler.convert_to_selections(band_object, True)
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

    @pyaedt_function_handler()
    def assign_voltage(self, face_list, amplitude=1, name=None):
        """Assign a voltage source to a list of faces in Maxwell 3D or a list of Objects in Maxwell 2D.

        Parameters
        ----------
        face_list : list
            List of faces or objects to assign a voltage source to.
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
        face_list = self.modeler.convert_to_selections(face_list, True)

        # if type(face_list) is not list and type(face_list) is not tuple:
        #     face_list = [face_list]
        if self.design_type == "Maxwell 2D":
            props = OrderedDict({"Objects": face_list, "Value": amplitude})
        else:
            props = OrderedDict({"Faces": face_list, "Voltage": amplitude})
        bound = BoundaryObject(self, name, props, "Voltage")
        if bound.create():
            self.boundaries.append(bound)
            return bound
        return False

    @pyaedt_function_handler()
    def assign_voltage_drop(self, face_list, amplitude=1, swap_direction=False, name=None):
        """Assign a voltage drop to a list of faces.

        Parameters
        ----------
        face_list : list
            List of faces to assign a voltage drop to.
        amplitude : float, optional
            Voltage amplitude in mV. The default is ``1``.
        swap_direction : bool, optional
            Whether to swap the direction. The default value is ``False``.
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
        face_list = self.modeler.convert_to_selections(face_list, True)

        props = OrderedDict({"Faces": face_list, "Voltage Drop": amplitude, "Point out of terminal": swap_direction})
        bound = BoundaryObject(self, name, props, "VoltageDrop")
        if bound.create():
            self.boundaries.append(bound)
            return bound
        return False

    @pyaedt_function_handler()
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
            Whether the winding is the solid type. The default is ``True``. If ``False``,
            the winding is the stranded type.
        current_value : float, optional
            Value of the current in amperes. The default is ``1``.
        res : float, optional
            Resistance in ohms. The default is ``0``.
        ind : float, optional
            Henry (H). The default is ``0``.
        voltage : float, optional
            Voltage value. The default is ``0``.
        parallel_branches : int, optional
            Number of parallel branches. The default is ``1``.
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
                "Current": self.modeler._arg_with_dim(current_value, "A"),
                "Resistance": self.modeler._arg_with_dim(res, "ohm"),
                "Inductance": self.modeler._arg_with_dim(ind, "H"),
                "Voltage": self.modeler._arg_with_dim(voltage, "V"),
                "ParallelBranchesNum": str(parallel_branches),
            }
        )
        bound = BoundaryObject(self, name, props, "Winding")
        if bound.create():
            self.boundaries.append(bound)
            if coil_terminals is None:
                coil_terminals = []
            if type(coil_terminals) is not list:
                coil_terminals = [coil_terminals]
            coil_names = []
            for coil in coil_terminals:
                c = self.assign_coil(coil)
                if c:
                    coil_names.append(c.name)

            if coil_names:
                self.add_winding_coils(bound.name, coil_names)
            return bound
        return False

    @pyaedt_function_handler()
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

    @pyaedt_function_handler()
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
        if polarity.lower() == "positive":
            point = False
        else:
            point = True

        input_object = self.modeler.convert_to_selections(input_object, True)

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
                    {
                        "Objects": input_object,
                        "Conductor number": str(conductor_number),
                        "PolarityType": polarity.lower(),
                    }
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

    @pyaedt_function_handler()
    def assign_force(self, input_object, reference_cs="Global", is_virtual=True, force_name=None):
        """Assign a force to one or more objects.

        Parameters
        ----------
        input_object : str, list
            One or more objects to assign the force to.
        reference_cs : str, optional
            Name of the reference coordinate system. The default is ``"Global"``.
        is_virtual : bool, optional
            Whether the force is virtual. The default is ``True.``
        force_name : str, optional
            Name of the force. The default is ``None``, in which case the default
            name is used.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.

        References
        ----------

        >>> oModule.AssignForce
        """
        if self.solution_type not in ["ACConduction", "DCConduction"]:
            input_object = self.modeler.convert_to_selections(input_object, True)
            if not force_name:
                force_name = generate_unique_name("Force")
            if self.design_type == "Maxwell 3D":
                prop = OrderedDict(
                    {
                        "Name": force_name,
                        "Reference CS": reference_cs,
                        "Is Virtual": is_virtual,
                        "Objects": input_object,
                    }
                )
            else:
                prop = OrderedDict(
                    {
                        "Name": force_name,
                        "Reference CS": reference_cs,
                        "Objects": input_object,
                    }
                )

            bound = MaxwellParameters(self, force_name, prop, "Force")
            if bound.create():
                self.boundaries.append(bound)
                return bound
        else:
            self.logger.error("Solution Type has not Matrix Parameter")
            return False

    @pyaedt_function_handler()
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
            Name of the torque. The default is ``None``, in which
            case the default name is used.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.

        References
        ----------

        >>> oModule.AssignTorque
        """
        if self.solution_type not in ["ACConduction", "DCConduction"]:
            if self.solution_type == "Transient":
                is_virtual = True
            input_object = self.modeler.convert_to_selections(input_object, True)
            if not torque_name:
                torque_name = generate_unique_name("Torque")
            if self.design_type == "Maxwell 3D":
                prop = OrderedDict(
                    {
                        "Name": torque_name,
                        "Is Virtual": is_virtual,
                        "Coordinate System": reference_cs,
                        "Axis": axis,
                        "Is Positive": is_positive,
                        "Objects": input_object,
                    }
                )
            else:
                prop = OrderedDict(
                    {
                        "Name": torque_name,
                        "Coordinate System": reference_cs,
                        "Is Positive": is_positive,
                        "Objects": input_object,
                    }
                )

            bound = MaxwellParameters(self, torque_name, prop, "Torque")
            if bound.create():
                self.boundaries.append(bound)
                return bound
        else:
            self.logger.error("Solution Type has not Matrix Parameter")
            return False

    @pyaedt_function_handler()
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
        self.modeler[name].solve_inside = activate
        return True

    @pyaedt_function_handler()
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

    @pyaedt_function_handler()
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

    @pyaedt_function_handler()
    def assign_symmetry(self, entity_list, symmetry_name=None, is_odd=True):
        """Assign symmetry boundary.

        Parameters
        ----------
        entity_list : list
            List IDs or :class:`pyaedt.modeler.Object3d.EdgePrimitive` or
            :class:`pyaedt.modeler.Object3d.FacePrimitive`.
        symmetry_name : str, optional
            Name of the symmetry.
        is_odd : bool, optional
            Type of the symmetry. The default is ``True`,` in which case the H field
            is tangential to the boundary. If ``False``, the H field is normal to
            the boundary.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.

        References
        ----------

        >>> oModule.AssignSymmetry
        """
        try:
            if symmetry_name is None:
                symmetry_name = generate_unique_name("Symmetry")

            object_list = []
            if entity_list:
                if self.design_type == "Maxwell 2D":
                    for entity in entity_list:
                        if isinstance(entity, EdgePrimitive):
                            edge_id = entity.id
                        elif isinstance(entity, int):
                            edge_id = entity
                        else:
                            msg = "The input is not an edge object or an integer."
                            raise ValueError(msg)
                        object_list.append(edge_id)
                    prop = OrderedDict({"Name": symmetry_name, "Edges": object_list, "IsOdd": is_odd})
                else:
                    for entity in entity_list:
                        if isinstance(entity, FacePrimitive):
                            face_id = entity.id
                        elif isinstance(entity, int):
                            face_id = entity
                        else:
                            msg = "The input is not a valid face object or an integer."
                            raise ValueError(msg)
                        object_list.append(face_id)
                    prop = OrderedDict({"Name": symmetry_name, "Faces": object_list, "IsOdd": is_odd})
            else:
                msg = "At least one edge must be provided."
                ValueError(msg)

            bound = BoundaryObject(self, symmetry_name, prop, "Symmetry")
            if bound.create():
                self.boundaries.append(bound)
                return bound
            return True
        except:
            return False

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
        parameter is ignored when a script is launched within AEDT.
    non_graphical : bool, optional
        Whether to launch AEDT in non-graphical mode. The default
        is ``False``, in which case AEDT is launched in graphical
        mode. This parameter is ignored when a script is launched within
        AEDT.
    new_desktop_session : bool, optional
        Whether to launch an instance of AEDT in a new thread, even if
        another instance of the ``specified_version`` is active on the
        machine. The default is ``True``. This parameter is ignored
        when a script is launched within AEDT.
    close_on_exit : bool, optional
        Whether to release AEDT on exit. The default is ``False``.
    student_version : bool, optional
        Whether to open the AEDT student version. The default is
        ``False``. This parameter is ignored when a script is launched
        within AEDT.
    machine : str, optional
        Machine name to connect the oDesktop session to. This works only in 2022 R2
        or later. The remote server must be up and running with the command
        `"ansysedt.exe -grpcsrv portnum"`. If the machine is `"localhost"`, the
        server also starts if not present.
    port : int, optional
        Port number on which to start the oDesktop communication on an already existing server.
        This parameter is ignored when a new server is created. It works only in 2022 R2 or later.
        The remote server must be up and running with the command `"ansysedt.exe -grpcsrv portnum"`.
    aedt_process_id : int, optional
        Process ID for the instance of AEDT to point PyAEDT at. The default is
        ``None``. This parameter is only used when ``new_desktop_session = False``.

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
        machine="",
        port=0,
        aedt_process_id=None,
    ):
        """
        Initialize the ``Maxwell`` class.
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
            machine,
            port,
            aedt_process_id,
        )
        Maxwell.__init__(self)


class Maxwell2d(Maxwell, FieldAnalysis3D, object):
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
        This parameter is ignored when a script is launched within AEDT.
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
        Machine name to connect the oDesktop session to. This works only in 2022 R2
        or later. The remote server must be up and running with the command
        `"ansysedt.exe -grpcsrv portnum"`. If the machine is `"localhost"`,
        the server also starts if not present.
    port : int, optional
        Port number of which to start the oDesktop communication on an already existing
        server. This parameter is ignored when creating a new server. It works only in 2022
        R2 or later. The remote server must be up and running with the command `"ansysedt.exe -grpcsrv portnum"`.
    aedt_process_id : int, optional
        Process ID for the instance of AEDT to point PyAEDT at. The default is
        ``None``. This parameter is only used when ``new_desktop_session = False``.

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
        machine="",
        port=0,
        aedt_process_id=None,
    ):
        self.is3d = False
        FieldAnalysis3D.__init__(
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
            machine,
            port,
            aedt_process_id,
        )
        Maxwell.__init__(self)

    @property
    def xy_plane(self):
        """Maxwell 2D plane between ``True`` and ``False``."""
        return self.design_solutions.xy_plane

    @xy_plane.setter
    @pyaedt_function_handler()
    def xy_plane(self, value=True):
        self.design_solutions.xy_plane = value

    @property
    def model_depth(self):
        """Model depth."""

        if "ModelDepth" in self.design_properties:
            value_str = self.design_properties["ModelDepth"]
            try:
                a = float_units(value_str)
            except:
                a = self.variable_manager[value_str].value
            finally:
                return a
        else:
            return None

    @model_depth.setter
    def model_depth(self, value):
        """Set model depth."""
        return self.change_design_settings(
            {"ModelDepth": self._modeler._arg_with_dim(value, self._modeler.model_units)}
        )

    @pyaedt_function_handler()
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
            solid_ids = [i for i, j in self.modeler.object_id_dict.items() if j.name in objectfilter]
        else:
            solid_ids = [i for i in list(self.modeler.object_id_dict.keys())]
        self.design_data = {
            "Project Directory": self.project_path,
            "Working Directory": self.working_directory,
            "Library Directories": self.library_list,
            "Dimension": self.modeler.dimension,
            "GeoMode": self.geometry_mode,
            "ModelUnits": self.modeler.model_units,
            "Symmetry": self.symmetry_multiplier,
            "ModelDepth": self.model_depth,
            "ObjectList": solid_ids,
            "LineList": self.modeler.vertex_data_of_lines(linefilter),
            "VarList": self.variable_manager.variable_names,
            "Setups": self.existing_analysis_setups,
            "MaterialProperties": self.get_object_material_properties(solid_bodies),
        }

        design_file = os.path.join(self.working_directory, "design_data.json")
        with open_file(design_file, "w") as fps:
            json.dump(convert(self.design_data), fps, indent=4)
        return True

    @pyaedt_function_handler()
    def read_design_data(self):
        """Read back the design data as a dictionary.

        Returns
        -------
        dict
            Dictionary of design data.

        """
        design_file = os.path.join(self.working_directory, "design_data.json")
        with open_file(design_file, "r") as fps:
            design_data = json.load(fps)
        return design_data

    @pyaedt_function_handler()
    def assign_balloon(self, edge_list, bound_name=None):
        """Assign a balloon boundary to a list of edges.

        Parameters
        ----------
        edge_list : list
            List of edges.
        bound_name : str, optional
            Name of the boundary. The default is ``None``, in which
            case the default name is used.

        Returns
        -------
        :class:`pyaedt.modules.Boundary.BoundaryObject`
            Boundary object.

        References
        ----------

        >>> oModule.AssignBalloon
        """
        edge_list = self.modeler.convert_to_selections(edge_list, True)

        if not bound_name:
            bound_name = generate_unique_name("Balloon")

        props2 = OrderedDict({"Edges": edge_list})
        bound = BoundaryObject(self, bound_name, props2, "Balloon")

        if bound.create():
            self.boundaries.append(bound)
            return bound
        return False

    @pyaedt_function_handler()
    def assign_vector_potential(self, input_edge, vectorvalue=0, bound_name=None):
        """Assign a vector to a list of edges.

        Parameters
        ----------
        input_edge : list
            List of edge names or edge IDs to assign a vector to.
        vectorvalue : float, optional
            Value of the vector. The default is ``0``.
        bound_name : str, optional
            Name of the boundary. The default is ``None``, in which
            case the default name is used.

        Returns
        -------
        :class:`pyaedt.modules.Boundary.BoundaryObject`
            Vector Potential Object

        References
        ----------

        >>> oModule.AssignVectorPotential
        """
        input_edge = self.modeler.convert_to_selections(input_edge, True)

        if not bound_name:
            bound_name = generate_unique_name("Vector")
        if type(input_edge[0]) is str:
            props2 = OrderedDict({"Objects": input_edge, "Value": str(vectorvalue), "CoordinateSystem": ""})
        else:
            props2 = OrderedDict({"Edges": input_edge, "Value": str(vectorvalue), "CoordinateSystem": ""})
        bound = BoundaryObject(self, bound_name, props2, "Vector Potential")

        if bound.create():
            self.boundaries.append(bound)
            return bound
        return False

    @pyaedt_function_handler()
    def assign_master_slave(
        self, master_edge, slave_edge, reverse_master=False, reverse_slave=False, same_as_master=True, bound_name=None
    ):
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
            Name of the master boundary. The default is ``None``, in which case the default name
            is used. The name of the slave boundary has a ``_dep`` suffix.

        Returns
        -------
        :class:`pyaedt.modules.Boundary.BoundaryObject`, :class:`pyaedt.modules.Boundary.BoundaryObject`
            Master and slave objects.

        References
        ----------

        >>> oModule.AssignIndependent
        >>> oModule.AssignDependent
        """
        master_edge = self.modeler.convert_to_selections(master_edge, True)
        slave_edge = self.modeler.convert_to_selections(slave_edge, True)
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

            props2 = OrderedDict(
                {
                    "Edges": slave_edge,
                    "ReverseU": reverse_slave,
                    "Independent": bound_name_m,
                    "SameAsMaster": same_as_master,
                }
            )
            bound2 = BoundaryObject(self, bound_name_s, props2, "Dependent")
            if bound2.create():
                self.boundaries.append(bound2)
                return bound, bound2
            else:
                return bound, False
        return False, False

    @pyaedt_function_handler()
    def assign_end_connection(self, objects, resistance=0, inductance=0, bound_name=None):
        """Assign an end connection to a list of objects.

        Parameters
        ----------
        objects : list of int or str or :class:`pyaedt.modeler.Object3d.Object3d`
            List of objects to assign an end connection to.
        resistance : float or str, optional
            Resistance value. If float is provided, the units are assumed to be ohms.
            The default value is ``0``,
        inductance : float or str, optional
            Inductance value. If a float is provided, the units are assumed to Henry (H).
            The default value is ``0``.
        bound_name : str, optional
            Name of the end connection boundary. The default is ``None``, in which case the
            default name is used.

        Returns
        -------
        :class:`pyaedt.modules.Boundary.BoundaryObject`
            New created object.

        References
        ----------

        >>> oModule.AssignEndConnection
        """
        if self.solution_type not in ["EddyCurrent", "Transient"]:
            self.logger.error("Excitation applicable only to Eddy current or Transient Solver.")
            return False
        if len(objects) < 2:
            self.logger.error("At least 2 objects are needed.")
            return False
        objects = self.modeler.convert_to_selections(objects, True)
        if not bound_name:
            bound_name = generate_unique_name("EndConnection")

        props = OrderedDict(
            {
                "Objects": objects,
                "ResistanceValue": self.modeler._arg_with_dim(resistance, "ohm"),
                "InductanceValue": self.modeler._arg_with_dim(inductance, "H"),
            }
        )
        bound = BoundaryObject(self, bound_name, props, "EndConnection")
        if bound.create():
            self.boundaries.append(bound)
            return bound
        return False
