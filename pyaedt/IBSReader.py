import io
import os

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
        s_line = ts.readline()
        # Component
        if IsStartedWith(s_line, "[Component] ") == True:
            read_component(s_line, ts)
        elif IsStartedWith(s_line, "[Model] ") == True:
            replace_model(s_line, ts)
        elif IsStartedWith(s_line, "[Model Selector] ") == True:
            read_model_selector(s_line, ts)

# Model
def replace_model(current_line: str, ts: io.StringIO):
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

        # Clamp
        if IsStartedWith(current_line, "[GND Clamp]") == True:
            model.Clamp = True
            break
        elif IsStartedWith(current_line, "[GND_Clamp]") == True:
            model.Clamp = True
            break

        # Enable
        elif IsStartedWith(current_line, "Enable ", True) == True:
            model.Enable = current_line[len("Enable") + 1:].strip()
        elif IsStartedWith(current_line, "[Rising Waveform]") == True:
            break
        elif IsStartedWith(current_line, "[Ramp]") == True:
            break

    Models.append(model)

# Model Selector
def read_model_selector(current_line: str, ts: io.StringIO):
    if IsStartedWith(current_line, "[Model Selector] ") != True :
        return

    model_selector = ModelSelector()
    model_selector.name = current_line.split("]")(1).strip()

    while IsStartedWith(current_line, "|") == True:
        current_line = ts.ReadLine

    if ts.AtEndOfStream == True:
        return

    # Model Selector
    while (IsStartedWith(current_line, "|") is False and current_line.strip() != ""):
        model_selector.ModelSelectorItems.append(MakeModel(current_line.strip()))
        current_line = ts.ReadLine

    # ModelSelectorItem
    model_selector.FillModelReference(Models)
    ModelSelectors.append(model_selector)

def MakeModel(s_line: str) -> ModelSelectorItem:
    item = ModelSelectorItem()
    i_start = s_line.index(" ", 1)

    if i_start > 0:
        item.name = s_line[i_start:].strip()
        item.Description = s_line[i_start:].strip()

    return item

# Component
def read_component(current_line: str, ts: io.StringIO):

    Components = []
    if IsStartedWith(current_line, "[Component] ") != True:
        return

    component = Component()
    component.name = GetComponentName(current_line)
    current_line = ts.ReadLine

    if IsStartedWith(current_line, "[Manufacturer]") == True:
        component.Manufacturer = current_line.replace("[Manufacturer]", "").strip()

    current_line = ts.ReadLine

    while True:
        curLine = ts.ReadLine
        if IsStartedWith(current_line, "[Package]") == True:
            break

    # '    If IsStartedWith(curLine, "[Package]") = True Then
    # '        component.Package = Trim(Replace(Replace$(curLine, "[Package]", ""), "|", ""))
    # '    End If

    FillPackageInfo(component, ts)

    # [pin]
    while IsStartedWith(current_line, "[Pin] ") == True or ts.AtEndOfStream == True:
        current_line = ts.ReadLine

    if ts.AtEndOfStream == True:
        return

    current_line = ts.ReadLine

    # [Pin]
    while True:
        current_line = ts.ReadLine
        if IsStartedWith(current_line, "|") == True:
            break

    while (current_line == ""):
        current_line = ts.ReadLine

    while IsStartedWith(current_line, "|") == False:
        component.Pins.append(MakePinObject(current_line))
        current_line = ts.ReadLine
        if current_line == "":
            break

    Components.append(component)

def FillPackageInfo(component: Component, ts3: io.StringIO):

    with open(ts3) as ts:
        while IsStartedWith(curLine, "|") == True:
            curLine = ts.readline()

    # the component object must be created first.
    component.R_pkg.FillData("R_pkg", curLine.strip())
    curLine = ts.ReadLine
    component.L_pkg.FillData("L_pkg", curLine.strip())
    curLine = ts.ReadLine
    component.C_pkg.FillData("C_pkg", curLine.strip())

def GetComponentName(line: str) -> str:
    name = ""
    name = line.replace("[Component]", "")
    return name.strip

# Pin
def MakePinObject(line: str) -> Pin:
    pin = Pin()
    currString = ""

    currString = line.strip().Replace("\t", " ")
    pin.PinName = GetFirstParameter(currString)

    currString = currString[len(pin.PinName) + 1:].strip()
    pin.SignalName = GetFirstParameter(currString)

    currString = currString[len(pin.SignalName) + 1:].strip()
    pin.modelName = GetFirstParameter(currString)

    currString = currString[len(pin.modelName) + 1:].strip()
    pin.R_pin = GetFirstParameter(currString)

    currString = currString[len(pin.R_pin) + 1:].strip()
    pin.L_pin = GetFirstParameter(currString)

    currString = currString[len(pin.L_pin) + 1:].strip()
    pin.C_pin = GetFirstParameter(currString)

    return pin


def GetFirstParameter(sString: str) ->str:
    if sString == "":
        return ""

    data = sString.split(" ")
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