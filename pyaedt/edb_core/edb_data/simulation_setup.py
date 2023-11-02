from pyaedt.generic.general_methods import pyaedt_function_handler
from pyaedt.edb_core.edb_data.hfss_simulation_setup_data import EdbFrequencySweep
from pyaedt.generic.general_methods import generate_unique_name
from pyaedt.generic.general_methods import is_linux
from pyaedt.edb_core.general import convert_netdict_to_pydict
from pyaedt.edb_core.general import convert_pydict_to_netdict


def _parse_value(v):
    """

    Parameters
    ----------
    v :


    Returns
    -------

    """
    #  duck typing parse of the value 'v'
    if v is None or v == "":
        pv = v
    elif v == "true":
        pv = True
    elif v == "false":
        pv = False
    else:
        try:
            pv = int(v)
        except ValueError:
            try:
                pv = float(v)
            except ValueError:
                if isinstance(v, str) and v[0] == v[-1] == "'":
                    pv = v[1:-1]
                else:
                    pv = v
    return pv


class BaseSimulationSetup(object):
    def __init__(self, pedb, edb_setup=None):
        self._pedb = pedb
        self._setup_type = None
        if edb_setup:
            self._edb_object = self._get_edb_setup_info(edb_setup)
        else:
            self._edb_object = None
        self._name = ""
        self._setup_type_mapping = {
            "kHFSS": self._pedb.simsetupdata.HFSSSimulationSettings,
            "kPEM": None,
            "kSIwave": self._pedb.simsetupdata.SIwave.SIWSimulationSettings,
            "kLNA": None,
            "kTransient": None,
            "kQEye": None,
            "kVEye": None,
            "kAMI": None,
            "kAnalysisOption": None,
            "kSIwaveDCIR": self._pedb.simsetupdata.SIwave.SIWDCIRSimulationSettings,
            "kSIwaveEMI": None,
            "kHFSSPI": None,
            "kDDRwizard": None,
            "kQ3D": None,
            "kNumSetupTypes": None,
        }


    @pyaedt_function_handler()
    def _get_edb_setup_info(self, edb_setup):

        if self._setup_type == "kSIwave":
            edb_sim_setup_info = self._edb.simsetupdata.SimSetupInfo[self._setup_type_mapping[self.setup_type]]()

            string = edb_setup.ToString().replace("\t", "").split("\r\n")
            if is_linux:
                string = string[0].split("\n")
            keys = [i.split("=")[0] for i in string if len(i.split("=")) == 2 and "SourceTermsToGround" not in i]
            values = [i.split("=")[1] for i in string if len(i.split("=")) == 2 and "SourceTermsToGround" not in i]
            for val in string:
                if "SourceTermsToGround()" in val:
                    break
                elif "SourceTermsToGround" in val:
                    sources = {}
                    val = val.replace("SourceTermsToGround(", "").replace(")", "").split(",")
                    for v in val:
                        source = v.split("=")
                        sources[source[0]] = source[1]
                    edb_sim_setup_info.SimulationSettings.DCIRSettings.SourceTermsToGround = convert_pydict_to_netdict(sources)
                    break
            for k in keys:
                value = _parse_value(values[keys.index(k)])
                setter = None
                if k in dir(edb_sim_setup_info.SimulationSettings):
                    setter = edb_sim_setup_info.SimulationSettings
                elif k in dir(edb_sim_setup_info.SimulationSettings.AdvancedSettings):
                    setter = edb_sim_setup_info.SimulationSettings.AdvancedSettings

                elif k in dir(edb_sim_setup_info.SimulationSettings.DCAdvancedSettings):
                    setter = edb_sim_setup_info.SimulationSettings.DCAdvancedSettings
                elif "DCIRSettings" in dir(edb_sim_setup_info.SimulationSettings) and k in dir(
                    edb_sim_setup_info.SimulationSettings.DCIRSettings
                ):
                    setter = edb_sim_setup_info.SimulationSettings.DCIRSettings
                elif k in dir(edb_sim_setup_info.SimulationSettings.DCSettings):
                    setter = edb_sim_setup_info.SimulationSettings.DCSettings
                elif k in dir(edb_sim_setup_info.SimulationSettings.AdvancedSettings):
                    setter = edb_sim_setup_info.SimulationSettings.AdvancedSettings
                if setter:
                    try:
                        setter.__setattr__(k, value)
                    except TypeError:
                        try:
                            setter.__setattr__(k, str(value))
                        except:
                            pass
            return edb_sim_setup_info
        elif self._setup_type == "kHFSS":
            return edb_setup.GetSimSetupInfo()

    @property
    def enabled(self):
        """Whether the setup is enabled."""
        return self._edb_object.SimulationSettings.Enabled

    @enabled.setter
    def enabled(self, value):
        self._edb_object.SimulationSettings.Enabled = value
        self._update_setup()

    @property
    def name(self):
        return self._edb_object.Name

    @name.setter
    def name(self, value):
        self._edb_object.Name = value
        self._name = value

    @property
    def position(self):
        return self._edb_object.Position

    @position.setter
    def position(self, value):
        self._edb_object.Position = value

    @property
    def setup_type(self):
        return self._edb_object.SimSetupType.ToString()

    @property
    def frequency_sweeps(self):
        """Get frequency sweep list."""
        temp = {}
        for i in list(self._edb_object.SweepDataList):
            temp[i.Name] = EdbFrequencySweep(self, None, i.Name, i)
        return temp

    @pyaedt_function_handler
    def _create(self, name=None):
        if not name:
            name = generate_unique_name(self.setup_type)
            self._name = name

        if self._edb_object:
            self._setup_type = self.setup_type

        self._edb_object = self._pedb.simsetupdata.SimSetupInfo[self._setup_type_mapping[self._setup_type]]()
        self._edb_object.Name = name
        self._update_setup()

    @pyaedt_function_handler
    def _generate_edb_setup(self):
        setup_type_mapping = {
            "kHFSS": self._pedb.edb_api.utility.utility.HFSSSimulationSetup,
            "kPEM": None,
            "kSIwave": self._pedb.edb_api.utility.utility.SIWaveSimulationSetup,
            "kLNA": None,
            "kTransient": None,
            "kQEye": None,
            "kVEye": None,
            "kAMI": None,
            "kAnalysisOption": None,
            "kSIwaveDCIR": self._pedb.edb_api.utility.utility.SIWaveDCIRSimulationSetup,
            "kSIwaveEMI": None,
            "kHFSSPI": None,
            "kDDRwizard": None,
            "kQ3D": None,
            "kNumSetupTypes": None,
        }
        return setup_type_mapping[self.setup_type](self._edb_object)

    @pyaedt_function_handler()
    def _update_setup(self):
        edb_setup = self._generate_edb_setup()
        if self.name in self._pedb.setups:
            self._pedb.layout.cell.DeleteSimulationSetup(self.name)
        self._pedb.layout.cell.AddSimulationSetup(edb_setup)
        return True