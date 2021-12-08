import os
import typing

Components = []
ModelSelectors = []
Models = []

class Component():
    pass

class Pin():
    pass

class ModelSelector():
    pass

class ModelSelectorItem():
    pass

class Model():
    pass

def read_project(fileName: str):
    """Read .ibis file content."""

    if os.path.exists(fileName) == False:
        error_message = fileName + "does not exist."
        raise FileExistsError(error_message)

    # Read *.ibis file.
    with open(fileName,'r') as ts:
        current_line = ts.readline()
        # Component
        if IsStartedWith(current_line, "[Component] ") == True:
            read_component(current_line, ts)
        elif IsStartedWith(current_line, "[Model] ") == True:
            replace_model(current_line, ts)
        elif IsStartedWith(current_line, "[Model Selector] ") == True:
            read_model_selector(current_line, ts)

# Model
def replace_model(current_line: str, ts: typing.TextIO):
    global Models
    if IsStartedWith(current_line, "[Model] ") != True:
        return

    model = Model()
    model.name = current_line.split("]")(1).strip()
    current_line = ts.ReadLine.replace("\t", "").strip()

    while IsStartedWith(current_line, "Model_type") != True:
        current_line = ts.ReadLine.replace("\t", "").strip()

    iStart = current_line.index(" ", 1)

    if iStart > 0:
        model.ModelType = current_line[iStart:].strip()

    # Clamp
    while ts.AtEndOfStream != True:
        current_line = ts.ReadLine.strip.replace("clamp", "Clamp")

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

    Models.append(model)

# Model Selector
def read_model_selector(current_line: str, ts: typing.TextIO):
    if IsStartedWith(current_line, "[Model Selector] ") != True :
        return

    model_selector = ModelSelector()
    model_selector.name = current_line.split("]")(1).strip()

    while IsStartedWith(current_line, "|") == True:
        current_line = ts.ReadLine

    # Model Selector
    while (IsStartedWith(current_line, "|") is False and current_line.strip() != ""):
        model_selector.ModelSelectorItems.append(make_model(current_line.strip()))
        current_line = ts.ReadLine

    # ModelSelectorItem
    model_selector.FillModelReference(Models)
    ModelSelectors.append(model_selector)

def make_model(current_line: str) -> ModelSelectorItem:
    item = ModelSelectorItem()
    i_start = current_line.index(" ", 1)

    if i_start > 0:
        item.name = current_line[i_start:].strip()
        item.Description = current_line[i_start:].strip()

    return item

# Component
def read_component(current_line: str, ts: typing.TextIO):
    global Components
    if IsStartedWith(current_line, "[Component] ") != True:
        return

    component = Component()
    component.name = get_component_name(current_line)
    current_line = ts.ReadLine

    if IsStartedWith(current_line, "[Manufacturer]") == True:
        component.Manufacturer = current_line.replace("[Manufacturer]", "").strip()

    current_line = ts.ReadLine

    while True:
        current_line = ts.ReadLine
        if IsStartedWith(current_line, "[Package]") == True:
            break

    fill_packageI_info(component, current_line, ts)

    # [pin]
    while IsStartedWith(current_line, "[Pin] ") == True:
        current_line = ts.ReadLine

    # current_line = ts.ReadLine

    while True:
        current_line = ts.ReadLine
        if IsStartedWith(current_line, "|") == True:
            break

    while (current_line == ""):
        current_line = ts.ReadLine

    while IsStartedWith(current_line, "|") == False:
        component.Pins.append(make_pin_object(current_line))
        current_line = ts.ReadLine
        if current_line == "":
            break

    Components.append(component)

def fill_packageI_info(component: Component, current_line: str, ts: typing.TextIO):
    while IsStartedWith(current_line, "|") == True:
        current_line = ts.readline()

    # the component object must be created first.
    component.R_pkg.FillData("R_pkg", current_line.strip())
    current_line = ts.ReadLine
    component.L_pkg.FillData("L_pkg", current_line.strip())
    current_line = ts.ReadLine
    component.C_pkg.FillData("C_pkg", current_line.strip())

def get_component_name(line: str) -> str:
    name = ""
    name = line.replace("[Component]", "")
    return name.strip

# Pin
def make_pin_object(line: str) -> Pin:
    pin = Pin()
    current_string = ""

    current_string = line.strip().Replace("\t", " ")
    pin.pin_name = get_first_parameter(current_string)

    current_string = current_string[len(pin.pin_name) + 1:].strip()
    pin.signal_name = get_first_parameter(current_string)

    current_string = current_string[len(pin.signal_name) + 1:].strip()
    pin.model_name = get_first_parameter(current_string)

    current_string = current_string[len(pin.model_name) + 1:].strip()
    pin.r_pin = get_first_parameter(current_string)

    current_string = current_string[len(pin.r_pin) + 1:].strip()
    pin.l_pin = get_first_parameter(current_string)

    current_string = current_string[len(pin.l_pin) + 1:].strip()
    pin.c_pin = get_first_parameter(current_string)

    return pin

def get_first_parameter(line: str) ->str:
    if line == "":
        return ""

    data = line.split(" ")
    return data(0).strip()

def IsStartedWith(src: str, find: str, ignore_case: bool=True) -> bool:
    if ignore_case == True:
        if src[:-len(find)].lower() == find.lower():
            return True
        else:
            return False
    else:
        if src[:-len(find)] == find:
            return True
        else:
            return False