# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 - 2026 Synopsys, Inc. and ANSYS, Inc. All rights reserved.
# SPDX-License-Identifier: MIT
#
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

"""The module contains the ``Mechanical`` class."""

import copy

from ansys.aedt.core.application.analysis_3d import FieldAnalysis3D
from ansys.aedt.core.base import PyAedtBase
from ansys.aedt.core.generic.constants import SolutionsMechanical
from ansys.aedt.core.generic.file_utils import generate_unique_name
from ansys.aedt.core.generic.general_methods import _merge_props
from ansys.aedt.core.generic.general_methods import pyaedt_function_handler
from ansys.aedt.core.internal.errors import AEDTRuntimeError
from ansys.aedt.core.mixins import CreateBoundaryMixin
from ansys.aedt.core.modules.boundary.common import BoundaryObject
from ansys.aedt.core.modules.setup_templates import SetupKeys
from ansys.aedt.core.modules.solve_setup import SetupIcepakFEA


class Mechanical(FieldAnalysis3D, CreateBoundaryMixin, PyAedtBase):
    """Provides the Mechanical application interface.

    Parameters
    ----------
    project : str, optional
        Name of the project to select or the full path to the project
        or AEDTZ archive to open.  The default is ``None``, in which
        case an attempt is made to get an active project. If no
        projects are present, an empty project is created.
    design : str, optional
        Name of the design to select. The default is ``None``, in
        which case an attempt is made to get an active design. If no
        designs are present, an empty design is created.
    solution_type : str, optional
        Solution type to apply to the design. The default is
        ``None``, in which case the default type is applied.
    setup : str, optional
        Name of the setup to use as the nominal. The default is
        ``None``, in which case the active setup is used or
        nothing is used.
    version : str, int, float, optional
        Version of AEDT to use. The default is ``None``, in which case
        the active version or latest installed version is used.
        This parameter is ignored when a script is launched within AEDT.
        Examples of input values are ``261``, ``26.1``, ``2026.1``, ``"2026.1"``.
    non_graphical : bool, optional
        Whether to launch AEDT in the non-graphical mode. The default
        is ``False``, in which case AEDT is launched in the graphical mode.
        This parameter is ignored when a script is launched within AEDT.
    new_desktop : bool, optional
        Whether to launch an instance of AEDT in a new thread, even if
        another instance of the ``version`` is active on the
        machine. The default is ``False``. This parameter is ignored when
        a script is launched within AEDT.
    close_on_exit : bool, optional
        Whether to release AEDT on exit. The default is ``False``.
    student_version : bool, optional
        Whether to open the AEDT student version. The default is ``False``.
        This parameter is ignored when a script is launched within AEDT.
    machine : str, optional
        Machine name to connect the oDesktop session to. Works only in 2022R2 and
        later. The remote server must be up and running with the command
        `"ansysedt.exe -grpcsrv portnum"`. If the machine is `"localhost"`,
        the server also starts if not present.
    port : int, optional
        Port number on which to start the oDesktop communication on an already existing server.
        This parameter is ignored when creating a new server. It works only in 2022 R2 or
        later. The remote server must be up and running with the command `"ansysedt.exe -grpcsrv portnum"`.
    aedt_process_id : int, optional
        Process ID for the instance of AEDT to point PyAEDT at. The default is
        ``None``. This parameter is only used when ``new_desktop = False``.
    remove_lock : bool, optional
        Whether to remove lock to project before opening it or not.
        The default is ``False``, which means to not unlock
        the existing project if needed and raise an exception.

    Examples
    --------
    Create an instance of Mechanical and connect to an existing
    Mechanical design or create a new Mechanical design if one does not exist.

    >>> from ansys.aedt.core import Mechanical
    >>> mech = Mechanical()

    Create an instance of Mechanical and link to a project named
    ``"projectname"``. If this project does not exist, create one with
    this name.

    >>> mech = Mechanical(project="projectname")

    Create an instance of Mechanical and link to a design named
    ``"designname"`` in a project named ``"projectname"``.

    >>> mech = Mechanical(project="projectname", design="designname")

    Create an instance of Mechanical and open the specified
    project, which is named ``"myfile.aedt"``.

    >>> mech = Mechanical(project="C:/Temp/myfile.aedt")

    Launch AEDT 2026 R1, open the ``"myfile.aedt"`` project, and create a
    structural design.

    >>> from ansys.aedt.core.generic.constants import SolutionsMechanical
    >>> mech = Mechanical(version="2026.1", project="C:/Temp/myfile.aedt", solution_type=SolutionsMechanical.Structural)

    """

    def __init__(
        self,
        project: str | None = None,
        design: str | None = None,
        solution_type: str | None = None,
        setup: str | None = None,
        version: str | None = None,
        non_graphical: bool | None = False,
        new_desktop: bool | None = False,
        close_on_exit: bool | None = False,
        student_version: bool | None = False,
        machine: str | None = "",
        port: int | None = 0,
        aedt_process_id: int | None = None,
        remove_lock: bool | None = False,
    ) -> None:
        FieldAnalysis3D.__init__(
            self,
            "ICEPAKFEA",
            project,
            design,
            solution_type,
            setup,
            version,
            non_graphical,
            new_desktop,
            close_on_exit,
            student_version,
            machine,
            port,
            aedt_process_id,
            remove_lock=remove_lock,
        )

    def _init_from_design(self, *args, **kwargs) -> None:
        self.__init__(*args, **kwargs)

    @pyaedt_function_handler()
    def assign_em_losses(
        self,
        design: str | None = "HFSSDesign1",
        setup: str | None = "Setup1",
        sweep: str | None = "LastAdaptive",
        map_frequency: str | None = None,
        surface_objects: list | None = None,
        source_project_name: str | None = None,
        parameters: list | None = None,
        assignment: list | None = None,
    ) -> BoundaryObject:
        """Map EM losses to a Mechanical design.

        Parameters
        ----------
        design : str, optional
            Name of the design of the source mapping. The default is ``"HFSSDesign1"``.
        setup : str, optional
            Name of the EM setup. The default is ``"Setup1"``.
        sweep : str, optional
            Name of the EM sweep to use for the mapping. The default is ``"LastAdaptive"``.
        map_frequency : str, optional
            Frequency to map. The default is ``None``. The value must be ``None`` for
            Eigenmode analysis.
        surface_objects : list, optional
            List objects in the source that are metals. The default is ``None``.
        source_project_name : str, optional
            Name of the source project. The default is ``None``, in which case
            the source from the same project is used.
        parameters : list, optional
            List of all parameters in the EM to map. The default is ``None``.
        assignment : list, optional
             The default is ``None``.

        Returns
        -------
        :class:`ansys.aedt.core.modules.boundary.common.BoundaryObject`

        References
        ----------
        >>> oModule.AssignEMLoss

        Examples
        --------
        Map the losses of an HFSS coaxial conductor computed at 1 GHz onto the same cylinder
        in a Mechanical thermal design of the same project.

        >>> from ansys.aedt.core import Hfss, Mechanical
        >>> from ansys.aedt.core.generic.constants import Plane
        >>> hfss = Hfss(project="coax_project", design="HFSSDesign1")
        >>> hfss_cyl = hfss.modeler.create_cylinder(Plane.XY, [0, 0, 0], 3, 30, 0, "MyCylinder", "brass")
        >>> hfss_setup = hfss.create_setup("Setup1")
        >>> hfss_setup.props["Frequency"] = "1GHz"

        Start Mechanical and copy bodies from the HFSS project.

        >>> mech = Mechanical(project="coax_project", design="MechanicalDesign1", solution_type="Thermal")
        >>> mech.copy_solid_bodies_from(design=hfss)
        >>> em_loss = mech.assign_em_losses(
        ...     design=hfss.design_name,
        ...     setup=hfss.setups[0].name,
        ...     sweep="LastAdaptive",
        ...     map_frequency=hfss.setups[0].props["Frequency"],
        ...     assignment=hfss.get_all_conductors_names(),
        ... )

        """
        if self.solution_type not in (
            SolutionsMechanical.Thermal,
            SolutionsMechanical.SteadyStateThermal,
            SolutionsMechanical.TransientThermal,
        ):
            raise AEDTRuntimeError("This method works only in a Mechanical Thermal analysis.")

        if surface_objects is None:
            surface_objects = []
        if parameters is None:
            parameters = []
        if assignment is None:
            assignment = []

        self.logger.info("Mapping HFSS EM Loss")
        oName = self.project_name
        if oName == source_project_name or source_project_name is None:
            projname = "This Project*"
        else:
            projname = source_project_name + ".aedt"
        #
        # Generate a list of model objects from the lists made previously and use to map the HFSS losses into Icepak.
        #
        if not assignment:
            allObjects = self.modeler.object_names
        else:
            allObjects = surface_objects + assignment[:]
        surfaces = surface_objects
        if map_frequency:
            intr = [map_frequency]
        else:
            intr = []

        argparam = {}

        variations = self.available_variations.nominal_variation(dependent_params=False)

        for key, value in variations.items():
            argparam[key] = value

        for el in parameters:
            argparam[el] = el

        props = {
            "Objects": allObjects,
            "allObjects": False,
            "Project": projname,
            "projname": "ElectronicsDesktop",
            "Design": design,
            "Soln": setup + " : " + sweep,
            "Params": argparam,
            "ForceSourceToSolve": True,
            "PreservePartnerSoln": True,
            "PathRelativeTo": "TargetProject",
        }
        if intr:
            props["Intrinsics"] = intr
            props["SurfaceOnly"] = surfaces

        name = generate_unique_name("EMLoss")
        return self._create_boundary(name, props, "EMLoss")

    @pyaedt_function_handler()
    def assign_thermal_map(
        self,
        assignment: list,
        design: str | None = "IcepakDesign1",
        setup: str | None = "Setup1",
        sweep: str | None = "SteadyState",
        source_project_name: str | None = None,
        parameters: list | None = None,
    ) -> BoundaryObject:
        """Map thermal losses to a Mechanical design.

        .. note::
           This method works in 2021 R2 only when coupled with Icepak.

        Parameters
        ----------
        assignment : list

        design : str, optional
            Name of the design with the source mapping. The default is ``"IcepakDesign1"``.
        setup : str, optional
            Name of the EM setup. The default is ``"Setup1"``.
        sweep : str, optional
            Name of the EM sweep to use for the mapping. The default is ``"SteadyState"``.
        source_project_name : str, optional
            Name of the source project. The default is ``None``, in which case the
            source from the same project is used.
        parameters : list, optional
            List of all parameters in the EM to map. The default is ``None``.

        Returns
        -------
        :class:`aedt.modules.boundary.Boundary object`
            Boundary object.

        References
        ----------
        >>> oModule.AssignThermalCondition

        Examples
        --------
        Map the temperatures of an Icepak steady-state solution onto the same cylinder
        in a Mechanical structural design of the same project.

        >>> from ansys.aedt.core import Icepak, Mechanical
        >>> from ansys.aedt.core.generic.constants import Plane
        >>> ipk = Icepak(project="thermal_project", design="IcepakDesign1", solution_type="SteadyState")
        >>> ipk_cyl = ipk.modeler.create_cylinder(Plane.XY, [0, 0, 0], 3, 30, 0, "MyCylinder", "brass")
        >>> ipk_setup = ipk.create_setup("Setup1")
        >>> mech = Mechanical(project="thermal_project", design="MechanicalDesign1", solution_type="Structural")
        >>> mech_setup = mech.create_setup()
        >>> mech_cyl = mech.modeler.create_cylinder(Plane.XY, [0, 0, 0], 3, 30, 0, "MyCylinder", "brass")
        >>> thermal_map = mech.assign_thermal_map(["MyCylinder"], design="IcepakDesign1", setup="Setup1")

        """
        if self.solution_type != SolutionsMechanical.Structural:
            raise AEDTRuntimeError("This method works only in a Mechanical Structural analysis.")

        if parameters is None:
            parameters = []

        self.logger.info("Mapping HFSS EM Loss")
        oName = self.project_name
        if oName == source_project_name or source_project_name is None:
            projname = "This Project*"
        else:
            projname = source_project_name + ".aedt"
        #
        # Generate a list of model objects from the lists made previously and use to map the HFSS losses into Icepak.
        #
        assignment = self.modeler.convert_to_selections(assignment, True)
        if not assignment:
            all_objects = self.modeler.object_names
        else:
            all_objects = assignment[:]
        argparam = {}

        variations = self.available_variations.nominal_variation(dependent_params=False)
        for key, value in variations.items():
            argparam[key] = value

        for el in parameters:
            argparam[el] = el

        props = {
            "Objects": all_objects,
            "Uniform": False,
            "Project": projname,
            "Product": "ElectronicsDesktop",
            "Design": design,
            "Soln": setup + " : " + sweep,
            "Params": argparam,
            "ForceSourceToSolve": True,
            "PreservePartnerSoln": True,
            "PathRelativeTo": "TargetProject",
        }

        name = generate_unique_name("ThermalLink")
        return self._create_boundary(name, props, "ThermalCondition")

    @pyaedt_function_handler()
    def assign_uniform_convection(
        self,
        assignment: list,
        convection_value: float | None = 1.0,
        convection_unit: str | None = "w_per_m2kel",
        temperature: str | None = "AmbientTemp",
        name: str | None = "",
    ) -> BoundaryObject:
        """Assign a uniform convection to the face list.

        Parameters
        ----------
        assignment : list
            List of objects, faces, or both.
        convection_value : float, optional
            Convection value. The default is ``"1.0"``.
        convection_unit : str, optional
            Units for the convection value. The default is ``"w_per_m2kel"``.
        temperature : str, optional
            Temperature. The default is ``"AmbientTemp"``.
        name : str, optional
            Name of the boundary. The default is ``""``, in which case the default
            name is used.

        Returns
        -------
        :class:`aedt.modules.boundary.Boundary object`
            Boundary object.

        References
        ----------
        >>> oModule.AssignConvection

        Examples
        --------
        Assign a convection of 3 W/(m^2 K) to the lateral face of a cylinder in a thermal design.

        >>> from ansys.aedt.core import Mechanical
        >>> mech = Mechanical(solution_type="Thermal")
        >>> cylinder = mech.modeler.create_cylinder(orientation="Z", origin=[0, 0, 0], radius=0.8, height=20)
        >>> convection = mech.assign_uniform_convection(
        ...     cylinder.faces[0].id, convection_value=3, temperature="AmbientTemp", name="Convection1"
        ... )

        """
        if self.solution_type not in (
            SolutionsMechanical.Thermal,
            SolutionsMechanical.SteadyStateThermal,
            SolutionsMechanical.TransientThermal,
        ):
            raise AEDTRuntimeError("This method works only in a Mechanical Thermal analysis.")

        props = {}
        assignment = self.modeler.convert_to_selections(assignment, True)

        if isinstance(assignment, list):
            if isinstance(assignment[0], str):
                props["Objects"] = assignment
            else:
                props["Faces"] = assignment

        props["Temperature"] = temperature
        props["Uniform"] = True
        props["FilmCoeff"] = str(convection_value) + convection_unit

        if not name:
            name = generate_unique_name("Convection")
        return self._create_boundary(name, props, "Convection")

    @pyaedt_function_handler()
    def assign_uniform_temperature(
        self, assignment: list, temperature: str | None = "AmbientTemp", name: str | None = ""
    ) -> BoundaryObject:
        """Assign a uniform temperature boundary.

        .. note::
            This method works only in a Mechanical Thermal analysis.

        Parameters
        ----------
        assignment : list
            List of objects, faces, or both.
        temperature : str, optional.
            Type of the temperature. The default is ``"AmbientTemp"``.
        name : str, optional
            Name of the boundary. The default is ``""``.

        Returns
        -------
        :class:`aedt.modules.boundary.Boundary object`
            Boundary object.

        References
        ----------
        >>> oModule.AssignTemperature

        Examples
        --------
        Fix the temperature of the top face of a cylinder in a thermal design.

        >>> from ansys.aedt.core import Mechanical
        >>> mech = Mechanical(solution_type="Thermal")
        >>> cylinder = mech.modeler.create_cylinder(orientation="Z", origin=[0, 0, 0], radius=0.8, height=20)
        >>> temperature = mech.assign_uniform_temperature(cylinder.top_face_z.id, temperature="35cel")
        >>> temperature.props["Temperature"]
        '35cel'

        """
        if self.solution_type not in (
            SolutionsMechanical.Thermal,
            SolutionsMechanical.SteadyStateThermal,
            SolutionsMechanical.TransientThermal,
        ):
            raise AEDTRuntimeError("This method works only in a Mechanical Thermal analysis.")

        props = {}
        assignment = self.modeler.convert_to_selections(assignment, True)

        if isinstance(assignment, list):
            if isinstance(assignment[0], str):
                props["Objects"] = assignment
            else:
                props["Faces"] = assignment

        props["Temperature"] = temperature

        if not name:
            name = generate_unique_name("Temp")
        return self._create_boundary(name, props, "Temperature")

    @pyaedt_function_handler()
    def assign_frictionless_support(self, assignment: list, name: str | None = "") -> BoundaryObject:
        """Assign a Mechanical frictionless support.

        .. note::
            This method works only in a Mechanical Structural analysis.

        Parameters
        ----------
        assignment : list
            List of faces to apply to the frictionless support.
        name : str, optional
            Name of the boundary. The default is ``""``, in which case the
            default name is used.

        Returns
        -------
        :class:`aedt.modules.boundary.Boundary object`
            Boundary object.

        References
        ----------
        >>> oModule.AssignFrictionlessSupport

        Examples
        --------
        Allow the bottom face of a cylinder to slide in its plane in a structural design.

        >>> from ansys.aedt.core import Mechanical
        >>> from ansys.aedt.core.generic.constants import Plane
        >>> mech = Mechanical(solution_type="Structural")
        >>> cylinder = mech.modeler.create_cylinder(Plane.XY, [0, 0, 0], 3, 30, 0, "MyCylinder", "brass")
        >>> support = mech.assign_frictionless_support(cylinder.bottom_face_z.id, name="Frictionless1")

        """
        if self.solution_type not in (SolutionsMechanical.Structural, SolutionsMechanical.Modal):
            raise AEDTRuntimeError("This method works only in a Mechanical Structural analysis.")

        props = {}
        assignment = self.modeler.convert_to_selections(assignment, True)
        if type(assignment) is list:
            if type(assignment[0]) is str:
                props["Objects"] = assignment
            else:
                props["Faces"] = assignment

        if not name:
            name = generate_unique_name("Temp")
        return self._create_boundary(name, props, "Frictionless")

    @pyaedt_function_handler()
    def assign_fixed_support(self, assignment: list, name: str | None = "") -> BoundaryObject:
        """Assign a Mechanical fixed support.

        .. note::
           This method works only in a Mechanical Structural analysis.

        Parameters
        ----------
        assignment : list
            List of faces to apply to the fixed support.
        name : str, optional
            Name of the boundary. The default is ``""``, in which case
            the default name is used.

        Returns
        -------
        aedt.modules.boundary.Boundary
            Boundary object.

        References
        ----------
        >>> oModule.AssignFixedSupport

        Examples
        --------
        Clamp the bottom face of a cylinder in a structural design.

        >>> from ansys.aedt.core import Mechanical
        >>> from ansys.aedt.core.generic.constants import Plane
        >>> mech = Mechanical(solution_type="Structural")
        >>> cylinder = mech.modeler.create_cylinder(Plane.XY, [0, 0, 0], 3, 30, 0, "MyCylinder", "brass")
        >>> support = mech.assign_fixed_support(cylinder.bottom_face_z.id, name="Fixed1")

        """
        if self.solution_type not in (SolutionsMechanical.Structural, SolutionsMechanical.Modal):
            raise AEDTRuntimeError("This method works only in a Mechanical Structural analysis.")

        props = {}
        assignment = self.modeler.convert_to_selections(assignment, True)

        if type(assignment) is list:
            props["Faces"] = assignment

        if not name:
            name = generate_unique_name("Temp")
        return self._create_boundary(name, props, "FixedSupport")

    @pyaedt_function_handler()
    def assign_thermal_condition_uniform(
        self, assignment: list, temperature: str, name: str | None = ""
    ) -> BoundaryObject:
        """Assign a Mechanical excitation as thermal condition, with uniform temperature.

        .. note::
           This method works only in a Mechanical Structural analysis.

        Parameters
        ----------
        assignment : list
            List of faces to apply to the fixed support.
        temperature : str
            Temperature of the thermal condition with units.
        name : str, optional
            Name of the boundary. The default is ``""``, in which case
            the default name is used.

        Returns
        -------
        :class:`aedt.modules.boundary.Boundary object`
            Boundary object.

        References
        ----------
        >>> oModule.AssignThermalCondition

        Examples
        --------
        >>> from ansys.aedt.core import Mechanical
        >>> from ansys.aedt.core.generic.constants import SolutionsMechanical
        >>> mech = Mechanical(solution_type=SolutionsMechanical.Structural)
        >>> box = mech.modeler.create_box([0, 0, 0], [10, 10, 3], "Box_warm", "copper")
        >>> condition = mech.assign_thermal_condition_uniform(
        ...     assignment=[box.name], temperature="100cel", name="ThermalCond_Box"
        ... )

        """
        if self.solution_type not in (SolutionsMechanical.Structural, SolutionsMechanical.Modal):
            raise AEDTRuntimeError("This method works only in a Mechanical Structural analysis.")

        props = {}
        assignment = self.modeler.convert_to_selections(assignment, True)

        if type(assignment) is list:
            props["Objects"] = assignment

        props["Uniform"] = True
        props["ThermalCondition"] = temperature

        if not name:
            name = generate_unique_name("ThermalCondition_Uniform")
        return self._create_boundary(name, props, "ThermalCondition")

    @property
    def existing_analysis_sweeps(self):
        """Existing analysis sweeps in the design.

        Returns
        -------
        list
            List of existing analysis sweeps.

        References
        ----------
        >>> oModule.GetSetups

        Examples
        --------
        >>> from ansys.aedt.core import Mechanical
        >>> mech = Mechanical(solution_type="Thermal")
        >>> setup = mech.create_setup("MySetup")
        >>> mech.existing_analysis_sweeps
        ['MySetup : Solution']

        """
        setup_list = self.setup_names
        sweep_list = []
        for el in setup_list:
            sweep_list.append(el + " : Solution")
        return sweep_list

    @pyaedt_function_handler()
    def assign_heat_flux(
        self, assignment: list, heat_flux_type: str, value: str, name: str | None = ""
    ) -> BoundaryObject:
        """Assign heat flux boundary condition to an object or face list.

        Parameters
        ----------
        assignment : list
            List of objects, faces, or both.
        heat_flux_type : str
            Type of the heat flux. Options are ``"Total Power"`` or ``"Surface Flux"``.
        value : str
            Value of heat flux with units.
        name : str, optional
            Name of the boundary. The default is ``""``, in which case the default
            name is used.

        Returns
        -------
        :class:`aedt.modules.boundary.Boundary object`
            Boundary object.

        References
        ----------
        >>> oModule.AssignHeatFlux

        Examples
        --------
        Assign a total power of 5 W to a box and a surface heat flux to a face of another box.

        >>> from ansys.aedt.core import Mechanical
        >>> mech = Mechanical(solution_type="Thermal")
        >>> box1 = mech.modeler.create_box([0, 0, 0], [10, 10, 3], "box1", "copper")
        >>> box2 = mech.modeler.create_box([20, 20, 2], [10, 10, 3], "box2", "copper")
        >>> flux1 = mech.assign_heat_flux([box1.name], heat_flux_type="Total Power", value="5W")
        >>> flux2 = mech.assign_heat_flux([box2.top_face_x.id], heat_flux_type="Surface Flux", value="25mW_per_m2")

        """
        if self.solution_type not in (
            SolutionsMechanical.Thermal,
            SolutionsMechanical.SteadyStateThermal,
            SolutionsMechanical.TransientThermal,
        ):
            raise AEDTRuntimeError("This method works only in a Mechanical Thermal analysis.")

        props = {}
        assignment = self.modeler.convert_to_selections(assignment, True)
        if type(assignment) is list:
            if type(assignment[0]) is str:
                props["Objects"] = assignment
            else:
                props["Faces"] = assignment

        if heat_flux_type == "Total Power":
            props["TotalPower"] = value
        else:
            props["SurfaceFlux"] = value

        if not name:
            name = generate_unique_name("HeatFlux")
        return self._create_boundary(name, props, "HeatFlux")

    @pyaedt_function_handler()
    def assign_heat_generation(self, assignment: list, value: str, name: str | None = "") -> BoundaryObject:
        """Assign a heat generation boundary condition to an object list.

        Parameters
        ----------
        assignment : list
            List of objects.
        value : str
            Value of heat generation with units.
        name : str, optional
            Name of the boundary. The default is ``""``, in which case the default
            name is used.

        Returns
        -------
        :class:`aedt.modules.boundary.Boundary object`
            Boundary object.

        References
        ----------
        >>> oModule.AssignHeatGeneration

        Examples
        --------
        Make a copper box dissipate 1 W in a thermal design.

        >>> from ansys.aedt.core import Mechanical
        >>> mech = Mechanical(solution_type="Thermal")
        >>> box = mech.modeler.create_box([40, 40, 2], [10, 10, 3], "box3", "copper")
        >>> heat_gen = mech.assign_heat_generation([box.name], value="1W", name="heatgenBC")
        >>> heat_gen.props["TotalPower"]
        '1W'

        """
        if self.solution_type not in (
            SolutionsMechanical.Thermal,
            SolutionsMechanical.SteadyStateThermal,
            SolutionsMechanical.TransientThermal,
        ):
            raise AEDTRuntimeError("This method works only in a Mechanical Thermal analysis.")

        props = {}
        assignment = self.modeler.convert_to_selections(assignment, True)
        if type(assignment) is list:
            props["Objects"] = assignment

        props["TotalPower"] = value

        if not name:
            name = generate_unique_name("HeatGeneration")
        return self._create_boundary(name, props, "HeatGeneration")

    @pyaedt_function_handler()
    def assign_2way_coupling(self, setup: str | None = None, number_of_iterations: int | None = 2) -> bool:
        """Assign two-way coupling to a setup.

        Parameters
        ----------
        setup : str, optional
            Name of the setup. The default is ``None``, in which case the active setup is used.
        number_of_iterations : int, optional
            Number of iterations. The default is ``2``.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.

        References
        ----------
        >>> oModule.AddTwoWayCoupling

        Examples
        --------
        Run two coupling iterations between a thermal Mechanical design and its EM source.

        >>> from ansys.aedt.core import Mechanical
        >>> mech = Mechanical(solution_type="Thermal")
        >>> setup = mech.create_setup()
        >>> mech.assign_2way_coupling(setup=setup.name, number_of_iterations=2)
        True
        >>> mech.release_desktop()

        """
        if not setup:
            if self.setups:
                setup = self.setups[0].name
            else:
                self.logger.error("Setup is not defined.")
                return False

        self.oanalysis.AddTwoWayCoupling(
            setup,
            [
                "NAME:Options",
                "NumCouplingIters:=",
                number_of_iterations,
            ],
        )
        return True

    @pyaedt_function_handler()
    def create_setup(self, name: str | None = None, **kwargs) -> SetupIcepakFEA:
        """Create an analysis setup for Icepak FEA.

        Parameters
        ----------
        name : str, optional
            Name of the setup.
        **kwargs : dict, optional
            Available keys depend on setup chosen.
            For more information, see
            :doc:`../SetupTemplatesMechanical`.

        Returns
        -------
        :class:`ansys.aedt.core.modules.solve_setup.SetupIcepakFEA`
            Setup object.

        References
        ----------
        >>> oModule.InsertSetup

        Examples
        --------
        >>> from ansys.aedt.core import Mechanical
        >>> mech = Mechanical(solution_type="Thermal")
        >>> setup = mech.create_setup("MySetup")
        >>> setup.props["Solver"] = "Direct"
        >>> setup.update()
        True

        """
        setup_keys = SetupKeys.get_setup_templates()
        setup_type = self.design_solutions.default_setup

        if not name:
            name = self.generate_unique_setup_name("MySetupAuto")
        elif name in self.setup_names:
            name = self.generate_unique_setup_name(name)
            self.logger.warning(f"Name already exists. New name assigned is {name}.")

        props = copy.deepcopy(setup_keys[setup_type])

        setup = SetupIcepakFEA(app=self, name=name, props=props)

        if "props" in kwargs:
            _merge_props(props, kwargs.pop("props"))
        for arg_name, arg_value in kwargs.items():
            if props[arg_name] is not None:
                props[arg_name] = arg_value

        setup.create()

        return setup
