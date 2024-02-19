import os
import re
import subprocess

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
        # spisimExe = "'{}'".format(spisimExe)"

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
                # subprocess.Popen(command, env=my_env, stdout=outfile, stderr=outfile).wait()
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
        reflections_lenght=None,
        modulation_type=None,
    ):
        """Compute effective return loss (erl) using Ansys SPISIM from a S-parameter file.

        Parameters
        ----------
        config_file : str, optional
            Configuration file to use as a reference. The default is ``None``, in
            which case this parameter is ignored.
        port_order : str, optional
            Whether to use "``EvenOdd``" or "``Incremental``" numbering for ``s4p`` files.
            Ignored if the ports are greater than 4.
        specify_through_ports : list, optional
            Input and Output ports on which compute the erl. Those are ordered like ``[inp, inneg, outp, outneg]``.
            Ignored if number of ports are 4.
        bandwidth : float, str, optional
            Application bandwidth: inverse of one UI (unit interval). Can be a float or str with unit ("m", "g").
            Default is ``30e9``.
        tdr_duration : float, optional
            TDR duration (in second): How long the TDR tailed data should be applied. Default is ``5``.
        z_terminations : float, optional
            Z-Terminations: termination (Z11 and Z22) when TDR is calculated. Default is ``50``.
        transition_time : float, str, optional
            Transition time: how fast (slew rate) input pulse transit from 0 to Vcc volt. Default is "``10p``".
        fixture_delay : float, optional
            Fixture delay: delay when input starts transition from 0 to Vcc. Default is ``500e-12``.
        input_amplitude : float, optional
            Input amplitude: Vcc volt of step input. Default is ``1.0``.
        ber : float, optional
            Specified BER: At what threshold ERL is calculated. Default is ``1e-4``.
        pdf_bin_size : float, optional
            PDF bin size: how to quantize the superimposed value. Default is ``1e-5``.
        signal_loss_factor : float, optional
            Signal loss factor (Beta). See SPISIM Help for info. Default is ``1.7e9``.
        permitted_reflection : float, optional
            Permitted reflection (Rho). See SPISIM Help for info. Default is ``0.18``.
        reflections_lenght : float, optional
            Length of the reflections: how many UI will be used to calculate ERL. Default is ``1000``.
        modulation_type : str, optional
           Modulations type: signal modulation type "``NRZ``" or "``PAM4``". Default is "``NRZ``".

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
        cfg_dict["INPARRY"] = self.touchstone_file.replace("\\", "/")
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
        cfg_dict["NCYCLES"] = reflections_lenght if reflections_lenght is not None else cfg_dict["NCYCLES"]

        new_cfg_file = os.path.join(self.working_directory, "spisim_erl.cfg")
        with open(new_cfg_file, "w") as fp:
            for k, v in cfg_dict.items():
                fp.write("{} = {}\n".format(k, v))

        out_processing = self._compute_spisim("CalcERL", self.working_directory, self.touchstone_file, new_cfg_file)
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
