import os
import typing

import pyaedt
import pyaedt.generic

ibis = None

class Component():
    def __init__(self):
        self._pins = []
        self._name = None
        self._buffers = []

    @property
    def pins(self):
        return self._pins

    @pins.setter
    def pins(self, value):
        self._pins = value

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, value):
        self._name = value

    @property
    def manufacturer(self):
        return self._manufacturer

    @manufacturer.setter
    def manufacturer(self, value):
        self._manufacturer = value

    @property
    def buffers(self):
        return self._buffers

    @buffers.setter
    def buffers(self, value):
        self._buffers = value

class Pin(Component):
    def __init__(self, name, circuit):
        self._name = name
        self._circuit = circuit
        self._short_name = None
        self._signal = None
        self._model = None
        self._r_value = None
        self._l_value = None
        self._c_value = None

    def add(self):
        self._circuit.modeler.schematic.o_component_manager.AddSolverOnDemandModel(self._name,["NAME:CosimDefinition","CosimulatorType:=",7,"CosimDefName:=","DefaultIBISNetlist","IsDefinition:=",True,"Connect:=",True,"Data:=",[],"GRef:=",[]])

    def insert(self, x, y, angle):
        self._circuit.modeler.schematic.create_component(
                            component_library = None,
                            component_name=self.name,
                            location=[x, y],
                            angle = angle,
                            )

    # def place_component(x: int, y: int, angle: int):
    #     pass

    @property
    def name(self):
        return self._name

    @property
    def short_name(self):
        return self._short_name

    @short_name.setter
    def short_name(self, value):
        self._short_name = value

    @property
    def signal(self):
        return self._signal

    @signal.setter
    def signal(self, value):
        self._signal = value

    @property
    def model(self):
        return self._model

    @model.setter
    def model(self, value):
        self._model = value

    @property
    def r_value(self):
        return self._r_value

    @model.setter
    def r_value(self, value):
        self._r_value = value

    @property
    def l_value(self):
        return self._l_value

    @model.setter
    def l_value(self, value):
        self._l_value = value

    @property
    def c_value(self):
        return self._c_value

    @model.setter
    def c_value(self, value):
        self._c_value = value


class Buffer():
    def __init__(self, name, circuit):
        self._name = name
        self._circuit = circuit

    # def insert(self):
    #     self._cricuit.modeler.schematic.create_component(
    #                         fields[0],
    #                         component_library=None,
    #                         component_name=self.name,
    #                         location=[xpos, ypos],
    #                         use_instance_id_netlist=use_instance,
    #                     )

    # def create_symbol(self):
    #     pass

    def place_component(x: int, y: int, angle: int):
        pass

    @property
    def name(self):
        return self._name

class ModelSelector():
    pass

class ModelSelectorItem():
    pass

class Model(Component):
    def create_symbol(self):
        pass

class Ibis():
    # Ibis reader must work independently or in Circuit.
    def __init__(self, name, circuit):
        self.circuit = circuit
        self._name = name
        self._components = []
        self._model_selectors = []
        self._models = []

    @property
    def name(self):
        return self._name

    @property
    def components(self):
        return self._components

    @components.setter
    def components(self, value):
        self._components = value

    @property
    def model_selectors(self):
        return self._model_selectors

    @model_selectors.setter
    def model_selectors(self, value):
        self._model_selectors = value

    @property
    def models(self):
        return self._models

    @models.setter
    def models(self, value):
        self._models = value


def read_project(fileName: str, circuit):
    """Read .ibis file content."""

    if os.path.exists(fileName) == False:
        error_message = fileName + "does not exist."
        raise FileExistsError(error_message)

    ibis_name = pyaedt.generic.general_methods.get_filename_without_extension(fileName)
    ibis = Ibis(ibis_name, circuit)

    # Read *.ibis file.
    with open(fileName, 'r') as f:
        while True:
            current_line = f.readline()
            if not current_line:
                break

            if IsStartedWith(current_line, "[Component] ") == True:
                read_component(ibis, current_line, f)
            elif IsStartedWith(current_line, "[Model] ") == True:
                replace_model(ibis, current_line, f)
            elif IsStartedWith(current_line, "[Model Selector] ") == True:
                read_model_selector(ibis, current_line, f)


    buffers = []
    for model_selector in ibis.model_selectors:
        buffer = Buffer(model_selector.name, circuit)
        buffers.append(buffer)

    for model in ibis.models:
        buffer = Buffer(model.name, circuit)
        buffers.append(buffer)

    if circuit:
        arg1 = ["NAME:Options", "Mode:=", 4, "Overwrite:=", False, "SupportsSimModels:=", False, "LoadOnly:=", False,]
        arg_buffers = ["NAME:Buffers"]
        for buffer in buffers:
            arg_buffers.append(buffer.name+":=")
            arg_buffers.append([False,"IbisSingleEnded"]) # WARNING DQS# is TRUE

        arg_components = ["NAME:Components"]
        for component in ibis.components:
            arg_component = ["NAME:"+component.name]
            for pin in component.pins:
                arg_component.append(pin.short_name+":=")
                arg_component.append([False,False])
            arg_components.append(arg_component)

        args = [arg1, arg_buffers, arg_components]

        circuit.modeler.schematic.o_component_manager.ImportModelsFromFile(fileName,args)

    return ibis


# Model
def replace_model(ibis: Ibis, current_line: str, f: typing.TextIO):

    if IsStartedWith(current_line, "[Model] ") != True:
        return

    model = Model()
    model.name = current_line.split("]")[1].strip()
    current_line = f.readline().replace("\t", "").strip()

    while IsStartedWith(current_line, "Model_type") != True:
        current_line = f.readline().replace("\t", "").strip()

    iStart = current_line.index(" ", 1)

    if iStart > 0:
        model.ModelType = current_line[iStart:].strip()

    # Clamp
    while not current_line:
        current_line = f.readline().strip.replace("clamp", "Clamp")

        if IsStartedWith(current_line, "[GND Clamp]") == True:
            model.Clamp = True
            break
        elif IsStartedWith(current_line, "[GND_Clamp]") == True:
            model.Clamp = True
            break
        elif IsStartedWith(current_line, "Enable ", True) == True:
            model.Enable = current_line[len("Enable") + 1:].strip()
        elif IsStartedWith(current_line, "[Rising Waveform]") == True:
            break
        elif IsStartedWith(current_line, "[Ramp]") == True:
            break

    ibis.models.append(model)

# Model Selector
def read_model_selector(ibis: Ibis, current_line: str, f: typing.TextIO):

    if IsStartedWith(current_line, "[Model Selector] ") != True :
        return

    model_selector = ModelSelector()
    model_selector.ModelSelectorItems = []
    model_selector.name = current_line.split("]")[1].strip()

    # while IsStartedWith(current_line, "|") == True:
    #     current_line = f.readline()

    current_line = f.readline()

    # Model Selector
    while (IsStartedWith(current_line, "|") is False and current_line.strip() != ""):
        model_selector.ModelSelectorItems.append(make_model(current_line.strip()))
        current_line = f.readline()

    # ModelSelectorItem
    #model_selector.FillModelReference(Models) @MAssimo: Is is it related to COM objecf.
    ibis.model_selectors.append(model_selector)

def make_model(current_line: str) -> ModelSelectorItem:
    item = ModelSelectorItem()
    i_start = current_line.index(" ", 1)

    if i_start > 0:
        item.name = current_line[i_start:].strip()
        item.Description = current_line[i_start:].strip()

    return item

# Component
def read_component(ibis: Ibis, current_line: str, f: typing.TextIO):

    if IsStartedWith(current_line, "[Component] ") != True:
        return

    component = Component()
    component.name = get_component_name(current_line)
    current_line = f.readline()

    if IsStartedWith(current_line, "[Manufacturer]") == True:
        component.manufacturer = current_line.replace("[Manufacturer]", "").strip()

    # current_line = f.readline()

    while True:
        current_line = f.readline()
        if IsStartedWith(current_line, "[Package]") == True:
            break

    fill_package_info(component, current_line, f)

    # [pin]
    while IsStartedWith(current_line, "[Pin] ") != True:
        current_line = f.readline()

    # current_line = f.readline()

    while True:
        current_line = f.readline()
        if IsStartedWith(current_line, "|") == True:
            break

    current_line = f.readline()

    while IsStartedWith(current_line, "|") == False:
        component.pins.append(make_pin_object(current_line, component.name, ibis))
        current_line = f.readline()
        if current_line == "":
            break

    ibis.components.append(component)

def fill_package_info(component: Component, current_line: str, f: typing.TextIO):
    while IsStartedWith(current_line, "|") == True or IsStartedWith(current_line, "[") == True:
        current_line = f.readline()

    # the component object must be created first.
    # component.R_pkg.FillData("R_pkg", current_line.strip())
    # current_line = f.readline()
    # component.L_pkg.FillData("L_pkg", current_line.strip())
    # current_line = f.readline()
    # component.C_pkg.FillData("C_pkg", current_line.strip())

    if IsStartedWith(current_line, "R_pkg") == True:
        component.R_pkg = current_line.strip()
        current_line = f.readline()
    elif IsStartedWith(current_line, "L_pkg") == True:
        component.L_pkg = current_line.strip()
        current_line = f.readline()
    elif IsStartedWith(current_line, "C_pkg") == True:
        component.C_pkg = current_line.strip()

def get_component_name(line: str) -> str:
    name = ""
    name = line.replace("[Component]", "")
    return name.strip()

# Pin
def make_pin_object(line: str, component_name: str, ibis: Ibis) -> Pin:

    current_string = ""

    current_string = line.strip().replace("\t", " ")
    pin_name = get_first_parameter(current_string)
    pin = Pin(pin_name + "_" + component_name + "_" + ibis.name, ibis.circuit)
    pin.short_name = pin_name
    current_string = current_string[len(pin.name) + 1:].strip()
    pin.signal = get_first_parameter(current_string)

    current_string = current_string[len(pin.signal) + 1:].strip()
    pin.model = get_first_parameter(current_string)

    current_string = current_string[len(pin.model) + 1:].strip()
    pin.r_value = get_first_parameter(current_string)

    current_string = current_string[len(pin.r_value) + 1:].strip()
    pin.l_value = get_first_parameter(current_string)

    current_string = current_string[len(pin.l_value) + 1:].strip()
    pin.c_value = get_first_parameter(current_string)

    return pin

def get_first_parameter(line: str) -> str:
    if line == "":
        return ""

    data = line.split(" ")
    return data[0].strip()

def IsStartedWith(src: str, find: str, ignore_case: bool=True) -> bool:
    if ignore_case == True:
        if src[:len(find)].lower() == find.lower():
            return True
        else:
            return False
    else:
        if src[:len(find)] == find:
            return True
        else:
            return False