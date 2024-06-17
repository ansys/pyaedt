# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 - 2024 ANSYS, Inc. and/or its affiliates.
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

# coding=utf-8
from collections import OrderedDict
import os
from pathlib import Path
import re
from struct import unpack
import subprocess  # nosec

from numpy import float64
from numpy import zeros

from pyaedt import generate_unique_name
from pyaedt.generic.general_methods import env_value
from pyaedt.generic.general_methods import generate_unique_folder_name
from pyaedt.generic.general_methods import open_file
from pyaedt.generic.general_methods import pyaedt_function_handler
from pyaedt.generic.settings import is_linux
from pyaedt.generic.settings import settings
from pyaedt.misc import current_version
from pyaedt.misc.spisim_com_configuration_files.com_parameters import COMParametersVer3p4


class SpiSim:
    """Provides support to SpiSim batch mode."""

    def __init__(self, touchstone_file=""):
        self.touchstone_file = touchstone_file
        if settings.aedt_version:
            self.desktop_install_dir = os.environ[env_value(settings.aedt_version)]
        else:
            self.desktop_install_dir = os.environ[env_value(current_version())]
        self.logger = settings.logger
        self._working_directory = ""

    @property
    def working_directory(self):
        """Working directory.

        Returns
        -------
        str
        """
        if self._working_directory != "":
            return self._working_directory
        if self.touchstone_file:
            self._working_directory = os.path.dirname(self.touchstone_file)
        return self._working_directory

    @working_directory.setter
    def working_directory(self, val):
        self._working_directory = val

    @pyaedt_function_handler()
    def _compute_spisim(self, parameter, out_file="", touchstone_file="", config_file=""):
        exec_name = "SPISimJNI_LX64.exe" if is_linux else "SPISimJNI_WIN64.exe"
        spisimExe = os.path.join(self.desktop_install_dir, "spisim", "SPISim", "modules", "ext", exec_name)

        cfgCmmd = ""
        if touchstone_file != "":
            cfgCmmd = cfgCmmd + '-i "%s"' % touchstone_file
        if config_file != "":
            if is_linux:
                cfgCmmd = "-v CFGFILE=%s" % config_file
            else:
                cfgCmmd = '-v CFGFILE="%s"' % config_file
        if out_file:
            cfgCmmd += ', -o "%s"' % out_file
        command = [spisimExe, parameter, cfgCmmd]
        # Debug('%s %s' % (cmdList[0], ' '.join(arguments)))
        # try up to three times to be sure
        if out_file:
            out_processing = os.path.join(out_file, generate_unique_name("spsim_out") + ".txt")
        else:
            out_processing = os.path.join(generate_unique_folder_name(), generate_unique_name("spsim_out") + ".txt")

        my_env = os.environ.copy()
        my_env.update(settings.aedt_environment_variables)

        if is_linux:  # pragma: no cover
            if "ANSYSEM_ROOT_PATH" not in my_env:  # pragma: no cover
                my_env["ANSYSEM_ROOT_PATH"] = self.desktop_install_dir
            if "SPISIM_OUTPUT_LOG" not in my_env:  # pragma: no cover
                my_env["SPISIM_OUTPUT_LOG"] = os.path.join(out_file, generate_unique_name("spsim_out") + ".log")
            with open_file(out_processing, "w") as outfile:
                subprocess.Popen(command, env=my_env, stdout=outfile, stderr=outfile).wait()  # nosec
        else:
            with open_file(out_processing, "w") as outfile:
                subprocess.Popen(" ".join(command), env=my_env, stdout=outfile, stderr=outfile).wait()  # nosec
        return out_processing

    @pyaedt_function_handler()
    def _get_output_parameter_from_result(self, out_file, parameter_name):
        if parameter_name == "ERL":
            try:
                with open_file(out_file, "r") as infile:
                    lines = infile.read()
                    parmDat = lines.split("[ParmDat]:", 1)[1]
                    for keyValu in parmDat.split(","):
                        dataAry = keyValu.split("=")
                        if dataAry[0].strip().lower() == parameter_name.lower():
                            return float(dataAry[1].strip().split()[0])
                self.logger.error(
                    "Failed to compute {}. Check input parameters and retry".format(parameter_name)
                )  # pragma: no cover
                return False  # pragma: no cover
            except IndexError:
                self.logger.error("Failed to compute {}. Check input parameters and retry".format(parameter_name))
                return False
        elif parameter_name == "COM":
            try:
                with open_file(out_file, "r") as infile:
                    txt = infile.read()
                i = 0
                com_results = []
                while True:
                    m = re.search(r"Case {}: Calculated COM = (.*?),".format(i), txt)
                    if m:
                        com_results.append(float(m.groups()[0]))
                        i = i + 1
                    else:
                        if i == 0:
                            self.logger.error("Failed to find results from SPISim log file. \n{txt}")
                        break

                return com_results
            except IndexError:  # pragma: no cover
                self.logger.error("Failed to compute {}. Check input parameters and retry".format(parameter_name))

    @pyaedt_function_handler()
    def compute_erl(
        self,
        config_file=None,
        port_order=None,
        specify_through_ports=None,
        bandwidth=None,
        tdr_duration=None,
        z_terminations=None,
        transition_time=None,
        fixture_delay=None,
        input_amplitude=None,
        ber=None,
        pdf_bin_size=None,
        signal_loss_factor=None,
        permitted_reflection=None,
        reflections_length=None,
        modulation_type=None,
    ):
        """Compute effective return loss (ERL) using Ansys SPISIM from S-parameter file.

        Parameters
        ----------
        config_file : str, optional
            Configuration file to use as a reference. The default is ``None``, in
            which case this parameter is ignored.
        port_order : str, optional
            Whether to use "``EvenOdd``" or "``Incremental``" numbering for S4P files.
            The default is ``None``. This parameter is ignored if there are more than four ports.
        specify_through_ports : list, optional
            Input and output ports to compute the ERL on. Those are ordered like ``[inp, inneg, outp, outneg]``.
            The default is ``None``. This parameter is ignored if there are more than four ports.
        bandwidth : float, str, optional
            Application bandwidth in hertz (Hz), which is the inverse of one UI (unit interval). The value
            can be a float or a string with the unit ("m", "g"). The default is ``30e9``.
        tdr_duration : float, optional
            Time domain reflectometry (TDR) duration in seconds, meaning how long the TDR tailed data should be applied.
            The default is ``5``.
        z_terminations : float, optional
            Z-terminations (Z11 and Z22) when TDR is calculated. The default is ``50``.
        transition_time : float, str, optional
            Transition time: how fast (slew rate) input pulse transit from 0 to Vcc volt. The default is "``10p``".
        fixture_delay : float, optional
            Fixture delay: delay when input starts transition from 0 to Vcc. The default is ``500e-12``.
        input_amplitude : float, optional
            Input amplitude: Vcc volt of step input. The default is ``1.0``.
        ber : float, optional
            Specified BER: At what threshold ERL is calculated. The default is ``1e-4``.
        pdf_bin_size : float, optional
            PDF bin size: how to quantize the superimposed value. The default is ``1e-5``.
        signal_loss_factor : float, optional
            Signal loss factor (Beta). For more information, see the SPISIM Help. The default is ``1.7e9``.
        permitted_reflection : float, optional
            Permitted reflection (Rho). For more information, see the SPISIM Help. The default is ``0.18``.
        reflections_length : float, optional
            Length of the reflections: how many UI will be used to calculate ERL. The default is ``1000``.
        modulation_type : str, optional
           Modulations type: signal modulation type "``NRZ``" or "``PAM4``". The default is "``NRZ``".

        Returns
        -------
        bool or float
            Effective return loss from the spisimExe command, ``False`` when failed.
        """

        cfg_dict = {
            "INPARRY": "",
            "MIXMODE": "",
            "THRUS4P": "",
            "BANDWID": 30e9,
            "TDR_DUR": 5,
            "BINSIZE": 1e-5,
            "REFIMPD": 50,
            "SPECBER": 1e-4,
            "MODTYPE": "NRZ",
            "FIXDELY": 500e-12,
            "INPVOLT": 1.0,
            "TRSTIME": "10p",
            "SIGBETA": 1.7e9,
            "REFLRHO": 0.18,
            "NCYCLES": 1000,
        }
        if config_file:
            with open_file(config_file, "r") as fp:
                lines = fp.readlines()
                for line in lines:
                    if not line.startswith("#") and "=" in line:
                        split_line = [i.strip() for i in line.split("=")]
                        cfg_dict[split_line[0]] = split_line[1]

        self.touchstone_file = self.touchstone_file.replace("\\", "/")
        cfg_dict["INPARRY"] = self.touchstone_file
        cfg_dict["MIXMODE"] = "" if "MIXMODE" not in cfg_dict else cfg_dict["MIXMODE"]
        if port_order is not None and self.touchstone_file.lower().endswith(".s4p"):
            cfg_dict["MIXMODE"] = port_order
        elif not self.touchstone_file.lower().endswith(".s4p"):
            cfg_dict["MIXMODE"] = ""
        cfg_dict["THRUS4P"] = "" if "THRUS4P" not in cfg_dict else cfg_dict["THRUS4P"]

        if specify_through_ports:
            if isinstance(specify_through_ports[0], (str, int)):
                thrus4p = ",".join([str(i) for i in specify_through_ports])
            else:  # pragma: no cover
                self.logger.error("Port not found.")
                return False
            cfg_dict["THRUS4P"] = thrus4p

        cfg_dict["BANDWID"] = bandwidth if bandwidth is not None else cfg_dict["BANDWID"]
        cfg_dict["TDR_DUR"] = tdr_duration if tdr_duration is not None else cfg_dict["TDR_DUR"]
        cfg_dict["BINSIZE"] = pdf_bin_size if pdf_bin_size is not None else cfg_dict["BINSIZE"]
        cfg_dict["REFIMPD"] = z_terminations if z_terminations is not None else cfg_dict["REFIMPD"]
        cfg_dict["SPECBER"] = ber if ber is not None else cfg_dict["SPECBER"]
        cfg_dict["MODTYPE"] = modulation_type if modulation_type is not None else cfg_dict["MODTYPE"]
        cfg_dict["FIXDELY"] = fixture_delay if fixture_delay is not None else cfg_dict["FIXDELY"]
        cfg_dict["INPVOLT"] = input_amplitude if input_amplitude is not None else cfg_dict["INPVOLT"]
        cfg_dict["TRSTIME"] = transition_time if transition_time is not None else cfg_dict["TRSTIME"]
        cfg_dict["SIGBETA"] = signal_loss_factor if signal_loss_factor is not None else cfg_dict["SIGBETA"]
        cfg_dict["REFLRHO"] = permitted_reflection if permitted_reflection is not None else cfg_dict["REFLRHO"]
        cfg_dict["NCYCLES"] = reflections_length if reflections_length is not None else cfg_dict["NCYCLES"]

        new_cfg_file = os.path.join(self.working_directory, "spisim_erl.cfg").replace("\\", "/")
        with open_file(new_cfg_file, "w") as fp:
            for k, v in cfg_dict.items():
                fp.write("# {}: {}\n".format(k, k))
                fp.write("{} = {}\n".format(k, v))
        retries = 3
        if "PYTEST_CURRENT_TEST" in os.environ:
            retries = 10
        trynumb = 0
        while trynumb < retries:
            out_processing = self._compute_spisim(
                "CalcERL",
                touchstone_file=self.touchstone_file,
                config_file=new_cfg_file,
                out_file=self.working_directory,
            )
            results = self._get_output_parameter_from_result(out_processing, "ERL")
            if results:
                return results
            self.logger.warning("Failing to compute ERL, retrying...")
            trynumb += 1
        self.logger.error("Failed to compute ERL.")
        return False

    @pyaedt_function_handler
    def compute_com(
        self,
        standard,
        config_file=None,
        port_order="EvenOdd",
        fext_s4p="",
        next_s4p="",
        out_folder="",
    ):
        """Compute Channel Operating Margin. Only COM ver3.4 is supported.

        Parameters
        ----------
        standard : int
            Name of the standard to apply. Supported stdnards are as below.
            COM_CUSTOM = 0
            COM_50GAUI_1_C2C = 1
            COM_100GAUI_2_C2C = 2
            COM_200GAUI_4 = 3
            COM_400GAUI_8 = 4
            COM_100GBASE_KR4 = 5
            COM_100GBASE_KP4 = 6
        config_file : str, Path, optional
            Config file to use.
        port_order : str, optional
            Whether to use "``EvenOdd``" or "``Incremental``" numbering for S4P files. The default is ``EvenOdd``.
            The default is ``None``. This parameter is ignored if there are more than four ports.
        fext_s4p : str, list, optional
            Fext touchstone file to use.
        next_s4p : str, list, optional
            Next touchstone file to use.
        out_folder : str, optional
            Output folder where to save report.

        Returns
        -------

        """

        com_param = COMParametersVer3p4()
        if standard == 0:
            if os.path.splitext(config_file)[-1] == ".cfg":
                com_param.load_spisim_cfg(config_file)
            else:
                com_param.load(config_file)
        else:
            com_param.standard = standard

        com_param.set_parameter("THRUSNP", self.touchstone_file)
        com_param.set_parameter("FEXTARY", fext_s4p if not isinstance(fext_s4p, list) else ";".join(fext_s4p))
        com_param.set_parameter("NEXTARY", next_s4p if not isinstance(next_s4p, list) else ";".join(next_s4p))

        com_param.set_parameter("Port Order", "[1 3 2 4]" if port_order == "EvenOdd" else "[1 2 3 4]")

        com_param.set_parameter("RESULT_DIR", out_folder if out_folder else self.working_directory)
        return self._compute_com(com_param)

    @pyaedt_function_handler
    def _compute_com(
        self,
        com_parameter,
    ):
        """Compute Channel Operating Margin.

        Parameters
        ----------
        com_parameter: :class:`COMParameters`
            COMParameters class.

        Returns
        -------

        """
        thru_snp = com_parameter.parameters["THRUSNP"].replace("\\", "/")
        fext_snp = com_parameter.parameters["FEXTARY"].replace("\\", "/")
        next_snp = com_parameter.parameters["NEXTARY"].replace("\\", "/")
        result_dir = com_parameter.parameters["RESULT_DIR"].replace("\\", "/")

        com_parameter.set_parameter("THRUSNP", thru_snp)
        com_parameter.set_parameter("FEXTARY", fext_snp)
        com_parameter.set_parameter("NEXTARY", next_snp)
        com_parameter.set_parameter("RESULT_DIR", result_dir)

        cfg_file = os.path.join(com_parameter.parameters["RESULT_DIR"], "com_parameters.cfg")
        com_parameter.export_spisim_cfg(cfg_file)

        out_processing = self._compute_spisim(parameter="COM", config_file=cfg_file)
        return self._get_output_parameter_from_result(out_processing, "COM")

    @pyaedt_function_handler
    def export_com_configure_file(self, file_path, standard=1):
        """Generate a configuration file for SpiSim.

        Parameters
        ----------
        file_path : str, Path
            Full path to configuration file to create.
        standard : int
            Index of the standard.
        Returns
        -------
        bool
        """
        return COMParametersVer3p4(standard).export(file_path)


def detect_encoding(file_path, expected_pattern="", re_flags=0):
    """Check encoding of a file."""
    for encoding in ("utf-8", "utf_16_le", "cp1252", "cp1250", "shift_jis"):
        try:
            with open_file(file_path, "r", encoding=encoding) as f:
                lines = f.read()
                f.seek(0)
        except UnicodeDecodeError:
            # This encoding didn't work, let's try again
            continue
        else:
            if len(lines) == 0:
                # Empty file
                continue
            if expected_pattern:
                if not re.match(expected_pattern, lines, re_flags):
                    # File did not have the expected string
                    # Try again with a different encoding (This is unlikely to resolve the issue)
                    continue
            if encoding == "utf-8" and lines[1] == "\x00":
                continue
            return encoding


class DataSet(object):
    """
    This is the base class for storing all traces of a RAW file. Returned by the get_trace() or by the get_axis()
    methods.
    Normally the user doesn't have to be aware of this class. It is only used internally to encapsulate the different
    implementations of the wave population.
    Data can be retrieved directly by using the [] operator.
    If numpy is available, the numpy vector can be retrieved by using the get_wave() method.
    The parameter whattype defines what is the trace representing in the simulation, Voltage, Current a Time or
    Frequency.
    """

    def __init__(
        self,
        name,
        whattype,
        datalen,
    ):
        """Base Class for both Axis and Trace Classes.
        Defines the common operations between both."""
        self.name = name
        self.whattype = whattype
        self.data = zeros(datalen, dtype=float64)

    def __len__(self):
        return len(self.data)

    def __iter__(self):
        return iter(self.data)

    def __getitem__(self, item):
        return self.data[item]

    @property
    def wave(self):
        """Retrieves the trace data.

        Returns
        -------
        :class:`numpy.array`
            The trace values.
        """
        return self.data


class Trace(DataSet):
    """This class is used to represent a trace.
    This class is constructed by the get_trace() command.
    If numpy is available the get_wave() method will return a numpy array.
    """

    def __init__(
        self,
        name,
        whattype,
        datalen,
        axis,
    ):
        super().__init__(name, whattype, datalen)
        self.axis = axis

    def __len__(self):
        """
        Returns the length of the axis.

        Returns
        -------
        int
            The number of data points.
        """
        return len(self.wave)


class SpiSimRawException(Exception):
    """Custom class for exception handling"""

    ...


class SpiSimRawRead(object):
    """Class for reading SPISim wave Files. It can read all types of Files."""

    @staticmethod
    def read_float64(f):
        s = f.read(8)
        return unpack("d", s)[0]

    @staticmethod
    def read_float32(f):  # pragma: no cover
        s = f.read(4)
        return unpack("f", s)[0]

    def __init__(self, raw_filename: str, **kwargs):
        raw_filename = Path(raw_filename)

        raw_file = open(raw_filename, "rb")

        ch = raw_file.read(6)
        if ch.decode(encoding="utf_8") == "Title:":
            self.encoding = "utf_8"
            sz_enc = 1
            line = "Title:"
        elif ch.decode(encoding="utf_16_le") == "Tit":  # pragma: no cover
            self.encoding = "utf_16_le"
            sz_enc = 2
            line = "Tit"
        else:  # pragma: no cover
            raise RuntimeError("Unrecognized encoding")
        settings.logger.info(f"Reading the file with encoding: '{self.encoding}' ")
        self.raw_params = OrderedDict(Filename=raw_filename)
        self.backannotations = []
        header = []
        binary_start = 6
        while True:
            ch = raw_file.read(sz_enc).decode(encoding=self.encoding, errors="replace")
            binary_start += sz_enc
            if ch == "\n":
                if self.encoding == "utf_8":
                    line = line.rstrip("\r")
                header.append(line)
                if line in ("Binary:", "Values:"):
                    self.raw_type = line
                    break
                line = ""
            else:
                line += ch

        for line in header:
            if not line.startswith("."):
                k, _, v = line.partition(":")
                if k == "Variables":
                    break
                self.raw_params[k] = v.strip()
        self.nPoints = int(self.raw_params["No. Points"], 10)
        self.nVariables = int(self.raw_params["No. Variables"], 10)
        self._traces = []

        self.axis = None
        self.flags = self.raw_params["Flags"].split()
        i = header.index("Variables:")
        ivar = 0
        for line in header[i + 1 : -1]:
            _, name, var_type = line.lstrip().split("\t")
            if ivar == 0:
                self.axis = Trace(name, var_type, self.nPoints, None)
                trace = self.axis
            else:
                trace = Trace(name, var_type, self.nPoints, self.axis)
            self._traces.append(trace)
            ivar += 1

        if len(self._traces) == 0:  # pragma: no cover
            raw_file.close()
            return

        if kwargs.get("headeronly", False):  # pragma: no cover
            raw_file.close()
            return

        if self.raw_type == "Binary:":
            for point in range(self.nPoints):
                for i, var in enumerate(self._traces):
                    value = self.read_float64(raw_file)
                    if value is not None:
                        var.data[point] = value
        else:  # pragma: no cover
            raw_file.close()
            raise SpiSimRawException("Unsupported RAW File. " "%s" "" % self.raw_type)

        raw_file.close()

        self.raw_params["No. Points"] = self.nPoints
        self.raw_params["No. Variables"] = self.nVariables
        self.raw_params["Variables"] = [var.name for var in self._traces]

    def get_raw_property(self, property_name=None):
        """
        Get a property. By default, it returns all properties defined in the RAW file.

        :param property_name: name of the property to retrieve.
        :type property_name: str
        :returns: Property object
        :rtype: str
        :raises: ValueError if the property doesn't exist
        """
        if property_name is None:
            return self.raw_params
        elif property_name in self.raw_params.keys():
            return self.raw_params[property_name]
        else:  # pragma: no cover
            raise ValueError("Invalid property. Use %s" % str(self.raw_params.keys()))

    @property
    def trace_names(self):
        """
        Returns a list of exiting trace names of the RAW file.

        Returns
        -------
        list
            Trace names.
        """
        return [trace.name for trace in self._traces]

    def get_trace(self, trace_ref):
        """Retrieves the trace with the requested name (trace_ref).

        Parameters
        ----------
        trace_ref: str, int
            Name of the trace or the index of the trace.
        """
        if isinstance(trace_ref, str):
            for trace in self._traces:
                if trace_ref.casefold() == trace.name.casefold():  # The trace names are case-insensitive
                    # assert isinstance(trace, DataSet)
                    return trace
            raise IndexError(
                f'{self} doesn\'t contain trace "{trace_ref}"\n'
                f"Valid traces are {[trc.name for trc in self._traces]}"
            )  # pragma: no cover
        else:
            return self._traces[trace_ref]

    def get_wave(self, trace_ref):
        """Retrieves the trace data with the requested name (trace_ref).

        Parameters
        ----------
        trace_ref: str, int
            Name of the trace or the index of the trace.

        Returns
        -------
        :class:`numpy.array`
            The trace values.
        """
        return self.get_trace(trace_ref).wave

    def get_axis(self):
        """This function is equivalent to get_trace(0).wave instruction.

        Returns
        -------
        :class:`numpy.array`
            Axis data.
        """
        if self.axis:
            return self.axis.wave
        else:  # pragma: no cover
            raise RuntimeError("This RAW file does not have an axis.")

    def __len__(self):
        """Compute the length of the data.

        Returns
        -------
        int
            Length of the data.
        """
        return self.axis.__len__()

    def __getitem__(self, item):
        return self.get_trace(item)
