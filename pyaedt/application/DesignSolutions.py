import copy

from pyaedt.generic.general_methods import aedt_exception_handler

solutions_types = {
    "Maxwell 2D": {
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
        },
        "Transient": {
            "name": "Transient",
            "options": "XY",
            "report_type": "Transient",
            "default_setup": 5,
            "default_adaptive": "Transient",
        },
        "Electrostatic": {
            "name": "Electrostatic",
            "options": "XY",
            "report_type": "Electrostatic",
            "default_setup": 8,
            "default_adaptive": "LastAdaptive",
        },
        "ElectricTransient": {
            "name": "ElectricTransient",
            "options": "XY",
            "report_type": None,
            "default_setup": 10,
            "default_adaptive": "Transient",
        },
        "ElectroDCConduction": {
            "name": "ElectroDCConduction",
            "options": "XY",
            "report_type": None,
            "default_setup": 9,
            "default_adaptive": "LastAdaptive",
        },
    },
    "Maxwell 3D": {
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
        },
        "Transient": {
            "name": "Transient",
            "options": None,
            "report_type": "Transient",
            "default_setup": 5,
            "default_adaptive": "Transient",
        },
        "Electrostatic": {
            "name": "Electrostatic",
            "options": None,
            "report_type": "Electrostatic",
            "default_setup": 8,
            "default_adaptive": "LastAdaptive",
        },
        "DCConduction": {
            "name": None,
            "options": None,
            "report_type": None,
            "default_setup": None,
            "default_adaptive": None,
        },
        "ElectroDCConduction": {
            "name": "ElectroDCConduction",
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
        },
    },
    "Twin Builder": {
        "TR": {"name": None, "options": None, "report_type": None, "default_setup": 35, "default_adaptive": None},
        "AC": {"name": None, "options": None, "report_type": None, "default_setup": None, "default_adaptive": None},
        "DC": {"name": None, "options": None, "report_type": None, "default_setup": None, "default_adaptive": None},
    },
    "Circuit Design": {
        "NexximLNA": {
            "name": None,
            "options": None,
            "report_type": "Standard",
            "default_setup": 15,
            "default_adaptive": None,
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
        },
        "NexximVerifEye": {
            "name": None,
            "options": None,
            "report_type": "Standard",
            "default_setup": 19,
            "default_adaptive": None,
        },
        "NexximQuickEye": {
            "name": None,
            "options": None,
            "report_type": "Standard",
            "default_setup": 18,
            "default_adaptive": None,
        },
        "NexximAMI": {
            "name": None,
            "options": None,
            "report_type": "Standard",
            "default_setup": 20,
            "default_adaptive": None,
        },
        "NexximOscillatorRSF": {
            "name": None,
            "options": None,
            "report_type": "Standard",
            "default_setup": 21,
            "default_adaptive": None,
        },
        "NexximOscillator1T": {
            "name": None,
            "options": None,
            "report_type": "Standard",
            "default_setup": 22,
            "default_adaptive": None,
        },
        "NexximOscillatorNT": {
            "name": None,
            "options": None,
            "report_type": "Standard",
            "default_setup": 23,
            "default_adaptive": None,
        },
        "NexximHarmonicBalance1T": {
            "name": None,
            "options": None,
            "report_type": "Standard",
            "default_setup": 24,
            "default_adaptive": None,
        },
        "NexximHarmonicBalanceNT": {
            "name": None,
            "options": None,
            "report_type": "Standard",
            "default_setup": 25,
            "default_adaptive": None,
        },
        "NexximSystem": {
            "name": None,
            "options": None,
            "report_type": "Standard",
            "default_setup": 26,
            "default_adaptive": None,
        },
        "NexximTVNoise": {
            "name": None,
            "options": None,
            "report_type": "Standard",
            "default_setup": 27,
            "default_adaptive": None,
        },
        "HSPICE": {
            "name": None,
            "options": None,
            "report_type": "Standard",
            "default_setup": 28,
            "default_adaptive": None,
        },
        "TR": {"name": None, "options": None, "report_type": "Standard", "default_setup": 17, "default_adaptive": None},
    },
    "2D Extractor": {
        "Open": {"name": "Open", "options": None, "report_type": None, "default_setup": 30, "default_adaptive": None},
        "Closed": {
            "name": "Closed",
            "options": None,
            "report_type": None,
            "default_setup": 31,
            "default_adaptive": None,
        },
    },
    "Q3D Extractor": {
        "Q3D Extractor": {
            "name": None,
            "options": None,
            "report_type": "Matrix",
            "default_setup": 14,
            "default_adaptive": None,
        }
    },
    "HFSS": {
        "Modal": {
            "name": "DrivenModal",
            "options": None,
            "report_type": "Modal Solution Data",
            "default_setup": 1,
            "default_adaptive": "LastAdaptive",
        },
        "Terminal": {
            "name": "DrivenTerminal",
            "options": None,
            "report_type": "Terminal Solution Data",
            "default_setup": 1,
            "default_adaptive": "LastAdaptive",
        },
        "DrivenModal": {
            "name": "DrivenModal",
            "options": None,
            "report_type": "Modal Solution Data",
            "default_setup": 1,
            "default_adaptive": "LastAdaptive",
        },
        "DrivenTerminal": {
            "name": "DrivenTerminal",
            "options": None,
            "report_type": "Terminal Solution Data",
            "default_setup": 1,
            "default_adaptive": "LastAdaptive",
        },
        "Transient": {
            "name": "Transient Network",
            "options": None,
            "report_type": "Terminal Solution Data",
            "default_setup": 3,
            "default_adaptive": "Transient",
        },
        "Eigenmode": {
            "name": None,
            "options": None,
            "report_type": "EigenMode Parameters",
            "default_setup": 2,
            "default_adaptive": "LastAdaptive",
        },
        "Characteristic": {
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
            "default_adaptive": None,
        },
    },
    "Icepak": {
        "SteadyState": {
            "name": "SteadyState",
            "options": "TemperatureAndFlow",
            "report_type": "Monitor",
            "default_setup": 11,
            "default_adaptive": None,
        },
        "Transient": {
            "name": "Transient",
            "options": "TemperatureAndFlow",
            "report_type": "Monitor",
            "default_setup": 36,
            "default_adaptive": None,
        },
    },
    "RMxprtSolution": {
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
        "TPIM": {"name": "TPIM", "options": None, "report_type": None, "default_setup": 34, "default_adaptive": None},
        "SPIM": {"name": "SPIM", "options": None, "report_type": None, "default_setup": 34, "default_adaptive": None},
        "TPSM": {"name": "TPSM", "options": None, "report_type": None, "default_setup": 34, "default_adaptive": None},
        "BLDC": {"name": "BLDC", "options": None, "report_type": None, "default_setup": 34, "default_adaptive": None},
        "ASSM": {"name": "ASSM", "options": None, "report_type": None, "default_setup": 34, "default_adaptive": None},
        "PMDC": {"name": "PMDC", "options": None, "report_type": None, "default_setup": 34, "default_adaptive": None},
        "SRM": {"name": "SRM", "options": None, "report_type": None, "default_setup": 34, "default_adaptive": None},
        "LSSM": {"name": "LSSM", "options": None, "report_type": None, "default_setup": 34, "default_adaptive": None},
        "UNIM": {"name": "UNIM", "options": None, "report_type": None, "default_setup": 34, "default_adaptive": None},
        "DCM": {"name": "DCM", "options": None, "report_type": None, "default_setup": 34, "default_adaptive": None},
        "CPSM": {"name": "CPSM", "options": None, "report_type": None, "default_setup": 34, "default_adaptive": None},
        "NSSM": {"name": "NSSM", "options": None, "report_type": None, "default_setup": 34, "default_adaptive": None},
    },
    "ModelCreation": {
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
    },
    "HFSS 3D Layout Design": {
        "HFSS3DLayout": {
            "name": None,
            "options": None,
            "report_type": None,
            "default_setup": 29,
            "default_adaptive": None,
        },
        "SiwaveDC3DLayout": {
            "name": None,
            "options": None,
            "report_type": None,
            "default_setup": 40,
            "default_adaptive": None,
        },
        "SiwaveAC3DLayout": {
            "name": None,
            "options": None,
            "report_type": None,
            "default_setup": 41,
            "default_adaptive": None,
        },
        "LNA3DLayout": {
            "name": None,
            "options": None,
            "report_type": None,
            "default_setup": 42,
            "default_adaptive": None,
        },
    },
    "Mechanical": {
        "Thermal": {
            "name": "Thermal",
            "options": None,
            "report_type": None,
            "default_setup": 32,
            "default_adaptive": None,
        },
        "Modal": {"name": "Modal", "options": None, "report_type": None, "default_setup": 33, "default_adaptive": None},
        "Structural": {
            "name": "Structural",
            "options": None,
            "report_type": None,
            "default_setup": 39,
            "default_adaptive": "Solution",
        },
    },
    "EMIT": {
        "EMIT": {"name": None, "options": None, "report_type": None, "default_setup": None, "default_adaptive": None}
    },
}

model_names = {
    "Maxwell 2D": "Maxwell2DModel",
    "Maxwell 3D": "Maxwell3DModel",
    "Twin Builder": "SimplorerCircuit",
    "Circuit Design": "NexximCircuit",
    "2D Extractor": "2DExtractorModel",
    "Q3D Extractor": "Q3DModel",
    "HFSS": "HFSSModel",
    "Mechanical": "MechanicalModel",
    "Icepak": "IcepakModel",
    "RMxprtSolution": "RMxprtDesign",
    "ModelCreation": "RMxprtDesign",
    "HFSS 3D Layout Design": "PlanarEMCircuit",
    "EMIT Design": "EMIT Design",
    "EMIT": "EMIT",
}


class DesignSolution(object):
    def __init__(self, odesign, design_type, aedt_version):
        self._odesign = odesign
        self._aedt_version = aedt_version
        self.model_name = model_names[design_type]
        assert design_type in solutions_types, "Wrong Design Type"
        # deepcopy doesn't work on remote
        self._solution_options = copy.deepcopy(solutions_types[design_type])
        if design_type == "HFSS" and aedt_version >= "2021.2":
            self._solution_options["Modal"]["name"] = "HFSS Hybrid Modal Network"
            self._solution_options["Terminal"]["name"] = "HFSS Hybrid Terminal Network"
        self._solution_type = self.solution_types[0]

    @property
    def solution_type(self):
        return self._solution_type

    @solution_type.setter
    @aedt_exception_handler
    def solution_type(self, soltype):
        if soltype is None:
            if "GetSolutionType" in dir(self._odesign):
                self._solution_type = self._odesign.GetSolutionType()
                if "Modal" in self._solution_type:
                    self._solution_type = "Modal"
                elif "Terminal" in self._solution_type:
                    self._solution_type = "Terminal"
        elif soltype and soltype in self._solution_options and self._solution_options[soltype]["name"]:
            self._solution_type = soltype
            if self._solution_options[soltype]["options"]:
                self._odesign.SetSolutionType(
                    self._solution_options[soltype]["name"], self._solution_options[soltype]["options"]
                )

            else:
                try:
                    self._odesign.SetSolutionType(self._solution_options[soltype]["name"])
                except:
                    self._odesign.SetSolutionType(self._solution_options[soltype]["name"], "")

    @property
    def report_type(self):
        return self._solution_options[self._solution_type]["report_type"]

    @property
    def default_setup(self):
        return self._solution_options[self._solution_type]["default_setup"]

    @property
    def default_adaptive(self):
        return self._solution_options[self._solution_type]["default_adaptive"]

    @property
    def solution_types(self):
        return list(self._solution_options.keys())

    @property
    def design_types(self):
        return list(solutions_types.keys())


class HFSSDesignSolution(DesignSolution, object):
    def __init__(self, odesign, design_type, aedt_version):
        DesignSolution.__init__(self, odesign, design_type, aedt_version)
        self._composite = "Composite" in self._solution_options[self._solution_type]["name"]
        self._hybrid = "Hybrid" in self._solution_options[self._solution_type]["name"]

    @property
    def hybrid(self):
        return self._hybrid

    @hybrid.setter
    @aedt_exception_handler
    def hybrid(self, val):
        if val:
            self._solution_options[self._solution_type]["name"] = self._solution_options[self._solution_type][
                "name"
            ].replace("HFSS", "HFSS Hybrid")
        else:
            self._solution_options[self._solution_type]["name"] = self._solution_options[self._solution_type][
                "name"
            ].replace("HFSS Hybrid", "HFSS")
        self._composite = val
        self.solution_type = self._solution_type

    @property
    def composite(self):
        return self._composite

    @composite.setter
    @aedt_exception_handler
    def composite(self, val):
        if val:
            self._solution_options[self._solution_type]["name"] = self._solution_options[self._solution_type][
                "name"
            ].replace("Network", "Composite")
        else:
            self._solution_options[self._solution_type]["name"] = self._solution_options[self._solution_type][
                "name"
            ].replace("Composite", "Network")
        self._composite = val
        self.solution_type = self._solution_type

    @aedt_exception_handler
    def set_auto_open(self, enable=True, boundary_type="Radiation"):
        options = ["NAME:Options", "EnableAutoOpen:=", enable]
        if enable:
            options.append("BoundaryType:=")
            options.append(boundary_type)
        self._solution_options[self._solution_type]["options"] = options
        self.solution_type = self._solution_type


class Maxwell2DDesignSolution(DesignSolution, object):
    def __init__(self, odesign, design_type, aedt_version):
        DesignSolution.__init__(self, odesign, design_type, aedt_version)
        self._geometry_mode = "XY"

    @property
    def xy_plane(self):
        return self._geometry_mode == "XY"

    @xy_plane.setter
    @aedt_exception_handler
    def xy_plane(self, val=True):
        if val:
            self._geometry_mode = "XY"
        else:
            self._geometry_mode = "about Z"
        self._solution_options[self._solution_type]["options"] = self._geometry_mode
        self.solution_type = self._solution_type

    @property
    def solution_type(self):
        return self._solution_type

    @solution_type.setter
    @aedt_exception_handler
    def solution_type(self, soltype):
        if soltype is None:
            if "GetSolutionType" in dir(self._odesign):
                self._solution_type = self._odesign.GetSolutionType()
                if "Modal" in self._solution_type:
                    self._solution_type = "Modal"
                elif "Terminal" in self._solution_type:
                    self._solution_type = "Terminal"
            return
        if soltype[-1:] == "Z":
            self._solution_options[self._solution_type]["options"] = "about Z"
            self._geometry_mode = "about Z"
            soltype = soltype[:-1]
        elif soltype[-2:] == "XY":
            self._solution_options[self._solution_type]["options"] = "XY"
            self._geometry_mode = "XY"
            soltype = soltype[:-2]
        if soltype in self._solution_options and self._solution_options[soltype]["name"]:
            self._solution_type = soltype
            try:
                opts = (
                    ""
                    if self._solution_options[soltype]["options"] is None
                    else self._solution_options[soltype]["options"]
                )
                self._odesign.SetSolutionType(self._solution_options[soltype]["name"], opts)
            except:
                pass


class IcepakDesignSolution(DesignSolution, object):
    def __init__(self, odesign, design_type, aedt_version):
        DesignSolution.__init__(self, odesign, design_type, aedt_version)
        self._problem_type = "TemperatureAndFlow"

    @property
    def problem_type(self):
        return self._problem_type

    @problem_type.setter
    @aedt_exception_handler
    def problem_type(self, val="TemperatureAndFlow"):
        if val == "TemperatureAndFlow":
            self._problem_type = val
            self._solution_options[self._solution_type]["options"] = self._problem_type
            if self._solution_type == "SteadyState":
                self._solution_options[self._solution_type]["default_setup"] = 11
            else:
                self._solution_options[self._solution_type]["default_setup"] = 36
        elif val == "TemperatureOnly":
            self._problem_type = val
            self._solution_options[self._solution_type]["options"] = self._problem_type
            if self._solution_type == "SteadyState":
                self._solution_options[self._solution_type]["default_setup"] = 12
            else:
                self._solution_options[self._solution_type]["default_setup"] = 37
        elif val == "FlowOnly":
            self._problem_type = val
            self._solution_options[self._solution_type]["options"] = self._problem_type
            if self._solution_type == "SteadyState":
                self._solution_options[self._solution_type]["default_setup"] = 13
            else:
                self._solution_options[self._solution_type]["default_setup"] = 38
        else:
            raise AttributeError("Wrong input. Expected values are TemperatureAndFlow, TemperatureOnly and FlowOnly.")

    @property
    def solution_type(self):
        return self._solution_type

    @solution_type.setter
    @aedt_exception_handler
    def solution_type(self, soltype):
        if soltype in self._solution_options and self._solution_options[soltype]["name"]:
            self._solution_type = soltype
            options = [
                "NAME:SolutionTypeOption",
                "SolutionTypeOption:=",
                soltype,
                "ProblemOption:=",
                self._problem_type,
            ]
            try:
                self._odesign.SetSolutionType(options)
            except:
                pass


class RmXprtDesignSolution(DesignSolution, object):
    def __init__(self, odesign, design_type, aedt_version):
        DesignSolution.__init__(self, odesign, design_type, aedt_version)
        self._design_type = design_type

    @property
    def solution_type(self):
        return self._solution_type

    @solution_type.setter
    @aedt_exception_handler
    def solution_type(self, soltype):
        if soltype:
            try:
                self._odesign.SetDesignFlow(self._design_type, soltype)
                self._solution_type = soltype
            except:
                pass

    @property
    def design_type(self):
        return self._design_type

    @design_type.setter
    @aedt_exception_handler
    def design_type(self, destype):
        if destype:
            self._design_type = destype
            self.solution_type = self._solution_type
