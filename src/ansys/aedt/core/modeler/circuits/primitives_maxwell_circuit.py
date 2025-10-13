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

from ansys.aedt.core.base import PyAedtBase
from ansys.aedt.core.generic.general_methods import pyaedt_function_handler
from ansys.aedt.core.modeler.circuits.primitives_circuit import CircuitComponents


class MaxwellCircuitComponents(CircuitComponents, PyAedtBase):
    """MaxwellCircuitComponents class.

    This class is for managing all circuit components for MaxwellCircuit.

    Examples
    --------
    Basic usage demonstrated with a MaxwellCircuit design:

    >>> from ansys.aedt.core import MaxwellCircuit
    >>> aedtapp = MaxwellCircuit()
    >>> prim = aedtapp.modeler.schematic
    """

    @property
    def design_libray(self):
        """Design Library."""
        return "Maxwell Circuit Elements"

    @property
    def tab_name(self):
        """Tab name."""
        return "PassedParameterTab"

    @pyaedt_function_handler()
    def __getitem__(self, partname):
        """Get object id from a string or integer.

        Parameters
        ----------
        partname : int or str
            ID or name of the object.

        Returns
        -------
        :class:`ansys.aedt.core.modeler.circuits.object_3d_circuit.CircuitComponent`
            Circuit Component Object.

        """
        if isinstance(partname, int):
            return self.components[partname]
        for el in self.components:
            if self.components[el].name == partname or self.components[el].composed_name == partname or el == partname:
                return self.components[el]

        return None

    def __init__(self, modeler):
        CircuitComponents.__init__(self, modeler)
        self._app = modeler._app
        self._modeler = modeler
        self._currentId = 0

    @pyaedt_function_handler(compname="name")
    def create_resistor(self, name=None, value=50, location=None, angle=0, use_instance_id_netlist=False):
        """Create a resistor.

        Parameters
        ----------
        name : str, optional
            Name of the resistor. The default is ``None``.
        value : float, optional
            Value for the resistor in Ohm. The default is ``50`` Ohm.
        location : list of float, optional
            Position on the X axis and Y axis. The default is ``None``.
        angle : float, optional
            Angle of rotation in degrees. The default is ``0``.
        use_instance_id_netlist : bool, optional
            Whether to use the instance ID in the net list or not. The default is ``False``.

        Returns
        -------
        :class:`ansys.aedt.core.modeler.circuits.object_3d_circuit.CircuitComponent`
            Circuit Component Object.

        References
        ----------
        >>> oEditor.CreateComponent

        Examples
        --------
        Create a resistor of 10 Ohm:

        >>> from ansys.aedt.core import MaxwellCircuit
        >>> circ = MaxwellCircuit()
        >>> circ.modeler.schematic.create_resistor(value=10)
        >>> circ.desktop_class.close_desktop()
        """
        if location is None:
            location = []

        id = self.create_component(
            name,
            component_library="Passive Elements",
            component_name="Res",
            location=location,
            angle=angle,
            use_instance_id_netlist=use_instance_id_netlist,
        )

        id.set_property("R", value)
        id.set_property("Name", name)
        return id

    @pyaedt_function_handler(compname="name")
    def create_inductor(self, name=None, value=50, location=None, angle=0, use_instance_id_netlist=False):
        """Create an inductor.

        Parameters
        ----------
        name : str, optional
            Name of the inductor. The default is ``None``.
        value : float, optional
            Value for the inductor in nH. The default is ``50`` nH.
        location : list of float, optional
            Position on the X axis and Y axis. The default is ``None``.
        angle : float, optional
            Angle rotation in degrees. The default is ``0``.
        use_instance_id_netlist : bool, optional
            Whether to use the instance ID in the net list or not. The default is ``False``.

        Returns
        -------
        :class:`ansys.aedt.core.modeler.circuits.object_3d_circuit.CircuitComponent`
            Circuit Component Object.

        References
        ----------
        >>> oEditor.CreateComponent

        Examples
        --------
        Create an inductor of 10 nH:

        >>> from ansys.aedt.core import MaxwellCircuit
        >>> circ = MaxwellCircuit()
        >>> circ.modeler.schematic.create_inductor(value=10)
        >>> circ.desktop_class.close_desktop()
        """
        if location is None:
            location = []

        id = self.create_component(
            name,
            component_library="Passive Elements",
            component_name="Ind",
            location=location,
            angle=angle,
            use_instance_id_netlist=use_instance_id_netlist,
        )

        id.set_property("L", value)
        id.set_property("Name", name)
        return id

    @pyaedt_function_handler(compname="name")
    def create_capacitor(self, name=None, value=50, location=None, angle=0, use_instance_id_netlist=False):
        """Create a capacitor.

        Parameters
        ----------
        name : str, optional
            Name of the capacitor. The default is ``None``.
        value : float, optional
            Value for the capacitor in pF. The default is ``50`` pF.
        location : list of float, optional
            Position on the X axis and Y axis.
        angle : float, optional
            Angle of rotation in degrees. The default is ``0``.
        use_instance_id_netlist : bool, optional
            Whether to use the instance ID in the net list or not. The default is ``False``.

        Returns
        -------
        :class:`ansys.aedt.core.modeler.circuits.object_3d_circuit.CircuitComponent`
            Circuit Component Object.

        References
        ----------
        >>> oEditor.CreateComponent

        Examples
        --------
        Create a capacitor of 10 pF:

        >>> from ansys.aedt.core import MaxwellCircuit
        >>> circ = MaxwellCircuit()
        >>> circ.modeler.schematic.create_capacitor(value=10)
        >>> circ.desktop_class.close_desktop()
        """
        if location is None:
            location = []
        id = self.create_component(
            name,
            component_library="Passive Elements",
            component_name="Cap",
            location=location,
            angle=angle,
            use_instance_id_netlist=use_instance_id_netlist,
        )

        id.set_property("C", value)
        id.set_property("Name", name)
        return id

    @pyaedt_function_handler(compname="name")
    def create_diode(self, name=None, location=None, angle=0, use_instance_id_netlist=False):
        """Create a diode.

        Parameters
        ----------
        name : str, optional
            Name of the diode. The default is ``None``.
        location : list of float, optional
            Position on the X axis and Y axis. The default is ``None``.
        angle : float, optional
            Angle of rotation in degrees. The default is ``0``.
        use_instance_id_netlist : bool, optional
            Whether to use the instance ID in the net list. The default is ``False``.

        Returns
        -------
        :class:`ansys.aedt.core.modeler.circuits.object_3d_circuit.CircuitComponent`
            Circuit Component Object.

        References
        ----------
        >>> oEditor.CreateComponent

        Examples
        --------
        Create a diode:

        >>> from ansys.aedt.core import MaxwellCircuit
        >>> circ = MaxwellCircuit()
        >>> circ.modeler.schematic.create_diode()
        >>> circ.desktop_class.close_desktop()
        """
        if location is None:
            location = []

        id = self.create_component(
            name,
            component_library="Passive Elements",
            component_name="DIODE",
            location=location,
            angle=angle,
            use_instance_id_netlist=use_instance_id_netlist,
        )

        id.set_property("Name", name)
        return id

    @pyaedt_function_handler(compname="name")
    def create_winding(self, name=None, location=None, angle=0, use_instance_id_netlist=False):
        """Create a winding linked to a Maxwell design.

        Parameters
        ----------
        name : str, optional
            Name of the winding. The default is ``None``.
        location : list of float, optional
            Position on the X axis and Y axis.
        angle : float, optional
            Angle rotation in degrees. The default is ``0``.
        use_instance_id_netlist : bool, optional
            Whether to use the instance ID in the net list. The default is ``False``.

        Returns
        -------
        :class:`ansys.aedt.core.modeler.circuits.object_3d_circuit.CircuitComponent`
            Circuit Component Object.

        References
        ----------
        >>> oEditor.CreateComponent

        Examples
        --------
        Create a winding:

        >>> from ansys.aedt.core import MaxwellCircuit
        >>> circ = MaxwellCircuit()
        >>> circ.modeler.schematic.create_winding(name="winding")
        >>> circ.desktop_class.close_desktop()
        """
        if location is None:
            location = []
        id = self.create_component(
            name,
            component_library="Dedicated Elements",
            component_name="Winding",
            location=location,
            angle=angle,
            use_instance_id_netlist=use_instance_id_netlist,
        )
        id.set_property("Name", name)
        return id
