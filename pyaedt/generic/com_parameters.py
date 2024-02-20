from pathlib import Path
from pyaedt import pyaedt_function_handler
from pyaedt import settings

logger = settings.logger


class COMParameters:
    _CFG_DIR = Path(__file__).parent.parent / "misc" / "spisim_com_configuration_files"
    _STD_TABLE_MAPPING = {"50GAUI-1_C2C": "com_120d_8.cfg", "100GBASE-KR4": "com_93_8.cfg"}

    def __init__(self, standard="50GAUI-1_C2C"):
        self._standard = standard
        self.standard = standard

    @property
    def standard(self):
        """Standard name.

        Returns
        -------
        str
        """
        return self._standard

    @standard.setter
    def standard(self, value):
        std_table = self._STD_TABLE_MAPPING[value]
        cfg_path = self._CFG_DIR / std_table
        self.load(cfg_path)
        self._standard = value

    @property
    def parameters(self):
        """Parameters of the standard with value.

        Returns
        -------
        dict
        """
        return {i: j for i, j in self.__dict__.items() if not i.startswith("_")}

    @pyaedt_function_handler
    def load(self, file_path):
        """Load configuration file.

        Returns
        -------
        bool
        """
        self._standard = "custom"
        with open(file_path, "r") as fp:
            lines = fp.readlines()
            for line in lines:
                if not line.startswith("#") and "=" in line:
                    split_line = [i.strip() for i in line.split("=")]
                    name, value = split_line
                    self.__setattr__(name, str(value))
        return True

    @pyaedt_function_handler
    def export(self, file_path):
        """Generate a configuration file for SpiSim.

        Parameters
        ----------
        file_path : str
            Full path to configuration file to create.

        Returns
        -------
        bool
        """
        with open(file_path, "w") as fp:
            fp.write("################################################################################\n")
            fp.write("# MODULE: COM\n")
            fp.write("# GENERATED ON\n")
            fp.write("################################################################################\n")
            for k, v in self.parameters.items():
                fp.write("# {0}: {0}\n".format(k.upper()))
                fp.write("{} = {}\n".format(k.upper(), v))
        return True
