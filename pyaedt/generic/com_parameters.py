from pathlib import Path

import pandas as pd
import win32com.client as win32

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


        Parameters
        ----------
        file_path: str
            Path of the configure file.

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
    def load_ieee_excel(self, file_path):
        """Load IEEE original configure file in Excel format.

        Parameters
        ----------
        file_path: str
         Path of the Execel file.

        Returns
        -------
        bool
        """
        excel = win32.gencache.EnsureDispatch("Excel.Application")
        excel.Visible = False

        wb = excel.Workbooks.Open(file_path)
        _com_param = wb.Sheets["COM_Settings"]

        com_param = {}
        com_param.update(_com_param.Range("A3", "B100").Value)
        com_param.update(_com_param.Range("F2", "G100").Value)
        com_param.update(_com_param.Range("J3", "K100").Value)

        wb.Close(True)
        excel.Quit()

        com_param_map = self._CFG_DIR / "00_COMSettingsExplained.csv"
        keys = {}
        keyword_mapping = pd.read_csv(com_param_map, skiprows=2, na_values="")
        keyword_mapping = keyword_mapping.fillna("")
        for spisim_name, matlab_name in list(keyword_mapping.iloc[:, 1:3].values):
            if not matlab_name:
                matlab_name = spisim_name
            keys[matlab_name] = spisim_name

        spisim_com_cfg = {}
        for k, v in com_param.items():
            if not k:
                continue
            if k in [
                "filter and Eq",
                "Operational",
                "TDR and ERL options",
                "Noise, jitter",
                "Table 92–12 parameters",
                "Floating Tap Control",
                "ICN & FOM_ILD parameters",
                "Receiver testing",
            ]:
                continue
            if k in keys:
                spisim_com_cfg[keys[k]] = v

        for i, j in spisim_com_cfg.items():
            self.__setattr__(i, str(j))

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
