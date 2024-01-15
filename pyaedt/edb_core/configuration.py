import json

from pyaedt.generic.general_methods import pyaedt_function_handler


class Configuration:
    """Enables export and import of a JSON configuration file that can be applied to a new or existing design."""

    def __init__(self, pedb):
        self._pedb = pedb

    @pyaedt_function_handler
    def load(self, config_file):
        """Import configuration settings from a JSON file and apply it to the current design.

        Parameters
        ----------
        config_file : str
            Full path to json file.

        Returns
        -------
        dict
            Config dictionary.

        Examples
        --------
        >>> from pyaedt import Edb
        >>> edbapp = Edb("ansys_pcb.aedb")
        >>> edbapp.configuration.load("configure.json")
        """

        components = self._pedb.components.components
        with open(config_file, "r") as f:
            data = json.load(f)

        for comp in data["Components"]:
            refdes = comp["RefDes"]
            part_type = comp["PartType"]

            comp_layout = components[refdes]
            comp_layout.type = part_type

            if part_type in ["Resistor", "Capacitor", "Inductor"]:
                comp_layout.is_enabled = comp["Enabled"]
                rlc_model = comp["RLCModel"] if "RLCModel" in comp else None
                # n_port_model = comp["NPortModel"] if "NPortModel" in comp else None
                # netlist_model = comp["NetlistModel"] if "NetlistModel" in comp else None
                # spice_model = comp["SpiceModel"] if "SpiceModel" in comp else None

                if rlc_model:
                    model_layout = comp_layout.model

                    pin_pairs = rlc_model["PinPairs"] if "PinPairs" in rlc_model else None
                    if pin_pairs:
                        for pp in model_layout.pin_pairs:
                            model_layout.delete_pin_pair_rlc(pp)

                        for pp in pin_pairs:
                            rlc_model_type = pp["Type"]
                            p1 = pp["p1"]
                            p2 = pp["p2"]

                            r = pp["R"] if "R" in pp else None
                            l = pp["L"] if "L" in pp else None
                            c = pp["C"] if "C" in pp else None

                            pin_pair = self._pedb.edb_api.utility.PinPair(p1, p2)
                            rlc = self._pedb.edb_api.utility.Rlc()

                            rlc.IsParallel = False if rlc_model_type == "Series" else True
                            if not r is None:
                                rlc.REnabled = True
                                rlc.R = self._pedb.edb_value(r)
                            else:
                                rlc.REnabled = False

                            if not l is None:
                                rlc.LEnabled = True
                                rlc.L = self._pedb.edb_value(l)
                            else:
                                rlc.LEnabled = False

                            if not c is None:
                                rlc.CEnabled = True
                                rlc.C = self._pedb.edb_value(c)
                            else:
                                rlc.CEnabled = False

                            model_layout.set_pin_pair_rlc(pin_pair, rlc)
                        comp_layout.model = model_layout

            # Configure port properties
            port_properties = comp["PortProperties"] if "PortProperties" in comp else None
            if port_properties:
                ref_offset = port_properties["ReferenceOffset"]
                ref_size_auto = port_properties["ReferenceSizeAuto"]
                ref_size_x = port_properties["ReferenceSizeX"]
                ref_size_y = port_properties["ReferenceSizeY"]
            else:
                ref_offset = 0
                ref_size_auto = True
                ref_size_x = 0
                ref_size_y = 0

            # Configure solder ball properties
            solder_ball_properties = comp["SolderballProperties"] if "SolderballProperties" in comp else None
            if solder_ball_properties:
                shape = solder_ball_properties["Shape"]
                diameter = solder_ball_properties["Diameter"]
                mid_diameter = (
                    solder_ball_properties["MidDiameter"] if "MidDiameter" in solder_ball_properties else diameter
                )
                height = solder_ball_properties["Height"]

                self._pedb.components.set_solder_ball(
                    component=refdes,
                    sball_diam=diameter,
                    sball_mid_diam=mid_diameter,
                    sball_height=height,
                    shape=shape,
                    auto_reference_size=ref_size_auto,
                    reference_height=ref_offset,
                    reference_size_x=ref_size_x,
                    reference_size_y=ref_size_y,
                )

            # Configure ports
            if "Ports" in comp:
                for port in comp["Ports"]:
                    port_type = port["Type"]
                    pos = port["From"]
                    if "Pin" in pos:
                        pin_name = pos["Pin"]
                        port_name = "{}_{}".format(refdes, pin_name)
                        pos_terminal = comp_layout.pins[pin_name].get_terminal(port_name, True)
                    else:  # Net
                        net_name = pos["Net"]
                        port_name = "{}_{}".format(refdes, net_name)
                        if port_type == "Circuit":
                            pg_name = "pg_{}".format(port_name)
                            _, pg = self._pedb.siwave.create_pin_group_on_net(refdes, net_name, pg_name)
                            pos_terminal = pg.get_terminal(port_name, True)
                        else:  # Coax port
                            for _, p in comp_layout.pins.items():
                                if p.net_name == net_name:
                                    pos_terminal = p.get_terminal(port_name, True)
                                    break

                    if port_type == "Circuit":
                        neg = port["To"]
                        if "Pin" in neg:
                            pin_name = neg["Pin"]
                            port_name = "{}_{}_ref".format(refdes, pin_name)
                            neg_terminal = comp_layout.pins[pin_name].get_terminal(port_name, True)
                        else:
                            net_name = neg["Net"]
                            port_name = "{}_{}_ref".format(refdes, net_name)
                            pg_name = "pg_{}".format(port_name)
                            if pg_name not in self._pedb.siwave.pin_groups:
                                _, pg = self._pedb.siwave.create_pin_group_on_net(refdes, net_name, pg_name)
                            else:
                                pg = self._pedb.siwave.pin_groups[pg_name]
                            neg_terminal = pg.get_terminal(port_name, True)

                        self._pedb.create_port(pos_terminal, neg_terminal, True)
                    else:
                        self._pedb.create_port(pos_terminal)

        # Configure HFSS setup
        setups = data["Setups"] if "Setups" in data else []
        for setup in setups:
            setup_type = setup["Type"]

            edb_setup = None
            if setup_type == "HFSS":
                name = setup["Name"]
                edb_setup = self._pedb.create_hfss_setup(name)
                edb_setup.set_solution_single_frequency(
                    setup["Fadapt"], max_num_passes=setup["MaxNumPasses"], max_delta_s=setup["MaxMagDeltaS"]
                )
            elif setup_type == "SIwaveSYZ":
                name = setup["Name"]
                edb_setup = self._pedb.create_siwave_syz_setup(name)
                edb_setup.si_slider_position = setup["SISliderPosition"]

            if "FreqSweep" in setup:
                for fsweep in setup["FreqSweep"]:
                    frequencies = fsweep["Frequencies"]
                    freqs = []

                    for d in frequencies:
                        if d["Distribution"] == "LinearStep":
                            freqs.append(
                                [
                                    "linear scale",
                                    self._pedb.edb_value(d["Start"]).ToString(),
                                    self._pedb.edb_value(d["Stop"]).ToString(),
                                    self._pedb.edb_value(d["Step"]).ToString(),
                                ]
                            )
                        elif d["Distribution"] == "LinearCount":
                            freqs.append(
                                [
                                    "linear count",
                                    self._pedb.edb_value(d["Start"]).ToString(),
                                    self._pedb.edb_value(d["Stop"]).ToString(),
                                    int(d["Points"]),
                                ]
                            )
                        elif d["Distribution"] == "LogScale":
                            freqs.append(
                                [
                                    "log scale",
                                    self._pedb.edb_value(d["Start"]).ToString(),
                                    self._pedb.edb_value(d["Stop"]).ToString(),
                                    int(d["Samples"]),
                                ]
                            )

                    edb_setup.add_frequency_sweep(
                        fsweep["Name"],
                        frequency_sweep=freqs,
                    )

        # Configure stackup
        stackup = data["Stackup"] if "Stackup" in data else None
        if stackup:
            materials = stackup["Materials"] if "Materials" in stackup else []
            materials_reformatted = {}
            for mat in materials:
                new_mat = {}
                new_mat["name"] = mat["Name"]
                if "Conductivity" in mat:
                    new_mat["conductivity"] = mat["Conductivity"]
                if "Permittivity" in mat:
                    new_mat["permittivity"] = mat["Permittivity"]
                if "DielectricLossTangent" in mat:
                    new_mat["loss_tangent"] = mat["DielectricLossTangent"]

                materials_reformatted[mat["Name"]] = new_mat

            layers = stackup["Layers"]
            layers_reformatted = {}

            for l in layers:
                lyr = {
                    "name": l["Name"],
                    "type": l["Type"],
                    "material": l["Material"],
                    "thickness": l["Thickness"],
                }
                if "FillMaterial" in l:
                    lyr["dielectric_fill"] = l["FillMaterial"]
                layers_reformatted[l["Name"]] = lyr
            stackup_reformated = {"layers": layers_reformatted, "materials": materials_reformatted}
            self._pedb.stackup.load(stackup_reformated)

        return data
