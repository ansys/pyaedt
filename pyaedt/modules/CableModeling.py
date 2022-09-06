import itertools
import json
import os

from pyaedt.application.Variables import decompose_variable_value
from pyaedt.generic.general_methods import generate_unique_name
from pyaedt.generic.LoadAEDTFile import load_entire_aedt_file


class Cable:
    """Contains all common Cable features.

    Parameters
    ----------
    app : :class:`pyaedt.hfss.Hfss`
    json_file_name : str, optional
        Path of the json file where the cable information are saved.
    working_dir : str, optional
        Working directory.

    Examples
    --------
    >>> from pyaedt import Hfss
    >>> from pyaedt.modules.CableModeling import Cable
    >>> hfss = Hfss()
    >>> cable_class = Cable(hfss)

    """

    def __init__(self, app, json_file_name=None, working_dir=None):
        self._app = app
        self._odesign = app.odesign
        self._omodule = self._odesign.GetModule("CableSetup")
        self.clock_source_definitions = None
        self.pwl_source_definitions = None
        if working_dir is None:
            self._working_dir = self._app.toolkit_directory
        else:
            self._working_dir = working_dir

        file_import = self._cable_properties_parser(self._omodule, self._working_dir)
        if file_import["CableManager"]["TDSources"]:
            if (
                "ClockSourceDef" in file_import["CableManager"]["TDSources"].keys()
                and file_import["CableManager"]["TDSources"]["ClockSourceDef"]
            ):
                self.clock_source_definitions = file_import["CableManager"]["TDSources"]["ClockSourceDef"]
            if (
                "PWLSourceDef" in file_import["CableManager"]["TDSources"].keys()
                and file_import["CableManager"]["TDSources"]["PWLSourceDef"]
            ):
                self.pwl_source_definitions = file_import["CableManager"]["TDSources"]["PWLSourceDef"]
            self.existing_sources_names = []
            if isinstance(self.clock_source_definitions, list):
                for source in self.clock_source_definitions:
                    if source.get("ClockSignalParams"):
                        self.existing_sources_names.append(source["TDSourceAttribs"]["Name"])
            elif isinstance(self.clock_source_definitions, dict):
                self.existing_sources_names.append(self.clock_source_definitions["TDSourceAttribs"]["Name"])
            if isinstance(self.pwl_source_definitions, list):
                for source in self.pwl_source_definitions:
                    if source.get("PWLSignalParams"):
                        self.existing_sources_names.append(source["TDSourceAttribs"]["Name"])
            elif isinstance(self.pwl_source_definitions, dict):
                self.existing_sources_names.append(self.pwl_source_definitions["TDSourceAttribs"]["Name"])

        self.cable_definitions = file_import["CableManager"]["Definitions"]
        self.existing_bundle_cables_names = []
        self.existing_straight_wire_cables_ids = []
        self.existing_straight_wire_cables_names = []
        self.existing_twisted_pair_cables_names = []
        bundle_cables_list = []
        st_wire_cables_list = []
        twisted_pair_cables_list = []
        if self.cable_definitions.get("CableBundle"):
            if not isinstance(self.cable_definitions.get("CableBundle"), list):
                bundle_cables_list.append(self.cable_definitions.get("CableBundle"))
            else:
                bundle_cables_list = self.cable_definitions.get("CableBundle")
            for x in bundle_cables_list:
                self.existing_bundle_cables_names.append(x["BundleAttribs"]["Name"])
        if self.cable_definitions.get("StWireCable"):
            if not isinstance(self.cable_definitions.get("StWireCable"), list):
                st_wire_cables_list.append(self.cable_definitions.get("StWireCable"))
            else:
                st_wire_cables_list = self.cable_definitions.get("StWireCable")
            for x in st_wire_cables_list:
                self.existing_straight_wire_cables_ids.append(x["ID"])
                self.existing_straight_wire_cables_names.append(x["StWireAttribs"]["Name"])
        if self.cable_definitions.get("TwistedPairCable"):
            if not isinstance(self.cable_definitions.get("TwistedPairCable"), list):
                twisted_pair_cables_list.append(self.cable_definitions.get("TwistedPairCable"))
            else:
                twisted_pair_cables_list = self.cable_definitions.get("TwistedPairCable")
            for x in twisted_pair_cables_list:
                self.existing_twisted_pair_cables_names.append(x["TwistedPairAttribs"]["Name"])

        if json_file_name:
            self._init_from_json(json_file_name)

    def create_cable(self):
        """Create a cable.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.
        """
        if self.cable_type == "bundle":
            try:
                if self.jacket_type == "insulation":
                    self._omodule.CreateCableBundle(
                        [
                            "NAME:BundleParams",
                            "AutoPack:=",
                            self.is_auto_pack,
                            [
                                "NAME:InsulationJacketParams",
                                "InsThickness:=",
                                self.insulation_thickness,
                                "JacketMaterial:=",
                                self.jacket_material,
                                "InnerDiameter:=",
                                self.inner_diameter,
                            ],
                        ],
                        ["NAME:BundleAttribs", "Name:=", self.cable_name],
                    )
                elif self.jacket_type == "braided shield":
                    self._omodule.CreateCableBundle(
                        [
                            "NAME:BundleParams",
                            "AutoPack:=",
                            self.is_auto_pack,
                            [
                                "NAME:BraidShieldJacketParams",
                                "JacketMaterial:=",
                                self.jacket_material,
                                "NumCarriers:=",
                                self.num_carriers,
                                "NumWiresInCarrier:=",
                                self.num_wires_carriers,
                                "WireDiameter:=",
                                self.wire_diameter,
                                "WeaveAngle:=",
                                self.weave_angle,
                                "InsThickness:=",
                                self.insulation_thickness,
                                "InnerDiameter:=",
                                self.inner_diameter,
                            ],
                        ],
                        ["NAME:BundleAttribs", "Name:=", self.cable_name],
                    )
                elif self.jacket_type == "no jacket":
                    self._omodule.CreateCableBundle(
                        [
                            "NAME:BundleParams",
                            "AutoPack:=",
                            self.is_auto_pack,
                            [
                                "NAME:VirtualJacketParams",
                                "JacketMaterial:=",
                                self.jacket_material,
                                "InnerDiameter:=",
                                self.inner_diameter,
                            ],
                        ],
                        ["NAME:BundleAttribs", "Name:=", self.cable_name],
                    )
                return True
            except:
                self._app.logger.error("Boundle cable not created.")
                return False
        elif self.cable_type == "straight wire":
            try:
                self._omodule.CreateStraightWireCable(
                    [
                        "NAME:StWireParams",
                        "WireStandard:=",
                        self.wire_standard,
                        "WireGauge:=",
                        self.wire_type,
                        "CondDiameter:=",
                        self.conductor_diameter,
                        "CondMaterial:=",
                        self.conductor_material,
                        "InsThickness:=",
                        self.straight_wire_insulation_thickness,
                        "InsMaterial:=",
                        self.insulation_material,
                        "InsType:=",
                        self.insulation_type.title(),
                    ],
                    ["NAME:StWireAttribs", "Name:=", self.cable_name],
                )
                return True
            except:
                self._app.logger.error("Straight wire cable not created.")
                return False
        else:
            try:
                if self.is_lay_length_specified.lower() == "true":
                    self._omodule.CreateTwistedPairCable(
                        self.assign_cable_to_twisted_pair,
                        [
                            "NAME:TwistedPairParams",
                            "IsLayLengthSpecified:=",
                            self.is_lay_length_specified,
                            "LayLength:=",
                            self.lay_length,
                        ],
                        ["NAME:TwistedPairAttribs", "Name:=", self.cable_name],
                    )
                elif self.is_lay_length_specified.lower() == "false":
                    self._omodule.CreateTwistedPairCable(
                        self.assign_cable_to_twisted_pair,
                        [
                            "NAME:TwistedPairParams",
                            "IsLayLengthSpecified:=",
                            self.is_lay_length_specified,
                            "TurnsPerMeter:=",
                            self.turns_per_meter,
                        ],
                        ["NAME:TwistedPairAttribs", "Name:=", self.cable_name],
                    )
                else:
                    self.logger.error("is_lay_length_specified value not valid. Value must be either True or False.")
                    return False
                return True
            except:
                self._app.logger.error("Twisted pair cable not created.")
                return False

    def update_cable_properties(self):
        """Update cable properties for all cable types.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.
        """
        try:
            if self.cable_type == "bundle":
                if self.jacket_type == "no jacket":
                    self.insulation_thickness = "0mm"
                self._odesign.ChangeProperty(
                    [
                        "NAME:AllTabs",
                        [
                            "NAME:Cable",
                            ["NAME:PropServers", "CableSetup:" + self.cable_name],
                            [
                                "NAME:ChangedProps",
                                ["NAME:Name", "Value:=", self.updated_name],
                                ["NAME:JacketType", "Value:=", self.jacket_type],
                                ["NAME:JacketMaterial", "Value:=", '"{}"'.format(self.jacket_material)],
                                ["NAME:InsulationThickness", "Value:=", self.insulation_thickness],
                                ["NAME:JacketInnerDiameter", "Value:=", self.inner_diameter],
                            ],
                        ],
                    ]
                )
            elif self.cable_type == "straight wire":
                self._odesign.ChangeProperty(
                    [
                        "NAME:AllTabs",
                        [
                            "NAME:Cable",
                            ["NAME:PropServers", "CableSetup:" + self.cable_name],
                            [
                                "NAME:ChangedProps",
                                ["NAME:Name", "Value:=", self.updated_name],
                                ["NAME:WireStandard", "Value:=", self.wire_standard],
                                ["NAME:WireType", "Value:=", "{:.2f}".format(float(self.wire_type))],
                                ["NAME:ConductorDiameter", "Value:=", self.conductor_diameter],
                                ["NAME:ConductorMaterial", "Value:=", '"{}"'.format(self.conductor_material)],
                                ["NAME:InsulationType", "Value:=", self.insulation_type.title()],
                                ["NAME:InsulationThickness", "Value:=", self.straight_wire_insulation_thickness],
                                ["NAME:InsulationMaterial", "Value:=", '"{}"'.format(self.insulation_material)],
                            ],
                        ],
                    ]
                )
            else:
                self._odesign.ChangeProperty(
                    [
                        "NAME:AllTabs",
                        [
                            "NAME:Cable",
                            ["NAME:PropServers", "CableSetup:" + self.cable_name],
                            [
                                "NAME:ChangedProps",
                                ["NAME:Name", "Value:=", self.updated_name],
                                ["NAME:Contained Cable", "Value:=", self.assign_cable_to_twisted_pair],
                                ["NAME:Specify Lay Length", "Value:=", self.is_lay_length_specified],
                                ["NAME:Lay Length", "Value:=", self.lay_length],
                                ["NAME:Turns Per Meter", "Value:=", self.turns_per_meter],
                            ],
                        ],
                    ]
                )
            return True
        except:
            self._app.logger.error("Cable properties not updated.")
            return False

    def update_shielding(self):
        """Create jacket type when cable type is bundle and jacket type is braid shield.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.
        """
        try:
            self._odesign.ChangeProperty(
                [
                    "NAME:AllTabs",
                    [
                        "NAME:Cable",
                        ["NAME:PropServers", "CableSetup:" + self.cable_name],
                        [
                            "NAME:ChangedProps",
                            ["NAME:Name", "Value:=", self.updated_name],
                            ["NAME:JacketType", "Value:=", self.jacket_type],
                            ["NAME:JacketMaterial", "Value:=", '"{}"'.format(self.jacket_material)],
                            ["NAME:InsulationThickness", "Value:=", self.insulation_thickness],
                            ["NAME:JacketInnerDiameter", "Value:=", self.inner_diameter],
                        ],
                    ],
                ]
            )
            self._odesign.ChangeProperty(
                [
                    "NAME:AllTabs",
                    [
                        "NAME:Shielding",
                        ["NAME:PropServers", "CableSetup:" + self.updated_name],
                        [
                            "NAME:ChangedProps",
                            ["NAME:NumCarriers", "Value:=", self.num_carriers],
                            ["NAME:NumWiresInCarrier", "Value:=", self.num_wires_carriers],
                            ["NAME:WireDiameter", "Value:=", self.wire_diameter],
                            ["NAME:WeaveAngle", "Value:=", self.weave_angle],
                        ],
                    ],
                ]
            )
            return True
        except:
            self._app.logger.error("Cable shielding properties not updated.")
            return False

    def remove_cables(self):
        """Remove a list of cables.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.
        """
        for cable_to_remove in self.cable_to_remove:
            if cable_to_remove not in itertools.chain(
                self.existing_bundle_cables_names,
                self.existing_straight_wire_cables_names,
                self.existing_twisted_pair_cables_names,
            ):
                self._app.logger.error("Provided cable name to remove doesn't exist in the current design.")
                return False
            else:
                try:
                    self._omodule.RemoveCable(cable_to_remove)
                    return True
                except:
                    self._app.logger.error("Remove cable failed.")
                    return False

    def add_cable_to_bundle(self):
        """Add a cable to an existing cable bundle.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.
        """
        if self.cables_to_add_to_bundle in self.existing_straight_wire_cables_names:
            try:
                self._omodule.AddCableToBundle(
                    self.bundle_cable,
                    self.cables_to_add_to_bundle,
                    self.number_of_cables_to_add,
                    ["NAME:CableInstParams", "XPos:=", "0mm", "YPos:=", "0mm", "RotX:=", "0deg"],
                    ["NAME:CableInstAttribs", "Name:=", self.cables_to_add_to_bundle],
                )
                return True
            except:
                self._app.logger.error("Add cable to Bundle failed. Please check the provided cable names.")
                return False
        else:
            self._app.logger.error("There is not any cable with the provided name.")
            return False

    def create_clock_source(self):
        """Create a clock source.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.
        """
        try:
            self._omodule.CreateClockSource(
                [
                    "NAME:ClockSignalParams",
                    "Period:=",
                    self.source_period,
                    "LowPulseVal:=",
                    self.low_pulse_value,
                    "HighPulseVal:=",
                    self.high_pulse_value,
                    "Risetime:=",
                    self.rise_time,
                    "Falltime:=",
                    self.fall_time,
                    "PulseWidth:=",
                    self.pulse_width,
                ],
                ["NAME:TDSourceAttribs", "Name:=", self.source_name],
            )
            return True
        except:
            self._app.logger.error("Clock source not created.")
            return False

    def update_clock_source(self):
        """Update clock source.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.
        """
        try:
            self._odesign.ChangeProperty(
                [
                    "NAME:AllTabs",
                    [
                        "NAME:Cable",
                        ["NAME:PropServers", "CableSetup:" + self.source_name],
                        [
                            "NAME:ChangedProps",
                            ["NAME:Name", "Value:=", self.updated_source_name],
                            ["NAME:Period", "Value:=", self.source_period],
                            ["NAME:LowPulseVal", "Value:=", self.low_pulse_value],
                            ["NAME:HighPulseVal", "Value:=", self.high_pulse_value],
                            ["NAME:Risetime", "Value:=", self.rise_time],
                            ["NAME:Falltime", "Value:=", self.fall_time],
                            ["NAME:PulseWidth", "Value:=", self.pulse_width],
                        ],
                    ],
                ]
            )
            return True
        except:
            self._app.logger.error("Clock source not created.")
            return False

    def remove_source(self):
        """Remove source.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.
        """
        try:
            self._omodule.RemoveTimeDomainSource(self.source_to_remove)
            return True
        except:
            self._app.logger.error("Source could not be removed.")
            return False

    def remove_all_sources(self):
        """Remove all sources.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.
        """
        try:
            if self.existing_sources_names:
                for source in self.existing_sources_names:
                    self._omodule.RemoveTimeDomainSource(source)
            return True
        except:
            self._app.logger.error("Source could not be removed.")
            return False

    def create_pwl_source(self):
        """Create a clock source.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.
        """
        try:
            self.signal_values.insert(0, "NAME:SignalValues")
            self.time_values.insert(0, "NAME:TimeValues")
            arg1 = [x for x in self.signal_values]
            arg2 = [x for x in self.time_values]
            self._omodule.CreatePWLSource(
                [
                    "NAME:PWLSignalParams",
                    arg1,
                    arg2,
                ],
                ["NAME:TDSourceAttribs", "Name:=", self.pwl_source_name],
            )
            return True
        except:
            self._app.logger.error("PWL source not created.")
            return False

    def create_pwl_source_from_file(self):
        """Create a pwl source from file.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.
        """
        try:
            self._omodule.CreatePWLSourceFromFile(
                self.pwl_source_file_path, ["NAME:TDSourceAttribs", "Name:=", generate_unique_name("pwl")]
            )
            return True
        except:
            self._app.logger.error("PWL source from file not created.")
            return False

    def update_pwl_source(self):
        """Update clock source.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.
        """
        self.signal_values.insert(0, "NAME:SignalValues")
        self.time_values.insert(0, "NAME:TimeValues")
        try:
            self._odesign.ChangeProperty(
                [
                    "NAME:AllTabs",
                    [
                        "NAME:Cable",
                        ["NAME:PropServers", "CableSetup:" + self.pwl_source_name],
                        [
                            "NAME:ChangedProps",
                            [
                                "NAME:Edit PWL...",
                                [
                                    "NAME:PWLSignalParams",
                                    [
                                        [x for x in self.signal_values],
                                    ],
                                    [
                                        [x for x in self.time_values],
                                    ],
                                ],
                            ],
                            ["NAME:Name", "Value:=", self.updated_pwl_source_name],
                        ],
                    ],
                ]
            )
            return True
        except:
            self._app.logger.error("PWL source not created.")
            return False

    def _init_from_json(self, json_file_name):
        try:
            with open(json_file_name, "r") as read_file:
                values = json.load(read_file)
        except FileNotFoundError as e:
            self._app.logger.error(str(e))
            return False
        except OSError as e:
            self._app.logger.error(str(e))
            return False
        except Exception as e:
            self._app.logger.error(str(e))
            return False

        # Cable implementation
        if values["Cable"].lower() == "true":
            try:
                if values["CableType"].lower() in ["bundle", "straight wire", "twisted pair"]:
                    self.cable_type = values["CableType"]
                else:
                    msg = "Cable type is not valid. Available values are: bundle, straight wire, twisted pair"
                    raise ValueError(msg)

                if values["UpdatedName"]:
                    self.updated_name = values["UpdatedName"]

                if values["CablesToRemove"]:
                    self.cable_to_remove = values["CablesToRemove"]

                if values["CablesToBundle"]:
                    if values["CablesToBundle"]["CablesToAdd"]:
                        self.cables_to_add_to_bundle = values["CablesToBundle"]["CablesToAdd"]
                        if values["CablesToBundle"]["BundleCable"]:
                            self.bundle_cable = values["CablesToBundle"]["BundleCable"]
                        if values["CablesToBundle"]["NumberOfCableToAdd"]:
                            self.number_of_cables_to_add = values["CablesToBundle"]["NumberOfCableToAdd"]
                        else:
                            self.number_of_cables_to_add = 2

                if self.cable_type == "bundle":
                    cable_bundle_properties = values["CableManager"]["Definitions"]["CableBundle"]
                    if cable_bundle_properties["BundleAttribs"]["Name"] is None:
                        self.cable_name = generate_unique_name("bundle")
                    else:
                        self.cable_name = cable_bundle_properties["BundleAttribs"]["Name"]
                    self.is_auto_pack = cable_bundle_properties["BundleParams"]["AutoPack"]

                    # Check Jacket type : only one can be True
                    bool_jacket_type_list = [
                        el == "True"
                        for el in [
                            values["IsJacketTypeInsulation"],
                            values["IsJacketTypeBraidShield"],
                            values["IsJacketTypeNoJacket"],
                        ]
                    ]
                    if bool_jacket_type_list.count(True) > 1:
                        msg = "Only one jacket type can be selected at time."
                        raise ValueError(msg)
                    else:
                        # Bundle Jacket type : Insulation
                        if bool_jacket_type_list[0]:
                            self.jacket_type = "insulation"
                            # Set default values if one or more keys are empty
                            if [
                                x
                                for x in cable_bundle_properties["BundleParams"]["InsulationJacketParams"]
                                if cable_bundle_properties["BundleParams"]["InsulationJacketParams"][x]
                                in [" ", "", [], None, 0, False]
                            ]:
                                self.insulation_thickness = "0.25mm"
                                self.jacket_material = "PVC plastic"
                                self.inner_diameter = "2.5mm"
                            else:
                                self.insulation_thickness = cable_bundle_properties["BundleParams"][
                                    "InsulationJacketParams"
                                ]["InsThickness"]
                                if self._app.materials.material_keys.get(
                                    cable_bundle_properties["BundleParams"]["InsulationJacketParams"][
                                        "JacketMaterial"
                                    ].lower()
                                ):
                                    self.jacket_material = cable_bundle_properties["BundleParams"][
                                        "InsulationJacketParams"
                                    ]["JacketMaterial"]
                                else:
                                    msg = "material provided doesn't exist."
                                    raise ValueError(msg)
                                self.inner_diameter = cable_bundle_properties["BundleParams"]["InsulationJacketParams"][
                                    "InnerDiameter"
                                ]
                        # Bundle Jacket type : Braided Shield
                        elif bool_jacket_type_list[1]:
                            self.jacket_type = "braided shield"
                            # Set default values if one or more keys are empty
                            if [
                                x
                                for x in cable_bundle_properties["BundleParams"]["BraidShieldJacketParams"]
                                if cable_bundle_properties["BundleParams"]["BraidShieldJacketParams"][x]
                                in ("", [], None, 0, False)
                            ]:
                                self.insulation_thickness = "0.25mm"
                                self.jacket_material = "copper"
                                self.num_carriers = "2"
                                self.num_wires_carriers = "5"
                                self.wire_diameter = "0.1mm"
                                self.weave_angle = "30deg"
                                self.inner_diameter = "2.5mm"
                            else:
                                if self._app.materials.material_keys.get(
                                    cable_bundle_properties["BundleParams"]["BraidShieldJacketParams"][
                                        "JacketMaterial"
                                    ].lower()
                                ):
                                    self.jacket_material = cable_bundle_properties["BundleParams"][
                                        "BraidShieldJacketParams"
                                    ]["JacketMaterial"]
                                else:
                                    msg = "material provided doesn't exist."
                                    raise ValueError(msg)
                                self.insulation_thickness = "0.25mm"
                                self.num_carriers = cable_bundle_properties["BundleParams"]["BraidShieldJacketParams"][
                                    "NumCarriers"
                                ]
                                self.num_wires_carriers = cable_bundle_properties["BundleParams"][
                                    "BraidShieldJacketParams"
                                ]["NumWiresInCarrier"]
                                self.wire_diameter = cable_bundle_properties["BundleParams"]["BraidShieldJacketParams"][
                                    "WireDiameter"
                                ]
                                self.weave_angle = cable_bundle_properties["BundleParams"]["BraidShieldJacketParams"][
                                    "WeaveAngle"
                                ]
                                self.inner_diameter = cable_bundle_properties["BundleParams"][
                                    "BraidShieldJacketParams"
                                ]["InnerDiameter"]
                        # Bundle Jacket type : no jacket
                        elif bool_jacket_type_list[2]:
                            self.jacket_type = "no jacket"
                            # Set default values if one or more keys are empty
                            if [
                                x
                                for x in cable_bundle_properties["BundleParams"]["VirtualJacketParams"]
                                if cable_bundle_properties["BundleParams"]["VirtualJacketParams"][x]
                                in ("", [], None, 0, False)
                            ]:
                                self.jacket_material = "None"
                                self.insulation_thickness = "0.25mm"
                                self.inner_diameter = "2.5mm"
                            else:
                                self.jacket_material = "None"
                                self.inner_diameter = cable_bundle_properties["BundleParams"]["VirtualJacketParams"][
                                    "InnerDiameter"
                                ]
                elif self.cable_type == "straight wire":
                    cable_st_wire_properties = values["CableManager"]["Definitions"]["StWireCable"]
                    if cable_st_wire_properties["StWireAttribs"]["Name"] is None:
                        self.cable_name = generate_unique_name("stwire")
                    else:
                        self.cable_name = cable_st_wire_properties["StWireAttribs"]["Name"]
                    # Set default values if one or more keys are empty
                    if [
                        x
                        for x in cable_st_wire_properties["StWireParams"]
                        if cable_st_wire_properties["StWireParams"][x] in ("", [], None, 0, False)
                    ]:
                        self.wire_standard = "ISO"
                        self.wire_type = "0.13"
                        self.conductor_diameter = "0.55mm"
                        self.conductor_material = "copper"
                        self.insulation_type = "Thin Wall"
                        self.straight_wire_insulation_thickness = "0.25mm"
                        self.insulation_material = "PVC plastic"
                    else:

                        if cable_st_wire_properties["StWireParams"]["WireStandard"] == "ISO":
                            self.wire_standard = cable_st_wire_properties["StWireParams"]["WireStandard"]
                        else:
                            msg = 'The only accepted wire standard is "ISO".'
                            raise ValueError(msg)
                        if cable_st_wire_properties["StWireParams"]["WireGauge"] in [
                            "0.13",
                            "0.22",
                            "0.35",
                            "0.5",
                            "0.75",
                            "1",
                            "1.5",
                            "2",
                            "2.5",
                            "3",
                            "4",
                            "5",
                            "6",
                            "10",
                            "16",
                            "25",
                            "35",
                            "50",
                            "70",
                            "95",
                            "120",
                        ]:
                            self.wire_type = cable_st_wire_properties["StWireParams"]["WireGauge"]
                            if self.wire_type in ["0.13", "0.22", "0.35"]:
                                insulation_type_options = ["Thin Wall", "Ultra-Thin Wall"]
                            elif self.wire_type in ["0.5", "0.75", "1", "1.5", "2", "2.5"]:
                                insulation_type_options = ["Thick Wall", "Thin Wall", "Ultra-Thin Wall"]
                            if self.wire_type in ["3", "4", "5", "6", "10", "16", "25"]:
                                insulation_type_options = ["Thick Wall", "Thin Wall"]
                            elif self.wire_type in ["35", "50", "70", "95", "120"]:
                                insulation_type_options = ["Thick Wall"]
                        else:
                            msg = (
                                "Wire type not valid. Available options are: 0.13, 0.22, 0.35, 0.5, 0.75, 1, 1.5, 2, "
                                "2.5, 3, 4, 5, 6, 10, 16, 25, 35, 50, 70, 95, 120."
                            )
                            raise ValueError(msg)
                        self.conductor_diameter = cable_st_wire_properties["StWireParams"]["CondDiameter"]
                        if self._app.materials.material_keys.get(
                            cable_st_wire_properties["StWireParams"]["CondMaterial"].lower()
                        ):
                            self.conductor_material = cable_st_wire_properties["StWireParams"]["CondMaterial"]
                        else:
                            msg = "material provided doesn't exist."
                            raise ValueError(msg)
                        if cable_st_wire_properties["StWireParams"]["InsType"].title() in insulation_type_options:
                            self.insulation_type = cable_st_wire_properties["StWireParams"]["InsType"]
                        else:
                            msg = (
                                "insulation type provided is not valid. Depending on wire type the available options"
                                "are thick wall, thin wall or ultra-thin wall."
                            )
                            raise ValueError(msg)
                        self.straight_wire_insulation_thickness = cable_st_wire_properties["StWireParams"][
                            "InsThickness"
                        ]
                        if self._app.materials.material_keys.get(
                            cable_st_wire_properties["StWireParams"]["InsMaterial"].lower()
                        ):
                            self.insulation_material = cable_st_wire_properties["StWireParams"]["InsMaterial"]
                        else:
                            raise ValueError("Material provided doesn't exist.")
                else:
                    cable_twisted_pair_properties = values["CableManager"]["Definitions"]["TwistedPairCable"]
                    if cable_twisted_pair_properties["TwistedPairAttribs"]["Name"] is None:
                        self.cable_name = generate_unique_name("tpair")
                    else:
                        self.cable_name = cable_twisted_pair_properties["TwistedPairAttribs"]["Name"]
                    if not self.existing_straight_wire_cables_names:
                        msg = (
                            "no straight wire cables existing in the project. "
                            "At least two are needed to create a twisted pair."
                        )
                        raise ValueError(msg)
                    else:
                        if (
                            cable_twisted_pair_properties["TwistedPairParams"]["StraightWireCableID"]
                            in self.existing_straight_wire_cables_ids
                        ):
                            index = self.existing_straight_wire_cables_ids.index(
                                cable_twisted_pair_properties["TwistedPairParams"]["StraightWireCableID"]
                            )
                            self.assign_cable_to_twisted_pair = self.existing_straight_wire_cables_names[index]
                        elif not cable_twisted_pair_properties["TwistedPairParams"]["StraightWireCableID"]:
                            msg = "no cable id provided. Please enter at least one valid cable id."
                            raise ValueError(msg)
                        else:
                            msg = (
                                "Cable provided doesn't exist in the current project. Please provide an existing"
                                " cable id."
                            )
                            raise ValueError(msg)
                            # Set default values if one or more keys are empty
                        if [
                            x
                            for x in cable_twisted_pair_properties["TwistedPairParams"]
                            if cable_twisted_pair_properties["TwistedPairParams"][x] in ("", [], None, 0, False)
                        ]:
                            self.assign_cable_to_twisted_pair = self.existing_straight_wire_cables_names[0]
                            self.is_lay_length_specified = "False"
                            self.lay_length = "14mm"
                            self.turns_per_meter = "72"
                        else:
                            self.is_lay_length_specified = cable_twisted_pair_properties["TwistedPairParams"][
                                "IsLayLengthSpecified"
                            ]
                            self.lay_length = cable_twisted_pair_properties["TwistedPairParams"]["LayLength"]
                            self.turns_per_meter = cable_twisted_pair_properties["TwistedPairParams"]["TurnsPerMeter"]
                return True
            except ValueError as e:
                self._app.logger.error(str(e))
                return False

        # Source implementation
        if values["Source"].lower() == "true":
            # Check whether both add and update source are True -> not possible.
            try:
                if values["AddClockSource"].lower() == "true" and values["UpdateClockSource"].lower() == "true":
                    msg = "AddClockSource and UpdateClockSource fields can't have the same value."
                    raise ValueError(msg)
                if values["AddPwlSource"].lower() == "true" and values["UpdatePwlSource"].lower() == "true":
                    msg = "AddPwlSource and UpdatePwlSource fields can't have the same value."
                    raise ValueError(msg)
            except ValueError as e:
                self._app.logger.error(str(e))
                return False

            try:
                # Check if user action is to remove the source
                if values["SourcesToRemove"]:
                    if values["SourcesToRemove"] in self.existing_sources_names:
                        self.source_to_remove = values["SourcesToRemove"]
                    else:
                        msg = "Source to remove doesn't exist in the current design."
                        raise ValueError(msg)
                # Check if user action is to add a clock source
                elif values["ClockSource"].lower() == "true":
                    source_properties = values["CableManager"]["TDSources"]["ClockSourceDef"]
                    if values["UpdateClockSource"].lower() == "true":
                        self.updated_source_name = values["UpdatedSourceName"]
                        if source_properties["TDSourceAttribs"]["Name"]:
                            self.source_name = source_properties["TDSourceAttribs"]["Name"]
                        else:
                            msg = "Provide source name to update."
                            raise ValueError(msg)
                    else:
                        if source_properties["TDSourceAttribs"]["Name"]:
                            self.source_name = source_properties["TDSourceAttribs"]["Name"]
                        else:
                            self.source_name = generate_unique_name("clock")

                    if source_properties["ClockSignalParams"]["Period"]:
                        unit = decompose_variable_value(source_properties["ClockSignalParams"]["Period"])[1]
                        if unit not in ["fs", "ps", "ns", "us", "ms", "s", "min", "hour", "day"]:
                            msg = "Period's unit provided is not valid."
                            raise ValueError(msg)
                        else:
                            self.source_period = source_properties["ClockSignalParams"]["Period"]
                    else:
                        self.source_period = "35us"

                    if source_properties["ClockSignalParams"]["LowPulseVal"]:
                        unit = decompose_variable_value(source_properties["ClockSignalParams"]["LowPulseVal"])[1]
                        if unit not in ["fV", "pV", "nV", "uV", "mV", "V", "kV", "megV", "gV", "dBV"]:
                            msg = "Low Pulse Value's unit provided is not valid."
                            raise ValueError(msg)
                        else:
                            self.low_pulse_value = source_properties["ClockSignalParams"]["LowPulseVal"]
                    else:
                        self.low_pulse_value = "0V"

                    if source_properties["ClockSignalParams"]["HighPulseVal"]:
                        unit = decompose_variable_value(source_properties["ClockSignalParams"]["HighPulseVal"])[1]
                        if unit not in ["fV", "pV", "nV", "uV", "mV", "V", "kV", "megV", "gV", "dBV"]:
                            msg = "High Pulse Value's unit provided is not valid."
                            raise ValueError(msg)
                        else:
                            self.high_pulse_value = source_properties["ClockSignalParams"]["HighPulseVal"]
                    else:
                        self.high_pulse_value = "1V"

                    if source_properties["ClockSignalParams"]["Risetime"]:
                        unit = decompose_variable_value(source_properties["ClockSignalParams"]["Risetime"])[1]
                        if unit not in ["fs", "ps", "ns", "us", "ms", "s", "min", "hour", "day"]:
                            msg = "Rise time unit provided is not valid."
                            raise ValueError(msg)
                        else:
                            self.rise_time = source_properties["ClockSignalParams"]["Risetime"]
                    else:
                        self.rise_time = "5us"

                    if source_properties["ClockSignalParams"]["Falltime"]:
                        unit = decompose_variable_value(source_properties["ClockSignalParams"]["Falltime"])[1]
                        if unit not in ["fs", "ps", "ns", "us", "ms", "s", "min", "hour", "day"]:
                            msg = "Fall time unit provided is not valid."
                            raise ValueError(msg)
                        else:
                            self.fall_time = source_properties["ClockSignalParams"]["Falltime"]
                    else:
                        self.fall_time = "5us"

                    if source_properties["ClockSignalParams"]["PulseWidth"]:
                        unit = decompose_variable_value(source_properties["ClockSignalParams"]["PulseWidth"])[1]
                        if unit not in ["fs", "ps", "ns", "us", "ms", "s", "min", "hour", "day"]:
                            msg = "Pulse width unit provided is not valid."
                            raise ValueError(msg)
                        else:
                            self.pulse_width = source_properties["ClockSignalParams"]["PulseWidth"]
                    else:
                        self.pulse_width = "20us"
                # Check if user action is to add a pwl source
                elif values["PwlSource"].lower() == "true":
                    # Check is user wants to add pwl source from file
                    if values["AddPwlSourceFromFile"]:
                        self.pwl_source_file_path = values["AddPwlSourceFromFile"]
                    else:
                        pwl_source_properties = values["CableManager"]["TDSources"]["PWLSourceDef"]
                        # Check if user wants to update pwl source
                        if values["UpdatePwlSource"].lower() == "true":
                            self.updated_pwl_source_name = values["UpdatedSourceName"]
                            if pwl_source_properties["TDSourceAttribs"]["Name"]:
                                self.pwl_source_name = pwl_source_properties["TDSourceAttribs"]["Name"]
                            else:
                                msg = "Provide a pwl source name to update."
                                raise ValueError(msg)
                        # If user doesn't want to update pwl source a pwl source is added manually
                        else:
                            if pwl_source_properties["TDSourceAttribs"]["Name"]:
                                self.pwl_source_name = pwl_source_properties["TDSourceAttribs"]["Name"]
                            else:
                                self.pwl_source_name = generate_unique_name("clock")

                        # User wants to manually add pwl source values
                        if (
                            pwl_source_properties["PWLSignalParams"]["SignalValues"][0]
                            != pwl_source_properties["PWLSignalParams"]["SignalValues"][-1]
                        ):
                            msg = "First and Last element of voltage list must be equal to each other."
                            raise ValueError(msg)
                        else:
                            self.signal_values = pwl_source_properties["PWLSignalParams"]["SignalValues"]
                        self.time_values = pwl_source_properties["PWLSignalParams"]["TimeValues"]
                        self.pwl_source_name = pwl_source_properties["TDSourceAttribs"]["Name"]
            except ValueError as e:
                self._app.logger.error(str(e))
                return False

    def _cable_properties_parser(self, omodule, working_dir):
        file_path_export = os.path.join(working_dir, "export_cable_library_test.txt")
        omodule.ExportCableLibrary(file_path_export)
        file_path_export_as_json = os.path.join(working_dir, "export_cable_library_as_json_test.json")
        with open(file_path_export_as_json, "w") as f:
            json.dump(load_entire_aedt_file(file_path_export), f)
        return load_entire_aedt_file(file_path_export)
