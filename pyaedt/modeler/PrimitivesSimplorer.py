from collections import defaultdict

from ..generic.general_methods import aedt_exception_handler
from .Object3d import CircuitComponent
from .PrimitivesCircuit import CircuitComponents


class SimplorerComponents(CircuitComponents):
    """
    Class for management of all CircuitComponents for Simplorer
    """

    @property
    def design_libray(self):
        return "Simplorer Elements"

    @property
    def tab_name(self):
        return "Quantities"

    @aedt_exception_handler
    def __getitem__(self, partname):
        """
        :param partname: if integer try to get the object id. if string, trying to get object Name
        :return: part object details
        """
        if type(partname) is int:
            return self.components[partname]
        for el in self.components:
            if self.components[el].name == partname or self.components[el].composed_name == partname or el == partname:
                return self.components[el]

        return None

    def __init__(self, parent, modeler):
        CircuitComponents.__init__(self, parent, modeler)
        self._parent = parent
        self.modeler = modeler
        self._currentId = 0
        self.components = defaultdict(CircuitComponent)
        pass

    @aedt_exception_handler
    def create_resistor(self, compname=None, value=50, xpos=0, ypos=0,angle=0, use_instance_id_netlist=False):
        """
        Create a new Resistor


        :param compname: name
        :param value: value
        :param xpos: x pos
        :param ypos: y pos
        :param angle:  angle
        :param use_instance_id_netlist: bool
        :return: id, name
        """
        id, name = self.create_component(compname, component_library="Basic Elements\\Circuit\\Passive Elements",
                                         component_name="R", xpos=xpos, ypos=ypos, angle=angle,
                                         use_instance_id_netlist=use_instance_id_netlist)

        self.components[id].set_property("R", value)

        return id, name

    @aedt_exception_handler
    def create_inductor(self, compname=None,value=50, xpos=0, ypos=0,angle=0, use_instance_id_netlist=False):
        """
        Create a new Inductor


        :param compname: name
        :param value: value
        :param xpos: x pos
        :param ypos: y pos
        :param angle:  angle
        :param use_instance_id_netlist: bool
        :return: id, name
        """
        id, name = self.create_component(compname, component_library="Basic Elements\\Circuit\\Passive Elements",
                                         component_name="L", xpos=xpos, ypos=ypos, angle=angle,
                                         use_instance_id_netlist=use_instance_id_netlist)

        self.components[id].set_property("L", value)
        return id, name

    @aedt_exception_handler
    def create_capacitor(self, compname=None,value=50, xpos=0, ypos=0, angle=0, use_instance_id_netlist=False):
        """
        Create a new Capacitor


        :param compname: name
        :param value: value
        :param xpos: x pos
        :param ypos: y pos
        :param angle:  angle
        :param use_instance_id_netlist: bool
        :return: id, name
        """
        id, name = self.create_component(compname, component_library="Basic Elements\\Circuit\\Passive Elements",
                                         component_name="C", xpos=xpos, ypos=ypos, angle=angle,
                                         use_instance_id_netlist=use_instance_id_netlist)


        self.components[id].set_property("C", value)
        return id, name

    @aedt_exception_handler
    def create_diode(self, compname=None,model_name="required", xpos=0, ypos=0, angle=0, use_instance_id_netlist=False):
        """
        Create a new Diode


        :param compname: name
        :param value: value
        :param xpos: x pos
        :param ypos: y pos
        :param angle:  angle
        :param use_instance_id_netlist: bool
        :return: id, name
        """
        id, name = self.create_component(compname,
                                         component_library="Basic Elements\\Circuit\\Semiconductors System Level",
                                         component_name="D", xpos=xpos, ypos=ypos, angle=angle,
                                         use_instance_id_netlist=use_instance_id_netlist)
        return id, name

    @aedt_exception_handler
    def create_npn(self, compname=None, value=None, xpos=0, ypos=0, angle=0, use_instance_id_netlist=False):
        """
        Create a new Transistor NPN


        :param compname: name
        :param value: value
        :param xpos: x pos
        :param ypos: y pos
        :param angle:  angle
        :param use_instance_id_netlist: bool
        :return: id, name
        """
        id, name = self.create_component(compname,
                                         component_library="Basic Elements\\Circuit\\Semiconductors System Level",
                                         component_name="BJT", xpos=xpos, ypos=ypos, angle=angle,
                                         use_instance_id_netlist=use_instance_id_netlist)
        return id, name

    @aedt_exception_handler
    def create_pnp(self, compname=None,value=50, xpos=0, ypos=0, angle=0, use_instance_id_netlist=False):
        """
        Create a new Transistor PNP


        :param compname: name
        :param value: value
        :param xpos: x pos
        :param ypos: y pos
        :param angle:  angle
        :param use_instance_id_netlist: bool
        :return: id, name
        """
        id, name = self.create_component(compname,
                                         component_library="Basic Elements\\Circuit\\Semiconductors System Level",
                                         component_name="BJT", xpos=xpos, ypos=ypos, angle=angle,
                                         use_instance_id_netlist=use_instance_id_netlist)

        return id, name