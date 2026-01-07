# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 - 2026 ANSYS, Inc. and/or its affiliates.
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

from __future__ import absolute_import

from ansys.aedt.core.generic.constants import DynamicMeta


class HfssConstants(metaclass=DynamicMeta):
    NAME = "HFSS"
    model_name = "HFSSModel"
    solution_default = "HFSS Terminal Network"
    solution_types = {
        "Modal": {
            "name": "HFSS Modal Network",
            "options": None,
            "report_type": "Modal Solution Data",
            "default_setup": 1,
            "default_adaptive": "LastAdaptive",
            "intrinsics": ["Freq", "Phase"],
        },
        "Terminal": {
            "name": "HFSS Terminal Network",
            "options": None,
            "report_type": "Terminal Solution Data",
            "default_setup": 1,
            "default_adaptive": "LastAdaptive",
            "intrinsics": ["Freq", "Phase"],
        },
        "DrivenModal": {
            "name": "DrivenModal",
            "options": None,
            "report_type": "Modal Solution Data",
            "default_setup": 1,
            "default_adaptive": "LastAdaptive",
            "intrinsics": ["Freq", "Phase"],
        },
        "DrivenTerminal": {
            "name": "DrivenTerminal",
            "options": None,
            "report_type": "Terminal Solution Data",
            "default_setup": 1,
            "default_adaptive": "LastAdaptive",
            "intrinsics": ["Freq", "Phase"],
        },
        "Transient Network": {
            "name": "Transient Network",
            "options": None,
            "report_type": "Terminal Solution Data",
            "default_setup": 3,
            "default_adaptive": "Transient",
            "intrinsics": ["Time"],
        },
        "Transient Composite": {
            "name": "Transient Composite",
            "options": None,
            "report_type": "Terminal Solution Data",
            "default_setup": 3,
            "default_adaptive": "Transient",
            "intrinsics": ["Time"],
        },
        "Transient": {
            "name": "Transient",
            "options": None,
            "report_type": "Terminal Solution Data",
            "default_setup": 3,
            "default_adaptive": "Transient",
            "intrinsics": ["Time"],
        },
        "Eigenmode": {
            "name": "Eigenmode",
            "options": None,
            "report_type": "EigenMode Parameters",
            "default_setup": 2,
            "default_adaptive": "LastAdaptive",
            "intrinsics": ["Phase"],
        },
        "Characteristic": {
            "name": "Characteristic Mode",
            "options": None,
            "report_type": None,
            "default_setup": None,
            "default_adaptive": None,
        },
        "Characteristic Mode": {
            "name": "Characteristic Mode",
            "options": None,
            "report_type": None,
            "default_setup": None,
            "default_adaptive": None,
        },
        "SBR+": {
            "name": "SBR+",
            "options": None,
            "report_type": "Modal Solution Data",
            "default_setup": 4,
            "default_adaptive": "Sweep",
            "intrinsics": ["Freq", "Phase"],
        },
    }
    mesher = "MeshSetup"
    default_material = "vacuum"
    report_templates = [
        "Modal Solution Data",
        "Terminal Solution Data",
        "Eigenmode Parameters",
        "Fields",
        "Far Fields",
        "Emissions",
        "Near Fields",
        "Antenna Parameters",
    ]
    property_tabs = {"boundary": "HfssTab", "excitation": "HfssTab", "setup": "HfssTab", "mesh": "MeshSetupTab"}


class Q3dConstants(metaclass=DynamicMeta):
    NAME = "Q3D Extractor"
    model_name = "Q3DModel"
    solution_default = "Q3D Extractor"
    solution_types = {
        "Q3D Extractor": {
            "name": None,
            "options": None,
            "report_type": "Matrix",
            "default_setup": 14,
            "default_adaptive": "LastAdaptive",
            "intrinsics": ["Freq", "Phase"],
        }
    }
    mesher = "MeshSetup"
    default_material = "copper"
    report_templates = ["Matrix", "CG Fields", "DC R/L Fields", "AC R/L Fields"]
    property_tabs = {"boundary": "Q3D", "excitation": "Q3D", "setup": "General", "mesh": "Q3D"}


class Extractor2dConstants(metaclass=DynamicMeta):
    NAME = "2D Extractor"
    model_name = "2DExtractorModel"
    solution_default = "Open"
    solution_types = {
        "Open": {
            "name": "Open",
            "options": None,
            "report_type": "Matrix",
            "default_setup": 30,
            "default_adaptive": "LastAdaptive",
            "intrinsics": ["Freq", "Phase"],
        },
        "Closed": {
            "name": "Closed",
            "options": None,
            "report_type": "Matrix",
            "default_setup": 31,
            "default_adaptive": "LastAdaptive",
            "intrinsics": ["Freq", "Phase"],
        },
    }
    mesher = "MeshSetup"
    default_material = "copper"
    report_templates = ["Matrix", "CG Fields", "RL Fields"]
    property_tabs = {"boundary": "2DExtractor", "excitation": "2DExtractor", "setup": "General", "mesh": "2DExtractor"}


class IcepakConstants(metaclass=DynamicMeta):
    NAME = "Icepak"
    model_name = "IcepakModel"
    solution_default = "SteadyState"
    solution_types = {
        "SteadyState": {
            "name": "SteadyState",
            "options": "TemperatureAndFlow",
            "report_type": "Monitor",
            "default_setup": 11,
            "default_adaptive": "SteadyState",
        },
        "Transient": {
            "name": "Transient",
            "options": "TemperatureAndFlow",
            "report_type": "Monitor",
            "default_setup": 36,
            "default_adaptive": "Transient",
        },
    }
    mesher = "MeshRegion"
    default_material = "air"
    report_templates = ["Monitor", "Fields"]
    property_tabs = {"boundary": "Icepak", "excitation": "Icepak", "setup": "Icepak", "mesh": "Icepak"}


class IcepakFeaConstants(metaclass=DynamicMeta):
    NAME = "IcepakFEA"
    model_name = "MechanicalModel"
    solution_default = "Thermal"
    solution_types = {
        "Thermal": {
            "name": "Thermal",
            "options": None,
            "report_type": "Fields",
            "default_setup": 32,
            "default_adaptive": "Solution",
        },
        "Steady-State Thermal": {
            "name": "Steady-State Thermal",
            "options": None,
            "report_type": "Fields",
            "default_setup": 32,
            "default_adaptive": "Solution",
        },
        "Transient Thermal": {
            "name": "Transient Thermal",
            "options": None,
            "report_type": "Fields",
            "default_setup": 57,
            "default_adaptive": "Solution",
        },
        "Modal": {"name": "Modal", "options": None, "report_type": None, "default_setup": 33, "default_adaptive": None},
        "Structural": {
            "name": "Structural",
            "options": None,
            "report_type": "Fields",
            "default_setup": 39,
            "default_adaptive": "Solution",
        },
    }
    mesher = "MeshSetup"
    default_material = "copper"
    report_templates = ["Standard", "Fields"]
    __versioned = {"2025.2": {"NAME": "Mechanical"}}
    property_tabs = {"boundary": "IcepakFEA", "excitation": "IcepakFEA", "setup": "IcepakFEA", "mesh": "IcepakFEA"}


class Hfss3dLayoutConstants(metaclass=DynamicMeta):
    NAME = "HFSS 3D Layout Design"

    model_name = "PlanarEMCircuit"
    solution_default = "HFSS3DLayout"
    solution_types = {
        "HFSS3DLayout": {
            "name": None,
            "options": None,
            "report_type": "Standard",
            "default_setup": 29,
            "default_adaptive": None,
            "intrinsics": ["Freq", "Phase"],
        },
        "SiwaveDC3DLayout": {
            "name": None,
            "options": None,
            "report_type": "Standard",
            "default_setup": 40,
            "default_adaptive": None,
        },
        "SiwaveAC3DLayout": {
            "name": None,
            "options": None,
            "report_type": "Standard",
            "default_setup": 41,
            "default_adaptive": None,
            "intrinsics": ["Freq"],
        },
        "LNA3DLayout": {
            "name": None,
            "options": None,
            "report_type": "Standard",
            "default_setup": 42,
            "default_adaptive": None,
            "intrinsics": ["Freq"],
        },
    }
    mesher = "SolveSetups"
    default_material = "copper"
    report_templates = ["Standard", "Fields", "Spectrum"]


class TwinbuilderConstants(metaclass=DynamicMeta):
    NAME = "Twin Builder"

    model_name = "SimplorerCircuit"
    solution_default = "TR"
    solution_types = {
        "TR": {
            "name": None,
            "options": None,
            "report_type": "Standard",
            "default_setup": 35,
            "default_adaptive": None,
            "intrinsics": ["Time"],
        },
        "AC": {
            "name": None,
            "options": None,
            "report_type": "Standard",
            "default_setup": None,
            "default_adaptive": None,
            "intrinsics": ["Freq"],
        },
        "DC": {
            "name": None,
            "options": None,
            "report_type": "Standard",
            "default_setup": None,
            "default_adaptive": None,
        },
    }
    report_templates = ["Standard", "Spectrum"]


class RmxprtConstants(metaclass=DynamicMeta):
    NAME = "RMxprtSolution"

    model_name = "RMxprtDesign"
    solution_default = "GRM"
    solution_types = {
        "GRM": {"name": "GRM", "options": None, "report_type": None, "default_setup": 34, "default_adaptive": None},
        "IRIM": {"name": "IRIM", "options": None, "report_type": None, "default_setup": 34, "default_adaptive": None},
        "ORIM": {"name": "ORIM", "options": None, "report_type": None, "default_setup": 34, "default_adaptive": None},
        "SRIM": {"name": "SRIM", "options": None, "report_type": None, "default_setup": 34, "default_adaptive": None},
        "WRIM": {"name": "WRIM", "options": None, "report_type": None, "default_setup": 34, "default_adaptive": None},
        "DFIG": {"name": "DFIG", "options": None, "report_type": None, "default_setup": 43, "default_adaptive": None},
        "AFIM": {"name": "AFIM", "options": None, "report_type": None, "default_setup": 34, "default_adaptive": None},
        "HM": {"name": "HM", "options": None, "report_type": None, "default_setup": 34, "default_adaptive": None},
        "RFSM": {"name": "RFSM", "options": None, "report_type": None, "default_setup": 34, "default_adaptive": None},
        "RASM": {"name": "RASM", "options": None, "report_type": None, "default_setup": 34, "default_adaptive": None},
        "RSM": {"name": "RSM", "options": None, "report_type": None, "default_setup": 34, "default_adaptive": None},
        "ISM": {"name": "ISM", "options": None, "report_type": None, "default_setup": 34, "default_adaptive": None},
        "APSM": {"name": "APSM", "options": None, "report_type": None, "default_setup": 34, "default_adaptive": None},
        "IBDM": {"name": "IBDM", "options": None, "report_type": None, "default_setup": 34, "default_adaptive": None},
        "ABDM": {"name": "ABDM", "options": None, "report_type": None, "default_setup": 34, "default_adaptive": None},
        "TPIM": {"name": "TPIM", "options": None, "report_type": None, "default_setup": 44, "default_adaptive": None},
        "SPIM": {"name": "SPIM", "options": None, "report_type": None, "default_setup": 45, "default_adaptive": None},
        "TPSM": {"name": "SYNM", "options": None, "report_type": None, "default_setup": 46, "default_adaptive": None},
        "BLDC": {"name": "BLDC", "options": None, "report_type": None, "default_setup": 47, "default_adaptive": None},
        "ASSM": {"name": "ASSM", "options": None, "report_type": None, "default_setup": 48, "default_adaptive": None},
        "PMDC": {"name": "PMDC", "options": None, "report_type": None, "default_setup": 49, "default_adaptive": None},
        "SRM": {"name": "SRM", "options": None, "report_type": None, "default_setup": 50, "default_adaptive": None},
        "LSSM": {"name": "LSSM", "options": None, "report_type": None, "default_setup": 51, "default_adaptive": None},
        "UNIM": {"name": "UNIM", "options": None, "report_type": None, "default_setup": 52, "default_adaptive": None},
        "DCM": {"name": "DCM", "options": None, "report_type": None, "default_setup": 53, "default_adaptive": None},
        "CPSM": {"name": "CPSM", "options": None, "report_type": None, "default_setup": 54, "default_adaptive": None},
        "NSSM": {"name": "NSSM", "options": None, "report_type": None, "default_setup": 55, "default_adaptive": None},
    }
    report_templates = []


class Maxwell3dConstants(metaclass=DynamicMeta):
    NAME = "Maxwell 3D"

    model_name = "Maxwell3DModel"
    solution_default = "Magnetostatic"
    solution_types = {
        "Magnetostatic": {
            "name": "Magnetostatic",
            "options": None,
            "report_type": "Magnetostatic",
            "default_setup": 6,
            "default_adaptive": "LastAdaptive",
        },
        "EddyCurrent": {
            "name": "EddyCurrent",
            "options": None,
            "report_type": "EddyCurrent",
            "default_setup": 7,
            "default_adaptive": "LastAdaptive",
            "intrinsics": ["Freq", "Phase"],
        },
        "AC Magnetic": {
            "name": "AC Magnetic",
            "options": None,
            "report_type": "AC Magnetic",
            "default_setup": 7,
            "default_adaptive": "LastAdaptive",
            "intrinsics": ["Freq", "Phase"],
        },
        "DCBiasedEddyCurrent": {
            "name": "DCBiasedEddyCurrent",
            "options": None,
            "report_type": "EddyCurrent",
            "default_setup": 60,
            "default_adaptive": "LastAdaptive",
            "intrinsics": ["Freq", "Phase"],
        },
        "AC Magnetic with DC": {
            "name": "DCBiasedEddyCurrent",
            "options": None,
            "report_type": "EddyCurrent",
            "default_setup": 60,
            "default_adaptive": "LastAdaptive",
            "intrinsics": ["Freq", "Phase"],
        },
        "Transient": {
            "name": "Transient",
            "options": None,
            "report_type": "Transient",
            "default_setup": 5,
            "default_adaptive": "Transient",
            "intrinsics": ["Time"],
        },
        "TransientAPhiFormulation": {
            "name": "TransientAPhiFormulation",
            "options": None,
            "report_type": "Transient",
            "default_setup": 56,
            "default_adaptive": "Transient",
            "intrinsics": ["Time"],
        },
        "Transient APhi": {
            "name": "Transient APhi",
            "options": None,
            "report_type": "Transient",
            "default_setup": 56,
            "default_adaptive": "Transient",
            "intrinsics": ["Time"],
        },
        "Electrostatic": {
            "name": "Electrostatic",
            "options": None,
            "report_type": "Electrostatic",
            "default_setup": 8,
            "default_adaptive": "LastAdaptive",
        },
        "ACConduction": {
            "name": "ACConduction",
            "options": None,
            "report_type": None,
            "default_setup": 59,
            "default_adaptive": "LastAdaptive",
            "intrinsics": ["Freq", "Phase"],
        },
        "AC Conduction": {
            "name": "ACConduction",
            "options": None,
            "report_type": None,
            "default_setup": 59,
            "default_adaptive": "LastAdaptive",
            "intrinsics": ["Freq", "Phase"],
        },
        "DCConduction": {
            "name": "DCConduction",
            "options": None,
            "report_type": None,
            "default_setup": 58,
            "default_adaptive": "LastAdaptive",
        },
        "DC Conduction": {
            "name": "DCConduction",
            "options": None,
            "report_type": None,
            "default_setup": 58,
            "default_adaptive": "LastAdaptive",
        },
        "ElectroDCConduction": {
            "name": "ElectroDCConduction",
            "options": None,
            "report_type": None,
            "default_setup": 9,
            "default_adaptive": "LastAdaptive",
        },
        "Electric DC Conduction": {
            "name": "Electric DC Conduction",
            "options": None,
            "report_type": None,
            "default_setup": 9,
            "default_adaptive": "LastAdaptive",
        },
        "ElectricTransient": {
            "name": "ElectricTransient",
            "options": None,
            "report_type": None,
            "default_setup": 10,
            "default_adaptive": "Transient",
            "intrinsics": ["Time"],
        },
        "Electric Transient": {
            "name": "ElectricTransient",
            "options": None,
            "report_type": None,
            "default_setup": 10,
            "default_adaptive": "Transient",
            "intrinsics": ["Time"],
        },
    }
    mesher = "MeshSetup"
    default_material = "vacuum"
    report_templates = [
        "Transient",
        "EddyCurrent",
        "Magnetostatic",
        "Electrostatic",
        "DCConduction",
        "ElectroDCConduction",
        "ElectricTransient",
        "Fields",
        "Spectrum",
    ]
    property_tabs = {
        "boundary": "Maxwell3D",
        "excitation": "Maxwell3D",
        "setup": ["General", "Convergence", "Solver"],
        "mesh": "Maxwell3D",
    }


class Maxwell2dConstants(metaclass=DynamicMeta):
    NAME = "Maxwell 2D"

    model_name = "Maxwell2DModel"
    solution_default = "Magnetostatic"
    solution_types = {
        "Magnetostatic": {
            "name": "Magnetostatic",
            "options": "XY",
            "report_type": "Magnetostatic",
            "default_setup": 6,
            "default_adaptive": "LastAdaptive",
        },
        "EddyCurrent": {
            "name": "EddyCurrent",
            "options": "XY",
            "report_type": "EddyCurrent",
            "default_setup": 7,
            "default_adaptive": "LastAdaptive",
            "intrinsics": ["Freq", "Phase"],
        },
        "AC Magnetic": {
            "name": "EddyCurrent",
            "options": "XY",
            "report_type": "EddyCurrent",
            "default_setup": 7,
            "default_adaptive": "LastAdaptive",
            "intrinsics": ["Freq", "Phase"],
        },
        "Transient": {
            "name": "Transient",
            "options": "XY",
            "report_type": "Transient",
            "default_setup": 5,
            "default_adaptive": "Transient",
            "intrinsics": ["Time"],
        },
        "Electrostatic": {
            "name": "Electrostatic",
            "options": "XY",
            "report_type": "Electrostatic",
            "default_setup": 8,
            "default_adaptive": "LastAdaptive",
        },
        "DCConduction": {
            "name": "DCConduction",
            "options": "XY",
            "report_type": "DCConduction",
            "default_setup": 58,
            "default_adaptive": "LastAdaptive",
        },
        "DC Conduction": {
            "name": "DCConduction",
            "options": "XY",
            "report_type": "DC Conduction",
            "default_setup": 58,
            "default_adaptive": "LastAdaptive",
        },
        "ACConduction": {
            "name": "ACConduction",
            "options": "XY",
            "report_type": "ACConduction",
            "default_setup": 59,
            "default_adaptive": "LastAdaptive",
            "intrinsics": ["Freq", "Phase"],
        },
        "AC Conduction": {
            "name": "ACConduction",
            "options": "XY",
            "report_type": "AC Conduction",
            "default_setup": 59,
            "default_adaptive": "LastAdaptive",
            "intrinsics": ["Freq", "Phase"],
        },
    }
    mesher = "MeshSetup"
    default_material = "vacuum"
    report_templates = [
        "Transient",
        "EddyCurrent",
        "Magnetostatic",
        "Electrostatic",
        "ElectricTransient",
        "ElectroDCConduction",
        "Fields",
        "Spectrum",
    ]
    property_tabs = {
        "boundary": "Maxwell2D",
        "excitation": "Maxwell2D",
        "setup": ["General", "Convergence", "Solver"],
        "mesh": "Maxwell2D",
    }


class EmitConstants(metaclass=DynamicMeta):
    NAME = "EMIT"

    model_name = "EMIT"
    solution_default = "EMIT"
    solution_types = {
        "EMIT": {"name": None, "options": None, "report_type": None, "default_setup": None, "default_adaptive": None}
    }
    report_templates = []


class ModelCreationConstants(metaclass=DynamicMeta):
    NAME = "ModelCreation"

    model_name = "RMxprtDesign"
    solution_default = "GRM"
    solution_types = {
        "GRM": {"name": "GRM", "options": None, "report_type": None, "default_setup": 34, "default_adaptive": None},
        "IRIM": {"name": "IRIM", "options": None, "report_type": None, "default_setup": 34, "default_adaptive": None},
        "ORIM": {"name": "ORIM", "options": None, "report_type": None, "default_setup": 34, "default_adaptive": None},
        "SRIM": {"name": "SRIM", "options": None, "report_type": None, "default_setup": 34, "default_adaptive": None},
        "WRIM": {"name": "WRIM", "options": None, "report_type": None, "default_setup": 34, "default_adaptive": None},
        "DFIG": {"name": "DFIG", "options": None, "report_type": None, "default_setup": 34, "default_adaptive": None},
        "AFIM": {"name": "AFIM", "options": None, "report_type": None, "default_setup": 34, "default_adaptive": None},
        "HM": {"name": "HM", "options": None, "report_type": None, "default_setup": 34, "default_adaptive": None},
        "RFSM": {"name": "RFSM", "options": None, "report_type": None, "default_setup": 34, "default_adaptive": None},
        "RASM": {"name": "RASM", "options": None, "report_type": None, "default_setup": 34, "default_adaptive": None},
        "RSM": {"name": "RSM", "options": None, "report_type": None, "default_setup": 34, "default_adaptive": None},
        "ISM": {"name": "ISM", "options": None, "report_type": None, "default_setup": 34, "default_adaptive": None},
        "APSM": {"name": "APSM", "options": None, "report_type": None, "default_setup": 34, "default_adaptive": None},
        "IBDM": {"name": "IBDM", "options": None, "report_type": None, "default_setup": 34, "default_adaptive": None},
        "ABDM": {"name": "ABDM", "options": None, "report_type": None, "default_setup": 34, "default_adaptive": None},
    }
    report_templates = []


class MaxwellCircuitConstants(metaclass=DynamicMeta):
    NAME = "Maxwell Circuit"
    model_name = "MaxCirCircuit"
    solution_default = ""
    solution_types = {
        "Maxwell Circuit": {
            "name": "Maxwell Circuit",
            "options": None,
            "report_type": None,
            "default_setup": None,
            "default_adaptive": None,
        }
    }
    report_templates = []


class CircuitConstants(metaclass=DynamicMeta):
    NAME = "Circuit Design"
    model_name = "NexximCircuit"
    solution_default = "NexximLNA"
    solution_types = {
        "NexximLNA": {
            "name": None,
            "options": None,
            "report_type": "Standard",
            "default_setup": 15,
            "default_adaptive": None,
            "intrinsics": ["Freq"],
        },
        "NexximDC": {
            "name": None,
            "options": None,
            "report_type": "Standard",
            "default_setup": 16,
            "default_adaptive": None,
        },
        "NexximTransient": {
            "name": None,
            "options": None,
            "report_type": "Standard",
            "default_setup": 17,
            "default_adaptive": None,
            "intrinsics": ["Time"],
        },
        "NexximVerifEye": {
            "name": None,
            "options": None,
            "report_type": "Standard",
            "default_setup": 19,
            "default_adaptive": None,
            "intrinsics": ["Time"],
        },
        "NexximQuickEye": {
            "name": None,
            "options": None,
            "report_type": "Standard",
            "default_setup": 18,
            "default_adaptive": None,
            "intrinsics": ["Time"],
        },
        "NexximAMI": {
            "name": None,
            "options": None,
            "report_type": "Standard",
            "default_setup": 20,
            "default_adaptive": None,
            "intrinsics": ["Time"],
        },
        "NexximOscillatorRSF": {
            "name": None,
            "options": None,
            "report_type": "Standard",
            "default_setup": 21,
            "default_adaptive": None,
            "intrinsics": ["Freq"],
        },
        "NexximOscillator1T": {
            "name": None,
            "options": None,
            "report_type": "Standard",
            "default_setup": 22,
            "default_adaptive": None,
            "intrinsics": ["Freq"],
        },
        "NexximOscillatorNT": {
            "name": None,
            "options": None,
            "report_type": "Standard",
            "default_setup": 23,
            "default_adaptive": None,
            "intrinsics": ["Freq"],
        },
        "NexximHarmonicBalance1T": {
            "name": None,
            "options": None,
            "report_type": "Standard",
            "default_setup": 24,
            "default_adaptive": None,
            "intrinsics": ["Freq"],
        },
        "NexximHarmonicBalanceNT": {
            "name": None,
            "options": None,
            "report_type": "Standard",
            "default_setup": 25,
            "default_adaptive": None,
            "intrinsics": ["Freq"],
        },
        "NexximSystem": {
            "name": None,
            "options": None,
            "report_type": "Standard",
            "default_setup": 26,
            "default_adaptive": None,
            "intrinsics": ["Time"],
        },
        "NexximTVNoise": {
            "name": None,
            "options": None,
            "report_type": "Standard",
            "default_setup": 27,
            "default_adaptive": None,
            "intrinsics": ["Freq"],
        },
        "HSPICE": {
            "name": None,
            "options": None,
            "report_type": "Standard",
            "default_setup": 28,
            "default_adaptive": None,
            "intrinsics": ["Time"],
        },
        "TR": {
            "name": None,
            "options": None,
            "report_type": "Standard",
            "default_setup": 17,
            "default_adaptive": None,
            "intrinsics": ["Time"],
        },
    }
    report_templates = ["Standard", "Eye Diagram", "Statistical Eye", "Spectrum", "EMIReceiver"]


class CircuitNetlistConstants(metaclass=DynamicMeta):
    NAME = "Circuit Netlist"

    model_name = "NexximNetlist"
    solution_default = ""
    solution_types = {
        "NexximLNA": {
            "name": None,
            "options": None,
            "report_type": "Standard",
            "default_setup": 15,
            "default_adaptive": None,
            "intrinsics": ["Freq"],
        },
        "NexximDC": {
            "name": None,
            "options": None,
            "report_type": "Standard",
            "default_setup": 16,
            "default_adaptive": None,
        },
        "NexximTransient": {
            "name": None,
            "options": None,
            "report_type": "Standard",
            "default_setup": 17,
            "default_adaptive": None,
            "intrinsics": ["Time"],
        },
        "NexximVerifEye": {
            "name": None,
            "options": None,
            "report_type": "Standard",
            "default_setup": 19,
            "default_adaptive": None,
            "intrinsics": ["Time"],
        },
        "NexximQuickEye": {
            "name": None,
            "options": None,
            "report_type": "Standard",
            "default_setup": 18,
            "default_adaptive": None,
            "intrinsics": ["Time"],
        },
        "NexximAMI": {
            "name": None,
            "options": None,
            "report_type": "Standard",
            "default_setup": 20,
            "default_adaptive": None,
            "intrinsics": ["Time"],
        },
        "NexximOscillatorRSF": {
            "name": None,
            "options": None,
            "report_type": "Standard",
            "default_setup": 21,
            "default_adaptive": None,
            "intrinsics": ["Freq"],
        },
        "NexximOscillator1T": {
            "name": None,
            "options": None,
            "report_type": "Standard",
            "default_setup": 22,
            "default_adaptive": None,
            "intrinsics": ["Freq"],
        },
        "NexximOscillatorNT": {
            "name": None,
            "options": None,
            "report_type": "Standard",
            "default_setup": 23,
            "default_adaptive": None,
            "intrinsics": ["Freq"],
        },
        "NexximHarmonicBalance1T": {
            "name": None,
            "options": None,
            "report_type": "Standard",
            "default_setup": 24,
            "default_adaptive": None,
            "intrinsics": ["Freq"],
        },
        "NexximHarmonicBalanceNT": {
            "name": None,
            "options": None,
            "report_type": "Standard",
            "default_setup": 25,
            "default_adaptive": None,
            "intrinsics": ["Freq"],
        },
        "NexximSystem": {
            "name": None,
            "options": None,
            "report_type": "Standard",
            "default_setup": 26,
            "default_adaptive": None,
            "intrinsics": ["Time"],
        },
        "NexximTVNoise": {
            "name": None,
            "options": None,
            "report_type": "Standard",
            "default_setup": 27,
            "default_adaptive": None,
            "intrinsics": ["Freq"],
        },
        "HSPICE": {
            "name": None,
            "options": None,
            "report_type": "Standard",
            "default_setup": 28,
            "default_adaptive": None,
            "intrinsics": ["Time"],
        },
        "TR": {
            "name": None,
            "options": None,
            "report_type": "Standard",
            "default_setup": 17,
            "default_adaptive": None,
            "intrinsics": ["Time"],
        },
    }
    report_templates = ["Standard", "Eye Diagram", "Statistical Eye", "Spectrum", "EMIReceiver"]


class DesignType(metaclass=DynamicMeta):
    """Design Type class"""

    (
        HFSS,
        Q3D,
        EXTRACTOR2D,
        ICEPAK,
        ICEPAKFEA,
        CIRCUIT,
        HFSS3DLAYOUT,
        TWINBUILDER,
        RMXPRT,
        MAXWELL3D,
        MAXWELL2D,
        EMIT,
        MODELCREATION,
        MAXWELLCIRCUIT,
        CIRCUITNETLIST,
    ) = (
        HfssConstants,
        Q3dConstants,
        Extractor2dConstants,
        IcepakConstants,
        IcepakFeaConstants,
        CircuitConstants,
        Hfss3dLayoutConstants,
        TwinbuilderConstants,
        RmxprtConstants,
        Maxwell3dConstants,
        Maxwell2dConstants,
        EmitConstants,
        ModelCreationConstants,
        MaxwellCircuitConstants,
        CircuitNetlistConstants,
    )
