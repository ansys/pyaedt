import io
import os

# VERSION 1.0 CLASS
# BEGIN
#   MultiUse = -1  'True
#   Persistable = 0  'NotPersistable
#   DataBindingBehavior = 0  'vbNone
#   DataSourceBehavior  = 0  'vbNone
#   MTSTransactionMode  = 0  'NotAnMTSObject
# END
# Attribute VB_Name = "IBSReader"
# Attribute VB_GlobalNameSpace = False
# Attribute VB_Creatable = True
# Attribute VB_PredeclaredId = False
# Attribute VB_Exposed = False
# Attribute VB_Ext_KEY = "SavedWithClassBuilder6" ,"Yes"
# Attribute VB_Ext_KEY = "Top_Level" ,"Yes"
# Option Explicit

# Public Components As New cComponents
# Public ModelSelectors As New cModelSelectors
# Public Models As New cModels
# Public ErrMsg As String

Private Const CONST_END_LINE_VALUE As String = "*   Format: HSPICE"

def reset():
    Components = cComponents()
    ModelSelectors = cModelSelectors()
    Models = cModels()

def read_project(fileName: str) ->bool:
# On Error GoTo ErrHand

    if os.path.exists(fileName) == False:
        error_message = fileName + "does not exist."
        ReadProject = False
        raise FileExistsError(error_message)

    #Component Model
    with open(fileName,'r') as ts:
        s_line = ts.readline()
        # Component
        if IsStartedWith(s_line, "[Component] ") == True:
            ReadComponent(s_line, ts)
        elif IsStartedWith(s_line, "[Model] ") == True:
            replace_model(s_line, ts)
        elif IsStartedWith(s_line, "[Model Selector] ") == True:
            ReadModelSelector(s_line, ts)

    ts = None
    fso = None
    ReadProject = True


# ==============================================================
# Model
# ==============================================================
def replace_model(sLine: str, ts: io.StringIO):

    if IsStartedWith(sLine, "[Model] ") != True:
        return

    curLine = sLine
    oModel = cModel()

    oModel.name = curLine.split("]")(1).strip()
    curLine = ts.ReadLine.replace("\t", "").strip()

    while IsStartedWith(curLine, "Model_type") != True and ts.AtEndOfStream != True:
        curLine = ts.ReadLine.replace("\t", "").strip()

    iStart = curLine.index(" ", 1)

    if iStart > 0:
        oModel.ModelType = curLine[iStart:].strip()

    # Clamp
    while ts.AtEndOfStream != True:
        curLine = ts.ReadLine.strip.replace("clamp", "Clamp")

        # Clamp
        if IsStartedWith(curLine, "[GND Clamp]") == True:
            oModel.Clamp = True
            break
        elif IsStartedWith(curLine, "[GND_Clamp]") == True:
            oModel.Clamp = True
            break

        # Enable
        elif IsStartedWith(curLine, "Enable ", True) == True:
            oModel.Enable = curLine[len("Enable") + 1:].strip()
        elif IsStartedWith(curLine, "[Rising Waveform]") == True:
            break
        elif IsStartedWith(curLine, "[Ramp]") == True:
            break

    Me.Models.append(oModel)


# ==============================================================
# Model Selector
# ==============================================================
def ReadModelSelector(s_line: str, ts: io.StringIO):

    if IsStartedWith(s_line, "[Model Selector] ") != True :
        return

    curLine = s_line
    oModelSelector = cModelSelector()
    oModelSelector.name = curLine.split("]")(1).strip()

    while IsStartedWith(curLine, "|") == True and (ts.AtEndOfStream != True):
        curLine = ts.ReadLine

    if ts.AtEndOfStream == True:
        return

    # Model Selector
    while (IsStartedWith(curLine, "|") is False and curLine.strip() != "") and ts.AtEndOfStream != True:
        oModelSelector.ModelSelectorItems.append(MakeModel(curLine.strip()))
        curLine = ts.ReadLine

    # DELETE IT
    # ModelSelectorItem
    oModelSelector.FillModelReference(Me.Models)
    Me.ModelSelectors.append(oModelSelector)

def MakeModel(s_line: str) -> cModelSelectorItem:

    Item = cModelSelectorItem()
    i_start = s_line.index(" ", 1)

    if i_start > 0:
        Item.name = s_line[i_start:].strip()
        Item.Description = s_line[i_start:].strip()

    return Item


# ==============================================================
# Component
# ==============================================================
def ReadComponent(sLine: str, ts: io.StringIO):

    if IsStartedWith(sLine, "[Component] ") != True:
        return

    curLine = sLine
    oComponent = cComponent()
    oComponent.name = GetComponentName(sLine)
    curLine = ts.ReadLine

    if IsStartedWith(curLine, "[Manufacturer]") == True:
        oComponent.Manufacturer = curLine.replace("[Manufacturer]", "").strip()

    curLine = ts.ReadLine

    while True:
        curLine = ts.ReadLine
        if IsStartedWith(curLine, "[Package]") == True or ts.AtEndOfStream == True:
            break

    # '    If IsStartedWith(curLine, "[Package]") = True Then
    # '        oComponent.Package = Trim(Replace(Replace$(curLine, "[Package]", ""), "|", ""))
    # '    End If

    FillPackageInfo(oComponent, ts)

    # [pin]
    while IsStartedWith(curLine, "[Pin] ") == True or ts.AtEndOfStream == True:
        curLine = ts.ReadLine

    if ts.AtEndOfStream == True:
        return

    curLine = ts.ReadLine

    # [Pin]
    while True:
        curLine = ts.ReadLine
        if IsStartedWith(curLine, "|") == True and ts.AtEndOfStream != True:
            break

    while (curLine == "") and (ts.AtEndOfStream != True):
        curLine = ts.ReadLine

    if ts.AtEndOfStream == True:
        return

    while IsStartedWith(curLine, "|") == False and ts.AtEndOfStream != True:
        oComponent.Pins.append(MakePinObject(curLine))
        curLine = ts.ReadLine
        if curLine == "":
            break

    Components.append(oComponent)


def FillPackageInfo(oComponent: cComponent, ts: io.StringIO):

    curLine = ts.ReadLine

    while IsStartedWith(curLine, "|") == True and ts.AtEndOfStream != True:
        curLine = ts.ReadLine

    oComponent.R_pkg.FillData("R_pkg", curLine.strip())
    curLine = ts.ReadLine
    oComponent.L_pkg.FillData("L_pkg", curLine.strip())
    curLine = ts.ReadLine
    oComponent.C_pkg.FillData("C_pkg", curLine.strip())

#     Do
#         If IsStartedWith(curLine, "R_pkg ") = True Then
#             oComponent.R_pkg.FillData "R_pkg", curLine
#         ElseIf IsStartedWith(curLine, "L_pkg ") = True Then
#             oComponent.L_pkg.FillData "L_pkg", curLine
#         ElseIf IsStartedWith(curLine, "C_pkg ") = True Then
#             oComponent.C_pkg.FillData "C_pkg", curLine
#         End If
#         curLine = ts.ReadLine
#     Loop While IsStartedWith(curLine, "") = False

def GetComponentName(sLine: str) -> str:
    name = ""
    name = sLine.replace("[Component]", "")
    return name.strip


# cPin
def MakePinObject(sLine: str) -> cPin:

    oPin = cPin()
    iStart = 0
    iEnd = 0
    iCurr = 0
    currString = ""
    i = 0

    currString = sLine.strip().Replace("\t", " ")
    oPin.PinName = GetFirstParameter(currString)

    currString = currString[len(oPin.PinName) + 1:].strip()
    oPin.SignalName = GetFirstParameter(currString)

    currString = currString[len(oPin.SignalName) + 1:].strip()
    oPin.modelName = GetFirstParameter(currString)

    currString = currString[len(oPin.modelName) + 1:].strip()
    oPin.R_pin = GetFirstParameter(currString)

    currString = currString[len(oPin.R_pin) + 1:].strip()
    oPin.L_pin = GetFirstParameter(currString)

    currString = currString[len(oPin.L_pin) + 1:].strip()
    oPin.C_pin = GetFirstParameter(currString)

    return oPin


def GetFirstParameter(sString: str) ->str:
    if sString == "":
        return ""

    param = ""
    data = ""
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