import copy

from pyaedt.generic.general_methods import pyaedt_function_handler

solutions_defaults = {
    "Maxwell 2D": "Magnetostatic",
    "Maxwell 3D": "Magnetostatic",
    "Twin Builder": "TR",
    "Circuit Design": "NexximLNA",
    "Maxwell Circuit": "",
    "2D Extractor": "Open",
    "Q3D Extractor": "Q3D Extractor",
    "HFSS": "HFSS Modal Network",
    "Icepak": "SteadyState",
    "RMxprtSolution": "GRM",
    "ModelCreation": "GRM",
    "HFSS 3D Layout Design": "HFSS3DLayout",
    "Mechanical": "Thermal",
    "EMIT": "EMIT",
}

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
        "DCConduction": {
            "name": "DCConduction",
            "options": "XY",
            "report_type": None,
            "default_setup": 8,
            "default_adaptive": "LastAdaptive",
        },
        "ACConduction": {
            "name": "ACConduction",
            "options": "XY",
            "report_type": None,
            "default_setup": 8,
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
        "TransientAPhiFormulation": {
            "name": "TransientAPhiFormulation",
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
        "ACConduction": {
            "name": None,
            "options": None,
            "report_type": None,
            "default_setup": None,
            "default_adaptive": "LastAdaptive",
        },
        "DCConduction": {
            "name": None,
            "options": None,
            "report_type": None,
            "default_setup": None,
            "default_adaptive": "LastAdaptive",
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
        "TR": {"name": None, "options": None, "report_type": "Standard", "default_setup": 35, "default_adaptive": None},
        "AC": {
            "name": None,
            "options": None,
            "report_type": "Standard",
            "default_setup": None,
            "default_adaptive": None,
        },
        "DC": {
            "name": None,
            "options": None,
            "report_type": "Standard",
            "default_setup": None,
            "default_adaptive": None,
        },
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
        "Open": {
            "name": "Open",
            "options": None,
            "report_type": "Matrix",
            "default_setup": 30,
            "default_adaptive": "LastAdaptive",
        },
        "Closed": {
            "name": "Closed",
            "options": None,
            "report_type": "Matrix",
            "default_setup": 31,
            "default_adaptive": "LastAdaptive",
        },
    },
    "Q3D Extractor": {
        "Q3D Extractor": {
            "name": None,
            "options": None,
            "report_type": "Matrix",
            "default_setup": 14,
            "default_adaptive": "LastAdaptive",
        }
    },
    "HFSS": {
        "Modal": {
            "name": "HFSS Modal Network",
            "options": None,
            "report_type": "Modal Solution Data",
            "default_setup": 1,
            "default_adaptive": "LastAdaptive",
        },
        "Terminal": {
            "name": "HFSS Terminal Network",
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
        "Transient Network": {
            "name": "Transient Network",
            "options": None,
            "report_type": "Terminal Solution Data",
            "default_setup": 3,
            "default_adaptive": "Transient",
        },
        "Transient": {
            "name": "Transient",
            "options": None,
            "report_type": "Terminal Solution Data",
            "default_setup": 3,
            "default_adaptive": "Transient",
        },
        "Eigenmode": {
            "name": "Eigenmode",
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
            "default_adaptive": "Sweep",
        },
    },
    "Icepak": {
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
    },
    "RMxprtSolution": {
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
    },
    "ModelCreation": {
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
    },
    "HFSS 3D Layout Design": {
        "HFSS3DLayout": {
            "name": None,
            "options": None,
            "report_type": "Standard",
            "default_setup": 29,
            "default_adaptive": None,
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
        },
        "LNA3DLayout": {
            "name": None,
            "options": None,
            "report_type": "Standard",
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
    # Maxwell Circuit has no solution type
    "Maxwell Circuit": {},
}

model_names = {
    "Maxwell 2D": "Maxwell2DModel",
    "Maxwell 3D": "Maxwell3DModel",
    "Twin Builder": "SimplorerCircuit",
    "Circuit Design": "NexximCircuit",
    "Maxwell Circuit": "MaxCirCircuit",
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
        self._design_type = design_type
        if design_type == "HFSS" and aedt_version >= "2021.2":
            self._solution_options["Modal"]["name"] = "HFSS Modal Network"
            self._solution_options["Terminal"]["name"] = "HFSS Terminal Network"
        self._solution_type = None

    @property
    def solution_type(self):
        """Get/Set the Solution Type of the active Design."""
        if self._design_type in ["Circuit Design", "Twin Builder", "HFSS 3D Layout Design", "EMIT", "Q3D Extractor"]:
            self._solution_type = solutions_defaults[self._design_type]
        elif self._odesign:
            try:
                self._solution_type = self._odesign.GetSolutionType()
            except:
                self._solution_type = solutions_defaults[self._design_type]
        elif self._solution_type is None:
            self._solution_type = solutions_defaults[self._design_type]
        return self._solution_type

    @solution_type.setter
    @pyaedt_function_handler()
    def solution_type(self, value):
        if value is None:
            if self._design_type in [
                "Circuit Design",
                "Twin Builder",
                "HFSS 3D Layout Design",
                "EMIT",
                "Q3D Extractor",
            ]:
                self._solution_type = solutions_defaults[self._design_type]
            elif self._odesign:
                try:
                    self._solution_type = self._odesign.GetSolutionType()
                except:
                    self._solution_type = solutions_defaults[self._design_type]
            else:
                self._solution_type = solutions_defaults[self._design_type]
        elif value and value in self._solution_options and self._solution_options[value]["name"]:
            self._solution_type = value
            if self._solution_options[value]["options"]:
                self._odesign.SetSolutionType(
                    self._solution_options[value]["name"], self._solution_options[value]["options"]
                )
            else:
                try:
                    self._odesign.SetSolutionType(self._solution_options[value]["name"])
                except:
                    self._odesign.SetSolutionType(self._solution_options[value]["name"], "")

    @property
    def report_type(self):
        """Return the default report type of the selected solution if present."""
        return self._solution_options[self.solution_type]["report_type"]

    @property
    def default_setup(self):
        """Return the default setup id of the selected solution if present."""
        return self._solution_options[self.solution_type]["default_setup"]

    @property
    def default_adaptive(self):
        """Return the default adaptive name of the selected solution if present."""
        return self._solution_options[self.solution_type]["default_adaptive"]

    @property
    def solution_types(self):
        """Return the list of all available solutions."""
        return list(self._solution_options.keys())

    @property
    def design_types(self):
        """Return the list of all available designs."""
        return list(solutions_types.keys())


class HFSSDesignSolution(DesignSolution, object):
    def __init__(self, odesign, design_type, aedt_version):
        DesignSolution.__init__(self, odesign, design_type, aedt_version)
        self._composite = False
        self._hybrid = False

    @property
    def solution_type(self):
        """Get/Set the Solution Type of the active Design."""
        if self._odesign:
            try:
                self._solution_type = self._odesign.GetSolutionType()
                if "Modal" in self._solution_type:
                    self._solution_type = "Modal"
                elif "Terminal" in self._solution_type:
                    self._solution_type = "Terminal"
            except:
                self._solution_type = solutions_defaults[self._design_type]
        elif self._solution_type is None:
            self._solution_type = solutions_defaults[self._design_type]
        return self._solution_type

    @solution_type.setter
    @pyaedt_function_handler()
    def solution_type(self, value):
        if self._aedt_version < "2021.2":
            if not value:
                self._solution_type = "DrivenModal"
                self._odesign.SetSolutionType(self._solution_type)
            elif "Modal" in value:
                self._solution_type = "DrivenModal"
                self._odesign.SetSolutionType(self._solution_type)
            elif "Terminal" in value:
                self._solution_type = "DrivenTerminal"
                self._odesign.SetSolutionType(self._solution_type)
            else:
                try:
                    self._odesign.SetSolutionType(self._solution_options[value]["name"])
                except:
                    self._odesign.SetSolutionType(self._solution_options[value]["name"], "")
        elif value is None:
            if self._odesign:
                try:
                    self._solution_type = self._odesign.GetSolutionType()
                    if "Modal" in self._solution_type:
                        self._solution_type = "Modal"
                    elif "Terminal" in self._solution_type:
                        self._solution_type = "Terminal"
                except:
                    self._solution_type = solutions_defaults[self._design_type]
            else:
                self._solution_type = solutions_defaults[self._design_type]
        elif value and value in self._solution_options and self._solution_options[value]["name"]:
            if value == "Transient":
                value = "Transient Network"
                self._solution_type = "Transient Network"
            elif "Modal" in value:
                value = "Modal"
                self._solution_type = "Modal"
            elif "Terminal" in value:
                value = "Terminal"
                self._solution_type = "Terminal"
            else:
                self._solution_type = value
            if self._solution_options[value]["options"]:
                self._odesign.SetSolutionType(
                    self._solution_options[value]["name"], self._solution_options[value]["options"]
                )
            else:
                try:
                    self._odesign.SetSolutionType(self._solution_options[value]["name"])
                except:
                    self._odesign.SetSolutionType(self._solution_options[value]["name"], "")

    @property
    def hybrid(self):
        """HFSS hybrid mode for the active solution."""
        if self._aedt_version < "2021.2":
            return False
        if self._hybrid is None and self.solution_type is not None:
            self._hybrid = "Hybrid" in self._solution_options[self.solution_type]["name"]
        return self._hybrid

    @hybrid.setter
    @pyaedt_function_handler()
    def hybrid(self, value):
        if self._aedt_version < "2021.2":
            return
        if value and "Hybrid" not in self._solution_options[self.solution_type]["name"]:
            self._solution_options[self.solution_type]["name"] = self._solution_options[self.solution_type][
                "name"
            ].replace("HFSS", "HFSS Hybrid")
        else:
            self._solution_options[self.solution_type]["name"] = self._solution_options[self.solution_type][
                "name"
            ].replace("HFSS Hybrid", "HFSS")
        self._hybrid = value
        self.solution_type = self.solution_type

    @property
    def composite(self):
        """HFSS composite mode for the active solution."""
        if self._aedt_version < "2021.2":
            return False
        if self._composite is None and self.solution_type is not None:
            self._composite = "Composite" in self._solution_options[self.solution_type]["name"]
        return self._composite

    @composite.setter
    @pyaedt_function_handler()
    def composite(self, val):
        if self._aedt_version < "2021.2":
            return
        if val:
            self._solution_options[self.solution_type]["name"] = self._solution_options[self.solution_type][
                "name"
            ].replace("Network", "Composite")
        else:
            self._solution_options[self.solution_type]["name"] = self._solution_options[self.solution_type][
                "name"
            ].replace("Composite", "Network")
        self._composite = val
        self.solution_type = self.solution_type

    @pyaedt_function_handler()
    def set_auto_open(self, enable=True, boundary_type="Radiation"):
        """Set Hfss auto open type.

        Parameters
        ----------
        enable : bool, optional
            Either to enable or not auto open. The default is ``True``.
        boundary_type : str, optional
            Boundary Type to be used with auto open. Default is `"Radiation"`.

        Returns
        -------
        bool
        """
        if self._aedt_version < "2021.2":
            return False
        options = ["NAME:Options", "EnableAutoOpen:=", enable]
        if enable:
            options.append("BoundaryType:=")
            options.append(boundary_type)
        self._solution_options[self.solution_type]["options"] = options
        self.solution_type = self.solution_type
        return True


class Maxwell2DDesignSolution(DesignSolution, object):
    def __init__(self, odesign, design_type, aedt_version):
        DesignSolution.__init__(self, odesign, design_type, aedt_version)
        self._geometry_mode = "XY"

    @property
    def xy_plane(self):
        """Get/Set Maxwell 2d plane between `"XY"` and `"about Z"`."""
        return self._geometry_mode == "XY"

    @xy_plane.setter
    @pyaedt_function_handler()
    def xy_plane(self, value=True):
        if value:
            self._geometry_mode = "XY"
        else:
            self._geometry_mode = "about Z"
        self._solution_options[self.solution_type]["options"] = self._geometry_mode
        self.solution_type = self.solution_type

    @property
    def solution_type(self):
        """Get/Set the Solution Type of the active Design."""
        if self._odesign and "GetSolutionType":
            try:
                self._solution_type = self._odesign.GetSolutionType()
            except:
                self._solution_type = solutions_defaults[self._design_type]
        return self._solution_type

    @solution_type.setter
    @pyaedt_function_handler()
    def solution_type(self, value):
        if value is None:
            if self._odesign and "GetSolutionType" in dir(self._odesign):
                self._solution_type = self._odesign.GetSolutionType()
                if "Modal" in self._solution_type:
                    self._solution_type = "Modal"
                elif "Terminal" in self._solution_type:
                    self._solution_type = "Terminal"
            return
        elif value[-1:] == "Z":
            self._solution_type = value[:-1]
            self._solution_options[self._solution_type]["options"] = "about Z"
            self._geometry_mode = "about Z"
        elif value[-2:] == "XY":
            self._solution_type = value[:-2]
            self._solution_options[self._solution_type]["options"] = "XY"
            self._geometry_mode = "XY"
        else:
            self._solution_type = value
        if self._solution_type in self._solution_options and self._solution_options[self._solution_type]["name"]:
            try:
                if self._solution_options[self._solution_type]["options"]:
                    opts = self._solution_options[self._solution_type]["options"]
                else:
                    opts = ""
                self._odesign.SetSolutionType(self._solution_options[self._solution_type]["name"], opts)
            except:
                pass


class IcepakDesignSolution(DesignSolution, object):
    def __init__(self, odesign, design_type, aedt_version):
        DesignSolution.__init__(self, odesign, design_type, aedt_version)
        self._problem_type = "TemperatureAndFlow"

    @property
    def problem_type(self):
        """Get/Set the problem type of the icepak Design.
        It can be any of`"TemperatureAndFlow"`, `"TemperatureOnly"`,`"FlowOnly"`.
        """
        if self._odesign:
            self._problem_type = self._odesign.GetProblemType()
        return self._problem_type

    @problem_type.setter
    @pyaedt_function_handler()
    def problem_type(self, value="TemperatureAndFlow"):
        if value == "TemperatureAndFlow":
            self._problem_type = value
            self._solution_options[self.solution_type]["options"] = self._problem_type
            if self.solution_type == "SteadyState":
                self._solution_options[self.solution_type]["default_setup"] = 11
            else:
                self._solution_options[self.solution_type]["default_setup"] = 36
        elif value == "TemperatureOnly":
            self._problem_type = value
            self._solution_options[self.solution_type]["options"] = self._problem_type
            if self.solution_type == "SteadyState":
                self._solution_options[self.solution_type]["default_setup"] = 12
            else:
                self._solution_options[self.solution_type]["default_setup"] = 37
        elif value == "FlowOnly":
            self._problem_type = value
            self._solution_options[self.solution_type]["options"] = self._problem_type
            if self.solution_type == "SteadyState":
                self._solution_options[self.solution_type]["default_setup"] = 13
            else:
                self._solution_options[self.solution_type]["default_setup"] = 38
        else:
            raise AttributeError("Wrong input. Expected values are TemperatureAndFlow, TemperatureOnly and FlowOnly.")
        self.solution_type = self.solution_type

    @property
    def solution_type(self):
        """Get/Set the Solution Type of the active Design."""
        if self._odesign:
            try:
                self._solution_type = self._odesign.GetSolutionType()
            except:
                self._solution_type = solutions_defaults[self._design_type]
        return self._solution_type

    @solution_type.setter
    @pyaedt_function_handler()
    def solution_type(self, solution_type):
        if solution_type:
            if "SteadyState" in solution_type:
                self._solution_type = "SteadyState"
            else:
                self._solution_type = "Transient"
            if "TemperatureAndFlow" in solution_type:
                self._problem_type = "TemperatureAndFlow"
            elif "TemperatureOnly" in solution_type:
                self._problem_type = "TemperatureOnly"
            elif "FlowOnly" in solution_type:
                self._problem_type = "FlowOnly"
            if self._solution_options[self._solution_type]["name"]:
                options = [
                    "NAME:SolutionTypeOption",
                    "SolutionTypeOption:=",
                    self._solution_type,
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

    @property
    def solution_type(self):
        """Get/Set the Machine Type of the active Design."""
        if self._solution_type is None and "GetMachineType" in dir(self._odesign):
            self._solution_type = self._odesign.GetMachineType()
        return self._solution_type

    @solution_type.setter
    @pyaedt_function_handler()
    def solution_type(self, solution_type):
        if solution_type:
            try:
                self._odesign.SetDesignFlow(self._design_type, solution_type)
                self._solution_type = solution_type
            except:
                pass

    @property
    def design_type(self):
        """Get/Set the Machine Design Type."""
        return self._design_type

    @design_type.setter
    @pyaedt_function_handler()
    def design_type(self, value):
        if value:
            self._design_type = value
            self.solution_type = self._solution_type
