"""This module contains the `Components` class.

"""
import math
import os
import re
import warnings

from pyaedt import _retry_ntimes
from pyaedt import generate_unique_name
from pyaedt.edb_core.EDB_Data import EDBComponent
from pyaedt.edb_core.general import convert_py_list_to_net_list
from pyaedt.edb_core.padstack import EdbPadstacks
from pyaedt.generic.constants import SourceType
from pyaedt.generic.general_methods import get_filename_without_extension
from pyaedt.generic.general_methods import is_ironpython
from pyaedt.generic.general_methods import pyaedt_function_handler
from pyaedt.modeler.GeometryOperators import GeometryOperators

try:
    import clr

    clr.AddReference("System")
    from System import String
except ImportError:
    if os.name != "posix":
        warnings.warn("This module requires PythonNet.")


def resistor_value_parser(RValue):
    """Convert a resistor value.

    Parameters
    ----------
    RValue : float
        Resistor value.

    Returns
    -------
    float
        Resistor value.

    """
    if isinstance(RValue, str):
        RValue = RValue.replace(" ", "")
        RValue = RValue.replace("meg", "m")
        RValue = RValue.replace("Ohm", "")
        RValue = RValue.replace("ohm", "")
        RValue = RValue.replace("k", "e3")
        RValue = RValue.replace("m", "e-3")
        RValue = RValue.replace("M", "e6")
    RValue = float(RValue)
    return RValue


class Components(object):
    """Manages EDB components and related methods.

    Parameters
    ----------
    edb_class : :class:`pyaedt.edb.Edb`

    Examples
    --------
    >>> from pyaedt import Edb
    >>> edbapp = Edb("myaedbfolder")
    >>> edbapp.core_components
    """

    def __init__(self, p_edb):
        self._pedb = p_edb
        self._cmp = {}
        self._res = {}
        self._cap = {}
        self._ind = {}
        self._ios = {}
        self._ics = {}
        self._others = {}
        self._pins = {}
        self._comps_by_part = {}
        self._init_parts()
        self._padstack = EdbPadstacks(self._pedb)

    @property
    def _logger(self):
        """Logger."""
        return self._pedb.logger

    @property
    def _edb(self):
        return self._pedb.edb

    @pyaedt_function_handler()
    def _init_parts(self):
        a = self.components
        a = self.resistors
        a = self.ICs
        a = self.Others
        a = self.inductors
        a = self.IOs
        a = self.components_by_partname
        return True

    @property
    def _builder(self):
        return self._pedb.builder

    def _get_edb_value(self, value):
        return self._pedb.edb_value(value)

    @property
    def _edbutils(self):
        return self._pedb.edbutils

    @property
    def _active_layout(self):
        return self._pedb.active_layout

    @property
    def _cell(self):
        return self._pedb.cell

    @property
    def _db(self):
        return self._pedb.db

    @property
    def _components_methods(self):
        return self._pedb.edblib.Layout.ComponentsMethods

    @property
    def components(self):
        """Component setup information.

        Returns
        -------
        dict[str, :class:`pyaedt.edb_core.EDB_Data.EDBComponent`]
            Default dictionary for the EDB component.

        Examples
        --------

        >>> from pyaedt import Edb
        >>> edbapp = Edb("myaedbfolder")
        >>> edbapp.core_components.components

        """
        if not self._cmp:
            self.refresh_components()
        return self._cmp

    @pyaedt_function_handler()
    def refresh_components(self):
        """Refresh the component dictionary."""
        self._cmp = {}
        self._logger.info("Refreshing the Components dictionary.")
        if self._active_layout:
            for cmp in self._active_layout.Groups:
                if cmp.GetType().ToString() == "Ansys.Ansoft.Edb.Cell.Hierarchy.Component":
                    self._cmp[cmp.GetName()] = EDBComponent(self, cmp)

    @property
    def resistors(self):
        """Resistors.

        Returns
        -------
        dict[str, :class:`pyaedt.edb_core.EDB_Data.EDBComponent`]
            Dictionary of resistors.

        Examples
        --------

        >>> from pyaedt import Edb
        >>> edbapp = Edb("myaedbfolder")
        >>> edbapp.core_components.resistors
        """
        self._res = {}
        for el, val in self.components.items():
            if val.type == "Resistor":
                self._res[el] = val
        return self._res

    @property
    def capacitors(self):
        """Capacitors.

        Returns
        -------
        dict[str, :class:`pyaedt.edb_core.EDB_Data.EDBComponent`]
            Dictionary of capacitors.

        Examples
        --------

        >>> from pyaedt import Edb
        >>> edbapp = Edb("myaedbfolder")
        >>> edbapp.core_components.capacitors
        """
        self._cap = {}
        for el, val in self.components.items():
            if val.type == "Capacitor":
                self._cap[el] = val
        return self._cap

    @property
    def inductors(self):
        """Inductors.

        Returns
        -------
        dict[str, :class:`pyaedt.edb_core.EDB_Data.EDBComponent`]
            Dictionary of inductors.

        Examples
        --------

        >>> from pyaedt import Edb
        >>> edbapp = Edb("myaedbfolder")
        >>> edbapp.core_components.inductors

        """
        self._ind = {}
        for el, val in self.components.items():
            if val.type == "Inductor":
                self._ind[el] = val
        return self._ind

    @property
    def ICs(self):
        """Integrated circuits.

        Returns
        -------
        dict[str, :class:`pyaedt.edb_core.EDB_Data.EDBComponent`]
            Dictionary of integrated circuits.

        Examples
        --------

        >>> from pyaedt import Edb
        >>> edbapp = Edb("myaedbfolder")
        >>> edbapp.core_components.ICs

        """
        self._ics = {}
        for el, val in self.components.items():
            if val.type == "IC":
                self._ics[el] = val
        return self._ics

    @property
    def IOs(self):
        """Circuit inupts and outputs.

        Returns
        -------
        dict[str, :class:`pyaedt.edb_core.EDB_Data.EDBComponent`]
            Dictionary of circuit inputs and outputs.

        Examples
        --------

        >>> from pyaedt import Edb
        >>> edbapp = Edb("myaedbfolder")
        >>> edbapp.core_components.IOs

        """
        self._ios = {}
        for el, val in self.components.items():
            if val.type == "IO":
                self._ios[el] = val
        return self._ios

    @property
    def Others(self):
        """Other core components.

        Parameters
        ----------

        Returns
        -------
        dict[str, :class:`pyaedt.edb_core.EDB_Data.EDBComponent`]
            Dictionary of other core components.

        Examples
        --------

        >>> from pyaedt import Edb
        >>> edbapp = Edb("myaedbfolder")
        >>> edbapp.core_components.others

        """
        self._others = {}
        for el, val in self.components.items():
            if val.type == "Other":
                self._others[el] = val
        return self._others

    @property
    def components_by_partname(self):
        """Components by part name.

        Returns
        -------
        dict
            Dictionary of components by part name.

        Examples
        --------

        >>> from pyaedt import Edb
        >>> edbapp = Edb("myaedbfolder")
        >>> edbapp.core_components.components_by_partname

        """
        self._comps_by_part = {}
        for el, val in self.components.items():
            if val.partname in self._comps_by_part.keys():
                self._comps_by_part[val.partname].append(val)
            else:
                self._comps_by_part[val.partname] = [val]
        return self._comps_by_part

    @pyaedt_function_handler()
    def get_component_list(self):
        """Retrieve conponent setup information.

        Returns
        -------
        list
            List of component setup information.

        """
        cmp_setup_info_list = self._edbutils.ComponentSetupInfo.GetFromLayout(self._active_layout)
        cmp_list = []
        for comp in cmp_setup_info_list:
            cmp_list.append(comp)
        return cmp_list

    @pyaedt_function_handler()
    def get_component_by_name(self, name):
        """Retrieve a component by name.

        Parameters
        ----------
        name : str
            Name of the component.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.

        """
        edbcmp = self._edb.Cell.Hierarchy.Component.FindByName(self._active_layout, name)
        if edbcmp is not None:
            return edbcmp
        else:
            pass

    @pyaedt_function_handler()
    def get_components_from_nets(self, netlist=None):
        """Retrieve components from a net list.

        Parameters
        ----------
        netlist : str, optional
            Name of the net list. The default is ``None``.

        Returns
        -------
        list
            List of components that belong to the signal nets.

        """
        cmp_list = []
        if isinstance(netlist, str):
            netlist = [netlist]
        components = list(self.components.keys())
        for refdes in components:
            cmpnets = self._cmp[refdes].nets
            if set(cmpnets).intersection(set(netlist)):
                cmp_list.append(refdes)
        return cmp_list

    @pyaedt_function_handler()
    def _get_edb_pin_from_pin_name(self, cmp, pin):
        if not isinstance(cmp, self._edb.Cell.Hierarchy.Component):
            return False
        if not isinstance(pin, str):
            pin = pin.GetName()
        pins = self.get_pin_from_component(component=cmp, pinName=pin)
        if pins:
            return pins[0]
        return False

    @pyaedt_function_handler()
    def get_component_placement_vector(
        self,
        mounted_component,
        hosting_component,
        mounted_component_pin1,
        mounted_component_pin2,
        hosting_component_pin1,
        hosting_component_pin2,
        flipped=False,
    ):
        """Get the placement vector between 2 components.

        Parameters
        ----------
        mounted_component : `edb.Cell.Hierarchy.Component`
            Mounted component name.
        hosting_component : `edb.Cell.Hierarchy.Component`
            Hosting component name.
        mounted_component_pin1 : str
            Mounted component Pin 1 name.
        mounted_component_pin2 : str
            Mounted component Pin 2 name.
        hosting_component_pin1 : str
            Hosted component Pin 1 name.
        hosting_component_pin2 : str
            Hosted component Pin 2 name.
        flipped : bool, optional
            Either if the mounted component will be flipped or not.

        Returns
        -------
        tuple
            Tuple of Vector offset, rotation and solder height.

        Examples
        --------
        >>> edb1 = Edb(edbpath=targetfile1,  edbversion="2021.2")
        >>> hosting_cmp = edb1.core_components.get_component_by_name("U100")
        >>> mounted_cmp = edb2.core_components.get_component_by_name("BGA")
        >>> vector, rotation, solder_ball_height = edb1.core_components.get_component_placement_vector(
        ...                                             mounted_component=mounted_cmp,
        ...                                             hosting_component=hosting_cmp,
        ...                                             mounted_component_pin1="A12",
        ...                                             mounted_component_pin2="A14",
        ...                                             hosting_component_pin1="A12",
        ...                                             hosting_component_pin2="A14")
        """
        m_pin1_pos = [0.0, 0.0]
        m_pin2_pos = [0.0, 0.0]
        h_pin1_pos = [0.0, 0.0]
        h_pin2_pos = [0.0, 0.0]
        if not isinstance(mounted_component, self._edb.Cell.Hierarchy.Component):
            return False
        if not isinstance(hosting_component, self._edb.Cell.Hierarchy.Component):
            return False

        if mounted_component_pin1:
            m_pin1 = self._get_edb_pin_from_pin_name(mounted_component, mounted_component_pin1)
            m_pin1_pos = self.get_pin_position(m_pin1)
        if mounted_component_pin2:
            m_pin2 = self._get_edb_pin_from_pin_name(mounted_component, mounted_component_pin2)
            m_pin2_pos = self.get_pin_position(m_pin2)

        if hosting_component_pin1:
            h_pin1 = self._get_edb_pin_from_pin_name(hosting_component, hosting_component_pin1)
            h_pin1_pos = self.get_pin_position(h_pin1)

        if hosting_component_pin2:
            h_pin2 = self._get_edb_pin_from_pin_name(hosting_component, hosting_component_pin2)
            h_pin2_pos = self.get_pin_position(h_pin2)
        #
        vector = [h_pin1_pos[0] - m_pin1_pos[0], h_pin1_pos[1] - m_pin1_pos[1]]
        vector1 = GeometryOperators.v_points(m_pin1_pos, m_pin2_pos)
        vector2 = GeometryOperators.v_points(h_pin1_pos, h_pin2_pos)
        multiplier = 1
        if flipped:
            multiplier = -1
        vector1[1] = multiplier * vector1[1]

        rotation = GeometryOperators.v_angle_sign_2D(vector1, vector2, False)
        if rotation != 0.0:
            layinst = mounted_component.GetLayout().GetLayoutInstance()
            cmpinst = layinst.GetLayoutObjInstance(mounted_component, None)
            center = cmpinst.GetCenter()
            center_double = [center.X.ToDouble(), center.Y.ToDouble()]
            vector_center = GeometryOperators.v_points(center_double, m_pin1_pos)
            x_v2 = vector_center[0] * math.cos(rotation) + multiplier * vector_center[1] * math.sin(rotation)
            y_v2 = -1 * vector_center[0] * math.sin(rotation) + multiplier * vector_center[1] * math.cos(rotation)
            new_vector = [x_v2 + center_double[0], y_v2 + center_double[1]]
            vector = [h_pin1_pos[0] - new_vector[0], h_pin1_pos[1] - new_vector[1]]

        if vector:
            solder_ball_height = self.get_solder_ball_height(mounted_component)
            return True, vector, rotation, solder_ball_height
        self._logger.warning("Failed to compute vector.")
        return False, [0, 0], 0, 0

    @pyaedt_function_handler()
    def get_solder_ball_height(self, cmp):
        """Get component solder ball height.

        Parameters
        ----------
        cmp : str or self._edb.Cell.Hierarchy.Component
            EDB component or str component name.

        Returns
        -------
        double, bool
            Salder ball height vale, ``False`` when failed.

        """
        if cmp is not None:
            if not (isinstance(cmp, self._edb.Cell.Hierarchy.Component)):
                cmp = self.get_component_by_name(cmp)
            cmp_prop = cmp.GetComponentProperty().Clone()
            return cmp_prop.GetSolderBallProperty().GetHeight()
        return False

    @pyaedt_function_handler()
    def create_port_on_component(
        self, component, net_list, port_type=SourceType.CoaxPort, do_pingroup=True, reference_net="gnd"
    ):
        """Create ports on given component.

        Parameters
        ----------
        component : str or self._edb.Cell.Hierarchy.Component
            EDB component or str component name.

        net_list : str or list of string.
            The list of nets where ports have to be created on the component.
            If net is not part of the component this one will be skipped.

        port_type : SourceType enumerator, CoaxPort or CircPort
            Define the type of port to be created. CoaxPort will auto generate solder balls.
            CircPort will generate circuit ports on pins belonging to the net list.

        do_pingroup : bool
            True activate pingroup during port creation (only used with combination of CoaxPort),
            False will take the closest reference pin and generate one port per signal pin.

        refnet : string or list of string.
            list of the reference net.

        Returns
        -------
        double, bool
            Salder ball height vale, ``False`` when failed.

        Examples
        --------

        >>> from pyaedt import Edb
        >>> edbapp = Edb("myaedbfolder")
        >>> net_list = ["M_DQ<1>", "M_DQ<2>", "M_DQ<3>", "M_DQ<4>", "M_DQ<5>"]
        >>> edbapp.core_components.create_port_on_component(component="U2A5", net_list=net_list,
        ...                                                 port_type=SourceType.CoaxPort,
        ...                                                 do_pingroup=False, reference_net="GND")

        """
        if isinstance(component, self._edb.Cell.Hierarchy.Component):
            cmp = component.GetName()
        if not isinstance(net_list, list):
            net_list = [net_list]
        for net in net_list:
            if not isinstance(net, str):
                try:
                    net_name = net.GetName()
                    if net_name != "":
                        net_list.append(net_name)
                except:
                    pass
        if reference_net in net_list:
            net_list.remove(reference_net)
        cmp_pins = self.get_pin_from_component(component, net_list)
        if len(cmp_pins) == 0:
            return False
        pin_layers = cmp_pins[0].GetPadstackDef().GetData().GetLayerNames()

        if port_type == SourceType.CoaxPort:
            pad_params = self._padstack.get_pad_parameters(pin=cmp_pins[0], layername=pin_layers[0], pad_type=0)
            sball_diam = min([self._get_edb_value(val).ToDouble() for val in pad_params[1]])
            sb_height = sball_diam
            self.set_solder_ball(component, sb_height, sball_diam)
            for pin in cmp_pins:
                self._padstack.create_coax_port(pin)

        elif port_type == SourceType.CircPort:
            ref_pins = self.get_pin_from_component(component, reference_net)
            if do_pingroup:
                pingroups = []
                if len(ref_pins) == 1:
                    ref_pin_group_term = self._create_terminal(ref_pins[0])
                else:
                    ref_pin_group = self.create_pingroup_from_pins(ref_pins)
                    ref_pin_group_term = self._create_pin_group_terminal(ref_pin_group[1])
                    if not ref_pin_group[0]:
                        return False
                ref_pin_group_term.SetBoundaryType(self._edb.Cell.Terminal.BoundaryType.PortBoundary)
                ref_pin_group_term.SetIsCircuitPort(True)
                for net in net_list:
                    pins = [pin for pin in cmp_pins if pin.GetNet().GetName() == net]
                    pin_group = self.create_pingroup_from_pins(pins)
                    if pin_group[0]:
                        pingroups.append(pin_group[1])
                pg_terminal = []
                for pg in pingroups:
                    pg_term = self._create_pin_group_terminal(pg)
                    pg_terminal.append(pg_term)
                for term in pg_terminal:
                    term.SetBoundaryType(self._edb.Cell.Terminal.BoundaryType.PortBoundary)
                    term.SetIsCircuitPort(True)
                    term.SetReferenceTerminal(ref_pin_group_term)
            else:
                for net in net_list:
                    pins = [pin for pin in cmp_pins if pin.GetNet().GetName().lower() == net]
                    for pin in pins:
                        ref_pin = self._get_closest_pin_from(pin, ref_pins)
                        ref_pin_term = self._create_terminal(ref_pin)
                        term = self._create_terminal(pin)
                        ref_pin_term.SetBoundaryType(self._edb.Cell.Terminal.BoundaryType.PortBoundary)
                        ref_pin_term.SetIsCircuitPort(True)
                        term.SetBoundaryType(self._edb.Cell.Terminal.BoundaryType.PortBoundary)
                        term.SetIsCircuitPort(True)
                        term.SetReferenceTerminal(ref_pin_term)
        return True

    @pyaedt_function_handler()
    def _create_terminal(self, pin):
        """Create terminal on component pin.

        Parameters
        ----------
        pin : Edb padstack instance.

        Returns
        -------
        Edb terminal.
        """

        res, pin_position, pin_rot = pin.GetPositionAndRotation(
            self._edb.Geometry.PointData(self._get_edb_value(0.0), self._get_edb_value(0.0)), 0.0
        )
        if not is_ironpython:
            res, from_layer, to_layer = pin.GetLayerRange(None, None)
        else:
            res, from_layer, to_layer = pin.GetLayerRange()
        cmp_name = pin.GetComponent().GetName()
        net_name = pin.GetNet().GetName()
        pin_name = pin.GetName()
        term_name = "{}_{}_{}".format(cmp_name, net_name, pin_name)
        term = self._edb.Cell.Terminal.PointTerminal.Create(
            pin.GetLayout(), pin.GetNet(), term_name, pin_position, from_layer
        )
        return term

    @pyaedt_function_handler()
    def _get_closest_pin_from(self, pin, ref_pinlist):
        """Returns the closest pin from given pin among the list of reference pins.

        Parameters
        ----------
        pin : Edb padstack instance.

        ref_pinlist : list of reference edb pins.

        Returns
        -------
        Edb pin.

        """
        res, pin_position, pin_rot = pin.GetPositionAndRotation(
            self._edb.Geometry.PointData(self._get_edb_value(0.0), self._get_edb_value(0.0)), 0.0
        )
        distance = 1e3
        closest_pin = ref_pinlist[0]
        for ref_pin in ref_pinlist:
            res, ref_pin_position, ref_pin_rot = ref_pin.GetPositionAndRotation(
                self._edb.Geometry.PointData(self._get_edb_value(0.0), self._get_edb_value(0.0)), 0.0
            )
            temp_distance = pin_position.Distance(ref_pin_position)
            if temp_distance < distance:
                distance = temp_distance
                closest_pin = ref_pin
        return closest_pin

    @pyaedt_function_handler()
    def _create_pin_group_terminal(self, pingroup, isref=False):
        """Creates edb pin group terminal from given edb pin group.

        Parameters
        ----------
        pingroup : Edb pin group.

        isref : bool

        Returns
        -------
        Edb pin group terminal.
        """

        layout = pingroup.GetLayout()
        cmp_name = pingroup.GetComponent().GetName()
        net_name = pingroup.GetNet().GetName()
        term_name = pingroup.GetUniqueName(layout, "Pingroup_{0}_{1}".format(cmp_name, net_name))
        pingroup_term = self._edb.Cell.Terminal.PinGroupTerminal.Create(
            self._active_layout, pingroup.GetNet(), term_name, pingroup, isref
        )
        return pingroup_term

    @pyaedt_function_handler()
    def _is_top_component(self, cmp):
        """Test the component placment layer.

        Parameters
        ----------
        cmp : self._edb.Cell.Hierarchy.Component
             Edb component.

        Returns
        -------
        bool
            ``True`` when component placed on top layer, ``False`` on bottom layer.


        """
        signal_layers = cmp.GetLayout().GetLayerCollection().Layers(self._edb.Cell.LayerTypeSet.SignalLayerSet)
        if cmp.GetPlacementLayer() == signal_layers[0]:
            return True
        else:
            return False

    @pyaedt_function_handler()
    def create_component_from_pins(self, pins, component_name, placement_layer=None):
        """Create a component from pins.

        Parameters
        ----------
        pins : list
            List of EDB core pins.
        component_name : str
            Name of the reference designator for the component.
        placement_layer : str
            Name of the layer used for placing the component.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.

        Examples
        --------

        >>> from pyaedt import Edb
        >>> edbapp = Edb("myaedbfolder")
        >>> pins = edbapp.core_components.get_pin_from_component("A1")
        >>> edbapp.core_components.create_component_from_pins(pins, "A1New")

        """
        # try:
        new_cmp = self._edb.Cell.Hierarchy.Component.Create(self._active_layout, component_name, component_name)
        new_group = self._edb.Cell.Hierarchy.Group.Create(self._active_layout, component_name)
        new_cmp.SetGroup(new_group)
        for pin in pins:
            pin.SetIsLayoutPin(True)
            if is_ironpython:
                test = new_group.AddMember(pin)
            else:
                if not self._components_methods.AddPinToGroup(new_group, pin):
                    self._logger.error(
                        "Failed to add pin {} to the group {}".format(pin.GetName(), new_group.GetName())
                    )
        if not placement_layer:
            new_cmp_layer_name = pins[0].GetPadstackDef().GetData().GetLayerNames()[0]
        else:
            new_cmp_layer_name = placement_layer
        new_cmp_placement_layer = self._edb.Cell.Layer.FindByName(
            self._active_layout.GetLayerCollection(), new_cmp_layer_name
        )
        new_cmp.SetPlacementLayer(new_cmp_placement_layer)
        # cmp_transform = System.Activator.CreateInstance(self._edb.Utility.)
        # new_cmp.SetTransform(cmp_transform)
        return (True, new_cmp)
        # except:
        #    return (False, None)

    @pyaedt_function_handler()
    def set_component_model(self, componentname, model_type="Spice", modelpath=None, modelname=None):
        """Assign a Spice or Touchstone model to a component.

        Parameters
        ----------
        componentname : str
            Name of the component.
        model_type : str, optional
            Type of the model. Options are ``"Spice"`` and
            ``"Touchstone"``.  The default is ``"Spice"``.
        modelpath : str, optional
            Full path to the model file. The default is ``None``.
        modelname : str, optional
            Name of the model. The default is ``None``.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.

        Examples
        --------

        >>> from pyaedt import Edb
        >>> edbapp = Edb("myaedbfolder")
        >>> edbapp.core_components.set_component_model("A1", model_type="Spice",
        ...                                            modelpath="pathtospfile",
        ...                                            modelname="spicemodelname")

        """
        if not modelname:
            modelname = get_filename_without_extension(modelpath)
        edbComponent = self.get_component_by_name(componentname)
        if str(edbComponent.EDBHandle) == "0":
            return False
        edbRlcComponentProperty = edbComponent.GetComponentProperty().Clone()

        componentPins = self.get_pin_from_component(componentname)
        componentNets = self.get_nets_from_pin_list(componentPins)
        pinNumber = len(componentPins)
        if model_type == "Spice":
            with open(modelpath, "r") as f:
                for line in f:
                    if "subckt" in line.lower():
                        pinNames = [i.strip() for i in re.split(" |\t", line) if i]
                        pinNames.remove(pinNames[0])
                        pinNames.remove(pinNames[0])
                        break
            if len(pinNames) == pinNumber:
                spiceMod = self._edb.Cell.Hierarchy.SPICEModel()
                spiceMod.SetModelPath(modelpath)
                spiceMod.SetModelName(modelname)
                terminal = 1
                for pn in pinNames:
                    spiceMod.AddTerminalPinPair(pn, str(terminal))
                    terminal += 1

                edbRlcComponentProperty.SetModel(spiceMod)
                if not edbComponent.SetComponentProperty(edbRlcComponentProperty):
                    self._logger.error("Error Assigning the Touchstone model")
                    return False
            else:
                self._logger.error("Wrong number of Pins")
                return False

        elif model_type == "Touchstone":

            nPortModelName = modelname
            edbComponentDef = edbComponent.GetComponentDef()
            nPortModel = self._edb.Definition.NPortComponentModel.FindByName(edbComponentDef, nPortModelName)
            if nPortModel.IsNull():
                nPortModel = self._edb.Definition.NPortComponentModel.Create(nPortModelName)
                nPortModel.SetReferenceFile(modelpath)
                edbComponentDef.AddComponentModel(nPortModel)

            sParameterMod = self._edb.Cell.Hierarchy.SParameterModel()
            sParameterMod.SetComponentModelName(nPortModel)
            gndnets = filter(lambda x: "gnd" in x.lower(), componentNets)
            if len(gndnets) > 0:

                net = gndnets[0]
            else:
                net = componentNets[len(componentNets) - 1]
            sParameterMod.SetReferenceNet(net)
            edbRlcComponentProperty.SetModel(sParameterMod)
            if not edbComponent.SetComponentProperty(edbRlcComponentProperty):
                self._logger.error("Error Assigning the Touchstone model")
                return False
        return True

    @pyaedt_function_handler()
    def create_pingroup_from_pins(self, pins, group_name=None):
        """Create a pin group on a component.

        Parameters
        ----------
        pins : list
            List of EDB core pins.
        group_name : str, optional
            Name for the group. The default is ``None``, in which case
            a default name is assigned as follows: ``[component Name] [NetName]``.

        Returns
        -------
        tuple
            (bool, pingroup)

        Examples
        --------
        >>> from pyaedt import Edb
        >>> edbapp = Edb("myaedbfolder")
        >>> edbapp.core_components.create_pingroup_from_pins(gndpinlist, "MyGNDPingroup")

        """
        if len(pins) < 1:
            self._logger.error("No pins specified for pin group %s", group_name)
            return (False, None)
        if group_name is None:
            cmp_name = pins[0].GetComponent().GetName()
            net_name = pins[0].GetNet().GetName()
            group_name = generate_unique_name("{}_{}_".format(cmp_name, net_name), n=3)
        pingroup = _retry_ntimes(
            10,
            self._edb.Cell.Hierarchy.PinGroup.Create,
            self._active_layout,
            group_name,
            convert_py_list_to_net_list(pins),
        )
        if pingroup.IsNull():
            return (False, None)
        else:
            pingroup.SetNet(pins[0].GetNet())
            return (True, pingroup)

    @pyaedt_function_handler()
    def delete_single_pin_rlc(self):
        """Delete all RLC components with a single pin.

        Returns
        -------
        list
            List of deleted RLC components.


        Examples
        --------

        >>> from pyaedt import Edb
        >>> edbapp = Edb("myaedbfolder")
        >>> list_of_deleted_rlcs = edbapp.core_components.delete_single_pin_rlc()
        >>> print(list_of_deleted_rlcs)

        """
        deleted_comps = []
        for comp, val in self.components.items():
            if val.numpins < 2 and (val.type == "Resistor" or val.type == "Capacitor" or val.type == "Inductor"):
                edb_cmp = self.get_component_by_name(comp)
                if edb_cmp is not None:
                    edb_cmp.Delete()
                    deleted_comps.append(comp)
                    self._pedb._logger.info("Component {} deleted".format(comp))
        for el in deleted_comps:
            del self.components[el]
        return deleted_comps

    @pyaedt_function_handler()
    def delete_component(self, component_name):
        """Delete a component.

        Parameters
        ----------
        component_name : str
            Name of the component.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.

        Examples
        --------

        >>> from pyaedt import Edb
        >>> edbapp = Edb("myaedbfolder")
        >>> edbapp.core_components.delete_component("A1")

        """
        edb_cmp = self.get_component_by_name(component_name)
        if edb_cmp is not None:
            edb_cmp.Delete()
            if edb_cmp in list(self.components.keys()):
                del self.components[edb_cmp]
            return True
        return False

    @pyaedt_function_handler()
    def disable_rlc_component(self, component_name):
        """Disable a RLC component.

        Parameters
        ----------
        component_name : str
            Name of the RLC component.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.

        Examples
        --------

        >>> from pyaedt import Edb
        >>> edbapp = Edb("myaedbfolder")
        >>> edbapp.core_components.disable_rlc_component("A1")

        """
        edb_cmp = self.get_component_by_name(component_name)
        if edb_cmp is not None:
            rlc_property = edb_cmp.GetComponentProperty().Clone()
            pin_pair_model = rlc_property.GetModel().Clone()
            pprlc = pin_pair_model.GetPinPairRlc(list(pin_pair_model.PinPairs)[0])
            pprlc.CEnabled = False
            pprlc.LEnabled = False
            pprlc.REnabled = False
            pin_pair_model.SetPinPairRlc(list(pin_pair_model.PinPairs)[0], pprlc)
            rlc_property.SetModel(pin_pair_model)
            edb_cmp.SetComponentProperty(rlc_property)
            return True
        return False

    @pyaedt_function_handler()
    def set_solder_ball(self, component="", sball_diam="100um", sball_height="150um"):
        """Set cylindrical solder balls on a given component.

        Parameters
        ----------
        componentname : str or EDB component
            Name of the discret component.

        sball_diam  : str, float
            Diameter of the solder ball.

        sball_height : str, float
            Height of the solder ball.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.

        Examples
        --------

        >>> from pyaedt import Edb
        >>> edbapp = Edb("myaedbfolder")
        >>> edbapp.core_components.set_solder_ball("A1")

        """
        if not isinstance(component, self._edb.Cell.Hierarchy.Component):
            edb_cmp = self.get_component_by_name(component)
        else:
            edb_cmp = component
        if edb_cmp:
            cmp_type = edb_cmp.GetComponentType()
            if cmp_type == self._edb.Definition.ComponentType.IC:
                ic_cmp_property = edb_cmp.GetComponentProperty().Clone()
                ic_die_prop = ic_cmp_property.GetDieProperty().Clone()
                ic_die_prop.SetType(self._edb.Definition.DieType.FlipChip)
                ic_die_prop.SetOrientation(self._edb.Definition.DieOrientation.ChipDown)
                ic_cmp_property.SetDieProperty(ic_die_prop)

                ic_solder_ball_prop = ic_cmp_property.GetSolderBallProperty().Clone()
                ic_solder_ball_prop.SetDiameter(self._get_edb_value(sball_diam), self._get_edb_value(sball_diam))
                ic_solder_ball_prop.SetHeight(self._get_edb_value(sball_height))
                ic_solder_ball_prop.SetShape(self._edb.Definition.SolderballShape.Cylinder)
                ic_cmp_property.SetSolderBallProperty(ic_solder_ball_prop)

                ic_port_prop = ic_cmp_property.GetPortProperty().Clone()
                ic_port_prop.SetReferenceSizeAuto(True)
                ic_cmp_property.SetPortProperty(ic_port_prop)
                edb_cmp.SetComponentProperty(ic_cmp_property)
                return True

            elif cmp_type == self._edb.Definition.ComponentType.IO:
                io_cmp_prop = edb_cmp.GetComponentProperty().Clone()
                io_solder_ball_prop = io_cmp_prop.GetSolderBallProperty().Clone()
                io_solder_ball_prop.SetDiameter(self._get_edb_value(sball_diam), self._get_edb_value(sball_diam))
                io_solder_ball_prop.SetHeight(self._get_edb_value(sball_height))
                io_solder_ball_prop.SetShape(self._edb.Definition.SolderballShape.Cylinder)
                io_cmp_prop.SetSolderBallProperty(io_solder_ball_prop)
                io_port_prop = io_cmp_prop.GetPortProperty().Clone()
                io_port_prop.SetReferenceSizeAuto(True)
                io_cmp_prop.SetPortProperty(io_port_prop)
                edb_cmp.SetComponentProperty(io_cmp_prop)
                return True
            elif cmp_type == self._edb.Definition.ComponentType.Other:
                other_cmp_prop = edb_cmp.GetComponentProperty().Clone()
                other_solder_ball_prop = other_cmp_prop.GetSolderBallProperty().Clone()
                other_solder_ball_prop.SetDiameter(self._get_edb_value(sball_diam), self._get_edb_value(sball_diam))
                other_solder_ball_prop.SetHeight(self._get_edb_value(sball_height))
                other_solder_ball_prop.SetShape(self._edb.Definition.SolderballShape.Cylinder)
                other_cmp_prop.SetSolderBallProperty(other_solder_ball_prop)
                other_port_prop = other_cmp_prop.GetPortProperty().Clone()
                other_port_prop.SetReferenceSizeAuto(True)
                other_cmp_prop.SetPortProperty(other_port_prop)
                edb_cmp.SetComponentProperty(other_port_prop)
            else:
                return False
        else:
            return False

    @pyaedt_function_handler()
    def set_component_rlc(self, componentname, res_value=None, ind_value=None, cap_value=None, isparallel=False):
        """Update values for an RLC component.

        Parameters
        ----------
        componentname :
            Name of the RLC component.
        res_value : float, optional
            Resistance value. The default is ``None``.
        ind_value : float, optional
            Inductor value.  The default is ``None``.
        cap_value : float optional
            Capacitor value.  The default is ``None``.
        isparallel : bool, optional
            Whether the RLC component is parallel. The default is ``False``.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.

        Examples
        --------

        >>> from pyaedt import Edb
        >>> edbapp = Edb("myaedbfolder")
        >>> edbapp.core_components.set_component_rlc(
        ...     "R1", res_value=50, ind_value=1e-9, cap_value=1e-12, isparallel=False
        ... )

        """
        edbComponent = self.get_component_by_name(componentname)
        componentType = edbComponent.GetComponentType()
        edbRlcComponentProperty = self._edb.Cell.Hierarchy.RLCComponentProperty()
        componentPins = self.get_pin_from_component(componentname)
        pinNumber = len(componentPins)
        if pinNumber == 2:
            fromPin = componentPins[0]
            toPin = componentPins[1]
            if res_value is None and ind_value is None and cap_value is None:
                return False
            rlc = self._edb.Utility.Rlc()
            rlc.IsParallel = isparallel
            if res_value is not None:
                rlc.REnabled = True
                rlc.R = self._get_edb_value(res_value)
            if ind_value is not None:
                rlc.LEnabled = True
                rlc.L = self._get_edb_value(ind_value)
            if cap_value is not None:
                rlc.CEnabled = True
                rlc.C = self._get_edb_value(cap_value)
            pinPair = self._edb.Utility.PinPair(fromPin.GetName(), toPin.GetName())
            rlcModel = self._edb.Cell.Hierarchy.PinPairModel()
            rlcModel.SetPinPairRlc(pinPair, rlc)
            if not edbRlcComponentProperty.SetModel(rlcModel) or not edbComponent.SetComponentProperty(
                edbRlcComponentProperty
            ):
                self._logger.error("Failed to set RLC model on component")
                return False
        else:
            self._logger.warning(
                "Component %s has not been assigned because either it is not present in the layout "
                "or it contains a number of pins not equal to 2",
                componentname,
            )
            return False
        self._logger.warning("RLC properties for Component %s has been assigned.", componentname)
        return True

    @pyaedt_function_handler()
    def update_rlc_from_bom(
        self, bom_file, delimiter=";", valuefield="Func des", comptype="Prod name", refdes="Pos / Place"
    ):
        """Update the EDC core component values (RLCs) with values coming from a BOM file.

        Parameters
        ----------
        bom_file : str
            Full path to the BOM file, which is a delimited text file.
            Header values needed inside the BOM reader must
            be explicitly set if different from the defaults.
        delimiter : str, optional
            Value to use for the delimiter. The default is ``";"``.
        valuefield : str, optional
            Field header containing the value of the component. The default is ``"Func des"``.
            The value for this parameter must being with the value of the component
            followed by a space and then the rest of the value. For example, ``"22pF"``.
        comptype : str, optional
            Field header containing the type of component. The default is ``"Prod name"``. For
            example, you might enter ``"Inductor"``.
        refdes : str, optional
            Field header containing the reference designator of the component. The default is
            ``"Pos / Place"``. For example, you might enter ``"C100"``.

        Returns
        -------
        bool
            ``True`` if the file contains the header and it is correctly parsed. ``True`` is
            returned even if no values are assigned.

        """
        with open(bom_file, "r") as f:
            Lines = f.readlines()
            found = False
            refdescolumn = None
            comptypecolumn = None
            valuecolumn = None
            for line in Lines:
                content_line = [i.strip() for i in line.split(delimiter)]
                if valuefield in content_line:
                    valuecolumn = content_line.index(valuefield)
                if comptype in content_line:
                    comptypecolumn = content_line.index(comptype)
                if refdes in content_line:
                    refdescolumn = content_line.index(refdes)
                elif refdescolumn:
                    found = True
                    new_refdes = content_line[refdescolumn].split(" ")[0]
                    new_value = content_line[valuecolumn].split(" ")[0]
                    new_type = content_line[comptypecolumn]
                    if "resistor" in new_type.lower():
                        self.set_component_rlc(new_refdes, res_value=new_value)
                    elif "capacitor" in new_type.lower():
                        self.set_component_rlc(new_refdes, cap_value=new_value)
                    elif "inductor" in new_type.lower():
                        self.set_component_rlc(new_refdes, ind_value=new_value)
        return found

    @pyaedt_function_handler()
    def get_pin_from_component(self, component, netName=None, pinName=None):
        """Retrieve the pins of a component.

        Parameters
        ----------
        component : str or EDB component
            Name of the component or the EDB component object.
        netName : str, optional
            Filter on the net name as an alternative to
            ``pinName``. The default is ``None``.
        pinName : str, optional
            Filter on the pin name an an alternative to
            ``netName``. The default is ``None``.

        Returns
        -------
        list
            List of pins when the component is found or ``[]`` otherwise.

        Examples
        --------

        >>> from pyaedt import Edb
        >>> edbapp = Edb("myaedbfolder", "project name", "release version")
        >>> edbapp.core_components.get_pin_from_component("R1", refdes)

        """
        if not isinstance(component, self._edb.Cell.Hierarchy.Component):
            component = self._edb.Cell.Hierarchy.Component.FindByName(self._active_layout, component)
        if netName:
            if not isinstance(netName, list):
                netName = [netName]
            # pins = []
            # cmp_obj = list(cmp.LayoutObjs)
            # for p in cmp_obj:
            #    if p.GetObjType() == 1:
            #        if p.IsLayoutPin():
            #            pin_net_name = p.GetNet().GetName()
            #            if pin_net_name in netName:
            #                pins.append(p)
            pins = [
                p
                for p in list(component.LayoutObjs)
                if int(p.GetObjType()) == 1 and p.IsLayoutPin() and p.GetNet().GetName() in netName
            ]
        elif pinName:
            if not isinstance(pinName, list):
                pinName = [pinName]
            pins = [
                p
                for p in list(component.LayoutObjs)
                if int(p.GetObjType()) == 1
                and p.IsLayoutPin()
                and (self.get_aedt_pin_name(p) in pinName or p.GetName() in pinName)
            ]
        else:
            pins = [p for p in list(component.LayoutObjs) if int(p.GetObjType()) == 1 and p.IsLayoutPin()]
        return pins

    @pyaedt_function_handler()
    def get_aedt_pin_name(self, pin):
        """Retrieve the pin name that is shown in AEDT.

        .. note::
           To obtain the EDB core pin name, use `pin.GetName()`.

        Parameters
        ----------
        pin : str
            Name of the pin in EDB core.

        Returns
        -------
        str
            Name of the pin in AEDT.

        Examples
        --------

        >>> from pyaedt import Edb
        >>> edbapp = Edb("myaedbfolder", "project name", "release version")
        >>> edbapp.core_components.get_aedt_pin_name(pin)

        """
        if is_ironpython:
            name = clr.Reference[String]()
            response = pin.GetProductProperty(0, 11, name)
        else:
            val = String("")
            response, name = pin.GetProductProperty(0, 11, val)
        name = str(name).strip("'")
        return name

    @pyaedt_function_handler()
    def get_pin_position(self, pin):
        """Retrieve the pin position in meters.

        Parameters
        ----------
        pin :str
            Name of the pin.

        Returns
        -------
        list
            Pin position as a list of float values in the form ``[x, y]``.

        Examples
        --------

        >>> from pyaedt import Edb
        >>> edbapp = Edb("myaedbfolder", "project name", "release version")
        >>> edbapp.core_components.get_pin_position(pin)

        """
        if is_ironpython:
            res, pt_pos, rot_pos = pin.GetPositionAndRotation()
        else:
            res, pt_pos, rot_pos = pin.GetPositionAndRotation(
                self._edb.Geometry.PointData(self._get_edb_value(0.0), self._get_edb_value(0.0)), 0.0
            )
        if pin.GetComponent().IsNull():
            transformed_pt_pos = pt_pos
        else:
            transformed_pt_pos = pin.GetComponent().GetTransform().TransformPoint(pt_pos)
        pin_xy = self._edb.Geometry.PointData(
            self._get_edb_value(str(transformed_pt_pos.X.ToDouble())),
            self._get_edb_value(str(transformed_pt_pos.Y.ToDouble())),
        )
        return [pin_xy.X.ToDouble(), pin_xy.Y.ToDouble()]

    @pyaedt_function_handler()
    def get_pins_name_from_net(self, pin_list, net_name):
        """Retrieve pins belonging to a net.

        Parameters
        ----------
        pin_list : list
            List of pins to check.
        net_name : str
            Name of the net.

        Returns
        -------
        list
            List of pins belong to the net.

        Examples
        --------

        >>> from pyaedt import Edb
        >>> edbapp = Edb("myaedbfolder", "project name", "release version")
        >>> edbapp.core_components.get_pins_name_from_net(pin_list, net_name)

        """
        pinlist = []
        for pin in pin_list:
            if pin.GetNet().GetName() == net_name:
                pinlist.append(pin.GetName())
        return pinlist

    @pyaedt_function_handler()
    def get_nets_from_pin_list(self, PinList):
        """Retrieve nets with one or more pins.

        Parameters
        ----------
        PinList : list
            List of pins.

        Returns
        -------
        list
            List of nets with one or more pins.

        Examples
        --------

        >>> from pyaedt import Edb
        >>> edbapp = Edb("myaedbfolder", "project name", "release version")
        >>> edbapp.core_components.get_nets_from_pin_list(pinlist)

        """
        netlist = []
        for pin in PinList:
            netlist.append(pin.GetNet().GetName())
        return list(set(netlist))

    @pyaedt_function_handler()
    def get_component_net_connection_info(self, refdes):
        """Retrieve net connection information.

        Parameters
        ----------
        refdes :
            Reference designator for the net.

        Returns
        -------
        dict
            Dictionary of the net connection information for the reference designator.

        Examples
        --------

        >>> from pyaedt import Edb
        >>> edbapp = Edb("myaedbfolder", "project name", "release version")
        >>> edbapp.core_components.get_component_net_connection_info(refdes)

        """
        component_pins = self.get_pin_from_component(refdes)
        data = {"refdes": [], "pin_name": [], "net_name": []}
        for pin_obj in component_pins:
            pin_name = pin_obj.GetName()
            net_name = pin_obj.GetNet().GetName()
            if pin_name is not None:
                data["refdes"].append(refdes)
                data["pin_name"].append(pin_name)
                data["net_name"].append(net_name)
        return data

    def get_rats(self):
        """Retrieve a list of dictionaries of the reference designator, pin names, and net names.

        Returns
        -------
        list
            List of dictionaries of the reference designator, pin names,
            and net names.

        Examples
        --------

        >>> from pyaedt import Edb
        >>> edbapp = Edb("myaedbfolder", "project name", "release version")
        >>> edbapp.core_components.get_rats()

        """
        df_list = []
        for refdes in self.components.keys():
            df = self.get_component_net_connection_info(refdes)
            df_list.append(df)
        return df_list

    def get_through_resistor_list(self, threshold=1):
        """Retrieve through resistors.

        Parameters
        ----------
        threshold : int, optional
            Threshold value. The default is ``1``.

        Returns
        -------
        list
            List of through resistors.

        Examples
        --------

        >>> from pyaedt import Edb
        >>> edbapp = Edb("myaedbfolder", "project name", "release version")
        >>> edbapp.core_components.get_through_resistor_list()

        """
        through_comp_list = []
        for refdes, comp_obj in self.resistors.items():

            numpins = comp_obj.numpins

            if numpins == 2:

                value = comp_obj.res_value
                value = resistor_value_parser(value)

                if value <= threshold:
                    through_comp_list.append(refdes)

        return through_comp_list

    @pyaedt_function_handler()
    def short_component_pins(self, component_name, pins_to_short=None, width=1e-3):
        """Short pins of component with a trace.

        Parameters
        ----------
        component_name : str
            Name of the component.
        pins_to_short : list, optional
            List of pins to short. If `None`, all pins will be shorted.
        width : float, optional
            Short Trace width. It will be used in trace computation algorithm

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.

        Examples
        --------

        >>> from pyaedt import Edb
        >>> edbapp = Edb("myaedbfolder")
        >>> edbapp.core_components.short_component_pins("J4A2", ["G4", "9", "3"])

        """
        component = self.components[component_name]
        pins = component.pins
        pins_list = []

        component.center
        for pin_name, pin in pins.items():
            if pins_to_short:
                if pin_name in pins_to_short:
                    pins_list.append(pin)
            else:
                pins_list.append(pin)
        positions_to_short = []
        center = component.center
        c = [center[0], center[1], 0]
        delta_pins = []
        w = width
        for pin in pins_list:
            placement_layer = pin.placement_layer
            positions_to_short.append(pin.position)
            if placement_layer in self._pedb.core_padstack.padstacks[pin.pin.GetPadstackDef().GetName()].pad_by_layer:
                pad = self._pedb.core_padstack.padstacks[pin.pin.GetPadstackDef().GetName()].pad_by_layer[
                    placement_layer
                ]
            else:
                layer = list(
                    self._pedb.core_padstack.padstacks[pin.pin.GetPadstackDef().GetName()].pad_by_layer.keys()
                )[0]
                pad = self._pedb.core_padstack.padstacks[pin.pin.GetPadstackDef().GetName()].pad_by_layer[layer]
            pars = pad.parameters_values
            geom = pad.geometry_type
            if geom < 6 and pars:
                delta_pins.append(max(pars) + min(pars) / 2)
                w = min(min(pars), w)
            elif pars:
                delta_pins.append(1.5 * pars[0])
                w = min(pars[0], w)
            elif pad.polygon_data:
                bbox = pad.polygon_data.GetBBox()
                lower = [bbox.Item1.X.ToDouble(), bbox.Item1.Y.ToDouble()]
                upper = [bbox.Item2.X.ToDouble(), bbox.Item2.Y.ToDouble()]
                pars = [abs(lower[0] - upper[0]), abs(lower[1] - upper[1])]
                delta_pins.append(max(pars) + min(pars) / 2)
                w = min(min(pars), w)
            else:
                delta_pins.append(1.5 * width)
        i = 0

        while i < len(positions_to_short) - 1:
            p0 = []
            p0.append([positions_to_short[i][0] - delta_pins[i], positions_to_short[i][1], 0])
            p0.append([positions_to_short[i][0] + delta_pins[i], positions_to_short[i][1], 0])
            p0.append([positions_to_short[i][0], positions_to_short[i][1] - delta_pins[i], 0])
            p0.append([positions_to_short[i][0], positions_to_short[i][1] + delta_pins[i], 0])
            p0.append([positions_to_short[i][0], positions_to_short[i][1], 0])
            l0 = [
                GeometryOperators.points_distance(p0[0], c),
                GeometryOperators.points_distance(p0[1], c),
                GeometryOperators.points_distance(p0[2], c),
                GeometryOperators.points_distance(p0[3], c),
                GeometryOperators.points_distance(p0[4], c),
            ]
            l0_min = l0.index(min(l0))
            p1 = []
            p1.append([positions_to_short[i + 1][0] - delta_pins[i + 1], positions_to_short[i + 1][1], 0])
            p1.append([positions_to_short[i + 1][0] + delta_pins[i + 1], positions_to_short[i + 1][1], 0])
            p1.append([positions_to_short[i + 1][0], positions_to_short[i + 1][1] - delta_pins[i + 1], 0])
            p1.append([positions_to_short[i + 1][0], positions_to_short[i + 1][1] + delta_pins[i + 1], 0])
            p1.append([positions_to_short[i + 1][0], positions_to_short[i + 1][1], 0])

            l1 = [
                GeometryOperators.points_distance(p1[0], c),
                GeometryOperators.points_distance(p1[1], c),
                GeometryOperators.points_distance(p1[2], c),
                GeometryOperators.points_distance(p1[3], c),
                GeometryOperators.points_distance(p1[4], c),
            ]
            l1_min = l1.index(min(l1))

            trace_points = [positions_to_short[i]]

            trace_points.append(p0[l0_min][:2])
            trace_points.append(c[:2])
            trace_points.append(p1[l1_min][:2])

            trace_points.append(positions_to_short[i + 1])

            path = self._pedb.core_primitives.Shape("polygon", points=trace_points)
            self._pedb.core_primitives.create_path(
                path,
                layer_name=placement_layer,
                net_name="short",
                width=w,
                start_cap_style="Flat",
                end_cap_style="Flat",
            )
            i += 1
        return True
