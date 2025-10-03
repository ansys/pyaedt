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

import copy
import re

from ansys.aedt.core.base import PyAedtBase
from ansys.aedt.core.generic.general_methods import pyaedt_function_handler
from ansys.aedt.core.modules.circuit_templates import SourceKeys


class Sources(PyAedtBase):
    """Manages sources in Circuit projects."""

    def __init__(self, app, name, source_type=None):
        self._app = app
        self._name = name
        self._props = self._source_props(name, source_type)
        self.source_type = source_type
        if not source_type:
            self.source_type = self._source_type_by_key()
        self._auto_update = True

    @property
    def name(self):
        """Source name.

        Returns
        -------
        str
        """
        return self._name

    @name.setter
    def name(self, source_name):
        if source_name not in self._app.source_names:
            if source_name != self._name:
                original_name = self._name
                self._name = source_name
                for port in self._app.excitation_names:
                    if original_name in self._app.design_excitations[port].props["EnabledPorts"]:
                        self._app.design_excitations[port].props["EnabledPorts"] = [
                            w.replace(original_name, source_name)
                            for w in self._app.design_excitations[port].props["EnabledPorts"]
                        ]
                    if original_name in self._app.design_excitations[port].props["EnabledAnalyses"]:
                        self._app.design_excitations[port].props["EnabledAnalyses"][source_name] = (
                            self._app.design_excitations[port].props["EnabledAnalyses"].pop(original_name)
                        )
                self.update(original_name)
        else:
            self._logger.warning("Name %s already assigned in the design", source_name)

    @property
    def _logger(self):
        """Logger."""
        return self._app.logger

    @pyaedt_function_handler()
    def _source_props(self, source, source_type=None):
        source_prop_dict = {}
        if source in self._app.source_names:
            source_aedt_props = self._app.odesign.GetChildObject("Excitations").GetChildObject(source)
            for el in source_aedt_props.GetPropNames():
                if el == "CosimDefinition":
                    source_prop_dict[el] = None
                elif el == "FreqDependentSourceData":
                    data = self._app.design_properties["NexximSources"]["Data"][source]["FDSFileName"]
                    freqs = re.findall(r"freqs=\[(.*?)\]", data)
                    magnitude = re.findall(r"magnitude=\[(.*?)\]", data)
                    angle = re.findall(r"angle=\[(.*?)\]", data)
                    vreal = re.findall(r"vreal=\[(.*?)\]", data)
                    vimag = re.findall(r"vimag=\[(.*?)\]", data)
                    source_file = re.findall("voltage_source_file=", data)
                    source_prop_dict["frequencies"] = None
                    source_prop_dict["vmag"] = None
                    source_prop_dict["vang"] = None
                    source_prop_dict["vreal"] = None
                    source_prop_dict["vimag"] = None
                    source_prop_dict["fds_filename"] = None
                    source_prop_dict["magnitude_angle"] = False
                    source_prop_dict["FreqDependentSourceData"] = data
                    if freqs:
                        source_prop_dict["frequencies"] = [float(i) for i in freqs[0].split()]
                    if magnitude:
                        source_prop_dict["vmag"] = [float(i) for i in magnitude[0].split()]
                    if angle:
                        source_prop_dict["vang"] = [float(i) for i in angle[0].split()]
                    if vreal:
                        source_prop_dict["vreal"] = [float(i) for i in vreal[0].split()]
                    if vimag:
                        source_prop_dict["vimag"] = [float(i) for i in vimag[0].split()]
                    if source_file:
                        source_prop_dict["fds_filename"] = data[len(re.findall("voltage_source_file=", data)[0]) :]
                    else:
                        if freqs and magnitude and angle:
                            source_prop_dict["magnitude_angle"] = True
                        elif freqs and vreal and vimag:
                            source_prop_dict["magnitude_angle"] = False

                elif el != "Name" and el != "Noise":
                    source_prop_dict[el] = source_aedt_props.GetPropValue(el)
                    if not source_prop_dict[el]:
                        source_prop_dict[el] = ""
        else:
            if source_type in SourceKeys.SourceNames:
                command_template = SourceKeys.SourceTemplates[source_type]
                commands = copy.deepcopy(command_template)
                props = [value for value in commands if isinstance(value, list)]
                for el in props[0]:
                    if isinstance(el, list):
                        if el[0] == "CosimDefinition":
                            source_prop_dict[el[0]] = None
                        elif el[0] == "FreqDependentSourceData":
                            source_prop_dict["frequencies"] = None
                            source_prop_dict["vmag"] = None
                            source_prop_dict["vang"] = None
                            source_prop_dict["vreal"] = None
                            source_prop_dict["vimag"] = None
                            source_prop_dict["fds_filename"] = None
                            source_prop_dict["magnitude_angle"] = True
                            source_prop_dict["FreqDependentSourceData"] = ""

                        elif el[0] != "ModelName" and el[0] != "LabelID":
                            source_prop_dict[el[0]] = el[3]

        return source_prop_dict

    @pyaedt_function_handler()
    def _update_command(self, name, source_prop_dict, source_type, fds_filename=None):
        command_template = SourceKeys.SourceTemplates[source_type]
        commands = copy.deepcopy(command_template)
        commands[0] = "NAME:" + name
        commands[10] = source_prop_dict["Netlist"]
        if fds_filename:
            commands[14] = fds_filename
        cont = 0
        props = [value for value in commands if isinstance(value, list)]
        for command in props[0]:
            if isinstance(command, list) and command[0] in source_prop_dict.keys() and command[0] != "CosimDefinition":
                if command[0] == "Netlist":
                    props[0].pop(cont)
                elif command[0] == "file" and source_prop_dict[command[0]]:
                    props[0][cont][3] = source_prop_dict[command[0]]
                    props[0][cont][4] = source_prop_dict[command[0]]
                elif command[0] == "FreqDependentSourceData" and fds_filename:
                    props[0][cont][3] = fds_filename
                    props[0][cont][4] = fds_filename
                else:
                    props[0][cont][3] = source_prop_dict[command[0]]
            cont += 1

        return commands

    @pyaedt_function_handler()
    def _source_type_by_key(self):
        for source_name in SourceKeys.SourceNames:
            template = SourceKeys.SourceProps[source_name]
            if list(self._props.keys()) == template:
                return source_name
        return None

    @pyaedt_function_handler()
    def update(self, original_name=None, new_source=None):
        """Update the source in AEDT.

        Parameters
        ----------
        original_name : str, optional
            Original name of the source. The default value is ``None``.
        new_source : str, optional
            New name of the source. The default value is ``None``.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.

        """
        arg0 = ["NAME:Data"]
        if self.source_type != "VoltageFrequencyDependent":
            fds_filename = None
        else:
            fds_filename = self._props["FreqDependentSourceData"]

        for source in self._app.sources:
            if "FreqDependentSourceData" in self._app.sources[source]._props.keys():
                fds_filename_source = self._app.sources[source]._props["FreqDependentSourceData"]
            else:
                fds_filename_source = None
            if source == self.name:
                arg0.append(list(self._update_command(source, self._props, self.source_type, fds_filename)))
            elif source != self.name and original_name == source:
                arg0.append(
                    list(
                        self._update_command(
                            self.name, self._props, self._app.sources[source].source_type, fds_filename
                        )
                    )
                )
            else:
                arg0.append(
                    list(
                        self._update_command(
                            source,
                            self._app.sources[source]._props,
                            self._app.sources[source].source_type,
                            fds_filename_source,
                        )
                    )
                )

        if new_source and new_source not in self._app.sources:
            arg0.append(list(self._update_command(self.name, self._props, self.source_type, fds_filename)))

        arg1 = ["NAME:NexximSources", ["NAME:NexximSources", arg0]]
        arg2 = ["NAME:ComponentConfigurationData"]

        # Check Ports with Sources
        arg3 = ["NAME:EnabledPorts"]
        for source_name in self._app.sources:
            excitation_source = []
            for port in self._app.excitation_names:
                # self._app.design_excitations[port]._props
                if source_name in self._app.design_excitations[port]._props["EnabledPorts"]:
                    excitation_source.append(port)
            arg3.append(source_name + ":=")
            arg3.append(excitation_source)

        if new_source and new_source not in self._app.sources:
            arg3.append(new_source + ":=")
            arg3.append([])

        arg4 = ["NAME:EnabledMultipleComponents"]
        for source_name in self._app.sources:
            arg4.append(source_name + ":=")
            arg4.append([])

        if new_source and new_source not in self._app.sources:
            arg4.append(new_source + ":=")
            arg4.append([])

        arg5 = ["NAME:EnabledAnalyses"]
        for source_name in self._app.sources:
            arg6 = ["NAME:" + source_name]
            for port in self._app.excitation_names:
                if source_name in self._app.design_excitations[port]._props["EnabledAnalyses"]:
                    arg6.append(port + ":=")
                    arg6.append(self._app.design_excitations[port]._props["EnabledAnalyses"][source_name])
                else:
                    arg6.append(port + ":=")
                    arg6.append([])
            arg5.append(arg6)

        if new_source and new_source not in self._app.sources:
            arg6 = ["NAME:" + new_source]
            for port in self._app.excitation_names:
                arg6.append(port + ":=")
                arg6.append([])
            arg5.append(arg6)

        arg7 = ["NAME:ComponentConfigurationData", arg3, arg4, arg5]
        arg2.append(arg7)

        self._app.odesign.UpdateSources(arg1, arg2)
        return True

    @pyaedt_function_handler()
    def delete(self):
        """Delete the source in AEDT.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.

        """
        self._app.modeler._odesign.DeleteSource(self.name)
        for port in self._app.excitation_names:
            if self.name in self._app.design_excitations[port].props["EnabledPorts"]:
                self._app.design_excitations[port].props["EnabledPorts"].remove(self.name)
            if self.name in self._app.design_excitations[port].props["EnabledAnalyses"]:
                del self._app.design_excitations[port].props["EnabledAnalyses"][self.name]
        return True

    @pyaedt_function_handler()
    def create(self):
        """Create a new source in AEDT.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.

        """
        self.update(original_name=None, new_source=self.name)
        return True


class PowerSinSource(Sources):
    """Power Sinusoidal Class."""

    def __init__(self, app, name, source_type=None):
        Sources.__init__(self, app, name, source_type)

    @property
    def _child(self):
        return self._app.odesign.GetChildObject("Excitations").GetChildObject(self.name)

    @property
    def ac_magnitude(self):
        """AC magnitude value.

        Returns
        -------
        str
        """
        return self._props["ACMAG"]

    @ac_magnitude.setter
    def ac_magnitude(self, value):
        self._props["ACMAG"] = value
        self._child.SetPropValue("ACMAG", value)

    @property
    def ac_phase(self):
        """AC phase value.

        Returns
        -------
        str
        """
        return self._props["ACPHASE"]

    @ac_phase.setter
    def ac_phase(self, value):
        self._props["ACPHASE"] = value
        self._child.SetPropValue("ACPHASE", value)

    @property
    def dc_magnitude(self):
        """DC voltage value.

        Returns
        -------
        str
        """
        return self._props["DC"]

    @dc_magnitude.setter
    def dc_magnitude(self, value):
        self._props["DC"] = value
        self._child.SetPropValue("DC", value)

    @property
    def power_offset(self):
        """Power offset from zero watts.

        Returns
        -------
        str
        """
        return self._props["VO"]

    @power_offset.setter
    def power_offset(self, value):
        self._props["VO"] = value
        self._child.SetPropValue("VO", value)

    @property
    def power_magnitude(self):
        """Available power of the source above power offset.

        Returns
        -------
        str
        """
        return self._props["POWER"]

    @power_magnitude.setter
    def power_magnitude(self, value):
        self._props["POWER"] = value
        self._child.SetPropValue("POWER", value)

    @property
    def frequency(self):
        """Frequency.

        Returns
        -------
        str
        """
        return self._props["FREQ"]

    @frequency.setter
    def frequency(self, value):
        self._props["FREQ"] = value
        self._child.SetPropValue("FREQ", value)

    @property
    def delay(self):
        """Delay to start of sine wave.

        Returns
        -------
        str
        """
        return self._props["TD"]

    @delay.setter
    def delay(self, value):
        self._props["TD"] = value
        self._child.SetPropValue("TD", value)

    @property
    def damping_factor(self):
        """Damping factor.

        Returns
        -------
        str
        """
        return self._props["ALPHA"]

    @damping_factor.setter
    def damping_factor(self, value):
        self._props["ALPHA"] = value
        self._child.SetPropValue("ALPHA", value)

    @property
    def phase_delay(self):
        """Phase delay.

        Returns
        -------
        str
        """
        return self._props["THETA"]

    @phase_delay.setter
    def phase_delay(self, value):
        self._props["THETA"] = value
        self._child.SetPropValue("THETA", value)

    @property
    def tone(self):
        """Frequency to use for harmonic balance.

        Returns
        -------
        str
        """
        return self._props["TONE"]

    @tone.setter
    def tone(self, value):
        self._props["TONE"] = value
        self._child.SetPropValue("TONE", value)


class PowerIQSource(Sources):
    """Power IQ Class."""

    def __init__(self, app, name, source_type=None):
        Sources.__init__(self, app, name, source_type)

    @property
    def _child(self):
        return self._app.odesign.GetChildObject("Excitations").GetChildObject(self.name)

    @property
    def carrier_frequency(self):
        """Carrier frequency value.

        Returns
        -------
        str
        """
        return self._props["FC"]

    @carrier_frequency.setter
    def carrier_frequency(self, value):
        self._props["FC"] = value
        self._child.SetPropValue("FC", value)

    @property
    def sampling_time(self):
        """Sampling time value.

        Returns
        -------
        str
        """
        return self._props["TS"]

    @sampling_time.setter
    def sampling_time(self, value):
        self._props["TS"] = value
        self._child.SetPropValue("TS", value)

    @property
    def dc_magnitude(self):
        """DC voltage value.

        Returns
        -------
        str
        """
        return self._props["DC"]

    @dc_magnitude.setter
    def dc_magnitude(self, value):
        self._props["DC"] = value
        self._child.SetPropValue("DC", value)

    @property
    def repeat_from(self):
        """Repeat from time.

        Returns
        -------
        str
        """
        return self._props["R"]

    @repeat_from.setter
    def repeat_from(self, value):
        self._props["R"] = value
        self._child.SetPropValue("R", value)

    @property
    def delay(self):
        """Delay to start of sine wave.

        Returns
        -------
        str
        """
        return self._props["TD"]

    @delay.setter
    def delay(self, value):
        self._props["TD"] = value
        self._child.SetPropValue("TD", value)

    @property
    def carrier_amplitude_voltage(self):
        """Carrier amplitude value, voltage-based.

        Returns
        -------
        str
        """
        return self._props["V"]

    @carrier_amplitude_voltage.setter
    def carrier_amplitude_voltage(self, value):
        self._props["V"] = value
        self._child.SetPropValue("V", value)

    @property
    def carrier_amplitude_power(self):
        """Carrier amplitude value, power-based.

        Returns
        -------
        str
        """
        return self._props["VA"]

    @carrier_amplitude_power.setter
    def carrier_amplitude_power(self, value):
        self._props["VA"] = value
        self._child.SetPropValue("VA", value)

    @property
    def carrier_offset(self):
        """Carrier offset.

        Returns
        -------
        str
        """
        return self._props["VO"]

    @carrier_offset.setter
    def carrier_offset(self, value):
        self._props["VO"] = value
        self._child.SetPropValue("VO", value)

    @property
    def real_impedance(self):
        """Real carrier impedance.

        Returns
        -------
        str
        """
        return self._props["RZ"]

    @real_impedance.setter
    def real_impedance(self, value):
        self._props["RZ"] = value
        self._child.SetPropValue("RZ", value)

    @property
    def imaginary_impedance(self):
        """Imaginary carrier impedance.

        Returns
        -------
        str
        """
        return self._props["IZ"]

    @imaginary_impedance.setter
    def imaginary_impedance(self, value):
        self._props["IZ"] = value
        self._child.SetPropValue("IZ", value)

    @property
    def damping_factor(self):
        """Damping factor.

        Returns
        -------
        str
        """
        return self._props["ALPHA"]

    @damping_factor.setter
    def damping_factor(self, value):
        self._props["ALPHA"] = value
        self._child.SetPropValue("ALPHA", value)

    @property
    def phase_delay(self):
        """Phase delay.

        Returns
        -------
        str
        """
        return self._props["THETA"]

    @phase_delay.setter
    def phase_delay(self, value):
        self._props["THETA"] = value
        self._child.SetPropValue("THETA", value)

    @property
    def tone(self):
        """Frequency to use for harmonic balance.

        Returns
        -------
        str
        """
        return self._props["TONE"]

    @tone.setter
    def tone(self, value):
        self._props["TONE"] = value
        self._child.SetPropValue("TONE", value)

    @property
    def i_q_values(self):
        """I and Q value at each timepoint.

        Returns
        -------
        str
        """
        i_q = []
        for cont in range(1, 20):
            i_q.append(
                [self._props["time" + str(cont)], self._props["ival" + str(cont)], self._props["qval" + str(cont)]]
            )
        return i_q

    @i_q_values.setter
    def i_q_values(self, value):
        cont = 0
        for point in value:
            self._props["time" + str(cont + 1)] = point[0]
            self._child.SetPropValue("time" + str(cont + 1), point[0])
            self._props["ival" + str(cont + 1)] = point[1]
            self._child.SetPropValue("ival" + str(cont + 1), point[1])
            self._props["qval" + str(cont + 1)] = point[2]
            self._child.SetPropValue("qval" + str(cont + 1), point[2])
            cont += 1

    @property
    def file(
        self,
    ):
        """File path with I and Q values.

        Returns
        -------
        str
        """
        return self._props["file"]

    @file.setter
    def file(self, value):
        self._props["file"] = str(value)
        self.update()


class VoltageFrequencyDependentSource(Sources):
    """Voltage Frequency Dependent Class."""

    def __init__(self, app, name, source_type=None):
        Sources.__init__(self, app, name, source_type)

    @property
    def _child(self):
        return self._app.odesign.GetChildObject("Excitations").GetChildObject(self.name)

    @property
    def frequencies(self):
        """List of frequencies in ``Hz``.

        Returns
        -------
        list
        """
        return self._props["frequencies"]

    @frequencies.setter
    def frequencies(self, value):
        self._props["frequencies"] = [float(i) for i in value]
        self._update_prop()

    @property
    def vmag(self):
        """List of magnitudes in ``V``.

        Returns
        -------
        list
        """
        return self._props["vmag"]

    @vmag.setter
    def vmag(self, value):
        self._props["vmag"] = [float(i) for i in value]
        self._update_prop()

    @property
    def vang(self):
        """List of angles in ``rad``.

        Returns
        -------
        list
        """
        return self._props["vang"]

    @vang.setter
    def vang(self, value):
        self._props["vang"] = [float(i) for i in value]
        self._update_prop()

    @property
    def vreal(self):
        """List of real values in ``V``.

        Returns
        -------
        list
        """
        return self._props["vreal"]

    @vreal.setter
    def vreal(self, value):
        self._props["vreal"] = [float(i) for i in value]
        self._update_prop()

    @property
    def vimag(self):
        """List of imaginary values in ``V``.

        Returns
        -------
        list
        """
        return self._props["vimag"]

    @vimag.setter
    def vimag(self, value):
        self._props["vimag"] = [float(i) for i in value]
        self._update_prop()

    @property
    def magnitude_angle(self):
        """Enable magnitude and angle data.

        Returns
        -------
        bool
        """
        return self._props["magnitude_angle"]

    @magnitude_angle.setter
    def magnitude_angle(self, value):
        self._props["magnitude_angle"] = value
        self._update_prop()

    @property
    def fds_filename(self):
        """FDS file path.

        Returns
        -------
        bool
        """
        return self._props["fds_filename"]

    @fds_filename.setter
    def fds_filename(self, name):
        if not name:
            self._props["fds_filename"] = None
            self._update_prop()
        else:
            self._props["fds_filename"] = str(name)
            self._props["FreqDependentSourceData"] = "voltage_source_file=" + str(name)
            self.update()

    @pyaedt_function_handler()
    def _update_prop(self):
        if (
            self._props["vmag"]
            and self._props["vang"]
            and self._props["frequencies"]
            and self._props["magnitude_angle"]
            and not self._props["fds_filename"]
        ):
            if len(self._props["vmag"]) == len(self._props["vang"]) == len(self._props["frequencies"]):
                self._props["FreqDependentSourceData"] = (
                    "freqs="
                    + str(self._props["frequencies"]).replace(",", "")
                    + " vmag="
                    + str(self._props["vmag"]).replace(",", "")
                    + " vang="
                    + str(self._props["vang"]).replace(",", "")
                )
                self.update()
        elif (
            self._props["vreal"]
            and self._props["vimag"]
            and self._props["frequencies"]
            and not self._props["magnitude_angle"]
            and not self._props["fds_filename"]
        ):
            if len(self._props["vreal"]) == len(self._props["vimag"]) == len(self._props["frequencies"]):
                self._props["FreqDependentSourceData"] = (
                    "freqs="
                    + str(self._props["frequencies"]).replace(",", "")
                    + " vreal="
                    + str(self._props["vreal"]).replace(",", "")
                    + " vimag="
                    + str(self._props["vimag"]).replace(",", "")
                )
                self.update()
        else:
            self._props["FreqDependentSourceData"] = ""
            self.update()
        return True


class VoltageDCSource(Sources):
    """Power Sinusoidal Class."""

    def __init__(self, app, name, source_type=None):
        Sources.__init__(self, app, name, source_type)

    @property
    def _child(self):
        return self._app.odesign.GetChildObject("Excitations").GetChildObject(self.name)

    @property
    def ac_magnitude(self):
        """AC magnitude value.

        Returns
        -------
        str
        """
        return self._props["ACMAG"]

    @ac_magnitude.setter
    def ac_magnitude(self, value):
        self._props["ACMAG"] = value
        self._child.SetPropValue("ACMAG", value)

    @property
    def ac_phase(self):
        """AC phase value.

        Returns
        -------
        str
        """
        return self._props["ACPHASE"]

    @ac_phase.setter
    def ac_phase(self, value):
        self._props["ACPHASE"] = value
        self._child.SetPropValue("ACPHASE", value)

    @property
    def dc_magnitude(self):
        """DC voltage value.

        Returns
        -------
        str
        """
        return self._props["DC"]

    @dc_magnitude.setter
    def dc_magnitude(self, value):
        self._props["DC"] = value
        self._child.SetPropValue("DC", value)


class VoltageSinSource(Sources):
    """Power Sinusoidal Class."""

    def __init__(self, app, name, source_type=None):
        Sources.__init__(self, app, name, source_type)

    @property
    def _child(self):
        return self._app.odesign.GetChildObject("Excitations").GetChildObject(self.name)

    @property
    def ac_magnitude(self):
        """AC magnitude value.

        Returns
        -------
        str
        """
        return self._props["ACMAG"]

    @ac_magnitude.setter
    def ac_magnitude(self, value):
        self._props["ACMAG"] = value
        self._child.SetPropValue("ACMAG", value)

    @property
    def ac_phase(self):
        """AC phase value.

        Returns
        -------
        str
        """
        return self._props["ACPHASE"]

    @ac_phase.setter
    def ac_phase(self, value):
        self._props["ACPHASE"] = value
        self._child.SetPropValue("ACPHASE", value)

    @property
    def dc_magnitude(self):
        """DC voltage value.

        Returns
        -------
        str
        """
        return self._props["DC"]

    @dc_magnitude.setter
    def dc_magnitude(self, value):
        self._props["DC"] = value
        self._child.SetPropValue("DC", value)

    @property
    def voltage_amplitude(self):
        """Voltage amplitude.

        Returns
        -------
        str
        """
        return self._props["VA"]

    @voltage_amplitude.setter
    def voltage_amplitude(self, value):
        self._props["VA"] = value
        self._child.SetPropValue("VA", value)

    @property
    def voltage_offset(self):
        """Voltage offset from zero watts.

        Returns
        -------
        str
        """
        return self._props["VO"]

    @voltage_offset.setter
    def voltage_offset(self, value):
        self._props["VO"] = value
        self._child.SetPropValue("VO", value)

    @property
    def frequency(self):
        """Frequency.

        Returns
        -------
        str
        """
        return self._props["FREQ"]

    @frequency.setter
    def frequency(self, value):
        self._props["FREQ"] = value
        self._child.SetPropValue("FREQ", value)

    @property
    def delay(self):
        """Delay to start of sine wave.

        Returns
        -------
        str
        """
        return self._props["TD"]

    @delay.setter
    def delay(self, value):
        self._props["TD"] = value
        self._child.SetPropValue("TD", value)

    @property
    def damping_factor(self):
        """Damping factor.

        Returns
        -------
        str
        """
        return self._props["ALPHA"]

    @damping_factor.setter
    def damping_factor(self, value):
        self._props["ALPHA"] = value
        self._child.SetPropValue("ALPHA", value)

    @property
    def phase_delay(self):
        """Phase delay.

        Returns
        -------
        str
        """
        return self._props["THETA"]

    @phase_delay.setter
    def phase_delay(self, value):
        self._props["THETA"] = value
        self._child.SetPropValue("THETA", value)

    @property
    def tone(self):
        """Frequency to use for harmonic balance.

        Returns
        -------
        str
        """
        return self._props["TONE"]

    @tone.setter
    def tone(self, value):
        self._props["TONE"] = value
        self._child.SetPropValue("TONE", value)


class CurrentSinSource(Sources):
    """Current Sinusoidal Class."""

    def __init__(self, app, name, source_type=None):
        Sources.__init__(self, app, name, source_type)

    @property
    def _child(self):
        return self._app.odesign.GetChildObject("Excitations").GetChildObject(self.name)

    @property
    def ac_magnitude(self):
        """AC magnitude value.

        Returns
        -------
        str
        """
        return self._props["ACMAG"]

    @ac_magnitude.setter
    def ac_magnitude(self, value):
        self._props["ACMAG"] = value
        self._child.SetPropValue("ACMAG", value)

    @property
    def ac_phase(self):
        """AC phase value.

        Returns
        -------
        str
        """
        return self._props["ACPHASE"]

    @ac_phase.setter
    def ac_phase(self, value):
        self._props["ACPHASE"] = value
        self._child.SetPropValue("ACPHASE", value)

    @property
    def dc_magnitude(self):
        """DC current value.

        Returns
        -------
        str
        """
        return self._props["DC"]

    @dc_magnitude.setter
    def dc_magnitude(self, value):
        self._props["DC"] = value
        self._child.SetPropValue("DC", value)

    @property
    def current_amplitude(self):
        """Current amplitude.

        Returns
        -------
        str
        """
        return self._props["VA"]

    @current_amplitude.setter
    def current_amplitude(self, value):
        self._props["VA"] = value
        self._child.SetPropValue("VA", value)

    @property
    def current_offset(self):
        """Current offset.

        Returns
        -------
        str
        """
        return self._props["VO"]

    @current_offset.setter
    def current_offset(self, value):
        self._props["VO"] = value
        self._child.SetPropValue("VO", value)

    @property
    def frequency(self):
        """Frequency.

        Returns
        -------
        str
        """
        return self._props["FREQ"]

    @frequency.setter
    def frequency(self, value):
        self._props["FREQ"] = value
        self._child.SetPropValue("FREQ", value)

    @property
    def delay(self):
        """Delay to start of sine wave.

        Returns
        -------
        str
        """
        return self._props["TD"]

    @delay.setter
    def delay(self, value):
        self._props["TD"] = value
        self._child.SetPropValue("TD", value)

    @property
    def damping_factor(self):
        """Damping factor.

        Returns
        -------
        str
        """
        return self._props["ALPHA"]

    @damping_factor.setter
    def damping_factor(self, value):
        self._props["ALPHA"] = value
        self._child.SetPropValue("ALPHA", value)

    @property
    def phase_delay(self):
        """Phase delay.

        Returns
        -------
        str
        """
        return self._props["THETA"]

    @phase_delay.setter
    def phase_delay(self, value):
        self._props["THETA"] = value
        self._child.SetPropValue("THETA", value)

    @property
    def multiplier(self):
        """Multiplier for simulating multiple parallel current sources.

        Returns
        -------
        str
        """
        return self._props["M"]

    @multiplier.setter
    def multiplier(self, value):
        self._props["M"] = value
        self._child.SetPropValue("M", value)

    @property
    def tone(self):
        """Frequency to use for harmonic balance.

        Returns
        -------
        str
        """
        return self._props["TONE"]

    @tone.setter
    def tone(self, value):
        self._props["TONE"] = value
        self._child.SetPropValue("TONE", value)
