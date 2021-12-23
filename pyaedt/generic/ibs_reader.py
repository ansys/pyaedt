import os
import typing

import pyaedt
import pyaedt.generic


class Component:
    """Component extracted from ibis model."""

    def __init__(self):
        self._name = None
        self._manufacturer = None
        self._pins = []
        self._buffers = []

    @property
    def name(self):
        """Name of the component."""
        return self._name

    @name.setter
    def name(self, value):
        self._name = value

    @property
    def manufacturer(self):
        """Manufacturer of the component."""
        return self._manufacturer

    @manufacturer.setter
    def manufacturer(self, value):
        self._manufacturer = value

    @property
    def pins(self):
        """Pins of the component."""
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
        """Full name of the pin including the component name and the ibis filename."""
        return self._name

    @property
    def short_name(self):
        """Name of the pin without the name of the component."""
        return self._short_name

    @short_name.setter
    def short_name(self, value):
        self._short_name = value

    @property
    def signal(self):
        return self._signal

    @signal.setter
    def signal(self, value):
        """Signal of the pin."""
        self._signal = value

    @property
    def model(self):
        return self._model

    @model.setter
    def model(self, value):
        self._model = value

    @property
    def r_value(self):
        """Resitance value in ohms."""
        return self._r_value

    @model.setter
    def r_value(self, value):
        self._r_value = value

    @property
    def l_value(self):
        """Inductance value in H."""
        return self._l_value

    @model.setter
    def l_value(self, value):
        self._l_value = value

    @property
    def c_value(self):
        """Capacitance value in F."""
        return self._c_value

    @model.setter
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
        """
        Insert a pin at a defined location inside the graphical window.

        Parameters
        ----------
        x: float
            X position of the pin.
        y: float
            Y position of the pin.
        angle: float, optional
            Angle of the pin. The default value is ``"0.0"``.
        """

        self._circuit.modeler.schematic.create_component(
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
        return f"{self.short_name}_{self._ibis_name}"

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
        """
        Insert a buffer at a defined location inside the graphical window.

        Parameters
        ----------
        x: float
            X position of the buffer.
        y: float
            Y position of the buffer.
        angle: float, optional
            Angle of the buffer. The default value is ``"0.0"``.
        """
        self._circuit.modeler.schematic.create_component(
            component_library=None,
            component_name=self.name,
            location=[x, y],
            angle=angle,
        )


class ModelSelector:
    pass


class ModelSelectorItem:
    pass


class Model:
    pass


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
        self._components = []
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


class IbisReader:
    def read_project(self, filename: str, circuit):
        """Reads *.ibis file content.

        Parameters
        ----------
        filename : str
            Name of ibis model.
        circuit : class:`pyaedt.circuit.Circuit`
            Circuit in which the ibis components will be used.

        Returns
        ----------
        :class:`pyaedt.generic.Ibis`
            Ibis object exposing all data from the ibis file.
        """

        if os.path.exists(filename) == False:
            error_message = filename + "does not exist."
            raise FileExistsError(error_message)

        ibis_name = pyaedt.generic.general_methods.get_filename_without_extension(filename)
        ibis = Ibis(ibis_name, circuit)

        # Read *.ibis file.
        with open(filename, "r") as file:
            while True:
                current_line = file.readline()
                if not current_line:
                    break

                if self.IsStartedWith(current_line, "[Component] ") == True:
                    self.read_component(ibis, current_line, file)
                elif self.IsStartedWith(current_line, "[Model] ") == True:
                    self.read_model(ibis, current_line, file)
                elif self.IsStartedWith(current_line, "[Model Selector] ") == True:
                    self.read_model_selector(ibis, current_line, file)

        buffers = []
        for model_selector in ibis.model_selectors:
            buffer = Buffer(ibis_name, model_selector.name, circuit)
            buffers.append(buffer)

        for model in ibis.models:
            buffer = Buffer(ibis_name, model.name, circuit)
            buffers.append(buffer)

        ibis.buffers = buffers

        if circuit:
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
                arg_buffers.append(f"{buffer.short_name}:=")
                arg_buffers.append([True, "IbisSingleEnded"])

            arg_components = ["NAME:Components"]
            for component in ibis.components:
                arg_component = [f"NAME:{component.name}"]
                for pin in component.pins:
                    arg_component.append(f"{pin.short_name}:=")
                    arg_component.append([True, False])
                arg_components.append(arg_component)

            args.append(arg_buffers)
            args.append(arg_components)

            circuit.modeler.schematic.o_component_manager.ImportModelsFromFile(filename, args)

        return ibis

    # Model
    def read_model(self, ibis: Ibis, current_line: str, file: typing.TextIO):
        """Extracts model's info.

        Parameters
        ----------
        ibis : :class:`pyaedt.generic.Ibis`
            ibis object containing all info.
        current_line : str
            Current line content.
        file : TextIO
            File's stream.

        """

        if self.IsStartedWith(current_line, "[Model] ") != True:
            return

        model = Model()
        model.name = current_line.split("]")[1].strip()
        current_line = file.readline().replace("\t", "").strip()

        while self.IsStartedWith(current_line, "Model_type") != True:
            current_line = file.readline().replace("\t", "").strip()

        iStart = current_line.index(" ", 1)

        if iStart > 0:
            model.ModelType = current_line[iStart:].strip()

        # Clamp
        while not current_line:
            current_line = file.readline().strip.replace("clamp", "Clamp")

            if self.IsStartedWith(current_line, "[GND Clamp]") == True:
                model.Clamp = True
                break
            elif self.IsStartedWith(current_line, "[GND_Clamp]") == True:
                model.Clamp = True
                break
            elif self.IsStartedWith(current_line, "Enable ", True) == True:
                model.Enable = current_line[len("Enable") + 1 :].strip()
            elif self.IsStartedWith(current_line, "[Rising Waveform]") == True:
                break
            elif self.IsStartedWith(current_line, "[Ramp]") == True:
                break

        ibis.models.append(model)

    # Model Selector
    def read_model_selector(self, ibis: Ibis, current_line: str, file: typing.TextIO):
        """Extracts model selector's info.

        Parameters
        ----------
        ibis : :class:`pyaedt.generic.Ibis`
            ibis object containing all info.
        current_line : str
            Current line content.
        file : TextIO
            File's stream.

        """

        if self.IsStartedWith(current_line, "[Model Selector] ") != True:
            return

        model_selector = ModelSelector()
        model_selector.ModelSelectorItems = []
        model_selector.name = current_line.split("]")[1].strip()

        current_line = file.readline()

        # Model Selector
        while self.IsStartedWith(current_line, "|") is False and current_line.strip() != "":
            model_selector.ModelSelectorItems.append(self.make_model(current_line.strip()))
            current_line = file.readline()

        # ModelSelectorItem
        ibis.model_selectors.append(model_selector)

    def make_model(self, current_line: str) -> ModelSelectorItem:
        """Creates model object.

        Parameters
        ----------
        current_line : str
            Current line content.

        Returns
        -------
        :class:`pyaedt.generic.ModelSelectorItem`
            Model selector item.

        """

        item = ModelSelectorItem()
        i_start = current_line.index(" ", 1)

        if i_start > 0:
            item.name = current_line[i_start:].strip()
            item.Description = current_line[i_start:].strip()

        return item

    # Component
    def read_component(self, ibis: Ibis, current_line: str, file: typing.TextIO):
        """Extracts component's info.

        Parameters
        ----------
        ibis : :class:`pyaedt.generic.Ibis`
            ibis object containing all info.
        current_line : str
            Current line content.
        file : TextIO
            File's stream.

        """

        if self.IsStartedWith(current_line, "[Component] ") != True:
            return

        component = Component()
        component.name = self.get_component_name(current_line)
        current_line = file.readline()

        if self.IsStartedWith(current_line, "[Manufacturer]") == True:
            component.manufacturer = current_line.replace("[Manufacturer]", "").strip()

        while True:
            current_line = file.readline()
            if self.IsStartedWith(current_line, "[Package]") == True:
                break

        self.fill_package_info(component, current_line, file)

        # [pin]
        while self.IsStartedWith(current_line, "[Pin] ") != True:
            current_line = file.readline()

        while True:
            current_line = file.readline()
            if self.IsStartedWith(current_line, "|") == True:
                break

        current_line = file.readline()

        while self.IsStartedWith(current_line, "|") == False:
            component.pins.append(self.make_pin_object(current_line, component.name, ibis))
            current_line = file.readline()
            if current_line == "":
                break

        ibis.components.append(component)

    def fill_package_info(self, component: Component, current_line: str, file: typing.TextIO):
        """Extracts model's info.

        Parameters
        ----------
        component : :class:`pyaedt.generic.Component`
            Current line content.
        current_line : str
            Current line content.
        file : TextIO
            File's stream.

        """
        while self.IsStartedWith(current_line, "|") == True or self.IsStartedWith(current_line, "[") == True:
            current_line = file.readline()

        if self.IsStartedWith(current_line, "R_pkg") == True:
            component.R_pkg = current_line.strip()
            current_line = file.readline()
        elif self.IsStartedWith(current_line, "L_pkg") == True:
            component.L_pkg = current_line.strip()
            current_line = file.readline()
        elif self.IsStartedWith(current_line, "C_pkg") == True:
            component.C_pkg = current_line.strip()

    def get_component_name(self, line: str) -> str:
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
        name = ""
        name = line.replace("[Component]", "")
        return name.strip()

    # Pin
    def make_pin_object(self, line: str, component_name: str, ibis: Ibis) -> Pin:
        """Extracts model's info.

        Parameters
        ----------
        line : str
            Current line content.
        component_name : str
            Name of the component.
        ibis : :class:`pyaedt.generic.Ibis`
            ibis object containing all info.

        Returns
        -------
        :class:`pyaedt.generic.Pin`
            Pin object.

        """

        current_string = ""

        current_string = line.strip().replace("\t", " ")
        pin_name = self.get_first_parameter(current_string)
        pin = Pin(pin_name + "_" + component_name + "_" + ibis.name, ibis.circuit)
        pin.short_name = pin_name
        current_string = current_string[len(pin.name) + 1 :].strip()
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

    def get_first_parameter(self, line: str) -> str:
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

    def IsStartedWith(self, src: str, find: str, ignore_case: bool = True) -> bool:
        """Verifies if a string content starts with a specific string or not.

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
            ``True`` if the src string starts with the patern.

        """

        if ignore_case == True:
            if src[: len(find)].lower() == find.lower():
                return True
            else:
                return False
        else:
            if src[: len(find)] == find:
                return True
            else:
                return False
