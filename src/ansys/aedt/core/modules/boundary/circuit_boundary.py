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

from ansys.aedt.core.generic.general_methods import pyaedt_function_handler
from ansys.aedt.core.modules.circuit_templates import SourceKeys


class Sources(object):
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
                for port in self._app.excitations:
                    if original_name in self._app.excitation_objects[port].props["EnabledPorts"]:
                        self._app.excitation_objects[port].props["EnabledPorts"] = [
                            w.replace(original_name, source_name)
                            for w in self._app.excitation_objects[port].props["EnabledPorts"]
                        ]
                    if original_name in self._app.excitation_objects[port].props["EnabledAnalyses"]:
                        self._app.excitation_objects[port].props["EnabledAnalyses"][source_name] = (
                            self._app.excitation_objects[port].props["EnabledAnalyses"].pop(original_name)
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
            for port in self._app.excitations:
                # self._app.excitation_objects[port]._props
                if source_name in self._app.excitation_objects[port]._props["EnabledPorts"]:
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
            for port in self._app.excitations:
                if source_name in self._app.excitation_objects[port]._props["EnabledAnalyses"]:
                    arg6.append(port + ":=")
                    arg6.append(self._app.excitation_objects[port]._props["EnabledAnalyses"][source_name])
                else:
                    arg6.append(port + ":=")
                    arg6.append([])
            arg5.append(arg6)

        if new_source and new_source not in self._app.sources:
            arg6 = ["NAME:" + new_source]
            for port in self._app.excitations:
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
        for port in self._app.excitations:
            if self.name in self._app.excitation_objects[port].props["EnabledPorts"]:
                self._app.excitation_objects[port].props["EnabledPorts"].remove(self.name)
            if self.name in self._app.excitation_objects[port].props["EnabledAnalyses"]:
                del self._app.excitation_objects[port].props["EnabledAnalyses"][self.name]
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


class PowerSinSource(Sources, object):
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


class PowerIQSource(Sources, object):
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
        self._props["file"] = value
        self.update()


class VoltageFrequencyDependentSource(Sources, object):
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
            self._props["fds_filename"] = name
            self._props["FreqDependentSourceData"] = "voltage_source_file=" + name
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


class VoltageDCSource(Sources, object):
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


class VoltageSinSource(Sources, object):
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


class CurrentSinSource(Sources, object):
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


class Excitations(object):
    """Manages Excitations in Circuit Projects.

    Examples
    --------

    """

    def __init__(self, app, name):
        self._app = app
        self._name = name
        for comp in self._app.modeler.schematic.components:
            if (
                "PortName" in self._app.modeler.schematic.components[comp].parameters.keys()
                and self._app.modeler.schematic.components[comp].parameters["PortName"] == self.name
            ):
                self.schematic_id = comp
                self.id = self._app.modeler.schematic.components[comp].id
                self._angle = self._app.modeler.schematic.components[comp].angle
                self.levels = self._app.modeler.schematic.components[comp].levels
                self._location = self._app.modeler.schematic.components[comp].location
                self._mirror = self._app.modeler.schematic.components[comp].mirror
                self.pins = self._app.modeler.schematic.components[comp].pins
                self._use_symbol_color = self._app.modeler.schematic.components[comp].usesymbolcolor
                break
        self._props = self._excitation_props(name)
        self._auto_update = True

    @property
    def name(self):
        """Excitation name.

        Returns
        -------
        str
        """
        return self._name

    @name.setter
    def name(self, port_name):
        if port_name not in self._app.excitations:
            if port_name != self._name:
                # Take previous properties
                self._app.odesign.RenamePort(self._name, port_name)
                self._name = port_name
                self._app.modeler.schematic.components[self.schematic_id].name = "IPort@" + port_name
                self.pins[0].name = "IPort@" + port_name + ";" + str(self.schematic_id)
        else:
            self._logger.warning("Name %s already assigned in the design", port_name)

    @property
    def angle(self):
        """Symbol angle.

        Returns
        -------
        float
        """
        return self._angle

    @angle.setter
    def angle(self, angle):
        self._app.modeler.schematic.components[self.schematic_id].angle = angle

    @property
    def mirror(self):
        """Enable port mirror.

        Returns
        -------
        bool
        """
        return self._mirror

    @mirror.setter
    def mirror(self, mirror_value=True):
        self._app.modeler.schematic.components[self.schematic_id].mirror = mirror_value
        self._mirror = mirror_value

    @property
    def location(self):
        """Port location.

        Returns
        -------
        list
        """
        return self._location

    @location.setter
    def location(self, location_xy):
        # The command must be called two times.
        self._app.modeler.schematic.components[self.schematic_id].location = location_xy
        self._app.modeler.schematic.components[self.schematic_id].location = location_xy
        self._location = location_xy

    @property
    def use_symbol_color(self):
        """Use symbol color.

        Returns
        -------
        list
        """
        return self._use_symbol_color

    @use_symbol_color.setter
    def use_symbol_color(self, use_color=True):
        self._app.modeler.schematic.components[self.schematic_id].usesymbolcolor = use_color
        self._app.modeler.schematic.components[self.schematic_id].set_use_symbol_color(use_color)
        self._use_symbol_color = use_color

    @property
    def impedance(self):
        """Port termination.

        Returns
        -------
        list
        """
        return [self._props["rz"], self._props["iz"]]

    @impedance.setter
    def impedance(self, termination=None):
        if termination and len(termination) == 2:
            self._app.modeler.schematic.components[self.schematic_id].change_property(
                ["NAME:rz", "Value:=", termination[0]]
            )
            self._app.modeler.schematic.components[self.schematic_id].change_property(
                ["NAME:iz", "Value:=", termination[1]]
            )
            self._props["rz"] = termination[0]
            self._props["iz"] = termination[1]

    @property
    def enable_noise(self):
        """Enable noise.

        Returns
        -------
        bool
        """

        return self._props["EnableNoise"]

    @enable_noise.setter
    def enable_noise(self, enable=False):
        self._app.modeler.schematic.components[self.schematic_id].change_property(
            ["NAME:EnableNoise", "Value:=", enable]
        )
        self._props["EnableNoise"] = enable

    @property
    def noise_temperature(self):
        """Enable noise.

        Returns
        -------
        str
        """

        return self._props["noisetemp"]

    @noise_temperature.setter
    def noise_temperature(self, noise=None):
        if noise:
            self._app.modeler.schematic.components[self.schematic_id].change_property(
                ["NAME:noisetemp", "Value:=", noise]
            )
            self._props["noisetemp"] = noise

    @property
    def microwave_symbol(self):
        """Enable microwave symbol.

        Returns
        -------
        bool
        """
        if self._props["SymbolType"] == 1:
            return True
        else:
            return False

    @microwave_symbol.setter
    def microwave_symbol(self, enable=False):
        if enable:
            self._props["SymbolType"] = 1
        else:
            self._props["SymbolType"] = 0
        self.update()

    @property
    def reference_node(self):
        """Reference node.

        Returns
        -------
        str
        """
        if self._props["RefNode"] == "Z":
            return "Ground"
        return self._props["RefNode"]

    @reference_node.setter
    def reference_node(self, ref_node=None):
        if ref_node:
            self._logger.warning("Set reference node only working with gRPC")
            if ref_node == "Ground":
                ref_node = "Z"
            self._props["RefNode"] = ref_node
            self.update()

    @property
    def enabled_sources(self):
        """Enabled sources.

        Returns
        -------
        list
        """
        return self._props["EnabledPorts"]

    @enabled_sources.setter
    def enabled_sources(self, sources=None):
        if sources:
            self._props["EnabledPorts"] = sources
            self.update()

    @property
    def enabled_analyses(self):
        """Enabled analyses.

        Returns
        -------
        dict
        """
        return self._props["EnabledAnalyses"]

    @enabled_analyses.setter
    def enabled_analyses(self, analyses=None):
        if analyses:
            self._props["EnabledAnalyses"] = analyses
            self.update()

    @pyaedt_function_handler()
    def _excitation_props(self, port):
        excitation_prop_dict = {}
        for comp in self._app.modeler.schematic.components:
            if (
                "PortName" in self._app.modeler.schematic.components[comp].parameters.keys()
                and self._app.modeler.schematic.components[comp].parameters["PortName"] == port
            ):
                excitation_prop_dict["rz"] = "50ohm"
                excitation_prop_dict["iz"] = "0ohm"
                excitation_prop_dict["term"] = None
                excitation_prop_dict["TerminationData"] = None
                excitation_prop_dict["RefNode"] = "Z"
                excitation_prop_dict["EnableNoise"] = False
                excitation_prop_dict["noisetemp"] = "16.85cel"

                if "RefNode" in self._app.modeler.schematic.components[comp].parameters:
                    excitation_prop_dict["RefNode"] = self._app.modeler.schematic.components[comp].parameters["RefNode"]
                if "term" in self._app.modeler.schematic.components[comp].parameters:
                    excitation_prop_dict["term"] = self._app.modeler.schematic.components[comp].parameters["term"]
                    excitation_prop_dict["TerminationData"] = self._app.modeler.schematic.components[comp].parameters[
                        "TerminationData"
                    ]
                else:
                    if "rz" in self._app.modeler.schematic.components[comp].parameters:
                        excitation_prop_dict["rz"] = self._app.modeler.schematic.components[comp].parameters["rz"]
                        excitation_prop_dict["iz"] = self._app.modeler.schematic.components[comp].parameters["iz"]

                if "EnableNoise" in self._app.modeler.schematic.components[comp].parameters:
                    if self._app.modeler.schematic.components[comp].parameters["EnableNoise"] == "true":
                        excitation_prop_dict["EnableNoise"] = True
                    else:
                        excitation_prop_dict["EnableNoise"] = False

                    excitation_prop_dict["noisetemp"] = self._app.modeler.schematic.components[comp].parameters[
                        "noisetemp"
                    ]

                if not self._app.design_properties or not self._app.design_properties["NexximPorts"]["Data"]:
                    excitation_prop_dict["SymbolType"] = 0
                else:
                    excitation_prop_dict["SymbolType"] = self._app.design_properties["NexximPorts"]["Data"][port][
                        "SymbolType"
                    ]

                if "pnum" in self._app.modeler.schematic.components[comp].parameters:
                    excitation_prop_dict["pnum"] = self._app.modeler.schematic.components[comp].parameters["pnum"]
                else:
                    excitation_prop_dict["pnum"] = None
                source_port = []
                if not self._app.design_properties:
                    enabled_ports = None
                else:
                    enabled_ports = self._app.design_properties["ComponentConfigurationData"]["EnabledPorts"]
                if isinstance(enabled_ports, dict):
                    for source in enabled_ports:
                        if enabled_ports[source] and port in enabled_ports[source]:
                            source_port.append(source)
                excitation_prop_dict["EnabledPorts"] = source_port

                components_port = []
                if not self._app.design_properties:
                    multiple = None
                else:
                    multiple = self._app.design_properties["ComponentConfigurationData"]["EnabledMultipleComponents"]
                if isinstance(multiple, dict):
                    for source in multiple:
                        if multiple[source] and port in multiple[source]:
                            components_port.append(source)
                excitation_prop_dict["EnabledMultipleComponents"] = components_port

                port_analyses = {}
                if not self._app.design_properties:
                    enabled_analyses = None
                else:
                    enabled_analyses = self._app.design_properties["ComponentConfigurationData"]["EnabledAnalyses"]
                if isinstance(enabled_analyses, dict):
                    for source in enabled_analyses:
                        if (
                            enabled_analyses[source]
                            and port in enabled_analyses[source]
                            and source in excitation_prop_dict["EnabledPorts"]
                        ):
                            port_analyses[source] = enabled_analyses[source][port]
                excitation_prop_dict["EnabledAnalyses"] = port_analyses
                return excitation_prop_dict

    @pyaedt_function_handler()
    def update(self):
        """Update the excitation in AEDT.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.

        """

        # self._logger.warning("Property port update only working with GRPC")

        if self._props["RefNode"] == "Ground":
            self._props["RefNode"] = "Z"

        arg0 = [
            "NAME:" + self.name,
            "IIPortName:=",
            self.name,
            "SymbolType:=",
            self._props["SymbolType"],
            "DoPostProcess:=",
            False,
        ]

        arg1 = ["NAME:ChangedProps"]
        arg2 = []

        # Modify RefNode
        if self._props["RefNode"] != "Z":
            arg2 = [
                "NAME:NewProps",
                ["NAME:RefNode", "PropType:=", "TextProp", "OverridingDef:=", True, "Value:=", self._props["RefNode"]],
            ]

        # Modify Termination
        if self._props["term"] and self._props["TerminationData"]:
            arg2 = [
                "NAME:NewProps",
                ["NAME:term", "PropType:=", "TextProp", "OverridingDef:=", True, "Value:=", self._props["term"]],
            ]

        for prop in self._props:
            skip1 = (prop == "rz" or prop == "iz") and isinstance(self._props["term"], str)
            skip2 = prop == "EnabledPorts" or prop == "EnabledMultipleComponents" or prop == "EnabledAnalyses"
            skip3 = prop == "SymbolType"
            skip4 = prop == "TerminationData" and not isinstance(self._props["term"], str)
            if not skip1 and not skip2 and not skip3 and not skip4 and self._props[prop] is not None:
                command = ["NAME:" + prop, "Value:=", self._props[prop]]
                arg1.append(command)

        arg1 = [["NAME:Properties", arg2, arg1]]
        self._app.odesign.ChangePortProperty(self.name, arg0, arg1)

        for source in self._app.sources:
            self._app.sources[source].update()
        return True

    @pyaedt_function_handler()
    def delete(self):
        """Delete the port in AEDT.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.

        """
        self._app.modeler._odesign.DeletePort(self.name)
        return True

    @property
    def _logger(self):
        """Logger."""
        return self._app.logger
