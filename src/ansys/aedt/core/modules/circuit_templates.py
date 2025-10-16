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

# Power Sinusoidal
PowerSinusoidal = [
    "NAME:Name",
    "DataId:=",
    "",
    "Type:=",
    1,
    "Output:=",
    2,
    "NumPins:=",
    2,
    "Netlist:=",
    "",
    "CompName:=",
    "Nexxim Circuit Elements\\Independent Sources:P_SIN",
    "FDSFileName:=",
    "",
    "BtnPropFileName:=",
    "",
    [
        "NAME:Properties",
        "TextProp:=",
        ["LabelID", "HD", "Property string for netlist ID", "V@ID"],
        "ValueProp:=",
        ["ACMAG", "D", "AC magnitude for small-signal analysis (Volts)", "nan V", 0],
        "ValuePropNU:=",
        ["ACPHASE", "D", "AC phase for small-signal analysis", "0deg", 0, "deg", "AdditionalPropInfo:=", ""],
        "ValueProp:=",
        ["DC", "D", "DC voltage (Volts)", "0V", 0],
        "ValuePropNU:=",
        ["VO", "D", "Power offset from zero watts", "0W", 0, "W", "AdditionalPropInfo:=", ""],
        "ValueProp:=",
        ["POWER", "D", "Available power of the source above VO", "0W", 0],
        "ValueProp:=",
        ["FREQ", "D", "Frequency (Hz)", "1GHz", 0],
        "ValueProp:=",
        ["TD", "D", "Delay to start of sine wave (seconds)", "0s", 0],
        "ValueProp:=",
        ["ALPHA", "D", "Damping factor (1/seconds)", "0", 0],
        "ValuePropNU:=",
        ["THETA", "D", "Phase delay", "0deg", 0, "deg", "AdditionalPropInfo:=", ""],
        "ValueProp:=",
        [
            "TONE",
            "D",
            "Frequency (Hz) to use for harmonic balance analysis, should be a "
            "submultiple of (or equal to) the driving frequency and should also be "
            "included in the HB analysis setup",
            "0Hz",
            0,
        ],
        "TextProp:=",
        ["ModelName", "SHD", "", "P_SIN"],
        "ButtonProp:=",
        ["CosimDefinition", "D", "", "Edit", "Edit", 40501, "ButtonPropClientData:=", []],
        "MenuProp:=",
        ["CoSimulator", "D", "", "DefaultNetlist", 0],
        [
            "Netlist",
            0,
            0,
            "V@ID %0 %1 *DC(DC=@DC) POWER SIN(?VO(@VO) ?POWER(@POWER) ?FREQ(@FREQ) ?TD(@TD) "
            "?ALPHA(@ALPHA) ?THETA(@THETA)) *TONE(TONE=@TONE) *ACMAG(AC @ACMAG @ACPHASE)",
        ],
    ],
]

PSinProps = [
    "ACMAG",
    "ACPHASE",
    "DC",
    "VO",
    "POWER",
    "FREQ",
    "TD",
    "ALPHA",
    "THETA",
    "TONE",
    "CosimDefinition",
    "CoSimulator",
    "CoSimulator/Choices",
    "Netlist",
]

# Voltage Sinusoidal
VoltageSinusoidal = [
    "NAME:Name",
    "DataId:=",
    "",
    "Type:=",
    1,
    "Output:=",
    0,
    "NumPins:=",
    2,
    "Netlist:=",
    "",
    "CompName:=",
    "Nexxim Circuit Elements\\Independent Sources:V_SIN",
    "FDSFileName:=",
    "",
    "BtnPropFileName:=",
    "",
    [
        "NAME:Properties",
        "TextProp:=",
        ["LabelID", "HD", "Property string for netlist ID", "V@ID"],
        "ValueProp:=",
        ["ACMAG", "D", "AC magnitude for small-signal analysis (Volts)", "nan V", 0],
        "ValuePropNU:=",
        ["ACPHASE", "D", "AC phase for small-signal analysis", "0deg", 0, "deg"],
        "ValueProp:=",
        ["DC", "D", "DC voltage (Volts)", "0V", 0],
        "ValueProp:=",
        ["VA", "D", "Voltage amplitude (Volts)", "0V", 0],
        "ValuePropNU:=",
        ["VO", "D", "Voltage offset from zero (Volts)", "0V", 0, "V"],
        "ValueProp:=",
        ["FREQ", "D", "Frequency (Hz)", "1GHz", 0],
        "ValueProp:=",
        ["TD", "D", "Delay to start of sine wave (seconds)", "0s", 0],
        "ValueProp:=",
        ["ALPHA", "D", "Damping factor (1/seconds)", "0", 0],
        "ValuePropNU:=",
        ["THETA", "D", "Phase delay", "0deg", 0, "deg"],
        "ValueProp:=",
        [
            "TONE",
            "D",
            "Frequency (Hz) to use for harmonic balance analysis, should be a "
            "submultiple of (or equal to) the driving frequency and should also be "
            "included in the HB analysis setup",
            "0Hz",
            0,
        ],
        "TextProp:=",
        ["ModelName", "SHD", "", "V_SIN"],
        "ButtonProp:=",
        ["CosimDefinition", "D", "", "", "Edit", 40501, "ButtonPropClientData:=", []],
        "MenuProp:=",
        ["CoSimulator", "D", "", "DefaultNetlist", 0],
        [
            "Netlist",
            0,
            0,
            "V@ID %0 %1 *DC(DC=@DC) SIN(?VO(@VO) ?VA(@VA) ?FREQ(@FREQ) ?TD(@TD) ?ALPHA(@ALPHA) ?THETA(@THETA))"
            " *TONE(TONE=@TONE) *ACMAG(AC @ACMAG @ACPHASE)",
        ],
    ],
]

VSinProps = [
    "ACMAG",
    "ACPHASE",
    "DC",
    "VA",
    "VO",
    "FREQ",
    "TD",
    "ALPHA",
    "THETA",
    "TONE",
    "CosimDefinition",
    "CoSimulator",
    "CoSimulator/Choices",
    "Netlist",
]

# Current Sinusoidal
CurrentSinusoidal = [
    "NAME:Name",
    "DataId:=",
    "",
    "Type:=",
    1,
    "Output:=",
    1,
    "NumPins:=",
    2,
    "Netlist:=",
    "",
    "CompName:=",
    "Nexxim Circuit Elements\\Independent Sources:I_SIN",
    "FDSFileName:=",
    "",
    "BtnPropFileName:=",
    "",
    [
        "NAME:Properties",
        "TextProp:=",
        ["LabelID", "HD", "Property string for netlist ID", "I@ID"],
        "ValueProp:=",
        ["ACMAG", "D", "AC magnitude for small-signal analysis (Amps)", "nan A", 0],
        "ValuePropNU:=",
        ["ACPHASE", "D", "AC phase for small-signal analysis", "0deg", 0, "deg", "AdditionalPropInfo:=", ""],
        "ValueProp:=",
        ["DC", "D", "DC current (Amps)", "0A", 0],
        "ValuePropNU:=",
        ["VO", "D", "Current offset (Amps)", "0A", 0, "A", "AdditionalPropInfo:=", ""],
        "ValueProp:=",
        ["VA", "D", "Current amplitude (Amps)", "0A", 0],
        "ValueProp:=",
        ["FREQ", "D", "Frequency (Hz)", "1GHz", 0],
        "ValueProp:=",
        ["TD", "D", "Delay to start of sine wave (seconds)", "0s", 0],
        "ValueProp:=",
        ["ALPHA", "D", "Damping factor (1/seconds)", "0", 0],
        "ValuePropNU:=",
        ["THETA", "D", "Phase delay", "0deg", 0, "deg"],
        "ValueProp:=",
        ["M", "D", "Multiplier for simulating multiple parallel current sources", "1", 0],
        "ValueProp:=",
        [
            "TONE",
            "D",
            "Frequency (Hz) to use for harmonic balance analysis, should be a "
            "submultiple of (or equal to) the driving frequency and should also be "
            "included in the HB analysis setup",
            "0Hz",
            0,
        ],
        "TextProp:=",
        ["ModelName", "SHD", "", "I_SIN"],
        "ButtonProp:=",
        ["CosimDefinition", "D", "", "", "Edit", 40501, "ButtonPropClientData:=", []],
        "MenuProp:=",
        ["CoSimulator", "D", "", "DefaultNetlist", 0],
        [
            "Netlist",
            0,
            0,
            "I@ID %0 %1 *DC(DC=@DC) SIN(?VO(@VO) ?VA(@VA) ?FREQ(@FREQ) ?TD(@TD) ?ALPHA(@ALPHA) ?THETA(@THETA) *M(M=@M))"
            "*TONE(TONE=@TONE) *ACMAG(AC @ACMAG @ACPHASE)",
        ],
    ],
]

ASinProps = [
    "ACMAG",
    "ACPHASE",
    "DC",
    "VO",
    "VA",
    "FREQ",
    "TD",
    "ALPHA",
    "THETA",
    "M",
    "TONE",
    "CosimDefinition",
    "CoSimulator",
    "CoSimulator/Choices",
    "Netlist",
]


# Power IQ
iq_properties = [
    "NAME:Properties",
    "TextProp:=",
    ["LabelID", "HD", "Property String for netlist ID", "A@ID"],
    "ValueProp:=",
    ["FC", "D", "Carrier frequency (Hertz)", "1GHz", 0],
    "ValueProp:=",
    ["TS", "D", "Sampling time (Second)", "nan s", 0],
    "ValueProp:=",
    ["DC", "D", "Source value at DC (Volt)", "0V", 0],
    "ValueProp:=",
    ["R", "D", "Repeat from time (Second)", "nan s", 0],
    "ValueProp:=",
    ["TD", "D", "Time delay (Second)", "0s", 0],
    "ValueProp:=",
    ["V", "D", "Carrier amplitude, voltage-based (Volts)", "1V", 0],
    "ValueProp:=",
    ["VA", "D", "Carrier amplitude, power-based (Watts)", "nan W", 0],
    "ValueProp:=",
    ["VO", "D", "Carrier amplitude offset (Volts or Watts)", "0", 0],
    "ValueProp:=",
    ["RZ", "D", "Real carrier impedance (Ohm)", "50ohm", 0],
    "ValueProp:=",
    ["IZ", "D", "Imaginary carrier impedance (Ohm)", "0ohm", 0],
    "ValueProp:=",
    ["ALPHA", "D", "Damping factor (1/Seconds)", "0", 0],
    "ValuePropNU:=",
    ["THETA", "D", "Phase delay", "0deg", 0, "deg"],
    "ValueProp:=",
    ["TONE", "D", "Source tone for HB analysis", "nan ", 0],
]

for i in range(1, 21):
    iq_properties.append("ValueProp:=")
    iq_properties.append(
        ["time" + str(i), "D", "Timepoint value where the corresponding voltage values are valid", "0s", 0]
    )
    iq_properties.append("ValueProp:=")
    iq_properties.append(["ival" + str(i), "D", "I value at the corresponding timepoint (Volts)", "0V", 0])
    iq_properties.append("ValueProp:=")
    iq_properties.append(["qval" + str(i), "D", "Q value at the corresponding timepoint (Volts)", "0V", 0])

power_iq_properties = iq_properties + [
    "TextProp:=",
    ["COMPONENT", "RHD", "", "vsiq_source"],
    "MenuProp:=",
    ["CoSimulator", "D", "", "DefaultNetlist", 0],
    "ButtonProp:=",
    ["CosimDefinition", "D", "", "", "Edit", 40501, "ButtonPropClientData:=", []],
    "ButtonProp:=",
    ["file", "OD", "", "", "", 4, "ButtonPropClientData:=", []],
    "ButtonProp:=",
    ["IQData", "OD", "", "IQData", "IQData", 2, "ButtonPropClientData:=", []],
    [
        "Netlist",
        0,
        0,
        "A@ID %0  %1 *FC(FC=@FC) *TS(TS=@TS) *DC(DC=@DC) *R(R=@R) *TD(TD=@TD) *V(V=@V) *VA("
        "VA=@VA) "
        "*VO(VO=@VO) *RZ(RZ=@RZ) *IZ(IZ=@IZ) *ALPHA(ALPHA=@ALPHA) *THETA(THETA=@THETA) "
        "*TONE(TONE=@TONE) *FILE(FILE=@FILE) TIMES=[?time1(@time1) *time2(@time2) *time3("
        "@time3) *time4(@time4) *time5(@time5) *time6(@time6) *time7(@time7) *time8(@time8) "
        "*time9( @time9) *time10(@time10) *time11(@time11) *time12(@time12) *time13(@time13) "
        "*time14(@time14) *time15(@time15) *time16(@time16) *time17(@time17) *time18(@time18)"
        "*time19(@time19) *time20(@time20)] I_T=[?ival1(@ival1) *ival2(@ival2) *ival3("
        "@ival3) *ival4(@ival4) *ival5(@ival5) *ival6(@ival6) *ival7(@ival7) *ival8(@ival8) "
        "*ival9(@ival9) *ival10(@ival10) *ival11(@ival11) *ival12(@ival12) *ival13(@ival13) "
        "*ival14(@ival14) *ival15(@ival15) *ival16(@ival16) *ival17(@ival17) *ival18("
        "@ival18) *ival19(@ival19) *ival20(@ival20)] Q_T=[?qval1(@qval1) *qval2(@qval2) "
        "*qval3(@qval3) *qval4(@qval4) *qval5(@qval5) *qval6(@qval6) *qval7(@qval7) *qval8("
        "@qval8) *qval9(@qval9) *qval10(@qval10) *qval11(@qval11) *qval12(@qval12) *qval13("
        "@qval13) *qval14(@qval14) *qval15(@qval15) *qval16(@qval16) *qval17(@qval17) "
        "*qval18(@qval18) *qval19(@qval19) *qval20(@qval20)] COMPONENT=@COMPONENT",
    ],
]

PowerIQ = [
    "NAME:Name",
    "DataId:=",
    "",
    "Type:=",
    5,
    "Output:=",
    2,
    "NumPins:=",
    2,
    "Netlist:=",
    "",
    "CompName:=",
    "Nexxim Circuit Elements\\Independent Sources:VSIQ",
    "FDSFileName:=",
    "",
    "BtnPropFileName:=",
    "",
    power_iq_properties,
]

PowerIQProps = [
    "FC",
    "TS",
    "DC",
    "R",
    "TD",
    "V",
    "VA",
    "VO",
    "RZ",
    "IZ",
    "ALPHA",
    "THETA",
    "TONE",
    "time1",
    "ival1",
    "qval1",
    "time2",
    "ival2",
    "qval2",
    "time3",
    "ival3",
    "qval3",
    "time4",
    "ival4",
    "qval4",
    "time5",
    "ival5",
    "qval5",
    "time6",
    "ival6",
    "qval6",
    "time7",
    "ival7",
    "qval7",
    "time8",
    "ival8",
    "qval8",
    "time9",
    "ival9",
    "qval9",
    "time10",
    "ival10",
    "qval10",
    "time11",
    "ival11",
    "qval11",
    "time12",
    "ival12",
    "qval12",
    "time13",
    "ival13",
    "qval13",
    "time14",
    "ival14",
    "qval14",
    "time15",
    "ival15",
    "qval15",
    "time16",
    "ival16",
    "qval16",
    "time17",
    "ival17",
    "qval17",
    "time18",
    "ival18",
    "qval18",
    "time19",
    "ival19",
    "qval19",
    "time20",
    "ival20",
    "qval20",
    "CoSimulator",
    "CoSimulator/Choices",
    "CosimDefinition",
    "file",
    "IQData",
    "Netlist",
]

# Voltage Frequency dependent
VoltageFrequency = [
    "NAME:Name",
    "DataId:=",
    "",
    "Type:=",
    17,
    "Output:=",
    0,
    "NumPins:=",
    2,
    "Netlist:=",
    "",
    "CompName:=",
    "Nexxim Circuit Elements\\Independent Sources:V_PWL_F",
    "FDSFileName:=",
    "",
    "BtnPropFileName:=",
    "",
    [
        "NAME:Properties",
        "TextProp:=",
        ["LabelID", "HD", "Property string for netlist ID", "V@ID"],
        "ButtonProp:=",
        ["FreqDependentSourceData", "D", "Frequency Dependent Source Data", "", "", 7, "ButtonPropClientData:=", []],
        "TextProp:=",
        ["COMPONENT", "RHD", "", "vsource_freq"],
        "ButtonProp:=",
        ["CosimDefinition", "SD", "", "Edit", "Edit", 0, "ButtonPropClientData:=", []],
        "MenuProp:=",
        ["CoSimulator", "D", "", "DefaultNetlist", 0],
        ["Netlist", 0, 0, "V@ID %0 %1 *FreqDependentSourceData(@FreqDependentSourceData)"],
    ],
]

VoltageFrequencyProps = [
    "frequencies",
    "vmag",
    "vang",
    "vreal",
    "vimag",
    "fds_filename",
    "magnitude_angle",
    "FreqDependentSourceData",
    "CosimDefinition",
    "CoSimulator",
    "CoSimulator/Choices",
    "Netlist",
]

# Voltage DC
VoltageDC = [
    "NAME:Name",
    "DataId:=",
    "",
    "Type:=",
    0,
    "Output:=",
    0,
    "NumPins:=",
    2,
    "Netlist:=",
    "",
    "CompName:=",
    "Nexxim Circuit Elements\\Independent Sources:V_DC",
    "FDSFileName:=",
    "",
    "BtnPropFileName:=",
    "",
    [
        "NAME:Properties",
        "TextProp:=",
        ["LabelID", "HD", "Property string for netlist ID", "V@ID"],
        "ValueProp:=",
        ["ACMAG", "D", "AC magnitude for small-signal analysis (Volts)", "nan V", 0],
        "ValuePropNU:=",
        ["ACPHASE", "D", "AC phase for small-signal analysis", "0deg", 0, "deg"],
        "ValueProp:=",
        ["DC", "D", "DC voltage (Volts)", "0V", 0],
        "TextProp:=",
        ["ModelName", "SHD", "", "V_DC"],
        "MenuProp:=",
        ["CoSimulator", "D", "", "DefaultNetlist", 0],
        "ButtonProp:=",
        ["CosimDefinition", "D", "", "", "Edit", 40501, "ButtonPropClientData:=", []],
        "ButtonProp:=",
        ["Noise", "OD", "", "Noise", "Noise", 0, "ButtonPropClientData:=", []],
        "TextProp:=",
        ["ModelName", "SHD", "", "V_DC"],
        "ButtonProp:=",
        ["CosimDefinition", "D", "", "Edit", "Edit", 40501, "ButtonPropClientData:=", []],
        "MenuProp:=",
        ["CoSimulator", "D", "", "DefaultNetlist", 0],
        [
            "Netlist",
            0,
            0,
            "V@ID %0 %1 *DC(DC=@DC) *ACMAG(AC @ACMAG @ACPHASE)",
        ],
    ],
]

DCProps = [
    "ACMAG",
    "ACPHASE",
    "DC",
    "POWER",
    "CosimDefinition",
    "CoSimulator",
    "CoSimulator/Choices",
    "Noise",
    "Netlist",
]


class SourceKeys:
    """Provides source keys."""

    SourceTemplates = {
        "PowerSin": PowerSinusoidal,
        "PowerIQ": PowerIQ,
        "VoltageFrequencyDependent": VoltageFrequency,
        "VoltageDC": VoltageDC,
        "VoltageSin": VoltageSinusoidal,
        "CurrentSin": CurrentSinusoidal,
    }

    SourceProps = {
        "PowerSin": PSinProps,
        "PowerIQ": PowerIQProps,
        "VoltageFrequencyDependent": VoltageFrequencyProps,
        "VoltageDC": DCProps,
        "VoltageSin": VSinProps,
        "CurrentSin": ASinProps,
    }

    SourceNames = [
        "PowerSin",
        "PowerIQ",
        "VoltageFrequencyDependent",
        "VoltageDC",
        "VoltageSin",
        "CurrentSin",
    ]
