# coding=utf-8
from collections import OrderedDict
import os
from pathlib import Path
import re
from struct import unpack
import subprocess  # nosec

from numpy import float32
from numpy import float64
from numpy import zeros

from pyaedt import generate_unique_name
from pyaedt import is_linux
from pyaedt import pyaedt_function_handler
from pyaedt import settings
from pyaedt.generic.com_parameters import COMParameters
from pyaedt.generic.general_methods import env_value
from pyaedt.misc import current_version


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
    def _compute_spisim(self, parameter, out_file, touchstone_file="", config_file=""):
        exec_name = "SPISimJNI_LX64.exe" if is_linux else "SPISimJNI_WIN64.exe"
        spisimExe = os.path.join(self.desktop_install_dir, "spisim", "SPISim", "modules", "ext", exec_name)

        cfgCmmd = ""
        if touchstone_file != "":
            cfgCmmd = cfgCmmd + '-i "%s"' % touchstone_file
        if config_file != "":
            cfgCmmd = '-v CFGFILE="%s"' % config_file
        if out_file:
            cfgCmmd += ' -o "%s"' % out_file
        command = [spisimExe, parameter, cfgCmmd]
        # Debug('%s %s' % (cmdList[0], ' '.join(arguments)))
        # try up to three times to be sure
        out_processing = os.path.join(out_file, generate_unique_name("spsim_out") + ".txt")
        my_env = os.environ.copy()
        my_env.update(settings.aedt_environment_variables)
        if is_linux:  # pragma: no cover
            command.append("&")
            with open(out_processing, "w") as outfile:
                subprocess.Popen(command, env=my_env, stdout=outfile, stderr=outfile).wait()  # nosec
        else:
            with open(out_processing, "w") as outfile:
                subprocess.Popen(" ".join(command), env=my_env, stdout=outfile, stderr=outfile).wait()  # nosec
        return out_processing

    @pyaedt_function_handler()
    def _get_output_parameter_from_result(self, out_file, parameter_name):
        if parameter_name == "ERL":
            try:
                with open(out_file, "r") as infile:
                    lines = infile.read()
                    parmDat = lines.split("[ParmDat]:", 1)[1]
                    for keyValu in parmDat.split(","):
                        dataAry = keyValu.split("=")
                        if dataAry[0].strip().lower() == parameter_name.lower():
                            return float(dataAry[1].strip().split()[0])
                self.logger.error("Failed to compute {}. Check input parameters and retry".format(parameter_name))
                return False
            except IndexError:
                self.logger.error("Failed to compute {}. Check input parameters and retry".format(parameter_name))
                return False
        elif parameter_name == "COM":
            try:
                with open(out_file, "r") as infile:
                    txt = infile.read()
                com_case_0 = re.search(r"Case 0: Calculated COM = (.*?),", txt).groups()[0]
                com_case_1 = re.search(r"Case 1: Calculated COM = (.*?),", txt).groups()[0]
                return float(com_case_0), float(com_case_1)
            except IndexError:
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
            with open(config_file, "r") as fp:
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
            if isinstance(specify_through_ports[0], int):
                thrus4p = ",".join([str(i) for i in specify_through_ports])
            else:
                try:
                    ports = list(self.excitations.keys())
                    thrus4p = ",".join([str(ports.index(i)) for i in specify_through_ports])
                except IndexError:
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
        with open(new_cfg_file, "w") as fp:
            for k, v in cfg_dict.items():
                fp.write("{} = {}\n".format(k, v))

        out_processing = self._compute_spisim(
            "CalcERL", touchstone_file=self.touchstone_file, config_file=new_cfg_file, out_file=self.working_directory
        )
        return self._get_output_parameter_from_result(out_processing, "ERL")

    @pyaedt_function_handler
    def compute_com(
        self,
        standard,
        config_file=None,
        port_order=None,
        fext_snp="",
        next_snp="",
        out_folder="",
    ):
        if standard == "custom":
            com_param = COMParameters()
            com_param.load(config_file)
        else:
            com_param = COMParameters(standard)

        com_param.thrusnp = self.touchstone_file
        com_param.fextary = fext_snp if not isinstance(fext_snp, list) else ";".join(fext_snp)
        com_param.nextary = next_snp if not isinstance(next_snp, list) else ";".join(next_snp)
        if port_order:
            com_param.port_order = port_order

        out_folder = out_folder if out_folder else self.working_directory

        com_param.thrusnp = com_param.thrusnp.replace("\\", "/")
        com_param.fextary = com_param.fextary.replace("\\", "/")
        com_param.nextary = com_param.nextary.replace("\\", "/")

        cfg_file = os.path.join(out_folder, "com_parameters.cfg")
        com_param.export(cfg_file)

        out_processing = self._compute_spisim(parameter="COM", config_file=cfg_file, out_file=out_folder)
        return self._get_output_parameter_from_result(out_processing, "COM")

    @staticmethod
    @pyaedt_function_handler
    def com_parameters(standard="50GAUI-1_C2C"):
        return COMParameters(standard)


def detect_encoding(file_path, expected_pattern="", re_flags=0):
    """Check encoding of a file."""
    for encoding in ("utf-8", "utf_16_le", "cp1252", "cp1250", "shift_jis"):
        try:
            with open(file_path, "r", encoding=encoding) as f:
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
    else:
        return Exception("Failed to identify encoding.")


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

    def __init__(self, name, whattype, datalen, numerical_type="real"):
        """Base Class for both Axis and Trace Classes.
        Defines the common operations between both."""
        self.name = name
        self.whattype = whattype
        self.numerical_type = numerical_type
        if numerical_type == "double":
            self.data = zeros(datalen, dtype=float64)
        elif numerical_type == "real":
            self.data = zeros(datalen, dtype=float32)
        else:
            raise NotImplementedError

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
    """This class is used to represent a trace. It derives from DataSet and implements the additional methods to
    support STEPed simulations.
    This class is constructed by the get_trace() command.
    Data can be accessed through the [] and len() operators, or by the get_wave() method.
    If numpy is available the get_wave() method will return a numpy array.
    """

    def __init__(self, name, whattype, datalen, axis, numerical_type="real"):
        super().__init__(name, whattype, datalen, numerical_type)
        self.axis = axis

    def get_len(self):
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
    def read_float32(f):
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
        elif ch.decode(encoding="utf_16_le") == "Tit":
            self.encoding = "utf_16_le"
            sz_enc = 2
            line = "Tit"
        else:
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
        numerical_type = "real"
        i = header.index("Variables:")
        ivar = 0
        for line in header[i + 1 : -1]:
            idx, name, var_type = line.lstrip().split("\t")
            if numerical_type == "real":
                axis_numerical_type = "double"
            else:
                axis_numerical_type = numerical_type
            if ivar == 0:
                self.axis = Trace(name, var_type, self.nPoints, None, axis_numerical_type)
                trace = self.axis
            else:
                trace = Trace(name, var_type, self.nPoints, self.axis, axis_numerical_type)
            self._traces.append(trace)
            ivar += 1

        if len(self._traces) == 0:
            raw_file.close()
            return

        if kwargs.get("headeronly", False):
            raw_file.close()
            return

        if self.raw_type == "Binary:":
            scan_functions = []
            for trace in self._traces:
                if trace.numerical_type in ["double", "real"]:
                    fun = self.read_float64
                else:
                    raise RuntimeError("Invalid data type {} for trace {}".format(trace.numerical_type, trace.name))
                scan_functions.append(fun)

            for point in range(self.nPoints):
                for i, var in enumerate(self._traces):
                    value = scan_functions[i](raw_file)
                    if value is not None:
                        var.data[point] = value

        else:
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
        else:
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
            )
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
        else:
            raise RuntimeError("This RAW file does not have an axis.")

    def get_len(self):
        """Compute the length of the data.

        Returns
        -------
        int
            Length of the data.
        """
        return self.axis.get_len()

    def __getitem__(self, item):
        return self.get_trace(item)
