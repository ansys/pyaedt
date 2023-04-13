import logging
import re
import warnings

from ansys.edb.definition import NPortComponentModel
from ansys.edb.hierarchy import PinPairModel
from ansys.edb.hierarchy import SParameterModel
from ansys.edb.hierarchy.component_group import ComponentType
from ansys.edb.hierarchy.spice_model import SPICEModel

# from ansys.edb.utility import PinPairRlc
# from ansys.edb.utility import PinPair
from ansys.edb.utility import Rlc

from pyaedt.edb_grpc.core.edb_data.padstacks_data import EDBPadstackInstance
from pyaedt.generic.general_methods import is_ironpython

if not is_ironpython:
    try:
        import numpy as np
    except ImportError:
        warnings.warn(
            "The NumPy module is required to run some functionalities of EDB.\n"
            "Install with \n\npip install numpy\n\nRequires CPython."
        )
from pyaedt.generic.general_methods import get_filename_without_extension
from pyaedt.generic.general_methods import pyaedt_function_handler


class EDBComponentDef(object):
    """Manages EDB functionalities for component definitions.

    Parameters
    ----------
    parent : :class:`pyaedt.edb_grpc.core.components.Components`
        Inherited AEDT object.
    comp_def : object
        Edb ComponentDef Object
    """

    def __init__(self, components, comp_def):
        self._pcomponents = components
        self._edb_comp_def = comp_def

    @property
    def _comp_model(self):
        return self._edb_comp_def.component_models  # pragma: no cover

    @property
    def part_name(self):
        """Retrieve component definition name."""
        return self._edb_comp_def.name

    @part_name.setter
    def part_name(self, name):
        self._edb_comp_def.name = name

    @property
    def type(self):
        """Retrieve the component definition type.

        Returns
        -------
        str
        """
        num = len(set(comp.type for refdes, comp in self.components.items()))
        if num == 0:  # pragma: no cover
            return None
        elif num == 1:
            return list(self.components.values())[0].type
        else:
            return "mixed"  # pragma: no cover

    @type.setter
    def type(self, value):
        for comp in list(self.components.values()):
            comp.type = value

    @property
    def components(self):
        """Get the list of components belonging to this component definition.

        Returns
        -------
        dict of :class:`pyaedt.edb_grpc.core.edb_data.components_data.EDBComponent`
        """
        comp_list = [
            EDBComponent(self._pcomponents, l)
            for l in self._pcomponents._edb.hierarchy.component.find_by_def(
                self._pcomponents._pedb.active_layout, self.part_name
            )
        ]
        return {comp.refdes: comp for comp in comp_list}

    @pyaedt_function_handler
    def assign_rlc_model(self, res, ind, cap, is_parallel=False):
        """Assign RLC to all components under this part name.

        Parameters
        ----------
        res : int, float
            Resistance.
        ind : int, float
            Inductance.
        cap : int, float
            Capacitance.
        is_parallel : bool, optional
            Whether it is parallel or series RLC component.
        """
        for comp in list(self.components.values()):
            res, ind, cap = res, ind, cap
            comp.assign_rlc_model(res, ind, cap, is_parallel)
        return True

    @pyaedt_function_handler
    def assign_s_param_model(self, file_path, model_name=None, reference_net=None):
        """Assign S-parameter to all components under this part name.

        Parameters
        ----------
        file_path : str
            File path of the S-parameter model.
        name : str, optional
            Name of the S-parameter model.
        Returns
        -------

        """
        for comp in list(self.components.values()):
            comp.assign_s_param_model(file_path, model_name, reference_net)
        return True

    @pyaedt_function_handler
    def assign_spice_model(self, file_path, model_name=None):
        """Assign Spice model to all components under this part name.

        Parameters
        ----------
        file_path : str
            File path of the Spice model.
        name : str, optional
            Name of the Spice model.
        Returns
        -------

        """
        for comp in list(self.components.values()):
            comp.assign_spice_model(file_path, model_name)
        return True


class EDBComponent(object):
    """Manages EDB functionalities for components.

    Parameters
    ----------
    parent : :class:`pyaedt.edb_grpc.core.components.Components`
        Inherited AEDT object.
    component : object
        Edb Component Object

    """

    class _PinPair(object):  # pragma: no cover
        def __init__(self, pcomp, edb_comp, edb_comp_prop, edb_model, edb_pin_pair):
            self._pedb_comp = pcomp
            self._edb_comp = edb_comp
            self._edb_comp_prop = edb_comp_prop
            self._edb_model = edb_model
            self._edb_pin_pair = edb_pin_pair

        @property
        def is_parallel(self):
            return self._pin_pair_rlc.is_parallel  # pragma: no cover

        @is_parallel.setter
        def is_parallel(self, value):
            self._pin_pair_rlc.is_parallel = value
            self._set_comp_prop()  # pragma: no cover

        @property
        def _pin_pair_rlc(self):
            return self._edb_model.pin_pair_rlc

        @property
        def rlc_enable(self):
            rlc = self._pin_pair_rlc
            return [rlc.r_enabled, rlc.l_enabled, rlc.c_enabled]

        @rlc_enable.setter
        def rlc_enable(self, value):
            rlc = self._pin_pair_rlc
            rlc.r_enabled = value[0]
            rlc.l_enabled = value[1]
            rlc.c_enabled = value[2]
            self._set_comp_prop()  # pragma: no cover

        @property
        def resistance(self):
            return self._pin_pair_rlc.r  # pragma: no cover

        @resistance.setter
        def resistance(self, value):
            self._pin_pair_rlc.r = value
            self._set_comp_prop(self._pin_pair_rlc)  # pragma: no cover

        @property
        def inductance(self):
            return self._pin_pair_rlc.l  # pragma: no cover

        @inductance.setter
        def inductance(self, value):
            self._pin_pair_rlc.l = value
            self._set_comp_prop(self._pin_pair_rlc)  # pragma: no cover

        @property
        def capacitance(self):
            return self._pin_pair_rlc.c  # pragma: no cover

        @capacitance.setter
        def capacitance(self, value):
            self._pin_pair_rlc.c = value
            self._set_comp_prop(self._pin_pair_rlc)  # pragma: no cover

        @property
        def rlc_values(self):  # pragma: no cover
            rlc = self._pin_pair_rlc
            return [rlc.r, rlc.l, rlc.c]

        @rlc_values.setter
        def rlc_values(self, values):  # pragma: no cover
            rlc = self._pin_pair_rlc
            rlc.R = values[0]
            rlc.L = values[1]
            rlc.C = values[2]
            self._set_comp_prop()  # pragma: no cover

        def _set_comp_prop(self):  # pragma: no cover
            self._edb_model.set_rlc(self._edb_pin_pair, self._pin_pair_rlc)
            self._edb_comp_prop.set_model(self._edb_model)  # to test
            self._edb_comp.component_property = self._edb_comp_prop

    class _SpiceModel(object):  # pragma: no cover
        def __init__(self, edb_model):
            self._edb_model = edb_model

        @property
        def file_path(self):
            return self._edb_model.model_path

        @property
        def name(self):
            return self._edb_model.model_name

    class _SparamModel(object):  # pragma: no cover
        def __init__(self, edb_model):
            self._edb_model = edb_model

        @property
        def name(self):
            return self._edb_model.component_model

        @property
        def reference_net(self):
            return self._edb_model.reference_net

    class _NetlistModel(object):  # pragma: no cover
        def __init__(self, edb_model):
            self._edb_model = edb_model

        @property
        def netlist(self):
            return self._edb_model.netlist

    def __init__(self, components, cmp):
        self._pcomponents = components
        self.edbcomponent = cmp
        self._layout_instance = None
        self._comp_instance = None

    @property
    def layout_instance(self):
        """Edb layout instance object."""
        if self._layout_instance is None:
            self._layout_instance = self._pcomponents._pedb.layout_instance
        return self._layout_instance

    @property
    def component_instance(self):
        """Edb component instance."""
        if self._comp_instance is None:
            self._comp_instance = self.layout_instance.get_layout_obj_instance_in_context(self.edbcomponent, None)
        return self._comp_instance

    @property
    def _pedb(self):  # pragma: no cover
        return self._pcomponents._pedb

    @property
    def _active_layout(self):  # pragma: no cover
        return self._pedb.active_layout

    @property
    def component_property(self):
        """``ComponentProperty`` object."""
        return self.edbcomponent.component_property

    @property
    def _edb_model(self):  # pragma: no cover
        return self.component_property.model  # should not need clone() command

    @property  # pragma: no cover
    def _pin_pairs(self):
        edb_comp_prop = self.component_property
        edb_model = self._edb_model
        return [
            self._PinPair(self, self.edbcomponent, edb_comp_prop, edb_model, pin_pair)
            for pin_pair in list(edb_model.PinPairs)
        ]

    @property
    def spice_model(self):
        """Get assigned Spice model properties."""
        if not self.model_type == "SPICEModel":
            return None
        else:
            return self._SpiceModel(self._edb_model)

    @property
    def s_param_model(self):
        """Get assigned S-parameter model properties."""
        if not self.model_type == "SParameterModel":
            return None
        else:
            return self._SparamModel(self._edb_model)

    @property
    def netlist_model(self):
        """Get assigned netlist model properties."""
        if not self.model_type == "NetlistModel":
            return None
        else:
            return self._NetlistModel(self._edb_model)

    @property
    def solder_ball_height(self):
        """Solder ball height if available."""
        if "GetSolderBallProperty" in dir(self.component_property):
            return self.component_property.solder_ball_property.height
        return None

    @property
    def solder_ball_placement(self):
        """Solder ball placement if available.."""
        if "GetSolderBallProperty" in dir(self.component_property):
            return int(self.component_property.solder_ball_property.placement)
        return 2

    @property
    def refdes(self):
        """Reference Designator Name.

        Returns
        -------
        str
            Reference Designator Name.
        """
        return self.edbcomponent.name

    @refdes.setter
    def refdes(self, name):
        self.edbcomponent.name = name

    @property
    def is_enabled(self):
        """Check if the current object is enabled.

        Returns
        -------
        bool
            ``True`` if current object is enabled, ``False`` otherwise.
        """
        if self.type in ["Resistor", "Capacitor", "Inductor"]:
            return self.component_property.is_enabled
        else:  # pragma: no cover
            return False

    @is_enabled.setter
    def is_enabled(self, enabled):
        """Enables the current object."""
        if self.type in ["Resistor", "Capacitor", "Inductor"]:
            component_property = self.component_property
            component_property.is_enabled = enabled
            self.edbcomponent.component_property = component_property

    @property
    def model_type(self):
        """Retrieve assigned model type."""
        _model_type = self._edb_model.type.split(".")[-1]  # to check the model has been refactored
        if _model_type == "PinPairModel":
            return "RLC"
        else:
            return _model_type

    @property
    def rlc_values(self):
        """Get component rlc values."""
        if not len(self._pin_pairs):
            return [None, None, None]
        pin_pair = self._pin_pairs[0]
        return pin_pair.rlc_values

    @rlc_values.setter
    def rlc_values(self, value):
        if isinstance(value, list):  # pragma no cover
            enabled = [True if i else False for i in value]
            model = PinPairModel.create()
            pin_names = list(self.pins.keys())
            for idx, i in enumerate(np.arange(len(pin_names) // 2)):
                pin_pair = (pin_names[idx], pin_names[idx + 1])
                rlc = Rlc(
                    r=value[0],
                    r_enabled=enabled[0],
                    l=value[1],
                    l_enabled=enabled[1],
                    c=value[2],
                    c_enabled=enabled[2],
                    is_parallel=False,
                )
                model.set_rlc(pin_pair, rlc)
            self._set_model(model)

    @property
    def value(self):
        """Retrieve discrete component value.

        Returns
        -------
        str
            Value. ``None`` if not an RLC Type.
        """
        if self.model_type == "RLC":
            pin_pair = self._pin_pairs[0]
            if len([i for i in pin_pair.rlc_enable if i]) == 1:
                return [pin_pair.rlc_values[idx] for idx, val in enumerate(pin_pair.rlc_enable) if val][0]
            else:
                return pin_pair.rlc_values
        elif self.model_type == "SPICEModel":
            return self.spice_model.file_path
        elif self.model_type == "SParameterModel":
            return self.s_param_model.name
        else:
            return self.netlist_model.netlist

    @value.setter
    def value(self, value):
        rlc_enabled = [True if i == self.type else False for i in ["Resistor", "Inductor", "Capacitor"]]
        rlc_values = [value if i == self.type else 0 for i in ["Resistor", "Inductor", "Capacitor"]]

        model = PinPairModel()
        pin_names = list(self.pins.keys())
        for idx, i in enumerate(np.arange(len(pin_names) // 2)):
            pin_pair = (pin_names[idx], pin_names[idx + 1])
            rlc = Rlc(
                r=rlc_values[0],
                r_enabled=rlc_enabled[0],
                l=rlc_values[1],
                l_enabled=rlc_enabled[1],
                c=rlc_values[2],
                c_enabled=rlc_enabled[2],
                is_parallel=False,
            )
            model.set_rlc(pin_pair, rlc)
        self._set_model(model)

    @property
    def res_value(self):
        """Resistance value.

        Returns
        -------
        str
            Resistance value or ``None`` if not an RLC type.
        """
        cmp_type = int(self.edbcomponent.GetComponentType())
        if 0 < cmp_type < 4:
            model = self.edbcomponent.model.clone()
            pinpairs = model.pin_pairs
            if not list(pinpairs):
                return "0"
            for pinpair in pinpairs:
                pair = pinpair.pin_pairs_rlc
                return pair.r
        return None

    @res_value.setter
    def res_value(self, value):  # pragma no cover
        if value:
            if self.rlc_values == [None, None, None]:
                self.rlc_values = [value, 0, 0]
            else:
                self.rlc_values = [value, self.rlc_values[1], self.rlc_values[2]]

    @property
    def cap_value(self):
        """Capacitance Value.

        Returns
        -------
        str
            Capacitance Value. ``None`` if not an RLC Type.
        """
        cmp_type = int(self.edbcomponent.obj_type)
        if 0 < cmp_type < 4:
            model = self.edbcomponent.model.clone()
            pinpairs = model.pin_pairs
            if not list(pinpairs):
                return "0"
            for pinpair in pinpairs:
                pair = pinpair.pin_pairs_rlc
                return pair.c
        return None

    @cap_value.setter
    def cap_value(self, value):  # pragma no cover
        if value:
            if self.rlc_values == [None, None, None]:
                self.rlc_values = [0, 0, value]
            else:
                self.rlc_values = [self.rlc_values[1], self.rlc_values[2], value]

    @property
    def ind_value(self):
        """Inductance Value.

        Returns
        -------
        str
            Inductance Value. ``None`` if not an RLC Type.
        """
        cmp_type = int(self.edbcomponent.GetComponentType())
        if 0 < cmp_type < 4:
            model = self.edbcomponent.model.clone()
            pinpairs = model.pin_pairs
            if not list(pinpairs):
                return "0"
            for pinpair in pinpairs:
                pair = pinpair.pin_pairs_rlc
                return pair.l
        return None

    @ind_value.setter
    def ind_value(self, value):  # pragma no cover
        if value:
            if self.rlc_values == [None, None, None]:
                self.rlc_values = [0, value, 0]
            else:
                self.rlc_values = [self.rlc_values[1], value, self.rlc_values[2]]

    @property
    def is_parallel_rlc(self):
        """Define if model is Parallel or Series.

        Returns
        -------
        bool
            ``True`` if it is a parallel rlc model. ``False`` for series RLC. ``None`` if not an RLC Type.
        """
        cmp_type = int(self.edbcomponent.obj_type)
        if 0 < cmp_type < 4:
            model = self.edbcomponent.model.clone()
            pinpairs = model.PinPairs
            for pinpair in pinpairs:
                pair = pinpair.pin_pairs_rlc
                return pair.is_parallel
        return None

    @is_parallel_rlc.setter
    def is_parallel_rlc(self, value):  # pragma no cover
        if not len(self._pin_pairs):
            logging.warning(self.refdes, " has no pin pair.")
        else:
            if isinstance(value, bool):
                model = self.edbcomponent.model.clone()
                pinpairs = model.pin_pairs
                if not list(pinpairs):
                    return "0"
                for pin_pair in pinpairs:
                    pin_pair_rlc = pin_pair.pin_pairs_rlc
                    pin_pair_rlc.is_parallel = value
                    pin_pair_model = self._edb_model
                    pin_pair_model.set_pin_pair_rlc(pin_pair, pin_pair_rlc)
                    self.edbcomponent.component_property.set_model(pin_pair_model)

    @property
    def center(self):
        """Compute the component center.

        Returns
        -------
        list
        """
        return self.edbcomponent.location

    @property
    def bounding_box(self):
        """Component's bounding box.

        Returns
        -------
        List[float]
            List of coordinates for the component's bounding box, with the list of
            coordinates in this order: [X lower left corner, Y lower left corner,
            X upper right corner, Y upper right corner].
        """
        return self.component_instance.get_bbox()

    @property
    def rotation(self):
        """Compute the component rotation in radian.

        Returns
        -------
        float
        """
        return self.edbcomponent.transform.rotation

    @property
    def pinlist(self):
        """Pins of the component.

        Returns
        -------
        list
            List of Pins of Component.
        """
        return [pin for pin in self.edbcomponent.members if pin.is_layout]

    @property
    def nets(self):
        """Nets of Component.

        Returns
        -------
        list
            List of Nets of Component.
        """
        return list(set([pin.net.name for pin in self.pinlist]))

    @property
    def pins(self):
        """EDBPadstackInstance of Component.

        Returns
        -------
        dic[str, :class:`pyaedt.edb_grpc.core.edb_data.definitions.EDBPadstackInstance`]
            Dictionary of EDBPadstackInstance Components.
        """
        pins = {}
        for el in self.pinlist:
            pins[el.net] = EDBPadstackInstance(el, self._pcomponents._pedb)
        return pins

    @property
    def type(self):
        """Component type.

        Returns
        -------
        str
            Component type.
        """
        cmp_type = self.edbcomponent.component_type
        if cmp_type == ComponentType.RESISTOR:
            return "Resistor"
        elif cmp_type == ComponentType.INDUCTOR:
            return "Inductor"
        elif cmp_type == ComponentType.CAPACITOR:
            return "Capacitor"
        elif cmp_type == ComponentType.IC:
            return "IC"
        elif cmp_type == ComponentType.IO:
            return "IO"
        elif cmp_type == ComponentType.OTHER:
            return "Other"

    @type.setter
    def type(self, new_type):
        """Set component type

        Parameters
        ----------
        new_type : str
            Type of the component. Options are ``"Resistor"``,  ``"Inductor"``, ``"Capacitor"``,
            ``"IC"``, ``"IO"`` and ``"Other"``.
        """
        if new_type == "Resistor":
            type_id = ComponentType.RESISTOR
        elif new_type == "Inductor":
            type_id = ComponentType.INDUCTOR
        elif new_type == "Capacitor":
            type_id = ComponentType.CAPACITOR
        elif new_type == "IC":
            type_id = ComponentType.IC
        elif new_type == "IO":
            type_id = ComponentType.IO
        elif new_type == "Other":
            type_id = ComponentType.OTHER
        else:
            return
        self.edbcomponent.component_type = type_id

    @property
    def numpins(self):
        """Number of Pins of Component.

        Returns
        -------
        int
            Number of Pins of Component.
        """
        return self.edbcomponent.num_pins

    @property
    def partname(self):  # pragma: no cover
        """Component part name.

        Returns
        -------
        str
            Component Part Name.
        """
        return self.part_name

    @partname.setter
    def partname(self, name):  # pragma: no cover
        """Set component part name."""
        self.part_name = name

    @property
    def part_name(self):
        """Component part name.

        Returns
        -------
        str
            Component part name.
        """
        return self.edbcomponent.component_def.name

    @part_name.setter
    def part_name(self, name):  # pragma: no cover
        """Set component part name."""
        self.edbcomponent.component_def.name = name

    @property
    def _edb(self):
        return self._pcomponents._edb

    @property
    def placement_layer(self):
        """Placement layer.

        Returns
        -------
        str
           Name of the placement layer.
        """
        return self.edbcomponent.placement_layer.name

    @property
    def lower_elevation(self):
        """Lower elevation of the placement layer.

        Returns
        -------
        float
            Lower elevation of the placement layer.
        """
        return self.edbcomponent.placement_layer.lower_elevation

    @property
    def upper_elevation(self):
        """Upper elevation of the placement layer.

        Returns
        -------
        float
            Upper elevation of the placement layer.

        """
        return self.edbcomponent.placement_layer.upper_elevation  # trying without cloning

    @property
    def top_bottom_association(self):
        """Top/bottom association of the placement layer.

        Returns
        -------
        int
            Top/bottom association of the placement layer, where:

            * 0 - Top associated
            * 1 - No association
            * 2 - Bottom associated
            * 4 - Number of top/bottom associations.
            * -1 - Undefined
        """
        return int(self.edbcomponent.placement_layer.top_bottom_association)

    @pyaedt_function_handler
    def _set_model(self, model):  # pragma: no cover
        comp_prop = self.component_property
        comp_prop.model = model
        self.edbcomponent.model = comp_prop
        if not self.edbcomponent.model:
            logging.error("Fail to assign model on {}.".format(self.refdes))
            return False
        return True

    @pyaedt_function_handler
    def assign_spice_model(self, file_path, name=None):
        """Assign Spice model to this component.

        Parameters
        ----------
        file_path : str
            File path of the Spice model.
        name : str, optional
            Name of the Spice model.

        Returns
        -------

        """
        if not name:
            name = get_filename_without_extension(file_path)

        with open(file_path, "r") as f:
            for line in f:
                if "subckt" in line.lower():
                    pinNames = [i.strip() for i in re.split(" |\t", line) if i]
                    pinNames.remove(pinNames[0])
                    pinNames.remove(pinNames[0])
                    break
        if len(pinNames) == self.numpins:
            model = SPICEModel()
            model.model_path(file_path)
            model.model_name(name)
            terminal = 1
            for pn in pinNames:
                model.add_terminal(pn, str(terminal))
                terminal += 1
        else:  # pragma: no cover
            logging.error("Wrong number of Pins")
            return False
        return self._set_model(model)

    @pyaedt_function_handler
    def assign_s_param_model(self, file_path, name=None, reference_net=None):
        """Assign S-parameter to this component.

        Parameters
        ----------
        file_path : str
            File path of the S-parameter model.
        name : str, optional
            Name of the S-parameter model.

        Returns
        -------

        """
        if not name:
            name = get_filename_without_extension(file_path)
        model_list = self.edbcomponent.component_def.component_models
        nport_model = [model for model in model_list if model.reference_file == file_path]
        if not nport_model:
            nport_model = NPortComponentModel.create(name)
            nport_model.reference_file = file_path
            self.edbcomponent.component_def.component_models.add(nport_model)
        model = SParameterModel.create(name, reference_net)
        return self._set_model(model)

    @pyaedt_function_handler
    def assign_rlc_model(self, res, ind, cap, is_parallel=False):
        """Assign RLC to this component.

        Parameters
        ----------
        res : int, float
            Resistance.
        ind : int, float
            Inductance.
        cap : int, float
            Capacitance.
        is_parallel : bool, optional
            Whether it is a parallel or series RLC component. The default is ``False``.
        """
        model = PinPairModel.create()
        pin_names = list(self.pins.keys())
        for idx, i in enumerate(np.arange(len(pin_names) // 2)):
            rlc = Rlc(res, True, ind, True, cap, True, is_parallel)
            model.set_rlc((pin_names[idx], pin_names[idx + 1]), rlc)
        return self._set_model(model)

    @pyaedt_function_handler
    def create_clearance_on_component(self, extra_soldermask_clearance=1e-4):
        """Create a Clearance on Soldermask layer by drawing a rectangle.

        Parameters
        ----------
        extra_soldermask_clearance : float, optional
            Extra Soldermask value in meter to be applied on component bounding box.
        Returns
        -------
            bool
        """
        bounding_box = self.bounding_box
        opening = [bounding_box[0] - extra_soldermask_clearance]
        opening.append(bounding_box[1] - extra_soldermask_clearance)
        opening.append(bounding_box[2] + extra_soldermask_clearance)
        opening.append(bounding_box[3] + extra_soldermask_clearance)

        comp_layer = self.placement_layer
        layer_names = list(self._pedb.stackup.stackup_layers.keys())
        layer_index = layer_names.index(comp_layer)
        if comp_layer in [layer_names[0] + layer_names[-1]]:
            return False
        elif layer_index < len(layer_names) / 2:
            soldermask_layer = layer_names[layer_index - 1]
        else:
            soldermask_layer = layer_names[layer_index + 1]

        if not self._pedb.core_primitives.get_primitives(layer_name=soldermask_layer):
            all_nets = list(self._pedb.core_nets.nets.values())
            poly = self._pedb._create_conformal(all_nets, 0, 1e-12, False, 0)
            self._pedb.core_primitives.create_polygon(poly, soldermask_layer, [], "")

        void = self._pedb.core_primitives.create_rectangle(
            soldermask_layer,
            "{}_opening".format(self.refdes),
            lower_left_point=opening[:2],
            upper_right_point=opening[2:],
        )
        void.is_negative = True
        return True
