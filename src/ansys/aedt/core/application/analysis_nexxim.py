# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 - 2026 ANSYS, Inc. and/or its affiliates.
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
from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ansys.aedt.core.modeler.schematic import ModelerNexxim

from ansys.aedt.core.application.analysis import Analysis
from ansys.aedt.core.base import PyAedtBase
from ansys.aedt.core.generic.configurations import ConfigurationsNexxim
from ansys.aedt.core.generic.constants import SubstrateType
from ansys.aedt.core.generic.file_utils import generate_unique_name
from ansys.aedt.core.generic.general_methods import pyaedt_function_handler
from ansys.aedt.core.generic.settings import settings
from ansys.aedt.core.modeler.circuits.object_3d_circuit import CircuitComponent
from ansys.aedt.core.modeler.circuits.object_3d_circuit import Excitations
from ansys.aedt.core.modules.boundary.circuit_boundary import CurrentSinSource
from ansys.aedt.core.modules.boundary.circuit_boundary import PowerIQSource
from ansys.aedt.core.modules.boundary.circuit_boundary import PowerSinSource
from ansys.aedt.core.modules.boundary.circuit_boundary import Sources
from ansys.aedt.core.modules.boundary.circuit_boundary import VoltageDCSource
from ansys.aedt.core.modules.boundary.circuit_boundary import VoltageFrequencyDependentSource
from ansys.aedt.core.modules.boundary.circuit_boundary import VoltageSinSource
from ansys.aedt.core.modules.setup_templates import SetupKeys
from ansys.aedt.core.modules.solve_setup import SetupCircuit

if TYPE_CHECKING:
    from ansys.aedt.core.modules.boundary.common import BoundaryObject
    from ansys.aedt.core.visualization.post.post_circuit import PostProcessorCircuit


class FieldAnalysisCircuit(Analysis, PyAedtBase):
    """Provides the Field Analysis Circuit interface for Nexxim.

    This class is for circuit analysis setup in Nexxim. It is automatically
    initialized by a call from an application such as Circuit, Twin Builder,
    or Maxwell Circuit.

    Parameters
    ----------
    application : str
        Name of the application. Options are ``"Circuit Design"``,
        ``"Twin Builder"``, or ``"Maxwell Circuit"``.
    project : str
        Name of the project to select or the full path to the project
        or AEDTZ archive to open.
    design : str
        Name of the design to select.
    solution_type : str
        Solution type to apply to the design.
    setup : str, optional
        Name of the setup to use as the nominal. The default is
        ``None``, in which case the active setup is used or
        nothing is used.
    version : str, optional
        Version of AEDT to use. The default is ``None``, in which case
        the active version or latest installed version is used.
        This parameter is ignored when a script is launched within AEDT.
    non_graphical : bool, optional
        Whether to launch AEDT in non-graphical mode. The default
        is ``False``, in which case AEDT is launched in graphical mode.
        This parameter is ignored when a script is launched within AEDT.
    new_desktop : bool, optional
        Whether to launch an instance of AEDT in a new thread, even if
        another instance of the ``specified_version`` is active on the
        machine. The default is ``False``. This parameter is ignored when
        a script is launched within AEDT.
    close_on_exit : bool, optional
        Whether to release AEDT on exit. The default is ``False``.
    student_version : bool, optional
        Whether to open the AEDT student version. The default is
        ``False``. This parameter is ignored when a script is launched
        within AEDT.
    machine : str, optional
        Machine name to connect the oDesktop session to. This parameter works only on
        2022 R2 or later. The remote server must be up and running with the command
        `"ansysedt.exe -grpcsrv portnum"`. If the machine is `"localhost"`, the server
        starts if it is not present. The default is ``""``.
    port : int, optional
        Port number on which to start the oDesktop communication on an already existing server.
        This parameter is ignored when creating a new server. It works only in 2022 R2 or later.
        The remote server must be up and running with the command `"ansysedt.exe -grpcsrv portnum"`.
        The default is ``0``.
    aedt_process_id : int, optional
        Process ID for the instance of AEDT to point PyAEDT at. The default is
        ``None``. This parameter is only used when ``new_desktop = False``.
    remove_lock : bool, optional
        Whether to remove lock to project before opening it or not.
        The default is ``False``, which means to not unlock
        the existing project if needed and raise an exception.

    """

    def __init__(
        self,
        application: str,
        project: str,
        design: str,
        solution_type: str,
        setup: str = None,
        version: str = None,
        non_graphical: bool = False,
        new_desktop: bool = False,
        close_on_exit: bool = False,
        student_version: bool = False,
        machine: str = "",
        port: int = 0,
        aedt_process_id: int = None,
        remove_lock: bool = False,
    ):
        Analysis.__init__(
            self,
            application,
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

        self._modeler = None
        self._post = None
        self._internal_excitations = {}
        self._internal_sources = None
        self._configurations = ConfigurationsNexxim(self)
        if not settings.lazy_load:
            self._modeler = self.modeler
            self._post = self.post

    @property
    def configurations(self) -> ConfigurationsNexxim:
        """Property to import and export configuration files.

        Returns
        -------
        :class:`ansys.aedt.core.generic.configurations.ConfigurationsNexxim`
        """
        return self._configurations

    @pyaedt_function_handler()
    def delete_setup(self, name: str) -> bool:
        """Delete a setup.

        Parameters
        ----------
        name : str
            Name of the setup.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.

        References
        ----------
        >>> oModule.RemoveSimSetup
        """
        if name in self.setup_names:
            self.oanalysis.RemoveSimSetup([name])
            for s in self.setups:
                if s.name == name:
                    self.setups.remove(s)
            return True
        return False

    @pyaedt_function_handler()
    def push_down(self, component: CircuitComponent | str) -> bool:
        """Push-down to the child component and reinitialize the Circuit object.

        Parameters
        ----------
        component : str or :class:`ansys.aedt.core.modeler.cad.object_3d.circuit.CircuitComponent`
            Component to initialize.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.
        """
        out_name = ""
        if isinstance(component, CircuitComponent):
            out_name = self.design_name + ":" + component.component_info["RefDes"]
        elif "U" == component[0]:
            out_name = self.design_name + ":" + component
        elif ":" not in component:
            for v in self.modeler.components.components:
                if component == v.composed_name.split(";")[0].split("@")[1]:
                    out_name = self.design_name + ":" + v.component_info["RefDes"]
        else:
            out_name = component
        try:
            self.desktop_class.active_design(self.oproject, out_name, self.design_type)
            self.__init__(project=self.project_name, design=out_name)
        except Exception:  # pragma: no cover
            return False
        return True

    @pyaedt_function_handler()
    def pop_up(self) -> bool:
        """Pop-up to parent Circuit design and reinitialize Circuit object.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.
        """
        try:
            parent_name = self.odesign.GetName().split(";")[1].split("/")[0]
            self.desktop_class.active_design(self.oproject, parent_name, self.design_type)
            self.__init__(project=self.project_name, design=parent_name)
        except Exception:
            return False
        return True

    @property
    def post(self) -> PostProcessorCircuit:
        """PostProcessor.

        Returns
        -------
        :class:`ansys.aedt.core.visualization.post.post_circuit.PostProcessorCircuit`
            PostProcessor object.
        """
        if self._post is None and self._odesign:
            from ansys.aedt.core.visualization.post import post_processor

            self._post = post_processor(self)
        return self._post

    @property
    def modeler(self) -> "ModelerNexxim":
        """Modeler object.

        Returns
        -------
        :class:`ansys.aedt.core.modeler.schematic.ModelerNexxim`
        """
        if self._modeler is None and self._odesign:
            self.logger.reset_timer()
            from ansys.aedt.core.modeler.schematic import ModelerNexxim

            self._modeler = ModelerNexxim(self)
            self.logger.info_timer("Modeler class has been initialized!")

        return self._modeler

    @property
    def setup_names(self) -> list:
        """Setup names.

        References
        ----------
        >>> oModule.GetAllSolutionSetups
        """
        return [i.split(" : ")[0] for i in self.oanalysis.GetAllSolutionSetups()]

    @property
    def source_names(self) -> list:
        """Get all source names.

        Returns
        -------
        list
            List of source names.

        References
        ----------
        >>> oDesign.GetChildObject("Excitations").GetChildNames()
        """
        return list(self.get_oo_name(self.odesign, "Excitations"))

    @property
    def source_objects(self) -> list:
        """Get all source objects.

        Returns
        -------
        list
            List of source objects.
        """
        return [self.sources[name] for name in self.sources]

    @property
    def sources(self) -> list[Sources]:
        """Get all sources.

        Returns
        -------
        list[:class:`ansys.aedt.core.modules.boundary.circuit_boundary.Sources`]
            List of sources.

        """
        props = {}
        if not self._internal_sources:
            for source in self.source_names:
                props[source] = Sources(self, source)
                if props[source].source_type == "PowerSin":
                    props[source] = PowerSinSource(self, source)
                elif props[source].source_type == "PowerIQ":
                    props[source] = PowerIQSource(self, source)
                elif props[source].source_type == "VoltageFrequencyDependent":
                    props[source] = VoltageFrequencyDependentSource(self, source)
                elif props[source].source_type == "VoltageDC":
                    props[source] = VoltageDCSource(self, source)
                elif props[source].source_type == "VoltageSin":
                    props[source] = VoltageSinSource(self, source)
                elif props[source].source_type == "CurrentSin":
                    props[source] = CurrentSinSource(self, source)
            self._internal_sources = props
        else:
            props = self._internal_sources
            if not sorted(list(props.keys())) == sorted(self.source_names):
                a = set(str(x) for x in props.keys())
                b = set(str(x) for x in self.source_names)
                if len(a) == len(b):
                    unmatched_new_name = list(b - a)[0]
                    unmatched_old_name = list(a - b)[0]
                    props[unmatched_new_name] = props[unmatched_old_name]
                    del props[unmatched_old_name]
                else:
                    for old_source in props.keys():
                        if old_source not in self.source_names:
                            del props[old_source]
                            break

        return props

    @property
    def excitation_names(self) -> list[str]:
        """Get all excitation names.

        Returns
        -------
        list
            List of excitation names. Excitations with multiple modes will return one
            excitation for each mode.

        References
        ----------
        >>> oModule.GetExcitations
        """
        return [p.replace("IPort@", "").split(";")[0] for p in self.modeler.oeditor.GetAllPorts() if "IPort@" in p]

    @property
    def design_excitations(self) -> dict[str, BoundaryObject]:
        """Get all excitation.

        Returns
        -------
        dict[str, :class:`ansys.aedt.core.modules.boundary.common.BoundaryObject`]
           Excitation boundaries.

        References
        ----------
        >>> oModule.GetExcitations
        """
        props = {}

        if not self._internal_excitations:
            for comp in self.modeler.schematic.components.values():
                if comp.name in self.excitation_names:
                    props[comp.name] = comp
            self._internal_excitations = props
        else:
            props = self._internal_excitations
            if not sorted(list(props.keys())) == sorted(self.excitation_names):
                a = set(str(x) for x in props.keys())
                b = set(str(x) for x in self.excitation_names)
                if len(a) == len(b):
                    unmatched_new_name = list(b - a)[0]
                    unmatched_old_name = list(a - b)[0]
                    props[unmatched_new_name] = props[unmatched_old_name]
                    del props[unmatched_old_name]
                else:
                    if len(a) > len(b):
                        for old_port in props.keys():
                            if old_port not in self.excitation_names:
                                del props[old_port]
                                return props
                    else:
                        for new_port in self.excitation_names:
                            if new_port not in props.keys():
                                props[new_port] = Excitations(self, new_port)
        return props

    @pyaedt_function_handler()
    def create_setup(self, name: str = "MySetupAuto", setup_type: str | None = None, **kwargs) -> SetupCircuit:
        """Create a setup.

        Parameters
        ----------
        name : str, optional
            Name of the new setup. The default is ``"MySetupAuto"``.
        setup_type : str, optional
            Type of the setup. The default is ``None``, in which case
            the default type is applied.
        **kwargs : dict, optional
            Extra arguments to set up the circuit.
            Available keys depend on the setup chosen.
            For more information, see
            :doc:`../SetupTemplatesCircuit`.


        Returns
        -------
        :class:`ansys.aedt.core.modules.solve_setup.SetupCircuit`
            Setup object.

        References
        ----------
        >>> oModule.AddLinearNetworkAnalysis
        >>> oModule.AddDCAnalysis
        >>> oModule.AddTransient
        >>> oModule.AddQuickEyeAnalysis
        >>> oModule.AddVerifEyeAnalysis
        >>> oModule.AddAMIAnalysis


        Examples
        --------
        >>> from ansys.aedt.core import Circuit
        >>> from ansys.aedt.core.generic.constants import Setups
        >>> app = Circuit()
        >>> app.create_setup(name="Setup1", setup_type=Setups.NexximLNA, Data="LINC 0GHz 4GHz 501")
        """
        if setup_type is None:
            setup_type = self.design_solutions.default_setup
        elif setup_type in SetupKeys.SetupNames:
            setup_type = SetupKeys.SetupNames.index(setup_type)
        name = self.generate_unique_setup_name(name)
        setup = SetupCircuit(self, setup_type, name)
        tmp_setups = self.setups
        setup.create()
        setup.auto_update = False

        if "props" in kwargs:
            for el in kwargs["props"]:
                setup.props[el] = kwargs["props"][el]
        for arg_name, arg_value in kwargs.items():
            if arg_name == "props":
                continue
            if setup[arg_name] is not None:
                setup[arg_name] = arg_value
        setup.auto_update = True
        setup.update()
        self._setups = tmp_setups + [setup]
        return setup

    @pyaedt_function_handler()
    def change_properties(
        self,
        aedt_object: object,
        tab_name: str,
        property_object: str,
        property_names: list,
        property_values: list,
        property_types: list = None,
    ) -> bool:
        """Change multiple properties.

        Parameters
        ----------
        aedt_object :
            AEDT object. It can be oproject, odesign, oeditor or any of the objects to which the property belongs.
        tab_name : str
            Name of the tab to update. Options are ``BaseElementTab``, ``EM Design``, and
            ``FieldsPostProcessorTab``. The default is ``BaseElementTab``.
        property_object : str
            Name of the property object.
        property_names : list
            List of property names. For example, ``["prop1", "prop2"]``.
        property_values : list
            List of property values corresponding to the property names.
        property_types : list, optional
            List of property types corresponding to the property names.
            Values are  ``"Value"``, ``"ButtonText"``, ``"Hidden"``.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.

        References
        ----------
        >>> oEditor.ChangeProperty
        """
        button_list = [
            "file",
            "buffer_mode",
            "logic_in",
            "out_of_in",
            "DataPattern",
            "txrj",
            "txpj",
            "txuj",
            "txcj",
            "txrj",
            "EyeMeasurementFunctions",
        ]
        if len(property_names) != len(property_values):
            raise ValueError("``property_names`` and ``property_values`` must have the same length.")
        if property_types and isinstance(property_types, str):
            property_types = [property_types] * len(property_names)
        elif property_types and len(property_types) != len(property_names):
            raise ValueError("``property_names`` and ``property_types`` must have the same length.")
        elif not property_types:
            property_types = ["Value" if i not in button_list else "ButtonText" for i in property_names]
        return super().change_properties(
            aedt_object, tab_name, property_object, property_names, property_values, property_types
        )


class SubstrateDataBlock(PyAedtBase):
    """Represents a substrate data block and provides the API to create it.

    Use the class-level factory methods (``microstrip``, ``stripline``, ...) to
    instantiate a correctly configured object, then call :meth:`create` to push it
    to AEDT.  Alternatively, pass *all* raw keyword arguments directly to the
    constructor for full control.

    Parameters
    ----------
    app : :class:`ansys.aedt.core.circuit.Circuit`
        Circuit application instance.
    name : str
        Unique name for the substrate data block.
    substrate_type : int
        One of the integer constants defined in :class:`SubstrateType`.
    dielectric : list of str
        List of dielectric parameters whose content depends on *substrate_type*.
    metal_material : str, optional
        Name of the primary conductor material. The default is ``"copper"``.
    metal_thickness : str, optional
        Primary conductor thickness including units.  The default is ``"0.7mil"``.
    bottom_metal_material : str, optional
        Name of the second (bottom) conductor material.
        The default is ``""`` (not specified).
    bottom_metal_thickness : str, optional
        Second conductor thickness. The default is ``""`` (not specified).
    cover_metal_material : str, optional
        Name of the third (cover) conductor material. The default is ``""`` (not specified).
    cover_metal_thickness : str, optional
        Third conductor thickness. The default is ``""`` (not specified).
    roughness : str, optional
        Surface roughness of the conductor including units. The default is ``""`` (not specified).
    metal_specify_type : int, optional
        Metal specification type flag used by AEDT. The default is ``0``.
    metal_temp_material : str, optional
        Temporary metal material name used by AEDT during parameter sweeps.
        The default is ``""`` (not specified).
    dielectric_temp_materials : list of str, optional
        List of up to five temporary dielectric material names used by AEDT
        during parameter sweeps. The default is five empty strings.

    Examples
    --------
    Create a microstrip substrate via the factory method:

    >>> from ansys.aedt.core import Circuit
    >>> cir = Circuit()
    >>> sub = SubstrateDataBlock.microstrip(
    ...     cir,
    ...     name="MySub",
    ...     dielectric_height="10mil",
    ...     dielectric_constant=4.4,
    ...     loss_tangent=0.02,
    ...     air_height="25mm",
    ...     roughness="1pm",
    ... )
    >>> sub.create()

    Create a stripline substrate:

    >>> sub = SubstrateDataBlock.stripline(
    ...     cir,
    ...     name="MyStripline",
    ...     dielectric_height="20mil",
    ...     dielectric_constant=4.4,
    ...     loss_tangent=0.02,
    ...     roughness="",
    ... )
    >>> sub.create()
    """

    def __init__(
        self,
        app,
        name: str | None,
        substrate_type: "SubstrateType",
        dielectric: list,
        metal_material: str = "copper",
        metal_thickness: str = "0.7mil",
        bottom_metal_material: str = "",
        bottom_metal_thickness: str = "",
        cover_metal_material: str = "",
        cover_metal_thickness: str = "",
        roughness: str = "",
        metal_specify_type: int = 0,
        metal_temp_material: str = "",
        dielectric_temp_materials: list | None = None,
    ) -> None:
        self._app = app
        # Disable during construction to avoid triggering updates before the object is fully initialized
        self._auto_update = False

        # Handle name assignment and uniqueness
        if not name:
            self._name = generate_unique_name("Substrate")
        elif name in self._app.substrates:
            new_name = generate_unique_name(name)
            app.logger.warning(
                f"Substrate data block '{name}' already exists in the design. Using '{new_name}' instead."
            )
            self._name = new_name
        else:
            self._name = name
        self._substrate_type = substrate_type
        self._dielectric = dielectric
        self._metal_material = metal_material
        self._metal_thickness = metal_thickness
        self._bottom_metal_material = bottom_metal_material
        self._bottom_metal_thickness = bottom_metal_thickness
        self._cover_metal_material = cover_metal_material
        self._cover_metal_thickness = cover_metal_thickness
        self._roughness = roughness
        self._metal_specify_type = metal_specify_type
        self._metal_temp_material = metal_temp_material
        self._dielectric_temp_materials = (
            dielectric_temp_materials if dielectric_temp_materials is not None else ["", "", "", "", ""]
        )

        # Ensure exactly 5 entries
        while len(self._dielectric_temp_materials) < 5:
            self._dielectric_temp_materials.append("")

        # Enable after construction
        self._auto_update = True

    @property
    def auto_update(self) -> bool:
        """Whether to push changes to AEDT immediately when a property is set."""
        return self._auto_update

    @auto_update.setter
    def auto_update(self, value: bool) -> None:
        self._auto_update = bool(value)

    @property
    def name(self) -> str:
        """Substrate name."""
        return self._name

    @name.setter
    def name(self, new_name: str) -> None:
        if new_name == self.name:
            return

        if new_name in self._app.substrate_names:
            old_name = new_name
            new_name = generate_unique_name(new_name)
            self._app.logger.warning(
                f"Substrate data block '{old_name}' already exists in the design. Using '{new_name}' instead."
            )
        self._app.odata_block.Rename(self._name, new_name)

        # Update substrates dictionary
        self._app._substrates[new_name] = self._app.substrates[self._name]
        del self._app._substrates[self._name]

        self._name = new_name

    @property
    def substrate_type(self):
        """Substrate type."""
        return self._substrate_type

    @substrate_type.setter
    def substrate_type(self, value) -> None:
        self._substrate_type = value
        if self.auto_update:
            self.update()

    @property
    def dielectric(self) -> list:
        """Dielectric parameters."""
        return self._dielectric

    @dielectric.setter
    def dielectric(self, value: list) -> None:
        self._dielectric = value
        if self.auto_update:
            self.update()

    @property
    def metal_material(self) -> str:
        """Primary conductor material name."""
        return self._metal_material

    @metal_material.setter
    def metal_material(self, value: str) -> None:
        self._metal_material = value
        if self.auto_update:
            self.update()

    @property
    def metal_thickness(self) -> str:
        """Primary conductor thickness."""
        return self._metal_thickness

    @metal_thickness.setter
    def metal_thickness(self, value: str) -> None:
        self._metal_thickness = value
        if self.auto_update:
            self.update()

    @property
    def bottom_metal_material(self) -> str:
        """Bottom conductor material name."""
        return self._bottom_metal_material

    @bottom_metal_material.setter
    def bottom_metal_material(self, value: str) -> None:
        self._bottom_metal_material = value
        if self.auto_update:
            self.update()

    @property
    def bottom_metal_thickness(self) -> str:
        """Bottom conductor thickness."""
        return self._bottom_metal_thickness

    @bottom_metal_thickness.setter
    def bottom_metal_thickness(self, value: str) -> None:
        self._bottom_metal_thickness = value
        if self.auto_update:
            self.update()

    @property
    def cover_metal_material(self) -> str:
        """Cover conductor material name."""
        return self._cover_metal_material

    @cover_metal_material.setter
    def cover_metal_material(self, value: str) -> None:
        self._cover_metal_material = value
        if self.auto_update:
            self.update()

    @property
    def cover_metal_thickness(self) -> str:
        """Cover conductor thickness."""
        return self._cover_metal_thickness

    @cover_metal_thickness.setter
    def cover_metal_thickness(self, value: str) -> None:
        self._cover_metal_thickness = value
        if self.auto_update:
            self.update()

    @property
    def roughness(self) -> str:
        """Conductor surface roughness."""
        return self._roughness

    @roughness.setter
    def roughness(self, value: str) -> None:
        self._roughness = value
        if self.auto_update:
            self.update()

    @property
    def metal_specify_type(self) -> int:
        """Metal specification type flag."""
        return self._metal_specify_type

    @metal_specify_type.setter
    def metal_specify_type(self, value: int) -> None:
        self._metal_specify_type = value
        if self.auto_update:
            self.update()

    @property
    def metal_temp_material(self) -> str:
        """Temporary metal material name."""
        return self._metal_temp_material

    @metal_temp_material.setter
    def metal_temp_material(self, value: str) -> None:
        self._metal_temp_material = value
        if self.auto_update:
            self.update()

    @property
    def dielectric_temp_materials(self) -> list:
        """Temporary dielectric material names (list of 5)."""
        return self._dielectric_temp_materials

    @dielectric_temp_materials.setter
    def dielectric_temp_materials(self, value: list) -> None:
        self._dielectric_temp_materials = value
        if self.auto_update:
            self.update()

    @classmethod
    def microstrip(
        cls,
        app,
        dielectric_height: str = "1mm",
        dielectric_constant: float = 2.2,
        loss_tangent: float = 0.0,
        air_height: str = "25mm",
        roughness: str = "",
        metal_material: str = "copper",
        metal_thickness: str = "0.7mil",
        name: str | None = None,
    ) -> "SubstrateDataBlock":
        """Create a microstrip substrate.

        Parameters
        ----------
        app : :class:`ansys.aedt.core.circuit.Circuit`
            Circuit application instance.
        dielectric_height : str, optional
            Dielectric layer height with units.  The default is ``"1mm"``.
        dielectric_constant : float, optional
            Relative permittivity (εr).  The default is ``2.2``.
        loss_tangent : float, optional
            Dielectric loss tangent.  The default is ``0.0``.
        air_height : str, optional
            Air-region height above the substrate with units.  The default is ``"25mm"``.
        roughness : str, optional
            Conductor surface roughness with units.  The default is ``""``.
        name : str, optional
            Substrate name.  A unique name is generated when ``None``.
        metal_material : str, optional
            Conductor material name.  The default is ``"copper"``.
        metal_thickness : str, optional
            Conductor thickness with units.  The default is ``"0.7mil"``.

        Returns
        -------
        SubstrateDataBlock
        """
        dielectric = [
            dielectric_height,
            str(dielectric_constant),
            str(loss_tangent),
            air_height,
            "0",
            "0",
            "0",
        ]
        return cls(
            app,
            name=name,
            substrate_type=SubstrateType.Microstrip,
            dielectric=dielectric,
            metal_material=metal_material,
            metal_thickness=metal_thickness,
            roughness=roughness,
        )

    @classmethod
    def stripline(
        cls,
        app,
        dielectric_height: str = "1mm",
        dielectric_constant: float = 2.2,
        loss_tangent: float = 0.0,
        roughness: str = "",
        metal_material: str = "copper",
        metal_thickness: str = "0.7mil",
        name: str | None = None,
        bottom_metal_material: str = "",
        bottom_metal_thickness: str = "",
    ) -> "SubstrateDataBlock":
        """Create a stripline substrate (Type 1).

        Parameters
        ----------
        app : :class:`ansys.aedt.core.circuit.Circuit`
            Circuit application instance.
        dielectric_height : str, optional
            Dielectric height between the conductor and the ground plane with units.
            The default is ``"1mm"``.
        dielectric_constant : float, optional
            Relative permittivity (εr).  The default is ``2.2``.
        loss_tangent : float, optional
            Dielectric loss tangent.  The default is ``0.0``.
        roughness : str, optional
            Conductor roughness with units.  The default is ``""``.
        name : str, optional
            Substrate name.  A unique name is generated when ``None``.
        metal_material : str, optional
            Top conductor material.  The default is ``"copper"``.
        metal_thickness : str, optional
            Top conductor thickness with units.  The default is ``"0.7mil"``.
        bottom_metal_material : str, optional
            Bottom conductor material.  The default is ``""``.
        bottom_metal_thickness : str, optional
            Bottom conductor thickness with units.  The default is ``""``.

        Returns
        -------
        SubstrateDataBlock
        """
        dielectric = [dielectric_height, str(dielectric_constant), str(loss_tangent)]
        return cls(
            app,
            name=name,
            substrate_type=SubstrateType.Stripline,
            dielectric=dielectric,
            metal_material=metal_material,
            metal_thickness=metal_thickness,
            bottom_metal_material=bottom_metal_material,
            bottom_metal_thickness=bottom_metal_thickness,
            roughness=roughness,
        )

    @classmethod
    def suspended_stripline(
        cls,
        app,
        dielectric_height: str = "1mm",
        air_height: str = "0.5mm",
        dielectric_constant: float = 2.2,
        loss_tangent: float = 0.0,
        roughness: str = "",
        metal_material: str = "copper",
        metal_thickness: str = "0.7mil",
        name: str | None = None,
    ) -> "SubstrateDataBlock":
        """Create a suspended stripline substrate (Type 2).

        Parameters
        ----------
        app : :class:`ansys.aedt.core.circuit.Circuit`
            Circuit application instance.
        dielectric_height : str, optional
            Dielectric slab height with units.  The default is ``"1mm"``.
        air_height : str, optional
            Air-gap height between the conductor and the dielectric with units.
            The default is ``"0.5mm"``.
        dielectric_constant : float, optional
            Relative permittivity (εr).  The default is ``2.2``.
        loss_tangent : float, optional
            Dielectric loss tangent.  The default is ``0.0``.
        roughness : str, optional
            Conductor roughness with units.  The default is ``""``.
        name : str, optional
            Substrate name.  A unique name is generated when ``None``.
        metal_material : str, optional
            Conductor material.  The default is ``"copper"``.
        metal_thickness : str, optional
            Conductor thickness with units.  The default is ``"0.7mil"``.

        Returns
        -------
        SubstrateDataBlock
        """
        dielectric = [dielectric_height, air_height, str(dielectric_constant), str(loss_tangent)]
        return cls(
            app,
            name=name,
            substrate_type=SubstrateType.SuspendedStripline,
            dielectric=dielectric,
            metal_material=metal_material,
            metal_thickness=metal_thickness,
            roughness=roughness,
        )

    @classmethod
    def offset_stripline(
        cls,
        app,
        dielectric_height: str = "1mm",
        dielectric_constant: float = 2.2,
        loss_tangent: float = 0.0,
        enclosure_width: str = "25mm",
        enclosure_height: str = "25mm",
        roughness: str = "",
        metal_material: str = "copper",
        metal_thickness: str = "0.7mil",
        name: str | None = None,
    ) -> "SubstrateDataBlock":
        """Create an offset stripline substrate (Type 3).

        Parameters
        ----------
        app : :class:`ansys.aedt.core.circuit.Circuit`
            Circuit application instance.
        dielectric_height : str, optional
            Dielectric layer height with units.  The default is ``"1mm"``.
        dielectric_constant : float, optional
            Relative permittivity (εr).  The default is ``2.2``.
        loss_tangent : float, optional
            Dielectric loss tangent.  The default is ``0.0``.
        enclosure_width : str, optional
            Enclosure width with units.  The default is ``"25mm"``.
        enclosure_height : str, optional
            Enclosure height with units.  The default is ``"25mm"``.
        roughness : str, optional
            Conductor roughness with units.  The default is ``""``.
        name : str, optional
            Substrate name.  A unique name is generated when ``None``.
        metal_material : str, optional
            Conductor material.  The default is ``"copper"``.
        metal_thickness : str, optional
            Conductor thickness with units.  The default is ``"0.7mil"``.

        Returns
        -------
        SubstrateDataBlock
        """
        dielectric = [
            dielectric_height,
            str(dielectric_constant),
            str(loss_tangent),
            enclosure_width,
            enclosure_height,
        ]
        return cls(
            app,
            name=name,
            substrate_type=SubstrateType.OffsetStripline,
            dielectric=dielectric,
            metal_material=metal_material,
            metal_thickness=metal_thickness,
            roughness=roughness,
        )

    @classmethod
    def coplanar_waveguide(
        cls,
        app,
        dielectric_height: str = "1mm",
        dielectric_constant: float = 2.2,
        loss_tangent: float = 0.0,
        cover_height: str = "25mm",
        roughness: str = "",
        metal_material: str = "copper",
        metal_thickness: str = "0.7mil",
        name: str | None = None,
        cover_metal_material: str = "",
        cover_metal_thickness: str = "",
    ) -> "SubstrateDataBlock":
        """Create a coplanar waveguide (CPW) substrate (Type 4).

        Parameters
        ----------
        app : :class:`ansys.aedt.core.circuit.Circuit`
            Circuit application instance.
        dielectric_height : str, optional
            Dielectric layer height with units.  The default is ``"1mm"``.
        dielectric_constant : float, optional
            Relative permittivity (εr).  The default is ``2.2``.
        loss_tangent : float, optional
            Dielectric loss tangent.  The default is ``0.0``.
        cover_height : str, optional
            Height from the conductor to the metallic cover with units.
            The default is ``"25mm"``.
        roughness : str, optional
            Conductor roughness with units.  The default is ``""``.
        name : str, optional
            Substrate name.  A unique name is generated when ``None``.
        metal_material : str, optional
            Strip conductor material.  The default is ``"copper"``.
        metal_thickness : str, optional
            Strip conductor thickness with units.  The default is ``"0.7mil"``.
        cover_metal_material : str, optional
            Cover conductor material.  The default is ``""``.
        cover_metal_thickness : str, optional
            Cover conductor thickness with units.  The default is ``""``.

        Returns
        -------
        SubstrateDataBlock
        """
        dielectric = [dielectric_height, str(dielectric_constant), str(loss_tangent), cover_height]
        return cls(
            app,
            name=name,
            substrate_type=SubstrateType.CoplanarWaveguide,
            dielectric=dielectric,
            metal_material=metal_material,
            metal_thickness=metal_thickness,
            cover_metal_material=cover_metal_material,
            cover_metal_thickness=cover_metal_thickness,
            roughness=roughness,
        )

    @classmethod
    def grounded_coplanar_waveguide(
        cls,
        app,
        dielectric_height: str = "1mm",
        dielectric_constant: float = 2.2,
        loss_tangent: float = 0.0,
        bottom_air_height: str = "5mm",
        top_air_height: str = "5mm",
        roughness: str = "",
        metal_material: str = "copper",
        metal_thickness: str = "0.7mil",
        name: str | None = None,
    ) -> "SubstrateDataBlock":
        """Create a grounded coplanar waveguide (GCPW) substrate (Type 5).

        Parameters
        ----------
        app : :class:`ansys.aedt.core.circuit.Circuit`
            Circuit application instance.
        dielectric_height : str, optional
            Dielectric slab height with units.  The default is ``"1mm"``.
        dielectric_constant : float, optional
            Relative permittivity (εr).  The default is ``2.2``.
        loss_tangent : float, optional
            Dielectric loss tangent.  The default is ``0.0``.
        bottom_air_height : str, optional
            Air gap below the dielectric slab with units.  The default is ``"5mm"``.
        top_air_height : str, optional
            Air gap above the dielectric slab with units.  The default is ``"5mm"``.
        roughness : str, optional
            Conductor roughness with units.  The default is ``""``.
        name : str, optional
            Substrate name.  A unique name is generated when ``None``.
        metal_material : str, optional
            Conductor material.  The default is ``"copper"``.
        metal_thickness : str, optional
            Conductor thickness with units.  The default is ``"0.7mil"``.

        Returns
        -------
        SubstrateDataBlock
        """
        dielectric = [
            dielectric_height,
            str(dielectric_constant),
            str(loss_tangent),
            bottom_air_height,
            top_air_height,
        ]
        return cls(
            app,
            name=name,
            substrate_type=SubstrateType.GroundedCoplanarWaveguide,
            dielectric=dielectric,
            metal_material=metal_material,
            metal_thickness=metal_thickness,
            roughness=roughness,
        )

    @classmethod
    def slotline(
        cls,
        app,
        dielectric_height: str = "1mm",
        dielectric_constant: float = 2.2,
        loss_tangent: float = 0.0,
        bottom_air_height: str = "5mm",
        top_air_height: str = "5mm",
        roughness: str = "",
        metal_material: str = "copper",
        metal_thickness: str = "0.7mil",
        name: str | None = None,
    ) -> "SubstrateDataBlock":
        """Create a slotline substrate (Type 6).

        Parameters
        ----------
        app : :class:`ansys.aedt.core.circuit.Circuit`
            Circuit application instance.
        dielectric_height : str, optional
            Dielectric slab height with units.  The default is ``"1mm"``.
        dielectric_constant : float, optional
            Relative permittivity (εr).  The default is ``2.2``.
        loss_tangent : float, optional
            Dielectric loss tangent.  The default is ``0.0``.
        bottom_air_height : str, optional
            Air gap below the dielectric slab with units.  The default is ``"5mm"``.
        top_air_height : str, optional
            Air gap above the dielectric slab with units.  The default is ``"5mm"``.
        roughness : str, optional
            Conductor roughness with units.  The default is ``""``.
        name : str, optional
            Substrate name.  A unique name is generated when ``None``.
        metal_material : str, optional
            Conductor material.  The default is ``"copper"``.
        metal_thickness : str, optional
            Conductor thickness with units.  The default is ``"0.7mil"``.

        Returns
        -------
        SubstrateDataBlock
        """
        dielectric = [
            dielectric_height,
            str(dielectric_constant),
            str(loss_tangent),
            bottom_air_height,
            top_air_height,
        ]
        return cls(
            app,
            name=name,
            substrate_type=SubstrateType.Slotline,
            dielectric=dielectric,
            metal_material=metal_material,
            metal_thickness=metal_thickness,
            roughness=roughness,
        )

    @classmethod
    def rectangular_waveguide(
        cls,
        app,
        num_layers: int = 1,
        roughness: str = "",
        metal_material: str = "copper",
        metal_thickness: str = "0.7mil",
        name: str | None = None,
    ) -> "SubstrateDataBlock":
        """Create a rectangular waveguide substrate (Type 9).

        Parameters
        ----------
        app : :class:`ansys.aedt.core.circuit.Circuit`
            Circuit application instance.
        num_layers : int, optional
            Number of dielectric layers in the stack.  The default is ``1``.
        roughness : str, optional
            Conductor roughness with units.  The default is ``""``.
        name : str, optional
            Substrate name.  A unique name is generated when ``None``.
        metal_material : str, optional
            Conductor material.  The default is ``"copper"``.
        metal_thickness : str, optional
            Conductor thickness with units.  The default is ``"0.7mil"``.

        Returns
        -------
        SubstrateDataBlock
        """
        dielectric = [str(num_layers), "0", str(num_layers)]
        return cls(
            app,
            name=name,
            substrate_type=SubstrateType.RectangularWaveguide,
            dielectric=dielectric,
            metal_material=metal_material,
            metal_thickness=metal_thickness,
            roughness=roughness,
        )

    @classmethod
    def substrate_reference(
        cls,
        app,
        dielectric_height: str = "1mm",
        dielectric_constant: float = 2.2,
        loss_tangent: float = 0.0,
        air_height: str = "25mm",
        roughness: str = "",
        metal_material: str = "copper",
        metal_thickness: str = "0.7mil",
        name: str | None = None,
    ) -> "SubstrateDataBlock":
        """Create a substrate reference (Type 10).

        A substrate reference is a named substrate used as a reference by
        transmission-line models in the schematic.

        Parameters
        ----------
        app : :class:`ansys.aedt.core.circuit.Circuit`
            Circuit application instance.
        name : str, optional
            Substrate name.  A unique name is generated when ``None``.
        dielectric_height : str, optional
            Dielectric layer height with units.  The default is ``"1mm"``.
        dielectric_constant : float, optional
            Relative permittivity (εr).  The default is ``2.2``.
        loss_tangent : float, optional
            Dielectric loss tangent.  The default is ``0.0``.
        air_height : str, optional
            Air-region height with units.  The default is ``"25mm"``.
        roughness : str, optional
            Conductor roughness with units.  The default is ``""``.
        metal_material : str, optional
            Conductor material.  The default is ``"copper"``.
        metal_thickness : str, optional
            Conductor thickness with units.  The default is ``"0.7mil"``.

        Returns
        -------
        SubstrateDataBlock
        """
        dielectric = [
            dielectric_height,
            str(dielectric_constant),
            str(loss_tangent),
            air_height,
            "0.0",
            "0.0",
            "0.0",
        ]
        return cls(
            app,
            name=name,
            substrate_type=SubstrateType.SubstrateReference,
            dielectric=dielectric,
            metal_material=metal_material,
            metal_thickness=metal_thickness,
            roughness=roughness,
        )

    @classmethod
    def from_dict(cls, app, data: dict) -> "SubstrateDataBlock":
        """Build `SubstrateDataBlock` from ``design_properties`` dict entry.

        Parameters
        ----------
        app : :class:`ansys.aedt.core.circuit.Circuit`
            Circuit application instance.
        data : dict
            One entry from ``app.design_properties['SubstrateData']``.

        Returns
        -------
        SubstrateDataBlock
            Reconstructed substrate object.
        """
        import re as _re

        name = data.get("Name", "")
        substrate_type = SubstrateType(int(data.get("Type", 0)))
        dielectric = list(data.get("Dielectric", []))
        metal_specify_type = int(data.get("MetalSpecifyType", 0))
        metal_temp_material = data.get("MetalTempMaterial", "")
        dielectric_temp_materials = [
            data.get("DielecTempMaterial0", ""),
            data.get("DielecTempMaterial1", ""),
            data.get("DielecTempMaterial2", ""),
            data.get("DielecTempMaterial3", ""),
            data.get("DielecTempMaterial4", ""),
        ]

        # Parse Metalization list:
        # Format: ["Metal('mat'", "res", "'thick')", "Metal('mat2'", ...], "Roughness('val')"]
        metals: list[list[str]] = []
        roughness = ""
        met_list = data.get("Metalization", [])
        i = 0
        while i < len(met_list):
            entry = str(met_list[i])
            if entry.startswith("Metal("):
                mat_raw = entry  # e.g. "Metal('copper'"
                mat_match = _re.search(r"Metal\('([^']*)'\s*$|Metal\('([^']*)'", mat_raw)
                metal_mat = ""
                if mat_match:
                    metal_mat = mat_match.group(1) or mat_match.group(2) or ""
                res_raw = str(met_list[i + 1]) if i + 1 < len(met_list) else ""
                try:
                    res_val = float(res_raw) if res_raw else ""
                except ValueError:
                    res_val = res_raw
                thick_raw = str(met_list[i + 2]) if i + 2 < len(met_list) else ""
                thick_match = _re.search(r"'([^']*)'", thick_raw)
                metal_thick = thick_match.group(1) if thick_match else thick_raw
                metals.append([metal_mat, res_val, metal_thick])
                i += 3
            elif entry.startswith("Roughness("):
                rough_match = _re.search(r"Roughness\('([^']*)'\)", entry)
                roughness = rough_match.group(1) if rough_match else ""
                i += 1
            else:
                i += 1

        def _get_metal(idx):
            if idx < len(metals):
                return metals[idx]
            return ["", "", ""]

        m0 = _get_metal(0)
        m1 = _get_metal(1)
        m2 = _get_metal(2)

        # Bypass name uniqueness check and auto_update during reconstruction
        obj = object.__new__(cls)
        obj._app = app
        obj._auto_update = False
        obj._name = name
        obj._substrate_type = substrate_type
        obj._dielectric = dielectric
        obj._metal_material = m0[0]
        obj._metal_thickness = m0[2]
        obj._bottom_metal_material = m1[0]
        obj._bottom_metal_thickness = m1[2]
        obj._cover_metal_material = m2[0]
        obj._cover_metal_thickness = m2[2]
        obj._roughness = roughness
        obj._metal_specify_type = metal_specify_type
        obj._metal_temp_material = metal_temp_material
        obj._dielectric_temp_materials = dielectric_temp_materials
        obj._auto_update = True
        return obj

    def _build_args(self) -> list:
        """Build the argument list for ``AddSubstrateDataBlock``."""
        dielec_temps = self.dielectric_temp_materials[:5]
        metalization = [
            "Metal:=",
            [self.metal_material, "", self.metal_thickness],
            "Metal:=",
            [self.bottom_metal_material, "", self.bottom_metal_thickness],
            "Metal:=",
            [self.cover_metal_material, "", self.cover_metal_thickness],
            "Roughness:=",
            [self.roughness],
        ]
        return [
            "NAME:DataBlock",
            "Name:=",
            self.name,
            "Type:=",
            int(self.substrate_type),
            "MetalSpecifyType:=",
            self.metal_specify_type,
            "DielecTempMaterial0:=",
            dielec_temps[0],
            "DielecTempMaterial1:=",
            dielec_temps[1],
            "DielecTempMaterial2:=",
            dielec_temps[2],
            "DielecTempMaterial3:=",
            dielec_temps[3],
            "DielecTempMaterial4:=",
            dielec_temps[4],
            "MetalTempMaterial:=",
            self.metal_temp_material,
            "Dielectric:=",
            self.dielectric,
            "DielectricRef:=",
            [0, ""],
            "Metalization:=",
            metalization,
        ]

    @pyaedt_function_handler()
    def create(self) -> "SubstrateDataBlock":
        """Push the substrate data block to the active Circuit design.

        Returns
        -------
        SubstrateDataBlock
            The current instance (``self``) so the call can be chained.

        Examples
        --------
        >>> from ansys.aedt.core import Circuit
        >>> from ansys.aedt.core.modeler.circuits.primitives_circuit import SubstrateDataBlock
        >>> cir = Circuit()
        >>> sub = SubstrateDataBlock.microstrip(cir, "MySub", "10mil", 4.4, 0.02, "25mm")
        >>> sub.create()
        """
        from ansys.aedt.core.internal.errors import AEDTRuntimeError

        try:
            self._app.odata_block.AddSubstrateDataBlock(self._build_args())

            self._app.substrates[self.name] = self
        except Exception as e:  # pragma: no cover
            raise AEDTRuntimeError(f"Failed to create substrate data block '{self.name}': {e}") from e
        return self

    @pyaedt_function_handler()
    def update(self) -> bool:
        """Push the current state of this substrate data block to AEDT.

        Use this method to apply changes after setting one or more properties
        with :attr:`auto_update` set to ``False``, or to force a refresh at
        any time.

        Returns
        -------
        bool
            ``True`` when successful.

        References
        ----------
        >>> oModule.EditSubstrateDataBlock

        Examples
        --------
        Batch update several parameters at once:

        >>> sub = cir.substrates["MySub"]
        >>> sub.auto_update = False
        >>> sub.metal_material = "aluminum"
        >>> sub.metal_thickness = "1mil"
        >>> sub.roughness = "2pm"
        >>> sub.auto_update = True
        >>> sub.update()
        """
        from ansys.aedt.core.internal.errors import AEDTRuntimeError

        try:
            self._app.odata_block.EditSubstrateDataBlock(self.name, self._build_args())
        except Exception as e:  # pragma: no cover
            raise AEDTRuntimeError(f"Failed to update substrate data block '{self.name}': {e}") from e
        return True
