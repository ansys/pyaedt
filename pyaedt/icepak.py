"""This module contains the ``Icepak`` class."""

from __future__ import absolute_import  # noreorder

from collections import OrderedDict
import csv
import math
import os
import warnings

from pyaedt import is_ironpython
from pyaedt import is_linux
from pyaedt.generic.general_methods import GrpcApiError
from pyaedt.modeler.cad.elements3d import FacePrimitive
from pyaedt.modules.SetupTemplates import SetupKeys

if is_linux and is_ironpython:
    import subprocessdotnet as subprocess
else:
    import subprocess

import re

from pyaedt.application.Analysis3D import FieldAnalysis3D
from pyaedt.generic.DataHandlers import _arg2dict
from pyaedt.generic.DataHandlers import random_string
from pyaedt.generic.configurations import ConfigurationsIcepak
from pyaedt.generic.general_methods import generate_unique_name
from pyaedt.generic.general_methods import open_file
from pyaedt.generic.general_methods import pyaedt_function_handler
from pyaedt.generic.settings import settings
from pyaedt.modeler.cad.components_3d import UserDefinedComponent
from pyaedt.modeler.geometry_operators import GeometryOperators
from pyaedt.modules.Boundary import BoundaryObject
from pyaedt.modules.Boundary import NativeComponentObject
from pyaedt.modules.Boundary import NetworkObject
from pyaedt.modules.Boundary import _create_boundary
from pyaedt.modules.monitor_icepak import Monitor


class Icepak(FieldAnalysis3D):
    """Provides the Icepak application interface.

    This class allows you to connect to an existing Icepak design or create a
    new Icepak design if one does not exist.

    Parameters
    ----------
    projectname : str, optional
        Name of the project to select or the full path to the project
        or AEDTZ archive to open.  The default is ``None``, in which
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
    specified_version : str, int, float, optional
        Version of AEDT to use. The default is ``None``, in which case
        the active version or latest installed version is  used.
        This parameter is ignored when Script is launched within AEDT.
        Examples of input values are ``232``, ``23.2``,``2023.2``,``"2023.2"``.
    non-graphical : bool, optional
        Whether to launch AEDT in non-graphical mode. The default
        is ``False``, in which case AEDT is launched in graphical mode.
        This parameter is ignored when a script is launched within AEDT.
    new_desktop_session : bool, optional
        Whether to launch an instance of AEDT in a new thread, even if
        another instance of the ``specified_version`` is active on the
        machine.  The default is ``True``.
    close_on_exit : bool, optional
        Whether to release AEDT on exit. The default is ``False``.
    student_version : bool, optional
        Whether to open the AEDT student version. The default is ``False``.
        This parameter is ignored when a script is launched within AEDT.
    machine : str, optional
        Machine name to connect the oDesktop session to. This works only in 2022 R2 or later.
        The remote server must be up and running with the command `"ansysedt.exe -grpcsrv portnum"`.
        If the machine is `"localhost"`, the server also starts if not present.
    port : int, optional
        Port number of which to start the oDesktop communication on an already existing server.
        This parameter is ignored when creating a new server. It works only in 2022 R2 or later.
        The remote server must be up and running with the command `"ansysedt.exe -grpcsrv portnum"`.
    aedt_process_id : int, optional
        Process ID for the instance of AEDT to point PyAEDT at. The default is
        ``None``. This parameter is only used when ``new_desktop_session = False``.

    Examples
    --------

    Create an instance of Icepak and connect to an existing Icepak
    design or create a new Icepak design if one does not exist.

    >>> from pyaedt import Icepak
    >>> icepak = Icepak()
    PyAEDT INFO: No project is defined. Project ...
    PyAEDT INFO: Active design is set to ...

    Create an instance of Icepak and link to a project named
    ``IcepakProject``. If this project does not exist, create one with
    this name.

    >>> icepak = Icepak("IcepakProject")
    PyAEDT INFO: Project ...
    PyAEDT INFO: Added design ...

    Create an instance of Icepak and link to a design named
    ``IcepakDesign1`` in a project named ``IcepakProject``.

    >>> icepak = Icepak("IcepakProject", "IcepakDesign1")
    PyAEDT INFO: Added design 'IcepakDesign1' of type Icepak.

    Create an instance of Icepak and open the specified project,
    which is ``myipk.aedt``.

    >>> icepak = Icepak("myipk.aedt")
    PyAEDT INFO: Project myipk has been created.
    PyAEDT INFO: No design is present. Inserting a new design.
    PyAEDT INFO: Added design ...

    Create an instance of Icepak using the 2023 R2 release and
    open the specified project, which is ``myipk2.aedt``.

    >>> icepak = Icepak(specified_version=2023.2, projectname="myipk2.aedt")
    PyAEDT INFO: Project...
    PyAEDT INFO: No design is present. Inserting a new design.
    PyAEDT INFO: Added design...
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
        FieldAnalysis3D.__init__(
            self,
            "Icepak",
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
        self._monitor = Monitor(self)
        self._configurations = ConfigurationsIcepak(self)

    def _init_from_design(self, *args, **kwargs):
        self.__init__(*args, **kwargs)

    def __enter__(self):
        return self

    @property
    def problem_type(self):
        """Problem type of the Icepak design. Options are ``"TemperatureAndFlow"``, ``"TemperatureOnly"``,
        and ``"FlowOnly"``.
        """
        return self.design_solutions.problem_type

    @problem_type.setter
    def problem_type(self, value="TemperatureAndFlow"):
        self.design_solutions.problem_type = value

    @property
    def existing_analysis_sweeps(self):
        """Existing analysis setups.

        Returns
        -------
        list of str
            List of all analysis setups in the design.

        """
        setup_list = self.existing_analysis_setups
        sweep_list = []
        s_type = self.solution_type
        for el in setup_list:
            sweep_list.append(el + " : " + s_type)
        return sweep_list

    @property
    def monitor(self):
        """Property to handle monitor objects.

        Returns
        -------
        :class:`pyaedt.modules.monitor_icepak.Monitor`
        """
        self._monitor._delete_removed_monitors()  # force update. some operations may delete monitors
        return self._monitor

    @pyaedt_function_handler()
    def assign_grille(
        self,
        air_faces,
        free_loss_coeff=True,
        free_area_ratio=0.8,
        resistance_type=0,
        external_temp="AmbientTemp",
        expternal_pressure="AmbientPressure",
        x_curve=["0", "1", "2"],
        y_curve=["0", "1", "2"],
        boundary_name=None,
    ):
        """Assign grille to a face or list of faces.

        Parameters
        ----------
        air_faces : str, list
            List of face names.
        free_loss_coeff : bool
            Whether to use the free loss coefficient. The default is ``True``. If ``False``,
            the free loss coefficient is not used.
        free_area_ratio : float, str
            Free loss coefficient value. The default is ``0.8``.
        resistance_type : int, optional
            Type of the resistance. Options are:

            - ``0`` for ``"Perforated Thin Vent"``
            - ``1`` for ``"Circular Metal Wire Screen"``
            - ``2`` for ``"Two-Plane Screen Cyl. Bars"``

            The default is ``0`` for ``"Perforated Thin Vent"``.
        external_temp : str, optional
            External temperature. The default is ``"AmbientTemp"``.
        expternal_pressure : str, optional
            External pressure. The default is ``"AmbientPressure"``.
        x_curve : list, optional
            List of X curves in m_per_sec. The default is ``["0", "1", "2"]``.
        y_curve : list
            List of Y curves in n_per_meter_q. The default is ``["0", "1", "2"]``.
        boundary_name : str, optional
            Boundary name. The default is ``None``, in which case the name will
            be generated automatically.

        Returns
        -------
        :class:`pyaedt.modules.Boundary.BoundaryObject`
            Boundary object when successful or ``None`` when failed.

        References
        ----------

        >>> oModule.AssignGrilleBoundary
        """
        if boundary_name is None:
            boundary_name = generate_unique_name("Grille")

        self.modeler.create_face_list(air_faces, "boundary_faces" + boundary_name)
        props = {}
        air_faces = self.modeler.convert_to_selections(air_faces, True)

        props["Faces"] = air_faces
        if free_loss_coeff:
            props["Pressure Loss Type"] = "Coeff"
            props["Free Area Ratio"] = str(free_area_ratio)
            props["External Rad. Temperature"] = external_temp
            props["External Total Pressure"] = expternal_pressure

        else:
            props["Pressure Loss Type"] = "Curve"
            props["External Rad. Temperature"] = external_temp
            props["External Total Pressure"] = expternal_pressure

        props["X"] = x_curve
        props["Y"] = y_curve
        bound = BoundaryObject(self, boundary_name, props, "Grille")
        if bound.create():
            self._boundaries[bound.name] = bound
            self.logger.info("Grille Assigned")
            return bound
        return None

    @pyaedt_function_handler()
    def assign_openings(self, air_faces):
        """Assign openings to a list of faces.

        Parameters
        ----------
        air_faces : list
            List of face names.

        Returns
        -------
        :class:`pyaedt.modules.Boundary.BoundaryObject`
            Boundary object when successful or ``None`` when failed.

        References
        ----------

        >>> oModule.AssignOpeningBoundary

        Examples
        --------

        Create an opening boundary for the faces of the ``"USB_GND"`` object.

        >>> faces = icepak.modeler["USB_GND"].faces
        >>> face_names = [face.id for face in faces]
        >>> boundary = icepak.assign_openings(face_names)
        PyAEDT INFO: Face List boundary_faces created
        PyAEDT INFO: Opening Assigned
        """
        boundary_name = generate_unique_name("Opening")
        self.modeler.create_face_list(air_faces, "boundary_faces" + boundary_name)
        props = {}
        air_faces = self.modeler.convert_to_selections(air_faces, True)

        props["Faces"] = air_faces
        props["Temperature"] = "AmbientTemp"
        props["External Rad. Temperature"] = "AmbientRadTemp"
        props["Inlet Type"] = "Pressure"
        props["Total Pressure"] = "AmbientPressure"
        bound = BoundaryObject(self, boundary_name, props, "Opening")
        if bound.create():
            self._boundaries[bound.name] = bound
            self.logger.info("Opening Assigned")
            return bound
        return None

    @pyaedt_function_handler()
    def assign_2way_coupling(
        self, setup_name=None, number_of_iterations=2, continue_ipk_iterations=True, ipk_iterations_per_coupling=20
    ):
        """Assign two-way coupling to a setup.

        Parameters
        ----------
        setup_name : str, optional
            Name of the setup. The default is ``None``, in which case the active setup is used.
        number_of_iterations : int, optional
            Number of iterations. The default is ``2``.
        continue_ipk_iterations : bool, optional
           Whether to continue Icepak iterations. The default is ``True``.
        ipk_iterations_per_coupling : int, optional
            Additional iterations per coupling. The default is ``20``.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.

        References
        ----------

        >>> oModule.AddTwoWayCoupling

        Examples
        --------

        >>> icepak.assign_2way_coupling("Setup1", 1, True, 10)
        True

        """
        if not setup_name:
            if self.setups:
                setup_name = self.setups[0].name
            else:
                self.logger.error("No setup is defined.")
                return False
        self.oanalysis.AddTwoWayCoupling(
            setup_name,
            [
                "NAME:Options",
                "NumCouplingIters:=",
                number_of_iterations,
                "ContinueIcepakIterations:=",
                continue_ipk_iterations,
                "IcepakIterationsPerCoupling:=",
                ipk_iterations_per_coupling,
            ],
        )
        return True

    @pyaedt_function_handler()
    def create_source_blocks_from_list(self, list_powers, assign_material=True, default_material="Ceramic_material"):
        """Assign to a box in Icepak the sources that come from the CSV file.

        Assignment is made by name.

        Parameters
        ----------
        list_powers : list
            List of input powers. It is a list of lists. For example,
            ``[["Obj1", 1], ["Obj2", 3]]``. The list can contain multiple
            columns for power inputs.
        assign_material : bool, optional
            Whether to assign a material. The default is ``True``.
        default_material : str, optional
            Default material to assign when ``assign_material=True``.
            The default is ``"Ceramic_material"``.

        Returns
        -------
        list of :class:`pyaedt.modules.Boundary.BoundaryObject`
            List of boundaries inserted.

        References
        ----------

        >>> oModule.AssignBlockBoundary

        Examples
        --------

        Create block boundaries from each box in the list.

        >>> box1 = icepak.modeler.create_box([1, 1, 1], [3, 3, 3], "BlockBox1", "copper")
        >>> box2 = icepak.modeler.create_box([2, 2, 2], [4, 4, 4], "BlockBox2", "copper")
        >>> blocks = icepak.create_source_blocks_from_list([["BlockBox1", 2], ["BlockBox2", 4]])
        PyAEDT INFO: Block on ...
        >>> blocks[1].props
        {'Objects': ['BlockBox1'], 'Block Type': 'Solid', 'Use External Conditions': False, 'Total Power': '2W'}
        >>> blocks[3].props
        {'Objects': ['BlockBox2'], 'Block Type': 'Solid', 'Use External Conditions': False, 'Total Power': '4W'}
        """
        oObjects = self.modeler.solid_names
        listmcad = []
        num_power = None
        for row in list_powers:
            if not num_power:
                num_power = len(row) - 1
                self["P_index"] = 0
            if row[0] in oObjects:
                listmcad.append(row)
                if num_power > 1:
                    self[row[0] + "_P"] = str(row[1:])
                    out = self.create_source_block(row[0], row[0] + "_P[P_index]", assign_material, default_material)

                else:
                    out = self.create_source_block(row[0], str(row[1]) + "W", assign_material, default_material)
                if out:
                    listmcad.append(out)

        return listmcad

    @pyaedt_function_handler()
    def create_source_block(
        self, object_name, input_power, assign_material=True, material_name="Ceramic_material", use_object_for_name=True
    ):
        """Create a source block for an object.

        .. deprecated:: 0.6.75
            This method is deprecated. Use the ``assign_solid_block()`` method instead.

        Parameters
        ----------
        object_name : str, list
            Name of the object.
        input_power : str or var
            Input power.
        assign_material : bool, optional
            Whether to assign a material. The default is ``True``.
        material_name :
            Material to assign if ``assign_material=True``. The default is ``"Ceramic_material"``.
        use_object_for_name : bool, optional
            Whether to use the object name for the source block name. The default is ``True``.

        Returns
        -------
        :class:`pyaedt.modules.Boundary.BoundaryObject`
            Boundary object when successful or ``None`` when failed.

        References
        ----------

        >>> oModule.AssignBlockBoundary

        Examples
        --------

        >>> box = icepak.modeler.create_box([5, 5, 5], [1, 2, 3], "BlockBox3", "copper")
        >>> block = icepak.create_source_block("BlockBox3", "1W", False)
        PyAEDT INFO: Block on ...
        >>> block.props
        {'Objects': ['BlockBox3'], 'Block Type': 'Solid', 'Use External Conditions': False, 'Total Power': '1W'}

        """
        if assign_material:
            if isinstance(object_name, list):
                for el in object_name:
                    self.modeler[el].material_name = material_name
            else:
                self.modeler[object_name].material_name = material_name
        props = {}
        if not isinstance(object_name, list):
            object_name = [object_name]
        object_name = self.modeler.convert_to_selections(object_name, True)
        props["Objects"] = object_name

        props["Block Type"] = "Solid"
        props["Use External Conditions"] = False
        props["Total Power"] = input_power
        if use_object_for_name:
            boundary_name = object_name[0]
        else:
            boundary_name = generate_unique_name("Block")

        bound = BoundaryObject(self, boundary_name, props, "Block")
        if bound.create():
            self._boundaries[bound.name] = bound
            self.logger.info("Block on {} with {} power created correctly.".format(object_name, input_power))
            return bound
        return None

    @pyaedt_function_handler()
    def create_conduting_plate(
        self,
        face_id,
        thermal_specification,
        thermal_dependent_dataset=None,
        input_power="0W",
        radiate_low=False,
        low_surf_material="Steel-oxidised-surface",
        radiate_high=False,
        high_surf_material="Steel-oxidised-surface",
        shell_conduction=False,
        thickness="1mm",
        solid_material="Al-Extruded",
        thermal_conductance="0W_per_Cel",
        thermal_resistance="0Kel_per_W",
        thermal_impedance="0celm2_per_w",
        bc_name=None,
    ):
        """Add a conductive plate thermal assignment on a face.

        .. deprecated:: 0.7.8
            This method is deprecated. Use the ``assign_conducting_plate()`` method instead.

        Parameters
        ----------
        face_id : int or str or list
            Integer indicating a face ID or a string indicating an object name. A list of face
            IDs or object names is also accepted.
        thermal_specification : str
            Select what thermal specification is to be applied. The possible choices are ``"Thickness"``,
            ``"Conductance"``, ``"Thermal Impedance"`` and ``"Thermal Resistance"``
        thermal_dependent_dataset : str, optional
            Name of the dataset if a thermal dependent power source is to be assigned. The default is ``None``.
        input_power : str, float, or int, optional
            Input power. The default is ``"0W"``. Ignored if thermal_dependent_dataset is set
        radiate_low : bool, optional
            Whether to enable radiation on the lower face. The default is ``False``.
        low_surf_material : str, optional
            Low surface material. The default is ``"Steel-oxidised-surface"``.
        radiate_high : bool, optional
            Whether to enable radiation on the higher face. The default is ``False``.
        high_surf_material : str, optional
            High surface material. The default is ``"Steel-oxidised-surface"``.
        shell_conduction : str, optional
            Whether to enable shell conduction. The default is ``False``.
        thickness : str, optional
            Thickness value, relevant only if ``thermal_specification="Thickness"``. The default is ``"1mm"``.
        thermal_conductance : str, optional
            Thermal Conductance value, relevant only if ``thermal_specification="Conductance"``.
            The default is ``"0W_per_Cel"``.
        thermal_resistance : str, optional
            Thermal resistance value, relevant only if ``thermal_specification="Thermal Resistance"``.
            The default is ``"0Kel_per_W"``.
        thermal_impedance : str, optional
            Thermal impedance value, relevant only if ``thermal_specification="Thermal Impedance"``.
            The default is ``"0celm2_per_w"``.
        solid_material : str, optional
            Material type for the wall. The default is ``"Al-Extruded"``.
        bc_name : str, optional
            Name of the plate. The default is ``None``.

        Returns
        -------
        :class:`pyaedt.modules.Boundary.BoundaryObject`
            Boundary object when successful or ``None`` when failed.

        """

        warnings.warn(
            "This method is deprecated in 0.7.8. Use the ``assign_conducting_plate()`` method.",
            DeprecationWarning,
        )

        if not bc_name:
            bc_name = generate_unique_name("Source")
        props = {}
        if not isinstance(face_id, list):
            face_id = [face_id]
        if isinstance(face_id[0], int):
            props["Faces"] = face_id
        elif isinstance(face_id[0], str):
            props["Objects"] = face_id
        if radiate_low:
            props["LowSide"] = OrderedDict(
                {"Radiate": True, "RadiateTo": "AllObjects", "Surface Material": low_surf_material}
            )
        else:
            props["LowSide"] = OrderedDict({"Radiate": False})
        if radiate_high:
            props["HighSide"] = OrderedDict(
                {"Radiate": True, "RadiateTo": "AllObjects - High", "Surface Material - High": high_surf_material}
            )
        else:
            props["HighSide"] = OrderedDict({"Radiate": False})
        props["Thermal Specification"] = thermal_specification
        props["Thickness"] = thickness
        props["Solid Material"] = solid_material
        props["Conductance"] = thermal_conductance
        props["Thermal Resistance"] = thermal_resistance
        props["Thermal Impedance"] = thermal_impedance
        if thermal_dependent_dataset is None:
            props["Total Power"] = input_power
        else:
            props["Total Power Variation Data"] = OrderedDict(
                {
                    "Variation Type": "Temp Dep",
                    "Variation Function": "Piecewise Linear",
                    "Variation Value": '["1W", "pwl({},Temp)"]'.format(thermal_dependent_dataset),
                }
            )
        props["Shell Conduction"] = shell_conduction
        bound = BoundaryObject(self, bc_name, props, "Conducting Plate")
        return _create_boundary(bound)

    @pyaedt_function_handler()
    def create_source_power(
        self,
        face_id,
        thermal_dependent_dataset=None,
        input_power=None,
        thermal_condtion="Total Power",
        surface_heat="0irrad_W_per_m2",
        temperature="AmbientTemp",
        radiate=False,
        source_name=None,
    ):
        """Create a source power for a face.

        .. deprecated:: 0.6.71
            This method is replaced by `assign_source`.

        Parameters
        ----------
        face_id : int or str
            If int, Face ID. If str, object name.
        thermal_dependent_dataset : str, optional
            Name of the dataset if a thermal dependent power source is to be assigned. The default is ``None``.
        input_power : str, float, or int, optional
            Input power. The default is ``"0W"``.
        thermal_condtion : str, optional
            Thermal condition. The default is ``"Total Power"``.
        surface_heat : str, optional
            Surface heat. The default is ``"0irrad_W_per_m2"``.
        temperature : str, optional
            Type of the temperature. The default is ``"AmbientTemp"``.
        radiate : bool, optional
            Whether to enable radiation. The default is ``False``.
        source_name : str, optional
            Name of the source. The default is ``None``.

        Returns
        -------
        :class:`pyaedt.modules.Boundary.BoundaryObject`
            Boundary object when successful or ``None`` when failed.

        References
        ----------

        >>> oModule.AssignSourceBoundary

        Examples
        --------

        Create two source boundaries from one box, one on the top face and one on the bottom face.

        >>> box = icepak.modeler.create_box([0, 0, 0], [20, 20, 20], name="SourceBox")
        >>> source1 = icepak.create_source_power(box.top_face_z.id, input_power="2W")
        >>> source1.props["Total Power"]
        '2W'
        >>> source2 = icepak.create_source_power(box.bottom_face_z.id,
        ...                                      thermal_condtion="Fixed Temperature",
        ...                                      temperature="28cel")
        >>> source2.props["Temperature"]
        '28cel'

        """
        if input_power == 0:
            input_power = "0W"
        if not bool(input_power) ^ bool(thermal_dependent_dataset):
            self.logger.error("Assign one input between ``thermal_dependent_dataset`` and  ``input_power``.")
        if not source_name:
            source_name = generate_unique_name("Source")
        props = {}
        if isinstance(face_id, int):
            props["Faces"] = [face_id]
        elif isinstance(face_id, str):
            props["Objects"] = [face_id]
        props["Thermal Condition"] = thermal_condtion
        if thermal_dependent_dataset is None:
            props["Total Power"] = input_power
        else:
            props["Total Power Variation Data"] = OrderedDict(
                {
                    "Variation Type": "Temp Dep",
                    "Variation Function": "Piecewise Linear",
                    "Variation Value": '["1W", "pwl({},Temp)"]'.format(thermal_dependent_dataset),
                }
            )
        props["Surface Heat"] = surface_heat
        props["Temperature"] = temperature
        props["Radiation"] = OrderedDict({"Radiate": radiate})
        bound = BoundaryObject(self, source_name, props, "SourceIcepak")
        return _create_boundary(bound)

    @pyaedt_function_handler()
    def create_network_block(
        self,
        object_name,
        power,
        rjc,
        rjb,
        gravity_dir,
        top=0,
        assign_material=True,
        default_material="Ceramic_material",
        use_object_for_name=True,
    ):
        """Create a network block.

        .. deprecated:: 0.6.27
            This method will be replaced by `create_two_resistor_network_block`.

        Parameters
        ----------
        object_name : str
            Name of the object to create the block for.
        power : str or var
            Input power.
        rjc : float
            RJC value.
        rjb : float
            RJB value.
        gravity_dir : int
            Gravity direction X to Z. Options are ``0`` to ``2``. Determines the orientation of network boundary faces.
        top : float, optional
            Chosen orientation (X to Z) coordinate value in millimeters of the top face of the board.
            The default is ''0 mm''.
            This parameter determines the casing and board side of the network.
        assign_material : bool, optional
            Whether to assign a material. The default is ``True``.
        default_material : str, optional
            Default material if ``assign_material=True``. The default is ``"Ceramic_material"``.
        use_object_for_name : bool, optional
             The default is ``True``.

        Returns
        -------
        :class:`pyaedt.modules.Boundary.BoundaryObject`
            Boundary object.

        References
        ----------

        >>> oModule.AssignNetworkBoundary

        Examples
        --------

        >>> box = icepak.modeler.create_box([4, 5, 6], [5, 5, 5], "NetworkBox1", "copper")
        >>> block = icepak.create_network_block("NetworkBox1", "2W", 20, 10, 2 , 1.05918)
        >>> block.props["Nodes"]["Internal"][0]
        '2W'
        """
        warnings.warn(
            "This method is deprecated in 0.6.27. Use the create_two_resistor_network_block() method.",
            DeprecationWarning,
        )
        if object_name in self.modeler.object_names:
            if gravity_dir > 2:
                gravity_dir = gravity_dir - 3
            faces_dict = self.modeler[object_name].faces
            faceCenter = {}
            for f in faces_dict:
                faceCenter[f.id] = f.center
            fcmax = -1e9
            fcmin = 1e9
            fcrjc = None
            fcrjb = None
            for fc in faceCenter:
                fc1 = faceCenter[fc]
                if fc1[gravity_dir] < fcmin:
                    fcmin = fc1[gravity_dir]
                    fcrjb = int(fc)
                if fc1[gravity_dir] > fcmax:
                    fcmax = fc1[gravity_dir]
                    fcrjc = int(fc)
            if fcmax < float(top):
                app = fcrjc
                fcrjc = fcrjb
                fcrjb = app
            if assign_material:
                self.modeler[object_name].material_name = default_material
            props = {}
            if use_object_for_name:
                boundary_name = object_name
            else:
                boundary_name = generate_unique_name("Block")
            props["Faces"] = [fcrjc, fcrjb]
            props["Nodes"] = OrderedDict(
                {
                    "Face" + str(fcrjc): [fcrjc, "NoResistance"],
                    "Face" + str(fcrjb): [fcrjb, "NoResistance"],
                    "Internal": [power],
                }
            )
            props["Links"] = OrderedDict(
                {
                    "Link1": ["Face" + str(fcrjc), "Internal", "R", str(rjc) + "cel_per_w"],
                    "Link2": ["Face" + str(fcrjb), "Internal", "R", str(rjb) + "cel_per_w"],
                }
            )
            props["SchematicData"] = OrderedDict({})
            bound = BoundaryObject(self, boundary_name, props, "Network")
            if bound.create():
                self._boundaries[bound.name] = bound
                self.modeler[object_name].solve_inside = False
                return bound
            return None

    @pyaedt_function_handler()
    def create_network_blocks(
        self, input_list, gravity_dir, top=0, assign_material=True, default_material="Ceramic_material"
    ):
        """Create network blocks from CSV files.

        Parameters
        ----------
        input_list : list
            List of sources with inputs ``rjc``, ``rjb``, and ``power``.
            For example, ``[[Objname1, rjc, rjb, power1, power2, ...], [Objname2, rjc2, rbj2, power1, power2, ...]]``.
        gravity_dir : int
            Gravity direction X to Z. Options are ``0`` to ``2``. This parameter determines the orientation of network
            boundary faces.
        top : float, optional
            Chosen orientation (X to Z) coordinate value in millimeters of the top face of
            the board. The default is ''0 mm''. This parameter determines the casing and
            board side of the network.

        assign_material : bool, optional
            Whether to assign a material. The default is ``True``.
        default_material : str, optional
            Default material if ``assign_material=True``. The default is ``"Ceramic_material"``.

        Returns
        -------
        list of :class:`pyaedt.modules.Boundary.BoundaryObject`
            List of boundary objects created.

        References
        ----------

        >>> oModule.AssignNetworkBoundary

        Examples
        --------

        Create network boundaries from each box in the list.

        >>> box1 = icepak.modeler.create_box([1, 2, 3], [10, 10, 10], "NetworkBox2", "copper")
        >>> box2 = icepak.modeler.create_box([4, 5, 6], [5, 5, 5], "NetworkBox3", "copper")
        >>> blocks = icepak.create_network_blocks([["NetworkBox2", 20, 10, 3], ["NetworkBox3", 4, 10, 2]],
        ...                                        2, 1.05918, False)
        >>> blocks[0].props["Nodes"]["Internal"]
        ['3W']
        """
        objs = self.modeler.solid_names
        countpow = len(input_list[0]) - 3
        networks = []
        for row in input_list:
            if row[0] in objs:
                if countpow > 1:
                    self[row[0] + "_P"] = str(row[3:])
                    self["P_index"] = 0
                    out = self.create_network_block(
                        row[0],
                        row[0] + "_P[P_index]",
                        row[1],
                        row[2],
                        gravity_dir,
                        top,
                        assign_material,
                        default_material,
                    )
                else:
                    if not row[3]:
                        pow = "0W"
                    else:
                        pow = str(row[3]) + "W"
                    out = self.create_network_block(
                        row[0], pow, row[1], row[2], gravity_dir, top, assign_material, default_material
                    )
                if out:
                    networks.append(out)
        return networks

    @pyaedt_function_handler()
    def assign_surface_monitor(self, face_name, monitor_type="Temperature", monitor_name=None):
        """Assign a surface monitor.

        Parameters
        ----------
        face_name : str
            Name of the face.
        monitor_type : str, optional
            Type of the monitor.  The default is ``"Temperature"``.
        monitor_name : str, optional
            Name of the monitor. The default is ``None``, in which case
            the default name is used.

        Returns
        -------
        str
            Monitor name when successful, ``False`` when failed.

        References
        ----------

        >>> oModule.AssignFaceMonitor

        Examples
        --------

        Create a rectangle named ``"Surface1"`` and assign a temperature monitor to that surface.

        >>> surface = icepak.modeler.create_rectangle(icepak.PLANE.XY,
        ...                                           [0, 0, 0], [10, 20], name="Surface1")
        >>> icepak.assign_surface_monitor("Surface1", monitor_name="monitor")
        'monitor'
        """
        return self._monitor.assign_surface_monitor(face_name, monitor_quantity=monitor_type, monitor_name=monitor_name)

    @pyaedt_function_handler()
    def assign_point_monitor(self, point_position, monitor_type="Temperature", monitor_name=None):
        """Create and assign a point monitor.

        Parameters
        ----------
        point_position : list
            List of the ``[x, y, z]`` coordinates for the point.
        monitor_type : str, optional
            Type of the monitor. The default is ``"Temperature"``.
        monitor_name : str, optional
            Name of the monitor. The default is ``None``, in which case
            the default name is used.

        Returns
        -------
        str
            Monitor name when successful, ``False`` when failed.

        References
        ----------
        >>> oModule.AssignPointMonitor

        Examples
        --------
        Create a temperature monitor at the point ``[1, 1, 1]``.

        >>> icepak.assign_point_monitor([1, 1, 1], monitor_name="monitor1")
        'monitor1'

        """
        return self._monitor.assign_point_monitor(
            point_position, monitor_quantity=monitor_type, monitor_name=monitor_name
        )

    @pyaedt_function_handler()
    def assign_point_monitor_in_object(self, name, monitor_type="Temperature", monitor_name=None):
        """Assign a point monitor in the centroid of a specific object.

        Parameters
        ----------
        name : str
            Name of the object to assign monitor point to.
        monitor_type : str, optional
            Type of the monitor.  The default is ``"Temperature"``.
        monitor_name : str, optional
            Name of the monitor. The default is ``None``, in which case
            the default name is used.

        Returns
        -------
        str
            Monitor name when successful, ``False`` when failed.

        References
        ----------

        >>> oModule.AssignPointMonitor

        Examples
        --------

        Create a box named ``"BlockBox1"`` and assign a temperature monitor point to that object.

        >>> box = icepak.modeler.create_box([1, 1, 1], [3, 3, 3], "BlockBox1", "copper")
        >>> icepak.assign_point_monitor(box.name, monitor_name="monitor2")
        "'monitor2'
        """
        return self._monitor.assign_point_monitor_in_object(
            name, monitor_quantity=monitor_type, monitor_name=monitor_name
        )

    @pyaedt_function_handler()
    def assign_block_from_sherlock_file(self, csv_name):
        """Assign block power to components based on a CSV file from Sherlock.

        Parameters
        ----------
        csv_name : str
            Name of the CSV file.

        Returns
        -------
        type
            Total power applied.

        References
        ----------

        >>> oModule.AssignBlockBoundary
        """
        with open_file(csv_name) as csvfile:
            csv_input = csv.reader(csvfile)
            component_header = next(csv_input)
            data = list(csv_input)
            k = 0
            component_data = {}
            for el in component_header:
                component_data[el] = [i[k] for i in data]
                k += 1
        total_power = 0
        i = 0
        all_objects = self.modeler.object_names
        for power in component_data["Applied Power (W)"]:
            try:
                float(power)
                if "COMP_" + component_data["Ref Des"][i] in all_objects:
                    status = self.create_source_block(
                        "COMP_" + component_data["Ref Des"][i], str(power) + "W", assign_material=False
                    )
                    if not status:
                        self.logger.warning(
                            "Warning. Block %s skipped with %sW power.", component_data["Ref Des"][i], power
                        )
                    else:
                        total_power += float(power)
                elif component_data["Ref Des"][i] in all_objects:
                    status = self.create_source_block(
                        component_data["Ref Des"][i], str(power) + "W", assign_material=False
                    )
                    if not status:
                        self.logger.warning(
                            "Warning. Block %s skipped with %sW power.", component_data["Ref Des"][i], power
                        )
                    else:
                        total_power += float(power)
            except:
                pass
            i += 1
        self.logger.info("Blocks inserted with total power %sW.", total_power)
        return total_power

    @pyaedt_function_handler()
    def assign_priority_on_intersections(self, component_prefix="COMP_"):
        """Validate an Icepak design.

        If there are intersections, priorities are automatically applied to overcome simulation issues.

        Parameters
        ----------
        component_prefix : str, optional
            Component prefix to search for. The default is ``"COMP_"``.

        Returns
        -------
        bool
             ``True`` when successful, ``False`` when failed.

        References
        ----------

        >>> oEditor.UpdatePriorityList
        """
        temp_log = os.path.join(self.working_directory, "validation.log")
        validate = self.odesign.ValidateDesign(temp_log)
        self.save_project()
        i = 2
        if validate == 0:
            priority_list = []
            with open_file(temp_log, "r") as f:
                lines = f.readlines()
                for line in lines:
                    if "[error]" in line and component_prefix in line and "intersect" in line:
                        id1 = line.find(component_prefix)
                        if self.aedt_version_id > "2023.2":
                            id2 = line[id1:].find(" ")
                        else:
                            id2 = line[id1:].find('"')
                        name = line[id1 : id1 + id2]
                        if name not in priority_list:
                            priority_list.append(name)
            self.logger.info("{} Intersections have been found. Applying Priorities".format(len(priority_list)))
            for objname in priority_list:
                self.mesh.add_priority(1, [objname], priority=i)
                i += 1
        return True

    @pyaedt_function_handler()
    def find_top(self, gravityDir):
        """Find the top location of the layout given a gravity.

        Parameters
        ----------
        gravityDir :
            Gravity direction from -X to +Z. Options are ``0`` to ``5``.

        Returns
        -------
        float
            Top position.

        References
        ----------

        >>> oEditor.GetModelBoundingBox
        """
        dirs = ["-X", "+X", "-Y", "+Y", "-Z", "+Z"]
        for dir in dirs:
            argsval = ["NAME:" + dir + " Padding Data", "Value:=", "0"]
            args = [
                "NAME:AllTabs",
                [
                    "NAME:Geometry3DCmdTab",
                    ["NAME:PropServers", "Region:CreateRegion:1"],
                    ["NAME:ChangedProps", argsval],
                ],
            ]
            self.modeler.oeditor.ChangeProperty(args)
        oBoundingBox = self.modeler.get_model_bounding_box()
        if gravityDir < 3:
            return oBoundingBox[gravityDir + 3]
        else:
            return oBoundingBox[gravityDir - 3]

    @pyaedt_function_handler()
    def create_parametric_fin_heat_sink(
        self,
        hs_height=100,
        hs_width=100,
        hs_basethick=10,
        pitch=20,
        thick=10,
        length=40,
        height=40,
        draftangle=0,
        patternangle=10,
        separation=5,
        symmetric=True,
        symmetric_separation=20,
        numcolumn_perside=2,
        vertical_separation=10,
        matname="Al-Extruded",
        center=[0, 0, 0],
        plane_enum=0,
        rotation=0,
        tolerance=1e-3,
    ):
        """Create a parametric heat sink.

        Parameters
        ----------
        hs_height : int, optional
            Height of the heat sink. The default is ``100``.
        hs_width : int, optional
            Width of the heat sink. The default is ``100``.
        hs_basethick : int, optional
            Thickness of the heat sink base. The default is ``10``.
        pitch : optional
            Pitch of the heat sink. The default is ``10``.
        thick : optional
            Thickness of the heat sink. The default is ``10``.
        length : optional
            Length of the heat sink. The default is ``40``.
        height : optional
            Height of the heat sink. The default is ``40``.
        draftangle : int, float, optional
            Draft angle in degrees. The default is ``0``.
        patternangle : int, float, optional
            Pattern angle in degrees. The default is ``10``.
        separation : optional
            The default is ``5``.
        symmetric : bool, optional
            Whether the heat sink is symmetric. The default is ``True``.
        symmetric_separation : optional
            The default is ``20``.
        numcolumn_perside : int, optional
            Number of columns per side. The default is ``2``.
        vertical_separation : optional
            The default is ``10``.
        matname : str, optional
            Name of the material. The default is ``Al-Extruded``.
        center : list, optional
           List of ``[x, y, z]`` coordinates for the center of
           the heatsink. The default is ``[0, 0, 0]``.
        plane_enum : str, int, optional
            Plane for orienting the heat sink.
            :class:`pyaedt.constants.PLANE` Enumerator can be used as input.
            The default is ``0``.
        rotation : int, float, optional
            The default is ``0``.
        tolerance : int, float, optional
            Tolerance value. The default is ``0.001``.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.

        Examples
        --------
        Create a symmetric fin heat sink.

        >>> from pyaedt import Icepak
        >>> icepak = Icepak()
        >>> icepak.insert_design("Heat_Sink_Example")
        >>> icepak.create_parametric_fin_heat_sink(draftangle=1.5, patternangle=8, numcolumn_perside=3,
        ...                                        vertical_separation=5.5, matname="Steel", center=[10, 0, 0],
        ...                                        plane_enum=icepak.PLANE.XY, rotation=45, tolerance=0.005)

        """
        all_objs = self.modeler.object_names
        self["FinPitch"] = self.modeler._arg_with_dim(pitch)
        self["FinThickness"] = self.modeler._arg_with_dim(thick)
        self["FinLength"] = self.modeler._arg_with_dim(length)
        self["FinHeight"] = self.modeler._arg_with_dim(height)
        self["DraftAngle"] = draftangle
        self["PatternAngle"] = patternangle
        self["FinSeparation"] = self.modeler._arg_with_dim(separation)
        self["VerticalSeparation"] = self.modeler._arg_with_dim(vertical_separation)
        self["HSHeight"] = self.modeler._arg_with_dim(hs_height)
        self["HSWidth"] = self.modeler._arg_with_dim(hs_width)
        self["HSBaseThick"] = self.modeler._arg_with_dim(hs_basethick)
        if numcolumn_perside > 1:
            self["NumColumnsPerSide"] = numcolumn_perside
        if symmetric:
            self["SymSeparation"] = self.modeler._arg_with_dim(symmetric_separation)
        self["Tolerance"] = self.modeler._arg_with_dim(tolerance)

        self.modeler.create_box(
            ["-HSWidth/200", "-HSHeight/200", "-HSBaseThick"],
            ["HSWidth*1.01", "HSHeight*1.01", "HSBaseThick+Tolerance"],
            "HSBase",
            matname,
        )
        fin_line = []
        fin_line.append(self.Position(0, 0, 0))
        fin_line.append(self.Position(0, "FinThickness", 0))
        fin_line.append(self.Position("FinLength", "FinThickness + FinLength*sin(PatternAngle*3.14/180)", 0))
        fin_line.append(self.Position("FinLength", "FinLength*sin(PatternAngle*3.14/180)", 0))
        fin_line.append(self.Position(0, 0, 0))
        self.modeler.create_polyline(fin_line, cover_surface=True, name="Fin")
        fin_line2 = []
        fin_line2.append(self.Position(0, "sin(DraftAngle*3.14/180)*FinThickness", "FinHeight"))
        fin_line2.append(self.Position(0, "FinThickness-sin(DraftAngle*3.14/180)*FinThickness", "FinHeight"))
        fin_line2.append(
            self.Position(
                "FinLength",
                "FinThickness + FinLength*sin(PatternAngle*3.14/180)-sin(DraftAngle*3.14/180)*FinThickness",
                "FinHeight",
            )
        )
        fin_line2.append(
            self.Position(
                "FinLength", "FinLength*sin(PatternAngle*3.14/180)+sin(DraftAngle*3.14/180)*FinThickness", "FinHeight"
            )
        )
        fin_line2.append(self.Position(0, "sin(DraftAngle*3.14/180)*FinThickness", "FinHeight"))
        self.modeler.create_polyline(fin_line2, cover_surface=True, name="Fin_top")
        self.modeler.connect(["Fin", "Fin_top"])
        self.modeler["Fin"].material_name = matname
        num = int((hs_width * 1.25 / (separation + thick)) / (max(1 - math.sin(patternangle * 3.14 / 180), 0.1)))
        self.modeler.move("Fin", self.Position(0, "-FinSeparation-FinThickness", 0))
        self.modeler.duplicate_along_line("Fin", self.Position(0, "FinSeparation+FinThickness", 0), num, True)
        all_names = self.modeler.object_names
        list = [i for i in all_names if "Fin" in i]
        if numcolumn_perside > 0:
            self.modeler.duplicate_along_line(
                list,
                self.Position("FinLength+VerticalSeparation", "FinLength*sin(PatternAngle*3.14/180)", 0),
                "NumColumnsPerSide",
                True,
            )

        all_names = self.modeler.object_names
        list = [i for i in all_names if "Fin" in i]
        self.modeler.split(list, self.PLANE.ZX, "PositiveOnly")
        all_names = self.modeler.object_names
        list = [i for i in all_names if "Fin" in i]
        self.modeler.create_coordinate_system(self.Position(0, "HSHeight", 0), mode="view", view="XY", name="TopRight")
        self.modeler.set_working_coordinate_system("TopRight")
        self.modeler.split(list, self.PLANE.ZX, "NegativeOnly")

        if symmetric:
            self.modeler.create_coordinate_system(
                self.Position("(HSWidth-SymSeparation)/2", 0, 0),
                mode="view",
                view="XY",
                name="CenterRightSep",
                reference_cs="TopRight",
            )

            self.modeler.split(list, self.PLANE.YZ, "NegativeOnly")
            self.modeler.create_coordinate_system(
                self.Position("SymSeparation/2", 0, 0),
                mode="view",
                view="XY",
                name="CenterRight",
                reference_cs="CenterRightSep",
            )
            self.modeler.duplicate_and_mirror(list, self.Position(0, 0, 0), self.Position(1, 0, 0))
            center_line = []
            center_line.append(self.Position("-SymSeparation", "Tolerance", "-Tolerance"))
            center_line.append(self.Position("SymSeparation", "Tolerance", "-Tolerance"))
            center_line.append(self.Position("VerticalSeparation", "-HSHeight-Tolerance", "-Tolerance"))
            center_line.append(self.Position("-VerticalSeparation", "-HSHeight-Tolerance", "-Tolerance"))
            center_line.append(self.Position("-SymSeparation", "Tolerance", "-Tolerance"))
            self.modeler.create_polyline(center_line, cover_surface=True, name="Center")
            self.modeler.thicken_sheet("Center", "-FinHeight-2*Tolerance")
            all_names = self.modeler.object_names
            list = [i for i in all_names if "Fin" in i]
            self.modeler.subtract(list, "Center", False)
        else:
            self.modeler.create_coordinate_system(
                self.Position("HSWidth", 0, 0), mode="view", view="XY", name="BottomRight", reference_cs="TopRight"
            )
            self.modeler.split(list, self.PLANE.YZ, "NegativeOnly")
        all_objs2 = self.modeler.object_names
        list_to_move = [i for i in all_objs2 if i not in all_objs]
        center[0] -= hs_width / 2
        center[1] -= hs_height / 2
        center[2] += hs_basethick
        self.modeler.set_working_coordinate_system("Global")
        self.modeler.move(list_to_move, center)
        if plane_enum == self.PLANE.XY:
            self.modeler.rotate(list_to_move, self.AXIS.X, rotation)
        elif plane_enum == self.PLANE.ZX:
            self.modeler.rotate(list_to_move, self.AXIS.X, 90)
            self.modeler.rotate(list_to_move, self.AXIS.Y, rotation)
        elif plane_enum == self.PLANE.YZ:
            self.modeler.rotate(list_to_move, self.AXIS.Y, 90)
            self.modeler.rotate(list_to_move, self.AXIS.Z, rotation)
        self.modeler.unite(list_to_move)
        self.modeler[list_to_move[0]].name = "HeatSink1"
        return True

    # fmt: off
    @pyaedt_function_handler()
    def edit_design_settings(
            self,
            gravity_dir=0,
            ambtemp=20,
            performvalidation=False,
            check_level="None",
            defaultfluid="air",
            defaultsolid="Al-Extruded",
            export_monitor=False,
            export_directory=os.getcwd(),
            gauge_pressure=0,
            radiation_temperature=20,
            ignore_unclassified_objects=False,
            skip_intersection_checks=False,
            **kwargs
    ):
        # fmt: on
        """Update the main settings of the design.

        Parameters
        ----------
        gravity_dir : int, optional
            Gravity direction from -X to +Z. Options are ``0`` to ``5``.
            The default is ``0``.
        ambtemp : float, str, optional
            Ambient temperature. The default is ``20``.
            The default unit is celsius for float or string including unit definition is accepted, e.g. ``325kel``.
        performvalidation : bool, optional
            Whether to perform validation. The default is ``False``.
        check_level : str, optional
            Level of check to perform during validation. The default
            is ``"None"``.
        defaultfluid : str, optional
            Default fluid material. The default is ``"air"``.
        defaultsolid : str, optional
            Default solid material. The default is ``"Al-Extruded"``.
        export_monitor : bool, optional
            Whether to use the default export directory for monitor point data.
            The default value is ``False``.
        export_directory : str, optional
            Default export directory for monitor point data. The default value is the current working directory.
        gauge_pressure : float, str, optional
            Set the Gauge pressure. It can be a float (units will be "n_per_meter_sq") or a string with units.
            Default is ``0``.
        radiation_temperature : float, str, optional
            Set the radiation temperature. It can be a float (units will be "cel") or a string with units.
            Default is ``20``.
        ignore_unclassified_objects : bool, optional
            Whether to ignore unclassified objects during validation check.
            The default value is ``False``.
        skip_intersection_checks : bool, optional
            Whether to skip intersection checks during validation check.
            The default value is ``False``.
        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.

        References
        ----------

        >>> oDesign.SetDesignSettings
        """
        #
        # Configure design settings for gravity etc
        IceGravity = ["X", "Y", "Z"]
        GVPos = False
        if "gravityDir" in kwargs:  # pragma: no cover
            warnings.warn(
                "`gravityDir` is deprecated. Use `gravity_dir` instead.",
                DeprecationWarning,
            )

            gravity_dir = kwargs["gravityDir"]
        if "CheckLevel" in kwargs:  # pragma: no cover
            warnings.warn(
                "`CheckLevel` is deprecated. Use `check_level` instead.",
                DeprecationWarning,
            )

            check_level = kwargs["CheckLevel"]
        if int(gravity_dir) > 2:
            GVPos = True
        GVA = IceGravity[int(gravity_dir) - 3]
        self._odesign.SetDesignSettings(
            [
                "NAME:Design Settings Data",
                "Perform Minimal validation:=",
                performvalidation,
                "Default Fluid Material:=",
                defaultfluid,
                "Default Solid Material:=",
                defaultsolid,
                "Default Surface Material:=",
                "Steel-oxidised-surface",
                "AmbientTemperature:=",
                self.value_with_units(ambtemp, "cel"),
                "AmbientPressure:=",
                self.value_with_units(gauge_pressure, "n_per_meter_sq"),
                "AmbientRadiationTemperature:=",
                self.value_with_units(radiation_temperature, "cel"),
                "Gravity Vector CS ID:=",
                1,
                "Gravity Vector Axis:=",
                GVA,
                "Positive:=",
                GVPos,
                "ExportOnSimulationComplete:=",
                export_monitor,
                "ExportDirectory:=",
                export_directory,
            ],
            [
                "NAME:Model Validation Settings",
                "EntityCheckLevel:=",
                check_level,
                "IgnoreUnclassifiedObjects:=",
                ignore_unclassified_objects,
                "SkipIntersectionChecks:=",
                skip_intersection_checks,
            ],
        )
        return True

    @pyaedt_function_handler()
    def assign_em_losses(
            self,
            designname="HFSSDesign1",
            setupname="Setup1",
            sweepname="LastAdaptive",
            map_frequency=None,
            surface_objects=None,
            source_project_name=None,
            paramlist=None,
            object_list=None,
    ):
        """Map EM losses to an Icepak design.

        Parameters
        ----------
        designname : string, optional
            Name of the design with the source mapping. The default is ``"HFSSDesign1"``.
        setupname : str, optional
            Name of the EM setup. The default is ``"Setup1"``.
        sweepname : str, optional
            Name of the EM sweep to use for the mapping. The default is ``"LastAdaptive"``.
        map_frequency : str, optional
            String containing the frequency to map. The default is ``None``.
            The value must be ``None`` for Eigenmode analysis.
        surface_objects : list, optional
            List of objects in the source that are metals. The default is ``None``.
        source_project_name : str, optional
            Name of the source project. The default is ``None``, in which case the
            source from the same project is used.
        paramlist : list, dict, optional
            List of all parameters to map from source and Icepak design. The default is ``None``.
            If ``None`` the variables are set to their values (no mapping).
            If it is a list, the specified variables in the icepak design are mapped to variables
            in the source design having the same name.
            If it is a dictionary, it is possible to map variables to the source design having a different name.
            The dictionary structure is {"source_design_variable": "icepak_variable"}.
        object_list : list, optional
            List of objects. The default is ``None``.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.

        References
        ----------

        >>> oModule.AssignEMLoss
        """
        if surface_objects is None:
            surface_objects = []
        if object_list is None:
            object_list = []

        self.logger.info("Mapping HFSS EM losses.")

        if self.project_name == source_project_name or source_project_name is None:
            project_name = "This Project*"
        else:
            project_name = source_project_name + ".aedt"
        #
        # Generate a list of model objects from the lists made previously and use to map the HFSS losses into Icepak
        #
        if not object_list:
            all_objects = self.modeler.object_names
            if "Region" in all_objects:
                all_objects.remove("Region")
        else:
            all_objects = object_list[:]

        surfaces = surface_objects
        if map_frequency:
            intr = [map_frequency]
        else:
            intr = []

        argparam = OrderedDict({})
        for el in self.available_variations.nominal_w_values_dict:
            argparam[el] = self.available_variations.nominal_w_values_dict[el]

        if paramlist and isinstance(paramlist, list):
            for el in paramlist:
                argparam[el] = el
        elif paramlist and isinstance(paramlist, dict):
            for el in paramlist:
                argparam[el] = paramlist[el]

        props = OrderedDict(
            {
                "Objects": all_objects,
                "Project": project_name,
                "Product": "ElectronicsDesktop",
                "Design": designname,
                "Soln": setupname + " : " + sweepname,
                "Params": argparam,
                "ForceSourceToSolve": True,
                "PreservePartnerSoln": True,
                "PathRelativeTo": "TargetProject",
            }
        )
        props["Intrinsics"] = intr
        props["SurfaceOnly"] = surfaces

        name = generate_unique_name("EMLoss")
        bound = BoundaryObject(self, name, props, "EMLoss")
        if bound.create():
            self._boundaries[bound.name] = bound
            self.logger.info("EM losses mapped from design: %s.", designname)
            return bound
        return False

    @pyaedt_function_handler()
    def eval_surface_quantity_from_field_summary(
            self,
            faces_list,
            quantity_name="HeatTransCoeff",
            savedir=None,
            filename=None,
            sweep_name=None,
            parameter_dict_with_values={},
    ):
        """Export the field surface output.

        This method exports one CSV file for the specified variation.

        Parameters
        ----------
        faces_list : list
            List of faces to apply.
        quantity_name : str, optional
            Name of the quantity to export. The default is ``"HeatTransCoeff"``.
        savedir : str, optional
            Directory to save the CSV file to. The default is ``None``, in which
            case the file is exported to the working directory.
        filename : str, optional
            Name of the CSV file. The default is ``None``, in which case the default
            name is used.
        sweep_name : str, optional
            Name of the setup and name of the sweep. For example, ``"IcepakSetup1 : SteatyState"``.
            The default is ``None``, in which case the active setup and active sweep are used.
        parameter_dict_with_values : dict, optional
            Dictionary of parameters defined for the specific setup with values. The default is ``{}``.

        Returns
        -------
        str
            Name of the file.

        References
        ----------

        >>> oModule.ExportFieldsSummary
        """
        name = generate_unique_name(quantity_name)
        self.modeler.create_face_list(faces_list, name)
        if not savedir:
            savedir = self.working_directory
        if not filename:
            filename = generate_unique_name(self.project_name + quantity_name)
        if not sweep_name:
            sweep_name = self.nominal_sweep
        self.osolution.EditFieldsSummarySetting(
            [
                "Calculation:=",
                ["Object", "Surface", name, quantity_name, "", "Default", "AmbientTemp"],
            ]
        )
        string = ""
        for el in parameter_dict_with_values:
            string += el + "='" + parameter_dict_with_values[el] + "' "
        filename = os.path.join(savedir, filename + ".csv")
        self.osolution.ExportFieldsSummary(
            [
                "SolutionName:=",
                sweep_name,
                "DesignVariationKey:=",
                string,
                "ExportFileName:=",
                filename,
                "IntrinsicValue:=",
                "",
            ]
        )
        return filename

    def eval_volume_quantity_from_field_summary(
            self,
            object_list,
            quantity_name="HeatTransCoeff",
            savedir=None,
            filename=None,
            sweep_name=None,
            parameter_dict_with_values={},
    ):
        """Export the field volume output.

        This method exports one CSV file for the specified variation.

        Parameters
        ----------
        object_list : list
            List of faces to apply.
        quantity_name : str, optional
            Name of the quantity to export. The default is ``"HeatTransCoeff"``.
        savedir : str, optional
            Directory to save the CSV file to. The default is ``None``, in which
            case the file is exported to the working directory.
        filename :  str, optional
            Name of the CSV file. The default is ``None``, in which case the default name
            is used.
        sweep_name :
            Name of the setup and name of the sweep. For example, ``"IcepakSetup1 : SteatyState"``.
            The default is ``None``, in which case the active setup and active sweep are used.
        parameter_dict_with_values : dict, optional
            Dictionary of parameters defined for the specific setup with values. The default is ``{}``

        Returns
        -------
        str
           Name of the file.

        References
        ----------

        >>> oModule.ExportFieldsSummary
        """
        if not savedir:
            savedir = self.working_directory
        if not filename:
            filename = generate_unique_name(self.project_name + quantity_name)
        if not sweep_name:
            sweep_name = self.nominal_sweep
        self.osolution.EditFieldsSummarySetting(
            [
                "Calculation:=",
                ["Object", "Volume", ",".join(object_list), quantity_name, "", "Default", "AmbientTemp"],
            ]
        )
        string = ""
        for el in parameter_dict_with_values:
            string += el + "='" + parameter_dict_with_values[el] + "' "
        filename = os.path.join(savedir, filename + ".csv")
        self.osolution.ExportFieldsSummary(
            [
                "SolutionName:=",
                sweep_name,
                "DesignVariationKey:=",
                string,
                "ExportFileName:=",
                filename,
                "IntrinsicValue:=",
                "",
            ]
        )
        return filename

    def export_summary(
            self,
            output_dir=None,
            solution_name=None,
            type="Object",
            geometry_type="Volume",
            quantity="Temperature",
            variation="",
            variation_list=None,
            filename="IPKsummaryReport",
            **kwargs
    ):
        """Export a fields summary of all objects.

        Parameters
        ----------
        output_dir : str, optional
            Name of directory for exporting the fields summary.
            The default is ``None``, in which case the fields summary
            is exported to the working directory.
        solution_name : str, optional
            Name of the solution. The default is ``None``, in which case the
            default solution is used.
        type : string, optional
            Entity type, ``"Boundary"`` or ``"Object"``. The default is ``"Object"``.
        geometry_type : str, optional
            Geometry type, ``"Volume"`` or ``"Surface"``. The default is ``"Volume"``.
        quantity : str, optional
            The default is ``"Temperature"``.
        variation : str, optional
            The default is ``""``.
        variation_list : list, optional
            The default is ``None``.
        filename : str, optional
            The default is ``"IPKsummaryReport"``.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.

        References
        ----------

        >>> oModule.EditFieldsSummarySetting
        >>> oModule.ExportFieldsSummary
        """
        if 'geometryType' in kwargs:
            warnings.warn("The 'geometryType' argument is deprecated. Use 'geometry_type' instead.",
                          DeprecationWarning)

        if 'variationlist' in kwargs:
            warnings.warn("The 'variationlist' argument is deprecated. Use 'variation_list' instead.",
                          DeprecationWarning)

        geometry_type = kwargs.get('geometryType', geometry_type)
        variation_list = kwargs.get('variationlist', variation_list)

        if variation_list is None:
            variation_list = []

        if type == "Object":
            all_objs = list(self.modeler.oeditor.GetObjectsInGroup("Solids"))
            all_objs_non_modeled = list(self.modeler.oeditor.GetObjectsInGroup("Non Model"))
            all_elements = [item for item in all_objs if item not in all_objs_non_modeled]
            self.logger.info("Objects lists " + str(all_elements))
        elif type == "Boundary":
            all_elements = [b.name for b in self.boundaries]
            self.logger.info("Boundary lists " + str(all_elements))
        else:
            self.logger.error("Entity type " + type + " not supported.")
            return False
        arg = []
        for el in all_elements:
            try:
                self.osolution.EditFieldsSummarySetting(
                    ["Calculation:=", [type, geometry_type, el, quantity, "", "Default"]]
                )
                arg.append("Calculation:=")
                arg.append([type, geometry_type, el, quantity, "", "Default"])
            except Exception as e:
                self.logger.warning("Object " + el + " not added.")
        if not output_dir:
            output_dir = self.working_directory
        self.osolution.EditFieldsSummarySetting(arg)
        if not os.path.exists(output_dir):
            os.mkdir(output_dir)
        if not solution_name:
            solution_name = self.nominal_sweep
        if variation:
            for l in variation_list:
                self.osolution.ExportFieldsSummary(
                    [
                        "SolutionName:=",
                        solution_name,
                        "DesignVariationKey:=",
                        variation + "='" + str(l) + "'",
                        "ExportFileName:=",
                        os.path.join(output_dir, filename + "_" + quantity + "_" + str(l) + ".csv"),
                    ]
                )
        else:
            self.osolution.ExportFieldsSummary(
                [
                    "SolutionName:=",
                    solution_name,
                    "DesignVariationKey:=",
                    "",
                    "ExportFileName:=",
                    os.path.join(output_dir, filename + "_" + quantity + ".csv"),
                ]
            )
        return True

    @pyaedt_function_handler()
    def get_radiation_settings(self, radiation):
        """Get radiation settings.

        Parameters
        ----------
        radiation : str
            Type of the radiation. Options are:

            * ``"Nothing"``
            * ``"Low"``
            * ``"High"``
            * ``"Both"``

        Returns
        -------
        (bool, bool)
            Tuple containing the low side radiation and the high side radiation.
        """
        if radiation == "Nothing":
            low_side_radiation = False
            high_side_radiation = False
        elif radiation == "Low":
            low_side_radiation = True
            high_side_radiation = False
        elif radiation == "High":
            low_side_radiation = False
            high_side_radiation = True
        elif radiation == "Both":
            low_side_radiation = True
            high_side_radiation = True
        return low_side_radiation, high_side_radiation

    @pyaedt_function_handler()
    def get_link_data(self, links_data, **kwargs):
        """Get a list of linked data.

        Parameters
        ----------
        linkData : list
            List of the data to retrieve for links. Options are:

            * Project name, if ``None`` use the active project
            * Design name
            * HFSS solution name, such as ``"HFSS Setup 1 : Last Adaptive"``
            * Force source design simulation, ``True`` or ``False``
            * Preserve source design solution, ``True`` or ``False``

        Returns
        -------
        list
            List containing the requested link data.

        """
        if "linkData" in kwargs:
            warnings.warn(
                "The ``linkData`` parameter was deprecated in 0.6.43. Use the ``links_data`` parameter instead.",
                DeprecationWarning,
            )
            links_data = kwargs["linkData"]

        if links_data[0] is None:
            project_name = "This Project*"
        else:
            project_name = links_data[0].replace("\\", "/")

        design_name = links_data[1]
        hfss_solution_name = links_data[2]
        force_source_sim_enabler = links_data[3]
        preserve_src_res_enabler = links_data[4]

        arg = [
            "NAME:DefnLink",
            "Project:=",
            project_name,
            "Product:=",
            "ElectronicsDesktop",
            "Design:=",
            design_name,
            "Soln:=",
            hfss_solution_name,
            ["NAME:Params"],
            "ForceSourceToSolve:=",
            force_source_sim_enabler,
            "PreservePartnerSoln:=",
            preserve_src_res_enabler,
            "PathRelativeTo:=",
            "TargetProject",
        ]

        return arg

    @pyaedt_function_handler()
    def create_fan(
            self,
            name=None,
            is_2d=False,
            shape="Circular",
            cross_section="XY",
            radius="0.008mm",
            hub_radius="0mm",
            origin=None,
    ):
        """Create a fan component in Icepak that is linked to an HFSS 3D Layout object.

        Parameters
        ----------
        name : str, optional
            Fan name. The default is ``None``, in which case the default name is used.
        is_2d : bool, optional
            Whether the fan is modeled as 2D. The default is ``False``, in which
            case the fan is modeled as 3D.
        shape : str, optional
            Fan shape. Options are ``"Circular"`` and ``"Rectangular"``. The default
            is ``"Circular"``.
        cross_section : str, optional
            Cross section plane of the fan. The default is ``"XY"``.
        radius : str, float, optional
            Radius of the fan in modeler units. The default is ``"0.008mm"``.
        hub_radius : str, float, optional
            Hub radius of the fan in modeler units. The default is ``"0mm"``,
        origin : list, optional
            List of ``[x,y,z]`` coordinates for the position of the fan in the modeler.

        Returns
        -------
        :class:`pyaedt.modules.Boundary.NativeComponentObject`
            NativeComponentObject object.

        References
        ----------

        >>> oModule.InsertNativeComponent
        """
        if not name:
            name = generate_unique_name("Fan")

        basic_component = OrderedDict(
            {
                "ComponentName": name,
                "Company": "",
                "Company URL": "",
                "Model Number": "",
                "Help URL": "",
                "Version": "1.0",
                "Notes": "",
                "IconType": "Fan",
            }
        )
        if is_2d:
            model = "2D"
        else:
            model = "3D"
        cross_section = GeometryOperators.cs_plane_to_plane_str(cross_section)
        native_component = OrderedDict(
            {
                "Type": "Fan",
                "Unit": self.modeler.model_units,
                "ModelAs": model,
                "Shape": shape,
                "MovePlane": cross_section,
                "Radius": self._arg_with_units(radius),
                "HubRadius": self._arg_with_units(hub_radius),
                "CaseSide": True,
                "FlowDirChoice": "NormalPositive",
                "FlowType": "Curve",
                "SwirlType": "Magnitude",
                "FailedFan": False,
                "DimUnits": ["m3_per_s", "n_per_meter_sq"],
                "X": ["0", "0.01"],
                "Y": ["3", "0"],
                "Pressure Loss Curve": OrderedDict(
                    {"DimUnits": ["m_per_sec", "n_per_meter_sq"], "X": ["", "", "", "3"], "Y": ["", "1", "10", "0"]}
                ),
                "IntakeTemp": "AmbientTemp",
                "Swirl": "0",
                "OperatingRPM": "0",
                "Magnitude": "1",
            }
        )
        native_props = OrderedDict(
            {
                "TargetCS": "Global",
                "SubmodelDefinitionName": name,
                "ComponentPriorityLists": OrderedDict({}),
                "NextUniqueID": 0,
                "MoveBackwards": False,
                "DatasetType": "ComponentDatasetType",
                "DatasetDefinitions": OrderedDict({}),
                "BasicComponentInfo": basic_component,
                "GeometryDefinitionParameters": OrderedDict({"VariableOrders": OrderedDict()}),
                "DesignDefinitionParameters": OrderedDict({"VariableOrders": OrderedDict()}),
                "MaterialDefinitionParameters": OrderedDict({"VariableOrders": OrderedDict()}),
                "MapInstanceParameters": "DesignVariable",
                "UniqueDefinitionIdentifier": "57c8ab4e-4db9-4881-b6bb-"
                                              + random_string(12, char_set="abcdef0123456789"),
                "OriginFilePath": "",
                "IsLocal": False,
                "ChecksumString": "",
                "ChecksumHistory": [],
                "VersionHistory": [],
                "NativeComponentDefinitionProvider": native_component,
                "InstanceParameters": OrderedDict(
                    {"GeometryParameters": "", "MaterialParameters": "", "DesignParameters": ""}
                ),
            }
        )

        component3d_names = list(self.modeler.oeditor.Get3DComponentInstanceNames(name))

        native = NativeComponentObject(self, "Fan", name, native_props)
        if native.create():
            user_defined_component = UserDefinedComponent(
                self.modeler, native.name, native_props["NativeComponentDefinitionProvider"], "Fan"
            )
            self.modeler.user_defined_components[native.name] = user_defined_component
            new_name = [
                i for i in list(self.modeler.oeditor.Get3DComponentInstanceNames(name)) if i not in component3d_names
            ][0]
            self.modeler.refresh_all_ids()
            self.materials._load_from_project()
            self._native_components.append(native)
            if origin:
                self.modeler.move(new_name, origin)
            return native
        return False

    @pyaedt_function_handler()
    def create_ipk_3dcomponent_pcb(
            self,
            compName,
            setupLinkInfo,
            solutionFreq,
            resolution,
            PCB_CS="Global",
            rad="Nothing",
            extent_type="Bounding Box",
            outline_polygon="",
            powerin="0W",
            custom_x_resolution=None,
            custom_y_resolution=None,
            **kwargs  # fmt: skip
    ):
        """Create a PCB component in Icepak that is linked to an HFSS 3D Layout object.

        Parameters
        ----------
        compName : str
            Name of the new PCB component.
        setupLinkInfo : list
            List of the five elements needed to set up the link in this format:
            ``[projectname, designname, solution name, forcesimulation (bool), preserve results (bool)]``.
        solutionFreq :
            Frequency of the solution if cosimulation is requested.
        resolution : int
            Resolution of the mapping.
        PCB_CS : str, optional
            Coordinate system for the PCB. The default is ``"Global"``.
        rad : str, optional
            Radiating faces. The default is ``"Nothing"``.
        extent_type : str, optional
            Type of the extent. Options are ``"Bounding Box"`` and ``"Polygon"``.
            The default is ``"Bounding Box"``.
        outline_polygon : str, optional
            Name of the polygon if ``extentype="Polygon"``. The default is ``""``.
        powerin : str, optional
            Power to dissipate if cosimulation is disabled. The default is ``"0W"``.
        custom_x_resolution
            The default is ``None``.
        custom_y_resolution
            The default is ``None``.

        Returns
        -------
        :class:`pyaedt.modules.Boundary.NativeComponentObject`
            NativeComponentObject object.

        References
        ----------

        >>> oModule.InsertNativeComponent
        """
        if "extenttype" in kwargs:
            warnings.warn(
                "The ``extenttype`` parameter was deprecated in 0.6.43. Use the ``extent_type`` parameter instead.",
                DeprecationWarning,
            )
            extent_type = kwargs["extenttype"]

        if "outlinepolygon" in kwargs:
            warnings.warn(
                """The ``outlinepolygon`` parameter was deprecated in 0.6.43.
                Use the ``outline_polygon`` parameter instead.""",
                DeprecationWarning,
            )
            outline_polygon = kwargs["outlinepolygon"]

        low_radiation, high_radiation = self.get_radiation_settings(rad)
        hfss_link_info = OrderedDict({})
        _arg2dict(self.get_link_data(setupLinkInfo), hfss_link_info)
        if extent_type == "Polygon" and not outline_polygon:
            native_props = OrderedDict(
                {
                    "NativeComponentDefinitionProvider": OrderedDict(
                        {
                            "Type": "PCB",
                            "Unit": self.modeler.model_units,
                            "MovePlane": "XY",
                            "Use3DLayoutExtents": True,
                            "ExtentsType": extent_type,
                            "CreateDevices": False,
                            "CreateTopSolderballs": False,
                            "CreateBottomSolderballs": False,
                            "Resolution": int(resolution),
                            "LowSide": OrderedDict({"Radiate": low_radiation}),
                            "HighSide": OrderedDict({"Radiate": high_radiation}),
                        }
                    )
                }
            )
        else:
            native_props = OrderedDict(
                {
                    "NativeComponentDefinitionProvider": OrderedDict(
                        {
                            "Type": "PCB",
                            "Unit": self.modeler.model_units,
                            "MovePlane": "XY",
                            "Use3DLayoutExtents": False,
                            "ExtentsType": extent_type,
                            "OutlinePolygon": outline_polygon,
                            "CreateDevices": False,
                            "CreateTopSolderballs": False,
                            "CreateBottomSolderballs": False,
                            "Resolution": int(resolution),
                            "LowSide": OrderedDict({"Radiate": low_radiation}),
                            "HighSide": OrderedDict({"Radiate": high_radiation}),
                        }
                    )
                }
            )
        native_props["BasicComponentInfo"] = OrderedDict({"IconType": "PCB"})
        if settings.aedt_version > "2023.2":  # pragma: no cover
            native_props["ViaHoleMaterial"] = "copper"
            native_props["IncludeMCAD"] = False

        if custom_x_resolution and custom_y_resolution:
            native_props["NativeComponentDefinitionProvider"]["UseThermalLink"] = solutionFreq != ""
            native_props["NativeComponentDefinitionProvider"]["CustomResolution"] = True
            native_props["NativeComponentDefinitionProvider"]["CustomResolutionRow"] = custom_x_resolution
            native_props["NativeComponentDefinitionProvider"]["CustomResolutionCol"] = custom_y_resolution
            # compDefinition += ["UseThermalLink:=", solutionFreq!="",
            #                    "CustomResolution:=", True, "CustomResolutionRow:=", custom_x_resolution,
            #                    "CustomResolutionCol:=", 600]
        else:
            native_props["NativeComponentDefinitionProvider"]["UseThermalLink"] = solutionFreq != ""
            native_props["NativeComponentDefinitionProvider"]["CustomResolution"] = False
            # compDefinition += ["UseThermalLink:=", solutionFreq != "",
            #                    "CustomResolution:=", False]
        if solutionFreq:
            native_props["NativeComponentDefinitionProvider"]["Frequency"] = solutionFreq
            native_props["NativeComponentDefinitionProvider"]["DefnLink"] = hfss_link_info["DefnLink"]
            # compDefinition += ["Frequency:=", solutionFreq, hfssLinkInfo]
        else:
            native_props["NativeComponentDefinitionProvider"]["Power"] = powerin
            native_props["NativeComponentDefinitionProvider"]["DefnLink"] = hfss_link_info["DefnLink"]
            # compDefinition += ["Power:=", powerin, hfssLinkInfo]

        native_props["TargetCS"] = PCB_CS
        native = NativeComponentObject(self, "PCB", compName, native_props)
        if native.create():
            user_defined_component = UserDefinedComponent(
                self.modeler, native.name, native_props["NativeComponentDefinitionProvider"], "PCB"
            )
            self.modeler.user_defined_components[native.name] = user_defined_component
            self.modeler.refresh_all_ids()
            self.materials._load_from_project()
            self._native_components.append(native)
            return native
        return False

    @pyaedt_function_handler()
    def create_pcb_from_3dlayout(
            self,
            component_name,
            project_name,
            design_name,
            resolution=2,
            extent_type="Bounding Box",
            outline_polygon="",
            close_linked_project_after_import=True,
            custom_x_resolution=None,
            custom_y_resolution=None,
            power_in=0,
            rad="Nothing",
            **kwargs  # fmt: skip
    ):
        """Create a PCB component in Icepak that is linked to an HFSS 3DLayout object linking only to the geometry file.

        .. note::
           No solution is linked.

        Parameters
        ----------
        component_name : str
            Name of the new PCB component to create in Icepak.
        project_name : str
            Name of the project or the full path to the project.
        design_name : str
            Name of the design.
        resolution : int, optional
            Resolution of the mapping. The default is ``2``.
        extent_type : str, optional
            Type of the extent. Options are ``"Polygon"`` and ``"Bounding Box"``. The default
            is ``"Bounding Box"``.
        outline_polygon : str, optional
            Name of the outline polygon if ``extent_type="Polygon"``. The default is ``""``.
        close_linked_project_after_import : bool, optional
            Whether to close the linked AEDT project after the import. The default is ``True``.
        custom_x_resolution : int, optional
            The default is ``None``.
        custom_y_resolution : int, optional
            The default is ``None``.
        power_in : float, optional
            Power in Watt.
        rad : str, optional
            Radiating faces. Options are:

            * ``"Nothing"``
            * ``"Low"``
            * ``"High"``
            * ``"Both"``

            The default is ``"Nothing"``.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.

        References
        ----------

        >>> oModule.InsertNativeComponent
        """
        if "extenttype" in kwargs:
            warnings.warn(
                "``extenttype`` was deprecated in 0.6.43. Use ``extent_type`` instead.",
                DeprecationWarning,
            )
            extent_type = kwargs["extenttype"]

        if "outlinepolygon" in kwargs:
            warnings.warn(
                "``outlinepolygon`` was deprecated in 0.6.43. Use ``outline_polygon`` instead.",
                DeprecationWarning,
            )
            outline_polygon = kwargs["outlinepolygon"]

        if project_name == self.project_name:
            project_name = "This Project*"
        link_data = [project_name, design_name, "<--EDB Layout Data-->", False, False]
        status = self.create_ipk_3dcomponent_pcb(
            component_name,
            link_data,
            "",
            resolution,
            extent_type=extent_type,
            outline_polygon=outline_polygon,
            custom_x_resolution=custom_x_resolution,
            custom_y_resolution=custom_y_resolution,
            powerin=self.modeler._arg_with_dim(power_in, "W"),
        )

        if close_linked_project_after_import and ".aedt" in project_name:
            prjname = os.path.splitext(os.path.basename(project_name))[0]
            self.close_project(prjname, save_project=False)
        self.logger.info("PCB component correctly created in Icepak.")
        return status

    @pyaedt_function_handler()
    def copyGroupFrom(self, group_name, source_design, source_project_name=None, source_project_path=None, **kwargs):
        """Copy a group from another design.

        Parameters
        ----------
        group_name : str
            Name of the group.
        source_design : str
            Name of the source design.
        source_project_name : str, optional
            Name of the source project. The default is ``None``, in which case the current active project is used.
        source_project_path : str, optional
            Path to the source project. The default is ``None``.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.

        References
        ----------

        >>> oEditor.Copy
        >>> oeditor.Paste
        """
        if "groupName" in kwargs:
            warnings.warn(
                "The ``groupName`` parameter was deprecated in 0.6.43. Use the ``group_name`` parameter instead.",
                DeprecationWarning,
            )
            group_name = kwargs["groupName"]

        if "sourceDesign" in kwargs:
            warnings.warn(
                "The ``sourceDesign`` parameter was deprecated in 0.6.43. Use the ``source_design`` parameter instead.",
                DeprecationWarning,
            )
            source_design = kwargs["sourceDesign"]

        if "sourceProject" in kwargs:
            warnings.warn(
                """The ``sourceProject`` parameter was deprecated in 0.6.43.
                Use the ``source_project_name`` parameter instead.""",
                DeprecationWarning,
            )
            source_project_name = kwargs["sourceProject"]

        if "sourceProjectPath" in kwargs:
            warnings.warn(
                """The ``sourceProjectPath`` parameter was deprecated in 0.6.43.
                Use the ``source_project_path`` parameter instead.""",
                DeprecationWarning,
            )
            source_project_path = kwargs["sourceProjectPath"]

        if source_project_name == self.project_name or source_project_name is None:
            active_project = self._desktop.GetActiveProject()
        else:
            self._desktop.OpenProject(source_project_path)
            active_project = self._desktop.SetActiveProject(source_project_name)

        active_design = active_project.SetActiveDesign(source_design)
        active_editor = active_design.SetActiveEditor("3D Modeler")
        active_editor.Copy(["NAME:Selections", "Selections:=", group_name])

        self.modeler.oeditor.Paste()
        self.modeler.refresh_all_ids()
        self.materials._load_from_project()
        return True

    @pyaedt_function_handler()
    def globalMeshSettings(
            self,
            meshtype,
            gap_min_elements="1",
            noOgrids=False,
            MLM_en=True,
            MLM_Type="3D",
            stairStep_en=False,
            edge_min_elements="1",
            object="Region",
    ):
        """Create a custom mesh tailored on a PCB design.

        Parameters
        ----------
        meshtype : int
            Type of the mesh. Options are ``1``, ``2``, and ``3``, which represent
            respectively a coarse, standard, and very accurate mesh.
        gap_min_elements : str, optional
            The default is ``"1"``.
        noOgrids : bool, optional
            The default is ``False``.
        MLM_en : bool, optional
            The default is ``True``.
        MLM_Type : str, optional
            The default is ``"3D"``.
        stairStep_en : bool, optional
            The default is ``False``.
        edge_min_elements : str, optional
            The default is ``"1"``.
        object : str, optional
            The default is ``"Region"``.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.

        References
        ----------

        >>> oModule.EditGlobalMeshRegion
        """
        bounding_box = self.modeler.oeditor.GetModelBoundingBox()
        xsize = abs(float(bounding_box[0]) - float(bounding_box[3])) / (15 * meshtype * meshtype)
        ysize = abs(float(bounding_box[1]) - float(bounding_box[4])) / (15 * meshtype * meshtype)
        zsize = abs(float(bounding_box[2]) - float(bounding_box[5])) / (10 * meshtype)
        MaxSizeRatio = 1 + (meshtype / 2)

        self.omeshmodule.EditGlobalMeshRegion(
            [
                "NAME:Settings",
                "MeshMethod:=",
                "MesherHD",
                "UserSpecifiedSettings:=",
                True,
                "ComputeGap:=",
                True,
                "MaxElementSizeX:=",
                str(xsize) + self.modeler.model_units,
                "MaxElementSizeY:=",
                str(ysize) + self.modeler.model_units,
                "MaxElementSizeZ:=",
                str(zsize) + self.modeler.model_units,
                "MinElementsInGap:=",
                gap_min_elements,
                "MinElementsOnEdge:=",
                edge_min_elements,
                "MaxSizeRatio:=",
                str(MaxSizeRatio),
                "NoOGrids:=",
                noOgrids,
                "EnableMLM:=",
                MLM_en,
                "EnforeMLMType:=",
                MLM_Type,
                "MaxLevels:=",
                "0",
                "BufferLayers:=",
                "0",
                "UniformMeshParametersType:=",
                "Average",
                "StairStepMeshing:=",
                stairStep_en,
                "MinGapX:=",
                str(xsize / 10) + self.modeler.model_units,
                "MinGapY:=",
                str(xsize / 10) + self.modeler.model_units,
                "MinGapZ:=",
                str(xsize / 10) + self.modeler.model_units,
                "Objects:=",
                [object],
            ]
        )
        return True

    @pyaedt_function_handler()
    def create_meshregion_component(
            self, scale_factor=1.0, name="Component_Region", restore_padding_values=[50, 50, 50, 50, 50, 50]
    ):
        """Create a bounding box to use as a mesh region in Icepak.

        Parameters
        ----------
        scale_factor : float, optional
            The default is ``1.0``.
        name : str, optional
            Name of the bounding box. The default is ``"Component_Region"``.
        restore_padding_values : list, optional
            The default is ``[50,50,50,50,50,50]``.

        Returns
        -------
        tuple
            Tuple containing the ``(x, y, z)`` distances of the region.

        References
        ----------

        >>> oeditor.ChangeProperty
        """
        self.modeler.edit_region_dimensions([0, 0, 0, 0, 0, 0])

        vertex_ids = self.modeler.oeditor.GetVertexIDsFromObject("Region")

        x_values = []
        y_values = []
        z_values = []

        for vertex_id in vertex_ids:
            tmp = self.modeler.oeditor.GetVertexPosition(vertex_id)
            x_values.append(tmp[0])
            y_values.append(tmp[1])
            z_values.append(tmp[2])

        scale_factor = scale_factor - 1
        delta_x = (float(max(x_values)) - float(min(x_values))) * scale_factor
        x_max = float(max(x_values)) + delta_x / 2.0
        x_min = float(min(x_values)) - delta_x / 2.0

        delta_y = (float(max(y_values)) - float(min(y_values))) * scale_factor
        y_max = float(max(y_values)) + delta_y / 2.0
        y_min = float(min(y_values)) - delta_y / 2.0

        delta_z = (float(max(z_values)) - float(min(z_values))) * scale_factor
        z_max = float(max(z_values)) + delta_z / 2.0
        z_min = float(min(z_values)) - delta_z / 2.0

        dis_x = str(float(x_max) - float(x_min))
        dis_y = str(float(y_max) - float(y_min))
        dis_z = str(float(z_max) - float(z_min))

        min_position = self.modeler.Position(str(x_min) + "mm", str(y_min) + "mm", str(z_min) + "mm")
        mesh_box = self.modeler.create_box(min_position, [dis_x + "mm", dis_y + "mm", dis_z + "mm"], name)

        self.modeler[name].model = False

        self.modeler.edit_region_dimensions(restore_padding_values)
        return dis_x, dis_y, dis_z

    @pyaedt_function_handler()
    def delete_em_losses(self, bound_name):
        """Delete the EM losses boundary.

        Parameters
        ----------
        bound_name : str
            Name of the boundary.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.

        References
        ----------

        >>> oModule.DeleteBoundaries
        """
        self.oboundary.DeleteBoundaries([bound_name])
        return True

    @pyaedt_function_handler()
    def delete_pcb_component(self, comp_name):
        """Delete a PCB component.

        Parameters
        ----------
        comp_name : str
            Name of the PCB component.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.

        References
        ----------

        >>> oEditor.Delete
        """
        arg = ["NAME:Selections", "Selections:=", comp_name]

        self.modeler.oeditor.Delete(arg)
        return True

    @pyaedt_function_handler()
    def get_liquid_objects(self):
        """Get liquid material objects.

        Returns
        -------
        list
            List of all liquid material objects.
        """
        mats = []
        for el in self.materials.liquids:
            mats.extend(self.modeler.convert_to_selections(self.modeler.get_objects_by_material(el), True))
        return mats

    @pyaedt_function_handler()
    def get_gas_objects(self):
        """Get gas objects.

        Returns
        -------
        list
            List of all gas objects.
        """
        mats = []
        for el in self.materials.gases:
            mats.extend(self.modeler.convert_to_selections(self.modeler.get_objects_by_material(el), True))
        return mats

    @pyaedt_function_handler()
    def generate_fluent_mesh(
            self,
            object_lists=None,
            meshtype="tetrahedral",
            min_size=None,
            max_size=None,
            inflation_layer_number=3,
            inflation_growth_rate=1.2,
            mesh_growth_rate=1.2,
    ):
        """Generate a Fluent mesh for a list of selected objects and assign the mesh automatically to the objects.

        Parameters
        ----------
        object_lists : list, optional
            List of objects to compute the Fluent mesh on. The default is ``None``, in which case
            all fluids objects are used to compute the mesh.
        meshtype : str, optional
            Mesh type. Options are ``"tethraedral"`` or ``"hexcore"``.
        min_size : float, optional
            Minimum mesh size. Default is smallest edge of objects/20.
        max_size : float, optional
            Maximum mesh size. Default is smallest edge of objects/5.
        inflation_layer_number : int, optional
            Inflation layer number. Default is ``3``.
        inflation_growth_rate : float, optional
            Inflation layer size. Default is ``1.2``.
        mesh_growth_rate : float, optional
            Growth rate. Default is ``1.2``.

        Returns
        -------
        :class:`pyaedt.modules.Mesh.MeshOperation`
        """
        version = self.aedt_version_id[-3:]
        ansys_install_dir = os.environ.get("ANSYS{}_DIR".format(version), "")
        if not ansys_install_dir:
            ansys_install_dir = os.environ.get("AWP_ROOT{}".format(version), "")
        assert ansys_install_dir, "Fluent {} has to be installed to generate mesh. Please set ANSYS{}_DIR".format(
            version, version
        )
        if not os.getenv("ANSYS{}_DIR".format(version)):
            os.environ["ANSYS{}_DIR".format(version)] = ansys_install_dir
        if not object_lists:
            object_lists = self.get_liquid_objects()
            assert object_lists, "No Fluids objects found."
        if not min_size or not max_size:
            dims = []
            # try:
            #     dim = self.modeler["Region"].shortest_edge()[0].length
            # except (AttributeError, KeyError, IndexError):
            for obj in object_lists:
                bb = self.modeler[obj].bounding_box
                dd = [abs(bb[3] - bb[0]), abs(bb[4] - bb[1]), abs(bb[5] - bb[2])]
                dims.append(min(dd))
            dim = min(dims)
            if not max_size:
                max_size = dim / 5
            if not min_size:
                min_size = dim / 20
            else:
                min_size = min(min_size, max_size / 4)
        object_lists = self.modeler.convert_to_selections(object_lists, True)
        file_name = self.project_name
        sab_file_pointer = os.path.join(self.working_directory, file_name + ".sab")
        mesh_file_pointer = os.path.join(self.working_directory, file_name + ".msh")
        fl_uscript_file_pointer = os.path.join(self.working_directory, "FLUscript.jou")
        if os.path.exists(mesh_file_pointer):
            os.remove(mesh_file_pointer)
        if os.path.exists(sab_file_pointer):
            os.remove(sab_file_pointer)
        if os.path.exists(fl_uscript_file_pointer):
            os.remove(fl_uscript_file_pointer)
        if os.path.exists(mesh_file_pointer + ".trn"):
            os.remove(mesh_file_pointer + ".trn")
        assert self.export_3d_model(file_name, self.working_directory, ".sab", object_lists), "Failed to export .sab"

        # Building Fluent journal script file *.jou
        fluent_script = open(fl_uscript_file_pointer, "w")
        fluent_script.write("/file/start-transcript " + '"' + mesh_file_pointer + '.trn"\n')
        fluent_script.write(
            '/file/set-tui-version "{}"\n'.format(self.aedt_version_id[-3:-1] + "." + self.aedt_version_id[-1:])
        )
        fluent_script.write("(enable-feature 'serial-hexcore-without-poly)\n")
        fluent_script.write('(cx-gui-do cx-activate-tab-index "NavigationPane*Frame1(TreeTab)" 0)\n')
        fluent_script.write("(%py-exec \"workflow.InitializeWorkflow(WorkflowType=r'Watertight Geometry')\")\n")
        cmd = "(%py-exec \"workflow.TaskObject['Import Geometry']."
        cmd += "Arguments.setState({r'FileName': r'" + sab_file_pointer + "',})\")\n"
        fluent_script.write(cmd)
        fluent_script.write("(%py-exec \"workflow.TaskObject['Import Geometry'].Execute()\")\n")
        fluent_script.write("(%py-exec \"workflow.TaskObject['Add Local Sizing'].AddChildToTask()\")\n")
        fluent_script.write("(%py-exec \"workflow.TaskObject['Add Local Sizing'].Execute()\")\n")
        fluent_script.write("(%py-exec \"meshtype = '{}'\")\n".format(meshtype))
        fluent_script.write('(%py-exec "gr = {}")\n'.format(mesh_growth_rate))
        fluent_script.write('(%py-exec "maxsize = {}")\n'.format(max_size))
        fluent_script.write('(%py-exec "minsize = {}")\n'.format(min_size))
        fluent_script.write('(%py-exec "nlayers = {}")\n'.format(inflation_layer_number))
        fluent_script.write('(%py-exec "pgr = {}")\n'.format(inflation_growth_rate))
        mesh_settings = "(%py-exec \"workflow.TaskObject['Generate the Surface Mesh'].Arguments.setState"
        mesh_settings += "({r'CFDSurfaceMeshControls': {r'CellsPerGap': 3,r'CurvatureNormalAngle': 18,"
        mesh_settings += "r'MaxSize': maxsize,r'MinSize': minsize,r'GrowthRate': gr},})\")\n"

        fluent_script.write(mesh_settings)
        fluent_script.write("(%py-exec \"workflow.TaskObject['Generate the Surface Mesh'].Execute()\")\n")
        cmd = "(%py-exec \"workflow.TaskObject['Describe Geometry'].UpdateChildTasks(SetupTypeChanged=False)\")\n"
        fluent_script.write(cmd)
        cmd = "(%py-exec \"workflow.TaskObject['Describe Geometry']."
        cmd += "Arguments.setState({r'SetupType': r'The geometry consists of only fluid regions with no voids',})\")\n"
        fluent_script.write(cmd)
        cmd = "(%py-exec \"workflow.TaskObject['Describe Geometry'].UpdateChildTasks(SetupTypeChanged=True)\")\n"
        fluent_script.write(cmd)
        cmd = "(%py-exec \"workflow.TaskObject['Describe Geometry'].Arguments.setState({r'InvokeShareTopology': r'Yes',"
        cmd += "r'SetupType': r'The geometry consists of only fluid regions with no voids',r'WallToInternal': "
        cmd += "r'Yes',})\")\n"
        fluent_script.write(cmd)
        cmd = "(%py-exec \"workflow.TaskObject['Describe Geometry'].UpdateChildTasks(SetupTypeChanged=False)\")\n"
        fluent_script.write(cmd)
        fluent_script.write("(%py-exec \"workflow.TaskObject['Describe Geometry'].Execute()\")\n")
        fluent_script.write("(%py-exec \"workflow.TaskObject['Apply Share Topology'].Execute()\")\n")
        fluent_script.write("(%py-exec \"workflow.TaskObject['Update Boundaries'].Execute()\")\n")
        fluent_script.write("(%py-exec \"workflow.TaskObject['Update Regions'].Execute()\")\n")
        fluent_script.write("(%py-exec \"workflow.TaskObject['Add Boundary Layers'].AddChildToTask()\")\n")

        fluent_script.write("(%py-exec \"workflow.TaskObject['Add Boundary Layers'].InsertCompoundChildTask()\")\n")
        cmd = "(%py-exec \"workflow.TaskObject['smooth-transition_1']."
        cmd += "Arguments.setState({r'BLControlName': r'smooth-transition_1',"
        cmd += "r'NumberOfLayers':nlayers, r'Rate':pgr})\")\n"
        fluent_script.write(cmd)
        fluent_script.write("(%py-exec \"workflow.TaskObject['Add Boundary Layers'].Arguments.setState({})\")\n")
        fluent_script.write("(%py-exec \"workflow.TaskObject['smooth-transition_1'].Execute()\")\n")
        # r'VolumeFill': r'hexcore' / r'tetrahedral'
        cmd = "(%py-exec \"workflow.TaskObject['Generate the Volume Mesh'].Arguments.setState({r'VolumeFill': "
        cmd += "meshtype, r'VolumeMeshPreferences': {r'MergeBodyLabels': r'yes',},})\")\n"
        fluent_script.write(cmd)
        fluent_script.write("(%py-exec \"workflow.TaskObject['Generate the Volume Mesh'].Execute()\")\n")
        fluent_script.write("/file/hdf no\n")
        fluent_script.write('/file/write-mesh "' + mesh_file_pointer + '"\n')
        fluent_script.write("/file/stop-transcript\n")
        fluent_script.write("/exit,\n")
        fluent_script.close()
        cmd = os.path.join(self.desktop_install_dir, "fluent", "ntbin", "win64", "fluent.exe")
        if is_linux:  # pragma: no cover
            cmd = os.path.join(ansys_install_dir, "fluent", "bin", "fluent")
        # Fluent command line parameters: -meshing -i <journal> -hidden -tm<x> (# processors for meshing) -wait
        fl_ucommand = [
            cmd,
            "3d",
            "-meshing",
            "-hidden",
            "-i",
        ]
        self.logger.info("Fluent is starting in Background with command line")
        if is_linux:
            fl_ucommand = ["bash"] + fl_ucommand + [fl_uscript_file_pointer]
        else:
            fl_ucommand = ["bash"] + fl_ucommand + ['"' + fl_uscript_file_pointer + '"']
        self.logger.info(" ".join(fl_ucommand))
        subprocess.call(fl_ucommand)
        if os.path.exists(mesh_file_pointer):
            self.logger.info("'" + mesh_file_pointer + "' has been created.")
            return self.mesh.assign_mesh_from_file(object_lists, mesh_file_pointer)
        self.logger.error("Failed to create msh file")

        return False

    @pyaedt_function_handler()
    def apply_icepak_settings(
            self,
            ambienttemp=20,
            gravityDir=5,
            perform_minimal_val=True,
            default_fluid="air",
            default_solid="Al-Extruded",
            default_surface="Steel-oxidised-surface",
    ):
        """Apply Icepak default design settings.

        Parameters
        ----------
        ambienttemp : float, str, optional
            Ambient temperature, which can be an integer or a parameter already
            created in AEDT. The default is ``20``.
        gravityDir : int, optional
            Gravity direction index in the range ``[0, 5]``. The default is ``5``.
        perform_minimal_val : bool, optional
            Whether to perform minimal validation. The default is ``True``.
            If ``False``, full validation is performed.
        default_fluid : str, optional
            Type of fluid. The default is ``"Air"``.
        default_solid : str, optional
            Type of solid. The default is ``"Al-Extruded"``.
        default_surface : str, optional
            Type of surface. The default is ``"Steel-oxidised-surface"``.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.

        References
        ----------

        >>> oDesign.SetDesignSettings
        """
        ambient_temperature = self.modeler._arg_with_dim(ambienttemp, "cel")

        axes = ["X", "Y", "Z"]
        GVPos = False
        if int(gravityDir) > 2:
            GVPos = True
        gravity_axis = axes[int(gravityDir) - 3]
        self.odesign.SetDesignSettings(
            [
                "NAME:Design Settings Data",
                "Perform Minimal validation:=",
                perform_minimal_val,
                "Default Fluid Material:=",
                default_fluid,
                "Default Solid Material:=",
                default_solid,
                "Default Surface Material:=",
                default_surface,
                "AmbientTemperature:=",
                ambient_temperature,
                "AmbientPressure:=",
                "0n_per_meter_sq",
                "AmbientRadiationTemperature:=",
                ambient_temperature,
                "Gravity Vector CS ID:=",
                1,
                "Gravity Vector Axis:=",
                gravity_axis,
                "Positive:=",
                GVPos,
            ],
            ["NAME:Model Validation Settings"],
        )
        return True

    @pyaedt_function_handler()
    def assign_surface_material(self, obj, mat):
        """Assign a surface material to one or more objects.

        Parameters
        ----------
        obj : str, list
            One or more objects to assign surface materials to.
        mat : str
            Material to assign. The material must be present in the database.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.

        References
        ----------

        >>> oEditor.ChangeProperty
        """
        objs = ["NAME:PropServers"]
        objs.extend(self.modeler.convert_to_selections(obj, True))
        try:
            self.modeler.oeditor.ChangeProperty(
                [
                    "NAME:AllTabs",
                    [
                        "NAME:Geometry3DAttributeTab",
                        objs,
                        ["NAME:ChangedProps", ["NAME:Surface Material", "Value:=", '"' + mat + '"']],
                    ],
                ]
            )
        except:
            self.logger.warning("Warning. The material is not the database. Use add_surface_material.")
            return False
        if mat.lower() not in self.materials.surface_material_keys:
            oo = self.get_oo_object(self.oproject, "Surface Materials/{}".format(mat))
            if oo:
                from pyaedt.modules.Material import SurfaceMaterial

                sm = SurfaceMaterial(self.materials, mat, material_update=False)
                sm.coordinate_system = oo.GetPropEvaluatedValue("Coordinate System Type")
                props = oo.GetPropNames()
                if "Surface Emissivity" in props:
                    sm.emissivity = oo.GetPropEvaluatedValue("Surface Emissivity")
                if "Surface Roughness" in props:
                    sm.surface_roughness = oo.GetPropEvaluatedValue("Surface Roughness")
                if "Solar Behavior" in props:
                    sm.surface_clarity_type = oo.GetPropEvaluatedValue("Solar Behavior")
                if "Solar Diffuse Absorptance" in props:
                    sm.surface_diffuse_absorptance = oo.GetPropEvaluatedValue("Solar Diffuse Absorptance")
                if "Solar Normal Absorptance" in props:
                    sm.surface_incident_absorptance = oo.GetPropEvaluatedValue("Solar Normal Absorptance")
                sm.update()
                sm._material_update = True
                self.materials.surface_material_keys[mat.lower()] = sm
        return True

    @pyaedt_function_handler()
    def import_idf(
            self,
            board_path,
            library_path=None,
            control_path=None,
            filter_cap=False,
            filter_ind=False,
            filter_res=False,
            filter_height_under=None,
            filter_height_exclude_2d=False,
            power_under=None,
            create_filtered_as_non_model=False,
            high_surface_thick="0.07mm",
            low_surface_thick="0.07mm",
            internal_thick="0.07mm",
            internal_layer_number=2,
            high_surface_coverage=30,
            low_surface_coverage=30,
            internal_layer_coverage=30,
            trace_material="Cu-Pure",
            substrate_material="FR-4",
            create_board=True,
            model_board_as_rect=False,
            model_device_as_rect=True,
            cutoff_height="5mm",
            component_lib="",
    ):
        """Import an IDF file into an Icepak design.

        Parameters
        ----------
        board_path : str
            Full path to the EMN/BDF file.
        library_path : str
            Full path to the EMP/LDF file. The default is ``None``, in which case a search for an EMP/LDF file
            with the same name as the EMN/BDF file is performed in the folder with the EMN/BDF file.
        control_path : str
            Full path to the XML file. The default is ``None``, in which case a search for an XML file
            with the same name as the EMN/BDF file is performed in the folder with the EMN/BDF file.
        filter_cap : bool, optional
            Whether to filter capacitors from the IDF file. The default is ``False``.
        filter_ind : bool, optional
            Whether to filter inductors from the IDF file. The default is ``False``.
        filter_res : bool, optional
            Whether to filter resistors from the IDF file. The default is ``False``.
        filter_height_under : float or str, optional
            Filter components under a given height. The default is ``None``, in which case
            no components are filtered based on height.
        filter_height_exclude_2d : bool, optional
            Whether to filter 2D components from the IDF file. The default is ``False``.
        power_under : float or str, optional
            Filter components with power under a given mW. The default is ``None``, in which
            case no components are filtered based on power.
        create_filtered_as_non_model : bool, optional
            Whether to set imported filtered components as ``Non-Model``. The default is ``False``.
        high_surface_thick : float or str optional
            High surface thickness. The default is ``"0.07mm"``.
        low_surface_thick : float or str, optional
            Low surface thickness. The default is ``"0.07mm"``.
        internal_thick : float or str, optional
            Internal layer thickness. The default is ``"0.07mm"``.
        internal_layer_number : int, optional
            Number of internal layers. The default is ``2``.
        high_surface_coverage : float, optional
            High surface material coverage. The default is ``30``.
        low_surface_coverage : float, optional
            Low surface material coverage. The default is ``30``.
        internal_layer_coverage : float, optional
            Internal layer material coverage. The default is ``30``.
        trace_material : str, optional
            Trace material. The default is ``"Cu-Pure"``.
        substrate_material : str, optional
            Substrate material. The default is ``"FR-4"``.
        create_board : bool, optional
            Whether to create the board. The default is ``True``.
        model_board_as_rect : bool, optional
            Whether to create the board as a rectangle. The default is ``False``.
        model_device_as_rect : bool, optional
            Whether to create the components as rectangles. The default is ``True``.
        cutoff_height : str or float, optional
            Cutoff height. The default is ``None``.
        component_lib : str, optional
            Full path to the component library.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.

        References
        ----------

        >>> oDesign.ImportIDF
        """
        active_design_name = self.oproject.GetActiveDesign().GetName()
        if not library_path:
            if board_path.endswith(".emn"):
                library_path = board_path[:-3] + "emp"
            if board_path.endswith(".bdf"):
                library_path = board_path[:-3] + "ldf"
        if not control_path and os.path.exists(board_path[:-3] + "xml"):
            control_path = board_path[:-3] + "xml"
        else:
            control_path = ""
        filters = []
        if filter_cap:
            filters.append("Cap")
        if filter_ind:
            filters.append("Ind")
        if filter_res:
            filters.append("Res")
        if filter_height_under:
            filters.append("Height")
        else:
            filter_height_under = "0.1mm"
        if power_under:
            filters.append("Power")
        else:
            power_under = "10mW"
        if filter_height_exclude_2d:
            filters.append("HeightExclude2D")
        if cutoff_height:
            cutoff = True
        else:
            cutoff = False
        if component_lib:
            replace_device = True
        else:
            replace_device = False
        self.odesign.ImportIDF(
            [
                "NAME:Settings",
                "Board:=",
                board_path.replace("\\", "\\\\"),
                "Library:=",
                library_path.replace("\\", "\\\\"),
                "Control:=",
                control_path.replace("\\", "\\\\"),
                "Filters:=",
                filters,
                "CreateFilteredAsNonModel:=",
                create_filtered_as_non_model,
                "HeightVal:=",
                self._arg_with_units(filter_height_under),
                "PowerVal:=",
                self._arg_with_units(power_under, "mW"),
                [
                    "NAME:definitionOverridesMap",
                ],
                ["NAME:instanceOverridesMap"],
                "HighSurfThickness:=",
                self._arg_with_units(high_surface_thick),
                "LowSurfThickness:=",
                self._arg_with_units(low_surface_thick),
                "InternalLayerThickness:=",
                self._arg_with_units(internal_thick),
                "NumInternalLayer:=",
                internal_layer_number,
                "HighSurfaceCopper:=",
                high_surface_coverage,
                "LowSurfaceCopper:=",
                low_surface_coverage,
                "InternalLayerCopper:=",
                internal_layer_coverage,
                "TraceMaterial:=",
                trace_material,
                "SubstrateMaterial:=",
                substrate_material,
                "CreateBoard:=",
                create_board,
                "ModelBoardAsRect:=",
                model_board_as_rect,
                "ModelDeviceAsRect:=",
                model_device_as_rect,
                "Cutoff:=",
                cutoff,
                "CutoffHeight:=",
                self._arg_with_units(cutoff_height),
                "ReplaceDevices:=",
                replace_device,
                "CompLibDir:=",
                component_lib,
            ]
        )
        self.modeler.add_new_objects()
        if active_design_name:
            self.oproject.SetActiveDesign(active_design_name)
        return True

    @pyaedt_function_handler()
    def create_two_resistor_network_block(self, object_name, pcb, power, rjb, rjc):
        """Function to create 2-Resistor network object.
        This method is going to replace create_network_block method.

        Parameters
        ----------
        object_name : str
            name of the object (3D block primitive) on which 2-R network is to be created
        pcb : str
            name of board touching the network block. If the board is a PCB 3D component, enter name of
            3D component instance
        power : float
            junction power in [W]
        rjb : float
            Junction to board thermal resistance in [K/W]
        rjc : float
            Junction to case thermal resistance in [K/W]

        Returns
        -------
        :class:`pyaedt.modules.Boundary.BoundaryObject`
            Boundary object.

        References
        ----------

        >>> oModule.AssignNetworkBoundary

        Examples
        --------
        >>> board = icepak.modeler.create_box([0, 0, 0], [50, 100, 2], "board", "copper")
        >>> box = icepak.modeler.create_box([20, 20, 2], [10, 10, 3], "network_box1", "copper")
        >>> network_block = icepak.create_two_resistor_network_block_new("network_box1", "board", "5W", 2.5, 5)
        >>> network_block.props["Nodes"]["Internal"][0]
        '5W'
        """

        def get_face_normal(obj_face):
            vertex1 = obj_face.vertices[0].position
            vertex2 = obj_face.vertices[1].position
            face_center = obj_face.center_from_aedt
            v1 = [i - j for i, j in zip(vertex1, face_center)]
            v2 = [i - j for i, j in zip(vertex2, face_center)]
            n = GeometryOperators.v_cross(v1, v2)
            normalized_n = GeometryOperators.normalize_vector(n)
            return normalized_n

        net_handle = self.modeler.get_object_from_name(object_name)
        if pcb in self.modeler.user_defined_component_names:
            part_names = sorted(
                [
                    pcb_layer
                    for pcb_layer in self.modeler.get_3d_component_object_list(componentname=pcb)
                    if re.search(self.modeler.user_defined_components[pcb].definition_name + r"_\d\d\d.*", pcb_layer)
                ]
            )

            pcb_layers = [part_names[0], part_names[-1]]
            for layer in pcb_layers:
                x = self.modeler.get_object_from_name(object_name).get_touching_faces(layer)
                if x:
                    board_side = x[0]
                    board_side_normal = get_face_normal(board_side)
                    pcb_handle = self.modeler.get_object_from_name(layer)
            pcb_faces = pcb_handle.faces_by_area(area=1e-5, area_filter=">=")
            for face in pcb_faces:
                pcb_normal = get_face_normal(face)
                dot_product = round(sum([x * y for x, y in zip(board_side_normal, pcb_normal)]))
                if dot_product == -1:
                    pcb_face = face
            pcb_face_normal = get_face_normal(pcb_face)
        else:
            pcb_handle = self.modeler.get_object_from_name(pcb)
            board_side = self.modeler.get_object_from_name(object_name).get_touching_faces(pcb)[0]
            board_side_normal = get_face_normal(board_side)
            for face in pcb_handle.faces:
                pcb_normal = get_face_normal(face)
                dot_product = round(sum([x * y for x, y in zip(board_side_normal, pcb_normal)]))
                if dot_product == -1:
                    pcb_face = face
            pcb_face_normal = get_face_normal(pcb_face)

        for face in net_handle.faces:
            net_face_normal = get_face_normal(face)
            dot_product = round(sum([x * y for x, y in zip(net_face_normal, pcb_face_normal)]))
            if dot_product == 1:
                case_side = face

        props = {
            "Faces": [board_side.id, case_side.id],
            "Nodes": OrderedDict(
                {
                    "Case_side(" + str(case_side) + ")": [case_side.id, "NoResistance"],
                    "Board_side(" + str(board_side) + ")": [board_side.id, "NoResistance"],
                    "Internal": [power],
                }
            ),
            "Links": OrderedDict(
                {
                    "Rjc": ["Case_side(" + str(case_side) + ")", "Internal", "R", str(rjc) + "cel_per_w"],
                    "Rjb": ["Board_side(" + str(board_side) + ")", "Internal", "R", str(rjb) + "cel_per_w"],
                }
            ),
            "SchematicData": ({}),
        }

        self.modeler.primitives[object_name].material_name = "Ceramic_material"
        boundary = BoundaryObject(self, object_name, props, "Network")
        if boundary.create():
            self._boundaries[boundary.name] = boundary
            self.modeler.primitives[object_name].solve_inside = False
            return boundary
        return None

    @pyaedt_function_handler()
    def assign_stationary_wall(
            self,
            geometry,
            boundary_condition,
            name=None,
            temperature="0cel",
            heat_flux="0irrad_W_per_m2",
            thickness="0mm",
            htc="0w_per_m2kel",
            ref_temperature="AmbientTemp",
            material="Al-Extruded",  # relevant if th>0
            radiate=False,
            radiate_surf_mat="Steel-oxidised-surface",  # relevant if radiate = False
            ht_correlation=False,
            ht_correlation_type="Natural Convection",
            ht_correlation_fluid="air",
            ht_correlation_flow_type="Turbulent",
            ht_correlation_flow_direction="X",
            ht_correlation_value_type="Average Values",  # "Local Values"
            ht_correlation_free_stream_velocity="1m_per_sec",
            ht_correlation_surface="Vertical",  # Top, Bottom, Vertical
            ht_correlation_amb_temperature="AmbientTemp",
            shell_conduction=False,
            ext_surf_rad=False,
            ext_surf_rad_material="Stainless-steel-cleaned",
            ext_surf_rad_ref_temp="AmbientTemp",
            ext_surf_rad_view_factor="1",
            **kwargs
    ):
        """Assign surface wall boundary condition.

        Parameters
        ----------
        geometry : str or int
            Name of the surface object or ID of the face.
        boundary_condition : str
            Type of the boundary condition. Options are ``"Temperature"``, ``"Heat Flux"``,
            or ``"Heat Transfer Coefficient"``.
        name : str, optional
            Name of the boundary condition. The default is ``None``.
        temperature : str or float or dict, optional
            Temperature to assign to the wall. This parameter is relevant if
            ``ext_condition="Temperature"``. If a float value is specified, the
            unit is degrees Celsius. A dictionary can be used for transient
             assignment. The dictionary should contain three keys: ``"Type"``, ``"Function"``, and
             ``"Values"``.

             - The value for the ``"Type"`` key must be ``"Transient"``.
             - Accepted values for the ``"Function"`` key are: ``"Linear"``, ``"Power Law"``, ``"Exponential"``,
             ``"Sinusoidal"``, ``"Square Wave"``, and ``"Piecewise Linear"``.
             The ``"Values"`` key contains a list of strings containing the parameters
            required by the ``"Function"`` key selection. For example, ``"Linear"`` requires two parameters:
            the value of the variable at t=0 and the slope of the line. The parameters required by
            each ``Function`` key selection is in Icepak documentation. The parameters must contain the
            units where needed. The default is ``"0cel"``.
        heat_flux : str or float or dict, optional
            Heat flux to assign to the wall. This parameter is relevant if
            ``ext_condition="Temperature"``. If a float value is specified,
            the unit is irrad_W_per_m2. A dictionary can be used for temperature-dependent or transient
            assignment. The dictionary should contain three keys: ``"Type"``, ``"Function"``, and
            ``"Values"``.

             - The value for the ``"Type"`` key must be ``"Transient"``.
             - Accepted values for the ``"Function"`` key are: ``"Linear"``, ``"Power Law"``, ``"Exponential"``,
             ``"Sinusoidal"``, ``"Square Wave"`` and ``"Piecewise Linear"``.
             ``"Values"`` contains a list of strings containing the parameters
            required by the ``"Function"`` selection (e.g. ``"Linear"`` requires two parameters:
            the value of the variable at t=0 and the slope of the line). The parameters required by
            each ``Function`` option is in Icepak documentation. The parameters must contain the
            units where needed. The default is ``"0irrad_W_per_m2"``.
        htc : str or float or dict, optional
            Heat transfer coefficient to assign to the wall. This parameter
            is relevant if ``ext_condition="Heat Transfer Coefficient"``. If a
            float value is specified, the unit is w_per_m2kel.
            A dictionary can be used for temperature dependent or transient
             assignment. The dictionary should contain three keys: ``"Type"``, ``"Function"``, and
             ``"Values"``. Accepted ``"Type"`` values are: ``"Temp Dep"`` and ``"Transient"``.
             - Accepted values for the ``"Function"`` key are: ``"Linear"``, ``"Power Law"``, ``"Exponential"``,
             ``"Sinusoidal"``, ``"Square Wave"`` and ``"Piecewise Linear"``. ``"Temp Dep"`` only
             support the latter. ``"Values"`` contains a list of strings containing the parameters
            required by the ``"Function"`` selection (e.g. ``"Linear"`` requires two parameters:
            the value of the variable at t=0 and the slope of the line). The parameters required by
            each ``Function`` option is in Icepak documentation. The parameters must contain the
            units where needed. The default is ``"0w_per_m2kel"``.
        thickness : str or float, optional
            Thickness of the wall. If a float value is specified, the unit is
            the current unit system set in Icepak. The default is ``"0mm"``.
        ref_temperature : str or float, optional
            Reference temperature for the definition of the heat transfer
            coefficient. This parameter is relevant if
            ``ext_condition="Heat Transfer Coefficient"``. The default
            is ``"AmbientTemp"``.
        material : str, optional
            Solid material of the wall. This parameter is relevant if
            the thickness is a non-zero value. The default is ``"Al-Extruded"``.
        radiate : bool, optional
            Whether to enable the inner surface radiation option. The default is ``False``.
        radiate_surf_mat : str, optional
            Surface material used for inner surface radiation. Relevant if it is enabled.
            The default is ``"Steel-oxidised-surface``.
        ht_correlation : bool, optional
            Whether to use the correlation option to compute the heat transfer coefficient.
            The default is ``False``.
        ht_correlation_type : str, optional
            The correlation type for the heat transfer coefficient. Options are
            "Natural Convection" and "Forced Convection". This parameter is
            relevant if ``ht_correlation=True``. The default is ``"Natural Convection"``.
        ht_correlation_fluid : str, optional
            Fluid for the correlation option. This parameter is relevant if
            ``ht_correlation=True``. The default is ``"air"``.
        ht_correlation_flow_type : str, optional
            Type of flow for the correlation option. This parameter
            is relevant if ``ht_correlation=True``. Options are ``"Turbulent"``
            and ``"Laminar"``. The default is ``"Turbulent"``.
        ht_correlation_flow_direction : str, optional
            Flow direction for the correlation option. This parameter is relevant if
            ``ht_correlation_type="Forced Convection"``. The default is ``"X"``.
        ht_correlation_value_type : str, optional
             Value type for the forced convection correlation option.
             This parameter is relevant if ``ht_correlation_type="Forced Convection"``.
             Options are "Average Values" and "Local Values". The default is
             ``"Average Values"``.
        ht_correlation_free_stream_velocity : str or float, optional
             Free stream flow velocity. This parameter is relevant if
             ``ht_correlation_type="Forced Convection"``. If a float value
             is specified, the default unit is ``m_per_sec``. The default is
             ``"1m_per_sec"``.
        ht_correlation_surface : str, optional
            Surface type for the natural convection correlation option.
            This parameter is relevant if ``ht_correlation_type="Natural Convection"``.
            Options are "Top", "Bottom", and "Vertical". The default is ``"Vertical"``.
        ht_correlation_amb_temperature : str or float, optional
            Ambient temperature for the natural convection correlation option.
            This parameter is relevant if ``ht_correlation_type="Natural Convection"``.
            If a float value is specified, the default unit is degrees Celsius.
            The default is ``"AmbientTemp"``.
        shell_conduction : bool, optional
            Whether to use the shell conduction option. The default is ``False``.
        ext_surf_rad : bool, optional
            Whether to use the external surface radiation option. This parameter
            is relevant if ``ext_condition="Heat Transfer Coefficient"``. The
            default is ``False``.
        ext_surf_rad_material : str, optional
            Surface material for the external surface radiation option. This parameter
            is relevant if ``ext_surf_rad=True``. The default is ``"Stainless-steel-cleaned"``.
        ext_surf_rad_ref_temp : str or float or dict, optional
             Reference temperature for the external surface radiation option. This parameter
             is relevant if  ``ext_surf_rad=True``.  If a float value is specified, the default
             unit is degrees Celsius.  A dictionary can be used for transient
             assignment. The dictionary should contain three keys: ``"Type"``, ``"Function"``, and
             ``"Values"``.

             - The value for the ``"Type"`` key must be ``"Transient"``.
             - Accepted values for the ``"Function"`` key are: ``"Linear"``, ``"Power Law"``, ``"Exponential"``,
             ``"Sinusoidal"``, ``"Square Wave"`` and ``"Piecewise Linear"``.
             ``"Values"`` contains a list of strings containing the parameters
            required by the ``"Function"`` selection (e.g. ``"Linear"`` requires two parameters:
            the value of the variable at t=0 and the slope of the line). The parameters required by
            each ``Function`` option is in Icepak documentation. The parameters must contain the
            units where needed. The default is ``"AmbientTemp"``.
        ext_surf_rad_view_factor : str or float, optional
            View factor for the external surface radiation option. The default is ``"1"``.

        Returns
        -------
        :class:`pyaedt.modules.Boundary.BoundaryObject`
            Boundary object when successful or ``None`` when failed.

        References
        ----------

        >>> oModule.AssignStationaryWallBoundary
        """
        if not name:
            name = generate_unique_name("StationaryWall")
        if isinstance(geometry, str):
            geometry = [geometry]
        elif isinstance(geometry, int):
            geometry = [geometry]
        if not isinstance(thickness, str):
            thickness = "{}{}".format(thickness, self.modeler.model_units)
        if heat_flux is not None and not isinstance(heat_flux, dict) and not isinstance(heat_flux, str):
            heat_flux = "{}irrad_W_per_m2".format(heat_flux)
        if temperature is not None and not isinstance(temperature, dict) and not isinstance(temperature, str):
            temperature = "{}cel".format(temperature)
        if htc is not None and not isinstance(htc, dict) and not isinstance(htc, str):
            htc = "{}w_per_m2kel".format(htc)
        if not isinstance(ref_temperature, str):
            ref_temperature = "{}cel".format(ref_temperature)
        if not isinstance(ht_correlation_free_stream_velocity, str):
            ht_correlation_free_stream_velocity = "{}m_per_sec".format(ht_correlation_free_stream_velocity)
        if not isinstance(ht_correlation_amb_temperature, str):
            ht_correlation_amb_temperature = "{}cel".format(ht_correlation_amb_temperature)
        if not isinstance(ext_surf_rad_view_factor, str):
            ext_surf_rad_view_factor = str(ext_surf_rad_view_factor)

        props = {}
        if isinstance(geometry[0], int):
            props["Faces"] = geometry
        else:
            props["Objects"] = geometry
        props["Thickness"] = (thickness,)
        props["Solid Material"] = material
        props["External Condition"] = boundary_condition
        if "htc_dataset" in kwargs:  # backward compatibility
            warnings.warn("``htc_dataset`` argument is being deprecated. Create a dictionary as per"
                          "documentation and assign it to the ``htc`` argument.", DeprecationWarning)
            if kwargs["htc_dataset"] is not None:
                htc = {"Type": "Temp Dep",
                       "Function": "Piecewise Linear",
                       "Values": kwargs["htc_dataset"],
                       }
        for quantity, assignment_value, to_add in [
            ("External Radiation Reference Temperature", ext_surf_rad_ref_temp, ext_surf_rad),
            ("Heat Transfer Coefficient", htc, boundary_condition == "Heat Transfer Coefficient"),
            ("Temperature", temperature, boundary_condition == "Temperature"),
            ("Heat Flux", heat_flux, boundary_condition == "Heat Flux")
        ]:
            if to_add:
                if isinstance(assignment_value, dict):
                    assignment_value = self._parse_variation_data(
                        quantity,
                        assignment_value["Type"],
                        variation_value=assignment_value["Values"],
                        function=assignment_value["Function"],
                    )
                    if assignment_value is None:  # pragma: no cover
                        return None
                    props.update(assignment_value)
                else:
                    props[quantity] = assignment_value
            else:
                props[quantity] = assignment_value
        props["Reference Temperature"] = ref_temperature
        props["Heat Transfer Data"] = {
            "Heat Transfer Correlation": ht_correlation,
            "Heat Transfer Convection Type": "Forced Convection",
        }
        if ht_correlation:
            props["Heat Transfer Data"].update(
                {
                    "Heat Transfer Correlation": True,
                    "Heat Transfer Convection Type": ht_correlation_type,
                    "Heat Transfer Convection Fluid Material": ht_correlation_fluid,
                }
            )
            if ht_correlation_type == "Forced Convection":
                props["Heat Transfer Data"].update(
                    {
                        "Flow Type": ht_correlation_flow_type,
                        "Flow Direction": ht_correlation_flow_direction,
                        "Heat Transfer Coeff Value Type": ht_correlation_value_type,
                        "Stream Velocity": ht_correlation_free_stream_velocity,
                    }
                )
            elif ht_correlation_type == "Natural Convection":
                props["Heat Transfer Data"].update(
                    {"Surface": ht_correlation_surface, "Ambient Temperature": ht_correlation_amb_temperature}
                )
        props["Radiation"] = {"Radiate": radiate, "RadiateTo": "AllObjects", "Surface Material": radiate_surf_mat}
        props["Shell Conduction"] = shell_conduction
        props["External Surface Radiation"] = ext_surf_rad
        props["External Material"] = ext_surf_rad_material
        props["External Radiation View Factor"] = ext_surf_rad_view_factor
        bound = BoundaryObject(self, name, props, "Stationary Wall")
        return _create_boundary(bound)

    @pyaedt_function_handler()
    def assign_stationary_wall_with_heat_flux(
            self,
            geometry,
            name=None,
            heat_flux="0irrad_W_per_m2",
            thickness="0mm",
            material="Al-Extruded",
            radiate=False,
            radiate_surf_mat="Steel-oxidised-surface",
            shell_conduction=False,
    ):
        """Assign a surface wall boundary condition with specified heat flux.

        Parameters
        ----------
        geometry : str or int
            Name of the surface object or ID of the face.
        name : str, optional
            Name of the boundary condition. The default is ``None``.
        heat_flux : str or float or dict, optional
            Heat flux to assign to the wall. If a float value is
            specified, the unit is ``irrad_W_per_m2``. A dictionary can be used for transient
            assignment. The dictionary should contain three keys: ``"Type"``, ``"Function"``, and
            ``"Values"``.

             - The value for the ``"Type"`` key must be ``"Transient"``.
             - Accepted values for the ``"Function"`` key are: ``"Linear"``, ``"Power Law"``, ``"Exponential"``,
             ``"Sinusoidal"``, ``"Square Wave"`` and ``"Piecewise Linear"``.
             ``"Values"`` contains a list of strings containing the parameters
            required by the ``"Function"`` selection (e.g. ``"Linear"`` requires two parameters:
            the value of the variable at t=0 and the slope of the line). The parameters required by
            each ``Function`` option is in Icepak documentation. The parameters must contain the
            units where needed. The default is ``"0irrad_W_per_m2"``.
        thickness : str or float, optional
            Thickness of the wall. If a float value is specified, the unit is the
            current unit system set in Icepak. The default is ``"0mm"``.
        material : str, optional
            Solid material of the wall. This parameter is relevant if the thickness
            is non-zero. The default is ``"Al-Extruded"``.
        radiate : bool, optional
            Whether to enable the inner surface radiation option. The default is ``False``.
        radiate_surf_mat : str, optional
            Surface material for the inner surface radiation. This parameter is
            relevant if ``radiate`` is enabled. The default is ``"Steel-oxidised-surface``.
        shell_conduction : bool, optional
            Whether to use the shell conduction option. The default is ``False``.

        Returns
        -------
        :class:`pyaedt.modules.Boundary.BoundaryObject`
            Boundary object.

        References
        ----------

        >>> oModule.AssignStationaryWallBoundary
        """
        return self.assign_stationary_wall(
            geometry,
            "Heat Flux",
            name=name,
            heat_flux=heat_flux,
            thickness=thickness,
            material=material,
            radiate=radiate,
            radiate_surf_mat=radiate_surf_mat,
            shell_conduction=shell_conduction,
        )

    @pyaedt_function_handler()
    def assign_stationary_wall_with_temperature(
            self,
            geometry,
            name=None,
            temperature="0cel",
            thickness="0mm",
            material="Al-Extruded",
            radiate=False,
            radiate_surf_mat="Steel-oxidised-surface",
            shell_conduction=False,
    ):
        """Assign a surface wall boundary condition with specified temperature.

        Parameters
        ----------
        geometry : str or int
            Name of the surface object or ID of the face.
        name : str, optional
            Name of the boundary condition. The default is ``None``.
        temperature : str or float or dict, optional
            Temperature to assign to the wall. If a float value is specified,
            the unit is degrees Celsius.  A dictionary can be used for transient
            assignment. The dictionary should contain three keys: ``"Type"``, ``"Function"``, and
            ``"Values"``.

             - The value for the ``"Type"`` key must be ``"Transient"``.
             - Accepted values for the ``"Function"`` key are: ``"Linear"``, ``"Power Law"``, ``"Exponential"``,
             ``"Sinusoidal"``, ``"Square Wave"``, and ``"Piecewise Linear"``.
             The ``"Values"`` key contains a list of strings containing the parameters
            required by the ``"Function"`` key selection. For example, ``"Linear"`` requires two parameters:
            the value of the variable at t=0 and the slope of the line. The parameters required by
            each ``Function`` key selection is in Icepak documentation. The parameters must contain the
            units where needed. The default is ``"0cel"``.
        thickness : str or float, optional
            Thickness of the wall. If a float value is specified used, the unit is the
            current unit system set in Icepak. The default is ``"0mm"``.
        material : str, optional
            Solid material of the wall. This parameter is relevant if the
            thickness is a non-zero value. The default is ``"Al-Extruded"``.
        radiate : bool, optional
            Whether to enable the inner surface radiation option. The default is ``False``.
        radiate_surf_mat : str, optional
            Surface material to use for inner surface radiation. This parameter is relevant
            if ``radiate`` is enabled. The default is ``"Steel-oxidised-surface``.
        shell_conduction : bool, optional
            Whether to use the shell conduction option. The default is ``False``.


        Returns
        -------
        :class:`pyaedt.modules.Boundary.BoundaryObject`
            Boundary object.

        References
        ----------

        >>> oModule.AssignStationaryWallBoundary
        """
        return self.assign_stationary_wall(
            geometry,
            "Temperature",
            name=name,
            temperature=temperature,
            thickness=thickness,
            material=material,
            radiate=radiate,
            radiate_surf_mat=radiate_surf_mat,
            shell_conduction=shell_conduction,
        )

    @pyaedt_function_handler()
    def assign_stationary_wall_with_htc(
            self,
            geometry,
            name=None,
            thickness="0mm",
            material="Al-Extruded",
            htc="0w_per_m2kel",
            ref_temperature="AmbientTemp",
            ht_correlation=False,
            ht_correlation_type="Natural Convection",
            ht_correlation_fluid="air",
            ht_correlation_flow_type="Turbulent",
            ht_correlation_flow_direction="X",
            ht_correlation_value_type="Average Values",
            ht_correlation_free_stream_velocity="1m_per_sec",
            ht_correlation_surface="Vertical",
            ht_correlation_amb_temperature="AmbientTemp",
            ext_surf_rad=False,
            ext_surf_rad_material="Stainless-steel-cleaned",
            ext_surf_rad_ref_temp="AmbientTemp",
            ext_surf_rad_view_factor="1",
            radiate=False,
            radiate_surf_mat="Steel-oxidised-surface",
            shell_conduction=False,
            **kwargs
    ):
        """Assign a surface wall boundary condition with specified heat transfer coefficient.

        Parameters
        ----------
        geometry : str or int
            Name of the surface object or id of the face.
        name : str, optional
            Name of the boundary condition. The default is ``None``.
        htc : str or float or dict, optional
            Heat transfer coefficient to assign to the wall. If a float value
            is specified, the unit is ``w_per_m2kel``. A dictionary can be used for temperature dependent or transient
             assignment. The dictionary should contain three keys: ``"Type"``, ``"Function"``, and
             ``"Values"``. Accepted ``"Type"`` values are: ``"Temp Dep"`` and ``"Transient"``.
             - Accepted values for the ``"Function"`` key are: ``"Linear"``, ``"Power Law"``, ``"Exponential"``,
             ``"Sinusoidal"``, ``"Square Wave"`` and ``"Piecewise Linear"``. ``"Temp Dep"`` only
             support the latter. ``"Values"`` contains a list of strings containing the parameters
            required by the ``"Function"`` selection (e.g. ``"Linear"`` requires two parameters:
            the value of the variable at t=0 and the slope of the line). The parameters required by
            each ``Function`` option is in Icepak documentation. The parameters must contain the
            units where needed. The default is ``"0w_per_m2kel"``.
        thickness : str or float, optional
            Thickness of the wall. If a float value is specified, the unit is the
            current unit system set in Icepak. The default is ``"0mm"``.
        ref_temperature : str or float, optional
            Reference temperature for the definition of the heat transfer
            coefficient. This parameter is relevant if
            ``ext_condition="Heat Transfer Coefficient"``. The default is ``"AmbientTemp"``.
        material : str, optional
            Solid material of the wall. This parameter is relevant if the thickness
            is non-zero. The default is ``"Al-Extruded"``.
        radiate : bool, optional
            Whether to enable the inner surface radiation option. The default is ``False``.
        radiate_surf_mat : str, optional
            Surface material for inner surface radiation. This parameter is relevant
            if ``radiate`` is enabled. The default is ``"Steel-oxidised-surface``.
        ht_correlation : bool, optional
            Whether to use the correlation option to compute the heat transfer
            coefficient. The default is ``False``.
        ht_correlation_type : str, optional
            Correlation type for the correlation option. This parameter is
            relevant if ``ht_correlation=True``. Options are "Natural Convection"
            and "Forced Convection". The default is ``"Natural Convection"``.
        ht_correlation_fluid : str, optional
            Fluid for the correlation option. This parameter is relevant if
            ``ht_correlation=True``. The default is ``"air"``.
        ht_correlation_flow_type : str, optional
            Type of flow for the correlation option. This parameter is relevant
            if ``ht_correlation=True``. Options are ``"Turbulent"`` and ``"Laminar"``.
            The default is ``"Turbulent"``.
        ht_correlation_flow_direction : str, optional
            Flow direction for the correlation option. This parameter is relevant
            if ``ht_correlation_type="Forced Convection"``. The default is ``"X"``.
        ht_correlation_value_type : str, optional
             Value type for the forced convection correlation option. This
             parameter is relevant if ``ht_correlation_type="Forced Convection"``.
             Options are "Average Values" and "Local Values". The default
             is ``"Average Values"``.
        ht_correlation_free_stream_velocity : str or float, optional
             Free stream flow velocity. This parameter is relevant if
             ``ht_correlation_type="Forced Convection"``.  If a float
             value is specified, ``m_per_sec`` is the unit. The default
             is ``"1m_per_sec"``.
        ht_correlation_surface : str, optional
            Surface for the natural convection correlation option. This parameter is
            relevant if ``ht_correlation_type="Natural Convection"``. Options are "Top",
            "Bottom", and "Vertical". The default is ``"Vertical"``.
        ht_correlation_amb_temperature : str or float, optional
            Ambient temperature for the natural convection correlation option.
            This parameter is relevant if ``ht_correlation_type="Natural Convection"``.
            If a float value is specified, the default unit is degrees Celsius. The
            default is ``"AmbientTemp"``.
        shell_conduction : bool, optional
            Whether to use the shell conduction option. The default is ``False``.
        ext_surf_rad : bool, optional
            Whether to use the external surface radiation option. This parameter
            is relevant if ``ext_condition="Heat Transfer Coefficient"``. The default
            is ``False``.
        ext_surf_rad_material : str, optional
            Surface material for the external surface radiation option. This parameter is
            relevant if ``ext_surf_rad=True``. The default is ``"Stainless-steel-cleaned"``.
        ext_surf_rad_ref_temp : str or float or dict, optional
             Reference temperature for the external surface radiation option. This
             parameter is relevant if ``ext_surf_rad=True``. If a float value is
             specified, the default unit is degrees Celsius.
              A dictionary can be used for temperature dependent or transient
             assignment. The dictionary should contain three keys: ``"Type"``, ``"Function"``, and
             ``"Values"``. Accepted ``"Type"`` values are: ``"Temp Dep"`` and ``"Transient"``.
             - Accepted values for the ``"Function"`` key are: ``"Linear"``, ``"Power Law"``, ``"Exponential"``,
             ``"Sinusoidal"``, ``"Square Wave"`` and ``"Piecewise Linear"``. ``"Temp Dep"`` only
             support the latter. ``"Values"`` contains a list of strings containing the parameters
            required by the ``"Function"`` selection (e.g. ``"Linear"`` requires two parameters:
            the value of the variable at t=0 and the slope of the line). The parameters required by
            each ``Function`` option is in Icepak documentation. The parameters must contain the
            units where needed. The default is ``"AmbientTemp"``.
        ext_surf_rad_view_factor : str or float, optional
            View factor for the external surface radiation option. The default is ``"1"``.


        Returns
        -------
        :class:`pyaedt.modules.Boundary.BoundaryObject`
            Boundary object.

        References
        ----------

        >>> oModule.AssignStationaryWallBoundary
        """
        if kwargs.get("htc_dataset", None):
            return self.assign_stationary_wall(
                geometry,
                "Heat Transfer Coefficient",
                name=name,
                thickness=thickness,
                material=material,
                htc=htc,
                htc_dataset=kwargs["htc_dataset"],
                ref_temperature=ref_temperature,
                ht_correlation=ht_correlation,
                ht_correlation_type=ht_correlation_type,
                ht_correlation_fluid=ht_correlation_fluid,
                ht_correlation_flow_type=ht_correlation_flow_type,
                ht_correlation_flow_direction=ht_correlation_flow_direction,
                ht_correlation_value_type=ht_correlation_value_type,
                ht_correlation_free_stream_velocity=ht_correlation_free_stream_velocity,
                ht_correlation_surface=ht_correlation_amb_temperature,
                ht_correlation_amb_temperature=ht_correlation_surface,
                ext_surf_rad=ext_surf_rad,
                ext_surf_rad_material=ext_surf_rad_material,
                ext_surf_rad_ref_temp=ext_surf_rad_ref_temp,
                ext_surf_rad_view_factor=ext_surf_rad_view_factor,
                radiate=radiate,
                radiate_surf_mat=radiate_surf_mat,
                shell_conduction=shell_conduction,
            )
        else:
            return self.assign_stationary_wall(
                geometry,
                "Heat Transfer Coefficient",
                name=name,
                thickness=thickness,
                material=material,
                htc=htc,
                ref_temperature=ref_temperature,
                ht_correlation=ht_correlation,
                ht_correlation_type=ht_correlation_type,
                ht_correlation_fluid=ht_correlation_fluid,
                ht_correlation_flow_type=ht_correlation_flow_type,
                ht_correlation_flow_direction=ht_correlation_flow_direction,
                ht_correlation_value_type=ht_correlation_value_type,
                ht_correlation_free_stream_velocity=ht_correlation_free_stream_velocity,
                ht_correlation_surface=ht_correlation_amb_temperature,
                ht_correlation_amb_temperature=ht_correlation_surface,
                ext_surf_rad=ext_surf_rad,
                ext_surf_rad_material=ext_surf_rad_material,
                ext_surf_rad_ref_temp=ext_surf_rad_ref_temp,
                ext_surf_rad_view_factor=ext_surf_rad_view_factor,
                radiate=radiate,
                radiate_surf_mat=radiate_surf_mat,
                shell_conduction=shell_conduction,
            )

    @pyaedt_function_handler()
    def create_setup(self, setupname="MySetupAuto", setuptype=None, **kwargs):
        """Create an analysis setup for Icepak.
        Optional arguments are passed along with ``setuptype`` and ``setupname``.  Keyword
        names correspond to the ``setuptype``
        corresponding to the native AEDT API.  The list of
        keywords here is not exhaustive.

        .. note::
           This method overrides the ``Analysis.setup()`` method for the HFSS app.

        Parameters
        ----------
        setuptype : int, str, optional
            Type of the setup. Options are ``"IcepakSteadyState"``
            and ``"IcepakTransient"``. The default is ``"IcepakSteadyState"``.
        setupname : str, optional
            Name of the setup. The default is ``"Setup1"``.
        **kwargs : dict, optional
            Available keys depend on setup chosen.
            For more information, see
            :doc:`../SetupTemplatesIcepak`.

        Returns
        -------
        :class:`pyaedt.modules.SolveSetup.SetupHFSS`
            3D Solver Setup object.

        References
        ----------

        >>> oModule.InsertSetup

        Examples
        --------

        >>> from pyaedt import Icepak
        >>> app = Icepak()
        >>> app.create_setup(setupname="Setup1", setuptype="TransientTemperatureOnly", MaxIterations=20)

        """
        if setuptype is None:
            setuptype = self.design_solutions.default_setup
        elif setuptype in SetupKeys.SetupNames:
            setuptype = SetupKeys.SetupNames.index(setuptype)
        if "props" in kwargs:
            return self._create_setup(setupname=setupname, setuptype=setuptype, props=kwargs["props"])
        else:
            setup = self._create_setup(setupname=setupname, setuptype=setuptype)
        setup.auto_update = False
        for arg_name, arg_value in kwargs.items():
            if setup[arg_name] is not None:
                setup[arg_name] = arg_value
        setup.auto_update = True
        setup.update()
        return setup

    @pyaedt_function_handler()
    def _parse_variation_data(self, quantity, variation_type, variation_value, function):
        if variation_type == "Transient" and self.solution_type == "SteadyState":
            self.logger.error("A transient boundary condition cannot be assigned for a non-transient simulation.")
            return None
        if variation_type == "Temp Dep" and function != "Piecewise Linear":
            self.logger.error("Temperature dependent assignment support only piecewise linear function.")
            return None
        out_dict = {"Variation Type": variation_type, "Variation Function": function}
        if function == "Piecewise Linear":
            if not isinstance(variation_value, list):
                variation_value = ["1", "pwl({},Temp)".format(variation_value)]
            else:
                variation_value = [variation_value[0], "pwl({},Temp)".format(variation_value[1])]
            out_dict["Variation Value"] = "[{}]".format(", ".join(['"' + str(i) + '"' for i in variation_value]))
        else:
            if variation_value is not None:
                out_dict["Variation Value"] = "[{}]".format(", ".join([str(i) for i in variation_value]))
        return {"{} Variation Data".format(quantity): out_dict}

    @pyaedt_function_handler()
    def assign_source(
            self,
            assignment,
            thermal_condition,
            assignment_value,
            boundary_name=None,
            radiate=False,
            voltage_current_choice=False,
            voltage_current_value=None,
    ):
        """Create a source power for a face.

        Parameters
        ----------
        assignment : int or str or list
            Integer indicating a face ID or a string indicating an object name. A list of face
            IDs or object names is also accepted.
        thermal_condition : str
            Thermal condition. Accepted values are ``"Total Power"``, ``"Surface Heat"``,
            ``"Temperature"``.
        assignment_value : str or dict
            Value and units of the input power, surface heat or temperature (depending on
            ``thermal_condition``). A dictionary can be used for temperature dependent or transient
             assignment. The dictionary should contain three keys: ``"Type"``, ``"Function"``, and
             ``"Values"``. Accepted ``"Type"`` values are: ``"Temp Dep"`` and ``"Transient"``.
             - Accepted values for the ``"Function"`` key are: ``"Linear"``, ``"Power Law"``, ``"Exponential"``,
             ``"Sinusoidal"``, ``"Square Wave"`` and ``"Piecewise Linear"``. ``"Temp Dep"`` only
             support the latter. ``"Values"`` contains a list of strings containing the parameters
            required by the ``"Function"`` selection (e.g. ``"Linear"`` requires two parameters:
            the value of the variable at t=0 and the slope of the line). The parameters required by
            each ``Function`` option is in Icepak documentation. The parameters must contain the
            units where needed.
        boundary_name : str, optional
            Name of the source boundary. The default is ``None``, in which case the boundary name
            is generated automatically.
        radiate : bool, optional
            Whether to enable radiation. The default is ``False``.
        voltage_current_choice : str or bool, optional
            Whether to assign ``"Voltage"`` or ``"Current"`` or none of them. The default is
            ``False`` (none of them is assigned).
        voltage_current_value : str or dict, optional
            Value and units of current or voltage assignment. A dictionary can be used for
            transient assignment. The dictionary must be structured as described for the
            ``assignment_value`` argument. The default is ``None``.

        Returns
        -------
        :class:`pyaedt.modules.Boundary.BoundaryObject`
            Boundary object when successful or ``None`` when failed.

        References
        ----------

        >>> oModule.AssignSourceBoundary

        Examples
        --------

        >>> from pyaedt import Icepak
        >>> app = Icepak()
        >>> box = app.modeler.create_box([0, 0, 0], [20, 20, 20], name="box")
        >>> ds = app.create_dataset1d_design("Test_DataSet", [1, 2, 3], [3, 4, 5])
        >>> app.solution_type = "Transient"
        >>> b = app.assign_source("box", "Total Power", assignment_value={"Type": "Temp Dep",
        ... "Function": "Piecewise Linear", "Values": "Test_DataSet"})

        """
        default_values = {"Total Power": "0W", "Surface Heat": "0irrad_W_per_m2", "Temperature": "AmbientTemp"}
        if not boundary_name:
            boundary_name = generate_unique_name("Source")
        props = {}
        if not isinstance(assignment, list):
            assignment = [assignment]
        if isinstance(assignment[0], int):
            props["Faces"] = assignment
        elif isinstance(assignment[0], str):
            props["Objects"] = assignment
        props["Thermal Condition"] = thermal_condition
        for quantity, value in default_values.items():
            if quantity == thermal_condition:
                if isinstance(assignment_value, dict):
                    assignment_value = self._parse_variation_data(
                        quantity,
                        assignment_value["Type"],
                        variation_value=assignment_value["Values"],
                        function=assignment_value["Function"],
                    )
                    if assignment_value is None:
                        return None
                    props.update(assignment_value)
                else:
                    props[quantity] = assignment_value
            else:
                props[quantity] = value
        props["Radiation"] = OrderedDict({"Radiate": radiate})
        props["Voltage/Current - Enabled"] = bool(voltage_current_choice)
        default_values = {"Current": "0A", "Voltage": "0V"}
        props["Voltage/Current Option"] = voltage_current_choice
        for quantity, value in default_values.items():
            if voltage_current_choice == quantity:
                if isinstance(voltage_current_value, dict):
                    if voltage_current_value["Type"] == "Temp Dep":
                        self.logger.error("Voltage or Current assignment does not support temperature dependence.")
                        return None
                    voltage_current_value = self._parse_variation_data(
                        quantity,
                        voltage_current_value["Type"],
                        variation_value=voltage_current_value["Values"],
                        function=voltage_current_value["Function"],
                    )
                    if voltage_current_value == None:
                        return None
                    props.update(voltage_current_value)
                else:
                    props[quantity] = voltage_current_value
            else:
                props[quantity] = value

        bound = BoundaryObject(self, boundary_name, props, "SourceIcepak")
        if bound.create():
            self._boundaries[bound.name] = bound
            return bound
        else:
            return None

    @pyaedt_function_handler()
    def create_network_object(self, name=None, props=None, create=False):
        """Create a thermal network.

        Parameters
        ----------
        name : str, optional
           Name of the network object. The default is ``None``, in which case
           the name is generated autotmatically.
        props : dict, optional
            Dictionary with information required by the ``oModule.AssignNetworkBoundary``
            object. The default is ``None``.
        create : bool, optional
            Whether to create immediately the network inside AEDT. The
            default is ``False``, which means the network can be modified
            from PyAEDT functions and the network created only afterwards.

        Returns
        -------
        :class:`pyaedt.modules.Boundary.BoundaryNetwork`
            Boundary network object when successful or ``None`` when failed.

        References
        ----------

        >>> oModule.AssignNetworkBoundary

        Examples
        --------

        >>> from pyaedt import Icepak
        >>> app = Icepak()
        >>> network = app.create_network_object()
        """
        bound = NetworkObject(self, name, props, create)
        if create:
            self._boundaries[bound.name] = bound
        return bound

    @pyaedt_function_handler()
    def create_resistor_network_from_matrix(self, sources_power, faces_ids, matrix, network_name=None, node_names=None):
        """Create a thermal network.

        Parameters
        ----------
        sources_power : list of str or list of float
            List containing all the power value of the internal nodes. If the element of
            the list is a float, the ``W`` unit is used.  Otherwise, the
            unit specified in the string is used.
        faces_ids :  list of int
            All the face IDs that are network nodes.
        matrix : list of list
            Strict lower-square triangular matrix containing the link values between
            the nodes of the network. If the element of the matrix is a float, the
            ``cel_per_w`` unit is used. Otherwise, the unit specified
            in the string is used. The element of the matrix in the i-th row
            and j-th column is the link value between the i-th node and j-th node.
            The list of nodes is automatically created from the lists for the
            ``sources_power`` and ``faces_ids`` parameters (in this order).
        network_name : str, optional
            Name of the network boundary. The default is ``None``, in which
            case the boundary name is generated automatically.
        node_names : list of str, optional
            Name of all the nodes in the network.

        Returns
        -------
        :class:`pyaedt.modules.Boundary.BoundaryNetwork`
            Boundary network object when successful or ``None`` when failed.

        References
        ----------

        >>> oModule.AssignNetworkBoundary

        Examples
        --------

        >>> from pyaedt import Icepak
        >>> app = Icepak()
        >>> box = app.modeler.create_box([0, 0, 0], [20, 50, 80])
        >>> faces_ids = [face.id for face in box.faces][0, 1]
        >>> sources_power = [3, "4mW"]
        >>> matrix = [[0, 0, 0, 0],
        >>>           [1, 0, 0, 0],
        >>>           [0, 3, 0, 0],
        >>>           [1, 2, 4, 0]]
        >>> boundary = app.assign_resistor_network_from_matrix(sources_power, faces_ids, matrix)
        """

        net = self.create_network_object(name=network_name)
        all_nodes = []
        for i, source in enumerate(sources_power):
            node_name = "Source" + str(i) if not node_names else node_names[i]
            net.add_internal_node(name=node_name, power=source)
            all_nodes.append(node_name)
        for i, id in enumerate(faces_ids):
            node_name = None if not node_names else node_names[i + len(sources_power)]
            second = net.add_face_node(id, name=node_name)
            all_nodes.append(second.name)
        for i in range(len(matrix)):
            for j in range(len(matrix[0])):
                if matrix[i][j] > 0:
                    net.add_link(all_nodes[i], all_nodes[j], matrix[i][j], "Link_" + all_nodes[i] + "_" + all_nodes[j])
        if net.create():
            self._boundaries[net.name] = net
            return net
        else:  # pragma: no cover
            return None

    @pyaedt_function_handler
    def assign_solid_block(
            self, object_name, power_assignment, boundary_name=None, htc=None, ext_temperature="AmbientTemp"
    ):
        """
        Assign block boundary for solid objects.

        Parameters
        ----------
        object_name : str or list
            Object name or a list of object names.
        power_assignment : str or dict
            String with the value and units of the power assignment or with
            ``"Joule Heating"``. For a temperature-dependent or transient
            assignment, a dictionary can be used. The dictionary should contain three keys:
            ``"Type"``, ``"Function"``, and ``"Values"``.
            - For the ``"Type"`` key, accepted values are ``"Temp Dep"`` and ``"Transient"``.
            - For the ``"Function"`` key, acceptable values depend on the ``"Type"`` key
            selection. When the ``"Type"`` key is set to ``"Temp Dep"``, the only
            accepted value is ``"Piecewise Linear"``. When the ``"Type"`` key is
            set to ``"Transient"``, acceptable values are `"Exponential"``, `"Linear"``,
            ``"Piecewise Linear"``, ``"Power Law"``, ``"Sinusoidal"``, and ``"SquareWave"``.
            - For the ``"Values"`` key, a list of strings contain the parameters required by
            the ``"Function"`` key selection. For example, when``"Linear"`` is set as the
            ``"Function"`` key, two parameters are required: the value of the variable
            at t=0 and the slope of the line. For the parameters required by each
            ``"Function"`` key selection, see the Icepak documentation. The parameters
            must contain the units where needed.
        boundary_name : str, optional
            Name of the source boundary. The default is ``None``, in which case the
            boundary name is automatically generated.
        htc : float, str, or dict, optional
            String with the value and units of the heat transfer coefficient for the
            external conditions. If a float is provided, the ``"w_per_m2kel"`` unit is used.
            For a temperature-dependent or transient
            assignment, a dictionary can be used. For more information, see the
            description for the preceding ``power_assignment`` parameter. The
            default is ``None``, in which case no external condition is applied.
        ext_temperature : float, str or dict, optional
            String with the value and units of temperature for the external conditions.
            If a float is provided, the ``"cel"`` unit is used.
            For a transient assignment, a dictionary can be used. For more information,
            see the description for the preceding ``power_assignment`` parameter. The
            default is ``"AmbientTemp"``, which is used if the ``htc`` parameter is not
            set to ``None``.

        Returns
        -------
        :class:`pyaedt.modules.Boundary.BoundaryObject`
            Boundary object when successful or ``None`` when failed.

        References
        ----------

        >>> oModule.AssignBlockBoundary

        Examples
        --------
        >>> from pyaedt import Icepak
        >>> ipk = Icepak()
        >>> ipk.solution_type = "Transient"
        >>> box = ipk.modeler.create_box([5, 5, 5], [1, 2, 3], "BlockBox3", "copper")
        >>> power_dict = {"Type": "Transient", "Function": "Sinusoidal", "Values": ["0W", 1, 1, "1s"]}
        >>> block = ipk.assign_solid_block("BlockBox3", power_dict)

        """
        if ext_temperature != "AmbientTemp" and ext_temperature is not None and not htc:
            self.logger.add_error_message("Set an argument for ``htc`` or remove the ``ext_temperature`` argument.")
            return None
        if isinstance(ext_temperature, dict) and ext_temperature["Type"] == "Temp Dep":
            self.logger.add_error_message(
                'It is not possible to use a "Temp Dep" assignment for ' "temperature assignment."
            )
            return None
        if not isinstance(object_name, list):
            object_name = [object_name]
        for o_n in object_name:
            if not self.modeler.get_object_from_name(o_n).solve_inside:
                self.logger.add_error_message(
                    "Use the ``assign_hollow_block()`` method with this object as ``solve_inside`` is ``False``."
                )
                return None
        props = {"Block Type": "Solid", "Objects": object_name}
        if isinstance(power_assignment, dict):
            assignment_value = self._parse_variation_data(
                "Total Power",
                power_assignment["Type"],
                variation_value=power_assignment["Values"],
                function=power_assignment["Function"],
            )
            props.update(assignment_value)
        elif power_assignment == "Joule Heating":
            assignment_value = self._parse_variation_data(
                "Total Power", "Joule Heating", variation_value=None, function="None"
            )
            props.update(assignment_value)
        elif isinstance(power_assignment, (float, int)):
            props["Total Power"] = str(power_assignment) + "W"
        else:
            props["Total Power"] = power_assignment

        if htc:
            props["Use External Conditions"] = True
            for quantity, assignment in [("Temperature", ext_temperature), ("Heat Transfer Coefficient", htc)]:
                if isinstance(assignment, dict):
                    assignment_value = self._parse_variation_data(
                        quantity,
                        assignment["Type"],
                        variation_value=assignment["Values"],
                        function=assignment["Function"],
                    )
                    props.update(assignment_value)
                else:
                    if isinstance(assignment, (float, int)):
                        assignment = str(assignment) + ["w_per_m2kel", "cel"][int(quantity == "Temperature")]
                    props[quantity] = assignment
        else:
            props["Use External Conditions"] = False

        if not boundary_name:
            boundary_name = generate_unique_name("Block")

        bound = BoundaryObject(self, boundary_name, props, "Block")
        return _create_boundary(bound)

    @pyaedt_function_handler
    def assign_hollow_block(
            self, object_name, assignment_type, assignment_value, boundary_name=None, external_temperature="AmbientTemp"
    ):
        """Assign block boundary for hollow objects.

        Parameters
        ----------
        object_name : str or list
            Object name or a list of object names.
        assignment_type : str
            Type of the boundary assignment. Options are ``"Heat Transfer Coefficient"``,
            ``"Heat Flux"``, ``"Temperature"``, and ``"Total Power"``.
        assignment_value : str or dict
            String with value and units of the assignment. If ``"Total Power"`` is
            the assignment type, ``"Joule Heating"`` can be used.
            For a temperature-dependent or transient assignment, a dictionary can be used.
            The dictionary should contain three keys: ``"Type"``, ``"Function"``, and ``"Values"``.
            - For the ``"Type"`` key, accepted values are ``"Temp Dep"`` and ``"Transient"``.
            - For the ``"Function"`` key, acceptable values depend on the ``"Type"`` key selection. When the ``"Type"``
            key is set to ``"Temp Dep"``, the only accepted value is ``"Piecewise Linear"``.
            When the ``"Type"`` key is set to ``"Transient"``, acceptable values are `"Exponential"``, `"Linear"``,
            ``"Piecewise Linear"``, ``"Power Law"``, ``"Sinusoidal"``, and ``"Square Wave"``.
            - For the ``"Values"`` key, a list of strings contain the parameters required by the ``"Function"``
            key selection. For example, when``"Linear"`` is set as the ``"Function"`` key, two parameters are required:
            the value of the variable at t=0 and the slope of the line.
            For the parameters required by each ``"Function"`` key selection, see the Icepak documentation.
            The parameters must contain the units where needed.
        boundary_name : str, optional
            Name of the source boundary. The default is ``None``, in which case the
            boundary is automatically generated.
        external_temperature : str, dict or float, optional
            String with the value and unit of the temperature for the heat transfer
            coefficient. If a float value is specified, the ``"cel"`` unit is automatically
            added.
            For a transient assignment, a dictionary can be used as described for the
            ``assignment_value`` argument. Temperature dependent assignment is not supported.
            The default is ``"AmbientTemp"``.

        Returns
        -------
        :class:`pyaedt.modules.Boundary.BoundaryObject`
            Boundary object when successful or ``None`` when failed.

        References
        ----------

        >>> oModule.AssignBlockBoundary

        Examples
        --------
        >>> from pyaedt import Icepak
        >>> ipk = Icepak()
        >>> ipk.solution_type = "Transient"
        >>> box = ipk.modeler.create_box([5, 5, 5], [1, 2, 3], "BlockBox5", "copper")
        >>> box.solve_inside = False
        >>> temp_dict = {"Type": "Transient", "Function": "Square Wave", "Values": ["1cel", "0s", "1s", "0.5s", "0cel"]}
        >>> block = ipk.assign_hollow_block("BlockBox5", "Heat Transfer Coefficient", "1w_per_m2kel", "Test", temp_dict)

        """
        if assignment_value == "Joule Heating" and assignment_type != "Total Power":
            self.logger.add_error_message(
                '``"Joule Heating"`` assignment is supported only if ``assignment_type``' 'is ``"Total Power"``.'
            )
            return None

        assignment_dict = {
            "Total Power": ["Fixed Heat", "Total Power"],
            "Heat Flux": ["Fixed Heat", "Heat Flux"],
            "Temperature": ["Fixed Temperature", "Fixed Temperature"],
            "Heat Transfer Coefficient": ["Internal Conditions", "Heat Transfer Coefficient"],
        }
        thermal_condition = assignment_dict.get(assignment_type, None)
        if thermal_condition is None:
            self.logger.add_error_message(
                'Valid options for assignment type are "Total Power", "Heat Flux",'
                '"Temperature", and "Heat Transfer Coefficient".'
                "{} not recognized.".format(assignment_type)
            )
            return None

        if not isinstance(object_name, list):
            object_name = [object_name]
        for o_n in object_name:
            if self.modeler.get_object_from_name(o_n).solve_inside:
                self.logger.add_error_message(
                    "Use ``assign_solid_block`` method with this object as ``solve_inside`` is ``True``."
                )
                return None
        props = {"Block Type": "Hollow", "Objects": object_name, "Thermal Condition": thermal_condition[0]}
        if thermal_condition[0] == "Fixed Heat":
            props["Use Total Power"] = thermal_condition[1] == "Total Power"
        if isinstance(assignment_value, dict):
            assignment_value_dict = self._parse_variation_data(
                thermal_condition[1],
                assignment_value["Type"],
                variation_value=assignment_value["Values"],
                function=assignment_value["Function"],
            )
            props.update(assignment_value_dict)
        elif assignment_value == "Joule Heating":
            assignment_value_dict = self._parse_variation_data(
                thermal_condition[1], "Joule Heating", variation_value=None, function="None"
            )
            props.update(assignment_value_dict)
        else:
            props[thermal_condition[1]] = assignment_value
        if thermal_condition[0] == "Internal Conditions":
            if isinstance(external_temperature, dict):
                if external_temperature["Type"] == "Temp Dep":
                    self.logger.add_error_message('It is not possible to use "Temp Dep" for a temperature assignment.')
                    return None
                assignment_value_dict = self._parse_variation_data(
                    "Temperature",
                    external_temperature["Type"],
                    variation_value=external_temperature["Values"],
                    function=external_temperature["Function"],
                )
                props.update(assignment_value_dict)
            else:
                props["Temperature"] = external_temperature

        if not boundary_name:
            boundary_name = generate_unique_name("Block")

        bound = BoundaryObject(self, boundary_name, props, "Block")
        return _create_boundary(bound)

    @pyaedt_function_handler()
    def get_fans_operating_point(self, export_file=None, setup_name=None, timestep=None, design_variation=None):
        """
        Get operating point of the fans in the design.

        Parameters
        ----------
        export_file : str, optional
            Name of the file in which the fans' operating point is saved. The default is
            ``None``, in which case the filename is automatically generated.
        setup_name : str, optional
            Setup name from which to determine the fans' operating point. The default is
            ``None``, in which case the first available setup is used.
        timestep : str, optional
            Time, with units, at which to determine the fans' operating point. The default
            is ``None``, in which case the first available timestep is used. This argument is
            only relevant in transient simulations.
        design_variation : str, optional
            Design variation from which to determine the fans' operating point. The default is
            ``None``, in which case the nominal variation is used.

        Returns
        -------
        list
            First element of the list is the csv filename, the second and third element of
            the list are the quantities with units describing the fan operating point,
            the fourth element contains the dictionary with the name of the fan instances
            as keys and list with volumetric flow rates and pressure rise floats associated
            with the operating points.

        References
        ----------

        >>> oModule.ExportFanOperatingPoint

        Examples
        --------
        >>> from pyaedt import Icepak
        >>> ipk = Icepak()
        >>> ipk.create_fan()
        >>> filename, vol_flow_name, p_rise_name, op_dict= ipk.get_fans_operating_point()
        """

        if export_file is None:
            path = self.temp_directory
            base_name = "{}_{}_FanOpPoint".format(self.project_name, self.design_name)
            export_file = os.path.join(path, base_name + ".csv")
            while os.path.exists(export_file):
                file_name = generate_unique_name(base_name)
                export_file = os.path.join(path, file_name + ".csv")
        if setup_name is None:
            setup_name = "{} : {}".format(self.get_setups()[0], self.solution_type)
        if timestep is None:
            timestep = ""
            if self.solution_type == "Transient":
                self.logger.warning("No timestep specified. First timestep will be exported.")
        else:
            if not self.solution_type == "Transient":
                self.logger.warning("Simulation is steady-state, timestep argument is ignored.")
                timestep = ""
        if design_variation is None:
            design_variation = ""
        self.osolution.ExportFanOperatingPoint(
            [
                "SolutionName:=",
                setup_name,
                "DesignVariationKey:=",
                design_variation,
                "ExportFilePath:=",
                export_file,
                "Overwrite:=",
                True,
                "TimeStep:=",
                timestep,
            ]
        )
        with open(export_file, "r") as f:
            reader = csv.reader(f)
            for line in reader:
                if "Fan Instances" in line:
                    vol_flow = line[1]
                    p_rise = line[2]
                    break
            var = {line[0]: [float(line[1]), float(line[2])] for line in reader}
        return [export_file, vol_flow, p_rise, var]

    @pyaedt_function_handler()
    def assign_free_opening(
            self,
            assignment,
            boundary_name=None,
            temperature="AmbientTemp",
            radiation_temperature="AmbientRadTemp",
            flow_type="Pressure",
            pressure="AmbientPressure",
            no_reverse_flow=False,
            velocity=["0m_per_sec", "0m_per_sec", "0m_per_sec"],
            mass_flow_rate="0kg_per_s",
            inflow=True,
            direction_vector=None,
    ):
        """
        Assign free opening boundary condition.

        Parameters
        ----------
        assignment : int or str or list
            Integer indicating a face ID or a string indicating an object name. A list of face
            IDs or object names is also accepted.
        boundary_name : str, optional
            Boundary name. Default is ``None``, in which case the name is generated automatically.
        temperature : str or float or dict, optional
            Prescribed temperature at the boundary. If a string is set,  a variable name or a
            number with the unit is expected. If a float is set, the unit ``'cel'`` is
            automatically added. Also, a dictionary containing the keys ``'Function'`` and ``'Values'``
            can be passed to set a transient behaviour. The acceptable values associated with those
            keys can be found in the Icepak documentation. Default is ``"AmbientTemp"``.
        radiation_temperature : str or float, optional
            Prescribed radiation temperature at the boundary. If a string is set,  a variable name
            or a number with the unit is expected. If a float is set, the unit ``'cel'`` is
            automatically added. Also, a dictionary containing the keys ``'Function'`` and
            ``'Values'`` can be passed to set a transient behaviour.
            The acceptable values associated with those keys can be found in the Icepak documentation.
            Default is ``"AmbientRadTemp"``.
        flow_type : int or str, optional
            Prescribed radiation flow type at the boundary. Available options are ``"Pressure"``,
            ``"Velocity"``, and ``"Mass Flow"``. The default is ``"Pressure"``.
        pressure : float or str or dict, optional
            Prescribed pressure (static or total coherently with flow type) at the boundary. If a
            string is set, a variable name or a number with the unit is expected. If a float is set,
            the unit ``'pascal'`` is automatically added. Also, a dictionary containing the keys
            ``'Function'`` and ``'Values'`` can be passed to set a transient behavior. The acceptable
            values associated with those keys can be found in the Icepak documentation.
            The default is ``"AmbientPressure"``.
        no_reverse_flow : bool, optional
            Option to block reverse flow at the boundary. Default is ``False``.
        velocity : list, optional
            Prescribed velocity at the boundary. If a list of strings is set, a variable name or a number
             with the unit is expected for each element. If list of floats is set, the unit ``'m_per_sec'``
            is automatically added. Also, a dictionary containing the keys ``'Function'`` and
            ``'Values'`` can be passed in one or more vector element to set a transient behaviour.
            The acceptable values associated with those keys can be found in the Icepak documentation.
            Default is ``["0m_per_sec", "0m_per_sec", "0m_per_sec"]``.
        mass_flow_rate : float or str or dict, optional
            Prescribed pressure (static or total coherently with flow type) at the boundary. If a
            string is set, a variable name or a number with the unit is expected. If a float is set,
            the unit ``'kg_per_s'`` is automatically added. Also, a dictionary containing the keys
            ``'Function'`` and ``'Values'`` can be passed to set a transient behaviour. The acceptable
            values associated with those keys can be found in the Icepak documentation.
            Default is ``"0kg_per_s"``.
        inflow : bool, optional
            Prescribe if the imposed mass flow is an inflow or an outflow. Default is ``"True"``,
            in which case an inflow is prescribed.
        direction_vector : list, optional
            Prescribe the direction of the massflow. Default is ``"None"``, in which case a
            massflow normal to the boundary is prescribed.

        Returns
        -------
        :class:`pyaedt.modules.Boundary.BoundaryObject`
            Boundary object when successful or ``None`` when failed.

        References
        ----------
        oModule.AssignOpeningBoundary

        Examples
        ----------
        >>> import pyaedt
        >>> icepak = pyaedt.Icepak()
        >>> f_id = icepak.modeler["Region"].faces[0].id
        >>> icepak.assign_free_opening(f_id)

        """
        # Sanitize input
        for i in range(len(velocity)):
            if not isinstance(velocity[i], str) and not isinstance(velocity[i], dict):
                velocity[i] = str(velocity[i]) + "m_per_sec"
        if not isinstance(mass_flow_rate, str) and not isinstance(mass_flow_rate, dict):
            mass_flow_rate = str(mass_flow_rate) + "kg_per_s"
        if not isinstance(temperature, str) and not isinstance(temperature, dict):
            temperature = str(temperature) + "cel"
        if not isinstance(radiation_temperature, str) and not isinstance(radiation_temperature, dict):
            radiation_temperature = str(radiation_temperature) + "cel"
        if not isinstance(pressure, str) and not isinstance(pressure, dict):
            pressure = str(pressure) + "pascal"
        # Dict creation
        props = {}
        if not isinstance(assignment, list):
            assignment = [assignment]
        if isinstance(assignment[0], int):
            props["Faces"] = assignment
        else:
            props["Objects"] = assignment
        possible_transient_properties = [
            ("Temperature", temperature),
            ("External Rad. Temperature", radiation_temperature),
        ]
        if flow_type == "Pressure":
            props["Inlet Type"] = flow_type
            props["No Reverse Flow"] = no_reverse_flow
            possible_transient_properties += [("Total Pressure", pressure)]
        elif flow_type == "Velocity":
            props["Inlet Type"] = flow_type
            possible_transient_properties += [
                ("Static Pressure", pressure),
                ("X Velocity", velocity[0]),
                ("Y Velocity", velocity[1]),
                ("Z Velocity", velocity[2]),
            ]
        elif flow_type == "Mass Flow":
            props["Inlet Type"] = flow_type
            if direction_vector is None:
                props["Mass Flow Direction"] = ("Normal to Boundary",)
            else:
                props["X"] = str(direction_vector[0])
                props["Y"] = str(direction_vector[1])
                props["Z"] = str(direction_vector[2])
            props["Mass Flow Condition"] = ["Out Flow", "In Flow"][int(inflow)]
            possible_transient_properties += [
                ("Total Pressure", pressure),
                ("Mass Flow Rate", mass_flow_rate),
                ("Y Velocity", velocity[1]),
                ("Z Velocity", velocity[2]),
            ]
        for quantity, assignment in possible_transient_properties:
            if isinstance(assignment, dict):
                if not self.solution_type == "Transient":
                    self.logger.error("Transient assignment is supported only in transient designs.")
                    return None
                assignment = self._parse_variation_data(
                    quantity,
                    "Transient",
                    variation_value=assignment["Values"],
                    function=assignment["Function"],
                )
                if assignment is None:
                    return None
                props.update(assignment)
            else:
                props[quantity] = assignment

        if not boundary_name:
            boundary_name = generate_unique_name("Opening")

        bound = BoundaryObject(self, boundary_name, props, "Opening")
        if bound.create():
            self._boundaries[bound.name] = bound
            return bound
        else:
            return None

    @pyaedt_function_handler()
    def assign_pressure_free_opening(
            self,
            assignment,
            boundary_name=None,
            temperature="AmbientTemp",
            radiation_temperature="AmbientRadTemp",
            pressure="AmbientPressure",
            no_reverse_flow=False,
    ):
        """
        Assign free opening boundary condition.

        Parameters
        ----------
        assignment : int or str or list
           Integer indicating a face ID or a string indicating an object name. A list of face
           IDs or object names is also accepted.
        boundary_name : str, optional
            Boundary name. Default is ``None``, in which case the name is generated automatically.
        temperature : str or float or dict, optional
            Prescribed temperature at the boundary. If a string is set,  a variable name or a
            number with the unit is expected. If a float is set, the unit ``'cel'`` is
            automatically added. Also, a dictionary containing the keys ``'Function'`` and ``'Values'``
            can be passed to set a transient behaviour. The acceptable values associated with those
            keys can be found in the Icepak documentation. Default is ``"AmbientTemp"``.
        radiation_temperature : str or float, optional
            Prescribed radiation temperature at the boundary. If a string is set,  a variable name
            or a number with the unit is expected. If a float is set, the unit ``'cel'`` is
            automatically added. Also, a dictionary containing the keys ``'Function'`` and
            ``'Values'`` can be passed to set a transient behaviour.
            The acceptable values associated with those keys can be found in the Icepak documentation.
            Default is ``"AmbientRadTemp"``.
        pressure : float or str or dict, optional
            Prescribed pressure (static or total coherently with flow type) at the boundary. If a
            string is set, a variable name or a number with the unit is expected. If a float is set,
            the unit ``'pascal'`` is automatically added. Also, a dictionary containing the keys
            ``'Function'`` and ``'Values'`` can be passed to set a transient behavior. The
            acceptable values associated with those keys can be found in the Icepak
            documentation. The default is ``"AmbientPressure"``.
        no_reverse_flow : bool, optional
            Option to block reverse flow at the boundary. Default is ``False``.


        Returns
        -------
        :class:`pyaedt.modules.Boundary.BoundaryObject`
            Boundary object when successful or ``None`` when failed.

        References
        ----------
        oModule.AssignOpeningBoundary

        Examples
        ----------
        >>> import pyaedt
        >>> icepak = pyaedt.Icepak()
        >>> f_id = icepak.modeler["Region"].faces[0].id
        >>> icepak.assign_pressure_free_opening(f_id)
        """
        return self.assign_free_opening(
            assignment,
            boundary_name=boundary_name,
            temperature=temperature,
            radiation_temperature=radiation_temperature,
            flow_type="Pressure",
            pressure=pressure,
            no_reverse_flow=no_reverse_flow,
        )

    @pyaedt_function_handler()
    def assign_velocity_free_opening(
            self,
            assignment,
            boundary_name=None,
            temperature="AmbientTemp",
            radiation_temperature="AmbientRadTemp",
            pressure="AmbientPressure",
            velocity=["0m_per_sec", "0m_per_sec", "0m_per_sec"],
    ):
        """
        Assign free opening boundary condition.

        Parameters
        ----------
        assignment : int or str or list
            Integer indicating a face ID or a string indicating an object name. A list of face
            IDs or object names is also accepted.
        boundary_name : str, optional
            Boundary name. Default is ``None``, in which case the name is generated automatically.
        temperature : str or float or dict, optional
            Prescribed temperature at the boundary. If a string is set,  a variable name or a
            number with the unit is expected. If a float is set, the unit ``'cel'`` is
            automatically added. Also, a dictionary containing the keys ``'Function'`` and ``'Values'``
            can be passed to set a transient behaviour. The acceptable values associated with those
            keys can be found in the Icepak documentation. Default is ``"AmbientTemp"``.
        radiation_temperature : str or float, optional
            Prescribed radiation temperature at the boundary. If a string is set,  a variable name
            or a number with the unit is expected. If a float is set, the unit ``'cel'`` is
            automatically added. Also, a dictionary containing the keys ``'Function'`` and
            ``'Values'`` can be passed to set a transient behaviour.
            The acceptable values associated with those keys can be found in the Icepak documentation.
            Default is ``"AmbientRadTemp"``.
        pressure : float or str or dict, optional
            Prescribed pressure (static or total coherently with flow type) at the boundary. If a
            string is set, a variable name or a number with the unit is expected. If a float is set,
            the unit ``'pascal'`` is automatically added. Also, a dictionary containing the keys
            ``'Function'`` and ``'Values'`` can be passed to set a transient behavior. The
            acceptable values associated with those keys can be found in the Icepak
            documentation. The default is ``"AmbientPressure"``.
        velocity : list, optional
            Prescribed velocity at the boundary. If a list of strings is set, a variable name or a number
             with the unit is expected for each element. If list of floats is set, the unit ``'m_per_sec'``
            is automatically added. Also, a dictionary containing the keys ``'Function'`` and
            ``'Values'`` can be passed in one or more vector element to set a transient behaviour.
            The acceptable values associated with those keys can be found in the Icepak documentation.
            Default is ``["0m_per_sec", "0m_per_sec", "0m_per_sec"]``.


        Returns
        -------
        :class:`pyaedt.modules.Boundary.BoundaryObject`
            Boundary object when successful or ``None`` when failed.

        References
        ----------
        oModule.AssignOpeningBoundary

        Examples
        ----------
        >>> import pyaedt
        >>> icepak = pyaedt.Icepak()
        >>> f_id = icepak.modeler["Region"].faces[0].id
        >>> icepak.assign_velocity_free_opening(f_id)
        """
        return self.assign_free_opening(
            assignment,
            boundary_name=boundary_name,
            temperature=temperature,
            radiation_temperature=radiation_temperature,
            flow_type="Velocity",
            pressure=pressure,
            velocity=velocity,
        )

    @pyaedt_function_handler()
    def assign_mass_flow_free_opening(
            self,
            assignment,
            boundary_name=None,
            temperature="AmbientTemp",
            radiation_temperature="AmbientRadTemp",
            pressure="AmbientPressure",
            mass_flow_rate="0kg_per_s",
            inflow=True,
            direction_vector=None,
    ):
        """
        Assign free opening boundary condition.

        Parameters
        ----------
        assignment : int or str or list
           Integer indicating a face ID or a string indicating an object name. A list of face
           IDs or object names is also accepted.
        boundary_name : str, optional
            Boundary name. The default is ``None``, in which case the name is generated automatically.
        temperature : str or float or dict, optional
            Prescribed temperature at the boundary. If a string is set,  a variable name or a
            number with the unit is expected. If a float is set, the unit ``'cel'`` is
            automatically added. Also, a dictionary containing the keys ``'Function'`` and ``'Values'``
            can be passed to set a transient behaviour. The acceptable values associated with those
            keys can be found in the Icepak documentation. Default is ``"AmbientTemp"``.
        radiation_temperature : str or float, optional
            Prescribed radiation temperature at the boundary. If a string is set,  a variable name
            or a number with the unit is expected. If a float is set, the unit ``'cel'`` is
            automatically added. Also, a dictionary containing the keys ``'Function'`` and
            ``'Values'`` can be passed to set a transient behaviour.
            The acceptable values associated with those keys can be found in the Icepak documentation.
            Default is ``"AmbientRadTemp"``.
        pressure : float or str or dict, optional
            Prescribed pressure (static or total coherently with flow type) at the boundary. If a
            string is set, a variable name or a number with the unit is expected. If a float is set,
            the unit ``'pascal'`` is automatically added. Also, a dictionary containing the keys
            ``'Function'`` and ``'Values'`` can be passed to set a transient behavior. The
            acceptable values associated with those keys can be found in the Icepak
            documentation. The default is ``"AmbientPressure"``.
        mass_flow_rate : float or str or dict, optional
            Prescribed pressure (static or total coherently with flow type) at the boundary. If a
            string is set, a variable name or a number with the unit is expected. If a float is set,
            the unit ``'kg_per_s'`` is automatically added. Also, a dictionary containing the keys
            ``'Function'`` and ``'Values'`` can be passed to set a transient behaviour. The acceptable
            values associated with those keys can be found in the Icepak documentation.
            Default is ``"0kg_per_s"``.
        inflow : bool, optional
            Prescribe if the imposed mass flow is an inflow or an outflow. Default is ``"True"``,
            in which case an inflow is prescribed.
        direction_vector : list, optional
            Prescribe the direction of the massflow. Default is ``"None"``, in which case a
            massflow normal to the boundary is prescribed.


        Returns
        -------
        :class:`pyaedt.modules.Boundary.BoundaryObject`
            Boundary object when successful or ``None`` when failed.

        References
        ----------
        oModule.AssignOpeningBoundary

        Examples
        ----------
        >>> import pyaedt
        >>> icepak = pyaedt.Icepak()
        >>> f_id = icepak.modeler["Region"].faces[0].id
        >>> icepak.assign_mass_flow_free_opening(f_id)
        """
        return self.assign_free_opening(
            assignment,
            boundary_name=boundary_name,
            temperature=temperature,
            radiation_temperature=radiation_temperature,
            flow_type="Mass Flow",
            pressure=pressure,
            mass_flow_rate=mass_flow_rate,
            inflow=inflow,
            direction_vector=direction_vector,
        )

    @pyaedt_function_handler()
    def assign_symmetry_wall(self, geometry, boundary_name=None):
        """Assign symmetry wall boundary condition.

        Parameters
        ----------
        geometry : str or int or list
            Surface object name or face ID. A list of surface object names
            or face IDs is also acceptable.
        boundary_name : str, optional
            Name of the boundary condition. The default is ``None``.

        Returns
        -------
        :class:`pyaedt.modules.Boundary.BoundaryObject`
            Boundary object when successful or ``None`` when failed.

        References
        ----------

        >>> oModule.AssignSymmetryWallBoundary
        """
        if not boundary_name:
            boundary_name = generate_unique_name("SymmetryWall")
        if isinstance(geometry, (str, int)):
            geometry = [geometry]

        props = {}
        if isinstance(geometry[0], int):
            props["Faces"] = geometry
        else:
            props["Objects"] = geometry

        bound = BoundaryObject(self, boundary_name, props, "Symmetry Wall")
        return _create_boundary(bound)

    @pyaedt_function_handler()
    def assign_adiabatic_plate(self, assignment, high_radiation_dict=None, low_radiation_dict=None, boundary_name=None):
        """
        Assign adiabatic plate boundary condition.

        Parameters
        ----------
        assignment : list
            List of strings containing object names, or list of integers
            containing face ids or list of faces or objects.
        high_radiation_dict : dictionary, optional
            Dictionary containing the radiation assignment for the high side.
            The two keys that are always required are ``"RadiateTo"`` and
            ``"Surface Material"``. If the value of ``"RadiateTo"`` is
            ``"RefTemperature"``, then the others required keys are
            ``"Ref. Temperature"`` and ``"View Factor"``. The other possible
            value of ``"RadiateTo"`` is ``"AllObjects"``. Default is ``None``
            in which case the radiation on the high side is set to off.
        low_radiation_dict : dictionary, optional
            Dictionary containing the radiation assignment for the low side.
            The dictionary structure is the same of ``high_radiation_dict``.
            Default is ``None``, in which case the radiation on the low side
            is set to off.

        Returns
        -------
        :class:`pyaedt.modules.Boundary.BoundaryObject`
            Boundary object when successful or ``None`` when failed.

        References
        ----------

        >>> oModule.AssignAdiabaticPlateBoundary

        Examples
        --------
        >>> from pyaedt import Icepak
        >>> ipk = Icepak()
        >>> box = ipk.modeler.create_box([5, 5, 5], [1, 2, 3], "Box", "copper")
        >>> ad_plate = ipk.assign_adiabatic_plate(box.top_face_x, None, {"RadiateTo": "AllObjects"})

        """
        if not isinstance(assignment, list):
            assignment = [assignment]
        if isinstance(assignment[0], str):
            key = "Objects"
        elif isinstance(assignment[0], int):
            key = "Faces"
        elif isinstance(assignment[0], FacePrimitive):
            key = "Faces"
            assignment = [f.id for f in assignment]
        else:
            key = "Objects"
            assignment = [o.name for o in assignment]
        props = {key: assignment}
        for rad_dict, side in zip([high_radiation_dict, low_radiation_dict], ["HighSide", "LowSide"]):
            props[side] = {"Radiate": bool(rad_dict)}
            if rad_dict is not None:
                for k, v in rad_dict.items():
                    if side == "HighSide":
                        if k == "RadiateTo":
                            v += " - High"
                        k += " - High"
                    props[side][k] = v

        if not boundary_name:
            boundary_name = generate_unique_name("AdiabaticPlate")

        bound = BoundaryObject(self, boundary_name, props, "Adiabatic Plate")
        try:
            if bound.create():
                self._boundaries[bound.name] = bound
                return bound
            else:  # pragma: no cover
                raise SystemExit
        except (GrpcApiError, SystemExit):  # pragma: no cover
            return None

    @pyaedt_function_handler()
    def assign_resistance(self, objects, boundary_name=None, total_power="0W", fluid="air", laminar=False,
                          loss_type="Device", linear_loss = ["1m_per_sec", "1m_per_sec", "1m_per_sec"],
                          quadratic_loss = [1, 1, 1], linear_loss_free_area_ratio = [1, 1, 1],
                          quadratic_loss_free_area_ratio = [1, 1, 1], power_law_constant=1, power_law_exponent=1,
                          loss_curves_x = [[0, 1], [0, 1]], loss_curves_y = [[0, 1], [0, 1]],
                          loss_curves_z = [[0, 1], [0, 1]], loss_curve_flow_unit = "m_per_sec",
                          loss_curve_pressure_unit = "n_per_meter_sq"):
        """
        Assign resistance boundary condition.

        Parameters
        ----------
        objects : list or str
            A list of objects to which the resistance condition will be
            assigned. It can be a single object (a string) or multiple
            objects specified as a list.
        boundary_name : str, optional
            The name of the boundary object that will be created. If not
            provided, a unique name will be generated. Default is ``None``.
        total_power : str, float, or dict, optional
            The total power transferred to the fluid through the resistance
            volume. It is specified as a string with value and unit, a float
            where the default unit "W" will be used, or a dictionary for
            transient assignment. The dictionary should contain two keys:
            ``"Function"`` and ``"Values"``.

            - For the ``"Function"`` key, options are ``"Exponential"``,
            ``"Linear"``, ``"Piecewise Linear"``, ``"Power Law"``,
            ``"Sinusoidal"``, and ``"Square Wave"``.
            - For the ``"Values"`` key, provide a list of strings containing
            the parameters required by the ``"Function"`` key selection. For
            example, when ``"Linear"`` is set as the ``"Function"`` key, two
            parameters are required: the value of the variable at t=0 and the
            slope of the line. For the parameters required by each
            ``"Function"`` key selection, see the Icepak documentation.

            Default is ``"0W"``.
        fluid : str, optional
            The material of the volume to which the resistance is being
            assigned. Default is ``"air"``.
        laminar : bool, optional
            Whether the flow inside the volume must be treated as laminar or
            not. Default is ``False``.
        loss_type : str, optional
            Type of pressure loss model to be used. It can have one of the
            following values: ``"Device"``, ``"Power Law"``, and
            ``"Loss Curve"``. Default is ``"Device"``.
        linear_loss : list of floats or list of strings, optional
            Three values representing the linear loss coefficients in the X, Y,
            and Z directions. These coefficients can be expressed as floats, in
            which case the default unit ``"m_per_sec"`` will be used, or as
            strings. Relevant only if ``loss_type=="Device"``.  Default is
            ``"1m_per_sec"`` for all three directions.
        quadratic_loss : list of floats or list of strings, optional
            Three values representing the quadratic loss coefficients in the X,
            Y, and Z directions. Relevant only if ``loss_type=="Device"``.
            Default is ``1`` for all three directions.
        linear_loss_free_area_ratio : list of floats or list of strings, optional
            Three values representing the linear loss free area ratio in the X,
            Y, and Z directions. Relevant only if ``loss_type=="Device"``.
            Default is ``1`` for all three directions.
        quadratic_loss_free_area_ratio : list of floats or list of strings, optional
            Three values representing the quadratic loss coefficient for each
            direction (X, Y, Z) in the loss model. Relevant only if
            ``loss_type=="Device"``. Default is ``1`` for all three directions.
        power_law_constant : str or float, optional
            Specifies the coefficient in the power law equation for pressure loss. Default is ``1``.
        power_law_exponent : str or float, optional
            Specifies the exponent value in the power law equation for pressure loss calculation. Default is ``1``.
        loss_curves_x : list of lists of float
            List of two list defining the loss curve in the X direction. The
            first list contains the mass flow rate value of the curve while
            the second contains the pressure values. Units can be specified with
            the ``loss_curve_flow_unit`` and ``loss_curve_pressure_unit``
            parameters. Default is ``[[0,1],[0,1]]``.
        loss_curves_y : list of lists of float
            List of two list defining the loss curve in the Y direction. The
            first list contains the mass flow rate value of the curve while
            the second contains the pressure values. Units can be specified with
            the ``loss_curve_flow_unit`` and ``loss_curve_pressure_unit``
            parameters. Default is ``[[0,1],[0,1]]``.
        loss_curves_z : list of lists of float
            List of two list defining the loss curve in the Z direction. The
            first list contains the mass flow rate value of the curve while the
            second contains the pressure values. Units can be specified with the
            ``loss_curve_flow_unit`` and ``loss_curve_pressure_unit``
            parameters. Default is ``[[0,1],[0,1]]``.
        loss_curve_flow_unit : str, optional
            Specifies the unit of flow rate in the loss curvev (for all
            directions). Default is ``"m_per_sec"``.
        loss_curve_pressure_unit : str, optional
            Specifies the unit of pressure drop in the loss curve (for all
            directions). Default is ``"n_per_meter_sq"``.

        Returns
        -------
        :class:`pyaedt.modules.Boundary.BoundaryObject`
            Boundary object when successful or ``None`` when failed.

        References
        ----------

        >>> oModule.AssignResistanceBoundary

        Examples
        --------
        """
        props = {"Objects": objects if isinstance(objects, list) else [objects], "Fluid Material": fluid,
                 "Laminar Flow": laminar}

        if loss_type == "Device":
            for direction, linear, quadratic, linear_far, quadratic_far in zip(["X", "Y", "Z"], linear_loss,
                                                                               quadratic_loss,
                                                                               linear_loss_free_area_ratio,
                                                                               quadratic_loss_free_area_ratio):
                props.update({
                    "Linear " + direction + " Coefficient": str(linear) + "m_per_sec" if not isinstance(linear,
                                                                                                   str) else str(
                        linear),
                    "Quadratic " + direction + " Coefficient": str(quadratic),
                    "Linear " + direction + " Free Area Ratio": str(linear_far),
                    "Quadratic " + direction + " Free Area Ratio": str(quadratic_far)
                })
        elif loss_type == "Power Law":
            props.update({
                "Pressure Loss Model": "Power Law",
                "Power Law Coefficient": power_law_constant,
                "Power Law Exponent": power_law_exponent
            })
        elif loss_type == "Loss Curve":
            props.update({"Pressure Loss Model": "Loss Curve"})
            for direction, values in zip(["X", "Y", "Z"], [loss_curves_x, loss_curves_y, loss_curves_z]):
                key = "Pressure Loss Curve {}".format(direction)
                props[key] = {
                    "DimUnits": [loss_curve_flow_unit, loss_curve_pressure_unit],
                    "X": [str(i) for i in values[0]],
                    "Y": [str(i) for i in values[1]]
                }

        if isinstance(total_power, dict):
            if not self.solution_type == "Transient":
                self.logger.error("Transient assignment is supported only in transient designs.")
                return None
            assignment = self._parse_variation_data(
                "Thermal Power",
                "Transient",
                variation_value=total_power["Values"],
                function=total_power["Function"],
            )
            props.update(assignment)
        else:
            props["Thermal Power"] = total_power

        if not boundary_name:
            boundary_name = generate_unique_name("Resistance")

        bound = BoundaryObject(self, boundary_name, props, "Resistance")
        try:
            if bound.create():
                self._boundaries[bound.name] = bound
                return bound
            else:  # pragma: no cover
                raise SystemExit
        except (GrpcApiError, SystemExit):  # pragma: no cover
            return None

    @pyaedt_function_handler()
    def assign_power_law_resistance(self, objects, boundary_name=None, total_power="0W", fluid="air", laminar=False,
                          power_law_constant=1, power_law_exponent=1):
        """
        Assign resistance boundary condition prescribing a power law.

        Parameters
        ----------
        objects : list or str
            A list of objects to which the resistance condition will be
            assigned. It can be a single object (a string) or multiple
            objects specified as a list.
        boundary_name : str, optional
            The name of the boundary object that will be created. If not
            provided, a unique name will be generated. Default is ``None``.
        total_power : str, float, or dict, optional
            The total power transferred to the fluid through the resistance
            volume. It is specified as a string with value and unit, a float
            where the default unit "W" will be used, or a dictionary for
            transient assignment. The dictionary should contain two keys:
            ``"Function"`` and ``"Values"``.

            - For the ``"Function"`` key, options are ``"Exponential"``,
            ``"Linear"``, ``"Piecewise Linear"``, ``"Power Law"``,
            ``"Sinusoidal"``, and ``"Square Wave"``.
            - For the ``"Values"`` key, provide a list of strings containing
            the parameters required by the ``"Function"`` key selection. For
            example, when ``"Linear"`` is set as the ``"Function"`` key, two
            parameters are required: the value of the variable at t=0 and the
            slope of the line. For the parameters required by each
            ``"Function"`` key selection, see the Icepak documentation.

            Default is ``"0W"``.
        fluid : str, optional
            The material of the volume to which the resistance is being
            assigned. Default is ``"air"``.
        laminar : bool, optional
            Whether the flow inside the volume must be treated as laminar or
            not. Default is ``False``.
        power_law_constant : str or float, optional
            Specifies the coefficient in the power law equation for pressure
            loss. Default is ``1``.
        power_law_exponent : str or float, optional
            Specifies the exponent value in the power law equation for pressure
            loss calculation. Default is ``1``.

        Returns
        -------
        :class:`pyaedt.modules.Boundary.BoundaryObject`
            Boundary object when successful or ``None`` when failed.

        References
        ----------

        >>> oModule.AssignResistanceBoundary

        Examples
        --------
        """
        return self.assign_resistance(objects, boundary_name=boundary_name, total_power=total_power, fluid=fluid,
                                      laminar=laminar, loss_type="Power Law",
                                      power_law_constant=power_law_constant, power_law_exponent=power_law_exponent)

    @pyaedt_function_handler()
    def assign_loss_curve_resistance(self, objects, boundary_name=None, total_power="0W", fluid="air", laminar=False,
                                     loss_curves_x = [[0, 1], [0, 1]],
                                     loss_curves_y = [[0, 1], [0, 1]], loss_curves_z = [[0, 1], [0, 1]],
                                     loss_curve_flow_unit="m_per_sec",
                                     loss_curve_pressure_unit="n_per_meter_sq"):
        """
        Assign resistance boundary condition prescribing a loss curve.

        Parameters
        ----------
        objects : list or str
            A list of objects to which the resistance condition will be
            assigned. It can be a single object (a string) or multiple
            objects specified as a list.
        boundary_name : str, optional
            The name of the boundary object that will be created. If not
            provided, a unique name will be generated. Default is ``None``.
        total_power : str, float, or dict, optional
            The total power transferred to the fluid through the resistance
            volume. It is specified as a string with value and unit, a float
            where the default unit "W" will be used, or a dictionary for
            transient assignment. The dictionary should contain two keys:
            ``"Function"`` and ``"Values"``.

            - For the ``"Function"`` key, options are ``"Exponential"``,
            ``"Linear"``, ``"Piecewise Linear"``, ``"Power Law"``,
            ``"Sinusoidal"``, and ``"Square Wave"``.
            - For the ``"Values"`` key, provide a list of strings containing
            the parameters required by the ``"Function"`` key selection. For
            example, when ``"Linear"`` is set as the ``"Function"`` key, two
            parameters are required: the value of the variable at t=0 and the
            slope of the line. For the parameters required by each
            ``"Function"`` key selection, see the Icepak documentation.

            Default is ``"0W"``.
        fluid : str, optional
            The material of the volume to which the resistance is being
            assigned. Default is ``"air"``.
        laminar : bool, optional
            Whether the flow inside the volume must be treated as laminar or
            not. Default is ``False``.
        loss_curves_x : list of lists of float
            List of two list defining the loss curve in the X direction. The
            first list contains the mass flow rate value of the curve while
            the second contains the pressure values. Units can be specified with
            the ``loss_curve_flow_unit`` and ``loss_curve_pressure_unit``
            parameters. Default is ``[[0,1],[0,1]]``.
        loss_curves_y : list of lists of float
            List of two list defining the loss curve in the Y direction. The
            first list contains the mass flow rate value of the curve while
            the second contains the pressure values. Units can be specified with
            the ``loss_curve_flow_unit`` and ``loss_curve_pressure_unit``
            parameters. Default is ``[[0,1],[0,1]]``.
        loss_curves_z : list of lists of float
            List of two list defining the loss curve in the Z direction. The
            first list contains the mass flow rate value of the curve while the
            second contains the pressure values. Units can be specified with the
            ``loss_curve_flow_unit`` and ``loss_curve_pressure_unit``
            parameters. Default is ``[[0,1],[0,1]]``.
        loss_curve_flow_unit : str, optional
            Specifies the unit of flow rate in the loss curvev (for all
            directions). Default is ``"m_per_sec"``.
        loss_curve_pressure_unit : str, optional
            Specifies the unit of pressure drop in the loss curve (for all
            directions). Default is ``"n_per_meter_sq"``.

        Returns
        -------
        :class:`pyaedt.modules.Boundary.BoundaryObject`
            Boundary object when successful or ``None`` when failed.

        References
        ----------

        >>> oModule.AssignResistanceBoundary

        Examples
        --------
        """
        return self.assign_resistance(objects, boundary_name=boundary_name, total_power=total_power, fluid=fluid,
                                      laminar=laminar, loss_type="Loss Curve", loss_curves_x=loss_curves_x,
                                      loss_curves_y=loss_curves_y, loss_curves_z=loss_curves_z,
                                      loss_curve_flow_unit=loss_curve_flow_unit,
                                      loss_curve_pressure_unit=loss_curve_pressure_unit)

    @pyaedt_function_handler()
    def assign_device_resistance(self, objects, boundary_name=None, total_power="0W", fluid="air", laminar=False,
                          linear_loss = ["1m_per_sec", "1m_per_sec", "1m_per_sec"], quadratic_loss = [1, 1, 1],
                          linear_loss_free_area_ratio = [1, 1, 1], quadratic_loss_free_area_ratio = [1, 1, 1]):
        """
        Assign resistance boundary condition using the device/approach model.

        Parameters
        ----------
        objects : list or str
            A list of objects to which the resistance condition will be
            assigned. It can be a single object (a string) or multiple
            objects specified as a list.
        boundary_name : str, optional
            The name of the boundary object that will be created. If not
            provided, a unique name will be generated. Default is ``None``.
        total_power : str, float, or dict, optional
            The total power transferred to the fluid through the resistance
            volume. It is specified as a string with value and unit, a float
            where the default unit "W" will be used, or a dictionary for
            transient assignment. The dictionary should contain two keys:
            ``"Function"`` and ``"Values"``.

            - For the ``"Function"`` key, options are ``"Exponential"``,
            ``"Linear"``, ``"Piecewise Linear"``, ``"Power Law"``,
            ``"Sinusoidal"``, and ``"Square Wave"``.
            - For the ``"Values"`` key, provide a list of strings containing
            the parameters required by the ``"Function"`` key selection. For
            example, when ``"Linear"`` is set as the ``"Function"`` key, two
            parameters are required: the value of the variable at t=0 and the
            slope of the line. For the parameters required by each
            ``"Function"`` key selection, see the Icepak documentation.

            Default is ``"0W"``.
        fluid : str, optional
            The material of the volume to which the resistance is being
            assigned. Default is ``"air"``.
        laminar : bool, optional
            Whether the flow inside the volume must be treated as laminar or
            not. Default is ``False``.
        linear_loss : list of floats or list of strings, optional
            Three values representing the linear loss coefficients in the X, Y,
            and Z directions. These coefficients can be expressed as floats, in
            which case the default unit ``"m_per_sec"`` will be used, or as
            strings. Relevant only if ``loss_type=="Device"``.  Default is
            ``"1m_per_sec"`` for all three directions.
        quadratic_loss : list of floats or list of strings, optional
            Three values representing the quadratic loss coefficients in the X,
            Y, and Z directions. Relevant only if ``loss_type=="Device"``.
            Default is ``1`` for all three directions.
        linear_loss_free_area_ratio : list of floats or list of strings, optional
            Three values representing the linear loss free area ratio in the X,
            Y, and Z directions. Relevant only if ``loss_type=="Device"``.
            Default is ``1`` for all three directions.
        quadratic_loss_free_area_ratio : list of floats or list of strings, optional
            Three values representing the quadratic loss coefficient for each
            direction (X, Y, Z) in the loss model. Relevant only if
            ``loss_type=="Device"``. Default is ``1`` for all three directions.

        Returns
        -------
        :class:`pyaedt.modules.Boundary.BoundaryObject`
            Boundary object when successful or ``None`` when failed.

        References
        ----------

        >>> oModule.AssignResistanceBoundary

        Examples
        --------
        """
        return self.assign_resistance(objects, boundary_name=boundary_name, total_power=total_power, fluid=fluid,
                                      laminar=laminar, loss_type="Device", linear_loss=linear_loss,
                                      quadratic_loss=quadratic_loss,
                                      linear_loss_free_area_ratio = linear_loss_free_area_ratio,
                                      quadratic_loss_free_area_ratio = quadratic_loss_free_area_ratio)

    @pyaedt_function_handler()
    def assign_recirculation_opening(self, face_list, extract_face, thermal_specification="Temperature",
                                     assignment_value="0cel", conductance_external_temperature=None,
                                     flow_specification="Mass Flow", flow_assignment="0kg_per_s_m2",
                                     flow_direction=None, start_time=None, end_time=None, boundary_name=None):
        """Assign recirculation faces.

        Parameters
        ----------
        face_list : list
            List of face primitive objects or a list of integers
            containing faces IDs.
        extract_face : modeler.cad.elements3d.FacePrimitive, int
             ID of the face on the extract side.
        thermal_specification : str, optional
            Type of the thermal assignment across the two recirculation
            faces. The default is ``"Temperature"``. Options are
            ``"Conductance"``, ``"Heat Input"``, and ``"Temperature"``.
        assignment_value : str or dict, optional
            String with value and units of the thermal assignment. For a
            transient assignment, a dictionary can be used. The dictionary
            should contain two keys: ``"Function"`` and ``"Values"``.
            - For the ``"Function"`` key, options are
            ``"Exponential"``, ``"Linear"``, ``"Piecewise Linear"``,
            ``"Power Law"``, ``"Sinusoidal"``, and ``"Square Wave"``.
            - For the ``"Values"`` key, provide a list of strings containing the
            parameters required by the ``"Function"`` key selection. For
            example, when ``"Linear"`` is set as the ``"Function"`` key, two
            parameters are required: the value of the variable at t=0 and the
            slope of the line. For the parameters required by each ``"Function"``
            key selection, see the Icepak documentation.
            The parameters must contain the units where needed.
            The default value is ``"0cel"``.
        conductance_external_temperature : str, optional
            External temperature value, which is needed if
            ``thermal_specification`` is set to ``"Conductance"``.
            The default is ``None``.
        flow_specification : str, optional
            Flow specification for the recirculation zone. The default is
            ``"Mass Flow"``. Options are: ``"Mass Flow"``, ``"Mass Flux"``,
            and ``"Volume Flow"``.
        flow_assignment : str or dict, optional
            String with the value and units of the flow assignment. For a
            transient assignment, a dictionary can be used. The dictionary
            should contain two keys: ``"Function"`` and ``"Values"``.
            - For the ``"Function"`` key, options are
            ``"Exponential"``, ``"Linear"``, ``"Piecewise Linear"``,
            ``"Power Law"``, ``"Sinusoidal"``, and ``"Square Wave"``.
            - For the ``"Values"`` key, provide a list of strings containing the
            parameters required by the ``"Function"`` key selection. For
            example, when``"Linear"`` is set as the ``"Function"`` key, two
            parameters are required: the value of the variable at t=0 and the
            slope of the line. For the parameters required by each
            ``"Function"`` key selection, see the Icepak documentation.
            The parameters must contain the units where needed.
            The default value is ``"0kg_per_s_m2"``.
        flow_direction : list, optional
            Flow direction enforced at the recirculation zone. The default value
            is ``None``, in which case the normal direction is used.
        start_time : str, optional
            Start of the time interval. This parameter is relevant only if the
            simulation is transient. The default value is ``"0s"``.
        end_time : str, optional
            End of the time interval. This parameter is relevant only if the
            simulation is transient. The default value is ``"0s"``.
        boundary_name : str, optional
            Name of the recirculation boundary. The default is ``None``, in
            which case the boundary is automatically generated.

        Returns
        -------
        :class:`pyaedt.modules.Boundary.BoundaryObject`
            Boundary object when successful or ``None`` when failed.

        References
        ----------

        >>> oModule.AssignRecircBoundary

        Examples
        --------
        >>> from pyaedt import Icepak
        >>> ipk = Icepak()
        >>> ipk.solution_type = "Transient"
        >>> box = ipk.modeler.create_box([5, 5, 5], [1, 2, 3], "BlockBoxEmpty", "copper")
        >>> box.solve_inside = False
        >>> recirc = ipk.assign_recirculation_opening([box.top_face_x, box.bottom_face_x], box.top_face_x,
        >>>                                          flow_assignment="10kg_per_s_m2")

        """
        if not len(face_list) == 2:
            self.logger.error("Recirculation boundary condition must be assigned to two faces.")
            return False
        if conductance_external_temperature is not None and thermal_specification != "Conductance":
            self.logger.warning(
                '``conductance_external_temperature`` does not have any effect unless the ``thermal_specification`` '
                'is ``"Conductance"``.')
        if conductance_external_temperature is not None and thermal_specification != "Conductance":
            self.logger.warning(
                '``conductance_external_temperature`` must be specified when ``thermal_specification`` '
                'is ``"Conductance"``. Setting ``conductance_external_temperature`` to ``"AmbientTemp"``.')
        if (start_time is not None or end_time is not None) and not self.solution_type == "Transient":
            self.logger.warning(
                '``start_time`` and ``end_time`` only effect steady-state simulations.')
        elif self.solution_type == "Transient" and not (start_time and end_time):
            self.logger.warning(
                '``start_time`` and ``end_time`` should be declared for transient simulations. Setting them to "0s".')
            start_time = "0s"
            end_time = "0s"
        assignment_dict = {
            "Conductance": "Conductance",
            "Heat Input": "Heat Flow",
            "Temperature": "Temperature Change"
        }
        props = {}
        if not isinstance(face_list[0], int):
            face_list = [f.id for f in face_list]
        props["Faces"] = face_list
        if isinstance(extract_face, int):
            extract_face = [extract_face]
        else:
            extract_face = [extract_face.id]
        props["ExtractFace"] = extract_face
        props["Thermal Condition"] = thermal_specification
        if isinstance(assignment_value, dict):
            if not self.solution_type == "Transient":
                self.logger.error("Transient assignment is supported only in transient designs.")
                return None
            assignment = self._parse_variation_data(
                assignment_dict[thermal_specification],
                "Transient",
                variation_value=assignment_value["Values"],
                function=assignment_value["Function"],
            )
            props.update(assignment)
        else:
            props[assignment_dict[thermal_specification]] = assignment_value
        if thermal_specification == "Conductance":
            props["External Temp"] = conductance_external_temperature
        if isinstance(flow_assignment, dict):
            if not self.solution_type == "Transient":
                self.logger.error("Transient assignment is supported only in transient designs.")
                return None
            assignment = self._parse_variation_data(
                flow_specification + " Rate",
                "Transient",
                variation_value=flow_assignment["Values"],
                function=flow_assignment["Function"],
            )
            props.update(assignment)
        else:
            props[flow_specification + " Rate"] = flow_assignment
        if flow_direction is None:
            props["Supply Flow Direction"] = "Normal"
        else:
            props["Supply Flow Direction"] = "Specified"
            if not (isinstance(flow_direction, list)):
                self.logger.error("``flow_direction`` can be only ``None`` or a list of strings or floats.")
                return False
            elif len(flow_direction) != 3:
                self.logger.error("``flow_direction`` must have only three components.")
                return False
            for direction, val in zip(["X", "Y", "Z"], flow_direction):
                props[direction] = str(val)
        if self.solution_type == "Transient":
            props["Start"] = start_time
            props["End"] = end_time
        if not boundary_name:
            boundary_name = generate_unique_name("Recirculating")

        bound = BoundaryObject(self, boundary_name, props, "Recirculating")
        return _create_boundary(bound)

    @pyaedt_function_handler()
    def assign_blower_type1(self, faces, inlet_face, fan_curve_pressure, fan_curve_flow, blower_power="0W", blade_rpm=0,
                            blade_angle="0rad", fan_curve_pressure_unit="n_per_meter_sq",
                            fan_curve_flow_unit="m3_per_s", boundary_name=None):
        """Assign blower type 1.

        Parameters
        ----------
        faces : list
            List of modeler.cad.elements3d.FacePrimitive or of integers
            containing faces ids.
        inlet_face : modeler.cad.elements3d.FacePrimitive, int or list
             Inlet faces.
        fan_curve_pressure : list
            List of the fan curve pressure values. Only floats should
            be included in the list as their unit can be modified with
            fan_curve_pressure_unit argument.
        fan_curve_flow : list
            List of the fan curve flow value. Only floats should be
            included in the list as their unit can be modified with
            fan_curve_flow_unit argument.
        blower_power : str, optional
            blower power expressed as a string containing the value and unit.
            Default is "0W".
        blade_rpm : float, optional
            Blade RPM value. Default is 0.
        blade_angle : str, optional
            Blade angle expressed as a string containing value and the unit.
            Default is "0rad".
        fan_curve_pressure_unit : str, optional
            Fan curve pressure unit. Default is "n_per_meter_sq".
        fan_curve_flow_unit : str, optional
            Fan curve flow unit. Default is "m3_per_s".
        boundary_name : str, optional
            Name of the recirculation boundary. The default is ``None``, in
            which case the boundary is automatically generated.


        Returns
        -------
        :class:`pyaedt.modules.Boundary.BoundaryObject`
            Boundary object when successful or ``None`` when failed.

        References
        ----------

        >>> oModule.AssignBlowerBoundary

        Examples
        --------
        >>> from pyaedt import Icepak
        >>> ipk = Icepak()
        >>> cylinder = self.aedtapp.modeler.create_cylinder(cs_axis="X", position=[0,0,0], radius=10, height=1)
        >>> curved_face = [f for f in cylinder.faces if not f.is_planar]
        >>> planar_faces = [f for f in cylinder.faces if f.is_planar]
        >>> cylinder.solve_inside=False
        >>> blower = self.aedtapp.assign_blower_type1([f.id for f in curved_face+planar_faces],
        >>>                                           [f.id for f in planar_faces], [10, 5, 0], [0, 2, 4])

        """
        props = {}
        props["Blade RPM"] = blade_rpm
        props["Fan Blade Angle"] = blade_angle
        props["Blower Type"] = "Type 1"
        return self._assign_blower(props, faces, inlet_face, fan_curve_flow_unit, fan_curve_pressure_unit,
                                   fan_curve_flow, fan_curve_pressure, blower_power, boundary_name)

    @pyaedt_function_handler()
    def assign_blower_type2(self, faces, inlet_face, fan_curve_pressure, fan_curve_flow, blower_power="0W",
                            exhaust_angle="0rad", fan_curve_pressure_unit="n_per_meter_sq",
                            fan_curve_flow_unit="m3_per_s", boundary_name=None):
        """Assign blower type 2.

        Parameters
        ----------
        faces : list
            List of modeler.cad.elements3d.FacePrimitive or of integers
            containing faces ids.
        inlet_face : modeler.cad.elements3d.FacePrimitive, int or list
             Inlet faces.
        fan_curve_pressure : list
            List of the fan curve pressure values. Only floats should
            be included in the list as their unit can be modified with
            fan_curve_pressure_unit argument.
        fan_curve_flow : list
            List of the fan curve flow value. Only floats should be
            included in the list as their unit can be modified with
            fan_curve_flow_unit argument.
        blower_power : str, optional
            blower power expressed as a string containing the value and unit.
            Default is "0W".
        exhaust_angle : float, optional
            Exhaust angle expressed as a string containing value and the unit.
            Default is "0rad".
        fan_curve_pressure_unit : str, optional
            Fan curve pressure unit. Default is "n_per_meter_sq".
        fan_curve_flow_unit : str, optional
            Fan curve flow unit. Default is "m3_per_s".
        boundary_name : str, optional
            Name of the recirculation boundary. The default is ``None``, in
            which case the boundary is automatically generated.


        Returns
        -------
        :class:`pyaedt.modules.Boundary.BoundaryObject`
            Boundary object when successful or ``None`` when failed.

        References
        ----------

        >>> oModule.AssignBlowerBoundary

        Examples
        --------
        >>> from pyaedt import Icepak
        >>> ipk = Icepak()
        >>> box = ipk.modeler.create_box([5, 5, 5], [1, 2, 3], "BlockBoxEmpty", "copper")
        >>> box.solve_inside=False
        >>> blower = self.aedtapp.assign_blower_type2([box.faces[0], box.faces[1]],
        >>>                                           [box.faces[0]], [10, 5, 0], [0, 2, 4])

        """
        props = {}
        props["Exhaust Exit Angle"] = exhaust_angle
        props["Blower Type"] = "Type 2"
        return self._assign_blower(props, faces, inlet_face, fan_curve_flow_unit, fan_curve_pressure_unit,
                                   fan_curve_flow, fan_curve_pressure, blower_power, boundary_name)

    @pyaedt_function_handler()
    def _assign_blower(self, props, faces, inlet_face, fan_curve_flow_unit, fan_curve_pressure_unit, fan_curve_flow,
                       fan_curve_pressure, blower_power, boundary_name):
        if isinstance(faces[0], int):
            props["Faces"] = faces
        else:
            props["Faces"] = [f.id for f in faces]
        if not isinstance(inlet_face, list):
            inlet_face = [inlet_face]
        if not isinstance(inlet_face[0], int):
            props["InletFace"] = [f.id for f in inlet_face]
        props["Blower Power"] = blower_power
        props["DimUnits"] = [fan_curve_flow_unit, fan_curve_pressure_unit]
        if len(fan_curve_flow) != len(fan_curve_pressure):
            self.logger.error("``fan_curve_flow`` and ``fan_curve_pressure`` must have the same length.")
            return False
        props["X"] = [str(pt) for pt in fan_curve_flow]
        props["Y"] = [str(pt) for pt in fan_curve_pressure]
        if not boundary_name:
            boundary_name = generate_unique_name("Blower")
        bound = BoundaryObject(self, boundary_name, props, "Blower")
        return _create_boundary(bound)

    @pyaedt_function_handler()
    def assign_conducting_plate(self, obj_plate, boundary_name=None, total_power="0W",
                                thermal_specification="Thickness", thickness="1mm", solid_material="Al-Extruded",
                                conductance="0W_per_Cel", shell_conduction=False, thermal_resistance="0Kel_per_W",
                                low_side_rad_material=None, high_side_rad_material=None,
                                thermal_impedance="0celm2_per_W"):
        """
        Assign thermal boundary conditions to a conducting plate.

        Parameters
        ----------
        obj_plate : str or int or list
            Object to assign the boundary to. If a string, specify a surface name.
            If an integer, specify a face ID.
        boundary_name : str, optional
            Boundary name. The default is ``None``, in which case a name is generated
            automatically.
        total_power : str or float or dict, optional
            Power dissipated by the plate. The default is ``"0W"``. If a float,
            the default unit is ``"W"``. A transient or temperature-dependent power
            can be assigned with a dictionary.
        thermal_specification : str, optional
            Type of condition to apply. The default is `"Thickness"``.
            Options are ``"Conductance"``, ``"Thermal Impedance"``,
            ``"Thermal Resistance"``, and ``"Thickness"``.
        thickness : str or float, optional
            If ``thermal_specification="Thickness"``, this parameter represents the
            thickness to model with the plate. The default is ``"1mm"``. If a float,
            the default unit is ``"mm"``.
        solid_material : str, optional
           If ``thermal_specification="Thickness"``, this parameter represents the
           material of the conducting plate. The default is ``"Al-Extruded"``.
        conductance : str or float, optional
             If ``thermal_specification="Conductance"``, this parameter represents the
             conductance of the plate. The default is ``"0W_per_Cel"``. If a float, the default
             unit is ``"W_per_Cel"``.
        thermal_resistance : str or float, optional
            If ``thermal_specification="Thermal Resistance"``, this parameter represents the
            thermal resistance of the plate. The default is ``"0Kel_per_W"``. If a float, the
            default unit is ``"Kel_per_W"``.
        thermal_impedance : str or float, optional
            If ``thermal_specification="Thermal Impedance"``, this parameter represents the
            thermal impedance of the plate. The default is ``"0Cel_m2_per_W"``. If a float, the
            default unit is "``Cel_m2_per_W"``.
        shell_conduction : bool, optional
            Whether to consider shell conduction. The default is ``False``.
        low_side_rad_material : str, optional
            Material on the low side for radiation. The default is ``None``, in which
            case radiation is disabled on the low side.
        high_side_rad_material : str, optional
            Material on the high side for radiation. The default is ``None``, in which
            case radiation is disabled on the high side.

        Returns
        -------
        :class:`pyaedt.modules.Boundary.BoundaryObject`
            Boundary object when successful or ``None`` when failed.

        """
        props = {}
        if not isinstance(obj_plate, list):
            obj_plate = [obj_plate]
        if all(isinstance(obj, int) for obj in obj_plate):
            props["Faces"] = obj_plate
        elif all(isinstance(obj, str) for obj in obj_plate):
            props["Objects"] = obj_plate
        else:
            raise AttributeError("Invalid ``obj_plate`` argument.")

        if isinstance(total_power, dict):
            assignment = self._parse_variation_data(
                "Total Power",
                total_power["Type"],
                variation_value=total_power["Values"],
                function=total_power["Function"],
            )
            props.update(assignment)
        else:
            props["Total Power"] = total_power
        props["Thermal Specification"] = thermal_specification
        for value, key, unit in zip(
                [thickness, conductance, thermal_resistance, thermal_impedance],
                ["Thickness", "Conductance", "Thermal Resistance", "Thermal Impedance"],
                ["mm", "W_per_Cel", "Kel_per_W", "Cel_m2_per_W"]
        ):
            if thermal_specification == key:
                if not isinstance(value, str):
                    value = str(value) + unit
                props[key] = value
        if thermal_specification == "Thickness":
            props["Solid Material"] = solid_material
        if low_side_rad_material is not None:
            props["LowSide"] = {"Radiate": False}
        else:
            props["LowSide"] = {"Radiate": True,
                                "RadiateTo": "AllObjects",
                                "Surface Material": low_side_rad_material}
        if high_side_rad_material is not None:
            props["LowSide"] = {"Radiate": False}
        else:
            props["HighSide"] = {"Radiate": True,
                                 "RadiateTo - High": "AllObjects - High",
                                 "Surface Material - High": high_side_rad_material}
        props["Shell Conduction"] = shell_conduction
        if not boundary_name:
            boundary_name = generate_unique_name("Plate")
        bound = BoundaryObject(self, boundary_name, props, "Conducting Plate")
        return _create_boundary(bound)

    def assign_conducting_plate_with_thickness(self, obj_plate, boundary_name=None, total_power="0W",
                                               thickness="1mm", solid_material="Al-Extruded",
                                               shell_conduction=False, low_side_rad_material=None,
                                               high_side_rad_material=None):
        """
        Assign thermal boundary conditions with thickness specification to a conducting plate.

        Parameters
        ----------
        obj_plate : str or int or list
            Object to assign the boundary to. If a string, specify a surface name.
            If an integer, specify a face ID.
        boundary_name : str, optional
            Boundary name. The default is ``None``, in which case a name is generated
            automatically.
        total_power : str or float or dict, optional
            Power dissipated by the plate. The default is ``"0W"``. If a float,
            the default unit is ``"W"``. A transient or temperature-dependent power
            can be assigned with a dictionary.
        thickness : str or float, optional
            If ``thermal_specification="Thickness"``, this parameter represents the
            thickness to model with the plate. The default is ``"1mm"``. If a float,
            the default unit is ``"mm"``.
        solid_material : str, optional
           If ``thermal_specification="Thickness"``, this parameter represents the
           material of the conducting plate. The default is ``"Al-Extruded"``.
        shell_conduction : bool, optional
            Whether to consider shell conduction. The default is ``False``.
        low_side_rad_material : str, optional
            Material on the low side for radiation. The default is ``None``, in which
            case radiation is disabled on the low side.
        high_side_rad_material : str, optional
            Material on the high side for radiation. The default is ``None``, in which
            case radiation is disabled on the high side.

        Returns
        -------
        :class:`pyaedt.modules.Boundary.BoundaryObject`
            Boundary object when successful or ``None`` when failed.

        """
        return self.assign_conducting_plate(obj_plate,
                                            boundary_name=boundary_name,
                                            total_power=total_power,
                                            thermal_specification="Thickness",
                                            thickness=thickness,
                                            solid_material=solid_material,
                                            shell_conduction=shell_conduction,
                                            low_side_rad_material=low_side_rad_material,
                                            high_side_rad_material=high_side_rad_material)

    def assign_conducting_plate_with_resistance(self, obj_plate, boundary_name=None, total_power="0W",
                                                thermal_resistance="0Kel_per_W",
                                                shell_conduction=False, low_side_rad_material=None,
                                                high_side_rad_material=None):
        """
        Assign thermal boundary conditions with thermal resistance specification to a conducting plate.

        Parameters
        ----------
        obj_plate : str or int or list
            Object to assign the boundary to. If a string, specify a surface name.
            If an integer, specify a face ID.
        boundary_name : str, optional
            Boundary name. The default is ``None``, in which case a name is generated
            automatically.
        total_power : str or float or dict, optional
            Power dissipated by the plate. The default is ``"0W"``. If a float,
            the default unit is ``"W"``. A transient or temperature-dependent power
            can be assigned with a dictionary.
        thermal_resistance : str or float, optional
            If ``thermal_specification="Thermal Resistance"``, this parameter represents the
            thermal resistance of the plate. The default is ``"0Kel_per_W"``. If a float, the
            default unit is ``"Kel_per_W"``.
        shell_conduction : bool, optional
            Whether to consider shell conduction. The default is ``False``.
        low_side_rad_material : str, optional
            Material on the low side for radiation. The default is ``None``, in which
            case radiation is disabled on the low side.
        high_side_rad_material : str, optional
            Material on the high side for radiation. The default is ``None``, in which
            case radiation is disabled on the high side.

        Returns
        -------
        :class:`pyaedt.modules.Boundary.BoundaryObject`
            Boundary object when successful or ``None`` when failed.

        """
        return self.assign_conducting_plate(obj_plate,
                                            boundary_name=boundary_name,
                                            total_power=total_power,
                                            thermal_specification="Thermal Resistance",
                                            thermal_resistance=thermal_resistance,
                                            shell_conduction=shell_conduction,
                                            low_side_rad_material=low_side_rad_material,
                                            high_side_rad_material=high_side_rad_material)

    def assign_conducting_plate_with_impedance(self, obj_plate, boundary_name=None, total_power="0W",
                                               thermal_impedance="0celm2_per_W",
                                               shell_conduction=False, low_side_rad_material=None,
                                               high_side_rad_material=None):
        """
        Assign thermal boundary conditions with thermal impedance specification to a conducting plate.

        Parameters
        ----------
        obj_plate : str or int or list
            Object to assign the boundary to. If a string, specify a surface name.
            If an integer, specify a face ID.
        boundary_name : str, optional
            Boundary name. The default is ``None``, in which case a name is generated
            automatically.
        total_power : str or float or dict, optional
            Power dissipated by the plate. The default is ``"0W"``. If a float,
            the default unit is ``"W"``. A transient or temperature-dependent power
            can be assigned with a dictionary.
        thermal_impedance : str or float, optional
            If ``thermal_specification="Thermal Impedance"``, this parameter represents the
            thermal impedance of the plate. The default is ``"0Cel_m2_per_W"``. If a float, the
            default unit is "``Cel_m2_per_W"``.
        shell_conduction : bool, optional
            Whether to consider shell conduction. The default is ``False``.
        low_side_rad_material : str, optional
            Material on the low side for radiation. The default is ``None``, in which
            case radiation is disabled on the low side.
        high_side_rad_material : str, optional
            Material on the high side for radiation. The default is ``None``, in which
            case radiation is disabled on the high side.

        Returns
        -------
        :class:`pyaedt.modules.Boundary.BoundaryObject`
            Boundary object when successful or ``None`` when failed.

        """
        return self.assign_conducting_plate(obj_plate,
                                            boundary_name=boundary_name,
                                            total_power=total_power,
                                            thermal_specification="Thermal Impedance",
                                            thermal_impedance=thermal_impedance,
                                            shell_conduction=shell_conduction,
                                            low_side_rad_material=low_side_rad_material,
                                            high_side_rad_material=high_side_rad_material)

    def assign_conducting_plate_with_conductance(self, obj_plate, boundary_name=None, total_power="0W",
                                                 conductance="0W_per_Cel",
                                                 shell_conduction=False, low_side_rad_material=None,
                                                 high_side_rad_material=None):
        """
        Assign thermal boundary conditions with conductance specification to a conducting plate.

        Parameters
        ----------
        obj_plate : str or int or list
            Object to assign the boundary to. If a string, specify a surface name.
            If an integer, specify a face ID.
        boundary_name : str, optional
            Boundary name. The default is ``None``, in which case a name is generated
            automatically.
        total_power : str or float or dict, optional
            Power dissipated by the plate. The default is ``"0W"``. If a float,
            the default unit is ``"W"``. A transient or temperature-dependent power
            can be assigned with a dictionary.
        conductance : str or float, optional
             If ``thermal_specification="Conductance"``, this parameter represents the
             conductance of the plate. The default is ``"0W_per_Cel"``. If a float, the default
             unit is ``"W_per_Cel"``.
        shell_conduction : bool, optional
            Whether to consider shell conduction. The default is ``False``.
        low_side_rad_material : str, optional
            Material on the low side for radiation. The default is ``None``, in which
            case radiation is disabled on the low side.
        high_side_rad_material : str, optional
            Material on the high side for radiation. The default is ``None``, in which
            case radiation is disabled on the high side.

        Returns
        -------
        :class:`pyaedt.modules.Boundary.BoundaryObject`
            Boundary object when successful or ``None`` when failed.

        """
        return self.assign_conducting_plate(obj_plate,
                                            boundary_name=boundary_name,
                                            total_power=total_power,
                                            thermal_specification="Conductance",
                                            conductance=conductance,
                                            shell_conduction=shell_conduction,
                                            low_side_rad_material=low_side_rad_material,
                                            high_side_rad_material=high_side_rad_material)
