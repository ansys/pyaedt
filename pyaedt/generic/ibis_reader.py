import os

import pyaedt
from pyaedt.generic.general_methods import open_file


class Component:
    """Component extracted from ibis model."""

    def __init__(self):
        self._name = None
        self._manufacturer = None
        self._pins = {}

    @property
    def name(self):
        """Name of the component.

        Examples
        --------
        >>> ibis = ibis_reader.IbisReader(os.path.join(path_to_ibis_files, "u26a_800_modified.ibs"), circuit)
        >>> ibis.components["MT47H64M4BP-3_25"].name
        'MT47H64M4BP-3_25'

        """

        return self._name

    @name.setter
    def name(self, value):
        self._name = value

    @property
    def manufacturer(self):
        """Manufacturer of the component.

        Examples
        --------
        >>> ibis = ibis_reader.IbisReader(os.path.join(path_to_ibis_files, "u26a_800_modified.ibs"), circuit)
        >>> ibis.components["MT47H64M4BP-3_25"].manufacturer
        'Micron Technology, Inc.'

        """

        return self._manufacturer

    @manufacturer.setter
    def manufacturer(self, value):
        self._manufacturer = value

    @property
    def pins(self):
        """Pins of the component.

        Examples
        --------
        >>> ibis = ibis_reader.IbisReader(os.path.join(path_to_ibis_files, "u26a_800_modified.ibs"), circuit)
        >>> pins = ibis.components["MT47H64M4BP-3_25"].pins

        """

        return self._pins

    @pins.setter
    def pins(self, value):
        self._pins = value


class Pin(Component):
    """Pin from a component with all its data feature.

    Parameters
    ----------
    name : str
        Name of the pin.
    circuit : class:`pyaedt.circuit.Circuit`
        Circuit in which the pin will be added to.
    """

    def __init__(self, name, circuit):
        self._name = name
        self._circuit = circuit
        self._short_name = None
        self._signal = None
        self._model = None
        self._r_value = None
        self._l_value = None
        self._c_value = None

    @property
    def name(self):
        """Full name of the pin including the component name and the ibis filename.

        Examples
        --------
        >>> ibis = ibis_reader.IbisReader(os.path.join(path_to_ibis_files, "u26a_800_modified.ibs"), circuit)
        >>> ibis.components["MT47H64M4BP-3_25"].pins["A1_MT47H64M4BP-3_25_u26a_800"].name
        'A1_MT47H64M4BP-3_25_u26a_800'

        """
        return self._name

    @property
    def short_name(self):
        """Name of the pin without the name of the component.

        Examples
        --------
        >>> ibis = ibis_reader.IbisReader(os.path.join(path_to_ibis_files, "u26a_800_modified.ibs"), circuit)
        >>> ibis.components["MT47H64M4BP-3_25"].pins["A1_MT47H64M4BP-3_25_u26a_800"].short_name
        'A1'

        """
        return self._short_name

    @short_name.setter
    def short_name(self, value):
        self._short_name = value

    @property
    def signal(self):
        """Signal of the pin.

        Examples
        --------
        >>> ibis = ibis_reader.IbisReader(os.path.join(path_to_ibis_files, "u26a_800_modified.ibs"), circuit)
        >>> ibis.components["MT47H64M4BP-3_25"].pins["A1_MT47H64M4BP-3_25_u26a_800"].signal
        'VDD'

        """
        return self._signal

    @signal.setter
    def signal(self, value):
        self._signal = value

    @property
    def model(self):
        """Model of the pin.

        Examples
        --------
        >>> ibis = ibis_reader.IbisReader(os.path.join(path_to_ibis_files, "u26a_800_modified.ibs"), circuit)
        >>> ibis.components["MT47H64M4BP-3_25"].pins["A1_MT47H64M4BP-3_25_u26a_800"].signal
        'POWER'

        """
        return self._model

    @model.setter
    def model(self, value):
        self._model = value

    @property
    def r_value(self):
        """Resitance value in ohms.

        Examples
        --------
        >>> ibis = ibis_reader.IbisReader(os.path.join(path_to_ibis_files, "u26a_800_modified.ibs"), circuit)
        >>> ibis.components["MT47H64M4BP-3_25"].pins["A1_MT47H64M4BP-3_25_u26a_800"].r_value
        '44.3m'

        """

        return self._r_value

    @r_value.setter
    def r_value(self, value):
        self._r_value = value

    @property
    def l_value(self):
        """Inductance value in H.

        Examples
        --------
        >>> ibis = ibis_reader.IbisReader(os.path.join(path_to_ibis_files, "u26a_800_modified.ibs"), circuit)
        >>> ibis.components["MT47H64M4BP-3_25"].pins["A1_MT47H64M4BP-3_25_u26a_800"].l_value
        '1.99nH'

        """
        return self._l_value

    @l_value.setter
    def l_value(self, value):
        self._l_value = value

    @property
    def c_value(self):
        """Capacitance value in F.

        Examples
        --------
        >>> ibis = ibis_reader.IbisReader(os.path.join(path_to_ibis_files, "u26a_800_modified.ibs"), circuit)
        >>> ibis.components["MT47H64M4BP-3_25"].pins["A1_MT47H64M4BP-3_25_u26a_800"].c_value
        '0.59pF'

        """
        return self._c_value

    @c_value.setter
    def c_value(self, value):
        self._c_value = value

    def add(self):
        """Add a pin to the list of components in the Project Manager."""
        self._circuit.modeler.schematic.o_component_manager.AddSolverOnDemandModel(
            self.name,
            [
                "NAME:CosimDefinition",
                "CosimulatorType:=",
                7,
                "CosimDefName:=",
                "DefaultIBISNetlist",
                "IsDefinition:=",
                True,
                "Connect:=",
                True,
                "Data:=",
                [],
                "GRef:=",
                [],
            ],
        )

    def insert(self, x, y, angle=0.0):
        """Insert a pin at a defined location inside the graphical window.

        Parameters
        ----------
        x : float
            X position of the pin.
        y : float
            Y position of the pin.
        angle : float, optional
            Angle of the pin. The default value is ``"0.0"``.

        Returns
        -------
        :class:`pyaedt.modeler.Object3d.CircuitComponent`
            Circuit Component Object.

        """

        return self._circuit.modeler.schematic.create_component(
            component_library=None,
            component_name=self.name,
            location=[x, y],
            angle=angle,
        )


class Buffer:
    def __init__(self, ibis_name, short_name, circuit):
        self._ibis_name = ibis_name
        self._short_name = short_name
        self._circuit = circuit

    @property
    def name(self):
        """Full name of the buffer including the ibis filename."""
        return "{}_{}".format(self.short_name, self._ibis_name)

    @property
    def short_name(self):
        """Short name of the buffer without the ibis filename included."""
        return self._short_name

    def add(self):
        """Add a buffer to the list of components in the Project Manager."""
        self._circuit.modeler.schematic.o_component_manager.AddSolverOnDemandModel(
            self.name,
            [
                "NAME:CosimDefinition",
                "CosimulatorType:=",
                7,
                "CosimDefName:=",
                "DefaultIBISNetlist",
                "IsDefinition:=",
                True,
                "Connect:=",
                True,
                "Data:=",
                [],
                "GRef:=",
                [],
            ],
        )

    def insert(self, x, y, angle=0.0):
        """Insert a buffer at a defined location inside the graphical window.

        Parameters
        ----------
        x : float
            X position of the buffer.
        y : float
            Y position of the buffer.
        angle : float, optional
            Angle of the buffer. The default value is ``"0.0"``.

        Returns
        -------
        :class:`pyaedt.modeler.Object3d.CircuitComponent`
            Circuit Component Object.

        """

        return self._circuit.modeler.schematic.create_component(
            component_library=None,
            component_name=self.name,
            location=[x, y],
            angle=angle,
        )


class ModelSelector:
    def __init__(self):
        self._model_selector_items = []
        self._name = None

    @property
    def model_selector_items(self):
        """Model selector items."""
        return self._model_selector_items

    @model_selector_items.setter
    def model_selector_items(self, value):
        self._model_selector_items = value

    @property
    def name(self):
        """Name of the model selector."""
        return self._name

    @name.setter
    def name(self, value):
        self._name = value


class ModelSelectorItem:
    def __init__(self):
        self._description = []
        self._name = None

    @property
    def description(self):
        """Description of the item."""
        return self._description

    @description.setter
    def description(self, value):
        self._description = value

    @property
    def name(self):
        """Name of the item."""
        return self._name

    @name.setter
    def name(self, value):
        self._name = value


class Model:
    def __init__(self):
        self._description = []
        self._name = None
        self._clamp = None
        self._enable = None

    @property
    def name(self):
        """Name of the item."""
        return self._name

    @name.setter
    def name(self, value):
        self._name = value

    @property
    def model_type(self):
        """Type of the model."""
        return self._model_type

    @model_type.setter
    def model_type(self, value):
        self._model_type = value

    @property
    def clamp(self):
        """Clamp."""
        return self._clamp

    @clamp.setter
    def clamp(self, value):
        self._clamp = value

    @property
    def enable(self):
        """Is model enabled or not."""
        return self._enable

    @enable.setter
    def enable(self, value):
        self._enable = value


class Ibis:
    """Ibis model with all data extracted: name, components, models.

    Parameters
    ----------
    name : str
        Name of ibis model.
    circuit : class:`pyaedt.circuit.Circuit`
        Circuit in which the ibis components will be used.
    """

    # Ibis reader must work independently or in Circuit.
    def __init__(self, name, circuit):
        self.circuit = circuit
        self._name = name
        self._components = {}
        self._model_selectors = []
        self._models = []

    @property
    def name(self):
        """Name of the ibis model."""
        return self._name

    @property
    def components(self):
        """List of all components included in the ibis file."""
        return self._components

    @components.setter
    def components(self, value):
        self._components = value

    @property
    def model_selectors(self):
        """List of all model selectors included in the ibis file."""
        return self._model_selectors

    @model_selectors.setter
    def model_selectors(self, value):
        self._model_selectors = value

    @property
    def models(self):
        """List of all models included in the ibis file."""
        return self._models

    @models.setter
    def models(self, value):
        self._models = value

    @property
    def buffers(self):
        """Buffers included into the ibis model."""
        return self._buffers

    @buffers.setter
    def buffers(self, value):
        self._buffers = value


class IbisReader(object):
    """Reads *.ibis file content.
    Setup an Ibis object exposing all the extracted data.

    Parameters
    ----------
    filename : str
        Name of ibis model.
    circuit : class:`pyaedt.circuit.Circuit`
        Circuit in which the ibis components will be used.
    """

    def __init__(self, filename, circuit):
        self._filename = filename
        self._circuit = circuit
        self._ibis_model = None

    @property
    def ibis_model(self):
        "Ibis model gathering the entire set of data extracted from the *.ibis file."
        return self._ibis_model

    def parse_ibis_file(self):
        """Reads *.ibis file content.

        Parameters
        ----------
        filename : str
            Name of ibis model.
        circuit : class:`pyaedt.circuit.Circuit`
            Circuit in which the ibis components will be used.

        Returns
        ----------
        :class:`pyaedt.generic.ibis_reader.Ibis`
            Ibis object exposing all data from the ibis file.

        Examples
        --------
        Read u26a_800.ibs file provided in the AEDT suit installation.
        >>> import os
        >>> from pyaedt import Desktop
        >>> from pyaedt.circuit import Circuit
        >>> from pyaedt.generic import ibis_reader
        >>> desktop = Desktop()
        >>> circuit = Circuit()
        >>> ibis = ibis_reader.IbisReader(os.path.join(desktop.install_path, "buflib", "IBIS", "u26a_800.ibs"), circuit)

        """

        if not os.path.exists(self._filename):
            raise Exception("{} does not exist.".format(self._filename))

        ibis_name = pyaedt.generic.general_methods.get_filename_without_extension(self._filename)
        ibis = Ibis(ibis_name, self._circuit)

        # Read *.ibis file.
        with open_file(self._filename, "r") as ibis_file:
            while True:
                current_line = ibis_file.readline()
                if not current_line:
                    break

                if is_started_with(current_line, "[Component] "):
                    self.read_component(ibis, current_line, ibis_file)
                elif is_started_with(current_line, "[Model] "):
                    self.read_model(ibis, current_line, ibis_file)
                elif is_started_with(current_line, "[Model Selector] "):
                    self.read_model_selector(ibis, current_line, ibis_file)

        buffers = {}
        for model_selector in ibis.model_selectors:
            buffer = Buffer(ibis_name, model_selector.name, self._circuit)
            buffers[buffer.name] = buffer

        for model in ibis.models:
            buffer = Buffer(ibis_name, model.name, self._circuit)
            buffers[buffer.name] = buffer

        ibis.buffers = buffers

        if self._circuit:
            args = [
                "NAME:Options",
                "Mode:=",
                4,
                "Overwrite:=",
                False,
                "SupportsSimModels:=",
                False,
                "LoadOnly:=",
                False,
            ]
            arg_buffers = ["NAME:Buffers"]
            for buffer in buffers:
                arg_buffers.append("{}:=".format(buffers[buffer].short_name))
                arg_buffers.append([True, "IbisSingleEnded"])
            model_names = [i.name for i in ibis.models]
            arg_components = ["NAME:Components"]
            for component in ibis.components:
                arg_component = ["NAME:{}".format(ibis.components[component].name)]
                for pin in ibis.components[component].pins:
                    arg_component.append("{}:=".format(ibis.components[component].pins[pin].short_name))
                    if ibis.components[component].pins[pin].model not in model_names:
                        arg_component.append([False, False])
                    else:
                        arg_component.append([True, False])
                arg_components.append(arg_component)

            args.append(arg_buffers)
            args.append(arg_components)

            self._circuit.modeler.schematic.o_component_manager.ImportModelsFromFile(self._filename, args)

        self._ibis_model = ibis

    # Model
    def read_model(self, ibis, current_line, ibis_file):
        """Extracts model's info.

        Parameters
        ----------
        ibis : :class:`pyaedt.generic.ibis_reader.Ibis`
            ibis object containing all info.
        current_line : str
            Current line content.
        ibis_file : TextIO
            File's stream.

        """

        if not is_started_with(current_line, "[Model] "):
            return

        model = Model()
        model.name = current_line.split("]")[1].strip()
        current_line = ibis_file.readline().replace("\t", "").strip()

        while not is_started_with(current_line, "Model_type"):
            current_line = ibis_file.readline().replace("\t", "").strip()

        iStart = current_line.index(" ", 1)

        if iStart > 0:
            model.ModelType = current_line[iStart:].strip()

        # Clamp
        while not current_line:
            current_line = ibis_file.readline().strip.replace("clamp", "Clamp")

            if is_started_with(current_line, "[GND Clamp]"):
                model.Clamp = True
                break
            elif is_started_with(current_line, "[GND_Clamp]"):
                model.Clamp = True
                break
            elif is_started_with(current_line, "Enable ", True):
                model.Enable = current_line[len("Enable") + 1 :].strip()
            elif is_started_with(current_line, "[Rising Waveform]"):
                break
            elif is_started_with(current_line, "[Ramp]"):
                break

        ibis.models.append(model)

    # Model Selector
    def read_model_selector(self, ibis, current_line, ibis_file):
        """Extracts model selector's info.

        Parameters
        ----------
        ibis : :class:`pyaedt.generic.ibis_reader.Ibis`
            ibis object containing all info.
        current_line : str
            Current line content.
        ibis_file : TextIO
            File's stream.

        """

        if not is_started_with(current_line, "[Model Selector] "):
            return

        model_selector = ModelSelector()
        model_selector.model_selector_items = []
        model_selector.name = current_line.split("]")[1].strip()

        current_line = ibis_file.readline()

        # Model Selector
        while not is_started_with(current_line, "|") and current_line.strip() != "":
            model_selector.model_selector_items.append(self.make_model(current_line.strip()))
            current_line = ibis_file.readline()

        # ModelSelectorItem
        ibis.model_selectors.append(model_selector)

    @classmethod
    def make_model(cls, current_line):
        """Creates model object.

        Parameters
        ----------
        current_line : str
            Current line content.

        Returns
        -------
        :class:`pyaedt.generic.ibis_reader.ModelSelectorItem`
            Model selector item.

        """

        item = ModelSelectorItem()
        i_start = current_line.index(" ", 1)

        if i_start > 0:
            item.name = current_line[i_start:].strip()
            item.description = current_line[i_start:].strip()

        return item

    # Component
    def read_component(self, ibis, current_line, ibis_file):
        """Extracts component's info.

        Parameters
        ----------
        ibis : :class:`pyaedt.generic.ibis_reader.Ibis`
            ibis object containing all info.
        current_line : str
            Current line content.
        ibis_file : TextIO
            File's stream.

        """

        if not is_started_with(current_line, "[Component] "):
            return

        component = Component()
        component.name = self.get_component_name(current_line)
        current_line = ibis_file.readline()

        if is_started_with(current_line, "[Manufacturer]"):
            component.manufacturer = current_line.replace("[Manufacturer]", "").strip()

        while True:
            current_line = ibis_file.readline()
            if is_started_with(current_line, "[Package]"):
                break

        self.fill_package_info(component, current_line, ibis_file)

        # [pin]
        while not is_started_with(current_line, "[Pin] "):
            current_line = ibis_file.readline()

        while True:
            current_line = ibis_file.readline()
            if is_started_with(current_line, "|"):
                break

        current_line = ibis_file.readline()

        while not is_started_with(current_line, "|"):
            pin = self.make_pin_object(current_line, component.name, ibis)
            component.pins[pin.name] = pin
            current_line = ibis_file.readline()
            if current_line == "":
                break

        ibis.components[component.name] = component

    @classmethod
    def fill_package_info(cls, component, current_line, ibis_file):
        """Extracts model's info.

        Parameters
        ----------
        component : :class:`pyaedt.generic.ibis_reader.Component`
            Current line content.
        current_line : str
            Current line content.
        ibis_file : TextIO
            File's stream.

        """
        while is_started_with(current_line, "|") or is_started_with(current_line, "["):
            current_line = ibis_file.readline()

        if is_started_with(current_line, "R_pkg"):
            component.R_pkg = current_line.strip()
            current_line = ibis_file.readline()
        elif is_started_with(current_line, "L_pkg"):
            component.L_pkg = current_line.strip()
            current_line = ibis_file.readline()
        elif is_started_with(current_line, "C_pkg"):
            component.C_pkg = current_line.strip()

    @classmethod
    def get_component_name(cls, line):
        """Gets the name of the component.

        Parameters
        ----------
        line : str
            Current line content.

        Returns
        -------
        str
            Name of the component.

        """
        return line.replace("[Component]", "").strip()

    # Pin
    def make_pin_object(self, line, component_name, ibis):
        """Extracts model's info.

        Parameters
        ----------
        line : str
            Current line content.
        component_name : str
            Name of the component.
        ibis : :class:`pyaedt.generic.ibis_reader.Ibis`
            ibis object containing all info.

        Returns
        -------
        :class:`pyaedt.generic.ibis_reader.Pin`
            Pin object.

        """

        current_string = ""

        current_string = line.strip().replace("\t", " ")
        pin_name = self.get_first_parameter(current_string)
        pin = Pin(pin_name + "_" + component_name + "_" + ibis.name, ibis.circuit)
        pin.short_name = pin_name
        current_string = current_string[len(pin.short_name) + 1 :].strip()
        pin.signal = self.get_first_parameter(current_string)

        current_string = current_string[len(pin.signal) + 1 :].strip()
        pin.model = self.get_first_parameter(current_string)

        current_string = current_string[len(pin.model) + 1 :].strip()
        pin.r_value = self.get_first_parameter(current_string)

        current_string = current_string[len(pin.r_value) + 1 :].strip()
        pin.l_value = self.get_first_parameter(current_string)

        current_string = current_string[len(pin.l_value) + 1 :].strip()
        pin.c_value = self.get_first_parameter(current_string)

        return pin

    @classmethod
    def get_first_parameter(cls, line):
        """Gets first parameter string value.

        Parameters
        ----------
        line : str
            Current line content.

        Returns
        -------
        str
            First info extracted from the current line.

        """

        if line == "":
            return ""

        data = line.split(" ")
        return data[0].strip()


def is_started_with(src, find, ignore_case=True):
    """Verifies if a string content starts with a specific string or not.

    This is identical to ``str.startswith``, except that it includes
    the ``ignore_case`` parameter.

    Parameters
    ----------
    src : str
        Current line content.
    find : str
        Current line content.
    ignore_case : bool, optional
        Case sensitive or not. The default value is ``True``.

    Returns
    -------
    bool
        ``True`` if the src string starts with the pattern.

    """

    if ignore_case:
        return src.lower().startswith(find.lower())
    return src.startswith(find)
