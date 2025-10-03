# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 - 2025 ANSYS, Inc. and/or its affiliates.
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
import warnings

from ansys.aedt.core.application.analysis import Analysis
from ansys.aedt.core.base import PyAedtBase
from ansys.aedt.core.generic.configurations import ConfigurationsNexxim
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


class FieldAnalysisCircuit(Analysis, PyAedtBase):
    """FieldCircuitAnalysis class.

    This class is for circuit analysis setup in Nexxim.

    It is automatically initialized by a call from an application,
    such as HFSS or Q3D. See the application function for its
    parameter definitions.

    Parameters
    ----------
    """

    def __init__(
        self,
        application,
        projectname,
        designname,
        solution_type,
        setup_name=None,
        version=None,
        non_graphical=False,
        new_desktop=False,
        close_on_exit=False,
        student_version=False,
        machine="",
        port=0,
        aedt_process_id=None,
        remove_lock=False,
    ):
        Analysis.__init__(
            self,
            application,
            projectname,
            designname,
            solution_type,
            setup_name,
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
    def configurations(self):
        """Property to import and export configuration files.

        Returns
        -------
        :class:`ansys.aedt.core.generic.configurations.Configurations`
        """
        return self._configurations

    @pyaedt_function_handler(setupname="name")
    def delete_setup(self, name):
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

    @pyaedt_function_handler(component_name="component")
    def push_down(self, component):
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
    def pop_up(self):
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
    def post(self):
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
    def existing_analysis_setups(self):
        """Existing analysis setups.

        .. deprecated:: 0.15.0
            Use :func:`setup_names` from setup object instead.

        Returns
        -------
        list of str
            List of all analysis setups in the design.

        References
        ----------
        >>> oModule.GetSetups
        """
        msg = "`existing_analysis_setups` is deprecated. Use `setup_names` method from setup object instead."
        warnings.warn(msg, DeprecationWarning)
        return self.setup_names

    @property
    def modeler(self):
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
    def setup_names(self):
        """Setup names.

        References
        ----------
        >>> oModule.GetAllSolutionSetups
        """
        return [i.split(" : ")[0] for i in self.oanalysis.GetAllSolutionSetups()]

    @property
    def source_names(self):
        """Get all source names.

        Returns
        -------
        list
            List of source names.

        References
        ----------
        >>> oDesign.GetChildObject("Excitations").GetChildNames()
        """
        return list(self.odesign.GetChildObject("Excitations").GetChildNames())

    @property
    def source_objects(self):
        """Get all source objects.

        Returns
        -------
        list
            List of source objects.
        """
        return [self.sources[name] for name in self.sources]

    @property
    def sources(self):
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
    def excitations(self):
        """Get all excitation names.

        .. deprecated:: 0.15.0
           Use :func:`excitation_names` property instead.

        Returns
        -------
        list
            List of excitation names. Excitations with multiple modes will return one
            excitation for each mode.

        References
        ----------
        >>> oModule.GetExcitations
        """
        mess = "The property `excitations` is deprecated.\n"
        mess += " Use `app.excitation_names` directly."
        warnings.warn(mess, DeprecationWarning)
        return self.excitation_names

    @property
    def excitation_names(self):
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
    def design_excitations(self):
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

    @pyaedt_function_handler(setupname="name", setuptype="setup_type")
    def create_setup(self, name="MySetupAuto", setup_type=None, **kwargs):
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
