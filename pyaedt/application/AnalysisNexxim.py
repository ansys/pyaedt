# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 - 2024 ANSYS, Inc. and/or its affiliates.
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

from pyaedt.application.Analysis import Analysis
from pyaedt.generic.general_methods import pyaedt_function_handler
from pyaedt.generic.settings import settings
from pyaedt.modeler.circuits.object3dcircuit import CircuitComponent
from pyaedt.modules.Boundary import CurrentSinSource
from pyaedt.modules.Boundary import Excitations
from pyaedt.modules.Boundary import PowerIQSource
from pyaedt.modules.Boundary import PowerSinSource
from pyaedt.modules.Boundary import Sources
from pyaedt.modules.Boundary import VoltageDCSource
from pyaedt.modules.Boundary import VoltageFrequencyDependentSource
from pyaedt.modules.Boundary import VoltageSinSource
from pyaedt.modules.SetupTemplates import SetupKeys
from pyaedt.modules.SolveSetup import SetupCircuit


class FieldAnalysisCircuit(Analysis):
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
        self._internal_excitations = None
        self._internal_sources = None
        if not settings.lazy_load:
            self._modeler = self.modeler
            self._post = self.post

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
        if name in self.existing_analysis_setups:
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
        component : str or :class:`pyaedt.modeler.cad.object3d.circuit.CircuitComponent`
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
        :class:`pyaedt.modules.AdvancedPostProcessing.CircuitPostProcessor`
            PostProcessor object.
        """
        if self._post is None:
            self.logger.reset_timer()
            from pyaedt.modules.PostProcessor import CircuitPostProcessor

            self._post = CircuitPostProcessor(self)
            self.logger.info_timer("Post class has been initialized!")

        return self._post

    @property
    def existing_analysis_sweeps(self):
        """Analysis setups.

        References
        ----------

        >>> oModule.GetAllSolutionSetups"""
        return self.existing_analysis_setups

    @property
    def existing_analysis_setups(self):
        """Analysis setups.

        References
        ----------

        >>> oModule.GetAllSolutionSetups"""
        setups = self.oanalysis.GetAllSolutionSetups()
        return setups

    @property
    def nominal_sweep(self):
        """Nominal sweep."""
        if self.existing_analysis_setups:
            return self.existing_analysis_setups[0]
        else:
            return ""

    @property
    def modeler(self):
        """Modeler object."""
        if self._modeler is None:
            self.logger.reset_timer()
            from pyaedt.modeler.schematic import ModelerNexxim

            self._modeler = ModelerNexxim(self)
            self.logger.info_timer("Modeler class has been initialized!")

        return self._modeler

    @property
    def setup_names(self):
        """Setup names.

        References
        ----------

        >>> oModule.GetAllSolutionSetups"""
        return self.oanalysis.GetAllSolutionSetups()

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
        List of :class:`pyaedt.modules.Boundary.Sources`
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
        """List of port names.

        Returns
        -------
        list
            List of excitation names.

        References
        ----------

        >>> oModule.GetAllPorts
        """
        ports = [p.replace("IPort@", "").split(";")[0] for p in self.modeler.oeditor.GetAllPorts() if "IPort@" in p]
        return ports

    @property
    def excitation_objects(self):
        """List of port objects.

        Returns
        -------
        dict
            List of port objects.
        """
        props = {}
        if not self._internal_excitations:
            for port in self.excitations:
                props[port] = Excitations(self, port)
            self._internal_excitations = props
        else:
            props = self._internal_excitations
            if not sorted(list(props.keys())) == sorted(self.excitations):
                a = set(str(x) for x in props.keys())
                b = set(str(x) for x in self.excitations)
                if len(a) == len(b):
                    unmatched_new_name = list(b - a)[0]
                    unmatched_old_name = list(a - b)[0]
                    props[unmatched_new_name] = props[unmatched_old_name]
                    del props[unmatched_old_name]
                else:
                    if len(a) > len(b):
                        for old_port in props.keys():
                            if old_port not in self.excitations:
                                del props[old_port]
                                return props
                    else:
                        for new_port in self.excitations:
                            if new_port not in props.keys():
                                props[new_port] = Excitations(self, new_port)
        return props

    @pyaedt_function_handler(setupname="name")
    def get_setup(self, name):
        """Retrieve the setup from the current design.

        Parameters
        ----------
        name : str
            Name of the setup.

        Returns
        -------
        type
            Setup object.

        """
        setup = SetupCircuit(self, self.solution_type, name, is_new_setup=False)
        if setup.props:
            self.active_setup = name
        return setup

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
        :class:`pyaedt.modules.SolveSetup.SetupCircuit`
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

        >>> from pyaedt import Circuit
        >>> app = Circuit()
        >>> app.create_setup(name="Setup1",setup_type=app.SETUPS.NexximLNA,Data="LINC 0GHz 4GHz 501")
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
